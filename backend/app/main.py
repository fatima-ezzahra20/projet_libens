from fastapi import FastAPI, HTTPException, UploadFile, File
from typing import List, Optional
from .database import supabase
from .models import ReleveResponse, ReleveListItem, Transaction, Solde
from .services.ner_model import extract_entities_from_text
from .services.ocr_extractor import extract_text_from_file
import uuid
import os
import shutil
import asyncio
from concurrent.futures import ThreadPoolExecutor
import datetime
import locale
from fastapi.middleware.cors import CORSMiddleware

# Définir le langage pour la conversion des mois
try:
    locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
except locale.Error:
    # Pour Windows, utiliser un format compatible
    locale.setlocale(locale.LC_TIME, 'French_France.1252')

executor = ThreadPoolExecutor()

app = FastAPI()

# <-- ADD THIS BLOCK
origins = [
    "http://localhost:3000",  # L'URL de votre frontend React
    "http://127.0.0.1:3000",  # Une autre forme pour le même domaine
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# END OF BLOCK -->

@app.post("/upload", response_model=ReleveResponse)
async def upload_releve(file: UploadFile = File(...)):
    file_path = None
    try:
        # 1. Sauvegarder le fichier temporairement
        upload_dir = "temp_uploads"
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 2. Extraire le texte avec l'OCR
        loop = asyncio.get_event_loop()
        extracted_text = await loop.run_in_executor(executor, extract_text_from_file, file_path)
        if not extracted_text:
            raise HTTPException(status_code=400, detail="L'OCR n'a pas pu extraire de texte du fichier.")

        # 3. Extraire les entités avec votre modèle NER
        extracted_entities = await loop.run_in_executor(executor, extract_entities_from_text, extracted_text)

        # 4. Traiter les entités pour former les transactions et le solde
        transactions_list = []
        solde_data = None
        solde_date_str = None
        
        current_transaction_data = {}
        for entity_data in extracted_entities:
            label = entity_data.get('label')
            text = entity_data.get('text')
            
            if label == 'SOLDE':
                try:
                    solde_data = Solde(solde=float(text))
                except (ValueError, TypeError):
                    pass
            elif label == 'DATE':
                current_transaction_data['date'] = text
                solde_date_str = text
            elif label == 'LIBELLE':
                current_transaction_data['libelle'] = text
            elif label == 'MONTANT':
                if 'date' in current_transaction_data:
                    current_transaction_data['montant'] = text
                    try:
                        parsed_date = datetime.datetime.strptime(current_transaction_data['date'], "%d/%m/%Y").date()
                        transactions_list.append(
                            Transaction(
                                date=parsed_date.isoformat(),
                                libelle=current_transaction_data.get('libelle', 'N/A'),
                                montant=float(current_transaction_data['montant'])
                            )
                        )
                        current_transaction_data = {}
                    except (ValueError, TypeError, AttributeError) as e:
                        print(f"Erreur de conversion de transaction : {e}")
                        current_transaction_data = {}

        # 5. Préparer et insérer les données dans Supabase
        releve_id = str(uuid.uuid4())
        
        releve_mois = None
        if solde_date_str:
            try:
                solde_datetime = datetime.datetime.strptime(solde_date_str, "%d/%m/%Y")
                releve_mois = solde_datetime.strftime("%B %Y")
            except (ValueError, TypeError):
                pass
        
        releve_data = {
            "id": releve_id,
            "filename": file.filename,
            "content": extracted_text,
            "solde": solde_data.solde if solde_data else None,
            "releve_mois": releve_mois
        }
        
        supabase.table("releves").insert(releve_data).execute()

        if transactions_list:
            transactions_to_insert = [
                {
                    "releve_id": releve_id,
                    "date": t.date,
                    "libelle": t.libelle,
                    "montant": t.montant
                } for t in transactions_list
            ]
            supabase.table("transaction").insert(transactions_to_insert).execute()
        
        # 6. Préparer et retourner la réponse
        return ReleveResponse(
            id=releve_id,
            filename=file.filename,
            content=extracted_text,
            transactions=transactions_list,
            solde=solde_data,
            releve_mois=releve_mois
        )

    except Exception as e:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Une erreur est survenue : {str(e)}")
    finally:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)



### Les autres endpoints


@app.get("/releves", response_model=List[ReleveListItem])
async def get_all_releves():
    try:
        releves_response = supabase.table("releves").select("id, filename, solde, releve_mois").execute()
        releves_list = [
            ReleveListItem(id=r['id'], filename=r['filename'], solde=r['solde'], releve_mois=r['releve_mois'])
            for r in releves_response.data
        ]
        return releves_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/releves/{releve_id}", response_model=ReleveResponse)
async def get_releve_details(releve_id: str):
    try:
        releve_response = supabase.table("releves").select("*").eq("id", releve_id).execute()
        if not releve_response.data:
            raise HTTPException(status_code=404, detail="Releve not found")
        releve_data = releve_response.data[0]
        transactions_response = supabase.table("transaction").select("*").eq("releve_id", releve_id).order("date").execute()
        transactions_list = [
            Transaction(date=t['date'], libelle=t['libelle'], montant=t['montant'])
            for t in transactions_response.data
        ]
        solde_data = None
        if 'solde' in releve_data and releve_data['solde'] is not None:
            solde_data = Solde(solde=float(releve_data['solde']), type_solde=releve_data.get('solde_type'))
        return ReleveResponse(
            id=releve_data['id'],
            filename=releve_data['filename'],
            content=releve_data['content'],
            transactions=transactions_list,
            solde=solde_data,
            releve_mois=releve_data.get('releve_mois')
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
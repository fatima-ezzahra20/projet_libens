# Fichier : backend/app/main.py

from fastapi import FastAPI, HTTPException, UploadFile, File
from typing import List, Optional
from .database import supabase
from .models import ReleveResponse, ReleveListItem, Transaction, Solde
from .services.ner_model import extract_entities_from_text
from .services.ocr_extractor import extract_text_from_file
import uuid
import json
import os
import shutil
import asyncio
from concurrent.futures import ThreadPoolExecutor
import datetime

# Créer un executor pour gérer les tâches synchrones
executor = ThreadPoolExecutor()

app = FastAPI()

@app.post("/upload", response_model=ReleveResponse)
async def upload_releve(file: UploadFile = File(...)):
    file_path = None
    try:
        # 1. Sauvegarder le fichier temporairement
        upload_dir = "temp_uploads"
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        file_path = os.path.join(upload_dir, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 2. Extraire le texte avec l'OCR (asynchrone)
        loop = asyncio.get_event_loop()
        extracted_text = await loop.run_in_executor(executor, extract_text_from_file, file_path)
        print("Texte extrait par l'OCR :", extracted_text)
        if not extracted_text:
            raise HTTPException(status_code=400, detail="L'OCR n'a pas pu extraire de texte du fichier.")

        # 3. Extraire les entités avec votre modèle NER (asynchrone)
        extracted_entities = await loop.run_in_executor(executor, extract_entities_from_text, extracted_text)
        print("NER Model Output:", extracted_entities)

        # 4. Séparer les transactions et le solde avec une logique plus robuste
        transactions_list = []
        solde_data = None
        
        current_transaction_data = {}
        for entity_data in extracted_entities:
            label = entity_data.get('label')
            text = entity_data.get('text')
            
            if label == 'SOLDE':
                try:
                    solde_data = Solde(solde=float(text), type_solde='CREDITEUR')
                except (ValueError, TypeError):
                    pass
            elif label == 'DATE':
                current_transaction_data['date'] = text
            elif label == 'LIBELLE':
                current_transaction_data['libelle'] = text
            elif label == 'MONTANT':
                if 'date' in current_transaction_data:
                    current_transaction_data['montant'] = text
                    try:
                        # Convertir la date avant de créer l'objet Transaction
                        parsed_date = datetime.datetime.strptime(current_transaction_data['date'], "%d/%m/%Y").date()
                        transactions_list.append(
                            Transaction(
                                date=parsed_date.isoformat(),
                                libelle=current_transaction_data.get('libelle', 'N/A'),
                                montant=float(current_transaction_data['montant'])
                            )
                        )
                        current_transaction_data = {}  # Réinitialiser pour la prochaine transaction
                    except (ValueError, TypeError, AttributeError) as e:
                        print(f"Erreur de conversion de transaction : {e}")
                        current_transaction_data = {}

        # 5. Préparer et insérer les données dans Supabase
        releve_id = str(uuid.uuid4())
        releve_data = {
            "id": releve_id,
            "filename": file.filename,
            "content": extracted_text,
            "solde": solde_data.solde if solde_data else None
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
            print("Transactions à insérer :", transactions_to_insert)
            supabase.table("transaction").insert(transactions_to_insert).execute()
        
        # 6. Préparer et retourner la réponse
        return ReleveResponse(
            id=releve_id,
            filename=file.filename,
            content=extracted_text,
            transactions=transactions_list,
            solde=solde_data
        )

    except Exception as e:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Une erreur est survenue : {str(e)}")
    finally:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)

## Les autres endpoints (/releves, /releves/{releve_id})
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
            solde_data = Solde(solde=float(releve_data['solde']))
        return ReleveResponse(
            id=releve_data['id'],
            filename=releve_data['filename'],
            content=releve_data['content'],
            transactions=transactions_list,
            solde=solde_data
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
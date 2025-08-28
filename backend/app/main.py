# Fichier : backend/app/main.py

from fastapi import FastAPI, HTTPException, UploadFile, File
from typing import List
from .database import supabase
from .models import ReleveResponse, ReleveListItem, ReleveRequest  # Assurez-vous d'importer ReleveRequest si vous le réutilisez
from .services.ner_model import extract_entities_from_text
from .services.ocr_extractor import extract_text_from_file
import uuid
import json
import os
import shutil

app = FastAPI()

# Point d'accès pour l'upload d'un relevé (accepte un fichier)
@app.post("/upload", response_model=ReleveResponse)
async def upload_releve(file: UploadFile = File(...)):
    try:
        # 1. Sauvegarder le fichier temporairement
        upload_dir = "temp_uploads"
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
            
        file_path = os.path.join(upload_dir, file.filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 2. Extraire le texte avec l'OCR
        extracted_text = extract_text_from_file(file_path)
        print("Texte extrait par l'OCR :", extracted_text) 
        
        if not extracted_text:
            raise HTTPException(status_code=400, detail="L'OCR n'a pas pu extraire de texte du fichier.")
            
        # 3. Extraire les entités avec votre modèle NER
        extracted_entities = extract_entities_from_text(extracted_text)
        
        # 4. Préparer les données pour Supabase
        releve_data = {
            "id": str(uuid.uuid4()),
            "filename": file.filename,
            "content": extracted_text,
            "extracted_entities": json.dumps(extracted_entities)
        }
        
        response = supabase.table("releves").insert(releve_data).execute()
        
        # 5. Nettoyer : Supprimer le fichier temporaire
        os.remove(file_path)
        
        if response.data:
            return ReleveResponse(
                id=response.data[0]['id'],
                filename=response.data[0]['filename'],
                content=response.data[0]['content'],
                extracted_entities=extracted_entities
            )
        else:
            raise HTTPException(status_code=500, detail="Erreur lors de l'insertion dans la base de données.")

    except Exception as e:
        # Assurer la suppression du fichier même en cas d'erreur
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Une erreur est survenue : {str(e)}")

## Les autres endpoints (/releves, /releves/{releve_id})

@app.get("/releves", response_model=List[ReleveListItem])
async def get_releves():
    try:
        response = supabase.table("releves").select("id, filename, created_at").order("created_at", desc=True).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/releves/{releve_id}", response_model=ReleveResponse)
async def get_releve_details(releve_id: str):
    try:
        response = supabase.table("releves").select("*").eq("id", releve_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Releve not found")
        
        releve_data = response.data[0]
        
        return ReleveResponse(
            id=releve_data['id'],
            filename=releve_data['filename'],
            content=releve_data['content'],
            extracted_entities=releve_data['extracted_entities']
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
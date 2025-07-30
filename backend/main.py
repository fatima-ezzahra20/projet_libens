from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from ocr.ocr_utilie import ocr_image, ocr_pdf
import spacy
import os
import tempfile
import logging

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restreindre en prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)

def detecter_type_document(texte: str) -> str:
    """Détection du type de document (facture ou relevé) à partir du texte OCRisé."""
    texte = texte.lower()
    facture_keywords = ["facture", "n° facture", "tva", "client", "montant", "date d'échéance"]
    releve_keywords = ["relevé", "solde", "opération", "crédit", "débit", "date opération"]

    score_facture = sum(kw in texte for kw in facture_keywords)
    score_releve = sum(kw in texte for kw in releve_keywords)

    logging.info(f"Score facture : {score_facture} | Score relevé : {score_releve}")

    if score_facture >= score_releve:
        return "facture"
    else:
        return "releve"

@app.post("/extract")
async def extract(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename)[1].lower()
    logging.info(f"Fichier reçu : {file.filename} | Extension : {ext}")

    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name
    logging.info(f"Fichier temporaire créé : {tmp_path}")

    try:
        # === OCR ===
        if ext in [".png", ".jpg", ".jpeg"]:
            texte = ocr_image(tmp_path)
        elif ext == ".pdf":
            texte = "\n\n".join(ocr_pdf(tmp_path))
        else:
            return JSONResponse(content={"error": "Format non supporté"}, status_code=400)

        logging.info("OCR terminé.")
        
        # === Détection du type ===
        type_doc = detecter_type_document(texte)
        logging.info(f"Type de document détecté : {type_doc}")

        # === Chargement du bon modèle ===
        if type_doc == "facture":
            nlp = spacy.load("ner_facture/modele_facture")
        else:
            nlp = spacy.load("ner_releve/modele_releve")  # ← adapte ce chemin

        # === Extraction des entités ===
        doc = nlp(texte)
        entites = [{"label": ent.label_, "text": ent.text} for ent in doc.ents]
        logging.info(f"Extraction terminée. {len(entites)} entités détectées.")

    except Exception as e:
        logging.error(f"Erreur lors du traitement : {e}")
        return JSONResponse(content={"error": "Erreur interne serveur"}, status_code=500)
    finally:
        os.remove(tmp_path)
        logging.info(f"Fichier temporaire supprimé : {tmp_path}")

    return {
        "texte": texte,
        "type_document": type_doc,
        "entites": entites
    }

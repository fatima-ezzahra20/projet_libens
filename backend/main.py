from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from facture import router as factures_router
from database import supabase  
import logging
import os
import tempfile
import spacy
from ocr_facture.ocr_utilie import ocr_image, ocr_pdf

app = FastAPI()
app.include_router(factures_router)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)

def detecter_type_document(texte: str) -> str:
    """Détecte si le document est une facture ou un relevé."""
    texte = texte.lower()
    facture_keywords = ["facture", "n° facture", "tva", "client", "montant", "date d'échéance"]
    releve_keywords = ["relevé", "solde", "opération", "crédit", "débit", "date opération"]
    score_facture = sum(kw in texte for kw in facture_keywords)
    score_releve = sum(kw in texte for kw in releve_keywords)
    return "facture" if score_facture >= score_releve else "releve"


def insert_invoice(entites, user_id: int):
    """Insère la facture et ses lignes dans Supabase."""
    facture_data = {
        "num_facture": entites["num_facture"],
        "fournisseur": entites["fournisseur"],
        "montant_total_ht": entites["montant_total_ht"],
        "montant_total_ttc": entites["montant_total_ttc"],
        "date_emission": entites["date_emission"],
        "date_echeance": entites["date_echeance"],
        "rib_iban": entites.get("rib_iban"),
        "user_id": user_id,
    }

    # ✅ Insertion dans la table factures
    facture_response = supabase.table("factures").insert(facture_data).execute()
    if not facture_response.data:
        raise Exception(f"Erreur insertion facture : {facture_response}")

    facture_id = facture_response.data[0]["id"]

    # ✅ Insertion des lignes si elles existent
    for ligne in entites.get("lignes", []):
       ligne_data = {
        "facture_id": facture_id,
        "description_ligne": ligne.get("description_ligne", ""),
        "quantite": int(ligne.get("quantite", 1)),
        "prix_unitaire_ht": float(ligne.get("prix_unitaire_ht", 0)),
        "montant_ligne": float(ligne.get("montant_ligne", 0)),
      }
       supabase.table("lignes_facture").insert(ligne_data).execute()


    return {**facture_data, "id": facture_id, "lignes": entites.get("lignes", [])}


@app.get("/")
def root():
    return {"message": "Backend API is running!"}


@app.post("/factures/upload")
async def upload_facture(facture: UploadFile = File(...), user_id: int = 1):
    ext = os.path.splitext(facture.filename)[1].lower()

    # 1️⃣ Sauvegarde temporaire
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        tmp.write(await facture.read())
        tmp_path = tmp.name

    try:
        # 2️⃣ OCR
        if ext in [".png", ".jpg", ".jpeg"]:
            texte = ocr_image(tmp_path)
        elif ext == ".pdf":
            texte = "\n\n".join(ocr_pdf(tmp_path))
        else:
            return JSONResponse({"error": "Format non supporté"}, status_code=400)

        # 3️⃣ Vérifier que c'est une facture
        type_doc = detecter_type_document(texte)
        if type_doc != "facture":
            return JSONResponse({"error": "Document n'est pas une facture"}, status_code=400)

        # 4️⃣ Extraction avec SpaCy
        nlp = spacy.load("ner_facture/modele_facture")
        doc = nlp(texte)
        entites = {
            "num_facture": next((ent.text for ent in doc.ents if ent.label_ == "NUM_FACTURE"), ""),
            "fournisseur": next((ent.text for ent in doc.ents if ent.label_ == "FOURNISSEUR"), ""),
            "montant_total_ht": float(next((ent.text.replace(",", ".") for ent in doc.ents if ent.label_ == "MONTANT_HT"), 0)),
            "montant_total_ttc": float(next((ent.text.replace(",", ".") for ent in doc.ents if ent.label_ == "MONTANT_TTC"), 0)),
            "date_emission": next((ent.text for ent in doc.ents if ent.label_ == "DATE_EMISSION"), ""),
            "date_echeance": next((ent.text for ent in doc.ents if ent.label_ == "DATE_ECHEANCE"), ""),
            "rib_iban": next((ent.text for ent in doc.ents if ent.label_ == "RIB_IBAN"), None),
            "lignes": []  
        }
        
        # CORRECTION : Meilleur regroupement des lignes
        lignes = []
        ligne_courante = {}

        for ent in doc.ents:
            if ent.label_ == "DESCRIPTION_LIGNE":
                # Nouvelle ligne détectée
                if ligne_courante:  # Sauvegarder la ligne précédente
                    lignes.append(ligne_courante)
                ligne_courante = {
                    "description_ligne": ent.text,
                    "quantite": 1,
                    "prix_unitaire_ht": 0.0,
                    "montant_ligne": 0.0
                }
            elif ent.label_ == "QUANTITE" and ligne_courante:
                try:
                    ligne_courante["quantite"] = int(ent.text)
                except ValueError:
                    ligne_courante["quantite"] = 1
            elif ent.label_ == "PRIX_UNITAIRE_HT" and ligne_courante:
                try:
                    ligne_courante["prix_unitaire_ht"] = float(ent.text.replace(",", "."))
                except ValueError:
                    ligne_courante["prix_unitaire_ht"] = 0.0
            elif ent.label_ == "MONTANT_LIGNE" and ligne_courante:
                try:
                    ligne_courante["montant_ligne"] = float(ent.text.replace(",", "."))
                except ValueError:
                    ligne_courante["montant_ligne"] = 0.0

        # Ajouter la dernière ligne
        if ligne_courante:
            lignes.append(ligne_courante)

        entites["lignes"] = lignes

        # 5️⃣ Insertion Supabase
        facture_record = insert_invoice(entites, user_id)

    finally:
        os.remove(tmp_path)

    return JSONResponse(content=facture_record)

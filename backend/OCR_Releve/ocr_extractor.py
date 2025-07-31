import os
import json
import pytesseract 
from PIL import Image
from pdf2image import convert_from_path
import numpy as np
from pathlib import Path
import cv2


# === CONFIGURATION ===
CURRENT_DIR = Path(__file__).resolve().parent
ROOT_DIR = CURRENT_DIR.parent  # == backend/
DOSSIER_ENTREE = ROOT_DIR / "DATA" / "Releve" / "releve_genere_entrainement2"
DOSSIER_PNG = CURRENT_DIR / "converted_images"
OUTPUT_FILE_100 = CURRENT_DIR / "ocr_output_cleaned_100.json"
OUTPUT_FILE_INCOMP = CURRENT_DIR / "ocr_output_cleaned_incomplets.json"

TESSERACT_PATH = r"/opt/homebrew/bin/tesseract"
POPPLER_PATH = "/opt/homebrew/bin"

pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

# ===Prétraitement=== 
def preprocess_image(img_pil):
    img_cv = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    return gray

def ocr_image_lines(image: Image.Image):
    """OCR une image PIL et retourne les lignes non vides"""
    img_cv = preprocess_image(image)  

    config = r"--oem 3 --psm 6 -l fra -c preserve_interword_spaces=1" 
    text = pytesseract.image_to_string(img_cv, config=config)
    
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    return lines

def ocr_pdf_lines(pdf_path):
    """OCR toutes les pages d’un PDF et retourne les lignes nettoyées"""
    lignes_totales = []
    try:
        images = convert_from_path(pdf_path, dpi=400, poppler_path=POPPLER_PATH)
        for img in images:
            lines = ocr_image_lines(img)
            lignes_totales.extend(lines)
    except Exception as e:
        print(f"❌ Erreur traitement PDF {pdf_path}: {e}")
    return lignes_totales

def ocr_fallback_png(nom_pdf):
    """
    OCR fallback pour un PDF converti en PNG.
    """
    nom_png = nom_pdf.replace(".pdf", "_page1.png")
    chemin_png = os.path.join(DOSSIER_PNG, nom_png)
    if not os.path.exists(chemin_png):
        return [], 0.0
    img = Image.open(chemin_png)
    lignes = ocr_image_lines(img)
    score = score_ocr(lignes)
    return lignes, score

def convertir_pdf_en_png_si_mauvais_score(nom_pdf):
    """
    Convertit un PDF en PNG si nécessaire.
    """
    pdf_path = os.path.join(DOSSIER_ENTREE, nom_pdf)
    try:
        pages = convert_from_path(pdf_path, dpi=600, poppler_path=POPPLER_PATH)
        for i, page in enumerate(pages):
            nom_png = nom_pdf.replace(".pdf", f"_page{i+1}.png")
            page.save(os.path.join(DOSSIER_PNG, nom_png), "PNG")
    except Exception as e:
        print(f"⚠️ Erreur de conversion PNG pour {nom_pdf}: {e}")




# === SCORE OCR ===
def score_ocr(lines):
    """
    Calcule un score de qualité OCR basé sur la présence de mots-clés attendus.
    """
    keywords = ["DATE", "OPÉRATION", "DÉBIT", "CRÉDIT", "SOLDE", "RIB", "COMPTE"]
    score = sum(1 for kw in keywords if any(kw in l.upper() for l in lines))
    return round(score / len(keywords), 2)

# === OCR + Export JSON ligne par ligne ===
all_data = []

for filename in os.listdir(DOSSIER_ENTREE):
    filepath = os.path.join(DOSSIER_ENTREE, filename)
    ext = os.path.splitext(filename)[1].lower()

    if ext == ".pdf":
        print(f"\n📄 OCR PDF : {filename}")
        lignes = ocr_pdf_lines(filepath)
        score = score_ocr(lignes)

        if score < 1.0:
            print(f"🔁 OCR Fallback PNG pour : {filename}")
            convertir_pdf_en_png_si_mauvais_score(filename)
            lignes, score = ocr_fallback_png(filename)

        print(f"📊 {filename} : OCR coverage = {score * 100:.1f}%")

        all_data.append({
            "filename": filename,
            "lines": lignes,
            "ocr_score": score
        })

    else:
        print(f"⛔ Fichier ignoré (non-PDF) : {filename}")


# === Séparation selon score OCR
data_100 = [doc for doc in all_data if doc["ocr_score"] == 1.0]
data_incomplets = [doc for doc in all_data if doc["ocr_score"] < 1.0]

# === Sauvegarde séparée
with open("ocr_output_cleaned_100.json", "w", encoding="utf-8") as f1:
    json.dump(data_100, f1, ensure_ascii=False, indent=2)

with open("ocr_output_cleaned_incomplets.json", "w", encoding="utf-8") as f2:
    json.dump(data_incomplets, f2, ensure_ascii=False, indent=2)

print(f"\n📁 Fichier des relevés OCRisés à 100% : ocr_output_cleaned_100.json")
print(f"📁 Fichier des relevés incomplets        : ocr_output_cleaned_incomplets.json")


print(f"\n✅ OCR terminé. Résultats ligne par ligne dans : {OUTPUT_FILE}")

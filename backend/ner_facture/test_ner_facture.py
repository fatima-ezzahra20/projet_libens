import os
import json
import pytesseract
import cv2
from PIL import Image
from pdf2image import convert_from_path
import numpy as np
import spacy
from pathlib import Path

# === CONFIGURATION ===
DOSSIER_ENTREE = "../../DATA/Facture/factures_test2"   # Dossier contenant les images et PDF
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
POPPLER_PATH = r"C:\Users\user\Downloads\Release-24.08.0-0\poppler-24.08.0\Library\bin"
MODEL_DIR = Path(__file__).parent / "modele_facture"

# Initialisation
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
nlp = spacy.load(MODEL_DIR)

# === OCR sur image ===
def ocr_image(image_path):
    image = cv2.imread(image_path)
    if image is None:
        print(f"❌ Erreur lecture image : {image_path}")
        return ""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    config = r"--oem 3 --psm 6 -l fra"
    texte = pytesseract.image_to_string(gray, config=config)
    texte = " ".join(texte.split())
    return texte

# === OCR sur PDF ===
def ocr_pdf(pdf_path):
    textes = []
    try:
        images = convert_from_path(pdf_path, dpi=200, poppler_path=POPPLER_PATH)
        for img in images:
            gray = img.convert("L")
            cv_img = cv2.cvtColor(np.array(gray), cv2.COLOR_GRAY2BGR)
            config = r"--oem 3 --psm 6 -l fra"
            texte = pytesseract.image_to_string(cv_img, config=config)
            texte = " ".join(texte.split())
            textes.append(texte)
    except Exception as e:
        print(f"❌ Erreur PDF {pdf_path} : {e}")
    return textes

# === Traitement global ===
for filename in os.listdir(DOSSIER_ENTREE):
    filepath = os.path.join(DOSSIER_ENTREE, filename)
    ext = os.path.splitext(filename)[1].lower()

    textes = []
    if ext in [".jpg", ".jpeg", ".png"]:
        print(f"\n📷 OCR image : {filename}")
        textes = [ocr_image(filepath)]

    elif ext == ".pdf":
        print(f"\n📄 OCR PDF : {filename}")
        textes = ocr_pdf(filepath)

    else:
        print(f"⛔ Fichier ignoré : {filename}")
        continue

    # === Prédiction NER spaCy ===
    for i, texte in enumerate(textes):
        doc = nlp(texte)
        print(f"\n--- Résultats NER pour {filename} - page {i+1} ---")
        for ent in doc.ents:
            print(f"{ent.label_:20} : {ent.text}")

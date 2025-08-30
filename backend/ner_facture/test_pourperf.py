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
DOSSIER_ENTREE = "../../DATA/Facture/factures_test2"
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
    return " ".join(texte.split())

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
            textes.append(" ".join(texte.split()))
    except Exception as e:
        print(f"❌ Erreur PDF {pdf_path} : {e}")
    return textes

# === Génération des prédictions ===
predictions = []

for filename in os.listdir(DOSSIER_ENTREE):
    filepath = os.path.join(DOSSIER_ENTREE, filename)
    ext = os.path.splitext(filename)[1].lower()

    textes = []
    if ext in [".jpg", ".jpeg", ".png"]:
        textes = [ocr_image(filepath)]
    elif ext == ".pdf":
        textes = ocr_pdf(filepath)
    else:
        continue

    for texte in textes:
        doc = nlp(texte)
        entities = [[ent.start_char, ent.end_char, ent.label_] for ent in doc.ents]
        predictions.append([texte, {"entities": entities}])

# === Enregistrement dans predictions.json ===
output_file = os.path.join(DOSSIER_ENTREE, "predictions.json")
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(predictions, f, ensure_ascii=False, indent=2)

print(f"\n✅ Prédictions enregistrées dans {output_file}")

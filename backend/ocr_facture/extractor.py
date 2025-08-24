import os
import json
import pytesseract
import cv2
from PIL import Image
from pdf2image import convert_from_path
import numpy as np

# === CONFIGURATION ===
DOSSIER_ENTREE = "../DATA/factures_train"
OUTPUT_FILE = "ocr_output.json" 
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
POPPLER_PATH = r"C:\Users\user\Downloads\Release-24.08.0-0\poppler-24.08.0\Library\bin"

# Initialisation
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

def ocr_image(image_path):
    image = cv2.imread(image_path)
    if image is None:
        print(f"❌ Erreur lecture image : {image_path}")
        return ""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    config = r"--oem 3 --psm 6 -l fra"
    texte = pytesseract.image_to_string(gray, config=config)
    texte = " ".join(texte.split()).replace("€", " €").replace(":", " : ").replace(",", ", ")
    return texte

def ocr_pdf(pdf_path):
    textes = []
    try:
        images = convert_from_path(pdf_path, dpi=200, poppler_path=POPPLER_PATH)
        for img in images:
            gray = img.convert("L")
            cv_img = cv2.cvtColor(np.array(gray), cv2.COLOR_GRAY2BGR)
            config = r"--oem 3 --psm 6 -l fra"
            texte = pytesseract.image_to_string(cv_img, config=config)
            texte = " ".join(texte.split()).replace("€", " €").replace(":", " : ").replace(",", ", ")
            textes.append(texte)
    except Exception as e:
        print(f"❌ Erreur PDF {pdf_path} : {e}")
    return textes

# === OCR + Export
all_data = []

for filename in os.listdir(DOSSIER_ENTREE):
    filepath = os.path.join(DOSSIER_ENTREE, filename)
    ext = os.path.splitext(filename)[1].lower()

    if ext in [".jpg", ".jpeg", ".png"]:
        print(f"\n📷 OCR image : {filename}")
        texte = ocr_image(filepath)
        all_data.append({ "text": texte })

    elif ext == ".pdf":
        print(f"\n📄 OCR PDF : {filename}")
        textes = ocr_pdf(filepath)
        for texte in textes:
            all_data.append({ "text": texte })

    else:
        print(f"⛔ Fichier ignoré : {filename}")


with open(OUTPUT_FILE, "w", encoding="utf-8") as out_file:
    json.dump(all_data, out_file, ensure_ascii=False, indent=2)

print(f"\n✅ OCR terminé. Résultats enregistrés dans : {OUTPUT_FILE}")

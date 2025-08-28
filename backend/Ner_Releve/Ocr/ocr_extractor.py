import os
import json
import pytesseract 
from PIL import Image
from pdf2image import convert_from_path
import numpy as np
from pathlib import Path
import cv2
import subprocess


# === CONFIGURATION ===
CURRENT_DIR = Path(__file__).resolve().parent
ROOT_DIR = CURRENT_DIR.parent.parent  # == projet_libens/
DOSSIER_ENTREE = ROOT_DIR / "DATA" / "Releve" / "releve_genere_entrainement2"
DOSSIER_PNG = CURRENT_DIR / "converted_images"
OUTPUT_FILE_100 = CURRENT_DIR / "ocr_output_cleaned_100.json"
OUTPUT_FILE_INCOMP = CURRENT_DIR / "ocr_output_cleaned_incomplets.json"

TESSERACT_PATH = r"/opt/homebrew/bin/tesseract"
POPPLER_PATH = "/opt/homebrew/bin"
DEBUG = False  # Active les sauvegardes d'images pour debug

pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
os.makedirs(DOSSIER_PNG, exist_ok=True)
DEBUG = True


# === OCR pleine page (haut du relevé) ===
def ocr_full_page(image: Image.Image):
    config = r"--oem 3 --psm 6 -l fra+eng"
    text = pytesseract.image_to_string(image, config=config)
    return text.splitlines()

# === Prétraitement OpenCV (bas du relevé - tableau) ===
def preprocess_image(img_pil):
    img_cv = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)

    # Améliorations :
    gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    gray = cv2.adaptiveThreshold(gray, 255,
                                 cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                 cv2.THRESH_BINARY, 11, 2)

    return gray


def detect_lines_from_image(gray_img, min_height=40, max_height=70):
    height = gray_img.shape[0]
    step = 60  # Hauteur moyenne d’une ligne
    lines = []
    for y in range(0, height, step):
        line = gray_img[y:y+step, :]
        if line.shape[0] < min_height:
            continue
        lines.append(line)
    return lines

def ocr_image_lines(image: Image.Image):
    img_cv = preprocess_image(image)
    lines = []
    for line_img in detect_lines_from_image(img_cv):

        config = r"--oem 3 --psm 7 -l fra+eng"
        text = pytesseract.image_to_string(line_img, config=config).strip()
        if text:
            lines.append(text)
    return lines

# === OCR Hybride (Header + Tableau) ===
def ocr_page_hybride(img: Image.Image):
    """
    OCR hybride :
    - Haut de la page : OCR brut (en-tête).
    - Bas de la page : OCR ligne par ligne (opérations).
    """
    width, height = img.size
    top_box = img.crop((0, 0, width, int(height * 0.30)))
    bottom_box = img.crop((0, int(height * 0.30), width, height))


    lines_header = ocr_full_page(top_box)
    lines_operations = ocr_image_lines(bottom_box)
    return lines_header + lines_operations

# === OCR PDF avec découpage hybride ===
def ocr_pdf_lines(pdf_path):
    lignes_totales = []
    try:
        images = convert_from_path(pdf_path, dpi=400, poppler_path=POPPLER_PATH)
        for img in images:
            lines = ocr_page_hybride(img)
            lignes_totales.extend(lines)
    except Exception as e:
        print(f"❌ Erreur traitement PDF {pdf_path}: {e}")
    return lignes_totales

# === OCR fallback brut PNG (en cas d'erreur PDF) ===
def ocr_fallback_png(nom_pdf):
    nom_png = nom_pdf.replace(".pdf", "_page1.png")
    chemin_png = os.path.join(DOSSIER_PNG, nom_png)
    if not os.path.exists(chemin_png):
        return [], 0.0
    img = Image.open(chemin_png)
    lignes = ocr_page_hybride(img)  # Utilise aussi le mode hybride pour PNG fallback
    score = score_ocr(lignes)
    return lignes, score

def convertir_pdf_en_png_si_mauvais_score(nom_pdf):
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
    keywords = ["DATE", "OPÉRATION", "DÉBIT", "CRÉDIT", "SOLDE", "RIB", "COMPTE"]
    score = sum(1 for kw in keywords if any(kw in l.upper() for l in lines))
    return round(score / len(keywords), 2)

# === OCR + Export JSON ligne par ligne ===
all_data = []

for filename in ["attijari_releve_05.pdf"]:
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
            "ocr_score": score,
            "nombre_de_lignes": len(lignes)
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

print(f"\n📁 Fichier des relevés OCRisés à 100% : ocr_output_cleaned_complets.json")
print(f"📁 Fichier des relevés incomplets        : ocr_output_cleaned_incomplets.json")
print(f"\n✅ OCR terminé. Résultats complets : {OUTPUT_FILE_100}")
print(f"⛔ Relevés incomplets sauvegardés dans : {OUTPUT_FILE_INCOMP}")

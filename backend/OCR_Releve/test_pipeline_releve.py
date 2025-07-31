import os
from pathlib import Path
from pdf2image import convert_from_path
import pytesseract
import spacy
import json
from PIL import Image
import re

# === CONFIGURATION ===
CURRENT_DIR = Path(__file__).resolve().parent
ROOT_DIR = CURRENT_DIR.parent
PDF_DIR = ROOT_DIR / "DATA" / "Releve" / "releve_genere_test"
TMP_IMG_DIR = ROOT_DIR / "DATA" / "Releve" / "tmp_images"
MODEL_PATH = ROOT_DIR / "backend" / "Ner_Releve" / "Model"
LANG = "fra"
N = 15  # Nombre de fichiers à tester

# Préparation
os.makedirs(TMP_IMG_DIR, exist_ok=True)
os.makedirs("outputs", exist_ok=True)

# Chargement du modèle
nlp = spacy.load(MODEL_PATH)

# Liste des fichiers PDF
pdf_files = list(PDF_DIR.glob("*.pdf"))[:N]

def convert_pdf_to_images(pdf_path):
    return convert_from_path(str(pdf_path), dpi=300)

def extract_text_from_image(image: Image.Image):
    gray = image.convert("L")
    config = r"--oem 3 --psm 6"
    return pytesseract.image_to_string(gray, lang=LANG, config=config)

def process_text_with_model(text: str):
    doc = nlp(text)
    return [{"text": ent.text, "label": ent.label_} for ent in doc.ents]

def fallback_regex_entities(text: str):
    entities = []

    # 🔍 Date format DD/MM/YYYY
    match_date = re.search(r"\b\d{2}/\d{2}/\d{4}\b", text)
    if match_date:
        entities.append({"text": match_date.group(), "label": "DATE"})

    # 🔍 Montant (nombre avec ou sans , ou .)
    match_amounts = re.findall(r"\b\d{1,3}(?:[.,]\d{3})*[.,]\d{2}\b", text)
    for amount in match_amounts:
        # Exclure les dates déjà reconnues
        if not any(ent["text"] == amount for ent in entities):
            entities.append({"text": amount, "label": "MONTANT"})

    # 🔍 Solde avec libellé explicite
    if "NOUVEAU SOLDE" in text.upper() and not any(e["label"] == "SOLDE" for e in entities):
        if match_amounts:
            entities.append({"text": match_amounts[-1], "label": "SOLDE"})

    return entities

# Résultats finaux
results = {}

print(f"\n📥 {len(pdf_files)} PDF trouvés dans {PDF_DIR.resolve()}")

for pdf in pdf_files:
    print(f"\n📄 Traitement du fichier : {pdf.name}")
    images = convert_pdf_to_images(pdf)
    print(f"🖼 {len(images)} page(s) convertie(s)")

    file_results = []

    for i, img in enumerate(images):
        img_path = TMP_IMG_DIR / f"{pdf.stem}_page_{i+1}.png"
        img.save(img_path)
        text = extract_text_from_image(img)
        print(f"📝 Texte OCR page {i+1} extrait...\n")

        lines = [line.strip() for line in text.strip().split("\n") if line.strip()]

        for line in lines:
            entities = process_text_with_model(line)

            if not entities:
                # Utilise fallback regex si aucune entité détectée par spaCy
                entities = fallback_regex_entities(line)

            if entities:
                file_results.append({
                    "text": line,
                    "entities": entities
                })
                print(f"🧾 Ligne gardée : {line}")
                for ent in entities:
                    print(f"→ {ent['label']}: {ent['text']}")

    results[pdf.name] = file_results

# Sauvegarde des résultats
OUTPUT_PATH = Path(__file__).resolve().parent / "outputs" / "test_ner_results_filtered.json"
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print("\n✅ Test terminé. Résultats enregistrés dans outputs/test_ner_results_filtered.json")

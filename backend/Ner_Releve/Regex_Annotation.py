import json
import re

INPUT_FILE = "../OCR/ocr_output_cleaned.json"   # Ton fichier ligne par ligne
OUTPUT_FILE = "train_data_global.json"          # Nouveau fichier annoté

# === REGEX patterns ===
date_pattern = r"\b\d{2}/\d{2}/\d{4}\b"
amount_pattern = r"\d{1,3}(?:[., ]\d{3})*(?:[.,]\d{2})"
solde_keywords = ["SOLDE", "NOUVEAU SOLDE", "SOLDE FINAL"]
libelle_keywords = [
    "VIREMENT", "RETRAIT", "PAIEMENT", "VERSEMENT", "CHÈQUE", "CHEQUE",
    "FRAIS", "REMBOURSEMENT", "AGIOS", "COTISATION", "INTÉRÊTS", "INTERNET"
]

# Fonction anti-chevauchement
def is_overlapping(start, end, entities):
    for s, e, _ in entities:
        if start < e and end > s:
            return True
    return False

# Fonction d’annotation d’une ligne de texte
def annotate_text(text):
    entities = []

    # 1. Solde
    for sk in solde_keywords:
        for match in re.finditer(rf"{sk}.*?{amount_pattern}", text, re.IGNORECASE):
            montant = re.search(amount_pattern, match.group())
            if montant:
                start = match.start() + montant.start()
                end = match.start() + montant.end()
                if not is_overlapping(start, end, entities):
                    entities.append((start, end, "SOLDE"))

    # 2. Montants
    for m in re.finditer(amount_pattern, text):
        start, end = m.start(), m.end()
        if not is_overlapping(start, end, entities):
            entities.append((start, end, "MONTANT"))

    # 3. Dates
    for m in re.finditer(date_pattern, text):
        start, end = m.start(), m.end()
        if not is_overlapping(start, end, entities):
            entities.append((start, end, "DATE"))

    # 4. Libellés
    for word in libelle_keywords:
        for m in re.finditer(rf"\b{word}\b", text, re.IGNORECASE):
            start, end = m.start(), m.end()
            if not is_overlapping(start, end, entities):
                entities.append((start, end, "LIBELLE"))

    return entities

# === Traitement principal ===
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    docs = json.load(f)

training_data = []
for doc in docs:
    lines = doc.get("lines", [])
    for line in lines:
        line = line.strip()
        if line:  # ignorer les lignes vides
            entities = annotate_text(line)
            training_data.append({
                "text": line,
                "entities": entities
            })

# === Sauvegarde ===
with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
    json.dump(training_data, out, ensure_ascii=False, indent=2)

print(f"✅ Données d'entraînement générées avec succès ligne par ligne : {OUTPUT_FILE}")


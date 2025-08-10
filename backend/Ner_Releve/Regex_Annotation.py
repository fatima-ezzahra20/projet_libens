import json
import re

# === FICHIERS ===
INPUT_FILE = "../OCR_Releve/outputs/batch/ocr_batch_results.json" 
OUTPUT_FILE = "train_data_global.json"          # Résultat avec annotations

# === PATTERNS ===
date_pattern = r"\b\d{2}/\d{2}/\d{4}\b"
amount_pattern = r"\d{1,3}(?:[., ]\d{3})*(?:[.,]\d{2})"
solde_keywords = ["SOLDE", "NOUVEAU SOLDE", "SOLDE FINAL"]
libelle_keywords = [
    "VIREMENT", "RETRAIT", "PAIEMENT", "VERSEMENT", "CHÈQUE", "CHEQUE",
    "FRAIS", "REMBOURSEMENT", "AGIOS", "COTISATION", "INTÉRÊTS","ACHAT","PRÉLÈVEMENT","REMISE", "INTERNET"
]

# === FONCTION anti-chevauchement ===
def is_overlapping(start, end, entities):
    for s, e, _ in entities:
        if start < e and end > s:
            return True
    return False

# === FONCTION D’ANNOTATION ===

def annotate_text(text):
    entities = []

    # 1. Chercher la DATE et le MONTANT sur la même ligne
    date_match = re.search(date_pattern, text)
    amount_match = re.search(amount_pattern, text)

    if date_match:
        entities.append((date_match.start(), date_match.end(), "DATE"))
    if amount_match:
        entities.append((amount_match.start(), amount_match.end(), "MONTANT"))

    # 2. Annoter LIBELLE = texte entre date et montant
    if date_match and amount_match and amount_match.start() > date_match.end():
        start_lib = date_match.end() + 1
        end_lib = amount_match.start() - 1
        if not is_overlapping(start_lib, end_lib, entities):
            entities.append((start_lib, end_lib, "LIBELLE"))

    # 3. Annoter SOLDE si présence des mots-clés
    for sk in solde_keywords:
        for match in re.finditer(rf"{sk}.*?{amount_pattern}", text, re.IGNORECASE):
        # Rechercher le montant directement dans la sous-chaîne matchée
            sub_text = match.group()
            sub_start = match.start()
            montant_match = re.search(amount_pattern, sub_text)
            if montant_match:
               start = sub_start + montant_match.start()
               end = sub_start + montant_match.end()
               if not is_overlapping(start, end, entities):
                  entities.append((start, end, "SOLDE"))

    return entities

# === TRAITEMENT PRINCIPAL ===
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    docs = json.load(f)

training_data = []
for doc in docs:
    for line in doc.get("lines", []):
        line = line.strip()
        if not line:
            continue
        entities = annotate_text(line)
        training_data.append({
            "text": line,
            "entities": entities
        })

# === SAUVEGARDE ===
with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
    json.dump(training_data, out, ensure_ascii=False, indent=2)

print(f"✅ Annotations enregistrées dans : {OUTPUT_FILE}")

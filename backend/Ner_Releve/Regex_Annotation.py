import json
import re

# === FICHIERS ===
INPUT_FILE = "../OCR_Releve/outputs/test_validation/ocr_batch_results.json" 
OUTPUT_FILE = "../OCR_Releve/outputs/test_validation/test_results.json"          # Résultat avec annotations

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

    # 1. Chercher la DATE sur la ligne
    date_match = re.search(date_pattern, text)
    if date_match:
        entities.append((date_match.start(), date_match.end(), "DATE"))

    # 2. Annoter SOLDE si présence des mots-clés, mémoriser les positions SOLDE
    solde_positions = []
    for sk in solde_keywords:
        for match in re.finditer(rf"{sk}.*?{amount_pattern}", text, re.IGNORECASE):
            sub_text = match.group()
            sub_start = match.start()
            montant_match = re.search(amount_pattern, sub_text)
            if montant_match:
                start = sub_start + montant_match.start()
                end = sub_start + montant_match.end()
                if not is_overlapping(start, end, entities):
                    entities.append((start, end, "SOLDE"))
                    solde_positions.append((start, end))

    # 3. Chercher le premier montant classique (amount_match)
    amount_match = re.search(amount_pattern, text)
    if amount_match:
        start = amount_match.start()
        end = amount_match.end()
        # Vérifier si ce montant n'est pas déjà annoté comme SOLDE
        is_solde = any(start >= s and end <= e for s, e in solde_positions)
        if not is_solde:
            if not is_overlapping(start, end, entities):
                entities.append((start, end, "MONTANT"))

    # 4. Annoter LIBELLE = texte entre date et premier montant/solde
    if date_match and (amount_match or solde_positions):
        start_lib = date_match.end() + 1
        # Trouver la position la plus proche après la date parmi montants et soldes
        candidate_positions = solde_positions[:]
        if amount_match:
            candidate_positions.append((amount_match.start(), amount_match.end()))
        candidate_positions = sorted(candidate_positions, key=lambda x: x[0])
        end_lib = None
        for s, e in candidate_positions:
            if s > start_lib:
                end_lib = s - 1
                break
        if end_lib and end_lib > start_lib:
            if not is_overlapping(start_lib, end_lib, entities):
                entities.append((start_lib, end_lib, "LIBELLE"))

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

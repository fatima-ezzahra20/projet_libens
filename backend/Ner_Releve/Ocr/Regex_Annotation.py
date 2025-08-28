import json
import re

# === FICHIERS ===
INPUT_FILE = "entrainement/entrainement_ocirisation.json"
OUTPUT_FILE = "entrainement/entrainement_annotation.json"  # Résultat avec annotations

# === PATTERNS ===
# Motif de date plus flexible pour gérer les erreurs d'OCR (ex: 17104 -> 17/04)
date_pattern = r"\b\d{1,2}[\/|l]\d{1,2}[\/|l]\d{4}\b"

# Motif de montant plus flexible
amount_pattern = r"[\d\s]{1,3}(?:[.,][\s\d]{3})*(?:[.,]\d{2})"

solde_keywords = ["SOLDE", "NOUVEAU SOLDE", "SOLDE FINAL"]


# === FONCTION D’ANNOTATION AMÉLIORÉE ===
def annotate_text(text: str):
    entities = []

    # 1. Annoter toutes les dates et montants
    all_matches = []

    for match in re.finditer(date_pattern, text):
        all_matches.append((match.start(), match.end(), "DATE", match.group()))

    for match in re.finditer(amount_pattern, text):
        all_matches.append((match.start(), match.end(), "RAW_AMOUNT", match.group()))

    all_matches.sort(key=lambda x: x[0])

    # 2. Labéliser les SOLDE et MONTANT et identifier les libellés
    final_entities = []

    # 2.1 Traitement des soldes
    solde_match = re.search(
        r"(?:NOUVEAU\s+SOLDE|SOLDE)\s+AU.*?(\d{1,3}(?:[., ]\d{3})*(?:[.,]\d{2}))",
        text,
        re.IGNORECASE,
    )
    if solde_match:
        start_solde = solde_match.start(1)
        end_solde = solde_match.end(1)
        final_entities.append((start_solde, end_solde, "SOLDE"))

    # 2.2 Traitement des transactions (date, libellé, montant)
    temp_entities = []
    for match in all_matches:
        if match[2] == "DATE":
            temp_entities.append(match)
        elif match[2] == "RAW_AMOUNT":
            # Si le montant n'est pas un solde
            is_solde = any(e[0] == match[0] and e[2] == "SOLDE" for e in final_entities)
            if not is_solde:
                temp_entities.append((match[0], match[1], "MONTANT", match[3]))

    # 2.3 Associer les entités
    for i in range(len(temp_entities)):
        if temp_entities[i][2] == "DATE":
            date_end = temp_entities[i][1]
            next_entity_start = len(text)

            # Chercher le prochain montant sur la même ligne
            for j in range(i + 1, len(temp_entities)):
                if temp_entities[j][2] == "MONTANT":
                    next_entity_start = temp_entities[j][0]
                    break

            # Le libellé est le texte entre la date et le prochain montant
            start_lib = date_end
            end_lib = next_entity_start

            if end_lib > start_lib:
                libelle_text = text[start_lib:end_lib].strip()
                # On annotera le libellé s'il y a du texte entre la date et le montant
                if libelle_text:
                    final_entities.append((start_lib, end_lib, "LIBELLE"))

            # Ajouter la date et le montant à la liste finale
            final_entities.append((temp_entities[i][0], temp_entities[i][1], "DATE"))
            for j in range(i + 1, len(temp_entities)):
                if temp_entities[j][2] == "MONTANT":
                    final_entities.append(
                        (temp_entities[j][0], temp_entities[j][1], "MONTANT")
                    )
                    break

    # Retirer les doublons et les entités vides
    unique_entities = []
    seen = set()
    for entity in final_entities:
        if (entity[0], entity[1], entity[2]) not in seen and entity[1] > entity[0]:
            unique_entities.append(entity)
            seen.add((entity[0], entity[1], entity[2]))

    # Trier pour la cohérence
    unique_entities.sort(key=lambda x: x[0])

    return unique_entities


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

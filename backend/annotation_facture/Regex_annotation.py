import json
import re
from tqdm import tqdm


def extraire_entites(texte):
    entities = []

    # NUM_FACTURE
    if match := re.search(r'FACTURE N[°º]?\s*(FAC-\d+)', texte, re.IGNORECASE):
        entities.append([match.start(1), match.end(1), "NUM_FACTURE"])

    # DATE_EMISSION
    if match := re.search(r"Date d['’]émission\s*:\s*(\d{4}-\d{2}-\d{2})", texte):
        entities.append([match.start(1), match.end(1), "DATE_EMISSION"])

    # DATE_ECHEANCE
    if match := re.search(r"Date d['’]échéance\s*:\s*(\d{4}-\d{2}-\d{2})", texte):
        entities.append([match.start(1), match.end(1), "DATE_ECHEANCE"])

    # FOURNISSEUR
    if match := re.search(r'Fournisseur\s+Client\s+([A-Za-zÀ-ÿ\'\-\s]+?)(?:\s+Tél|:|\n)', texte):
        entities.append([match.start(1), match.end(1), "FOURNISSEUR"])

       

    # RIB/IBAN
    if match := re.search(r'RIB\s*:\s*([A-Z]{2}\d{2}(?:\s?\d{5}){4,5})', texte):
        entities.append([match.start(1), match.end(1), "RIB_IBAN"])

    # MONTANT_HT
    if match := re.search(r'Total HT\s*:\s*([\d.,]+)', texte, re.IGNORECASE):
        entities.append([match.start(1), match.end(1), "MONTANT_HT"])

    # MONTANT_TTC
    if match := re.search(r'Total TTC\s*:\s*([\d.,]+)', texte, re.IGNORECASE):
        entities.append([match.start(1), match.end(1), "MONTANT_TTC"])

    # LIGNES PRODUITS
    lignes = re.findall(r"([\wÀ-ÿ\s'’]+)\s+(\d+)\s+([\d.]+)\s+([\d.]+)", texte)
    for ligne in lignes:
        description, quantite, pu, total = ligne
        # On cherche les index dans le texte (attention à la duplication possible)
        desc_match = re.search(re.escape(description.strip()), texte)
        if desc_match:
            entities.append([desc_match.start(), desc_match.end(), "DESCRIPTION_LIGNE"])
        q_match = re.search(rf"\b{quantite}\b", texte)
        if q_match:
            entities.append([q_match.start(), q_match.end(), "QUANTITE"])
        pu_match = re.search(rf"\b{pu}\b", texte)
        if pu_match:
            entities.append([pu_match.start(), pu_match.end(), "PRIX_UNITAIRE_HT"])
        total_match = re.search(rf"\b{total}\b", texte)
        if total_match:
            entities.append([total_match.start(), total_match.end(), "MONTANT_LIGNE"])

    return entities


def remove_overlapping_entities(entities):
    # Trier les entités par position de début
    entities = sorted(entities, key=lambda x: x[0])
    non_overlapping = []
    last_end = -1

    for start, end, label in entities:
        if start >= last_end:
            non_overlapping.append((start, end, label))
            last_end = end
        else:
            print(f"⚠️  Conflit détecté entre {label} et une entité précédente.")
    return non_overlapping
# Charger le fichier JSON OCR
with open("../ocr_facture/ocr_output_test.json", "r", encoding="utf-8") as f:
    factures = json.load(f)
# Construire le fichier d'annotations (format [texte, {"entities": [...]}])
annotations = []

for facture in tqdm(factures, desc="📝 Génération annotations"):
    texte = facture["text"]
    entites = extraire_entites(texte)
    entites = remove_overlapping_entities(entites)
    annotations.append([
        texte,
        {
            "entities": entites
        }
    ])

# Sauvegarder au format demandé
with open("../ner_facture/test_data.json", "w", encoding="utf-8") as f:
    json.dump(annotations, f, ensure_ascii=False, indent=2)

print("✅ Annotations automatiques générées pour toutes les factures !")

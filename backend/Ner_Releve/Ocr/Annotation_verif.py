import json
import re

def correct_annotations_improved(data):
    """
    Corrects annotations in a JSON file by fixing mislabeled amounts and
    removing duplicate or overlapping 'MONTANT' entities.
    """
    corrected_data = []

    amount_regex = re.compile(r'\s(\d+\.\d{1,2})$')

    for item in data:
        text = item['text']
        entities = item.get('entities', [])
        
        match = amount_regex.search(text)
        
        # Start with a new, empty list of entities
        new_entities = []

        if match:
            amount_start = match.start(1)
            amount_end = match.end(1)
            
            # This is the new, correct MONTANT entity
            correct_montant = [amount_start, amount_end, "MONTANT"]

            # Filter out all existing MONTANT entities
            for entity in entities:
                if entity[2] != "MONTANT":
                    # Check for LIBELLE that needs correction
                    if entity[2] == "LIBELLE" and entity[1] > amount_start:
                        # Trim the LIBELLE to end just before the amount
                        entity[1] = amount_start - 1
                    
                    new_entities.append(entity)
            
            # Add the new, correct MONTANT entity
            new_entities.append(correct_montant)

        else:
            # If no amount is found at the end, keep all original entities
            new_entities = entities
        
        # Sort the entities to maintain a consistent order
        new_entities.sort(key=lambda x: x[0])
        
        corrected_item = {
            "text": text,
            "entities": new_entities
        }
        corrected_data.append(corrected_item)

    return corrected_data

# === EXÉCUTION DU SCRIPT ===
if __name__ == "__main__":
    INPUT_FILE = "_annotation_test_corrige.json"
    OUTPUT_FILE = "annotation_test_final.json"
    
    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            data_to_correct = json.load(f)
    except FileNotFoundError:
        print(f"Erreur : Le fichier '{INPUT_FILE}' est introuvable.")
        data_to_correct = None

    if data_to_correct:
        print("Début de la correction des chevauchements d'annotations...")
        corrected_data = correct_annotations_improved(data_to_correct)
        
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(corrected_data, f, indent=2, ensure_ascii=False)
        
        print(f"Correction terminée. Les données finales sont sauvegardées dans '{OUTPUT_FILE}'")
    else:
        print("Opération annulée.")
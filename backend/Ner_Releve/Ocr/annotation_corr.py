import json
import re

# === FICHIERS ===
INPUT_FILE = "test_val/annotation_test.json"
OUTPUT_FILE = "_annotation_test_corrige.json"

def correct_annotations(file_path):
    """
    Corrects annotations in a JSON file where single-decimal amounts
    are mislabeled as part of the 'LIBELLE'.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Erreur : Le fichier '{file_path}' est introuvable.")
        return None

    corrected_data = []

    # Regex to find a number with a decimal at the end of the string
    amount_regex = re.compile(r'\s(\d+\.\d{1,2})$')

    for item in data:
        text = item['text']
        entities = item.get('entities', [])
        
        match = amount_regex.search(text)
        
        if match:
            amount_start = match.start(1)
            amount_end = match.end(1)
            
            is_amount_annotated = any(
                entity[2] == "MONTANT" and entity[0] == amount_start
                for entity in entities
            )
            
            if not is_amount_annotated:
                for entity in entities:
                    if entity[2] == "LIBELLE" and entity[1] == amount_end:
                        entity[1] = amount_start - 1
                
                entities.append([amount_start, amount_end, "MONTANT"])
        
        entities.sort(key=lambda x: x[0])
        
        corrected_item = {
            "text": text,
            "entities": entities
        }
        corrected_data.append(corrected_item)

    return corrected_data

# === EXÉCUTION DU SCRIPT ===
if __name__ == "__main__":
    print("Début de la correction des annotations...")
    
    # 1. Appeler la fonction de correction
    corrected_data = correct_annotations(INPUT_FILE)

    if corrected_data:
        # 2. Sauvegarder les données corrigées dans le fichier de sortie
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(corrected_data, f, indent=2, ensure_ascii=False)
        
        print(f"Correction terminée. Données sauvegardées dans '{OUTPUT_FILE}'")
    else:
        print("La correction n'a pas pu être effectuée en raison d'une erreur.")
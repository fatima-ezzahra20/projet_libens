import json
import re

def correct_annotations_final(data):
    """
    Corrects annotations by removing leading spaces from LIBELLE entities.
    """
    corrected_data = []

    for item in data:
        text = item['text']
        entities = item.get('entities', [])
        
        corrected_entities = []
        for entity in entities:
            start, end, label = entity
            
            # Correction pour l'entité LIBELLE
            if label == "LIBELLE":
                # Check if the entity starts with a space and remove it
                if text[start] == ' ':
                    start += 1
                
                # Check for a specific case like "VIREMENT REGU DE M. AHMED BENNANI"
                # where the label ends with an extra character or a space.
                # We can correct it by looking at the next character.
                if text[end-1] == ' ' or text[end-1] == 'A':
                    end -= 1

            corrected_entities.append([start, end, label])

        # Sort the entities to maintain a consistent order
        corrected_entities.sort(key=lambda x: x[0])
        
        corrected_item = {
            "text": text,
            "entities": corrected_entities
        }
        corrected_data.append(corrected_item)

    return corrected_data

# === EXÉCUTION DU SCRIPT ===
if __name__ == "__main__":
    # Assurez-vous que l'input est le fichier d'annotation actuel
    INPUT_FILE = "annotation_test_final.json"
    OUTPUT_FILE = "annotation_test_final_labelle.json"
    
    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            data_to_correct = json.load(f)
    except FileNotFoundError:
        print(f"Erreur : Le fichier '{INPUT_FILE}' est introuvable. Veuillez vérifier le chemin.")
        data_to_correct = None

    if data_to_correct:
        print("Début du nettoyage des annotations...")
        corrected_data = correct_annotations_final(data_to_correct)
        
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(corrected_data, f, indent=2, ensure_ascii=False)
        
        print(f"Nettoyage terminé. Les données finales sont sauvegardées dans '{OUTPUT_FILE}'")
    else:
        print("Opération annulée.")
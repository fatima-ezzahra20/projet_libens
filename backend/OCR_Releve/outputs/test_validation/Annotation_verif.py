import json

def validate_json_annotations(file_path):
    """
    Vérifie l'intégrité des annotations dans un fichier JSON.
    Retourne True si aucune erreur n'est trouvée, sinon affiche les erreurs et retourne False.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Erreur: Le fichier '{file_path}' n'a pas été trouvé.")
        return False
    except json.JSONDecodeError:
        print(f"Erreur: Le fichier '{file_path}' n'est pas un JSON valide.")
        return False

    is_valid = True
    print(f"📝 Démarrage de la vérification du fichier : {file_path}\n")

    for i, item in enumerate(data):
        text = item.get("text", "")
        entities = item.get("entities", [])
        
        # Vérifie si le champ 'text' et 'entities' existent
        if not isinstance(text, str):
            print(f"❌ Erreur à l'exemple {i+1}: 'text' doit être une chaîne de caractères.")
            is_valid = False
            continue

        if not isinstance(entities, list):
            print(f"❌ Erreur à l'exemple {i+1}: 'entities' doit être une liste.")
            is_valid = False
            continue

        # Vérifier les indices
        for start, end, label in entities:
            if not (0 <= start <= end <= len(text)):
                print(f"❌ Erreur à l'exemple {i+1}: Indices invalides ({start}, {end}) pour le texte de longueur {len(text)}.")
                is_valid = False
                
            # Vérifier que l'entité n'est pas vide
            if start == end:
                print(f"❌ Erreur à l'exemple {i+1}: Entité vide trouvée à ({start}, {end}).")
                is_valid = False

            # Vérifier le contenu de l'entité
            annotated_text = text[start:end]
            if not annotated_text.strip():
                print(f"⚠️ Avertissement à l'exemple {i+1}: L'entité pour le label '{label}' est un espace vide.")

        # Vérifier les chevauchements
        if len(entities) > 1:
            entities.sort(key=lambda x: x[0])
            for j in range(len(entities) - 1):
                start1, end1, label1 = entities[j]
                start2, end2, label2 = entities[j+1]
                if start2 < end1:
                    print(f"❌ Erreur à l'exemple {i+1}: Chevauchement d'entités entre '{text[start1:end1]}' ({label1}) et '{text[start2:end2]}' ({label2}).")
                    is_valid = False
    
    if is_valid:
        print("✅ Le fichier d'annotations est bien formaté et ne contient pas d'erreurs évidentes.")
    else:
        print("\n🚫 Des erreurs ont été trouvées dans le fichier. Veuillez les corriger.")
    
    return is_valid

# Exemple d'utilisation
if __name__ == "__main__":
    file_to_check = "test_results.json"  
    validate_json_annotations(file_to_check)
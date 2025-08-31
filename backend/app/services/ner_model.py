import spacy
import json

import os


# Calcule le chemin absolu de la racine de votre projet
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Correction : Le chemin doit être construit directement depuis la racine du projet
MODEL_PATH = os.path.join(BASE_DIR,  "Ner_Releve", "Model")

nlp = None

def get_model():
    """Charge le modèle spaCy si ce n'est pas déjà fait."""
    global nlp
    if nlp is None:
        print("⏳ Chargement du modèle spaCy...")
        nlp = spacy.load(MODEL_PATH)
    return nlp

def extract_entities_from_text(text: str):
    """
    Utilise le modèle NER pour extraire les entités d'un texte.
    """
    nlp_model = get_model()
    doc = nlp_model(text)
    
    entities = []
    for ent in doc.ents:
        entities.append({"text": ent.text, "label": ent.label_})
        
    return entities
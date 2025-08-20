import json
import spacy
from spacy.scorer import Scorer
from spacy.training import Example

# === CONFIG ===
MODEL_PATH = "../../../Ner_Releve/Model/" # chemin vers ton modèle entraîné
                       
TEST_DATA_FILE = "test_results.json"  # annotations auto générées

# === 1. Charger le modèle spaCy ===
print("⏳ Chargement du modèle spaCy...")
nlp = spacy.load(MODEL_PATH)

# === 2. Charger les données de test ===
with open(TEST_DATA_FILE, "r", encoding="utf-8") as f:
    test_data = json.load(f)

print(f"📄 {len(test_data)} exemples de test chargés")

# === 3. Préparer les exemples spaCy ===
examples = []
for item in test_data:
    # 1. Créer le document PREDIT en le passant par le modèle
    doc = nlp(item["text"])
    
    # 2. Créer un dictionnaire de référence (gold_dict) avec les annotations réelles
    gold_dict = {"entities": item["entities"]}
    
    # 3. Créer l'objet Example qui compare le document prédit et les annotations réelles
    examples.append(Example.from_dict(doc, gold_dict))

# === 4. Évaluation ===
scorer = Scorer()
scores = scorer.score(examples)

print("\n=== Résultats du modèle ===")
print(f"Precision : {scores['ents_p']:.2f}")
print(f"Recall    : {scores['ents_r']:.2f}")
print(f"F1-score  : {scores['ents_f']:.2f}")

# === 5. (Optionnel) Afficher quelques prédictions ===
print("\n=== Exemples de prédictions ===")
for i, item in enumerate(test_data[:5]):  # juste 5 lignes pour aperçu
    doc = nlp(item["text"])
    print(f"Texte: {item['text']}")
    print("Vrai :", [(item['text'][s:e], label) for s, e, label in item["entities"]])
    print("Prédit :", [(ent.text, ent.label_) for ent in doc.ents])
    print("---")

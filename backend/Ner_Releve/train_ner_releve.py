import spacy
from spacy.training.example import Example
import random
import json
from pathlib import Path
import os

# === 1. Chargement des données d'entraînement ===
DATA_PATH = Path(__file__).parent / "train_data_global.json"

with DATA_PATH.open(encoding="utf-8") as f:
    raw_data = json.load(f)

# Conversion au format attendu par spaCy [(text, {"entities": [...]})]
TRAIN_DATA = [(entry["text"], {"entities": entry["entities"]}) for entry in raw_data]
print(f"📄 {len(TRAIN_DATA)} exemples chargés depuis {DATA_PATH}")

# === 2. Création du modèle spaCy vierge avec pipeline NER ===
nlp = spacy.blank("fr")
if "ner" not in nlp.pipe_names:
    ner = nlp.add_pipe("ner", last=True)
else:
    ner = nlp.get_pipe("ner")

# Ajout dynamique des labels
labels = {label for _, ann in TRAIN_DATA for _, _, label in ann["entities"]}
for label in labels:
    ner.add_label(label)
print("🏷️ Labels ajoutés :", labels)

# === 3. Initialisation & entraînement ===
nlp.initialize()

n_iter = 40
dropout = 0.3
batch_size = 8

for epoch in range(n_iter):
    random.shuffle(TRAIN_DATA)
    losses = {}

    batches = spacy.util.minibatch(TRAIN_DATA, size=batch_size)
    for batch in batches:
        examples = [Example.from_dict(nlp.make_doc(text), ann) for text, ann in batch]
        nlp.update(examples, drop=dropout, losses=losses)

    print(f"🔁 Époque {epoch+1}/{n_iter} | Perte : {losses.get('ner', 0):.4f}")

# === 4. Sauvegarde du modèle ===
output_dir = Path("Model/")
output_dir.mkdir(exist_ok=True)
nlp.to_disk(output_dir)
print(f"✅ Modèle entraîné sauvegardé dans : {output_dir.resolve()}")

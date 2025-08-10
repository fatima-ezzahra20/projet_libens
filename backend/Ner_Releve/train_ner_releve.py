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

# Vérification des entités (évite erreurs d'entraînement)
TRAIN_DATA = []
for entry in raw_data:
    text = entry["text"]
    entities = []
    for start, end, label in entry["entities"]:
        if 0 <= start < end <= len(text):
            entities.append((start, end, label))
    TRAIN_DATA.append((text, {"entities": entities}))

print(f"📄 {len(TRAIN_DATA)} exemples chargés depuis {DATA_PATH}")

# === 2. Création ou rechargement du modèle spaCy ===
output_dir = Path("Model/")
if output_dir.exists():
    print("📦 Rechargement du modèle existant pour fine-tuning...")
    nlp = spacy.load(output_dir)
    ner = nlp.get_pipe("ner")
else:
    nlp = spacy.blank("fr")
    ner = nlp.add_pipe("ner")

# Ajout dynamique des labels
labels = {label for _, ann in TRAIN_DATA for _, _, label in ann["entities"]}
for label in labels:
    ner.add_label(label)
print("🏷️ Labels ajoutés :", labels)

# === 3. Initialisation & entraînement ===
if not output_dir.exists():
    nlp.initialize()

n_iter = 40
dropout = 0.3
batch_size = 8

loss_log = []

for epoch in range(n_iter):
    random.shuffle(TRAIN_DATA)
    losses = {}

    batches = spacy.util.minibatch(TRAIN_DATA, size=batch_size)
    for batch in batches:
        examples = [Example.from_dict(nlp.make_doc(text), ann) for text, ann in batch]
        nlp.update(examples, drop=dropout, losses=losses)

    epoch_loss = losses.get("ner", 0.0)
    print(f"🔁 Époque {epoch+1}/{n_iter} | Perte : {epoch_loss:.4f}")
    loss_log.append(f"{epoch+1},{epoch_loss:.4f}")

# === 4. Sauvegarde du modèle ===
output_dir.mkdir(exist_ok=True)
nlp.to_disk(output_dir)
print(f"✅ Modèle entraîné sauvegardé dans : {output_dir.resolve()}")

# === 5. Sauvegarde des pertes (facultatif) ===
with open(output_dir / "losses.txt", "w") as f:
    for line in loss_log:
        f.write(line + "\n")

# === 6. Exemple de prédiction ===
print("\n=== EXEMPLE DE PRÉDICTION ===")
test_text = "03/04/2025 VERSEMENT DE SALAIRE MENSUEL 7483.25"
doc = nlp(test_text)
for ent in doc.ents:
    print(f"{ent.text} -> {ent.label_}")

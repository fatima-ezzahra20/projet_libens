"""
Entraîne un modèle spaCy NER pour extraire les champs d'une facture :
FOURNISSEUR, NUM_FACTURE, DATE_EMISSION, DATE_ECHEANCE,
DESCRIPTION_LIGNE, QUANTITE, PRIX_UNITAIRE_HT, MONTANT_HT,
MONTANT_TTC, RIB_IBAN
"""

import spacy
from spacy.training.example import Example
import random
import json
import pathlib
import os

# ------------------------------------------------------------------
# 1) Charger le jeu d'entraînement (train_data.json dans le même dossier)
# ------------------------------------------------------------------
DATA_PATH = pathlib.Path(__file__).parent / "annotations_auto.json"

with DATA_PATH.open(encoding="utf-8") as f:
    TRAIN_DATA = json.load(f)
print(f"📄  {len(TRAIN_DATA)} exemples chargés depuis {DATA_PATH}")    


# ------------------------------------------------------------------
# 2) Créer un modèle spaCy vierge en français + composant NER
# ------------------------------------------------------------------
nlp = spacy.blank("fr")              # modèle vide => plus rapide à entraîner
ner = nlp.add_pipe("ner", last=True)

# Ensemble des étiquettes à apprendre (récupérées du JSON)
LABELS = {
    label
    for _, ann in TRAIN_DATA
    for _, _, label in ann["entities"]
}

for label in LABELS:
    ner.add_label(label)
print("🏷️  Labels ajoutés :", LABELS)

# ------------------------------------------------------------------
# 3) Boucle d'entraînement
# ------------------------------------------------------------------
n_iter = 30              # nombre d'époques
dropout = 0.25           # dropout régularisation

nlp.initialize()         # initialise les poids

for epoch in range(1, n_iter + 1):
    random.shuffle(TRAIN_DATA)
    losses = {}

    batches = spacy.util.minibatch(TRAIN_DATA, size=8)
    for batch in batches:
        for texts, annotations in batch:
            example = Example.from_dict(nlp.make_doc(texts), annotations)
            nlp.update([example], drop=dropout, losses=losses)

    print(f"Époque {epoch:02d} | Loss = {losses.get('ner', 0.0):.4f}")


print("\n🎉  Entraînement terminé !")

# ------------------------------------------------------------------
# 4) Sauvegarde du modèle
# ------------------------------------------------------------------
MODEL_DIR = pathlib.Path(__file__).parent / "modele_facture"
MODEL_DIR.mkdir(exist_ok=True)

nlp.to_disk(MODEL_DIR)
print(f"💾  Modèle sauvé dans : {MODEL_DIR.resolve()}")


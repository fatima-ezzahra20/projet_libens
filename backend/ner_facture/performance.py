import json
from sklearn.metrics import precision_score, recall_score, f1_score
from sklearn.preprocessing import LabelEncoder
import json
from collections import defaultdict

# === Fichiers JSON ===
GROUND_TRUTH_FILE = "test_data.json"
PREDICTIONS_FILE = "../../DATA/Facture/factures_test2/predictions.json"

# === Paramètre tolérance pour les montants ===
TOLERANCE_MONTANT = 0.01

# === Charger les fichiers ===
with open(GROUND_TRUTH_FILE, "r", encoding="utf-8") as f:
    ground_truth_list = json.load(f)

with open(PREDICTIONS_FILE, "r", encoding="utf-8") as f:
    predictions_list = json.load(f)

# === Normalisation du texte ===
def normalize_text(s):
    if isinstance(s, list):
        return [normalize_text(x) for x in s]
    return "".join(str(s).lower().split())

# === Comparaison des valeurs numériques avec tolérance ===
def compare_valeurs(gt_val, pred_val, tol=TOLERANCE_MONTANT):
    try:
        return abs(float(gt_val) - float(pred_val)) <= tol
    except:
        return normalize_text(gt_val) == normalize_text(pred_val)

# === Transformer chaque facture en dictionnaire label → valeurs ===
def build_dict(fac_list):
    result = {}
    if len(fac_list) < 2:
        return result
    entities = fac_list[1].get("entities", [])
    texte = fac_list[0]
    for ent in entities:
        start, end, label = ent
        value = texte[start:end].strip()
        if label in result:
            if isinstance(result[label], list):
                result[label].append(value)
            else:
                result[label] = [result[label], value]
        else:
            result[label] = value
    return result

# Construire dictionnaires ground truth et predictions
ground_truth = {i: build_dict(fac) for i, fac in enumerate(ground_truth_list)}
predictions = {i: build_dict(fac) for i, fac in enumerate(predictions_list)}

# === Collecte de tous les champs ===
all_champs = set()
for fac in ground_truth.values():
    all_champs.update(fac.keys())
print(f"Champs à évaluer : {all_champs}")

# === Fonction pour calculer precision, recall, F1 manuellement ===
def compute_metrics(matches, total_true, total_pred):
    precision = matches / total_pred if total_pred > 0 else 0
    recall = matches / total_true if total_true > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    return round(precision, 3), round(recall, 3), round(f1, 3)

# === Évaluation par champ ===
resultats_champs = {}

for champ in all_champs:
    matches_total = 0
    total_true = 0
    total_pred = 0

    for fac_id in ground_truth:
        gt_val = ground_truth[fac_id].get(champ, "")
        pred_val = predictions.get(fac_id, {}).get(champ, "")

        # Convertir en liste si ce n'est pas déjà une liste
        if not isinstance(gt_val, list):
            gt_val = [gt_val]
        if not isinstance(pred_val, list):
            pred_val = [pred_val]

        total_true += len(gt_val)
        total_pred += len(pred_val)

        # Comparer toutes les valeurs
        for val in gt_val:
            if any(compare_valeurs(val, p) for p in pred_val):
                matches_total += 1

    precision, recall, f1 = compute_metrics(matches_total, total_true, total_pred)
    resultats_champs[champ] = {
        "precision": precision,
        "recall": recall,
        "f1_score": f1
    }

# === Affichage des résultats ===
print("\n=== Évaluation complète ===")
for champ, metrics in resultats_champs.items():
    print(f"{champ:20} | Precision: {metrics['precision']:.3f} | Recall: {metrics['recall']:.3f} | F1: {metrics['f1_score']:.3f}")

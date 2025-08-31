from html2image import Html2Image
from jinja2 import Template
from faker import Faker
import pytesseract
from PIL import Image
import json
import random
import os


# === Configuration ===
HTML_TEMPLATE_FILE = "../../../DATA/Releve/Template/attijari_template.html"

# CORRECTION : Séparez le dossier de sortie des images du fichier JSON
IMAGES_DIR = "test_val"
JSON_FILE = os.path.join(IMAGES_DIR, "ocr_test.json")
NUM_RELEVES = 125
DPI_SIZE = (1240, 1754)

fake = Faker('fr_FR')
hti = Html2Image()
hti.browser_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
hti.output_path = IMAGES_DIR  # Utilisez le chemin du dossier ici

# Créez le dossier pour les images (si il n'existe pas)
os.makedirs(IMAGES_DIR, exist_ok=True)

LIBELLES_FR = [
    "RETRAIT GAB HORS AGENCE",
    "VIREMENT REÇU DE M. AHMED BENNANI",
    "PAIEMENT CB AMAZON FR",
    "PRÉLÈVEMENT ORANGE MAROC",
    "REMISE CHÈQUE N° 589632",
    "VERSEMENT DE SALAIRE MENSUEL",
    "ACHAT SUPERMARCHÉ MARJANE",
    "PAIEMENT FACTURE INTERNET IAM"
]

def generer_operations(n=6):
    ops = []
    for _ in range(n):
        sens = fake.random_element(elements=('debit', 'credit'))
        montant = round(fake.pyfloat(left_digits=4, right_digits=2, positive=True), 2)
        ops.append({
            "date": fake.date_between(start_date='-6M', end_date='today').strftime("%d/%m/%Y"),
            "libelle": random.choice(LIBELLES_FR),
            "debit": montant if sens == "debit" else None,
            "credit": montant if sens == "credit" else None,
        })
    return ops

batch_results = []

# === Lecture du template une seule fois ===
with open(HTML_TEMPLATE_FILE, 'r', encoding='utf-8') as f:
    template = Template(f.read())

for i in range(1, NUM_RELEVES + 1):
    contexte = {
        "nom_client": fake.name(),
        "adresse_client_ligne1": fake.street_address(),
        "adresse_client_ligne2": fake.city(),
        "numero_compte": fake.iban(),
        "rib": fake.iban(),
        "operations": generer_operations(7),
        "date_solde": fake.date_this_year().strftime("%d/%m/%Y"),
        "solde_final": round(fake.pyfloat(left_digits=4, right_digits=2, positive=True), 2),
        "statut_solde": fake.random_element(elements=("CRÉDITEUR", "DÉBITEUR"))
    }

    html_rendered = template.render(**contexte)
    image_filename = f"releve_{i}.png"
    hti.screenshot(html_str=html_rendered, save_as=image_filename, size=DPI_SIZE)

    image_path = os.path.join(IMAGES_DIR, image_filename)
    image = Image.open(image_path)

    ocr_text = pytesseract.image_to_string(image)
    ocr_lines = [line.strip() for line in ocr_text.splitlines() if line.strip()]

    ocr_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
    confidences = [
        int(ocr_data['conf'][j])
        for j in range(len(ocr_data['text']))
        if ocr_data['conf'][j] != '-1'
    ]
    ocr_score = round(sum(confidences) / len(confidences), 2) if confidences else 0

    batch_results.append({
        "filename": image_filename,
        "lines": ocr_lines,
        "ocr_score": ocr_score
    })

    print(f"[{i}/{NUM_RELEVES}] ✔ OCR {image_filename} → Score : {ocr_score:.2f}")

# === Sauvegarde finale JSON
with open(os.path.join(IMAGES_DIR, "entrainement_ocirisation.json"), "w", encoding="utf-8") as f:
    json.dump(batch_results, f, ensure_ascii=False, indent=2)



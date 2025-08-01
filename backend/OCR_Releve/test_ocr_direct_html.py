from html2image import Html2Image
from jinja2 import Template
from faker import Faker
import pytesseract
from PIL import Image
import json
import random
import os

# === Configuration ===
OUTPUT_IMAGE = "outputs/releve_direct.png"
HTML_TEMPLATE_FILE = "../../DATA/Releve/Template/attijari_template.html"
  # fichier HTML dans ton dossier projet
fake = Faker('fr_FR')

# === Données factices ===
def generer_operations(n=6):
    ops = []
    for _ in range(n):
        sens = fake.random_element(elements=('debit', 'credit'))
        montant = round(fake.pyfloat(left_digits=4, right_digits=2, positive=True), 2)
        ops.append({
            "date": fake.date_between(start_date='-6M', end_date='today').strftime("%d/%m/%Y"),
            "libelle": fake.sentence(nb_words=4),
            "debit": montant if sens == "debit" else None,
            "credit": montant if sens == "credit" else None,
        })
    return ops

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

# === Lecture et rendu du template ===
with open(HTML_TEMPLATE_FILE, 'r', encoding='utf-8') as f:
    template = Template(f.read())

html_rendered = template.render(**contexte)

# === Générer PNG ===
# === Générer PNG ===
hti = Html2Image()
hti.browser_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
hti.output_path = 'outputs'
hti.screenshot(html_str=html_rendered, save_as="releve_direct.png", size=(1240, 1754))


# === OCR ligne par ligne ===
image = Image.open(OUTPUT_IMAGE)
ocr_text = pytesseract.image_to_string(image)
ocr_lines = [line.strip() for line in ocr_text.splitlines() if line.strip()]

# === OCR par mot pour calcul du score
ocr_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
confidences = [
    int(ocr_data['conf'][i])
    for i in range(len(ocr_data['text']))
    if ocr_data['conf'][i] != '-1'
]
ocr_score = round(sum(confidences) / len(confidences), 2) if confidences else 0

# === Affichage console ===
print("========== TEXTE OCRISÉ ==========\n")
for line in ocr_lines:
    print(line)
print("\n========== SCORE MOYEN OCR ==========")
print(f"{ocr_score:.2f} / 100")

# === Résultat JSON final ===
ocr_result_json = {
    "filename": os.path.basename(OUTPUT_IMAGE),
    "lines": ocr_lines,
    "ocr_score": ocr_score
}

# === Sauvegarde JSON ===
with open("outputs/ocr_direct_result.json", "w", encoding="utf-8") as f:
    json.dump(ocr_result_json, f, ensure_ascii=False, indent=2)

print("\n✅ Résultat sauvegardé dans outputs/ocr_direct_result.json")

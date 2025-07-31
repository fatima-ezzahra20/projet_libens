import os
import random
from jinja2 import Environment, FileSystemLoader
from faker import Faker
from weasyprint import HTML
from datetime import datetime
from pathlib import Path
import zipfile

# === PARAMÈTRES ===
BANK_NAME = "attijari"  # Choisir entre "attijari", "bcp", "cih", "sg"
EXPORT_FORMAT = "pdf"  # "pdf" ou "png"
NB_FILES = 100  # Combien de fichiers à générer

# === CHEMINS ===
ROOT_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = ROOT_DIR / "Template"
OUTPUT_DIR = ROOT_DIR / "releve_genere_entrainement2"
OUTPUT_DIR.mkdir(exist_ok=True)

# === INITIALISATION ===
faker = Faker("fr_FR")
env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))

# === LIBELLÉS EN FRANÇAIS ===
LIBELLES_FR = [
    "RETRAIT GAB HORS AGENCE",
    "VIREMENT PERMANENT LOYER",
    "VERSEMENT ESPÈCES EN AGENCE",
    "VIREMENT REÇU DE M. AHMED BENNANI",
    "PAIEMENT CB AMAZON FR",
    "PRÉLÈVEMENT ORANGE MAROC",
    "REMISE CHÈQUE N° 589632",
    "INTÉRÊTS CRÉDIT IMMOBILIER",
    "PAIEMENT ÉLECTRICITÉ LYDEC",
    "VERSEMENT DE SALAIRE MENSUEL",
    "PRÉLÈVEMENT ASSURANCE",
    "ACHAT SUPERMARCHÉ MARJANE",
    "PAIEMENT FACTURE INTERNET IAM",
    "REMBOURSEMENT PRÊT PERSONNEL"
]


# === DONNÉES DE TEST DYNAMIQUES ===

def generate_fake_operations(n=10):
    operations = []
    for _ in range(n):
        has_credit = random.choice([True, False])
        operations.append({
            "date": faker.date_between(start_date="-2y", end_date="today").strftime("%d/%m/%Y"),
            "libelle": random.choice(LIBELLES_FR),
            "debit": f"{random.uniform(100, 5000):.2f}" if not has_credit else "",
            "credit": f"{random.uniform(100, 5000):.2f}" if has_credit else "",
        })
    return operations
def generate_fake_data():
    montant_solde = random.uniform(-5000, 20000)
    statut_solde = "CRÉDITEUR" if montant_solde >= 0 else "DÉBITEUR"
    return {
        "client_name": faker.name(),
        "client_address": faker.address().replace("\n", ", "),
        "rib": faker.iban(),
        "compte": faker.bban(),
        "solde_final": f"{abs(montant_solde):,.2f}".replace(",", " "),  # valeur absolue, formatée
        "statut_solde": statut_solde,
        "date_solde": faker.date_this_year().strftime("%d/%m/%Y"),
        "operations": generate_fake_operations(random.randint(7, 12)),
    }

# === GÉNÉRATION ===
template_file = f"{BANK_NAME}_template.html"
template = env.get_template(template_file)

for i in range(1, NB_FILES + 1):
    data = generate_fake_data()
    html_out = template.render(data)
    filename = f"{BANK_NAME}_releve_{i:02}.{EXPORT_FORMAT}"
    filepath = OUTPUT_DIR / filename

    if EXPORT_FORMAT == "pdf":
        HTML(string=html_out).write_pdf(str(filepath))
    else:
        HTML(string=html_out).write_png(str(filepath))  # Nécessite CairoSVG si PNG



print(f"✅ {NB_FILES} relevés {EXPORT_FORMAT.upper()} générés pour {BANK_NAME} dans : {OUTPUT_DIR}")


import random
from faker import Faker
import datetime
import os
from jinja2 import Template
from html2image import Html2Image

# === Configuration ===
HTML_TEMPLATE_FILE = "../../../DATA/Releve/Template/attijari_template.html"
IMAGES_DIR = "Validation"
NUM_RELEVES = 20
DPI_SIZE = (1240, 1754)

fake = Faker('fr_FR')
hti = Html2Image()
hti.browser_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
hti.output_path = IMAGES_DIR

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

SOLDE_TYPES = ["CRÉDITEUR", "DÉBITEUR"]

def generer_operations(n, start_date, end_date):
    ops = []
    days = [start_date + datetime.timedelta(days=d) for d in range((end_date - start_date).days + 1)]
    
    for _ in range(n):
        sens = random.choice(['debit', 'credit'])
        montant = round(random.uniform(10.50, 10000.00), 2)
        
        libelle_base = random.choice(LIBELLES_FR)
        if libelle_base == "VIREMENT REÇU DE M. AHMED BENNANI":
            libelle = f"VIREMENT REÇU DE M. {fake.last_name().upper()} {fake.first_name().upper()}"
        elif libelle_base == "REMISE CHÈQUE N° 589632":
            libelle = f"REMISE CHÈQUE N° {random.randint(100000, 999999)}"
        else:
            libelle = libelle_base
        
        ops.append({
            "date": random.choice(days).strftime("%d/%m/%Y"),
            "libelle": libelle,
            "montant": montant,
            "debit": montant if sens == "debit" else None,
            "credit": montant if sens == "credit" else None,
        })
    return ops

def generate_bank_statement_html(num_transactions):
    # Choisir un mois et une année aléatoires
    month = random.randint(1, 12)
    year = 2025
    
    start_date_month = datetime.date(year, month, 1)
    if month == 12:
        end_date_month = datetime.date(year + 1, 1, 1) - datetime.timedelta(days=1)
    else:
        end_date_month = datetime.date(year, month + 1, 1) - datetime.timedelta(days=1)

    operations = generer_operations(num_transactions, start_date_month, end_date_month)

    solde = round(random.uniform(1000.00, 15000.00), 2)
    solde_type = random.choice(SOLDE_TYPES)
    solde_date = end_date_month.strftime("%d/%m/%Y")
    
    contexte = {
        "nom_client": fake.name(),
        "adresse_client_ligne1": fake.street_address(),
        "adresse_client_ligne2": fake.city(),
        "numero_compte": fake.iban(),
        "rib": fake.iban(),
        "operations": operations,
        "date_solde": solde_date,
        "solde_final": solde,
        "statut_solde": solde_type
    }
    
    with open(HTML_TEMPLATE_FILE, 'r', encoding='utf-8') as f:
        template = Template(f.read())
        html_rendered = template.render(**contexte)
    
    return html_rendered

if __name__ == '__main__':
    for i in range(1, NUM_RELEVES + 1):
        html_content = generate_bank_statement_html(num_transactions=random.randint(5, 10))
        image_filename = f"releve_{i}.png"
        
        hti.screenshot(html_str=html_content, save_as=image_filename, size=DPI_SIZE)
        
        print(f"[{i}/{NUM_RELEVES}] ✔ Fichier généré : {os.path.join(IMAGES_DIR, image_filename)}")
import os
import random
import cv2
import numpy as np
from faker import Faker
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from pdf2image import convert_from_path
from tqdm import tqdm
from PIL import Image, ImageFilter, ImageOps

fake = Faker("fr_FR")  # Faker en français

OUTPUT_DIR = "DATA/Factures_test"
os.makedirs(OUTPUT_DIR, exist_ok=True)

POPPLER_PATH = r"C:\Users\user\Downloads\Release-24.08.0-0\poppler-24.08.0\Library\bin"

# Dictionnaire fournisseur -> produits associés
produits_par_fournisseur = {
    "Société Maroc Télécom": [
        "Modem routeur WiFi",
        "Carte SIM 4G",
        "Téléphone fixe",
        "Routeur fibre optique",
        "Accessoires télécom"
    ],
    
    "Office Chérifien des Phosphates": [
        "Phosphates bruts",
        "Engrais phosphatés",
        "Produits chimiques agricoles"
    ],
    "Cosumar": [
        "Sucre cristallisé",
        "Sucre roux",
        "Produits dérivés du sucre"
    ],
    "Lesieur Cristal": [
        "Huile d'olive vierge",
        "Huile de tournesol",
        "Margarine",
        "Produits cosmétiques"
    ],
    "Holcim Maroc": [
        "Ciment gris Portland",
        "Béton prêt à l'emploi",
        "Granulats",
        "Produits de construction"
    ],
    "Maroc Taswiq": [
        "Produits artisanaux en terre cuite",
        "Tapis berbères",
        "Vêtements traditionnels modernisés"
    ],
    "Label’Vie": [
        "Produits alimentaires frais",
        "Boissons gazeuses",
        "Produits ménagers"
    ],
    "Managem": [
        "Métaux précieux",
        "Minerais divers",
        "Produits miniers"
    ],
    "Orange Maroc": [
        "Smartphone Samsung Galaxy S21",
        "Carte prépayée Orange",
        "Forfait mobile",
        "Accessoires téléphonie"
    ],
}

clients_marocains = [
    "Mohamed El Amrani",
    "Fatima Zahra Benali",
    "Youssef Haddad",
    "Khadija El Fassi",
    "Abdelkader Bennis",
    "Sara Lahlou",
    "Rachid Bouzid",
    "Nadia Choukri",
    "Karim Elmoutawakil",
    "Salma Bouziane",
]

villes_quartiers = [
    "Casablanca - Maarif",
    "Rabat - Agdal",
    "Marrakech - Gueliz",
    "Fès - Medina",
    "Tanger - Malabata",
    "Agadir - Talborjt",
    "Meknès - Ville Nouvelle",
    "Oujda - Hay Mohammadi",
    "El Jadida - Centre Ville",
    "Nador - Boukhalef",
]

def gen_invoice_data():
    fournisseur = random.choice(list(produits_par_fournisseur.keys()))
    produits_fournisseur = produits_par_fournisseur[fournisseur]

    nb_items = random.randint(2, min(6, len(produits_fournisseur)))  # max 6 ou nombre dispo
    items = []
    total_ht = 0

    produits_choisis = random.sample(produits_fournisseur, nb_items)

    for desc in produits_choisis:
        qte = random.randint(1, 10)
        pu = round(random.uniform(50, 1000), 2)
        total = round(qte * pu, 2)
        total_ht += total
        items.append({
            "description": desc,
            "quantité": qte,
            "prix unitaire": pu,
            "total": total
        })

    # RIB marocain plausible
    rib = f"MA{random.randint(10, 99)} {random.randint(10000, 99999)} {random.randint(10000, 99999)} {random.randint(1000000000, 9999999999)}"

    # Téléphone marocain mobile typique
    tel = f"+212 {random.choice([6,7])}{random.randint(10000000, 99999999)}"

    client = random.choice(clients_marocains)
    adresse_four = random.choice(villes_quartiers)
    adresse_client = random.choice(villes_quartiers)

    return {
        "num": f"FAC-{fake.unique.random_int(1000, 9999)}",
        "fournisseur": fournisseur,
        "tel": tel,
        "email": fake.company_email(),
        "adresse_four": adresse_four,
        "rib": rib,
        "client": client,
        "adresse_client": adresse_client,
        "date_em": fake.date_between("-60d", "today"),
        "date_ech": fake.date_between("today", "+30d"),
        "items": items,
        "total_ht": round(total_ht, 2),
        "tva": 0.0,
        "total_ttc": round(total_ht, 2)
    }


def draw_pdf(data, filepath):
    c = canvas.Canvas(filepath, pagesize=A4)
    width, height = A4
    margin = 20*mm
    y = height - margin
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin, y, f"FACTURE N° {data['num']}")
    c.setFont("Helvetica", 10)
    y -= 18
    c.drawString(margin, y, f"Date d'émission : {data['date_em']}")
    y -= 14
    c.drawString(margin, y, f"Date d'échéance : {data['date_ech']}")
    y -= 28
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y, "Fournisseur")
    c.drawString(width/2, y, "Client")
    c.setFont("Helvetica", 10)
    y -= 14

   
    c.drawString(margin, y, data['fournisseur'])
    y -= 12
    c.drawString(margin, y, f"Tél : {data['tel']}")
    y -= 12
    c.drawString(margin, y, f"Email : {data['email']}")
    y -= 12
    c.drawString(margin, y, f"RIB : {data['rib']}")
    y -= 12
    c.drawString(margin, y, data['adresse_four'])
    y_client = y
    c.drawString(width/2, y_client, data['client'])
    c.drawString(width/2, y_client - 12, data['adresse_client'])
    y -= 30
    c.setFont("Helvetica-Bold", 11)
    c.drawString(margin, y, "Description")
    c.drawString(width*0.55, y, "Qté")
    c.drawString(width*0.65, y, "PU (MAD)")
    c.drawString(width*0.8, y, "Total (MAD)")
    y -= 12
    c.setFont("Helvetica", 10)
    for item in data['items']:
        c.drawString(margin, y, item['description'][:45])
        c.drawRightString(width*0.62, y, str(item['quantité']))
        c.drawRightString(width*0.75, y, f"{item['prix unitaire']:.2f}")
        c.drawRightString(width*0.95, y, f"{item['total']:.2f}")
        y -= 12
    y -= 10
    c.setFont("Helvetica-Bold", 10)
    c.drawRightString(width*0.75, y, "Total HT :")
    c.drawRightString(width*0.95, y, f"{data['total_ht']:.2f} MAD")
    y -= 14
    c.drawRightString(width*0.75, y, "Total TTC :")
    c.drawRightString(width*0.95, y, f"{data['total_ttc']:.2f} MAD")
    c.showPage()
    c.save()

def pdf_to_scanned_image(pdf_path, img_path):
    images = convert_from_path(pdf_path, dpi=200, poppler_path=POPPLER_PATH)
    img = images[0].convert("L")
    img = ImageOps.autocontrast(img, cutoff=2)
    img = img.filter(ImageFilter.GaussianBlur(0.8))
    np_img = cv2.cvtColor(np.array(img), cv2.COLOR_GRAY2BGR)
    noise = cv2.randn(np_img.copy(), 0, 8)
    noisy = cv2.add(np_img, noise)
    final = Image.fromarray(cv2.cvtColor(noisy, cv2.COLOR_BGR2GRAY))
    final.save(img_path, "PNG", quality=90)

# Exécution pour générer les factures (PDF et PNG)
print("📄 Génération de 50 factures PDF marocaines avec produits cohérents...")
for _ in tqdm(range(20)):
    data = gen_invoice_data()
    pdf_path = os.path.join(OUTPUT_DIR, f"{data['num']}.pdf")
    draw_pdf(data, pdf_path)

print("🖼️ Génération de 50 factures images (PNG)...")
for _ in tqdm(range(20)):
    data = gen_invoice_data()
    temp_pdf = os.path.join(OUTPUT_DIR, f"{data['num']}_temp.pdf")
    img_path = os.path.join(OUTPUT_DIR, f"{data['num']}.png")
    draw_pdf(data, temp_pdf)
    pdf_to_scanned_image(temp_pdf, img_path)
    os.remove(temp_pdf)

print(f"\n✅ Terminé : 100 factures (50 PDF + 50 images) créées dans {OUTPUT_DIR}/")




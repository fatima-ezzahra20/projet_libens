import os
import random
from faker import Faker
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from pdf2image import convert_from_path
from PIL import Image, ImageFilter, ImageOps
import cv2
import numpy as np 

# Initialisation
fake = Faker("fr_FR")
OUTPUT_DIR = "factures_test2"
os.makedirs(OUTPUT_DIR, exist_ok=True)

POPPLER_PATH = r"C:\Users\user\Downloads\Release-24.08.0-0\poppler-24.08.0\Library\bin"

# Fournisseurs marocains réalistes mais variés
fournisseurs = [
    "Société Maroc Télécom", "Maroc Télécom SARL", "Cosumar Distribution",
    "Lesieur Maroc", "Holcim Maroc", "Maroc Taswiq", "Label’Vie",
    "Managem", "Orange Maroc", "Société Alpha"
]

produits_par_fournisseur = {
    "Société Maroc Télécom": ["Modem WiFi", "Carte SIM 4G", "Routeur fibre", "Téléphone fixe"],
    "Maroc Télécom SARL": ["Forfait mobile", "Routeur 4G", "Accessoires télécom"],
    "Cosumar Distribution": ["Sucre cristallisé", "Sucre roux", "Produits dérivés du sucre"],
    "Lesieur Maroc": ["Huile d’olive", "Huile de tournesol", "Margarine"],
    "Holcim Maroc": ["Ciment gris", "Béton prêt à l'emploi", "Granulats"],
    "Maroc Taswiq": ["Tapis berbères", "Pottery artisanal", "Vêtements traditionnels"],
    "Label’Vie": ["Produits frais", "Boissons gazeuses", "Produits ménagers"],
    "Managem": ["Métaux précieux", "Minerais divers", "Produits miniers"],
    "Orange Maroc": ["Smartphone Samsung", "Carte prépayée Orange", "Forfait mobile"],
    "Société Alpha": ["Produit A", "Produit B", "Produit C"]
}

villes_quartiers = [
    "Casablanca - Maarif", "Rabat - Agdal", "Marrakech - Gueliz",
    "Fès - Medina", "Tanger - Malabata", "Agadir - Talborjt",
    "Meknès - Ville Nouvelle", "Oujda - Hay Mohammadi", "El Jadida - Centre Ville",
    "Nador - Boukhalef"
]

def gen_invoice_data(facture_id):
    fournisseur = random.choice(fournisseurs)
    produits_fournisseur = produits_par_fournisseur[fournisseur]
    nb_items = random.randint(2, min(5, len(produits_fournisseur)))
    produits_choisis = random.sample(produits_fournisseur, nb_items)
    
    items = []
    total_ht = 0
    for prod in produits_choisis:
        qte = random.randint(1, 10)
        pu = round(random.uniform(50, 1000), 2)
        montant = round(qte * pu, 2)
        total_ht += montant
        items.append({"description": prod, "quantité": qte, "prix_unitaire": pu, "montant": montant})
    
    client = fake.name()
    adresse_client = random.choice(villes_quartiers)
    adresse_four = random.choice(villes_quartiers)
    rib = f"MA{random.randint(10, 99)} {random.randint(10000, 99999)} {random.randint(10000, 99999)} {random.randint(1000000000, 9999999999)}"
    tel = f"+212 {random.choice([6,7])}{random.randint(10000000, 99999999)}"
    date_em = fake.date_between(start_date="-60d", end_date="today")
    date_ech = fake.date_between(start_date="today", end_date="+30d")
    
    total_ttc = round(total_ht * 1.2, 2)  
    
    return {
        "num": f"FAC-{facture_id:04d}",
        "fournisseur": fournisseur,
        "client": client,
        "adresse_client": adresse_client,
        "adresse_four": adresse_four,
        "rib": rib,
        "tel": tel,
        "date_em": date_em,
        "date_ech": date_ech,
        "items": items,
        "total_ht": round(total_ht,2),
        "total_ttc": total_ttc
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
    c.drawString(width/2, y, data['client'])
    y -= 12
    c.drawString(margin, y, f"Tél: {data['tel']}")
    c.drawString(width/2, y, data['adresse_client'])
    y -= 12
    c.drawString(margin, y, f"RIB: {data['rib']}")
    y -= 12
    c.drawString(margin, y, data['adresse_four'])
    
    y -= 20
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
        c.drawRightString(width*0.75, y, f"{item['prix_unitaire']:.2f}")
        c.drawRightString(width*0.95, y, f"{item['montant']:.2f}")
        y -= 12
    
    y -= 10
    c.setFont("Helvetica-Bold", 10)
    c.drawRightString(width*0.75, y, "Total HT :")
    c.drawRightString(width*0.95, y, f"{data['total_ht']:.2f} MAD")
    y -= 12
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

# Génération des factures
for fid in range(1, 101):
    data = gen_invoice_data(fid)
    pdf_path = os.path.join(OUTPUT_DIR, f"{data['num']}.pdf")
    img_path = os.path.join(OUTPUT_DIR, f"{data['num']}.png")
    draw_pdf(data, pdf_path)
    pdf_to_scanned_image(pdf_path, img_path)
    print(f"Facture {fid} générée dans {OUTPUT_DIR}")

print("✅ 50 factures test marocaines réalistes (PDF + image) générées dans un seul dossier !")

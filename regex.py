# Extraction du numéro de facture
facture_num = re.search(r'Facture\s*n°?\s*:? ?(\w+)', texte)
if facture_num:
    print("Numéro de facture :", facture_num.group(1))

# Extraction d'une date (JJ/MM/AAAA)
dates = re.findall(r'\d{2}/\d{2}/\d{4}', texte)
print("Dates trouvées :", dates)

# Extraction d'un montant en euros
montants = re.findall(r'(\d+[.,]?\d*)\s?€', texte)
print("Montants trouvés :", montants)

# Extraction de RIB ou IBAN
rib = re.search(r'([A-Z]{2}[0-9]{2}[A-Z0-9]{11,30})', texte)
if rib:
    print("RIB trouvé :", rib.group(1))
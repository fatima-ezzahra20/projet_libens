import streamlit as st
from ocr.ocr_utilie import ocr_image, ocr_pdf
import spacy
import os
import tempfile

# Charger le modèle spaCy NER entraîné
nlp = spacy.load("ner_facture/modele_facture")

st.title("🧾 Extraction de données de factures")

uploaded_file = st.file_uploader("Importer une image ou un PDF", type=["png", "jpg", "jpeg", "pdf"])

if uploaded_file is not None:
    ext = os.path.splitext(uploaded_file.name)[1].lower()

    # Sauvegarder temporairement le fichier uploadé pour traitement OCR
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    # Faire OCR selon le type de fichier
    if ext in [".png", ".jpg", ".jpeg"]:
        st.image(tmp_path, caption="Image importée", use_column_width=True)
        texte = ocr_image(tmp_path)

    elif ext == ".pdf":
        st.info("PDF détecté - affichage du texte extrait")
        textes = ocr_pdf(tmp_path)
        texte = "\n\n".join(textes)

    else:
        st.error("Format non supporté.")
        st.stop()

    # Afficher le texte OCRisé
    st.subheader("📄 Texte OCRisé")
    st.text_area("", texte, height=300)

    # Appliquer le modèle spaCy NER
    doc = nlp(texte)

    # Afficher les entités extraites
    st.subheader("🔍 Entités détectées")
    if doc.ents:
        for ent in doc.ents:
            st.markdown(f"- **{ent.label_}** : {ent.text}")
    else:
        st.warning("Aucune entité détectée.")

    # Optionnel : nettoyer le fichier temporaire
    os.remove(tmp_path)

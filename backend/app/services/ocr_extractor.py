# Fichier : backend/app/services/ocr_extractor.py

import pytesseract
from PIL import Image
import fitz  # PyMuPDF
import os

def extract_text_from_file(file_path: str):
    """
    Extrait le texte d'un fichier image ou PDF en utilisant l'OCR.
    """
    file_extension = os.path.splitext(file_path)[1].lower()
    
    if file_extension in ['.jpg', '.jpeg', '.png']:
        try:
            return pytesseract.image_to_string(Image.open(file_path))
        except Exception as e:
            print(f"Erreur d'OCR sur l'image : {e}")
            return None
    elif file_extension == '.pdf':
        try:
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text()
            return text
        except Exception as e:
            print(f"Erreur d'OCR sur le PDF : {e}")
            return None
    else:
        return None
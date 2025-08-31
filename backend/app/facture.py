from fastapi import APIRouter
from .database import supabase

router = APIRouter()

@router.get("/factures/{user_id}")
def get_factures(user_id: int):
    response = supabase.table("factures") \
        .select("id, num_facture, fournisseur, montant_total_ttc, date_emission, date_echeance") \
        .eq("user_id", user_id) \
        .execute()
    return response.data

@router.get("/facture/{facture_id}")
def get_facture_details(facture_id: int):
    facture = supabase.table("factures") \
        .select("*") \
        .eq("id", facture_id) \
        .single() \
        .execute()

    lignes = supabase.table("lignes_facture") \
        .select("*") \
        .eq("facture_id", facture_id) \
        .execute()

    return {
        "facture": facture.data,
        "lignes": lignes.data
    }

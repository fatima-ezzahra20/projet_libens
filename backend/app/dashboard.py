from fastapi import APIRouter
from .database import supabase
from collections import defaultdict
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/")
def get_dashboard():
    # Récupérer toutes les factures et relevés
    factures_res = supabase.table("factures").select("*", count="exact").execute()
    releves_res = supabase.table("releves").select("*", count="exact").execute()

    factures = supabase.table("factures").select("date_emission, montant_total_ttc").execute().data or []
    releves = supabase.table("releves").select("releve_mois, solde").execute().data or []

    # Totaux montants
    total_montant_factures = sum(float(f.get("montant_total_ttc") or 0) for f in factures)
    total_montant_releves = sum(float(r.get("solde") or 0) for r in releves)

    # Totaux nombre
    total_nombre_factures = factures_res.count or 0
    total_nombre_releves = releves_res.count or 0

    # Evolution mensuelle
    factures_par_mois = defaultdict(float)
    for f in factures:
        mois = datetime.fromisoformat(f["date_emission"]).strftime("%Y-%m")
        factures_par_mois[mois] += float(f.get("montant_total_ttc") or 0)

    releves_par_mois = defaultdict(float)
    for r in releves:
        mois = r.get("releve_mois")
        if mois:
            releves_par_mois[mois] += float(r.get("solde") or 0)

    return {
        "total_montant_factures": total_montant_factures,
        "total_montant_releves": total_montant_releves,
        "total_nombre_factures": total_nombre_factures,
        "total_nombre_releves": total_nombre_releves,
        "factures_par_mois": [{"mois": m, "total": t} for m, t in sorted(factures_par_mois.items())],
        "releves_par_mois": [{"mois": m, "total": t} for m, t in sorted(releves_par_mois.items())]
    }

@router.get("/dashboard/proches-echeances")
def factures_proches_echeances(jours: int = 7):
    today = datetime.today()
    date_limite = today + timedelta(days=jours)

    factures_res = supabase.table("factures").select("*").execute()
    factures = factures_res.data or []

    result = []
    for f in factures:
        try:
            date_echeance = datetime.strptime(f["date_echeance"], "%Y-%m-%d")
            if today <= date_echeance <= date_limite:
                result.append({
                    "num_facture": f.get("num_facture"),
                    "fournisseur": f.get("fournisseur"),
                    "montant_total_ttc": f.get("montant_total_ttc"),
                    "date_echeance": f.get("date_echeance")
                })
        except Exception:
            continue

    return result

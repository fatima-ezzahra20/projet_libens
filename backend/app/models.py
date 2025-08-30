from pydantic import BaseModel
from typing import List, Optional
import datetime

# La classe Transaction reste inchangée, elle est correcte.
class Transaction(BaseModel):
    date: str
    libelle: str
    montant: float

# La classe Solde reste inchangée, elle est correcte.
class Solde(BaseModel):
    solde: float
   

# La classe ReleveResponse est mise à jour pour inclure le mois du relevé.
class ReleveResponse(BaseModel):
    id: str
    filename: str
    content: str
    transactions: List[Transaction]
    solde: Optional[Solde]
    releve_mois: Optional[str]

# La classe ReleveListItem est corrigée pour correspondre à la nouvelle route GET /releves.
# Elle ne contient que les informations de base nécessaires à la liste.
class ReleveListItem(BaseModel):
    id: str
    filename: str
    solde: Optional[float]
    releve_mois: Optional[str]
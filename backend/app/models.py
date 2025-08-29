from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import datetime

# 1. New class for a transaction - Name corrected
class Transaction(BaseModel):
    # The transaction ID is not needed here, as it will be managed
    # by the database upon insertion.
    date: str
    libelle: str
    montant: float

# 2. New class for the final balance
class Solde(BaseModel):
    solde: float
    # You can add the type 'CREDITEUR' or 'DEBITEUR' if you want
    type_solde: Optional[str] = None 

# 3. Modification of the ReleveResponse class
# This class must now return the list of transactions
# and the final balance, instead of the raw entities.
class ReleveResponse(BaseModel):
    id: str
    filename: str
    content: str
    transactions: List[Transaction]  # Replaced with a list of transactions
    solde: Optional[Solde] # Added the final balance

# The ReleveListItem class remains unchanged for now
class ReleveListItem(BaseModel):
    id: str
    filename: str
    created_at: datetime.datetime # Better to use the datetime type
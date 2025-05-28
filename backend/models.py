from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime

class WatchConfiguration(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    case: str
    dial: str
    hands: str
    strap: str
    box: str
    engraving: Optional[str] = None
    customer_name: str
    customer_surname: str
    customer_email: str
    customer_phone: str
    customer_address: str
    customer_city: str
    customer_postcode: str
    payment_method: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    price: float  # Ukupna cijena

class Case(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    price: float

class Dial(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    price: float

class Hands(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    price: float

class Strap(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    price: float

class Box(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    price: float
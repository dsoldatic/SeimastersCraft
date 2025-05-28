# backend/seed_components.py

from sqlmodel import SQLModel, Session, create_engine
from models import Case, Dial, Hands, Strap, Box

engine = create_engine("sqlite:///watchcraft.db")

components = {
    Case: [("Datejust 36", 120), ("Explorer II", 150), ("Oyster Perpetual", 100)],
    Dial: [("Ice Blue Arab", 80), ("Black Roman", 70), ("Silver Baton", 60)],
    Hands: [("Silver", 20), ("Gold", 25), ("Black", 15)],
    Strap: [("Silver Jubilee", 90), ("Black Rubber", 70), ("Brown Leather", 50)],
    Box: [("Default", 0), ("Luxury Wooden", 30), ("Travel Pouch", 10)],
}

with Session(engine) as session:
    for model, items in components.items():
        for name, price in items:
            obj = model(name=name, price=price)
            session.add(obj)
    session.commit()

print("Komponente su uspješno dodane u bazu.")
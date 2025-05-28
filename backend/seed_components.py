from sqlmodel import Session, create_engine
from models import Case, Dial, Hands, Strap, Box
from pathlib import Path
import re

engine = create_engine("sqlite:///watchcraft.db")

# Mapa tipova komponenti na klase modela i putanje foldera
component_info = {
    Case: "case",
    Dial: "dial",
    Hands: "hands",
    Strap: "strap",
    Box: "box",
}

def parse_filename(filename: str):
    # Primjer imena: case-silver-datejust-39mm-120.png
    # Izvući cijenu i složiti naziv bez cijene i ekstenzije
    base = filename.replace(".png", "")
    parts = base.split("-")[1:]  # preskače 'case', 'dial', itd.
    price_match = re.search(r'(\d+)', parts[-1])
    price = float(price_match.group(1)) if price_match else 0
    name = " ".join(parts[:-1]) + f" - {price} €"
    return name.title(), price

with Session(engine) as session:
    for model, folder_name in component_info.items():
        folder_path = Path(__file__).parent / "static" / "img" / folder_name
        if not folder_path.exists():
            print(f"Folder ne postoji: {folder_path}")
            continue

        for file in folder_path.glob("*.png"):
            name, price = parse_filename(file.name)
            
            # Provjera da li već postoji komponenta u bazi sa tim imenom da se ne duplicira
            exists = session.exec(
                select(model).where(model.name == name)
            ).first()
            if not exists:
                obj = model(name=name, price=price)
                session.add(obj)

    session.commit()

print("Komponente su uspješno dodane u bazu.")
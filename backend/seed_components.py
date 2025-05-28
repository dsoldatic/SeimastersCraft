from sqlmodel import Session, create_engine, select
from models import Case, Dial, Hands, Strap, Box
from pathlib import Path
import re

engine = create_engine("sqlite:///watchcraft.db")

def seed_from_folder(model, folder_path):
    components = []
    folder = Path(folder_path)
    for file in folder.glob("*.png"):
        filename = file.name
        base = filename.replace(".png", "")
        parts = base.split("-")[1:]  # preskači prefix (npr. case, dial)
        
        # Izvući cijenu iz zadnjeg dijela naziva
        price_match = re.search(r'(\d+)', parts[-1])
        price = float(price_match.group(1)) if price_match else 0
        
        # Sastavi ime bez cijene i bez "mm"
        # Ovdje ukloni i cijenu iz naziva
        name_parts = parts[:-1]
        # ukloni "mm" ako postoji u nazivu
        name_clean = " ".join(part.replace("mm", "") for part in name_parts).strip()
        components.append((name_clean.title(), price))

    with Session(engine) as session:
        for name, price in components:
            exists = session.exec(select(model).where(model.name == name)).first()
            if not exists:
                obj = model(name=name, price=price)
                session.add(obj)
        session.commit()
    print(f"Seed za {model.__name__} gotov.")

seed_from_folder(Case, "backend/static/img/case")
seed_from_folder(Dial, "backend/static/img/dial")
seed_from_folder(Hands, "backend/static/img/hands")
seed_from_folder(Strap, "backend/static/img/strap")
seed_from_folder(Box, "backend/static/img/box")
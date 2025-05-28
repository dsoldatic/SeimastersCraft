import os
import re
import uvicorn  
from pathlib import Path
from typing import List

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select

from models import (
    WatchConfiguration, Case, Dial, Hands, Strap, Box, SQLModel
)
from database import get_session, init_db, engine
from mailer import send_email

app = FastAPI(title="SeimastersCraft API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# inicijalna izrada tablica
init_db()

# seedanje podataka, samo ako još nemaš komponente
def init_components():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        if not session.exec(select(Case)).first():
            session.add_all([
                Case(name="datejust 36", price=100),
                Dial(name="ice blue arab", price=80),
                Hands(name="silver", price=50),
                Strap(name="silver jubilee", price=60),
                Box(name="default", price=40)
            ])
            session.commit()

init_components()


@app.post("/order")
def create_order(config: WatchConfiguration, session: Session = Depends(get_session)):
    # provjera duplikata
    existing = session.exec(
        select(WatchConfiguration).where(
            WatchConfiguration.case == config.case,
            WatchConfiguration.dial == config.dial,
            WatchConfiguration.hands == config.hands,
            WatchConfiguration.strap == config.strap,
            WatchConfiguration.box == config.box,
            WatchConfiguration.engraving == config.engraving,
            WatchConfiguration.customer_name == config.customer_name,
            WatchConfiguration.customer_surname == config.customer_surname,
            WatchConfiguration.customer_email == config.customer_email,
            WatchConfiguration.customer_phone == config.customer_phone,
            WatchConfiguration.customer_address == config.customer_address,
            WatchConfiguration.customer_city == config.customer_city,
            WatchConfiguration.customer_postcode == config.customer_postcode,
            WatchConfiguration.payment_method == config.payment_method
        )
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Ova narudžba je već poslana.")

    # ako frontend nije poslao price, izračunaj ovdje
    if not config.price:
        def get_price(model, name):
            return session.exec(select(model.price).where(model.name == name)).first() or 0
        config.price = (
            get_price(Case, config.case) +
            get_price(Dial, config.dial) +
            get_price(Hands, config.hands) +
            get_price(Strap, config.strap) +
            get_price(Box, config.box)
        )

    session.add(config)
    session.commit()
    session.refresh(config)

    subject = "Potvrda narudžbe – SeimastersCraft"
    # plain text
    body_plain = f"""
Hvala na narudžbi!

Konfiguracija sata:
Kućište: {config.case}
Brojčanik: {config.dial}
Kazaljke: {config.hands}
Remen: {config.strap}
Kutija: {config.box}
Gravura: {config.engraving or 'Nema'}

Ukupna cijena: {config.price:.2f} €

Podaci za dostavu:
Ime: {config.customer_name} {config.customer_surname}
Adresa: {config.customer_address}, {config.customer_city}, {config.customer_postcode}
Broj mobitela: {config.customer_phone}
Email: {config.customer_email}
Način plaćanja: {config.payment_method}

Napomena: Slika vašeg sata će vam biti poslana u roku 24–48 sati.
"""
    # HTML verzija
    body_html = f"""
<p>Hvala na narudžbi!</p>
<h3>Konfiguracija sata:</h3>
<ul>
  <li><strong>Kućište:</strong> {config.case}</li>
  <li><strong>Brojčanik:</strong> {config.dial}</li>
  <li><strong>Kazaljke:</strong> {config.hands}</li>
  <li><strong>Remen:</strong> {config.strap}</li>
  <li><strong>Kutija:</strong> {config.box}</li>
  <li><strong>Gravura:</strong> {config.engraving or 'Nema'}</li>
</ul>
<p><strong>Ukupna cijena:</strong> {config.price:.2f} €</p>
<h3>Podaci za dostavu:</h3>
<ul>
  <li><strong>Ime:</strong> {config.customer_name} {config.customer_surname}</li>
  <li><strong>Adresa:</strong> {config.customer_address}, {config.customer_city}, {config.customer_postcode}</li>
  <li><strong>Broj mobitela:</strong> {config.customer_phone}</li>
  <li><strong>Email:</strong> {config.customer_email}</li>
  <li><strong>Način plaćanja:</strong> {config.payment_method}</li>
</ul>
<p><em>Napomena: Slika vašeg sata će vam biti poslana u roku 24–48 sati.</em></p>
"""

    send_email(config.customer_email, subject, body_plain, body_html)
    send_email("seimasterswatches@gmail.com", "Nova narudžba", body_plain, body_html)

    return {"message": f"Narudžba primljena! Ukupna cijena: {config.price:.2f} €"}


@app.get("/admin/configurations", response_model=List[WatchConfiguration])
def get_all_configurations(session: Session = Depends(get_session)):
    return session.exec(select(WatchConfiguration)).all()


@app.get("/components/cases", response_model=List[Case])
def get_cases(session: Session = Depends(get_session)):
    return session.exec(select(Case)).all()

@app.get("/components/dials", response_model=List[Dial])
def get_dials(session: Session = Depends(get_session)):
    return session.exec(select(Dial)).all()

@app.get("/components/hands", response_model=List[Hands])
def get_hands(session: Session = Depends(get_session)):
    return session.exec(select(Hands)).all()

@app.get("/components/straps", response_model=List[Strap])
def get_straps(session: Session = Depends(get_session)):
    return session.exec(select(Strap)).all()

@app.get("/components/boxes", response_model=List[Box])
def get_boxes(session: Session = Depends(get_session)):
    return session.exec(select(Box)).all()

@app.get("/components")
def get_components(session: Session = Depends(get_session)):
    return {
        "cases": session.exec(select(Case)).all(),
        "dials": session.exec(select(Dial)).all(),
        "hands": session.exec(select(Hands)).all(),
        "straps": session.exec(select(Strap)).all(),
        "boxes": session.exec(select(Box)).all()
    }


@app.get("/image-components")
def get_image_components(type: str = Query(..., regex="^(case|dial|hands|strap|box)$")):
    folder = Path(__file__).parent.parent / "frontend" / "watchcraft-frontend" / "public" / "img" / type
    if not folder.exists():
        raise HTTPException(status_code=404, detail="Folder ne postoji.")

    components = []
    for file in folder.glob("*.png"):
        match = re.match(rf"{type}-([a-z0-9\-]+)-(\d+)[€]?.png", file.name, re.IGNORECASE)
        if match:
            name  = match.group(1).replace("-", " ").title()
            price = int(match.group(2))
            components.append({
                "name": name,
                "price": price,
                "filename": f"{type}/{file.name}"
            })
    return components


# ---------------------------------------------
# Pokretanje servera kad se main.py izvršava direktno
# ---------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
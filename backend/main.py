import os
import re
import uvicorn
from typing import List

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select

from database import get_session, init_db, engine
from mailer import send_email
from models import WatchConfiguration, Case, Dial, Hands, Strap, Box, SQLModel

app = FastAPI(title="SeimastersCraft API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# inicijalna izrada tablica i seedanje
init_db()
def init_components():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        if not session.exec(select(Case)).first():
            session.add_all([
                Case(name="datejust 36", price=100),
                Dial(name="ice blue arab", price=80),
                Hands(name="silver", price=50),
                Strap(name="silver jubilee", price=60),
                Box(name="default", price=40),
            ])
            session.commit()
init_components()


@app.post("/order")
def create_order(
    config: WatchConfiguration,
    session: Session = Depends(get_session)
):
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
            WatchConfiguration.payment_method == config.payment_method,
        )
    ).first()
    if existing:
        raise HTTPException(400, "Ova narudžba je već poslana.")

    if not config.price:
        def _price(m, name):
            return session.exec(select(m.price).where(m.name == name)).first() or 0
        config.price = (
            _price(Case, config.case)
            + _price(Dial, config.dial)
            + _price(Hands, config.hands)
            + _price(Strap, config.strap)
            + _price(Box, config.box)
        )

    session.add(config)
    session.commit()
    session.refresh(config)

    subject = "Potvrda narudžbe – SeimastersCraft"
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
  <li><strong>Mobitel:</strong> {config.customer_phone}</li>
  <li><strong>Email:</strong> {config.customer_email}</li>
  <li><strong>Plaćanje:</strong> {config.payment_method}</li>
</ul>
<p><em>Napomena: Slika vašeg sata stiže u 24–48h.</em></p>
"""

    send_email(config.customer_email, subject, body_plain, body_html)
    send_email(
        os.environ["GMAIL_USER"],
        "Nova narudžba",
        body_plain,
        body_html,
    )

    return {"message": f"Narudžba primljena! Ukupna cijena: {config.price:.2f} €"}


@app.get("/admin/configurations", response_model=List[WatchConfiguration])
def admin_list(session: Session = Depends(get_session)):
    return session.exec(select(WatchConfiguration)).all()


@app.get("/components/{typ}", response_model=List)
def list_components(typ: str, session: Session = Depends(get_session)):
    model = {
        "cases": Case,
        "dials": Dial,
        "hands": Hands,
        "straps": Strap,
        "boxes": Box
    }.get(typ)
    if not model:
        raise HTTPException(404, "Nepoznat tip komponente.")
    return session.exec(select(model)).all()


@app.get("/image-components")
def image_components(type: str = Query(..., regex="^(case|dial|hands|strap|box)$")):
    raise HTTPException(404, "Serviranje slika je onemogućeno na backendu.")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, log_level="info")
import os
import re
import uvicorn
from pathlib import Path
from typing import List

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from fastapi.responses import JSONResponse
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

img_path = Path(__file__).parent / "static" / "img"
if img_path.exists():
    app.mount("/img", StaticFiles(directory=img_path), name="img")

# Inicijalna izrada tablica i seedanje
init_db()


@app.get("/image-components")
def get_image_components(type: str = Query(..., regex="^(case|dial|hands|strap|box)$")):
    folder = Path(__file__).parent / "static" / "img" / type
    if not folder.exists():
        raise HTTPException(status_code=404, detail="Folder ne postoji.")

    components = []
    for file in folder.glob("*.png"):
        filename = file.name
        base = filename.replace(".png", "")
        parts = base.split("-")[1:]
        price_match = re.search(r'(\d+)', parts[-1])
        price = float(price_match.group(1)) if price_match else 0
        name = " ".join(parts[:-1]) + f" - {price} €"
        components.append({
            "name": name.title(),
            "filename": filename,
            "price": price
        })

    return JSONResponse(content=components)

@app.post("/order")
def create_order(order: WatchConfiguration, session: Session = Depends(get_session)):
    session.add(order)
    session.commit()
    session.refresh(order)

    # Email korisniku
    try:
        subject = "Potvrda narudžbe - SeimastersCraft"
        body_plain = f"Hvala na narudžbi, {order.customer_name}!"
        body_html = f"""
        <html><body>
        <h2>Hvala na narudžbi, {order.customer_name}!</h2>
        <p>Primili smo vašu konfiguraciju sata s ukupnom cijenom {order.price} €.</p>
        </body></html>
        """
        send_email(order.customer_email, subject, body_plain, body_html)

        # Email adminu
        admin_body = f"""
        <html><body>
        <h3>Nova narudžba od {order.customer_name} {order.customer_surname}</h3>
        <p>Email: {order.customer_email}</p>
        <p>Telefon: {order.customer_phone}</p>
        <p>Adresa: {order.customer_address}, {order.customer_city}, {order.customer_postcode}</p>
        <p>Konfiguracija: {order.case}, {order.dial}, {order.hands}, {order.strap}, {order.box}</p>
        <p>Cijena: {order.price} €</p>
        <p>Plaćanje: {order.payment_method}</p>
        <p>Gravura: {order.engraving}</p>
        </body></html>
        """
        send_email(GMAIL_USER, f"Nova narudžba od {order.customer_name}", body_plain, admin_body)

    except Exception as e:
        print("Greška prilikom slanja maila:", str(e))

    return {"message": "Narudžba je zaprimljena!"}    

# Pokretanje servera kad se main.py izvršava direktno
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
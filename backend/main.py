import os
from dotenv import load_dotenv
load_dotenv()
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

# Serve static images
img_path = Path(__file__).parent / "static" / "img"
if img_path.exists():
    app.mount("/img", StaticFiles(directory=img_path), name="img")

# DB init
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

def format_html(order: WatchConfiguration, is_admin=False):
    content = f"""
    <p><strong>Konfiguracija sata:</strong></p>
    <ul>
        <li><strong>Kućište:</strong> {order.case}</li>
        <li><strong>Brojčanik:</strong> {order.dial}</li>
        <li><strong>Kazaljke:</strong> {order.hands}</li>
        <li><strong>Remen:</strong> {order.strap}</li>
        <li><strong>Kutija:</strong> {order.box}</li>
        <li><strong>Gravura:</strong> {order.engraving or 'Nema'}</li>
    </ul>
    <p><strong>Ukupna cijena:</strong> {order.price} €</p>
    <p><strong>Podaci za dostavu:</strong></p>
    <ul>
        <li><strong>Ime:</strong> {order.customer_name} {order.customer_surname}</li>
        <li><strong>Adresa:</strong> {order.customer_address}, {order.customer_city}, {order.customer_postcode}</li>
        <li><strong>Broj mobitela:</strong> {order.customer_phone}</li>
        <li><strong>Email:</strong> {order.customer_email}</li>
        <li><strong>Način plaćanja:</strong> {order.payment_method}</li>
    </ul>
    """

    kupac_intro = "<h3>Hvala na narudžbi!</h3>" if not is_admin else ""
    napomena = "<p><em>Napomena: Slika vašeg sata će vam biti poslana u roku 24–48 sati.</em></p>" if not is_admin else ""

    return f"{kupac_intro}{content}{napomena}"

@app.post("/order")
def submit_order(order: WatchConfiguration, session: Session = Depends(get_session)):
    session.add(order)
    session.commit()
    session.refresh(order)

    plain = "Hvala na narudžbi!\nVaš sat je uspješno naručen."

    try:
        # Emailovi
        html_customer = format_html(order, is_admin=False)
        html_admin = format_html(order, is_admin=True)

        send_email(order.customer_email, "Potvrda narudžbe – SeimastersCraft", plain, html_customer)
        send_email("seimasterswatches@gmail.com", f"Nova narudžba od {order.customer_email}", plain, html_admin)

    except Exception as e:
        print("Greška prilikom slanja maila:", e)

    return {"message": "Narudžba zaprimljena, potvrda poslana emailom."}

# Run
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
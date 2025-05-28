#!/bin/bash

echo "🔧 Provjera static/img foldera..."
mkdir -p backend/static/img

echo "📁 Kopiranje slika iz frontend/public/img/ u backend/static/img/"
cp -R frontend/watchcraft-frontend/public/img/* backend/static/img/

echo "✅ Provjera .gitignore da ne ignorira slike..."

if grep -q "static/img" .gitignore || grep -q "\*.png" .gitignore; then
  echo "⚠️ UPOZORENJE: .gitignore možda blokira static/img ili *.png"
  echo "   Molimo ručno ukloni te linije iz .gitignore ako želiš deploy slika."
  exit 1
fi

echo "✅ Dodavanje fajlova u Git..."
git add backend/static/img
git commit -m "Deploy slika u static/img za produkciju"
git push

echo "🚀 Promjene su poslane na GitHub. Railway će sad automatski pokrenuti deploy."
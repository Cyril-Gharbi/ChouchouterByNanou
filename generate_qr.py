import qrcode

# Ton URL Railway
url = "https://web-production-c8a9d.up.railway.app/scan"

# Générer le QR code
img = qrcode.make(url)

# Sauvegarder le fichier
with open("qr_railway.png", "wb") as f:
    img.save(f, format="PNG")

print("QR code créé : qr_railway.png ✅")

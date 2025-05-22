import qrcode

url = "https://fd96-2001-861-3206-56a0-e949-c047-ff23-a2eb.ngrok-free.app/scan"

qr = qrcode.make(url)
qr.save("qr_scan.png")

print("QR code généré : qr_scan.png")
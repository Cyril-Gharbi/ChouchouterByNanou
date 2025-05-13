import qrcode

url = "https://779e-2001-861-3206-56a0-3453-b35-c3da-72e7.ngrok-free.app/scan"

qr = qrcode.make(url)
qr.save("qr_scan.png")

print("QR code généré : qr_scan.png")
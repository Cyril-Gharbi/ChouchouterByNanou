import qrcode

url = "http://localhost:5000/scan"

qr = qrcode.make(url)
qr.save("qr_scan.png")

print("QR code généré : qr_scan.png")
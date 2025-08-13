import cv2
import pytesseract
import re

pytesseract.pytesseract.tesseract_cmd = r"C:\Users\simay\Tesseract-OCR\tesseract.exe"

TR_PLATE_REGEX = re.compile(r'^(0[1-9]|[1-7][0-9]|8[0-1])[ ]?([A-Z]{1,3})[ ]?(\d{2,4})$')

kamera = cv2.VideoCapture(0)
if not kamera.isOpened():
    print("Kamera acilmadi!")
    raise SystemExit

print("Kamera baslatildi. Dogrulama icin 'E' (evet) veya 'H' (hayır) tuslarini kullan.")
frame_count = 0
ocr_interval = 10
plaka = ""
son_okunan = ""

while True:
    ret, kare = kamera.read()
    if not ret:
        print("Kare alinamadi!")
        break

    frame_count += 1

    if frame_count % ocr_interval == 0:
        gri = cv2.cvtColor(kare, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        gri = clahe.apply(gri)
        _, binimg = cv2.threshold(gri, 110, 255, cv2.THRESH_BINARY)

        config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        raw = pytesseract.image_to_string(binimg, lang='eng', config=config)

        txt = re.sub(r'[^A-Z0-9 ]', '', raw.upper())
        txt = txt.replace('Ö', 'O').replace('O', '0') if False else txt
        txt_compact = txt.replace(" ", "")

        m = re.match(r'(\d{2})([A-Z]{1,3})(\d{2,4})', txt_compact)
        if m:
            aday = f"{m.group(1)} {m.group(2)} {m.group(3)}"
            if TR_PLATE_REGEX.match(aday):
                son_okunan = aday  # ekranda onay isteyeceğiz

    cv2.putText(kare, f"Son: {son_okunan or '-'}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    if son_okunan:
        cv2.putText(kare, "E: Onayla, H: Reddet, Q: Cikis", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    cv2.imshow("Kamera", kare)
    key = cv2.waitKey(1) & 0xFF

    if key == ord('q'):
        print("Cikis.")
        break
    if son_okunan and key in (ord('e'), ord('E')):
        plaka = son_okunan
        print(f"Plaka dogrulandi: {plaka}")
        break
    if son_okunan and key in (ord('h'), ord('H')):
        print("Reddedildi, yeni kareler bekleniyor...")
        son_okunan = ""

kamera.release()
cv2.destroyAllWindows()

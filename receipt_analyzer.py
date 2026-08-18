import pytesseract
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r"C:\Users\HP\Desktop\tesseract.exe"

config = r'--tessdata-dir "C:\Users\HP\Desktop\tessdata"'

image = Image.open(r"C:\Users\HP\Downloads\receipt.jpg")

text = pytesseract.image_to_string(
    image,
    lang="eng",
    config=config
)

print(text)
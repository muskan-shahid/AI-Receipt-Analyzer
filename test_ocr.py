import os
import pytesseract
from PIL import Image

# Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r"C:\Users\HP\Desktop\tesseract.exe"

# Tesseract language data folder
os.environ["TESSDATA_PREFIX"] = r"C:\Users\HP\Desktop\tessdata"

# Receipt image
image = Image.open(r"C:\Users\HP\Downloads\receipt.jpg")

# Extract text
text = pytesseract.image_to_string(
    image,
    lang="eng"
)

print("===== OCR RESULT =====")
print(text)
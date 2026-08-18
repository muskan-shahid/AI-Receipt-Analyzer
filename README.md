# 🧾 AI Receipt Analyzer

> Transform receipt images into structured financial insights using AI-powered OCR, data extraction, analytics, and interactive visualizations.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-App-red?logo=streamlit)
![OCR](https://img.shields.io/badge/OCR-Tesseract-green)
![AI](https://img.shields.io/badge/AI-Powered-purple)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 📌 Overview

**AI Receipt Analyzer** is an intelligent receipt-processing application that converts unstructured receipt images into clean, structured financial data and actionable insights.

Simply upload a receipt, and the system leverages OCR preprocessing and pattern recognition algorithms to extract key transaction metrics, itemized lists, and spending classifications. The parsed data is automatically analyzed and displayed through interactive Streamlit dashboards.

---

## ✨ Key Features

* **📷 Multiformat Upload:** Supports high-resolution receipt images in `JPG`, `JPEG`, `PNG`, and `WEBP` formats.
* **🔍 AI & Tesseract OCR:** Automated pre-processing with OpenCV (grayscale, noise reduction, thresholding) followed by text extraction via PyTesseract.
* **🧠 Structured Extraction:** Smart identification of core financial attributes:
  * 🏪 **Merchant:** Store name and vendor metadata.
  * 📅 **Date & Time:** Standardized transaction timestamp.
  * 💳 **Payment Method:** Credit, debit, or cash tags.
  * 🧾 **Itemized Breakdown:** Product names, quantities, and individual prices.
  * 💰 **Financial Totals:** Subtotal, Tax/VAT, tips, and grand total.
* **📊 Analytics & Visualizations:** Interactive expense dashboards displaying spending by category, vendor trends, and price breakdowns.
* **📂 Data Export:** Download parsed financial records in structured JSON or CSV formats.

---

## 🛠️ Tech Stack

* **Language:** Python 3.10+
* **Framework:** Streamlit
* **OCR & Vision:** Tesseract OCR, PyTesseract, OpenCV (`opencv-python`), Pillow (`PIL`)
* **Data & Analytics:** Pandas, NumPy, Matplotlib

---

## 📂 Project Structure

```text
AI-Receipt-Analyzer/
│
├── assets/             # Screenshots, badges, and UI design assets
├── outputs/            # Extracted JSON/CSV exports (ignored by git)
├── uploads/            # Temporary storage for uploaded receipts (ignored by git)
│
├── .gitignore          # Excludes temporary outputs, venv, and user uploads
├── app.py              # Main Streamlit web application dashboard
├── receipt_analyzer.py # Core OCR preprocessing & data extraction logic
├── README.md           # Project documentation
└── requirements.txt    # Python dependencies
```
## 📸 App Preview & Interface

### 📥 1. Image Upload & Receipt Parsing
Upload receipt images (`.jpg`, `.jpeg`, `.png`, `.webp`) for automatic field extraction and OCR processing.

![Upload Interface](assets/01-upload-interface.png)

---

### 🧾 2. Receipt Extraction & Key Metadata
View extracted merchant details, transaction dates, payment types, and line items side-by-side with the receipt image.

![Receipt Summary & Details](assets/02-receipt-summary.png)

---
## 📸 Screenshots

### 🏠 Main Interface

<img width="945" height="379" alt="Main Interface" src="https://github.com/user-attachments/assets/37c559c2-fb4d-4fa9-84b2-a91b4736afc2" />

---

### 🔍 OCR Results

<img width="740" height="394" alt="OCR Results" src="https://github.com/user-attachments/assets/a91f1cf1-88a0-41cf-b700-778ec160faea" />

---

### 💰 Financial Insights

<img width="746" height="404" alt="Financial Insights" src="https://github.com/user-attachments/assets/f71d80ee-d7fe-404c-825d-16510f0dd0f6" />

---

### 📊 Analytics

<img width="739" height="391" alt="Analytics" src="https://github.com/user-attachments/assets/5929025b-19d9-4d1c-8762-191b9da972b4" />

---

### 📈 Visualizations

<img width="1443" height="781" alt="Visualizations" src="https://github.com/user-attachments/assets/b36acc24-03f9-4021-9c2b-e72ae556d149" />
---
## 👩‍💻 Author

**Muskan Shahid**

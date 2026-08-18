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

### 📊 3. Financial Breakdown & Visual Analytics
Interactive charts display expenditure totals, itemized price distribution, and spending ratios.

<p align="center">
  <img src="assets/03-financial-breakdown.png" width="48%" title="Financial Overview">
  <img src="assets/04-spending-by-item.png" width="48%" title="Itemized Charts">
</p>

---

### 💡 4. Savings Insights & Raw Export
Analyze savings metrics and export parsed items directly to structured JSON or CSV format.

<p align="center">
  <img src="assets/05-savings-gauge.png" width="48%" title="Savings Rate Gauge">
  <img src="assets/06-extracted-items-table.png" width="48%" title="Extracted Items Table">
</p>


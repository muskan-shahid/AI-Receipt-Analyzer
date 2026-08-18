import json
import os
import re
import shutil
from pathlib import Path

import pandas as pd
import pytesseract
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go


from PIL import (
    Image,
    ImageEnhance,
    ImageFilter,
    ImageOps,
    ImageStat,
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Receipt Analyzer",
    page_icon="🧾",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# TESSERACT PATH RESOLUTION
# ============================================================

def resolve_tesseract():
    """
    Find Tesseract automatically on Windows.
    """

    possible_paths = [
        Path(
            r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        ),
        Path(
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"
        ),
        Path(
            r"C:\Users\HP\Desktop\tesseract.exe"
        ),
    ]

    for path in possible_paths:

        if path.is_file():
            return path

    system_path = shutil.which("tesseract")

    if system_path:
        return Path(system_path)

    return None


TESSERACT_PATH = resolve_tesseract()


# ============================================================
# TESSDATA PATH
# ============================================================


def resolve_tessdata(tesseract_path):
    """Find tessdata on Windows and Linux/Streamlit Cloud."""

    if tesseract_path is None:
        return None

    possible_paths = [
        tesseract_path.parent / "tessdata",

        # Linux / Streamlit Cloud
        Path("/usr/share/tesseract-ocr/tessdata"),
        Path("/usr/share/tesseract-ocr/5/tessdata"),
        Path("/usr/share/tesseract-ocr/4.00/tessdata"),
        Path("/usr/share/tesseract-ocr/5.3/tessdata"),

        # Windows
        Path("C:/Program Files/Tesseract-OCR/tessdata"),
        Path("C:/Program Files (x86)/Tesseract-OCR/tessdata"),
        Path("C:/Users/HP/Desktop/tessdata"),
    ]

    for path in possible_paths:
        if path.is_dir():
            return path

    for base_path in [
        Path("/usr/share"),
        Path("/usr/local/share"),
    ]:
        if base_path.exists():
            try:
                for path in base_path.rglob("tessdata"):
                    if path.is_dir():
                        return path
            except (PermissionError, OSError):
                pass

    return None


TESSDATA_PATH = resolve_tessdata(
    TESSERACT_PATH
)

if TESSDATA_PATH:

    ENG_DATA_PATH = (
        TESSDATA_PATH / "eng.traineddata"
    )

else:

    ENG_DATA_PATH = None


# ============================================================
# TESSERACT SETUP
# ============================================================

def setup_tesseract():

    if TESSERACT_PATH is None:

        return False, (
            "Tesseract executable was not found.\n\n"
            "Expected location:\n"
            "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
        )

    if TESSDATA_PATH is None:

        return False, (
            "Tessdata folder was not found."
        )

    if ENG_DATA_PATH is None or not ENG_DATA_PATH.is_file():

        return False, (
            "eng.traineddata was not found in:\n"
            f"{TESSDATA_PATH}"
        )

    pytesseract.pytesseract.tesseract_cmd = str(
        TESSERACT_PATH
    )

    # Point directly to the tessdata folder.
    os.environ["TESSDATA_PREFIX"] = str(
        TESSDATA_PATH
    )

    return True, "Tesseract configured successfully."


tesseract_ok, tesseract_message = setup_tesseract()


# ============================================================
# GET AVAILABLE OCR LANGUAGES
# ============================================================

def get_available_languages():

    if not tesseract_ok:
        return ["eng"]

    try:

        languages = pytesseract.get_languages(
            config=""
        )

        languages = set(
            languages
        )

        options = []

        # English
        if "eng" in languages:
            options.append(
                ("English", "eng")
            )

        # Polish
        if "pol" in languages:
            options.append(
                ("Polish", "pol")
            )

        # English + Polish
        if (
            "eng" in languages
            and "pol" in languages
        ):
            options.append(
                ("English + Polish", "eng+pol")
            )

        # Urdu
        if "urd" in languages:
            options.append(
                ("Urdu", "urd")
            )

        # English + Urdu
        if (
            "eng" in languages
            and "urd" in languages
        ):
            options.append(
                ("English + Urdu", "eng+urd")
            )

        # Hindi
        if "hin" in languages:
            options.append(
                ("Hindi", "hin")
            )

        if not options:
            options = [
                ("English", "eng")
            ]

        return options

    except Exception:

        return [
            ("English", "eng")
        ]


language_options = get_available_languages()


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>
    /* =========================================================
       AI RECEIPT ANALYZER — PREMIUM NAVY + CYAN THEME
       ========================================================= */

    .stApp {
        background:
            radial-gradient(circle at 88% 0%, rgba(34,211,238,0.10), transparent 30%),
            radial-gradient(circle at 5% 85%, rgba(20,184,166,0.08), transparent 32%),
            #07111f;
        color: #e8f1f8;
    }

    .main .block-container {
        max-width: 1450px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a1728 0%, #081321 100%);
        border-right: 1px solid rgba(148,163,184,0.12);
    }

    section[data-testid="stSidebar"] * {
        color: #dbeafe;
    }

    section[data-testid="stSidebar"] .stCaption {
        color: #94a3b8 !important;
    }

    h1 {
        color: #f8fafc !important;
        letter-spacing: -0.03em;
        font-weight: 800 !important;
    }

    h2, h3 {
        color: #e2e8f0 !important;
        font-weight: 750 !important;
    }

    .hero {
        padding: 24px 28px;
        margin: 8px 0 28px 0;
        border: 1px solid rgba(34,211,238,0.18);
        border-radius: 20px;
        background:
            linear-gradient(135deg, rgba(15,31,52,0.92), rgba(9,25,42,0.72));
        box-shadow: 0 18px 50px rgba(0,0,0,0.20);
    }

    .hero-kicker {
        color: #22d3ee;
        font-size: 0.78rem;
        font-weight: 800;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        margin-bottom: 7px;
    }

    .hero-title {
        color: #f8fafc;
        font-size: 2.25rem;
        font-weight: 850;
        line-height: 1.05;
        margin-bottom: 8px;
    }

    .hero-text {
        color: #9fb3c8;
        font-size: 1rem;
        margin: 0;
    }

    div[data-testid="stMetric"] {
        background: linear-gradient(145deg, rgba(15,30,49,0.92), rgba(10,23,39,0.88));
        border: 1px solid rgba(148,163,184,0.13);
        border-radius: 16px;
        padding: 16px 18px;
        box-shadow: 0 8px 28px rgba(0,0,0,0.18);
    }

    div[data-testid="stMetricLabel"] {
        color: #8fa5ba !important;
        font-size: 0.82rem !important;
        font-weight: 600 !important;
    }

    div[data-testid="stMetricValue"] {
        color: #22d3ee !important;
        font-weight: 800 !important;
        font-size: 1.25rem !important;
    }

    .stButton > button,
    .stDownloadButton > button {
        border-radius: 11px;
        min-height: 44px;
        font-weight: 750;
        background: linear-gradient(135deg, #22d3ee 0%, #14b8a6 100%);
        color: #03131d;
        border: 0;
        box-shadow: 0 8px 22px rgba(34,211,238,0.14);
        transition: all 0.2s ease;
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover {
        box-shadow: 0 0 24px rgba(34,211,238,0.28);
        transform: translateY(-1px);
    }

    div[data-testid="stFileUploader"] {
        border: 1px dashed rgba(34,211,238,0.35);
        border-radius: 16px;
        background: rgba(11,27,44,0.58);
        padding: 6px;
    }

    div[data-baseweb="select"] > div,
    .stTextInput > div > div,
    .stTextArea textarea {
        background: #0b1b2d !important;
        border-color: rgba(148,163,184,0.18) !important;
        color: #e2e8f0 !important;
    }

    .ocr-box {
        background: #06101c;
        border: 1px solid rgba(34,211,238,0.12);
        border-radius: 14px;
        padding: 18px;
    }

    .status-card {
        padding: 12px 14px;
        border-radius: 12px;
        background: rgba(34,211,238,0.07);
        border: 1px solid rgba(34,211,238,0.14);
        color: #bae6fd;
        margin-bottom: 14px;
    }

    .stAlert {
        border-radius: 12px !important;
    }

    .stDataFrame {
        border-radius: 14px;
        overflow: hidden;
    }

    hr {
        border-color: rgba(148,163,184,0.10) !important;
    }

    footer {
        visibility: hidden;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title(
        "🧾 AI Receipt Analyzer"
    )

    st.write(
        "Transform receipt images into "
        "structured financial insights."
    )

    st.divider()

    if tesseract_ok:

        st.success(
            "✅ OCR Engine Online"
        )

        try:

            version = str(
                pytesseract.get_tesseract_version()
            )

            st.caption(
                version
            )

        except Exception:

            st.caption(
                "Tesseract loaded"
            )

    else:

        st.error(
            "❌ OCR Engine Error"
        )

        st.code(
            tesseract_message
        )

    st.divider()

    st.subheader(
        "Supported Receipts"
    )

    st.write("🛒 Grocery")
    st.write("👕 Clothing")
    st.write("🍔 Restaurant")
    st.write("💊 Pharmacy")
    st.write("🏪 Retail")
    st.write("💳 Card / Cash")
    st.write("🧾 Invoice-style")
    st.write("🇵🇱 Polish receipts")


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="hero">
        <div class="hero-kicker">AI • OCR • FINANCIAL INSIGHTS</div>
        <div class="hero-title">Receipt Intelligence</div>
        <p class="hero-text">
            Turn receipt images into structured financial data with OCR,
            automatic field extraction, item detection, and JSON export.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# UPLOAD
# ============================================================

st.subheader(
    "📤 Upload your receipt"
)

uploaded_file = st.file_uploader(
    "JPG, JPEG, PNG or WEBP",
    type=[
        "jpg",
        "jpeg",
        "png",
        "webp",
    ],
)


# ============================================================
# EMPTY STATE
# ============================================================

if uploaded_file is None:

    st.info(
        "🧾 Upload a receipt to begin. "
        "Supported: grocery, retail, restaurant, "
        "pharmacy and invoice receipts."
    )

    st.stop()


# ============================================================
# IMAGE
# ============================================================

try:

    image = Image.open(
        uploaded_file
    ).convert("RGB")

except Exception as error:

    st.error(
        f"Could not open image: {error}"
    )

    st.stop()

# ============================================================
# OCR LANGUAGE
# ============================================================

language_options = [
    ("English", "eng"),
    ("Polish", "pol"),
]

language_labels = [
    label
    for label, code in language_options
]

selected_label = st.selectbox(
    "OCR Language",
    language_labels,
)

selected_language = dict(
    language_options
)[selected_label]

# ============================================================
# IMAGE PREPROCESSING
# ============================================================

def preprocess_image(img):
    """
    Create several OCR-friendly image variants.

    Receipts often contain tiny text, uneven lighting, gray paper,
    shadows, and low contrast. Using more than one preprocessing
    variant makes Tesseract much more reliable than a single pass.
    """

    # Fix camera orientation when EXIF data is available.
    img = ImageOps.exif_transpose(img).convert("RGB")

    width, height = img.size

    # Upscale small receipt images while preserving aspect ratio.
    target_width = 2200
    if width < target_width:
        scale = target_width / width
        img = img.resize(
            (int(width * scale), int(height * scale)),
            Image.Resampling.LANCZOS,
        )

    gray = ImageOps.grayscale(img)
    gray = ImageOps.autocontrast(gray, cutoff=1)

    # Mild denoising before sharpening.
    denoised = gray.filter(ImageFilter.MedianFilter(size=3))
    enhanced = ImageEnhance.Contrast(denoised).enhance(2.0)
    enhanced = ImageEnhance.Sharpness(enhanced).enhance(1.8)
    enhanced = enhanced.filter(ImageFilter.SHARPEN)

    # High-contrast binary version. The threshold is deliberately
    # moderate so thin receipt characters are not erased.
    threshold = enhanced.point(lambda p: 255 if p > 175 else 0)

    return [
        ("enhanced", enhanced),
        ("threshold", threshold),
        ("original_gray", gray),
    ]


def _ocr_score(text, confidence_values):
    """
    Score an OCR result using both useful text length and
    Tesseract confidence. This avoids selecting a long result
    containing mostly noise.
    """
    cleaned = re.sub(r"\s+", " ", text).strip()
    if not cleaned:
        return -1

    letters = len(re.findall(r"[A-Za-zĄąĆćĘęŁłŃńÓóŚśŹźŻż]", cleaned))
    digits = len(re.findall(r"\d", cleaned))
    useful = letters + digits

    valid_conf = [float(v) for v in confidence_values if str(v) not in ("-1", "")]
    avg_conf = sum(valid_conf) / len(valid_conf) if valid_conf else 0

    # Receipt OCR needs both readable words and numbers.
    return (avg_conf * 1.8) + min(useful, 220) * 0.35


def run_ocr(img, language):
    """
    Robust receipt OCR.

    IMPORTANT: do not choose the OCR result only by character count or
    confidence. For receipts, preserving lines and detecting words such
    as QTY, ITEM, PAYMENT and CARD is more important.
    """
    variants = preprocess_image(img)
    candidates = []
    psm_modes = [6, 4, 11, 3]

    receipt_keywords = (
        "RECEIPT", "QTY", "ITEM", "PAYMENT", "CARD", "TOTAL",
        "SUBTOTAL", "TAX", "VAT", "THANK", "CASH", "DECLINED",
        "INVOICE", "DATE"
    )

    for variant_name, processed in variants:
        for psm in psm_modes:
            try:
                text = pytesseract.image_to_string(
                    processed,
                    lang=language,
                    config=f"--oem 3 --psm {psm}",
                    timeout=30,
                ).strip()

                if not text:
                    continue

                upper = text.upper()
                keyword_hits = sum(1 for word in receipt_keywords if word in upper)
                lines = [x.strip() for x in text.splitlines() if x.strip()]
                alpha_words = len(re.findall(r"[A-Za-z]{2,}", text))
                digits = len(re.findall(r"\d", text))
                useful_lines = sum(
                    1 for line in lines
                    if re.search(r"[A-Za-z]", line) and len(line) >= 3
                )

                # Receipt-specific score. Keep line-rich PSM 6/4 ahead of
                # sparse PSM 11 when both contain the same information.
                score = (
                    keyword_hits * 35
                    + min(alpha_words, 100) * 1.5
                    + min(digits, 80) * 0.8
                    + min(useful_lines, 35) * 2.0
                    + (8 if psm in (6, 4) else 0)
                )

                candidates.append({
                    "text": text,
                    "score": score,
                    "variant": variant_name,
                    "psm": psm,
                })

            except Exception:
                continue

    if not candidates:
        return ""

    best = max(candidates, key=lambda item: item["score"])

    # Re-run the selected configuration to preserve the exact line layout.
    for variant_name, processed in variants:
        if variant_name == best["variant"]:
            try:
                return pytesseract.image_to_string(
                    processed,
                    lang=language,
                    config=f"--oem 3 --psm {best['psm']}",
                    timeout=30,
                ).strip()
            except Exception:
                break

    return best["text"]

# ============================================================
# TEXT NORMALIZATION
# ============================================================

def clean_ocr_text(text):
    """
    Clean common OCR whitespace issues.
    """

    text = text.replace(
        "\x0c",
        ""
    )

    text = text.replace(
        "\r",
        "\n"
    )

    # Normalize common OCR punctuation/spacing artifacts.
    text = text.replace("—", "-").replace("–", "-")
    # Common receipt OCR substitutions. Only apply safe, context-specific fixes.
    text = re.sub(r"(EVERY\s+DAY\s+)3[.:]83\s*(AM|PM)", r"\g<1>3:03 \2", text, flags=re.IGNORECASE)
    text = re.sub(r"(EVERY\s+DAY\s+)3[.:]03\s*(AM|PM)", r"\g<1>3:03 \2", text, flags=re.IGNORECASE)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n[ \t]+", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


# ============================================================
# AMOUNT NORMALIZATION
# ============================================================

def normalize_amount(value):
    """
    Normalize monetary values.

    Handles:

        29.99
        29,99
        1.299,99
        1,299.99
    """

    if value is None:
        return 0.0

    value = str(
        value
    ).strip()

    value = re.sub(
        r"[^\d,.\-]",
        "",
        value
    )

    if not value:
        return 0.0

    # European decimal
    if (
        "," in value
        and "." not in value
    ):

        value = value.replace(
            ",",
            "."
        )

    # Both separators
    elif (
        "," in value
        and "." in value
    ):

        # European:
        # 1.299,99
        if (
            value.rfind(",")
            >
            value.rfind(".")
        ):

            value = value.replace(
                ".",
                ""
            )

            value = value.replace(
                ",",
                "."
            )

        # US:
        # 1,299.99
        else:

            value = value.replace(
                ",",
                ""
            )

    try:

        return float(
            value
        )

    except ValueError:

        return 0.0


def decimal_amounts(text):
    """
    Extract decimal monetary values.
    """

    return re.findall(
        r"\d+(?:[.,]\d{2})",
        text
    )


# ============================================================
# CURRENCY
# ============================================================

def detect_currency(text):
    """
    Detect currency using currency codes/symbols
    and regional receipt indicators.
    """

    upper = text.upper()

    # Explicit currencies
    if (
        "PLN" in upper
        or "ZŁ" in upper
        or "ZLOT" in upper
    ):
        return "PLN"

    if (
        "EUR" in upper
        or "€" in text
    ):
        return "EUR"

    if (
        "GBP" in upper
        or "£" in text
    ):
        return "GBP"

    if (
        "USD" in upper
        or "$" in text
    ):
        return "USD"

    if (
        "PKR" in upper
        or "₨" in text
    ):
        return "PKR"

    # Polish OCR indicators
    polish_indicators = [
        "PTU",
        "KARTA",
        "SUMA",
        "SPRZED",
        "PARAGON",
    ]

    if any(
        indicator in upper
        for indicator in polish_indicators
    ):
        return "PLN"

    return "Unknown"


def format_amount(
    value,
    currency
):
    """
    Display monetary value. Zero is shown as "Not detected"
    when no financial amount was actually extracted.
    """

    if value is None or value <= 0:
        return "Not detected"

    if not currency or currency == "Unknown":
        return f"{value:,.2f}"

    return f"{value:,.2f} {currency}"


# ============================================================
# DATE
# ============================================================

def extract_date(text):
    """Extract the purchase date while ignoring RETURN BY / expiration dates."""
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue

        if re.search(r"\bRETURN\s+BY\b|\bEXPIRES?\b|\bVALID\s+THRU\b", line, re.I):
            continue

        # YYYY-MM-DD / YYYY.MM.DD / YYYY+MM+DD
        m = re.search(r"\b(20\d{2})[-/.+](0?[1-9]|1[0-2])[-/.+](0?[1-9]|[12]\d|3[01])\b", line)
        if m:
            y, mo, d = map(int, m.groups())
            return f"{y:04d}-{mo:02d}-{d:02d}"

        # MM/DD/YYYY or MM/DD/YY
        m = re.search(r"\b(0?[1-9]|1[0-2])[-/.](0?[1-9]|[12]\d|3[01])[-/.](20\d{2}|\d{2})\b", line)
        if m:
            mo, d, y = m.groups()
            y = int(y)
            if y < 100:
                y += 2000
            return f"{y:04d}-{int(mo):02d}-{int(d):02d}"

        # DD/MM/YYYY or DD/MM/YY, only when first number > 12
        m = re.search(r"\b(1[3-9]|2\d|3[01])[-/.](0?[1-9]|1[0-2])[-/.](20\d{2}|\d{2})\b", line)
        if m:
            d, mo, y = m.groups()
            y = int(y)
            if y < 100:
                y += 2000
            return f"{y:04d}-{int(mo):02d}-{int(d):02d}"

    return "Not detected"


# ============================================================
# TIME
# ============================================================

def extract_time(text):
    """Extract a valid time and reject impossible OCR readings."""
    match = re.search(
        r"\b(\d{1,2})\s*[:.]\s*(\d{2})\s*(AM|PM)?\b",
        text,
        flags=re.IGNORECASE,
    )

    if not match:
        return "Not detected"

    hour = int(match.group(1))
    minute = int(match.group(2))
    meridiem = match.group(3)

    if hour > 23 or minute > 59:
        return "Not detected"

    if meridiem:
        return f"{hour}:{minute:02d} {meridiem.upper()}"

    return f"{hour}:{minute:02d}"

# ============================================================
# PAYMENT
# ============================================================

def extract_payment(text):
    """Detect payment method, prioritizing explicit receipt payment labels."""
    upper = text.upper()

    # Explicit debit/credit labels should take priority over generic CARD.
    if re.search(r"\b(?:DEBIT\s+CARD|US\s+DEBIT|DEBIT)\b", upper):
        if "DECLINED" in upper or "DECLINE" in upper:
            return "Debit Card — Declined"
        return "Debit Card"

    if re.search(r"\b(?:CREDIT\s+CARD|CREDIT)\b", upper):
        if "DECLINED" in upper or "DECLINE" in upper:
            return "Credit Card — Declined"
        return "Credit Card"

    if re.search(r"\b(?:KARTA|CARD)\b", upper):
        if "DECLINED" in upper or "DECLINE" in upper:
            return "Card — Declined"
        return "Card"

    if "VISA" in upper:
        return "Visa"
    if "MASTERCARD" in upper or "MASTER CARD" in upper:
        return "Mastercard"
    if "CASH" in upper or "GOTOWKA" in upper or "GOTÓWKA" in upper:
        return "Cash"
    if "PAYPAL" in upper:
        return "PayPal"
    if "APPLE PAY" in upper:
        return "Apple Pay"
    if "GOOGLE PAY" in upper:
        return "Google Pay"

    return "Not detected"


# ============================================================
# MERCHANT
# ============================================================

def extract_merchant(text):
    """Extract the merchant from the top of the receipt."""
    lines = [re.sub(r"\s+", " ", line).strip() for line in text.splitlines() if line.strip()]

    # Strong known-brand/company matches.
    for line in lines[:15]:
        upper = line.upper()
        if re.fullmatch(r"TARGET", upper):
            return "TARGET"
        if re.search(r"\bSMYK\s*S\.?\s*A\.?\b", upper):
            return "SMYK S.A."

    ignore = re.compile(
        r"receipt|invoice|subtotal|total|tax|vat|gst|paragon|date|time|"
        r"tel|phone|www|thank\s*you|thankyou|cashier|terminal|"
        r"return\s+by|expires?|valid\s+thru|payment|qty|item|"
        r"you\s+were\s+served|every\s+day|no\s+refunds|no\s+returns",
        re.IGNORECASE,
    )

    # Prefer clean top-of-receipt names and reject addresses, barcodes and metadata.
    for line in lines[:15]:
        clean = re.sub(r"^[^A-Za-zĄąĆćĘęŁłŃńÓóŚśŹźŻż]+", "", line).strip()
        if not (3 <= len(clean) <= 70):
            continue
        if ignore.search(clean):
            continue
        if re.fullmatch(r"[\d\W_]+", clean):
            continue
        if re.search(
            r"\b(?:st|street|rd|road|ave|avenue|blvd|drive|dr|way|"
            r"irvine|warszawa|skarzysko|nip|bdo)\b",
            clean,
            re.I,
        ):
            continue
        return clean[:70]

    return "Not detected"


# ============================================================
# TAX EXTRACTION
# ============================================================

def _money_values(line):
    """Extract monetary-looking values, including OCR spacing such as '$29. 41'."""
    line = line.replace(" ", "")
    values = re.findall(
        r"(?<!\d)(?:\d{1,3}(?:[,.]\d{3})*|\d+)(?:[.,]\d{2})(?!\d)",
        line,
    )
    return [normalize_amount(v) for v in values if normalize_amount(v) > 0]


def _next_money(lines, index, lookahead=2):
    """Find the first monetary value on the current or next few lines."""
    for j in range(index, min(index + lookahead + 1, len(lines))):
        vals = _money_values(lines[j])
        if vals:
            return vals[-1]
    return 0.0


def extract_tax(text):
    """
    Extract the actual tax/VAT amount.

    Important:
    On Target receipts the TAX line can contain BOTH:
      - the taxable base, e.g. 25.38
      - the actual tax, e.g. 2.03

    Never use the taxable base as the tax amount.
    """
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    for i, line in enumerate(lines):
        upper = line.upper()

        if not re.search(
            r"\b(?:TAX|VAT|GST|SALES\s*TAX|CA\s*TAX|PODATEK|PTU)\b",
            upper,
        ):
            continue

        # If the line contains a percentage/rate, the actual tax is
        # normally printed on the following line.
        if re.search(r"\d+(?:[.,]\d+)?\s*%", line):
            # Target-style OCR may put both taxable base and actual tax
            # on the same line:
            # CA TAX 8.0000% on $25.38 $2.03
            after_on = re.search(
                r"\bon\b.*?((?:[$€£₹]\s*)?\d+(?:[.,]\s*\d{2}))",
                line,
                re.I,
            )
            all_values = _money_values(line)
            if after_on:
                # If there is another amount after the taxable base,
                # that last amount is the actual tax.
                if len(all_values) >= 2:
                    return all_values[-1]
                if all_values:
                    # Only one amount after "on": use the following line
                    # if present, otherwise use the same-line amount.
                    value = _next_money(lines, i + 1, 2)
                    return value if value > 0 else all_values[-1]

            value = _next_money(lines, i + 1, 3)
            if value > 0:
                return value

        # Polish fiscal receipts can print the VAT amount on the same
        # line as the PTU label.
        vals = _money_values(line)
        if vals:
            # For "PTU A 23,00% 5,61", choose the last monetary value.
            return vals[-1]

        value = _next_money(lines, i + 1, 3)
        if value > 0:
            return value

    return 0.0


def extract_total(text):
    """Extract the actual receipt total, preferring explicit payment total."""

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    # Highest-confidence Target amount:
    # "*9873 DEBIT TOTAL PAYMENT $29.41"
    for line in lines:
        if re.search(r"\bTOTAL\s+PAYMENT\b", line, re.I):
            values = _money_values(line)
            if values:
                return values[-1]

    # Exact TOTAL line.
    for i, line in enumerate(lines):
        if re.search(r"\bTOTAL\b", line, re.I):
            if re.search(r"\bTOTAL\s+SAVINGS\b", line, re.I):
                continue

            values = _money_values(line)
            if values:
                return values[-1]

            value = _next_money(lines, i + 1, 2)
            if value > 0:
                return value

    # Other receipt grand-total labels.
    for i, line in enumerate(lines):
        if re.match(
            r"^\s*(?:GRAND\s+TOTAL|TOTAL\s+AMOUNT|AMOUNT\s+DUE|"
            r"BALANCE\s+DUE|SUMA|RAZEM|RAZEN|DO\s+ZAPLACENIA|DO\s+ZAPŁATY)\b",
            line,
            re.I,
        ):
            value = _next_money(lines, i, 3)
            if value > 0:
                return value

    return 0.0

def extract_subtotal(text):
    """Extract subtotal from SUBTOTAL or Polish taxable-sales labels."""
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    for i, line in enumerate(lines):
        if re.search(r"\bSUB[\s-]*TOTAL\b", line, re.I):
            value = _next_money(lines, i, 2)
            if value > 0:
                return value

        # Polish fiscal receipt: SPRZED. OPOD. PTU A 29,99
        if re.search(r"\bSPRZED\.?\s*OPOD\b", line, re.I):
            vals = _money_values(line)
            if vals:
                return vals[-1]
            value = _next_money(lines, i + 1, 2)
            if value > 0:
                return value

    return 0.0


# ============================================================
# SAVINGS
# ============================================================

def extract_savings(text):
    """Extract the receipt's explicit total savings/discount amount."""

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    # Strongest Target label.
    for i, line in enumerate(lines):
        if re.search(r"\bTOTAL\s+SAVINGS(?:\s+THIS\s+TRIP)?\b", line, re.I):
            # Prefer an amount after the label on the same line.
            values = _money_values(line)
            if values:
                return values[-1]

            # Otherwise inspect the next few lines.
            value = _next_money(lines, i + 1, 3)
            if value > 0:
                return value

    # Other explicit total/discount labels.
    for i, line in enumerate(lines):
        if re.search(
            r"\b(?:TOTAL\s+DISCOUNT|SAVINGS|DISCOUNT|RABAT)\b",
            line,
            re.I,
        ):
            values = _money_values(line)
            if values:
                return values[-1]

            value = _next_money(lines, i + 1, 2)
            if value > 0:
                return value

    return 0.0

# ============================================================
# ITEM EXTRACTION
# ============================================================

def extract_items(text):
    """Extract retail receipt items from both line-separated and compact OCR."""

    lines = [
        re.sub(r"\s+", " ", x).strip()
        for x in text.splitlines()
        if x.strip()
    ]
    items = []

    def money_values(line):
        return _money_values(line)

    def is_barcode(value):
        return bool(re.fullmatch(r"\d{6,20}", re.sub(r"[\s.-]", "", value)))

    def clean_name(value):
        value = re.sub(r"\s+", " ", value).strip(" .:-|'\"|")
        value = re.sub(r"^[^A-Za-zĄąĆćĘęŁłŃńÓóŚśŹźŻż]+", "", value)
        value = re.sub(r"\s+", " ", value).strip()
        return value

    def valid_name(value):
        if not value or len(value) < 3:
            return False
        if not re.search(r"[A-Za-zĄąĆćĘęŁłŃńÓóŚśŹźŻż]", value):
            return False
        if re.fullmatch(r"[A-Za-z]", value):
            return False
        if re.search(
            r"^(TARGET|USA|SUBTOTAL|TOTAL|TAX|SAVINGS|DEBIT|CREDIT|PAYMENT|"
            r"RETURN|INDICATES|ENTERTAINMENT(?:\s*-\s*)?ELECTRONICS|GROCERY|"
            r"HOME|PARAGON|KARTA|ROZLICZENIE|SUMA|PTU|NIP|BDO)$",
            value,
            re.I,
        ):
            return False
        return True

    def add_item(name, price):
        name = clean_name(name)
        if not valid_name(name):
            name = "Not detected"

        item = {
            "Quantity": 1,
            "Item": name,
            "Price": price,
            "Price Status": "Detected",
        }

        key = (item["Item"].upper(), round(item["Price"], 2))
        if not any(
            (x["Item"].upper(), round(x["Price"], 2)) == key
            for x in items
        ):
            items.append(item)

    # --------------------------------------------------------
    # Compact OCR: barcode + product + T + price on one line.
    # Example:
    # 059030549: CLAUS COUTUR. T $9.95
    # --------------------------------------------------------
    compact_pattern = re.compile(
        r"(?P<barcode>\d{6,20})\s*[:|.-]?\s*"
        r"(?P<name>.+?)\s+"
        r"(?:T|FN|H)\s*[.:,;\-]*\s*"
        r"(?P<price>[$€£₹]?\s*\d+(?:[.,]\s*[.,]?\s*\d{2}))\b",
        re.I,
    )

    for line in lines:
        for match in compact_pattern.finditer(line):
            name = match.group("name")
            price_text = re.sub(r"\s+", "", match.group("price"))
            price_text = re.sub(r"\.(?=\.)", "", price_text)
            price_text = re.sub(r"\,(?=\.)", "", price_text)
            price = normalize_amount(price_text)
            # Remove trailing OCR punctuation and noise.
            name = re.sub(r"[\s.]+$", "", name)
            add_item(name, price)

    # --------------------------------------------------------
    # Barcode blocks where OCR preserved separate lines.
    # --------------------------------------------------------
    barcode_indexes = [
        i for i, line in enumerate(lines)
        if is_barcode(line)
    ]

    for pos, barcode_i in enumerate(barcode_indexes):
        next_barcode = (
            barcode_indexes[pos + 1]
            if pos + 1 < len(barcode_indexes)
            else len(lines)
        )

        name_candidates = []
        price = None

        for j in range(barcode_i + 1, next_barcode):
            line = lines[j]

            # Financial section means this barcode block is finished.
            if re.search(
                r"^(SUBTOTAL|TOTAL|SAVINGS|PAYMENT|US\s+DEBIT|AID|"
                r"CA\s*TAX|SALES\s*TAX|TOTAL\s+PAYMENT|ROZLICZENIE|"
                r"SUMA\s+PLN|SUMA\s+PTU)\b",
                line,
                re.I,
            ):
                break

            if re.search(r"^RETURN\s+BY\b", line, re.I):
                continue

            # If OCR kept everything on one line, compact parsing above
            # already handled it.
            if compact_pattern.search(line):
                continue

            if re.fullmatch(r"(?:T|FN|H)", line, re.I):
                continue

            values = money_values(line)
            if values:
                price = values[-1]
                break

            # Ignore receipt metadata and category headings.
            if re.search(
                r"^(USA|AID|VCD|REC\s*#?|NIP|BDO|IRVINE)\b|"
                r"^(ENTERTAINMENT\s*-\s*ELECTRONICS|GROCERY|HOME)$",
                line,
                re.I,
            ):
                continue

            candidate = clean_name(line)
            if valid_name(candidate):
                name_candidates.append(candidate)

        if price is not None:
            name = name_candidates[0] if name_candidates else "Not detected"
            add_item(name, price)

    # --------------------------------------------------------
    # Description -> T -> price when no barcode is present.
    # --------------------------------------------------------
    for i in range(len(lines) - 2):
        line = lines[i]

        if is_barcode(line):
            continue

        if not valid_name(line):
            continue

        if re.search(
            r"TARGET|RETURN\s+BY|SUBTOTAL|TOTAL|TAX|SAVINGS|DEBIT|CREDIT|"
            r"PAYMENT|IRVINE|USA|INDICATES|REC\s*#?|PARAGON|ROZLICZENIE|"
            r"SUMA|PTU",
            line,
            re.I,
        ):
            continue

        if re.fullmatch(r"(?:T|FN|H)", lines[i + 1], re.I):
            values = money_values(lines[i + 2])
            if values:
                add_item(clean_name(line), values[-1])

    # Remove duplicates while preserving order.
    unique = []
    seen = set()

    for item in items:
        key = (
            item["Quantity"],
            item["Item"].upper(),
            round(item["Price"], 2),
        )
        if key not in seen:
            seen.add(key)
            unique.append(item)

    return unique

# ============================================================
# TRANSACTION ID
# ============================================================

def extract_transaction_id(text):
    """Extract transaction/reference ID robustly from OCR."""

    lines = [
        re.sub(r"\s+", " ", line).strip()
        for line in text.splitlines()
        if line.strip()
    ]

    # Target can be OCR'd as:
    # REC#2 -6356-0336-0173-8659-8
    # RECH2-6356-0336-0173-8659-8
    # REC H2 ...
    target_pattern = re.compile(
        r"\bREC\s*[#H]?\s*\d+\s*"
        r"[-\s]*\d+[-\s]*\d+[-\s]*\d+[-\s]*(\d{3,8})[-\s]*\d\b",
        re.I,
    )

    for line in lines:
        match = target_pattern.search(line)
        if match:
            return match.group(1)

        # More permissive fallback: locate REC/RECH followed by
        # a sequence of numeric groups and return the penultimate group.
        if re.search(r"\bREC\s*[#H]?\s*\d", line, re.I):
            tail = line[re.search(r"\bREC\s*[#H]?\s*\d", line, re.I).start():]
            groups = re.findall(r"\d+", tail)
            if len(groups) >= 2:
                return groups[-2]

    # Polish / labelled transaction numbers.
    for i, line in enumerate(lines):
        if re.search(r"\bNR\.?\s*TRANSAK", line, re.I):
            same_line = re.search(
                r"\bNR\.?\s*TRANSAK\S*\s*[:#-]?\s*(\d{3,20})\b",
                line,
                re.I,
            )
            if same_line:
                return same_line.group(1)

            for next_line in lines[i + 1:i + 3]:
                candidate = re.search(r"\b(\d{3,20})\b", next_line)
                if candidate:
                    return candidate.group(1)

    return "Not detected"

# ============================================================
# RUN ANALYSIS
# ============================================================

def analyze_receipt(text):

    cleaned_text = clean_ocr_text(
        text
    )

    data = {

        "merchant": extract_merchant(
            cleaned_text
        ),

        "date": extract_date(
            cleaned_text
        ),

        "time": extract_time(
            cleaned_text
        ),

        "payment": extract_payment(
            cleaned_text
        ),

        "currency": detect_currency(
            cleaned_text
        ),

        "subtotal": extract_subtotal(
            cleaned_text
        ),

        "tax": extract_tax(
            cleaned_text
        ),

        "total": extract_total(
            cleaned_text
        ),

        "savings": extract_savings(
            cleaned_text
        ),

        "items": extract_items(
            cleaned_text
        ),

        "transaction_id": extract_transaction_id(
            cleaned_text
        ),
    }

    return data


# ============================================================
# ANALYZE BUTTON
# ============================================================

analyze = st.button(
    "✨ Analyze Receipt",
    type="primary",
    use_container_width=True,
)


if analyze:

    if not tesseract_ok:

        st.error(
            "Tesseract engine is not available."
        )

        st.code(
            tesseract_message
        )

        st.stop()

    with st.spinner(
        "🔍 Reading receipt..."
    ):

        try:

            raw_text = run_ocr(
                image,
                selected_language,
            )

            if not raw_text.strip():

                st.warning(
                    "No readable text was detected."
                )

                st.stop()

            data = analyze_receipt(
                raw_text
            )

            st.session_state[
                "receipt_text"
            ] = clean_ocr_text(
                raw_text
            )

            st.session_state[
                "receipt_data"
            ] = data

            st.session_state[
                "receipt_image"
            ] = image

            st.markdown(
                '<div class="status-card">✓ Receipt analyzed successfully — OCR and structured extraction completed.</div>',
                unsafe_allow_html=True,
            )

        except Exception as error:

            st.error(
                "OCR execution failed."
            )

            st.code(
                str(error)
            )

            st.stop()

def safe_float(value):
    """
    Safely convert extracted financial values to float.
    Handles None, strings, commas, and OCR text.
    """

    try:
        if value is None:
            return 0.0

        if isinstance(value, str):
            value = value.strip()

            if value.lower() in {
                "",
                "n/a",
                "na",
                "not detected",
                "unknown",
                "none",
            }:
                return 0.0

            # Remove currency symbols/text
            value = re.sub(
                r"[^\d,.\-]",
                "",
                value
            )

            # Handle decimal comma
            if "," in value and "." not in value:
                value = value.replace(",", ".")

            # Handle European format: 1.299,99
            elif "," in value and "." in value:
                if value.rfind(",") > value.rfind("."):
                    value = value.replace(".", "")
                    value = value.replace(",", ".")
                else:
                    # US format: 1,299.99
                    value = value.replace(",", "")

        return float(value)

    except (ValueError, TypeError):
        return 0.0
# ============================================================
# RESULTS
# ============================================================

if "receipt_data" in st.session_state:

    data = st.session_state[
        "receipt_data"
    ]

    receipt_text = st.session_state[
        "receipt_text"
    ]

    receipt_image = st.session_state[
        "receipt_image"
    ]

    currency = data.get(
        "currency",
        "Unknown",
    )

    st.divider()

    # --------------------------------------------------------
    # PREVIEW + SUMMARY
    # --------------------------------------------------------

    left, right = st.columns(
        [1, 1],
        gap="large",
    )

    with left:

        st.subheader(
            "🖼️ Receipt Preview"
        )

        st.image(
            receipt_image,
            use_container_width=True,
        )

    with right:

        st.subheader(
            "🧾 Receipt Summary"
        )

        s1, s2 = st.columns(2)

        with s1:

            st.metric(
                "Merchant",
                data["merchant"],
            )

        with s2:

            st.metric(
                "Date",
                data["date"],
            )

        s3, s4 = st.columns(2)

        with s3:

            st.metric(
                "Payment",
                data["payment"],
            )

        with s4:

            st.metric(
                "Currency",
                currency,
            )

        s5, s6 = st.columns(2)

        with s5:

            st.metric(
                "Time",
                data["time"],
            )

        with s6:

            st.metric(
                "Transaction ID",
                data.get("transaction_id", "Not detected"),
            )

    # --------------------------------------------------------
    # FINANCIAL SUMMARY
    # --------------------------------------------------------

    if (
        data["total"] <= 0
        and data["subtotal"] <= 0
        and data["tax"] <= 0
    ):
        st.info(
            "ℹ️ No clearly labelled financial amounts were detected. "
            "Values are shown as Not detected rather than 0.00."
        )

    st.subheader(
        "💰 Financial Summary"
    )

    m1, m2, m3, m4 = st.columns(4)

    with m1:

        st.metric(
            "Subtotal",
            format_amount(
                data["subtotal"],
                currency,
            ),
        )

    with m2:

        st.metric(
            "Tax",
            format_amount(
                data["tax"],
                currency,
            ),
        )

    with m3:

        st.metric(
            "Total",
            format_amount(
                data["total"],
                currency,
            ),
        )

    with m4:

        st.metric(
            "Savings",
            format_amount(
                data["savings"],
                currency,
            ),
        )
 # ============================================================
# VISUAL FINANCIAL INSIGHTS
# ============================================================

st.subheader("📊 Visual Financial Insights")

subtotal = safe_float(data.get("subtotal"))
tax = safe_float(data.get("tax"))
total = safe_float(data.get("total"))
savings = safe_float(data.get("savings"))

# ------------------------------------------------------------
# FINANCIAL BREAKDOWN
# ------------------------------------------------------------

chart_df = pd.DataFrame({
    "Category": ["Subtotal", "Tax", "Savings", "Total"],
    "Amount": [subtotal, tax, savings, total]
})

fig = px.bar(
    chart_df,
    x="Category",
    y="Amount",
    text="Amount",
    title="💰 Financial Breakdown",
)

fig.update_traces(
    texttemplate="%{text:.2f}",
    textposition="outside"
)

fig.update_layout(
    height=400,
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=20, r=20, t=60, b=20),
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ------------------------------------------------------------
# ITEM SPENDING
# ------------------------------------------------------------

items = data.get("items", [])

if items:

    item_df = pd.DataFrame(items)

    if "Item" in item_df.columns and "Price" in item_df.columns:

        item_df["Price"] = pd.to_numeric(
            item_df["Price"],
            errors="coerce"
        ).fillna(0)

        item_df = item_df[
            item_df["Price"] > 0
        ]

        if not item_df.empty:

            col1, col2 = st.columns(2, gap="large")

            # ------------------------------------------------
            # DONUT CHART
            # ------------------------------------------------

            with col1:

                fig_items = px.pie(
                    item_df,
                    names="Item",
                    values="Price",
                    hole=0.55,
                    title="🛒 Spending by Item"
                )

                fig_items.update_layout(
                    height=430,
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    legend=dict(
                        orientation="h",
                        y=-0.15
                    )
                )

                st.plotly_chart(
                    fig_items,
                    use_container_width=True
                )

            # ------------------------------------------------
            # ITEM PRICE BAR CHART
            # ------------------------------------------------

            with col2:

                item_df_sorted = item_df.sort_values(
                    "Price",
                    ascending=True
                )

                fig_prices = px.bar(
                    item_df_sorted,
                    x="Price",
                    y="Item",
                    orientation="h",
                    text="Price",
                    title="🏷️ Item Prices"
                )

                fig_prices.update_traces(
                    texttemplate="%{text:.2f}",
                    textposition="outside"
                )

                fig_prices.update_layout(
                    height=430,
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    margin=dict(l=20, r=50, t=60, b=20)
                )

                st.plotly_chart(
                    fig_prices,
                    use_container_width=True
                )


# ------------------------------------------------------------
# SAVINGS INSIGHT
# ------------------------------------------------------------

if total > 0 and savings > 0:

    savings_percentage = (
        savings / (total + savings)
    ) * 100

    st.subheader("💡 Savings Insight")

    s1, s2 = st.columns(2)

    with s1:

        st.metric(
            "Total Savings",
            format_amount(
                savings,
                currency
            )
        )

    with s2:

        st.metric(
            "Savings Rate",
            f"{savings_percentage:.1f}%"
        )

    savings_fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=savings_percentage,
            title={
                "text": "Savings Rate"
            },
            gauge={
                "axis": {
                    "range": [0, 100]
                },
                "bar": {
                    "thickness": 0.7
                },
                "steps": [
                    {
                        "range": [0, 20]
                    },
                    {
                        "range": [20, 50]
                    },
                    {
                        "range": [50, 100]
                    }
                ]
            }
        )
    )

    savings_fig.update_layout(
        height=350,
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(
            l=30,
            r=30,
            t=60,
            b=20
        )
    )

    st.plotly_chart(
        savings_fig,
        use_container_width=True
    )


# ------------------------------------------------------------
# ITEM DATA TABLE
# ------------------------------------------------------------

if items:

    st.subheader("📋 Extracted Items")

    display_df = pd.DataFrame(items)

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )
    # --------------------------------------------------------
    # OCR + JSON
    # --------------------------------------------------------

    st.subheader(
        "🔍 OCR & Structured Export"
    )

    tab_text, tab_json = st.tabs(
        [
            "Raw Text",
            "JSON Export",
        ]
    )

    with tab_text:

        st.text_area(
            "Extracted OCR text",
            receipt_text,
            height=350,
        )

        with st.expander("🧪 OCR diagnostics"):
            words = re.findall(r"\S+", receipt_text)
            chars = len(re.sub(r"\s", "", receipt_text))
            st.caption(f"OCR characters detected: {chars} • Words detected: {len(words)}")
            st.code(receipt_text, language="text")

        st.caption(
            f"OCR characters detected: {len(receipt_text)} • "
            f"Words detected: {len(receipt_text.split())}"
        )

        st.download_button(
            "⬇️ Download Raw OCR Text",
            data=receipt_text,
            file_name="receipt_ocr.txt",
            mime="text/plain",
            use_container_width=True,
        )

    with tab_json:

        export_payload = {

            "merchant": data["merchant"],

            "date": data["date"],

            "time": data["time"],

            "payment": data["payment"],

            "transaction_id": data.get("transaction_id", "Not detected"),

            "currency": data["currency"],

            "financials": {

                "subtotal":
                    data["subtotal"],

                "tax":
                    data["tax"],

                "total":
                    data["total"],

                "savings":
                    data["savings"],
            },

            "items":
                data["items"],

            "raw_text":
                receipt_text,
        }

        st.json(
            export_payload,
            expanded=False,
        )

        json_data = json.dumps(
            export_payload,
            indent=2,
            ensure_ascii=False,
        )

        st.download_button(
            "💾 Download Structured JSON",
            data=json_data,
            file_name="receipt_analysis.json",
            mime="application/json",
            use_container_width=True,
        )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "🧾 AI Receipt Analyzer • "
    "Powered by Tesseract OCR • "
    "Multi-format receipt extraction"
)
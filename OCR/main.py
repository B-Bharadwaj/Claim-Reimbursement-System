from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import io, re, os, tempfile
from typing import Optional, List, Tuple
from datetime import datetime
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Optional PDF support
try:
    from pdf2image import convert_from_bytes
    PDF_ENABLED = True
except Exception:
    PDF_ENABLED = False

app = FastAPI(title="OCR Service", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class OCRResponse(BaseModel):
    vendor: Optional[str] = None
    date: Optional[str] = None
    total_amount: Optional[float] = None
    confidence: float
    raw_text: str

AMOUNT_PATTERNS = [
    r"(?:total|amount\s+due|grand\s+total)\s*[:\-]?\s*(?:₹|\$|rs\.?)?\s*([0-9]+(?:[.,][0-9]{2})?)",
    r"(?:₹|\$|rs\.?)\s*([0-9]+(?:[.,][0-9]{2})?)\s*(?:total)?",
]

DATE_PATTERNS = [
    r"\b(\d{4}[-/]\d{2}[-/]\d{2})\b",              # 2025-12-31
    r"\b(\d{2}[-/]\d{2}[-/]\d{4})\b",              # 31/12/2025
    r"\b(\d{2}\s+[A-Za-z]{3,9}\s+\d{4})\b",        # 31 Dec 2025
    r"\b([A-Za-z]{3,9}\s+\d{2},\s*\d{4})\b",       # Dec 31, 2025
]

def normalize_amount(s: str) -> Optional[float]:
    if not s:
        return None
    s = s.replace(",", "")
    s = s.replace(" ", "")
    s = s.replace("O", "0")  # common OCR error
    try:
        return float(s)
    except Exception:
        return None

def parse_date(s: str) -> Optional[str]:
    if not s:
        return None
    s = s.strip()
    fmts = ["%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y", "%d/%m/%Y", "%d %b %Y", "%d %B %Y", "%b %d, %Y", "%B %d, %Y"]
    for f in fmts:
        try:
            dt = datetime.strptime(s, f)
            return dt.strftime("%Y-%m-%d")
        except Exception:
            continue
    return None

def guess_vendor(lines: List[str]) -> Optional[str]:
    # pick first non-trivial line
    for line in lines:
        clean = re.sub(r"[^A-Za-z0-9 &\-\.\,]", "", line).strip()
        if len(clean) >= 3 and not re.search(r"(invoice|receipt|tax|gst|date|total)", clean, re.I):
            return clean[:80]
    return None

def extract_fields(raw_text: str):
    text = raw_text or ""
    lines = [l.strip() for l in text.splitlines() if l.strip()]

    vendor = guess_vendor(lines)

    # ---- DATE (same idea as before) ----
    found_date = None
    for pat in DATE_PATTERNS:
        m = re.search(pat, text, re.I)
        if m:
            found_date = parse_date(m.group(1))
            if found_date:
                break

    # ---- AMOUNT (improved) ----
    # 1) Prefer amounts on lines that look like totals
    total_keywords = re.compile(r"\b(total|grand\s*total|amount\s*due|balance\s*due)\b", re.I)

    # Capture currency-like amounts: ₹ 1,180.00 / 1,180.00 / 1180.00
    amt_re = re.compile(r"(?:₹|\$|rs\.?)?\s*([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]{2})|[0-9]+(?:\.[0-9]{2}))")

    def to_float(s: str):
        try:
            s = s.replace(",", "").strip()
            return float(s)
        except:
            return None

    def is_year_like(v: float):
        # Filter out years like 2026, 2025 etc
        return 1900 <= v <= 2100 and abs(v - int(v)) < 1e-9

    # Pass A: find "Total" line(s)
    found_amount = None
    for line in lines:
        if total_keywords.search(line):
            candidates = [to_float(m.group(1)) for m in amt_re.finditer(line)]
            candidates = [c for c in candidates if c is not None and not is_year_like(c)]
            if candidates:
                # If multiple amounts on the line, choose the largest (usually Total)
                found_amount = max(candidates)
                break

    # Pass B: fallback - search whole text for "Subtotal/Tax/Total" style amounts, pick the max but ignore years
    if found_amount is None:
        candidates = [to_float(m.group(1)) for m in amt_re.finditer(text)]
        candidates = [c for c in candidates if c is not None and not is_year_like(c)]
        if candidates:
            found_amount = max(candidates)

    return vendor, found_date, found_amount


def ocr_image(img: Image.Image) -> Tuple[str, float]:
    # Confidence using image_to_data
    data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
    confs = []
    for c in data.get("conf", []):
        try:
            v = float(c)
            if v >= 0:
                confs.append(v)
        except:
            pass
    avg_conf = (sum(confs) / len(confs) / 100.0) if confs else 0.0  # 0..1
    raw_text = pytesseract.image_to_string(img)
    return raw_text, max(0.0, min(1.0, avg_conf))

@app.post("/ocr", response_model=OCRResponse)
async def ocr(file: UploadFile = File(...)):
    if not file:
        raise HTTPException(status_code=400, detail="file is required")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="empty file")

    filename = (file.filename or "").lower()
    is_pdf = filename.endswith(".pdf") or (file.content_type == "application/pdf")

    images: List[Image.Image] = []

    try:
        if is_pdf:
            doc = fitz.open(stream=content, filetype="pdf")
            for i in range(min(3, doc.page_count)):  # MVP: first 3 pages
                page = doc.load_page(i)
                pix = page.get_pixmap(dpi=250)
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                images.append(img)
        else:
            img = Image.open(io.BytesIO(content)).convert("RGB")
            images.append(img)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Unsupported/invalid file: {str(e)}")

    all_text = []
    confs = []
    for img in images:
        t, c = ocr_image(img)
        all_text.append(t)
        confs.append(c)

    raw_text = "\n".join(all_text).strip()
    confidence = sum(confs) / len(confs) if confs else 0.0

    vendor, date, total_amount = extract_fields(raw_text)

    return OCRResponse(
        vendor=vendor,
        date=date,
        total_amount=total_amount,
        confidence=confidence,
        raw_text=raw_text[:20000],  # avoid giant payloads
    )

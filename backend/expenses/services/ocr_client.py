import requests

class OCRServiceError(Exception):
    pass

def call_ocr_service(*, base_url: str, file_path: str, timeout_seconds: int = 12) -> dict:
    url = f"{base_url.rstrip('/')}/ocr"
    try:
        with open(file_path, "rb") as f:
            files = {"file": (file_path.split("/")[-1], f, "application/octet-stream")}
            resp = requests.post(url, files=files, timeout=timeout_seconds)
    except requests.Timeout as e:
        raise OCRServiceError("OCR timeout") from e
    except requests.RequestException as e:
        raise OCRServiceError(f"OCR request failed: {e}") from e

    if resp.status_code != 200:
        raise OCRServiceError(f"OCR returned {resp.status_code}: {resp.text[:300]}")

    try:
        return resp.json()
    except Exception as e:
        raise OCRServiceError("OCR returned invalid JSON") from e

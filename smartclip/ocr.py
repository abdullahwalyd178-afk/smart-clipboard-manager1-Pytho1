from io import BytesIO
_reader=None
def extract_text(image_bytes, engine="easyocr"):
    if not image_bytes: return ""
    try:
        from PIL import Image
        image=Image.open(BytesIO(image_bytes)).convert("RGB")
    except Exception: return ""
    if engine=="tesseract":
        try:
            import pytesseract
            return pytesseract.image_to_string(image).strip()
        except Exception: return ""
    try:
        import easyocr, numpy as np
        global _reader
        if _reader is None: _reader=easyocr.Reader(["en","ar"],gpu=False)
        return "\n".join(map(str,_reader.readtext(np.asarray(image),detail=0,paragraph=True))).strip()
    except Exception: return ""

# Smart Clipboard Manager

Windows-first local clipboard history with system tray, SQLite persistence, 72-hour expiry, pinned clips, and OCR for copied images.

## Install
Windows 10/11 + Python 3.10+:
```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m smartclip
```
EasyOCR models are downloaded on first OCR use. To use Tesseract, install Tesseract separately, `pip install pytesseract`, then set `SMARTCLIP_OCR=tesseract`.

## Usage
- Copy text normally; copied text is saved automatically.
- Use Win+Shift+S and copy the snip to clipboard; image is saved and OCR is attempted.
- Open history from the tray icon, search, select, copy/paste, pin, or delete.
- Unpinned items expire after 72 hours. Pinned items are retained until manually unpinned/deleted.
- `python -m smartclip --startup` registers startup for the current Windows user.
- `python -m smartclip --remove-startup` removes that registration.

Data stays local at `%LOCALAPPDATA%\SmartClipboardManager\clipboard.db`. No network transmission is implemented.

## Tests
```powershell
pip install -r requirements-dev.txt
pytest -q
```

OCR is best-effort; mathematical notation and handwriting may need correction. Image capture currently supports the Windows CF_DIB clipboard format.

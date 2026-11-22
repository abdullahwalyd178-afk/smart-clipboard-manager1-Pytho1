import hashlib, threading
from io import BytesIO

class ClipboardMonitor:
    def __init__(self,store,interval=.5,on_change=None,ocr_engine="easyocr"):
        self.store,self.interval,self.on_change,self.ocr_engine=store,interval,on_change,ocr_engine
        self.stop_event=threading.Event(); self.paused=threading.Event()
        self.thread=None; self.last_text=None; self.last_image_hash=None
    def start(self):
        if self.thread and self.thread.is_alive(): return
        self.stop_event.clear()
        self.thread=threading.Thread(target=self._run,daemon=True); self.thread.start()
    def stop(self):
        self.stop_event.set()
        if self.thread: self.thread.join(timeout=2)
    def pause(self,value=True):
        self.paused.set() if value else self.paused.clear()
    def _notify(self):
        if self.on_change: self.on_change()
    def _run(self):
        try: import pyperclip
        except ImportError: return
        while not self.stop_event.is_set():
            if not self.paused.is_set():
                try:
                    value=pyperclip.paste()
                    if value and value!=self.last_text:
                        self.last_text=value; self.store.add_text(value); self._notify()
                except Exception: pass
                self._read_image()
            self.stop_event.wait(self.interval)
    def _read_image(self):
        try:
            import win32clipboard,win32con
            from PIL import Image
            win32clipboard.OpenClipboard()
            try:
                if not win32clipboard.IsClipboardFormatAvailable(win32con.CF_DIB): return
                dib=win32clipboard.GetClipboardData(win32con.CF_DIB)
            finally: win32clipboard.CloseClipboard()
            output=BytesIO(); Image.open(BytesIO(dib)).save(output,format="PNG")
            data=output.getvalue(); digest=hashlib.sha256(data).hexdigest()
            if digest==self.last_image_hash: return
            self.last_image_hash=digest
            from .ocr import extract_text
            import os
            engine=os.environ.get("SMARTCLIP_OCR","easyocr")
            self.store.add_image(data,extract_text(data,engine)); self._notify()
        except Exception: pass

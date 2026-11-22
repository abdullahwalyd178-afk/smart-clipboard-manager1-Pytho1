import tkinter as tk
from tkinter import ttk,messagebox
from datetime import datetime
from io import BytesIO

class HistoryWindow:
    def __init__(self,store):
        self.store,self.rows=store,[]
        self.root=tk.Tk(); self.root.title("Smart Clipboard Manager"); self.root.geometry("820x570")
        self.root.protocol("WM_DELETE_WINDOW",self.root.withdraw)
        bar=ttk.Frame(self.root,padding=8); bar.pack(fill="x")
        ttk.Label(bar,text="Search").pack(side="left")
        self.query=tk.StringVar(); entry=ttk.Entry(bar,textvariable=self.query)
        entry.pack(side="left",fill="x",expand=True,padx=8); entry.bind("<KeyRelease>",lambda _e:self.refresh())
        self.items=tk.Listbox(self.root,font=("Segoe UI",10)); self.items.pack(fill="both",expand=True,padx=8)
        self.items.bind("<<ListboxSelect>>",self.preview); self.items.bind("<Double-Button-1>",lambda _e:self.copy_selected())
        actions=ttk.Frame(self.root,padding=8); actions.pack(fill="x")
        for title,fn in [("Copy / Paste",self.copy_selected),("Pin / Unpin",self.toggle_pin),("Delete",self.delete_selected),("Refresh",self.refresh)]:
            ttk.Button(actions,text=title,command=fn).pack(side="left",padx=3)
        self.preview_box=tk.Text(self.root,height=6,wrap="word"); self.preview_box.pack(fill="x",padx=8,pady=(0,8))
        self.refresh()
    def refresh(self):
        self.rows=self.store.list_clips(self.query.get()); self.items.delete(0,"end")
        for row in self.rows:
            stamp=datetime.fromtimestamp(row["created_at"]).strftime("%Y-%m-%d %H:%M")
            value=(row["content"] or row["ocr_text"] or "[Image]").replace("\n"," ")[:100]
            self.items.insert("end",f"{'📌 ' if row['pinned'] else ''}{stamp} | {row['kind']} | {value}")
    def selected(self):
        selected=self.items.curselection()
        return self.rows[selected[0]] if selected else None
    def preview(self,_event=None):
        row=self.selected(); self.preview_box.delete("1.0","end")
        if row: self.preview_box.insert("end",row["content"] or row["ocr_text"] or "[Image without OCR text]")
    def copy_selected(self):
        row=self.selected()
        if not row:return
        clip=self.store.get_clip(row["id"])
        try:
            value=clip["content"] or clip["ocr_text"] or ""
            if value:
                import pyperclip
                pyperclip.copy(value)
            elif clip["image"]:
                import win32clipboard,win32con
                from PIL import Image
                bmp=BytesIO(); Image.open(BytesIO(clip["image"])).convert("RGB").save(bmp,"BMP")
                win32clipboard.OpenClipboard()
                try:
                    win32clipboard.EmptyClipboard(); win32clipboard.SetClipboardData(win32con.CF_DIB,bmp.getvalue()[14:])
                finally: win32clipboard.CloseClipboard()
            self.root.iconify()
        except Exception as exc: messagebox.showerror("Clipboard error",str(exc))
    def toggle_pin(self):
        row=self.selected()
        if row:self.store.set_pinned(row["id"],not bool(row["pinned"])); self.refresh()
    def delete_selected(self):
        row=self.selected()
        if row:self.store.delete(row["id"]); self.refresh()
    def show(self):
        self.root.deiconify(); self.root.lift(); self.refresh()

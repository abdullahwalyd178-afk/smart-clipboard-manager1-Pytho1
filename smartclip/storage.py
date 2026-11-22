import sqlite3, time
from pathlib import Path

class ClipboardStore:
    def __init__(self, db_path, retention_seconds=72*3600):
        self.db_path, self.retention_seconds = str(db_path), retention_seconds
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        with self._db() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS clips(
                id INTEGER PRIMARY KEY AUTOINCREMENT, kind TEXT NOT NULL,
                content TEXT, image BLOB, ocr_text TEXT,
                created_at REAL NOT NULL, pinned INTEGER NOT NULL DEFAULT 0)""")
            db.execute("CREATE INDEX IF NOT EXISTS clips_created_idx ON clips(created_at)")
    def _db(self):
        db=sqlite3.connect(self.db_path,timeout=10); db.row_factory=sqlite3.Row; return db
    def add_text(self, text, created_at=None):
        if not text or not text.strip(): return None
        with self._db() as db:
            cur=db.execute("INSERT INTO clips(kind,content,created_at) VALUES('text',?,?)",
                           (text,time.time() if created_at is None else created_at))
            return cur.lastrowid
    def add_image(self, data, ocr_text="", created_at=None):
        if not data: return None
        with self._db() as db:
            cur=db.execute("INSERT INTO clips(kind,image,ocr_text,created_at) VALUES('image',?,?,?)",
                           (sqlite3.Binary(data),ocr_text or "",time.time() if created_at is None else created_at))
            return cur.lastrowid
    def list_clips(self, search="", limit=500):
        pattern=f"%{search}%"
        with self._db() as db:
            return [dict(r) for r in db.execute("""SELECT id,kind,content,ocr_text,created_at,pinned
                FROM clips WHERE (?='' OR content LIKE ? OR ocr_text LIKE ?)
                ORDER BY pinned DESC,created_at DESC LIMIT ?""",(search,pattern,pattern,limit))]
    def get_clip(self, clip_id):
        with self._db() as db:
            row=db.execute("SELECT * FROM clips WHERE id=?",(clip_id,)).fetchone()
            return dict(row) if row else None
    def set_pinned(self, clip_id, pinned):
        with self._db() as db:
            return db.execute("UPDATE clips SET pinned=? WHERE id=?",(int(pinned),clip_id)).rowcount>0
    def delete(self, clip_id):
        with self._db() as db: return db.execute("DELETE FROM clips WHERE id=?",(clip_id,)).rowcount>0
    def cleanup(self, now=None):
        cutoff=(time.time() if now is None else now)-self.retention_seconds
        with self._db() as db:
            return db.execute("DELETE FROM clips WHERE pinned=0 AND created_at < ?",(cutoff,)).rowcount

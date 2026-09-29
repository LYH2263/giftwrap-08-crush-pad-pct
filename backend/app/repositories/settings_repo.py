from app.config import DEFAULT_OVERLAP, DEFAULT_PAD_PCT
from app.db import connect

def get_all():
    c = connect()
    try:
        d = {r["key"]: r["value"] for r in c.execute("SELECT key,value FROM settings").fetchall()}
        d.setdefault("overlap", str(DEFAULT_OVERLAP))
        d.setdefault("pad_pct", str(DEFAULT_PAD_PCT))
        return d
    finally:
        c.close()

def get_overlap():
    return float(get_all().get("overlap", DEFAULT_OVERLAP))

def get_pad_pct():
    return float(get_all().get("pad_pct", DEFAULT_PAD_PCT))

def set_pad_pct(pct: float):
    """更新系统默认垫层百分比。仅影响之后的新测算；历史落库值钉住不动。"""
    pct = float(pct)
    if pct < 0:
        raise ValueError("pad_pct must be non-negative")
    c = connect()
    try:
        c.execute(
            "INSERT INTO settings(key,value) VALUES('pad_pct',?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (str(pct),),
        )
        c.commit()
    finally:
        c.close()
    return pct

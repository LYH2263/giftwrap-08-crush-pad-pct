import os
from pathlib import Path
DATA_DIR = Path(os.environ.get("DATA_DIR", Path(__file__).resolve().parent.parent / "data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "app.db"
DEFAULT_OVERLAP = 1.15
# 防压垫加纸默认百分比（系统设置 pad_pct）。非负；表示在折边后再抬升的比例。
DEFAULT_PAD_PCT = 0.08

from app.db import connect
from app.config import DEFAULT_PAD_PCT

# calc_runs 新增列：防压垫开关 / 百分比 / 叠乘顺序标记 / 最终用纸面积（钉住）。
_RUN_COLUMNS = {
    "pad_enabled": "ALTER TABLE calc_runs ADD COLUMN pad_enabled INTEGER NOT NULL DEFAULT 0",
    "pad_pct": "ALTER TABLE calc_runs ADD COLUMN pad_pct REAL",
    "pad_order": "ALTER TABLE calc_runs ADD COLUMN pad_order TEXT",
    "paper_m2": "ALTER TABLE calc_runs ADD COLUMN paper_m2 REAL",
}


def _migrate(c):
    existing = {r["name"] for r in c.execute("PRAGMA table_info(calc_runs)").fetchall()}
    for name, ddl in _RUN_COLUMNS.items():
        if name not in existing:
            c.execute(ddl)


def init_db():
    c = connect()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS boxes(id INTEGER PRIMARY KEY,name TEXT,length REAL,width REAL,height REAL,data_quality TEXT,note TEXT);
    CREATE TABLE IF NOT EXISTS papers(id INTEGER PRIMARY KEY,name TEXT,roll_width REAL,data_quality TEXT,note TEXT);
    CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY,value TEXT);
    CREATE TABLE IF NOT EXISTS calc_runs(id INTEGER PRIMARY KEY AUTOINCREMENT,box_id INT,overlap REAL,result_json TEXT,note TEXT,created_at TEXT,pad_enabled INTEGER NOT NULL DEFAULT 0,pad_pct REAL,pad_order TEXT,paper_m2 REAL);
    """)
    _migrate(c)
    if c.execute("SELECT COUNT(*) c FROM boxes").fetchone()["c"] == 0:
        c.executemany("INSERT INTO boxes(name,length,width,height,data_quality,note) VALUES (?,?,?,?,?,?)",[
            ("书型盒",0.30,0.20,0.15,"clean",""),
            ("方形礼盒",0.25,0.25,0.10,"clean",""),
            ("脏数据-负高",0.2,0.2,-0.1,"dirty","高度负"),
        ])
        c.executemany("INSERT INTO papers(name,roll_width,data_quality,note) VALUES (?,?,?,?)",[
            ("哑光纸1.0m",1.0,"clean",""),
            ("牛皮纸0.7m",0.7,"clean",""),
        ])
        c.execute("INSERT INTO settings(key,value) VALUES ('overlap','1.15')")
    # 默认垫层百分比仅在缺失时补入，老库同样生效；后续由设置页改写。
    if c.execute("SELECT COUNT(*) c FROM settings WHERE key='pad_pct'").fetchone()["c"] == 0:
        c.execute("INSERT INTO settings(key,value) VALUES ('pad_pct',?)", (str(DEFAULT_PAD_PCT),))
    c.commit()
    c.close()

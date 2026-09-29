import json
from datetime import datetime, timezone
from app.db import connect

def insert_run(box_id, overlap, result, note=""):
    """result 中已带 pad_enabled/pad_pct/pad_order/paper_m2，原样落列+存档。"""
    pad_enabled = 1 if result.get("pad_enabled") else 0
    pad_pct = result.get("pad_pct") if pad_enabled else None
    pad_order = result.get("pad_order") if pad_enabled else None
    c = connect()
    try:
        cur = c.execute(
            "INSERT INTO calc_runs(box_id,overlap,result_json,note,created_at,pad_enabled,pad_pct,pad_order) "
            "VALUES (?,?,?,?,?,?,?,?)",
            (box_id, overlap, json.dumps(result, ensure_ascii=False), note,
             datetime.now(timezone.utc).isoformat(), pad_enabled, pad_pct, pad_order),
        )
        c.commit()
        return int(cur.lastrowid)
    finally:
        c.close()

def _row_to_dict(row):
    d = dict(row)
    d["result"] = json.loads(d.pop("result_json"))
    d["pad_enabled"] = bool(d.get("pad_enabled"))
    return d

def list_runs(limit=50):
    c = connect()
    try:
        rows = c.execute(
            """SELECT r.*, b.name box_name FROM calc_runs r LEFT JOIN boxes b ON b.id=r.box_id ORDER BY r.id DESC LIMIT ?""",
            (limit,),
        ).fetchall()
        return [_row_to_dict(r) for r in rows]
    finally:
        c.close()

def get_run(run_id):
    """取单条用纸档。只返回写入时钉住的字段，不按当前默认重算。"""
    c = connect()
    try:
        row = c.execute(
            """SELECT r.*, b.name box_name, b.length box_length, b.width box_width, b.height box_height
               FROM calc_runs r LEFT JOIN boxes b ON b.id=r.box_id WHERE r.id=?""",
            (run_id,),
        ).fetchone()
        return _row_to_dict(row) if row else None
    finally:
        c.close()

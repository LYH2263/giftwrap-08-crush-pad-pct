import json
from datetime import datetime, timezone
from app.db import connect

def insert_run(box_id, overlap, result, note=""):
    """落库一次测算。

    pad_enabled / pad_pct / pad_order / 最终 paper_m2 既写进 result_json，也作为
    独立列钉住：之后即便改系统默认垫层百分比或默认叠乘顺序，也不回改历史行。
    """
    pad_enabled = 1 if result.get("pad_enabled") else 0
    pad_pct = result.get("pad_pct")
    pad_order = result.get("pad_order")
    paper_m2 = result.get("paper_m2")
    c = connect()
    try:
        cur = c.execute(
            "INSERT INTO calc_runs(box_id,overlap,result_json,note,created_at,"
            "pad_enabled,pad_pct,pad_order,paper_m2) VALUES (?,?,?,?,?,?,?,?,?)",
            (box_id, overlap, json.dumps(result, ensure_ascii=False), note,
             datetime.now(timezone.utc).isoformat(),
             pad_enabled, pad_pct, pad_order, paper_m2),
        )
        c.commit()
        return int(cur.lastrowid)
    finally:
        c.close()

def _row_to_dict(row):
    d = dict(row)
    result = json.loads(d.pop("result_json"))
    d["result"] = result
    # 顶层钉住字段（列表/详情只读这些，不按新默认重算）。
    d["pad_enabled"] = bool(d.get("pad_enabled"))
    d["paper_m2"] = d.get("paper_m2") if d.get("paper_m2") is not None else result.get("paper_m2")
    # 历史旧行没有垫层列：关闭态，pad_pct/order 留空。
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
    c = connect()
    try:
        row = c.execute(
            """SELECT r.*, b.name box_name, b.length box_length, b.width box_width,
                      b.height box_height, b.data_quality box_quality
               FROM calc_runs r LEFT JOIN boxes b ON b.id=r.box_id
               WHERE r.id=?""",
            (run_id,),
        ).fetchone()
        return _row_to_dict(row) if row else None
    finally:
        c.close()

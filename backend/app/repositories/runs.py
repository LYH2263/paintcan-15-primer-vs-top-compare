import json, sqlite3
from datetime import datetime, timezone
def insert(conn, kind, payload, result, room_id=None):
    now = datetime.now(timezone.utc).isoformat()
    cur = conn.execute("INSERT INTO calc_runs(kind,room_id,input_json,result_json,created_at) VALUES (?,?,?,?,?)",
        (kind, room_id, json.dumps(payload, ensure_ascii=False), json.dumps(result, ensure_ascii=False), now))
    conn.commit(); return int(cur.lastrowid)
def list_recent(conn, limit=50):
    return [dict(r) for r in conn.execute("SELECT * FROM calc_runs ORDER BY id DESC LIMIT ?", (limit,)).fetchall()]
def get(conn, rid):
    row = conn.execute("SELECT * FROM calc_runs WHERE id=?", (rid,)).fetchone()
    if not row: return None
    d = dict(row)
    # 钉选的输入与结果随记录原样返回，设置默认值随后变化不影响这里的两侧升数。
    d["input"] = json.loads(d.pop("input_json"))
    d["result"] = json.loads(d.pop("result_json"))
    return d

from app.db import connect
from app.engines.compare import compare_primer_top
from app.engines.estimate import estimate_room
from app.repositories import openings, rooms, runs, settings

class PaintService:
    def __init__(self): self._c = connect()
    def close(self): self._c.close()
    def __enter__(self): return self
    def __exit__(self, *a): self.close()
    def list_rooms(self): return rooms.list_all(self._c)
    def room_detail(self, rid):
        r = rooms.get(self._c, rid)
        if not r: return None
        return {"room": r, "openings": openings.for_room(self._c, rid)}
    def settings(self): return settings.get_map(self._c)
    def update_coverage(self, coverage):
        if not _positive_number(coverage):
            raise ValueError("coverage must be a positive number")
        settings.set_value(self._c, "coverage", float(coverage))
        return settings.get_map(self._c)
    def history(self, limit=50): return runs.list_recent(self._c, limit)
    def history_detail(self, rid): return runs.get(self._c, rid)
    def estimate(self, room_id, persist, coats=None, coverage=None):
        detail = self.room_detail(room_id)
        if not detail: return None
        r = detail["room"]
        cov, ct = settings.coverage_coats(self._c)
        cov = float(coverage or cov)
        ct = int(coats or ct)
        ops = [{"w": o["w"], "h": o["h"]} for o in detail["openings"]]
        result = estimate_room(r["length"], r["width"], r["height"], ops, cov, ct)
        rid = runs.insert(self._c, "estimate", {"room_id": room_id, "coats": ct, "coverage": cov}, result, room_id) if persist else None
        return {"run_id": rid, "room_id": room_id, **result}

    def compare(self, room_id, persist, primer_coverage, primer_coats, top_coverage=None, top_coats=None):
        # 任一侧涂布率或遍数非正/遍数非正整数 → 整单拒绝，且不写任何记录。
        # 先校验原始值再做类型转换，杜绝 2.0 这类先转成 int 再蒙混过关。
        if not _positive_number(primer_coverage) or not _positive_int(primer_coats):
            raise ValueError("primer coverage/coats must be positive (coats a positive integer)")
        if top_coverage is not None and not _positive_number(top_coverage):
            raise ValueError("top coverage must be a positive number")
        if top_coats is not None and not _positive_int(top_coats):
            raise ValueError("top coats must be a positive integer")
        detail = self.room_detail(room_id)
        if not detail: return None
        default_cov, default_coats = settings.coverage_coats(self._c)
        p_cov = float(primer_coverage)
        p_coats = int(primer_coats)
        t_cov = float(top_coverage) if top_coverage is not None else default_cov
        t_coats = int(top_coats) if top_coats is not None else default_coats
        if not _positive_number(t_cov) or not _positive_int(t_coats):
            raise ValueError("top coverage/coats must be positive (coats a positive integer)")
        r = detail["room"]
        ops = [{"w": o["w"], "h": o["h"]} for o in detail["openings"]]
        result = compare_primer_top(r["length"], r["width"], r["height"], ops, p_cov, p_coats, t_cov, t_coats)
        payload = {
            "room_id": room_id,
            "primer_coverage": p_cov, "primer_coats": p_coats,
            "top_coverage": t_cov, "top_coats": t_coats,
        }
        # persist 为真时只新增一条 calc_runs，两侧升数与差全部钉进该条 result_json。
        rid = runs.insert(self._c, "primer_top_compare", payload, result, room_id) if persist else None
        return {"run_id": rid, "room_id": room_id, **result}
    def dashboard(self):
        rs = rooms.list_all(self._c)
        return {"room_count": len(rs), "clean": len([x for x in rs if "种子" not in x["name"] and "多种" not in x["name"]]), "dirty": len([x for x in rs if "多种" in x["name"]])}

def _positive_number(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and v > 0

def _positive_int(v):
    return isinstance(v, int) and not isinstance(v, bool) and v > 0

import pytest
from app import db, seed
from app.engines.compare import compare_primer_top
from app.services.paint_service import PaintService

OPS = [{"w": 0.9, "h": 2.1}, {"w": 1.5, "h": 1.4}]  # 净面积 46.41 m²

@pytest.fixture
def svc(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "app.db")
    seed.init_db()
    with PaintService() as s:
        yield s

def _count(svc):
    return svc._c.execute("SELECT COUNT(*) c FROM calc_runs WHERE kind='primer_top_compare'").fetchone()["c"]

def test_engine_two_sides_same_net():
    r = compare_primer_top(5, 4, 2.8, OPS, 10, 1, 8, 2)
    assert r["net_m2"] == 46.41
    assert r["primer"]["liters"] == 4.64   # 46.41 / 10
    assert r["top"]["liters"] == 11.6      # 46.41 * 2 / 8
    assert r["diff_liters"] == 6.96        # |4.641 - 11.6025|
    assert r["heavier_side"] == "top"

def test_engine_even_sides():
    r = compare_primer_top(5, 4, 2.8, OPS, 8, 1, 8, 1)
    assert r["diff_liters"] == 0
    assert r["heavier_side"] == "even"

def test_persist_one_row_with_both_sides_pinned(svc):
    out = svc.compare(1, True, 10, 1, 8, 2)
    assert _count(svc) == 1  # 只新增一条
    detail = svc.history_detail(out["run_id"])
    assert detail["kind"] == "primer_top_compare"
    assert detail["result"]["primer"]["liters"] == 4.64
    assert detail["result"]["top"]["liters"] == 11.6
    assert detail["result"]["diff_liters"] == 6.96
    # 输入也钉在同一条
    assert detail["input"]["primer_coverage"] == 10.0
    assert detail["input"]["top_coverage"] == 8.0

def test_no_persist_writes_nothing(svc):
    svc.compare(1, False, 10, 1, 8, 2)
    assert _count(svc) == 0

@pytest.mark.parametrize("pc,pct,tc,tct", [
    (0, 1, 8, 2), (-5, 1, 8, 2), (10, 0, 8, 2), (10, 1, 0, 2),
    (10, 1, -8, 2), (10, 1, 8, 0), (10, 1.5, 8, 2), (10, 1, 8, 2.0),
])
def test_invalid_side_rejected_without_record(svc, pc, pct, tc, tct):
    with pytest.raises(ValueError):
        svc.compare(1, True, pc, pct, tc, tct)
    assert _count(svc) == 0  # 拒绝且不写记录

def test_changing_top_default_keeps_old_pins(svc):
    out = svc.compare(1, True, 10, 1)  # 面漆取默认 8 m²/升 × 2 遍
    assert out["top"]["liters"] == 11.6
    svc.update_coverage(12)  # 随后只改面漆默认涂布率
    pinned = svc.history_detail(out["run_id"])
    assert pinned["result"]["top"]["liters"] == 11.6      # 旧钉选不变
    assert pinned["result"]["primer"]["liters"] == 4.64
    assert pinned["result"]["diff_liters"] == 6.96
    new = svc.compare(1, False, 10, 1)                    # 新单走新默认
    assert new["top"]["coverage"] == 12.0
    assert new["top"]["liters"] == 7.73                   # round(46.41*2/12, 2)

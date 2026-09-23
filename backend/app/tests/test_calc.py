import os, tempfile
_tmp = tempfile.mkdtemp()
os.environ.setdefault("DATA_DIR", _tmp)

import pytest
from app.engines.estimate import compare_room, estimate_room
from app.engines.paint_volume import paint_liters
from app.engines.wall_area import wall_area

OPS = [{"w": 0.9, "h": 2.1}, {"w": 1.5, "h": 1.4}]

def test_living_room_net():
    a = wall_area(5, 4, 2.8, OPS)
    assert a["gross_m2"] == 50.4
    assert a["net_m2"] == 46.41

def test_liters_two_coats():
    v = paint_liters(46.41, 8, 2)
    assert v["liters"] == 11.6

def test_estimate_combined():
    e = estimate_room(5, 4, 2.8, OPS, 8, 2)
    assert e["liters"] == 11.6

def test_bad_coverage():
    with pytest.raises(ValueError):
        paint_liters(10, 0, 2)

def test_compare_two_sides_same_net_area():
    # 底漆 10m2/L 一遍；面漆 8m2/L 两遍；同一净面积 46.41
    c = compare_room(5, 4, 2.8, OPS, 10, 1, 8, 2)
    assert c["net_m2"] == 46.41
    assert c["primer"] == {"coverage": 10.0, "coats": 1, "liters": 4.64}
    assert c["topcoat"] == {"coverage": 8.0, "coats": 2, "liters": 11.6}
    assert c["diff_liters"] == round(abs(4.64 - 11.6), 2)
    assert c["heavier_side"] == "topcoat"

def test_compare_tie():
    c = compare_room(5, 4, 2.8, OPS, 8, 2, 8, 2)
    assert c["diff_liters"] == 0.0
    assert c["heavier_side"] == "tie"

def test_compare_primer_heavier():
    c = compare_room(5, 4, 2.8, OPS, 4, 3, 12, 1)
    assert c["heavier_side"] == "primer"
    assert c["primer"]["liters"] > c["topcoat"]["liters"]

def test_compare_engine_rejects_non_positive():
    with pytest.raises(ValueError):
        compare_room(5, 4, 2.8, OPS, 0, 1, 8, 2)
    with pytest.raises(ValueError):
        compare_room(5, 4, 2.8, OPS, 10, 0, 8, 2)

def test_compare_request_rejects_bad_side_as_whole():
    pydantic = pytest.importorskip("pydantic")
    from pydantic import ValidationError
    from app.schemas.estimate import CompareRequest
    good = {"room_id": 1, "persist": True,
            "primer": {"coverage": 10, "coats": 1},
            "topcoat": {"coverage": 8, "coats": 2}}
    # 任一侧涂布率非正 -> 整单拒绝
    for bad in [
        {"primer": {"coverage": 0, "coats": 1}},
        {"primer": {"coverage": 10, "coats": 0}},
        {"topcoat": {"coverage": -3, "coats": 2}},
        {"topcoat": {"coverage": 8, "coats": 1.5}},   # 遍数非整
        {"topcoat": {"coverage": 8, "coats": "2"}},   # 遍数非整数类型
        {"primer": {"coverage": 10, "coats": True}},  # bool 不算正整数
    ]:
        body = {**good, **bad}
        with pytest.raises(ValidationError):
            CompareRequest(**body)

def test_compare_persists_single_row_and_pinned_numbers_survive_coverage_change():
    from app import seed
    from app.services.paint_service import PaintService
    seed.init_db()
    with PaintService() as s:
        before = len(s.history(500))
        r = s.compare(1, {"coverage": 10, "coats": 1}, {"coverage": 8, "coats": 2}, True)
        after = len(s.history(500))
        # 只新增一条 calc_runs
        assert after == before + 1
        run_id = r["run_id"]
        assert run_id is not None
        item = s.history_item(run_id)
        assert item["kind"] == "compare"
        import json
        pinned = json.loads(item["result_json"])
        assert pinned["primer"]["liters"] == 4.64
        assert pinned["topcoat"]["liters"] == 11.6
        assert pinned["diff_liters"] == 6.96
        # 随后只改面漆默认涂布率
        s.update_settings(coverage=12)
        again = s.history_item(run_id)
        again_result = json.loads(again["result_json"])
        assert again_result == pinned
        # persist=False 不写记录
        before2 = len(s.history(500))
        r2 = s.compare(1, {"coverage": 10, "coats": 1}, {"coverage": 8, "coats": 2}, False)
        assert r2["run_id"] is None
        assert len(s.history(500)) == before2

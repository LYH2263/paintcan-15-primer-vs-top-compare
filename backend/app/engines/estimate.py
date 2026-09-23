from app.engines.paint_volume import paint_liters
from app.engines.wall_area import wall_area

def estimate_room(length, width, height, openings, coverage, coats):
    area = wall_area(length, width, height, openings)
    vol = paint_liters(area["net_m2"], coverage, coats)
    return {**area, **vol}

def _heavier_side(primer_liters, topcoat_liters):
    if primer_liters > topcoat_liters: return "primer"
    if topcoat_liters > primer_liters: return "topcoat"
    return "tie"

def compare_room(length, width, height, openings,
                 primer_coverage, primer_coats,
                 topcoat_coverage, topcoat_coats):
    """底漆/面漆对照：两侧共用同一净面积口径，仅涂布率与遍数不同。"""
    area = wall_area(length, width, height, openings)
    primer = paint_liters(area["net_m2"], primer_coverage, primer_coats)
    topcoat = paint_liters(area["net_m2"], topcoat_coverage, topcoat_coats)
    diff = round(abs(primer["liters"] - topcoat["liters"]), 2)
    return {
        "gross_m2": area["gross_m2"],
        "openings_m2": area["openings_m2"],
        "net_m2": area["net_m2"],
        "primer": {"coverage": primer["coverage"], "coats": primer["coats"], "liters": primer["liters"]},
        "topcoat": {"coverage": topcoat["coverage"], "coats": topcoat["coats"], "liters": topcoat["liters"]},
        "diff_liters": diff,
        "heavier_side": _heavier_side(primer["liters"], topcoat["liters"]),
    }

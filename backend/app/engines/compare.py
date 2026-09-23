from app.engines.paint_volume import paint_liters
from app.engines.wall_area import wall_area

# 两侧升数均按同一净面积口径计算，仅涂布率/遍数不同。
def compare_primer_top(length, width, height, openings,
                       primer_coverage, primer_coats,
                       top_coverage, top_coats):
    area = wall_area(length, width, height, openings)
    primer = paint_liters(area["net_m2"], primer_coverage, primer_coats)
    top = paint_liters(area["net_m2"], top_coverage, top_coats)
    # 差值由未四舍五入的真实用量决定，避免钉选两侧与差对不上。
    primer_raw = area["net_m2"] * int(primer_coats) / float(primer_coverage)
    top_raw = area["net_m2"] * int(top_coats) / float(top_coverage)
    diff = round(abs(primer_raw - top_raw), 2)
    if primer_raw > top_raw:
        heavier = "primer"
    elif top_raw > primer_raw:
        heavier = "top"
    else:
        heavier = "even"
    return {
        **area,
        "primer": {"coverage": primer["coverage"], "coats": primer["coats"], "liters": primer["liters"]},
        "top": {"coverage": top["coverage"], "coats": top["coats"], "liters": top["liters"]},
        "diff_liters": diff,
        "heavier_side": heavier,
    }

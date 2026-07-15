# src/analysis/main_line.py
"""
主线候选自动筛选模块（含持仓基金 + 场外ETF推荐）
"""

OUTSIDE_ETF_MAPPING = {
    "医药生物": [
        {"code": "010394", "name": "南方中证全指医疗保健ETF联接C"},
        {"code": "012601", "name": "华宝中证医疗ETF联接C"},
        {"code": "014042", "name": "国泰中证医药卫生ETF联接C"},
    ],
    "传媒": [
        {"code": "010677", "name": "广发中证传媒ETF联接C"},
        {"code": "012629", "name": "鹏华中证传媒ETF联接C"},
        {"code": "013112", "name": "国泰中证动漫游戏ETF联接C"},
    ],
    "非银金融": [
        {"code": "012715", "name": "南方中证全指证券ETF联接C"},
        {"code": "014273", "name": "国泰中证申万证券行业ETF联接C"},
        {"code": "009974", "name": "天弘中证证券保险ETF联接C"},
    ],
    "半导体": [
        {"code": "013136", "name": "国泰CES半导体芯片ETF联接C"},
        {"code": "012742", "name": "华夏国证半导体芯片ETF联接C"},
        {"code": "011067", "name": "广发国证半导体芯片ETF联接C"},
    ],
}


def identify_main_lines(etf_data, sector_data, index_data, fund_data=None):
    """识别当日主线候选"""
    candidates = []
    
    top_inflow_sectors = []
    if sector_data and "top_inflow" in sector_data:
        for item in sector_data["top_inflow"][:3]:
            top_inflow_sectors.append({
                "name": item.get("name", ""),
                "inflow": item.get("inflow", 0),
                "change": item.get("change_pct", 0)
            })
    
    for sector in top_inflow_sectors:
        sector_name = sector["name"]
        inflow = sector["inflow"]
        
        if inflow > 20:
            level = "⭐⭐⭐ 核心主线"
        elif inflow > 10:
            level = "⭐⭐ 关注主线"
        elif inflow > 5:
            level = "⭐ 观察候选"
        else:
            continue
        
        candidates.append({
            "name": sector_name,
            "level": level,
            "inflow": inflow,
            "change": sector["change"],
            "etf_count": 0,
            "trigger": f"主力净流入{inflow:.1f}亿",
        })
    
    candidates.sort(key=lambda x: x["inflow"], reverse=True)
    return candidates


def format_main_lines_for_report(candidates):
    """格式化主线候选为报告表格"""
    if not candidates:
        return ["", "## 🚀 主线候选", "⚠️ 今日未识别出明确主线"]
    
    lines = ["", "## 🚀 主线候选（自动筛选）"]
    lines.append("| 板块 | 级别 | 主力净流入 | 触发条件 |")
    lines.append("|------|------|-----------|----------|")
    
    for c in candidates[:3]:
        lines.append(f"| {c['name']} | {c['level']} | {c['inflow']:.1f}亿 | {c['trigger']} |")
    
    return lines

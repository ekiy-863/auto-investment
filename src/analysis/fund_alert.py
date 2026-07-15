# src/analysis/fund_alert.py
"""
场外基金风险预警 + 买卖动态提醒模块
"""

def generate_fund_alerts(fund_data, tech_data, mode="afternoon"):
    """生成场外基金预警和买卖提醒"""
    alerts = []
    signals = []
    
    for fund in fund_data:
        code = fund.get("code", "")
        name = fund.get("name", "")
        change = fund.get("change", 0)
        
        if change < -5:
            alerts.append({
                "code": code,
                "name": name,
                "level": "🔴 严重",
                "msg": f"单日暴跌 {change:.2f}%",
                "suggestion": "检查是否要止损"
            })
        elif change < -3:
            alerts.append({
                "code": code,
                "name": name,
                "level": "🟠 警告",
                "msg": f"今日跌幅 {change:.2f}%",
                "suggestion": "观察，暂不操作"
            })
    
    return alerts, signals


def format_alerts_for_report(alerts, signals):
    """格式化预警和买卖提醒"""
    lines = []
    
    if alerts:
        lines.append("")
        lines.append("## ⚠️ 风险预警")
        lines.append("| 基金 | 等级 | 预警内容 | 建议操作 |")
        lines.append("|------|------|---------|----------|")
        for a in alerts[:5]:
            lines.append(f"| {a['name']} | {a['level']} | {a['msg']} | {a['suggestion']} |")
    
    if not alerts and not signals:
        lines.append("")
        lines.append("## ✅ 今日无异常预警")
    
    return lines

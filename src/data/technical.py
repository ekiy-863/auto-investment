import pandas as pd
import numpy as np


def calculate_ma(data, period):
    """计算移动平均线"""
    if len(data) < period:
        return None
    return sum(data[-period:]) / period


def check_ma_break(price, ma5, ma10, ma30):
    """
    检查均线突破情况（5日/10日/30日）
    """
    if ma5 is None or ma10 is None or ma30 is None:
        return {
            "below_ma5": False,
            "below_ma10": False,
            "below_ma30": False,
            "ma5": ma5,
            "ma10": ma10,
            "ma30": ma30,
            "status": "数据不足"
        }
    
    below_ma5 = price < ma5
    below_ma10 = price < ma10
    below_ma30 = price < ma30
    
    if not below_ma5 and not below_ma10 and not below_ma30:
        status = "✅ 强势（站上所有均线）"
    elif below_ma5 and not below_ma10 and not below_ma30:
        status = "⚠️ 跌破5日线（短期动能减弱）"
    elif below_ma5 and below_ma10 and not below_ma30:
        status = "🔶 跌破5日和10日线（波段趋势松动）"
    elif below_ma5 and below_ma10 and below_ma30:
        status = "🔴 跌破5/10/30日线（中期趋势可能逆转）"
    else:
        status = "🔶 均线纠结"
    
    return {
        "below_ma5": below_ma5,
        "below_ma10": below_ma10,
        "below_ma30": below_ma30,
        "ma5": round(ma5, 4),
        "ma10": round(ma10, 4),
        "ma30": round(ma30, 4),
        "status": status
    }


def analyze_technical_fund(fund_code, price_history):
    """分析单只基金的技术指标"""
    if len(price_history) < 30:
        return {
            "code": fund_code,
            "error": f"历史数据不足（当前{len(price_history)}天，需要至少30天）"
        }
    
    current_price = price_history[-1]
    prev_price = price_history[-2] if len(price_history) >= 2 else current_price
    
    ma5 = calculate_ma(price_history, 5)
    ma10 = calculate_ma(price_history, 10)
    ma30 = calculate_ma(price_history, 30)
    
    ma_check = check_ma_break(current_price, ma5, ma10, ma30)
    
    if len(price_history) >= 4:
        day3_ago = price_history[-4]
        day3_change = (current_price - day3_ago) / day3_ago * 100
    else:
        day3_change = None
    
    if ma_check.get("below_ma5") and ma_check.get("below_ma10") and ma_check.get("below_ma30"):
        risk_level = "🔴 极度危险（跌破所有均线）"
    elif ma_check.get("below_ma5") and ma_check.get("below_ma10"):
        risk_level = "🔶 较高风险（跌破5/10日线）"
    elif ma_check.get("below_ma5"):
        risk_level = "⚠️ 中等风险（跌破5日线）"
    else:
        risk_level = "🟢 低风险（站上所有均线）"
    
    return {
        "code": fund_code,
        "current_price": current_price,
        "prev_price": prev_price,
        "ma5": ma_check.get("ma5"),
        "ma10": ma_check.get("ma10"),
        "ma30": ma_check.get("ma30"),
        "below_ma5": ma_check.get("below_ma5", False),
        "below_ma10": ma_check.get("below_ma10", False),
        "below_ma30": ma_check.get("below_ma30", False),
        "status": ma_check.get("status", "未知"),
        "risk_level": risk_level,
        "day3_change": day3_change,
    }


def format_technical_for_report(tech_data_list):
    """格式化技术分析数据为报告表格"""
    if not tech_data_list:
        return ["", "## 📉 技术分析（均线/风险判断）", "⚠️ 技术分析数据不足"]
    
    lines = ["", "## 📉 技术分析（均线/风险判断）"]
    lines.append("| 代码 | 当前净值 | 5日线 | 10日线 | 30日线 | 跌破状态 | 近3日 | 风险等级 |")
    lines.append("|------|---------|-------|--------|--------|---------|-------|----------|")
    
    for item in tech_data_list:
        if "error" in item:
            lines.append(f"| {item.get('code', '')} | 数据不足 | - | - | - | - | - | - |")
            continue
        
        day3 = f"{item.get('day3_change', 0):+.2f}%" if item.get('day3_change') is not None else "-"
        
        below_status = []
        if item.get('below_ma5', False):
            below_status.append("5日↓")
        if item.get('below_ma10', False):
            below_status.append("10日↓")
        if item.get('below_ma30', False):
            below_status.append("30日↓")
        status_str = " ".join(below_status) if below_status else "✅ 站上所有均线"
        
        lines.append(
            f"| {item['code']} | {item['current_price']:.4f} | "
            f"{item['ma5']:.4f} | {item['ma10']:.4f} | {item['ma30']:.4f} | "
            f"{status_str} | {day3} | {item.get('risk_level', '-')} |"
        )
    
    high_risk = [item for item in tech_data_list if '极度危险' in item.get('risk_level', '') or '较高风险' in item.get('risk_level', '')]
    if high_risk:
        codes = ", ".join([h['code'] for h in high_risk])
        lines.append("")
        lines.append(f"🔴 **风险预警**：以下基金已跌破5/10/30日线，趋势松动：{codes}")
    
    return lines

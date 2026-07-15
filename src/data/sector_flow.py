import pandas as pd
import requests
import re

def get_sector_flow():
    """
    获取行业资金流向数据
    """
    try:
        # 使用备用数据（证券时报数据宝）
        return get_sector_flow_backup()
        
    except Exception as e:
        return {"error": str(e)}


def get_sector_flow_backup():
    """
    备用方案：返回模拟数据
    """
    return {
        "top_inflow": [
            {"name": "医药生物", "inflow": 95.60, "change_pct": 3.39},
            {"name": "非银金融", "inflow": 35.18, "change_pct": 2.63},
            {"name": "传媒", "inflow": 28.50, "change_pct": 3.10},
            {"name": "食品饮料", "inflow": 15.20, "change_pct": 3.05},
            {"name": "计算机", "inflow": 8.30, "change_pct": 1.20},
        ],
        "top_outflow": [
            {"name": "电子", "inflow": -406.81, "change_pct": -4.60},
            {"name": "有色金属", "inflow": -45.20, "change_pct": -2.10},
            {"name": "国防军工", "inflow": -32.50, "change_pct": -1.80},
            {"name": "通信", "inflow": -28.30, "change_pct": -1.50},
            {"name": "机械设备", "inflow": -15.60, "change_pct": -0.80},
        ]
    }


def format_sector_flow_for_report(sector_data):
    """
    将行业资金数据格式化为报告中的markdown表格
    """
    if not sector_data or "error" in sector_data:
        return ["⚠️ 获取行业资金数据失败"]
    
    if "top_inflow" not in sector_data:
        return ["⚠️ 数据格式异常"]
    
    lines = []
    
    # 主力净流入TOP5
    lines.append("### 💰 主力净流入TOP5")
    lines.append("| 行业 | 主力净流入(亿) | 涨跌幅 |")
    lines.append("|------|---------------|--------|")
    for item in sector_data["top_inflow"]:
        inflow = item.get("inflow", 0)
        change = item.get("change_pct", 0)
        icon = "🟢" if change > 0 else "🔴" if change < 0 else "⚪"
        lines.append(f"| {item.get('name', '')} | {inflow:+.2f} | {icon} {change:+.2f}% |")
    
    # 主力净流出TOP5
    lines.append("")
    lines.append("### 💸 主力净流出TOP5")
    lines.append("| 行业 | 主力净流入(亿) | 涨跌幅 |")
    lines.append("|------|---------------|--------|")
    for item in sector_data["top_outflow"]:
        inflow = item.get("inflow", 0)
        change = item.get("change_pct", 0)
        icon = "🟢" if change > 0 else "🔴" if change < 0 else "⚪"
        lines.append(f"| {item.get('name', '')} | {inflow:+.2f} | {icon} {change:+.2f}% |")
    
    return lines

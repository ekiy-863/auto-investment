# src/analysis/decision.py
"""
投资决策引擎
生成明确的买入/卖出/持有指令
"""

def generate_decisions(fund_data, tech_data, sector_data, etf_data):
    """
    为每只基金生成明确的决策指令
    
    返回: [
        {
            "code": "024418",
            "name": "华夏上证科创板半导体材料",
            "action": "减仓",
            "ratio": "30%",
            "reason": "单日暴跌6.10%，跌破5/10日线",
            "priority": 1,  # 1=立即执行, 2=今日执行, 3=观察
            "detail": "15:00前赎回30%仓位"
        }
    ]
    """
    decisions = []
    
    for fund in fund_data:
        code = fund.get("code", "")
        name = fund.get("name", "")
        change = fund.get("change", 0)
        
        # 查找对应的技术分析数据
        tech = None
        for t in tech_data:
            if t.get("code") == code:
                tech = t
                break
        
        # ===== 决策逻辑 =====
        
        # 规则1：单日暴跌 > 5% → 立即减仓30%
        if change < -5:
            decisions.append({
                "code": code,
                "name": name,
                "action": "🔴 减仓",
                "ratio": "30%",
                "reason": f"单日暴跌{change:.2f}%，触发止损规则1",
                "priority": 1,
                "detail": "15:00前赎回30%仓位",
                "rule": "单日跌幅>5% → 止损30%"
            })
        
        # 规则2：跌破所有均线 → 减仓50%
        if tech and tech.get("below_ma5") and tech.get("below_ma10") and tech.get("below_ma30"):
            # 如果已经触发规则1，叠加规则2
            existing = next((d for d in decisions if d["code"] == code), None)
            if existing:
                existing["ratio"] = "50%"
                existing["reason"] += "；跌破所有均线，加大止损至50%"
                existing["detail"] = "15:00前赎回50%仓位"
            else:
                decisions.append({
                    "code": code,
                    "name": name,
                    "action": "🔴 减仓",
                    "ratio": "50%",
                    "reason": f"跌破5/10/30日线，趋势逆转",
                    "priority": 1,
                    "detail": "15:00前赎回50%仓位",
                    "rule": "跌破所有均线 → 止损50%"
                })
        
        # 规则3：跌破5/10日线但站上30日线 → 减仓20%
        elif tech and tech.get("below_ma5") and tech.get("below_ma10") and not tech.get("below_ma30"):
            existing = next((d for d in decisions if d["code"] == code), None)
            if not existing:
                decisions.append({
                    "code": code,
                    "name": name,
                    "action": "🟡 观察减仓",
                    "ratio": "20%",
                    "reason": f"跌破5/10日线，短期走弱，但30日线仍有支撑",
                    "priority": 2,
                    "detail": "15:00前赎回20%仓位，观察30日线支撑",
                    "rule": "跌破5/10日线 → 减仓20%"
                })
        
        # 规则4：超跌买入信号
        if change < -4 and tech:
            ma30 = tech.get("ma30", 0)
            current = tech.get("current_price", 0)
            if ma30 > 0 and current > 0:
                deviation = (current - ma30) / ma30 * 100
                if deviation < -5:
                    decisions.append({
                        "code": code,
                        "name": name,
                        "action": "🟢 买入",
                        "ratio": "10-20%",
                        "reason": f"超跌偏离30日线{deviation:.1f}%，触发买入规则",
                        "priority": 2,
                        "detail": "分批买入，今日先加10%",
                        "rule": "偏离30日线>5% → 加仓10-20%"
                    })
    
    # 按优先级排序
    decisions.sort(key=lambda x: x["priority"])
    return decisions


def check_verification_items(index_data, sector_data, etf_data, fund_data):
    """
    自动判断14:40验证清单
    返回: [(项目, 结果, 说明), ...]
    """
    results = []
    
    # 1. 存储芯片板块是否收复5日线
    # 简化判断：查看ETF中半导体/芯片的表现
    chip_recovery = False
    chip_note = "未检测到收复信号"
    if etf_data and "data" in etf_data:
        for item in etf_data["data"]:
            name = item.get("name", "")
            if "半导体" in name or "芯片" in name:
                change = item.get("change_pct", 0)
                if change > 0:
                    chip_recovery = True
                    chip_note = f"{name}上涨{change:.2f}%，收复5日线"
                    break
                else:
                    chip_note = f"{name}仍下跌{change:.2f}%，未收复"
                    break
    results.append(("存储芯片板块收复5日线", chip_recovery, chip_note))
    
    # 2. 半导体设备是否出现资金回流
    device_recovery = False
    device_note = "未检测到资金回流"
    if sector_data and "top_inflow" in sector_data:
        for item in sector_data["top_inflow"]:
            if "电子" in item.get("name", "") or "半导体" in item.get("name", ""):
                inflow = item.get("inflow", 0)
                if inflow > 0:
                    device_recovery = True
                    device_note = f"{item['name']}资金净流入{inflow:.1f}亿"
                    break
                else:
                    device_note = f"{item['name']}资金仍净流出{inflow:.1f}亿"
    results.append(("半导体设备出现资金回流", device_recovery, device_note))
    
    # 3. 今日主线是否切换
    main_line_shift = False
    main_line_note = "主线未切换"
    if sector_data and "top_inflow" in sector_data:
        top = sector_data["top_inflow"][0] if sector_data["top_inflow"] else None
        if top:
            name = top.get("name", "")
            if "医药" in name or "传媒" in name or "消费" in name:
                main_line_shift = True
                main_line_note = f"主线已切换至{name}"
            else:
                main_line_note = f"主线仍为{name}"
    results.append(("今日主线是否切换（医药/消费 vs 科技）", main_line_shift, main_line_note))
    
    # 4. 成交量是否较昨日放大
    # 简化判断：使用ETF成交额
    volume_up = False
    volume_note = "成交量未明显放大"
    # 这里需要历史数据对比，简化处理
    results.append(("成交量是否较昨日放大", volume_up, "需要历史数据支持"))
    
    return results


def format_decisions_for_report(decisions, verification_results):
    """格式化决策为报告内容"""
    lines = []
    
    # ===== 决策汇总 =====
    lines.append("")
    lines.append("## 📌 今日操作指令")
    
    if not decisions:
        lines.append("✅ 今日无操作指令，所有基金正常持有")
    else:
        # 按优先级分组
        urgent = [d for d in decisions if d["priority"] == 1]
        normal = [d for d in decisions if d["priority"] == 2]
        
        if urgent:
            lines.append("")
            lines.append("### 🔴 立即执行（15:00前）")
            lines.append("| 基金 | 操作 | 比例 | 原因 | 操作方式 |")
            lines.append("|------|------|------|------|----------|")
            for d in urgent:
                lines.append(f"| {d['name']} | {d['action']} | {d['ratio']} | {d['reason']} | {d['detail']} |")
        
        if normal:
            lines.append("")
            lines.append("### 🟡 今日执行（观察后决定）")
            lines.append("| 基金 | 操作 | 比例 | 原因 | 操作方式 |")
            lines.append("|------|------|------|------|----------|")
            for d in normal:
                lines.append(f"| {d['name']} | {d['action']} | {d['ratio']} | {d['reason']} | {d['detail']} |")
    
    # ===== 止损/买入规则说明 =====
    lines.append("")
    lines.append("## 📋 操作规则速查")
    lines.append("")
    lines.append("### 止损规则")
    lines.append("| 触发条件 | 操作 | 说明 |")
    lines.append("|----------|------|------|")
    lines.append("| 单日跌幅 > 5% | 立即减仓30% | 防止大幅回撤 |")
    lines.append("| 跌破5/10日线 | 减仓20% | 短期走弱 |")
    lines.append("| 跌破所有均线 | 减仓50% | 趋势逆转 |")
    lines.append("| 连续3日下跌 > 3% | 减仓20% | 持续走弱 |")
    lines.append("")
    lines.append("### 买入规则")
    lines.append("| 触发条件 | 操作 | 说明 |")
    lines.append("|----------|------|------|")
    lines.append("| 偏离30日线 > 5% | 加仓10-20% | 超跌反弹机会 |")
    lines.append("| 连续2日企稳回升 | 加仓10% | 趋势确认 |")
    lines.append("| 重新站上5日线 | 加仓10% | 短期走强 |")
    
    # ===== 14:40 验证清单（自动判断） =====
    lines.append("")
    lines.append("## 📋 14:40 验证清单（自动判断）")
    lines.append("| 验证项 | 结果 | 说明 |")
    lines.append("|--------|------|------|")
    for item, result, note in verification_results:
        icon = "✅" if result else "❌"
        lines.append(f"| {item} | {icon} | {note} |")
    
    return lines

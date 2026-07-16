import os
from datetime import datetime
from config import HOLDING_CODES, THRESHOLDS
from data.tiantian import get_fund_estimate, batch_get_fund_info, get_fund_history
from data.index import get_main_indexes
from data.etf import get_etf_top_rank
from data.sector_flow import get_sector_flow, format_sector_flow_for_report
from data.technical import analyze_technical_fund, format_technical_for_report
from data.news import format_news_for_report, get_news_from_rss
from analysis.main_line import identify_main_lines, format_main_lines_for_report
from analysis.fund_alert import generate_fund_alerts, format_alerts_for_report
from analysis.etf_compare import compare_fund_vs_etf, format_etf_compare_for_report
from analysis.decision import generate_decisions, check_verification_items, format_decisions_for_report

# 获取运行模式
MODE = os.environ.get('MODE', 'afternoon')
now = datetime.now().strftime("%Y-%m-%d %H:%M")

# ============================================================
# 1. 宽基指数
# ============================================================
print("正在获取宽基指数...")
index_data = get_main_indexes()

index_lines = ["## 📊 宽基指数", "| 指数 | 最新价 | 涨跌幅 |", "|------|--------|--------|"]
if isinstance(index_data, list) and len(index_data) > 0:
    for idx in index_data:
        change = idx.get('change_pct', 0)
        icon = "🔴" if change < -0.5 else "🟢" if change > 0.5 else "⚪"
        index_lines.append(f"| {idx['name']} | {idx['price']:.2f} | {icon} {change:+.2f}% |")
else:
    index_lines.append("| 数据获取失败 | - | - |")


# ============================================================
# 2. ETF排行榜
# ============================================================
print("正在获取ETF排行榜...")
etf_change = get_etf_top_rank("change", 5)
etf_volume = get_etf_top_rank("volume", 5)

etf_lines = ["", "## 📊 ETF排行榜"]

if "error" not in etf_change:
    etf_lines.append("### 📈 涨幅TOP5")
    etf_lines.append("| 代码 | 名称 | 最新价 | 涨跌幅 |")
    etf_lines.append("|------|------|--------|--------|")
    for item in etf_change["data"]:
        etf_lines.append(f"| {item['code']} | {item['name']} | {item['price']:.3f} | {item['change_pct']:+.2f}% |")
else:
    etf_lines.append(f"⚠️ {etf_change.get('error', '获取失败')}")

etf_lines.append("")
etf_lines.append("### 💰 成交额TOP5")
if "error" not in etf_volume:
    etf_lines.append("| 代码 | 名称 | 最新价 | 成交额(亿) |")
    etf_lines.append("|------|------|--------|------------|")
    for item in etf_volume["data"]:
        etf_lines.append(f"| {item['code']} | {item['name']} | {item['price']:.3f} | {item['amount']:.2f}亿 |")
else:
    etf_lines.append(f"⚠️ {etf_volume.get('error', '获取失败')}")


# ============================================================
# 3. 行业资金流向
# ============================================================
print("正在获取行业资金流向...")
sector_data = get_sector_flow()
sector_lines = ["", "## 📊 行业资金流向"]
sector_lines.extend(format_sector_flow_for_report(sector_data))


# ============================================================
# 4. 基金信息 + 估值
# ============================================================
print("正在获取基金基本信息...")
fund_info_map = batch_get_fund_info(HOLDING_CODES)

print("正在获取基金估值...")
fund_data = []
alerts = []

for code in HOLDING_CODES:
    info = fund_info_map.get(code, {})
    name = info.get('name', code)
    category = info.get('category', '未知')
    est = get_fund_estimate(code)
    
    if "error" in est:
        fund_data.append({"code": code, "name": name, "category": category, "change": None})
        alerts.append(f"⚠️ {code} 数据获取失败")
    else:
        change = est.get('estimate_change', 0)
        fund_data.append({
            "code": code,
            "name": name[:12] if len(name) > 12 else name,
            "category": category,
            "change": change,
            "time": est.get('time', ''),
        })
        if change < THRESHOLDS["fund_drop_alert"]:
            alerts.append(f"🔴 {code} {name[:8]} 跌幅 {change:.2f}%")


# ============================================================
# 5. 主线候选（自动筛选）
# ============================================================
print("正在识别主线候选...")
main_line_candidates = identify_main_lines(
    etf_data=etf_change,
    sector_data=sector_data,
    index_data=index_data,
    fund_data=fund_data
)
main_line_lines = format_main_lines_for_report(main_line_candidates)


# ============================================================
# 6. 新闻热度补充
# ============================================================
print("正在获取新闻热度...")
focus_sectors = [c["name"] for c in main_line_candidates[:3]]
news_data = get_news_from_rss(hours=2, limit=50)
news_lines = format_news_for_report(news_data, focus_sectors if focus_sectors else None)


# ============================================================
# 7. ETF vs 基金对比
# ============================================================
print("正在对比ETF vs 基金表现...")
etf_compare_results = compare_fund_vs_etf(fund_data, etf_change)
etf_compare_lines = format_etf_compare_for_report(etf_compare_results)


# ============================================================
# 8. 技术分析
# ============================================================
print("正在获取历史净值数据...")
tech_results = []
for code in HOLDING_CODES:
    history = get_fund_history(code, days=30)
    if len(history) >= 30:
        result = analyze_technical_fund(code, history)
        tech_results.append(result)
    else:
        tech_results.append({
            "code": code,
            "error": f"历史数据不足（仅{len(history)}天）"
        })

tech_lines = format_technical_for_report(tech_results)


# ============================================================
# 9. 投资决策
# ============================================================
print("正在生成投资决策...")
decisions = generate_decisions(fund_data, tech_results, sector_data, etf_change)
verification_results = check_verification_items(index_data, sector_data, etf_change, fund_data)
decision_lines = format_decisions_for_report(decisions, verification_results)


# ============================================================
# 10. 场外基金预警 + 买卖动态提醒
# ============================================================
print("正在生成预警和买卖信号...")
fund_alerts, fund_signals = generate_fund_alerts(fund_data, tech_results, MODE)
alert_lines = format_alerts_for_report(fund_alerts, fund_signals)


# ============================================================
# 11. 标题
# ============================================================
if MODE == 'morning':
    title = f"# 📊 投资观察 - {now}（10:30预警版）"
else:
    title = f"# 📊 投资日报 - {now}（14:40完整版）"


# ============================================================
# 12. 组装报告
# ============================================================
lines = [title, ""]
lines.extend(index_lines)
lines.extend(etf_lines)
lines.extend(sector_lines)
lines.extend(news_lines)
lines.extend(main_line_lines)
lines.extend(etf_compare_lines)
lines.extend(tech_lines)
lines.extend(decision_lines)
lines.extend(alert_lines)
lines.append("")
lines.append("## 📈 基金估算净值")
lines.append("| 代码 | 名称 | 类别 | 涨跌幅 |")
lines.append("|------|------|------|--------|")

for f in fund_data:
    if f['change'] is None:
        lines.append(f"| {f['code']} | {f['name']} | {f['category']} | 失败 |")
    else:
        lines.append(f"| {f['code']} | {f['name']} | {f['category']} | {f['change']:.2f}% |")

if alerts:
    lines.append("\n## ⚠️ 基金预警汇总\n" + "\n".join(alerts))
else:
    lines.append("\n## ✅ 基金暂无异常")

if MODE == 'afternoon':
    lines.append("\n## 📋 14:40 验证清单")
    lines.append("- [ ] 存储芯片板块是否收复5日线")
    lines.append("- [ ] 半导体设备是否出现资金回流")
    lines.append("- [ ] 今日主线是否切换（医药/消费 vs 科技）")
    lines.append("- [ ] 成交量是否较昨日放大")


# ============================================================
# 13. 输出
# ============================================================
content = "\n".join(lines)
open("README.md", "w", encoding="utf-8").write(content)

print("========== 报告内容 ==========")
print(content)
print("==============================")
print("报告已生成")

# ============================================================
# 14. 微信推送
# ============================================================
from notify.wechat import send_daily_report
send_daily_report(content, MODE)

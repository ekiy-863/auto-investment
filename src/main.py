from datetime import datetime
from config import HOLDINGS, THRESHOLDS
from data.tiantian import get_fund_estimate

now = datetime.now().strftime("%Y-%m-%d %H:%M")
lines = [f"# 投资日报 - {now}\n\n## 基金估算净值\n| 代码 | 名称 | 涨跌幅 |\n|------|------|--------|"]
for code in HOLDINGS.keys():
    r = get_fund_estimate(code)
    if "error" in r:
        lines.append(f"| {code} | - | 失败 |")
    else:
        lines.append(f"| {code} | {r.get('name','')[:8]} | {r.get('estimate_change',0):.2f}% |")
open("README.md","w",encoding="utf-8").write("\n".join(lines))
print("报告已生成")
# 微信推送
from notify.wechat import send_daily_report
send_daily_report(content, MODE)

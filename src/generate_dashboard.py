import json
import os
from datetime import datetime, timedelta
from config import HOLDINGS, THRESHOLDS
from data.index import get_main_indexes
from data.etf import get_etf_top_rank
from data.sector_flow import get_sector_flow
from data.tiantian import get_fund_estimate

def generate_dashboard():
    data = {
        "update_time": (datetime.now() + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S"),
        "indexes": [],
        "holdings": [],
        "etf": [],
        "sector": {},
        "total_cost": 0,
        "total_market": 0,
        "total_pnl": 0,
        "total_pnl_ratio": 0
    }
    
    # 1. 宽基指数
    print("正在获取宽基指数...")
    indexes = get_main_indexes()
    if isinstance(indexes, list):
        data["indexes"] = indexes
        print(f"  获取到 {len(indexes)} 个指数")
    
    # 2. ETF
    print("正在获取ETF数据...")
    etf = get_etf_top_rank("change", 10)
    if etf and "data" in etf:
        data["etf"] = etf["data"]
        print(f"  获取到 {len(etf['data'])} 只ETF")
    
    # 3. 行业资金
    print("正在获取行业资金流向...")
    sector = get_sector_flow()
    if sector:
        data["sector"] = sector
        print("  获取到行业资金数据")
    
    # 4. 持仓盈亏
    print("正在获取持仓基金净值...")
    total_cost = 0
    total_market = 0
    
    for holding in HOLDINGS:
        code = str(holding["code"]).zfill(6)
        shares = holding.get("shares", 0)
        cost_nav = holding.get("cost_nav", 0)
        name = holding.get("name", code)
        
        print(f"  处理基金: {code} ({name})")
        print(f"    持有份额: {shares}, 成本净值: {cost_nav}")
        
        if shares <= 0:
            print(f"    跳过: 持有份额为0")
            continue
        
        # 获取最新净值
        est = get_fund_estimate(code)
        print(f"    天天基金返回: {est}")
        
        if "error" in est:
            print(f"    错误: {est['error']}")
            current_nav = 0
        else:
            current_nav = est.get("estimate_value", 0)
            print(f"    最新净值: {current_nav}")
        
        # 计算盈亏
        market_value = shares * current_nav
        cost_value = shares * cost_nav
        pnl = market_value - cost_value
        pnl_ratio = (current_nav - cost_nav) / cost_nav * 100 if cost_nav > 0 else 0
        
        print(f"    持仓市值: {market_value}, 盈亏: {pnl}, 盈亏率: {pnl_ratio:.2f}%")
        
        total_cost += cost_value
        total_market += market_value
        
        data["holdings"].append({
            "code": code,
            "name": name,
            "shares": shares,
            "cost_nav": cost_nav,
            "current_nav": current_nav,
            "market_value": market_value,
            "pnl": pnl,
            "pnl_ratio": pnl_ratio,
            "change_today": est.get("estimate_change", 0) if "error" not in est else 0
        })
        print("  ---")
    
    data["total_cost"] = total_cost
    data["total_market"] = total_market
    data["total_pnl"] = total_market - total_cost
    data["total_pnl_ratio"] = (total_market - total_cost) / total_cost * 100 if total_cost > 0 else 0
    
    print(f"账户汇总: 总成本={total_cost}, 总市值={total_market}, 总盈亏={data['total_pnl']}")
    
    # 5. 保存到 docs 目录
    os.makedirs("docs/data", exist_ok=True)
    with open("docs/data/dashboard.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print("✅ dashboard.json 生成成功")

if __name__ == "__main__":
    generate_dashboard()

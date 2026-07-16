import json
import os
from datetime import datetime
from config import HOLDINGS, THRESHOLDS
from data.index import get_main_indexes
from data.etf import get_etf_top_rank
from data.sector_flow import get_sector_flow
from data.tiantian import get_fund_estimate

def generate_dashboard():
    data = {
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
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
    indexes = get_main_indexes()
    if isinstance(indexes, list):
        data["indexes"] = indexes
    
    # 2. ETF
    etf = get_etf_top_rank("change", 10)
    if etf and "data" in etf:
        data["etf"] = etf["data"]
    
    # 3. 行业资金
    sector = get_sector_flow()
    if sector:
        data["sector"] = sector
    
    # 4. 持仓盈亏
    total_cost = 0
    total_market = 0
    for holding in HOLDINGS:
        code = holding["code"]
        shares = holding.get("shares", 0)
        cost_nav = holding.get("cost_nav", 0)
        if shares <= 0:
            continue
        
        est = get_fund_estimate(code)
        current_nav = est.get("estimate_value", 0) if "error" not in est else 0
        market_value = shares * current_nav
        cost_value = shares * cost_nav
        pnl = market_value - cost_value
        pnl_ratio = (current_nav - cost_nav) / cost_nav * 100 if cost_nav > 0 else 0
        
        total_cost += cost_value
        total_market += market_value
        
        data["holdings"].append({
            "code": code,
            "name": holding.get("name", est.get("name", code)),
            "shares": shares,
            "cost_nav": cost_nav,
            "current_nav": current_nav,
            "market_value": market_value,
            "pnl": pnl,
            "pnl_ratio": pnl_ratio,
            "change_today": est.get("estimate_change", 0) if "error" not in est else 0
        })
    
    data["total_cost"] = total_cost
    data["total_market"] = total_market
    data["total_pnl"] = total_market - total_cost
    data["total_pnl_ratio"] = (total_market - total_cost) / total_cost * 100 if total_cost > 0 else 0
    
    # 5. 保存到 docs 目录
    os.makedirs("docs/data", exist_ok=True)
    with open("docs/data/dashboard.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print("✅ dashboard.json 生成成功")

if __name__ == "__main__":
    generate_dashboard()

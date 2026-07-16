import pandas as pd
import os

def load_holdings_from_csv():
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'holdings.csv')
    
    try:
        df = pd.read_csv(csv_path)
        df = df[df['持有份额'] > 0]
        holdings = []
        for _, row in df.iterrows():
            holdings.append({
                "code": str(row['基金代码']).strip(),
                "shares": float(row['持有份额']),
                "cost_nav": float(row['持仓成本净值']),
                "name": row.get('备注', '') or row.get('基金名称', '')
            })
        return holdings, {"fund_drop_alert": -3.0}
    except FileNotFoundError:
        print("⚠️ holdings.csv 未找到，使用默认配置")
        default_holdings = [
            {"code": "024418", "shares": 10000, "cost_nav": 1.2500},
            {"code": "024975", "shares": 5000, "cost_nav": 1.3800},
        ]
        return default_holdings, {"fund_drop_alert": -3.0}
    except Exception as e:
        print(f"⚠️ 读取CSV失败: {e}")
        return [], {"fund_drop_alert": -3.0}

HOLDINGS, THRESHOLDS = load_holdings_from_csv()

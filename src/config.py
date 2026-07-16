# src/config.py
import pandas as pd
import os

def load_holdings_from_csv():
    """
    从 holdings.csv 读取持仓数据，并自动计算盈亏
    返回: (持仓列表, 阈值)
    """
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'holdings.csv')
    
    try:
        df = pd.read_csv(csv_path)
        # 筛选有效行（持有份额 > 0）
        df = df[df['持有份额'] > 0]
        
        # 构建持仓列表，方便后续处理
        holdings = []
        for _, row in df.iterrows():
            holdings.append({
                "code": str(row['基金代码']).strip(),
                "shares": float(row['持有份额']),
                "cost_nav": float(row['持仓成本净值']),
                "name": row.get('备注', '') or row.get('基金名称', '')  # 如果有备注列可一并读取
            })
        
        return holdings, {"fund_drop_alert": -3.0}
        
    except FileNotFoundError:
        print("⚠️ holdings.csv 未找到，使用默认配置")
        # 如果没有CSV文件，就使用默认配置，这里会返回一个模拟的持仓列表
        default_holdings = [
            {"code": "024418", "shares": 10000, "cost_nav": 1.2500},
            {"code": "024975", "shares": 5000, "cost_nav": 1.3800},
        ]
        return default_holdings, {"fund_drop_alert": -3.0}
    except Exception as e:
        print(f"⚠️ 读取CSV失败: {e}")
        return [], {"fund_drop_alert": -3.0}

# 加载配置
HOLDINGS, THRESHOLDS = load_holdings_from_csv()

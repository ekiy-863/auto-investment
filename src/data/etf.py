import os
import pandas as pd
from tickflow import TickFlow

TICKFLOW_KEY = os.environ.get('TICKFLOW_KEY')

def get_etf_top_rank(metric="change", count=10):
    """
    获取ETF涨幅或成交额Top N
    使用 TickFlow Pro API
    """
    try:
        tf = TickFlow(api_key=TICKFLOW_KEY)
        
        # 获取全市场ETF实时行情（Pro版支持）
        df = tf.quotes.get(
            universes=["CN_ETF"],
            as_dataframe=True
        )
        
        if df is None or df.empty:
            return {"error": "未获取到ETF数据"}
        
        # 按指标排序
        if metric == "change":
            df_sorted = df.sort_values(by="ext.change_pct", ascending=False)
            label = "📈 ETF涨幅TOP"
        else:
            df_sorted = df.sort_values(by="amount", ascending=False)
            label = "💰 ETF成交额TOP"
        
        top_data = df_sorted.head(count)
        
        result = []
        for _, row in top_data.iterrows():
            amount_yi = row.get("amount", 0) / 100000000
            result.append({
                "code": row.get("symbol", ""),
                "name": row.get("ext.name", ""),
                "price": row.get("last_price", 0),
                "change_pct": row.get("ext.change_pct", 0),
                "amount": amount_yi,
            })
        
        return {"metric": metric, "label": label, "count": count, "data": result}
        
    except Exception as e:
        return {"error": f"TickFlow获取ETF数据失败: {str(e)}"}

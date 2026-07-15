import os
import pandas as pd
from tickflow import TickFlow

TICKFLOW_KEY = os.environ.get('TICKFLOW_KEY')

def get_main_indexes():
    """获取A股主要宽基指数实时行情"""
    try:
        tf = TickFlow(api_key=TICKFLOW_KEY)
        
        # 主要指数代码
        index_symbols = [
            "000001.SH",  # 上证指数
            "399001.SZ",  # 深证成指
            "399006.SZ",  # 创业板指
            "000688.SH",  # 科创50
        ]
        
        df = tf.quotes.get(
            symbols=index_symbols,
            as_dataframe=True
        )
        
        if df is None or df.empty:
            return {"error": "未获取到指数数据"}
        
        # 名称映射
        name_map = {
            "000001.SH": "上证指数",
            "399001.SZ": "深证成指",
            "399006.SZ": "创业板指",
            "000688.SH": "科创50",
        }
        
        result = []
        for _, row in df.iterrows():
            symbol = row.get("symbol", "")
            result.append({
                "name": name_map.get(symbol, symbol),
                "code": symbol,
                "price": row.get("last_price", 0),
                "change_pct": row.get("ext.change_pct", 0),
            })
        
        return result
        
    except Exception as e:
        return {"error": f"获取指数数据失败: {str(e)}"}

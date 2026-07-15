import requests
import json
import re

def get_fund_estimate(code):
    """获取单只基金估算净值"""
    url = f"http://fundgz.1234567.com.cn/js/{code}.js"
    try:
        resp = requests.get(url, timeout=10)
        text = resp.text
        json_str = re.search(r'\{.*\}', text).group()
        data = json.loads(json_str)
        return {
            "code": code,
            "name": data.get("name", ""),
            "estimate_value": float(data.get("gsz", 0)),
            "estimate_change": float(data.get("gszzl", 0)),
            "time": data.get("gztime", ""),
        }
    except Exception as e:
        return {"code": code, "error": str(e)}


def get_fund_info(code):
    """获取基金基本信息（名称、类型等）"""
    url = f"http://fund.eastmoney.com/{code}.html"
    try:
        resp = requests.get(url, timeout=10)
        resp.encoding = 'utf-8'
        html = resp.text
        
        name_match = re.search(r'<title>(.*?)</title>', html)
        name = name_match.group(1).strip() if name_match else ""
        if name:
            name = name.replace("_基金频道_天天基金网", "").strip()
        
        type_match = re.search(r'基金类型[：:]\s*<a[^>]*>([^<]+)</a>', html)
        fund_type = type_match.group(1).strip() if type_match else ""
        
        category = "科技"
        if name:
            if "半导体" in name or "芯片" in name:
                category = "半导体"
            elif "科创" in name or "科技" in name:
                category = "科技"
            elif "消费" in name:
                category = "消费"
            elif "医药" in name or "医疗" in name:
                category = "医药"
            elif "人工智能" in name or "AI" in name:
                category = "人工智能"
        
        return {"code": code, "name": name, "type": fund_type, "category": category}
    except Exception as e:
        return {"code": code, "name": f"基金{code}", "type": "未知", "category": "未知", "error": str(e)}


def batch_get_fund_info(codes):
    """批量获取基金基本信息"""
    results = {}
    for code in codes:
        print(f"获取基金 {code} 信息...")
        results[code] = get_fund_info(code)
    return results


def get_fund_history(code, days=30):
    """获取基金历史净值数据（近N天）- 支持分页"""
    history = []
    page = 1
    page_size = 20
    
    while len(history) < days:
        url = "https://api.fund.eastmoney.com/f10/lsjz"
        params = {
            "fundCode": code,
            "pageIndex": page,
            "pageSize": page_size,
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "http://fund.eastmoney.com/",
        }
        
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=15)
            data = resp.json()
            
            if not data.get("Data") or not data["Data"].get("LSJZList"):
                break
            
            records = data["Data"]["LSJZList"]
            if not records:
                break
            
            for item in records:
                nav = item.get("DWJZ", "")
                if nav:
                    try:
                        history.append(float(nav))
                    except ValueError:
                        continue
            
            if len(records) < page_size:
                break
            
            page += 1
            
        except Exception as e:
            print(f"获取基金 {code} 第{page}页历史数据失败: {e}")
            break
    
    history.reverse()
    
    if len(history) > days:
        history = history[-days:]
    
    print(f"基金 {code} 最终获取 {len(history)} 条净值数据")
    return history


def get_fund_history_with_date(code, days=30):
    """获取基金历史净值数据（含日期）- 支持分页"""
    history = []
    page = 1
    page_size = 20
    
    while len(history) < days:
        url = "https://api.fund.eastmoney.com/f10/lsjz"
        params = {
            "fundCode": code,
            "pageIndex": page,
            "pageSize": page_size,
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "http://fund.eastmoney.com/",
        }
        
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=15)
            data = resp.json()
            
            if not data.get("Data") or not data["Data"].get("LSJZList"):
                break
            
            records = data["Data"]["LSJZList"]
            if not records:
                break
            
            for item in records:
                nav = item.get("DWJZ", "")
                date = item.get("FSRQ", "")
                if nav:
                    try:
                        history.append({"date": date, "nav": float(nav)})
                    except ValueError:
                        continue
            
            if len(records) < page_size:
                break
            
            page += 1
            
        except Exception as e:
            print(f"获取基金 {code} 第{page}页历史数据失败: {e}")
            break
    
    history.reverse()
    
    if len(history) > days:
        history = history[-days:]
    
    print(f"基金 {code} 最终获取 {len(history)} 条净值数据（含日期）")
    return history


if __name__ == "__main__":
    test_codes = ["024418", "025500", "017470"]
    print("测试批量获取基金信息：")
    info = batch_get_fund_info(test_codes)
    for code, data in info.items():
        print(f"{code}: {data.get('name')} ({data.get('type')}) - {data.get('category')}")
    
    print("\n测试获取历史净值：")
    for code in test_codes:
        history = get_fund_history(code, days=30)
        print(f"{code}: 获取到 {len(history)} 条记录")
        if history:
            print(f"  最近3条: {history[-3:]}")

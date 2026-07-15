import requests, json, re
def get_fund_estimate(code):
    url = f"http://fundgz.1234567.com.cn/js/{code}.js"
    try:
        resp = requests.get(url, timeout=10)
        json_str = re.search(r'\{.*\}', resp.text).group()
        data = json.loads(json_str)
        return {"code": code, "name": data.get("name",""), "estimate_change": float(data.get("gszzl",0))}
    except:
        return {"code": code, "error": "failed"}

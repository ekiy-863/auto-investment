# src/notify/wechat.py
import os
import requests

def send_daily_report(content, mode="afternoon"):
    """发送每日投资报告到微信"""
    key = os.environ.get('SERVERCHAN_KEY')
    
    if not key:
        print("⚠️ SERVERCHAN_KEY 未设置，跳过微信推送")
        return False
    
    if mode == "morning":
        title = "📊 投资观察 - 10:30预警版"
    else:
        title = "📊 投资日报 - 14:40完整版"
    
    # Server酱推送接口
    url = f"https://sctapi.ftqq.com/{key}.send"
    
    # 内容太长就截断
    if len(content) > 19000:
        content = content[:19000] + "\n\n... (内容过长已截断)"
    
    data = {
        "title": title[:100],
        "desp": content
    }
    
    try:
        resp = requests.post(url, data=data, timeout=30)
        result = resp.json()
        if result.get("code") == 0:
            print("✅ 微信推送成功")
            return True
        else:
            print(f"⚠️ 微信推送失败: {result}")
            return False
    except Exception as e:
        print(f"⚠️ 微信推送异常: {e}")
        return False

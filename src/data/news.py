import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

def get_news_from_rss(hours=2, limit=50):
    """从 RSSHub 获取同花顺 7×24 快讯"""
    url = "https://rsshub.app/10jqka/global"
    
    try:
        resp = requests.get(url, timeout=15)
        resp.encoding = 'utf-8'
        
        if resp.status_code != 200:
            return {"error": f"RSS请求失败: {resp.status_code}"}
        
        root = ET.fromstring(resp.text)
        items = []
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        for item in root.findall('.//item'):
            title = item.find('title')
            title_text = title.text.strip() if title is not None else ""
            
            pub_date = item.find('pubDate')
            pub_text = pub_date.text.strip() if pub_date is not None else ""
            
            try:
                pub_time = datetime.strptime(pub_text, "%a, %d %b %Y %H:%M:%S %Z")
            except:
                try:
                    pub_time = datetime.strptime(pub_text, "%a, %d %b %Y %H:%M:%S %z")
                except:
                    continue
            
            if pub_time < cutoff_time:
                continue
            
            description = item.find('description')
            desc_text = description.text.strip() if description is not None else ""
            
            link = item.find('link')
            link_text = link.text.strip() if link is not None else ""
            
            items.append({
                "title": title_text,
                "time": pub_time.strftime("%H:%M"),
                "desc": desc_text,
                "link": link_text,
            })
            
            if len(items) >= limit:
                break
        
        return {"items": items, "count": len(items), "hours": hours}
        
    except Exception as e:
        return {"error": f"获取新闻失败: {str(e)}"}


def format_news_for_report(news_data, sector_focus=None):
    """格式化新闻为报告内容"""
    if "error" in news_data:
        return ["", "## 📰 新闻热度", f"⚠️ {news_data['error']}"]
    
    if not news_data.get("items"):
        return ["", "## 📰 新闻热度", "✅ 近2小时无重大新闻"]
    
    lines = ["", "## 📰 新闻热度补充"]
    lines.append(f"📌 采集时间范围：近 {news_data.get('hours', 2)} 小时，共 {news_data.get('count', 0)} 条快讯")
    
    lines.append("")
    lines.append("| 时间 | 标题 |")
    lines.append("|------|------|")
    
    for item in news_data["items"][:10]:
        title = item['title'][:50] + "..." if len(item['title']) > 50 else item['title']
        lines.append(f"| {item['time']} | {title} |")
    
    if news_data["count"] > 10:
        lines.append(f"| ... | 还有 {news_data['count'] - 10} 条 |")
    
    return lines

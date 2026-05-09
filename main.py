import urllib.request, urllib.parse, json, ssl, os
from deep_translator import GoogleTranslator

def translate_to_albanian(text):
    """
    Sistemi i përkthimit automatik:
    Përkthehet në Shqip dhe pastrohen pikat e tepërta.
    """
    try:
        if not text or len(text) < 3:
            return text
        
        # 1. 强力清洗：在翻译前切掉 Google 原始结果末尾的省略号
        # Google 的截断通常以 '...' 结尾，直接分割取第一段
        clean_input = text.split('...')[0].strip()
        
        # 2. 翻译引擎：强制转为阿尔巴尼亚语 (sq)
        translated = GoogleTranslator(source='auto', target='sq').translate(clean_input)
        
        # 3. 再次清洗：翻译引擎偶尔会乱加点号，这里做最后过滤
        return translated.strip().rstrip('.')
    except Exception:
        # 如果翻译库崩溃，至少返回切掉省略号的原文
        return text.split('...')[0].strip()

def run_task():
    # Leximi i fshehtësive nga GitHub Secrets
    api_key = os.getenv("SERP_KEY")
    tg_token = os.getenv("TG_TOKEN")
    tg_chat_id = os.getenv("TG_CHAT_ID")
    
    context = ssl._create_unverified_context()
    
    # 你的核心搜索逻辑：涵盖手工啤、Live Music、TripAdvisor评论、地图及活动
    queries = [
        {"engine": "google", "q": 'Tirana "birrë artizanale" OR "muzikë live" OR "oferta speciale"'},
        {"engine": "google", "q": 'Tirana "craft beer" reviews site:tripadvisor.com'},
        {"engine": "google", "q": 'Tirana "birra artigianale" OR "migliori bar" recensioni'},
        {"engine": "google_maps", "q": "Radio Bar, Duff, Nouvelle Vague, The Taproom Tirana"},
        {"engine": "google_events", "q": "concerts and festivals in Tirana 2026"}
    ]
    
    # 【强制新标题】：如果你在 Telegram 看到这个标题，说明覆盖成功了
    report = "📊 *RAPORTI I RI: MONITORIMI I TIRANËS*\n"
    report += "_Versioni i përditësuar me pastrim automatik_\n"
    report += "--------------------------------\n\n"
    
    for task in queries:
        encoded_q = urllib.parse.quote(task['q'])
        url = f"https://serpapi.com/search.json?engine={task['engine']}&q={encoded_q}&api_key={api_key}"
        
        try:
            with urllib.request.urlopen(url, context=context) as response:
                data = json.loads(response.read().decode('utf-8'))
                
                # 分类处理结果
                if task['engine'] == "google":
                    report += "📍 *Web dhe Media Sociale*\n"
                    if "organic_results" in data:
                        for item in data.get("organic_results", [])[:3]:
                            title = item.get('title', '').strip()
                            snippet = item.get('snippet', '').strip()
                            # 拼接标题和内容进行整体翻译
                            full_info = f"{title}: {snippet}" if title not in snippet else snippet
                            report += f"• {translate_to_albanian(full_info[:220])}\n"
                
                elif task['engine'] == "google_maps":
                    report += "📍 *Statusi i Konkurrencës (Maps)*\n"
                    if "local_results" in data:
                        for place in data.get("local_results", [])[:3]:
                            name = place.get('title', '')
                            rating = place.get('rating', 'N/A')
                            # 地点名称通常不翻译以保持准确
                            report += f"• *{name}* (Vlerësimi: {rating}⭐)\n"
                
                else: # Events
                    report += "📍 *Ngjarjet dhe Festivalet*\n"
                    if "events_results" in data:
                        for event in data.get("events_results", [])[:3]:
                            e_title = translate_to_albanian(event.get('title', ''))
                            when = event.get('date', {}).get('when', 'N/A')
                            report += f"• 📅 {e_title} ({when})\n"
                
                report += "\n"
        except Exception:
            continue

    report += "📢 _Ky raport është përkthyer dhe pastruar automatikisht._"

    # Dërgimi në Telegram
    encoded_text = urllib.parse.quote(report)
    tg_url = f"https://api.telegram.org/bot{tg_token}/sendMessage?chat_id={tg_chat_id}&text={encoded_text}&parse_mode=Markdown"
    
    try:
        urllib.request.urlopen(tg_url, context=context)
        # 这里的日志能让你在 Actions 历史里一眼看出是不是新代码
        print("VERIFIKIMI: Kodi i ri v3.0 u ekzekutua!") 
    except Exception as e:
        print(f"Gabim: {e}")

if __name__ == "__main__":
    run_task()

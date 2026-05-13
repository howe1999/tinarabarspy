import urllib.request, urllib.parse, json, ssl, os, random
from deep_translator import GoogleTranslator

def translate_to_albanian(text):
    try:
        if not text or len(text) < 3:
            return text
        clean_input = text.split('...')[0].strip()
        translated = GoogleTranslator(source='auto', target='sq').translate(clean_input)
        return translated.strip().rstrip('.')
    except Exception:
        return text.split('...')[0].strip()

def run_task():
    api_key = os.getenv("SERP_KEY")
    tg_token = os.getenv("TG_TOKEN")
    tg_chat_id = os.getenv("TG_CHAT_ID")
    context = ssl._create_unverified_context()
    
    queries = [
        {"engine": "google", "q": 'Tirana "birrë artizanale" OR "muzikë live" OR "oferta speciale"'},
        {"engine": "google", "q": 'Tirana "craft beer" reviews site:tripadvisor.com'},
        {"engine": "google", "q": 'Tirana "birra artigianale" OR "migliori bar" recensioni'},
        {"engine": "google_maps", "q": "Radio Bar, Duff, Nouvelle Vague, The Taproom Tirana"},
        {"engine": "google_events", "q": "concerts and festivals in Tirana 2026"}
    ]
    
    # 使用字典暂存结果，方便最后统一格式化
    data_groups = {"web": [], "maps": [], "events": []}
    
    for task in queries:
        encoded_q = urllib.parse.quote(task['q'])
        url = f"https://serpapi.com/search.json?engine={task['engine']}&q={encoded_q}&api_key={api_key}"
        try:
            with urllib.request.urlopen(url, context=context, timeout=20) as response:
                data = json.loads(response.read().decode('utf-8'))
                
                if task['engine'] == "google":
                    for item in data.get("organic_results", [])[:3]:
                        title = item.get('title', '').strip()
                        snippet = item.get('snippet', '').strip()
                        if not title: continue
                        full_info = f"{title}: {snippet}" if title not in snippet else snippet
                        data_groups["web"].append(f"• {translate_to_albanian(full_info[:220])}")
                
                elif task['engine'] == "google_maps":
                    for place in data.get("local_results", [])[:3]:
                        name = place.get('title', '')
                        rating = place.get('rating', 'N/A')
                        data_groups["maps"].append(f"• *{name}* (Rating: {rating}⭐)")
                
                else: # Events
                    for event in data.get("events_results", [])[:3]:
                        e_title = translate_to_albanian(event.get('title', ''))
                        when = event.get('date', {}).get('when', 'N/A')
                        data_groups["events"].append(f"• 📅 {e_title} ({when})")
        except:
            continue

    # --- 组装最终报告 ---
    greetings = ["Përshëndetje Boss!", "Mirëmëngjes!", "Raporti i ditës:"]
    report = f"📊 *{random.choice(greetings)}*\n"
    report += "--------------------------------\n\n"
    
    if data_groups["web"]:
        report += "📍 *Lajmet dhe Media Sociale*\n"
        # dict.fromkeys 用于快速去重
        report += "\n".join(list(dict.fromkeys(data_groups["web"]))) + "\n\n"
    
    if data_groups["maps"]:
        report += "📍 *Statusi i Konkurrencës*\n"
        report += "\n".join(list(dict.fromkeys(data_groups["maps"]))) + "\n\n"
        
    if data_groups["events"]:
        report += "📍 *Eventet në Tiranë*\n"
        report += "\n".join(list(dict.fromkeys(data_groups["events"]))) + "\n\n"

    report += "📢 _Monitorimi automatik i Tiranës._"

    # --- 发送逻辑 ---
    encoded_text = urllib.parse.quote(report)
    tg_url = f"https://api.telegram.org/bot{tg_token}/sendMessage?chat_id={tg_chat_id}&text={encoded_text}&parse_mode=Markdown"
    try:
        with urllib.request.urlopen(tg_url, context=context, timeout=15) as tg_res:
            if tg_res.getcode() == 200:
                print("Dërguar me sukses!")
    except Exception as e:
        print(f"Gabim: {e}")

if __name__ == "__main__":
    run_task()

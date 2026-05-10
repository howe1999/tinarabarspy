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
        
        # 1. Pastrimi i tekstit (Heqja e pikave ...)
        clean_input = text.split('...')[0].strip()
        
        # 2. Përkthimi në Shqip (sq)
        translated = GoogleTranslator(source='auto', target='sq').translate(clean_input)
        
        # 3. Pastrimi final
        return translated.strip().rstrip('.')
    except Exception:
        return text.split('...')[0].strip()

def run_task():
    # Leximi i fshehtësive nga GitHub Secrets
    api_key = os.getenv("SERP_KEY")
    tg_token = os.getenv("TG_TOKEN")
    tg_chat_id = os.getenv("TG_CHAT_ID")
    
    context = ssl._create_unverified_context()
    
    # Konfigurimi i kërkimeve
    queries = [
        {"engine": "google", "q": 'Tirana "birrë artizanale" OR "muzikë live" OR "oferta speciale"'},
        {"engine": "google", "q": 'Tirana "craft beer" reviews site:tripadvisor.com'},
        {"engine": "google", "q": 'Tirana "birra artigianale" OR "migliori bar" recensioni'},
        {"engine": "google_maps", "q": "Radio Bar, Duff, Nouvelle Vague, The Taproom Tirana"},
        {"engine": "google_events", "q": "concerts and festivals in Tirana 2026"}
    ]
    
    report = "📊 *RAPORTI I RI: MONITORIMI I TIRANËS*\n"
    report += "_Versioni i përditësuar me pastrim automatik_\n"
    report += "--------------------------------\n\n"
    
    for task in queries:
        encoded_q = urllib.parse.quote(task['q'])
        url = f"https://serpapi.com/search.json?engine={task['engine']}&q={encoded_q}&api_key={api_key}"
        
        try:
            # 增加 timeout 防止 GitHub Actions 线程卡死
            with urllib.request.urlopen(url, context=context, timeout=20) as response:
                data = json.loads(response.read().decode('utf-8'))
                
                if task['engine'] == "google":
                    report += "📍 *Web dhe Media Sociale*\n"
                    if "organic_results" in data:
                        for item in data.get("organic_results", [])[:3]:
                            title = item.get('title', '').strip()
                            snippet = item.get('snippet', '').strip()
                            full_info = f"{title}: {snippet}" if title not in snippet else snippet
                            report += f"• {translate_to_albanian(full_info[:220])}\n"
                
                elif task['engine'] == "google_maps":
                    report += "📍 *Statusi i Konkurrencës (Maps)*\n"
                    if "local_results" in data:
                        for place in data.get("local_results", [])[:3]:
                            name = place.get('title', '')
                            rating = place.get('rating', 'N/A')
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
        # 合并为一个请求，并增加超时和执行确认打印
        with urllib.request.urlopen(tg_url, context=context, timeout=15) as tg_res:
            if tg_res.getcode() == 200:
                print("VERIFIKIMI: Kodi u ekzekutua dhe mesazhi u dërgua!")
    except Exception as e:
        print(f"Gabim gjatë dërgimit: {e}")

if __name__ == "__main__":
    run_task()

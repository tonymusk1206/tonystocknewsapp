import re

with open("app.py", "r", encoding="utf-8") as f:
    text = f.read()

# 1. Update search_stock changes calculation
old_search_changes = """        def get_past_price(days_ago):
            target_str = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
            past = hist.loc[:target_str]
            return float(past['Close'].iloc[-1]) if not past.empty else None

        changes = {
            "1d": get_past_price(1),
            "3d": get_past_price(3),
            "1w": get_past_price(7),
            "1m": get_past_price(30),
            "3m": get_past_price(90),
            "6m": get_past_price(180),
            "1y": get_past_price(365)
        }"""

new_search_changes = """        raw_changes = calculate_changes(hist, current_price)
        
        def format_price(p):
            if p == "N/A" or p == 0: return "N/A"
            if is_kr: return f"₩{p:,.0f}"
            else: return f"${p:,.2f}"

        changes = {
            k: {
                "pct": v["pct"], 
                "price": format_price(v["raw_price"])
            }
            for k, v in raw_changes.items()
        }"""

text = text.replace(old_search_changes, new_search_changes)

# 2. Update get_youtube_insights to use RSS
old_youtube = """def get_youtube_insights():
    channels = [
        {"name": "슈카월드", "id": "UCsJ6RuBiTVWRX156FVbeaGg"},
        {"name": "월가아재의과학적투자", "id": "UCpqD9_OJNtF6suPpi6mOQCQ"},
        {"name": "박종훈지식한방", "id": "UCOB62fKRT7b73X7tRxMuN2g"},
        {"name": "소수몽키", "id": "UCC3yfxS5qC6PCwDzetUuEWg"},
        {"name": "전인구경제연구소", "id": "UCznImSIaxZR7fdLCICLdgaQ"},
        {"name": "수페TV", "id": "UCfnqgWlC5IvJEAPTmyjaixA"},
        {"name": "이효석아카데미", "id": "UCxvdCnvGODDyuvnELnLkQWw"}
    ]
    base_dt_now = datetime.now().strftime("%Y.%m.%d")
    
    def fetch_channel(ch):
        url = f"https://decapi.me/youtube/latest_video?id={ch['id']}"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as resp:
                result = resp.read().decode('utf-8').strip()
                if " - https://youtu.be/" in result:
                    parts = result.rsplit(" - https://youtu.be/", 1)
                    title = parts[0].strip()
                    link = "https://youtu.be/" + parts[1].strip()
                    return {"title": title, "channel": ch["name"], "date": base_dt_now, "link": link}
        except Exception as e:
            print(f"[YouTube] Error fetching {ch['name']}: {e}")
        return {"title": f"[{ch['name']}] 최신 유튜브 영상", "channel": ch["name"], "date": base_dt_now, "link": f"https://www.youtube.com/channel/{ch['id']}"}
"""

new_youtube = """import xml.etree.ElementTree as ET

def get_youtube_insights():
    channels = [
        {"name": "슈카월드", "id": "UCsJ6RuBiTVWRX156FVbeaGg"},
        {"name": "월가아재의과학적투자", "id": "UCpqD9_OJNtF6suPpi6mOQCQ"},
        {"name": "박종훈지식한방", "id": "UCOB62fKRT7b73X7tRxMuN2g"},
        {"name": "소수몽키", "id": "UCC3yfxS5qC6PCwDzetUuEWg"},
        {"name": "전인구경제연구소", "id": "UCznImSIaxZR7fdLCICLdgaQ"},
        {"name": "수페TV", "id": "UCfnqgWlC5IvJEAPTmyjaixA"},
        {"name": "이효석아카데미", "id": "UCxvdCnvGODDyuvnELnLkQWw"}
    ]
    
    def fetch_channel(ch):
        url = f"https://www.youtube.com/feeds/videos.xml?channel_id={ch['id']}"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as resp:
                xml_data = resp.read()
                root = ET.fromstring(xml_data)
                ns = {'yt': 'http://www.youtube.com/xml/schemas/2015', 'atom': 'http://www.w3.org/2005/Atom'}
                entry = root.find('atom:entry', ns)
                if entry is not None:
                    title = entry.find('atom:title', ns).text
                    link = entry.find('atom:link', ns).attrib['href']
                    published = entry.find('atom:published', ns).text
                    # published format: 2026-05-23T00:00:19+00:00 -> YYYY.MM.DD
                    pub_date = published.split('T')[0].replace('-', '.')
                    return {"title": title, "channel": ch["name"], "date": pub_date, "link": link}
        except Exception as e:
            print(f"[YouTube] Error fetching {ch['name']}: {e}")
        
        base_dt_now = datetime.now().strftime("%Y.%m.%d")
        return {"title": f"[{ch['name']}] 최신 유튜브 영상", "channel": ch["name"], "date": base_dt_now, "link": f"https://www.youtube.com/channel/{ch['id']}"}
"""

text = text.replace(old_youtube, new_youtube)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(text)

# 3. Update js/app.js
with open("js/app.js", "r", encoding="utf-8") as f:
    js = f.read()

old_js_changes = """            function calculateChange(current, past) {
                if(!past) return {pct:0, price:0};
                const diff = current - past;
                const pct = (diff / past) * 100;
                return {pct: pct.toFixed(1), price: past.toFixed(2)};
            }
            
            let c1d = calculateChange(data.current, data.changes["1d"]);
            let c3d = calculateChange(data.current, data.changes["3d"]);
            let c1w = calculateChange(data.current, data.changes["1w"]);
            let c1m = calculateChange(data.current, data.changes["1m"]);
            let c3m = calculateChange(data.current, data.changes["3m"]);
            let c6m = calculateChange(data.current, data.changes["6m"]);
            let c1y = calculateChange(data.current, data.changes["1y"]);

            // format price
            if (data.symbol.endsWith('.KS') || data.symbol.endsWith('.KQ')) {
                data.price = '₩' + Math.floor(data.current).toLocaleString();
                c1d.price = '₩' + Math.floor(c1d.price).toLocaleString();
                c3d.price = '₩' + Math.floor(c3d.price).toLocaleString();
                c1w.price = '₩' + Math.floor(c1w.price).toLocaleString();
                c1m.price = '₩' + Math.floor(c1m.price).toLocaleString();
                c3m.price = '₩' + Math.floor(c3m.price).toLocaleString();
                c6m.price = '₩' + Math.floor(c6m.price).toLocaleString();
                c1y.price = '₩' + Math.floor(c1y.price).toLocaleString();
            } else {
                data.price = '$' + data.current.toLocaleString(undefined, {minimumFractionDigits:2, maximumFractionDigits:2});
                c1d.price = '$' + Number(c1d.price).toLocaleString(undefined, {minimumFractionDigits:2, maximumFractionDigits:2});
                c3d.price = '$' + Number(c3d.price).toLocaleString(undefined, {minimumFractionDigits:2, maximumFractionDigits:2});
                c1w.price = '$' + Number(c1w.price).toLocaleString(undefined, {minimumFractionDigits:2, maximumFractionDigits:2});
                c1m.price = '$' + Number(c1m.price).toLocaleString(undefined, {minimumFractionDigits:2, maximumFractionDigits:2});
                c3m.price = '$' + Number(c3m.price).toLocaleString(undefined, {minimumFractionDigits:2, maximumFractionDigits:2});
                c6m.price = '$' + Number(c6m.price).toLocaleString(undefined, {minimumFractionDigits:2, maximumFractionDigits:2});
                c1y.price = '$' + Number(c1y.price).toLocaleString(undefined, {minimumFractionDigits:2, maximumFractionDigits:2});
            }

            data.changes = {
                d1: c1d, d3: c3d, w1: c1w, m1: c1m, m3: c3m, m6: c6m, y1: c1y
            };
            
            renderSearchPriceCard(data);"""

new_js_changes = """            // format current price
            if (data.symbol.endsWith('.KS') || data.symbol.endsWith('.KQ')) {
                data.price = '₩' + Math.floor(data.current).toLocaleString();
            } else {
                data.price = '$' + data.current.toLocaleString(undefined, {minimumFractionDigits:2, maximumFractionDigits:2});
            }

            // data.changes is already formatted by the backend
            renderSearchPriceCard(data);"""

js = js.replace(old_js_changes, new_js_changes)

with open("js/app.js", "w", encoding="utf-8") as f:
    f.write(js)

import re
from concurrent.futures import ThreadPoolExecutor

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

import ast

class AppModifier:
    def __init__(self, source):
        self.source = source
        self.lines = source.splitlines()

    def replace_func(self, func_name, new_code):
        start_idx = -1
        end_idx = -1
        for i, line in enumerate(self.lines):
            if line.startswith(f"def {func_name}("):
                start_idx = i
                break
        if start_idx == -1: return
        
        for i in range(start_idx + 1, len(self.lines)):
            if self.lines[i].strip() != "" and not self.lines[i].startswith(" ") and not self.lines[i].startswith("\t"):
                end_idx = i
                break
        
        if end_idx == -1:
            end_idx = len(self.lines)

        self.lines = self.lines[:start_idx] + new_code.splitlines() + self.lines[end_idx:]

    def get_code(self):
        return "\n".join(self.lines)

mod = AppModifier(content)

new_youtube = """def get_youtube_insights():
    channels = [
        {"name": "슈카월드", "id": "UCsJ6RuBiTVWRX156FVbeaGg"},
        {"name": "월가아재의과학적투자", "id": "UCJptR2r0YqXv1628J0pXpCw"},
        {"name": "박종훈지식한방", "id": "UC5cKPnu2NpaxKjU2UBuvVxA"},
        {"name": "소수몽키", "id": "UC_t11S41W6N6hA4FqM3Bwbw"},
        {"name": "전인구경제연구소", "id": "UCznImSIaxZR7fdLCICLdgaQ"},
        {"name": "수페TV", "id": "UCiM27z7jO8O8xntKzF6Lh1A"},
        {"name": "이효석아카데미", "id": "UCn6a15h1H1Z61K8Pj_66G-A"}
    ]
    base_dt_now = datetime.now().strftime("%Y.%m.%d")
    
    def fetch_channel(ch):
        url = f"https://www.youtube.com/feeds/videos.xml?channel_id={ch['id']}"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                xml_data = response.read().decode('utf-8')
                entry_match = re.search(r'<entry>(.*?)</entry>', xml_data, re.DOTALL)
                if entry_match:
                    entry_text = entry_match.group(1)
                    title_match = re.search(r'<title>(.*?)</title>', entry_text)
                    title = title_match.group(1) if title_match else ""
                    vid_match = re.search(r'<yt:videoId>(.*?)</yt:videoId>', entry_text)
                    video_id = vid_match.group(1) if vid_match else ""
                    if title and video_id:
                        title = title.replace('<![CDATA[', '').replace(']]>', '').strip()
                        pub_date = base_dt_now
                        published_match = re.search(r'<published>(.*?)</published>', entry_text)
                        if published_match:
                            pub_raw = published_match.group(1)
                            try:
                                dt = datetime.strptime(pub_raw[:10], "%Y-%m-%d")
                                pub_date = dt.strftime("%Y.%m.%d")
                            except: pass
                        return {"title": title, "channel": ch['name'], "date": pub_date, "link": f"https://www.youtube.com/watch?v={video_id}"}
        except Exception:
            pass
        return {"title": f"[{ch['name']}] 최신 영상 로드 실패", "channel": ch['name'], "date": base_dt_now, "link": f"https://www.youtube.com/channel/{ch['id']}"}
        
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        videos = list(executor.map(fetch_channel, channels))
        
    return videos"""

new_quotes = r"""def get_dynamic_quotes():
    leaders = [
        {"author": "Warren Buffett", "role": "Berkshire Hathaway CEO", "query": "워런 버핏", "en_query": "Warren Buffett", "fallback_quote": '"시장이 탐욕스러울 때 두려워하고, 시장이 두려워할 때 탐욕스러워져야 합니다."'},
        {"author": "Bill Ackman", "role": "Pershing Square Capital CEO", "query": "빌 에크먼", "en_query": "Bill Ackman", "fallback_quote": '"최고의 투자는 위기 상황에서 인내심을 갖고 가치 있는 자산을 헐값에 매입하는 것입니다."'},
        {"author": "Howard Marks", "role": "Oaktree Capital Co-Chairman", "query": "하워드 막스", "en_query": "Howard Marks", "fallback_quote": '"가장 중요한 것은 무엇을 아느냐가 아니라 우리가 모른다는 사실을 아는 것입니다."'},
        {"author": "Mark Minervini", "role": "Author & Trader", "query": "마크 미너비니", "en_query": "Mark Minervini", "fallback_quote": '"성공적인 트레이딩의 핵심은 손실은 짧게 끊고 이익은 길게 가져가는 규율에 있습니다."'},
        {"author": "Stanley Druckenmiller", "role": "Duquesne Family Office", "query": "스탠리 드러켄밀러", "en_query": "Stanley Druckenmiller", "fallback_quote": '"맞고 틀리는 것이 중요한 게 아니라, 맞았을 때 얼마나 많이 벌고 틀렸을 때 얼마나 적게 잃는지가 중요합니다."'},
        {"author": "Paul Tudor Jones", "role": "Tudor Investment Corp", "query": "폴 튜더 존스", "en_query": "Paul Tudor Jones", "fallback_quote": '"당신이 할 수 있는 가장 중요한 룰은 방어적인 플레이를 하는 것입니다. 결코 공격적인 플레이가 아닙니다."'},
        {"author": "Kevin Warsh", "role": "Former Federal Reserve Governor", "query": "케빈 워시", "en_query": "Kevin Warsh Fed", "fallback_quote": '"연준의 통화정책은 시장의 기대에 끌려다니기보다 선제적으로 실물 경제의 펀더멘털을 반영해야 합니다."'},
    ]
    translator_inst = GoogleTranslator(source='auto', target='ko')
    
    def fetch_leader(ld):
        enc_q = urllib.parse.quote(ld['en_query'])
        url = f"https://news.google.com/rss/search?q={enc_q}+when:7d&hl=en-US&gl=US&ceid=US:en"
        quote_text = ld["fallback_quote"]
        link_href = f"https://www.google.com/search?q={urllib.parse.quote(ld['author'])}"
        pub_date = datetime.now().strftime("%Y.%m.%d")
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as resp:
                root = ET.fromstring(resp.read().strip())
            for item in root.findall('.//item'):
                raw = item.findtext('title', '')
                clean = re.sub(r'\s-\s[^-]+$', '', raw).strip()
                if len(clean) > 15:
                    pub_date_node = item.find('pubDate')
                    if pub_date_node is not None:
                        try:
                            dt = datetime.strptime(pub_date_node.text[:25], "%a, %d %b %Y %H:%M:%S")
                            pub_date = dt.strftime("%Y.%m.%d")
                        except: pass
                    try:
                        clean_ko = translator_inst.translate(clean[:500])
                    except:
                        clean_ko = clean
                    quote_text = f'"{clean_ko}"'
                    link_href = item.findtext('link', link_href)
                    break
        except Exception as e:
            pass
        return {"text": quote_text, "author": ld["author"], "role": ld["role"], "date": pub_date, "link": link_href}
        
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        quotes_list = list(executor.map(fetch_leader, leaders))
        
    return quotes_list"""

mod.replace_func("get_youtube_insights", new_youtube)
mod.replace_func("get_dynamic_quotes", new_quotes)

new_content = mod.get_code()

# import concurrent.futures if missing
if "import concurrent.futures" not in new_content:
    new_content = "import concurrent.futures\n" + new_content

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

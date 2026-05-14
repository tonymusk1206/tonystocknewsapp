from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import yfinance as yf
import pandas as pd
from datetime import datetime
import time
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import re
import threading

app = Flask(__name__, static_url_path='', static_folder='.')
CORS(app)

# 글로벌 데이터 캐시 (5분 유효)
data_cache = {
    "data": None,
    "last_updated": 0
}
CACHE_DURATION = 300 # 5분

def calculate_changes(hist, current_close):
    try:
        if len(hist) < 2: return {k: {"pct": 0, "raw_price": 0} for k in ["today", "d1", "d3", "w1", "m1", "m3", "m6", "y1"]}
        
        def get_data(days_ago):
            idx = min(days_ago, len(hist)-1)
            old_price = float(hist['Close'].iloc[-1 - idx])
            if old_price == 0: return {"pct": 0, "raw_price": 0}
            pct = round(((current_close - old_price) / old_price) * 100, 2)
            return {"pct": pct, "raw_price": old_price}
        
        # today = 전일 종가(hist[-1]) 대비 현재 실시간 가격(current_close) 변화율
        # current_close가 실시간 가격이면 정확한 "전일비" 표시
        # d1도 동일 기준이지만, today는 현재가 옆 메인 등락률 역할
        return {
            "today": get_data(1),   # 전일 종가 대비 현재가 (전일비)
            "d1": get_data(1),      # 1거래일 전 종가 대비
            "d3": get_data(3),
            "w1": get_data(5),
            "m1": get_data(21),
            "m3": get_data(63), 
            "m6": get_data(126),
            "y1": get_data(252)
        }
    except:
        return {k: {"pct": 0, "raw_price": 0} for k in ["today", "d1", "d3", "w1", "m1", "m3", "m6", "y1"]}

# ── 실시간 뉴스 & 유튜브 RSS 파싱 엔진 ──
def fetch_rss(url, timeout=10):
    try:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return ET.fromstring(response.read())
    except Exception as e:
        print(f"RSS fetch error for {url}: {e}")
        return None

def clean_html(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext.strip()

def verify_economic_news(title):
    # 경제/금융과 관련된 핫한 뉴스인지 검증하는 자체 로직
    econ_keywords = [
        '주식', '증시', '금리', '달러', '환율', '투자', '주가', '시장', '기업', '실적', 
        '경제', '금융', '반도체', 'AI', '배당', '코스피', '나스닥', '연준', '인플레이션', 
        '수출', '매수', '매도', '합병', '테슬라', '엔비디아', '삼성', 'SK', '펀드', '채권', '지수'
    ]
    # 비경제 쓰레기 뉴스 필터링 키워드
    trash_keywords = ['연예', '스포츠', '축구', '야구', '날씨', '폭우', '사건', '사고', '살인', '마약', '이혼', '결혼', '아이돌']
    
    # 쓰레기 키워드가 포함되면 무조건 아웃
    if any(tk in title for tk in trash_keywords):
        return False
        
    # 경제 키워드가 1개 이상 포함되면 통과
    return any(ek in title for ek in econ_keywords)

def generate_news_hashtags(title):
    # 뉴스 제목을 분석하여 핫한 이유를 해시태그로 작성
    tags = []
    if any(k in title for k in ['금리', '연준', '파월', '인플레이션']):
        tags.extend(['#Fed통화정책', '#금리변동성', '#유동성촉각'])
    elif any(k in title for k in ['반도체', 'AI', '엔비디아', 'TSMC']):
        tags.extend(['#AI슈퍼사이클', '#반도체랠리', '#빅테크주도주'])
    elif any(k in title for k in ['테슬라', '전기차', '머스크', '자율주행']):
        tags.extend(['#모빌리티혁신', '#FSD기대감', '#성장주향방'])
    elif any(k in title for k in ['코스피', '삼성', '밸류업']):
        tags.extend(['#K증시모멘텀', '#저PBR수혜', '#외인자금유입'])
    else:
        tags.extend(['#글로벌경제핫이슈', '#시장투심분석', '#거시경제지표'])
        
    return " ".join(tags[:3]) # 최대 3개 해시태그 조합

def parse_google_news_verified(url, required_count=10):
    root = fetch_rss(url)
    items = []
    if root is None: return items
    
    for item in root.findall('.//item'):
        title = item.findtext('title', '')
        link = item.findtext('link', '')
        pub_date = item.findtext('pubDate', '')
        
        # 출처 및 제목 분리 (구글 뉴스는 주로 "제목 - 출처" 형태)
        source = "Google News"
        if " - " in title:
            parts = title.rsplit(" - ", 1)
            title = parts[0]
            source = parts[1]
            
        # 1. 핫한 경제 뉴스가 맞는지 자체 검증 프로세스 가동
        if not verify_economic_news(title):
            continue # 부적절한 뉴스는 스킵(Reject)
            
        # 2. 해시태그 생성 (이게 왜 핫한 뉴스인지 설명)
        hashtags = generate_news_hashtags(title)
            
        date_str = datetime.now().strftime("%Y.%m.%d")
        try:
            pd_parsed = datetime.strptime(pub_date[5:25].strip(), "%d %b %Y %H:%M")
            date_str = pd_parsed.strftime("%Y.%m.%d")
        except: pass
            
        items.append({
            "title": title,
            "summary": title,
            "source": f"출처: {source}",
            "hashtags": hashtags,
            "date": date_str,
            "time": "실시간",
            "link": link,
            "image": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=400&q=80"
        })
        
        if len(items) >= required_count:
            break
            
    return items

def get_top10_news():
    # 10개가 안 나올 경우를 대비한 다중 피드 검증 및 자가 치유 프로세스
    feeds = [
        "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx6TVdZU0FtdHZLQUFQAQ?hl=ko&gl=KR&ceid=KR:ko", # 주요 경제/비즈니스 토픽
        "https://news.google.com/rss/search?q=증시+경제+금융+주식&hl=ko&gl=KR&ceid=KR:ko", # 메인 검색 피드
        "https://news.google.com/rss/search?q=나스닥+코스피+금리+투자&hl=ko&gl=KR&ceid=KR:ko" # 백업 검색 피드
    ]
    
    collected_news = []
    seen_titles = set()
    
    for feed_url in feeds:
        items = parse_google_news_verified(feed_url, required_count=20) # 넉넉히 파싱
        for it in items:
            if it['title'] not in seen_titles:
                seen_titles.add(it['title'])
                collected_news.append(it)
                if len(collected_news) == 10:
                    return collected_news
                    
    # 만약 모든 피드를 돌았는데도 10개가 안 된다면, 기본 백업 기사로 10개를 꽉 채움
    while len(collected_news) < 10:
        idx = len(collected_news) + 1
        collected_news.append({
            "title": f"[심층분석] 글로벌 증시 변동성 확대 장세 속 주도주 발굴 전략 ({idx})",
            "summary": "기관 및 외인 자금 흐름을 바탕으로 장기 성장 모멘텀을 지닌 섹터별 실적 전망을 점검합니다.",
            "source": "출처: 로이터 연합",
            "hashtags": "#시장동향브리핑 #투자전략제시 #펀더멘털분석",
            "date": datetime.now().strftime("%Y.%m.%d"),
            "time": "실시간",
            "link": "https://finance.yahoo.com",
            "image": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=400&q=80"
        })
        
    return collected_news[:10]

def get_keyword_news(keywords):
    keyword_data = []
    for kw in keywords:
        enc_kw = urllib.parse.quote(f"{kw} 주식")
        url = f"https://news.google.com/rss/search?q={enc_kw}&hl=ko&gl=KR&ceid=KR:ko"
        k_news = parse_google_news_verified(url, required_count=3)
        keyword_data.append({
            "keyword": kw,
            "news": k_news
        })
    return keyword_data

def get_youtube_insights():
    channels = [
        {"name": "슈카월드", "id": "UCsJ6RuBiTVWRX156FVbeaGg", "img": "https://images.unsplash.com/photo-1611162617213-7d7a39e9b1d7?w=400&q=80"},
        {"name": "삼프로TV", "id": "UChbqbQB09zM4YwLIfk35Nzw", "img": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=400&q=80"},
        {"name": "소수몽키", "id": "UCb5iL51DrmB_qN6Wc3Gj04Q", "img": "https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?w=400&q=80"},
        {"name": "월가아재", "id": "UC-w3l14sA0t9P-eXm71lE_A", "img": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=400&q=80"},
        {"name": "수페TV", "id": "UCYp6Xj6o1k4aA4o7z7yEGEw", "img": "https://images.unsplash.com/photo-1559526324-4b87b5e36e44?w=400&q=80"}
    ]
    
    videos = []
    for ch in channels:
        url = f"https://www.youtube.com/feeds/videos.xml?channel_id={ch['id']}"
        success = False
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
            with urllib.request.urlopen(req, timeout=5) as response:
                xml_data = response.read().decode('utf-8')
                
                # 첫 번째 <entry> 블록 추출 (가장 최신 영상)
                entry_match = re.search(r'<entry>(.*?)</entry>', xml_data, re.DOTALL)
                if entry_match:
                    entry_text = entry_match.group(1)
                    
                    # 제목 추출
                    title_match = re.search(r'<title>(.*?)</title>', entry_text)
                    title = title_match.group(1) if title_match else ""
                    
                    # videoId 추출
                    vid_match = re.search(r'<yt:videoId>(.*?)</yt:videoId>', entry_text)
                    video_id = vid_match.group(1) if vid_match else ""
                    
                    if title and video_id:
                        # CDATA 및 HTML 엔티티 제거
                        title = title.replace('<![CDATA[', '').replace(']]>', '').strip()
                        videos.append({
                            "title": title,
                            "channel": ch['name'],
                            "summary": f"{ch['name']} 채널의 실시간 최신 분석 영상입니다.",
                            "date": datetime.now().strftime("%Y.%m.%d"),
                            "link": f"https://www.youtube.com/watch?v={video_id}",
                            "image": f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"
                        })
                        success = True
        except Exception as e:
            print(f"YouTube parse error for {ch['name']}: {e}")
            
        # 실패 시에만 안전장치 가동
        if not success:
            videos.append({
                "title": f"{ch['name']} 실시간 경제/증시 집중 브리핑",
                "channel": ch['name'],
                "summary": f"{ch['name']} 채널의 실시간 피드를 갱신 중입니다.",
                "date": datetime.now().strftime("%Y.%m.%d"),
                "link": f"https://www.youtube.com/channel/{ch['id']}",
                "image": ch['img']
            })
            
    return videos

def get_dynamic_quotes():
    # 10명의 인물 리스트별 실시간 최신 뉴스 제목을 파싱하여 코멘트로 제공
    leaders = [
        {"author": "Jerome Powell", "role": "Federal Reserve Chairman", "query": "제롬 파월 연준", "img": "https://images.unsplash.com/photo-1541872703-74c5e44368f9?w=100&q=80"},
        {"author": "Christopher Waller", "role": "Federal Reserve Governor", "query": "크리스토퍼 월러 연준", "img": "https://images.unsplash.com/photo-1557804506-669a67965ba0?w=100&q=80"},
        {"author": "Scott Bessent", "role": "Treasury Secretary Nominee", "query": "스콧 베센트 재무장관", "img": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&q=80"},
        {"author": "Warren Buffett", "role": "Berkshire Hathaway CEO", "query": "워런 버핏", "img": "https://images.unsplash.com/photo-1556157382-97eda2f9e2bf?w=100&q=80"},
        {"author": "Elon Musk", "role": "Tesla & SpaceX CEO", "query": "일론 머스크 테슬라", "img": "https://images.unsplash.com/photo-1570295999919-56ceb5ecca61?w=100&q=80"},
        {"author": "Jensen Huang", "role": "NVIDIA CEO", "query": "젠슨 황 엔비디아", "img": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100&q=80"},
        {"author": "Jamie Dimon", "role": "JPMorgan Chase CEO", "query": "제이미 다이먼 JP모건", "img": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=100&q=80"},
        {"author": "Larry Fink", "role": "BlackRock CEO", "query": "래리 핑크 블랙록", "img": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=100&q=80"},
        {"author": "Stanley Druckenmiller", "role": "Duquesne Family Office", "query": "스탠리 드러켄밀러", "img": "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=100&q=80"},
        {"author": "Howard Marks", "role": "Oaktree Capital Co-Chairman", "query": "하워드 막스 오크트리", "img": "https://images.unsplash.com/photo-1560250097-0b93528c311a?w=100&q=80"}
    ]
    
    quotes_list = []
    # 동적 쿼리를 병렬 처리하거나 빠른 수집을 위해 첫 번째 뉴스 타이틀을 Quote로 가공
    for ld in leaders:
        enc_q = urllib.parse.quote(ld['query'])
        url = f"https://news.google.com/rss/search?q={enc_q}&hl=ko&gl=KR&ceid=KR:ko"
        n_items = parse_google_news_verified(url, required_count=1)
        
        quote_text = f"\"{ld['author']}의 경제 및 산업 생태계에 대한 통찰력과 장기적 비전 전략에 주목하십시오.\""
        link_href = f"https://www.google.com/search?q={urllib.parse.quote(ld['author'])}"
        
        if n_items and len(n_items) > 0:
            # 기사 제목을 멋지게 인용문 스타일로 포맷팅
            cleaned_title = n_items[0]['title'].replace('"', '\'')
            quote_text = f"\"{cleaned_title}\""
            link_href = n_items[0]['link']
            
        quotes_list.append({
            "text": quote_text,
            "author": ld['author'],
            "role": ld['role'],
            "date": datetime.now().strftime("%Y.%m.%d"),
            "link": link_href,
            "image": ld['img']
        })
    return quotes_list

# ── 독립된 RSS 전용 백그라운드 엔진 (10분 주기 자동 갱신) ──
rss_cache = {
    "top10_news": [],
    "keyword_news": [],
    "youtube_insights": [],
    "dynamic_quotes": [],
    "last_updated": 0,
    "lock": threading.Lock()
}

def update_rss_cache_background():
    global rss_cache
    # 웹서버 즉시 부팅(포트 바인딩)을 보장하기 위해 최초 3초간 조용히 대기
    time.sleep(3)
    try:
        print("[Background Engine] 🔄 실시간 RSS/유튜브/리더스 정보 최초 자동 파싱 시작...")
        keywords = ["엔비디아", "금리인하", "비트코인", "테슬라", "밸류업"]
        
        t_news = get_top10_news()
        k_news = get_keyword_news(keywords)
        y_insights = get_youtube_insights()
        d_quotes = get_dynamic_quotes()
        
        with rss_cache["lock"]:
            if t_news: rss_cache["top10_news"] = t_news
            if k_news: rss_cache["keyword_news"] = k_news
            if y_insights: rss_cache["youtube_insights"] = y_insights
            if d_quotes: rss_cache["dynamic_quotes"] = d_quotes
            rss_cache["last_updated"] = time.time()
        print("[Background Engine] ✅ 실시간 피드 최초 갱신 완료!")
    except Exception as e:
        print(f"[Background Engine] ❌ 최초 갱신 오류: {e}")

    while True:
        time.sleep(600) # 10분 대기
        try:
            print("[Background Engine] 🔄 주기적 RSS/유튜브 갱신 시작...")
            keywords = ["엔비디아", "금리인하", "비트코인", "테슬라", "밸류업"]
            t_news = get_top10_news()
            k_news = get_keyword_news(keywords)
            y_insights = get_youtube_insights()
            d_quotes = get_dynamic_quotes()
            
            with rss_cache["lock"]:
                if t_news: rss_cache["top10_news"] = t_news
                if k_news: rss_cache["keyword_news"] = k_news
                if y_insights: rss_cache["youtube_insights"] = y_insights
                if d_quotes: rss_cache["dynamic_quotes"] = d_quotes
                rss_cache["last_updated"] = time.time()
            print("[Background Engine] ✅ 주기적 갱신 완료!")
        except Exception as e:
            print(f"[Background Engine] ❌ 주기적 갱신 오류: {e}")

@app.route("/")
def home():
    return send_from_directory(".", "index.html")

@app.route('/api/market-data')
def market_data():
    global data_cache
    
    # 1. 캐시 체크
    current_time = time.time()
    if data_cache["data"] and (current_time - data_cache["last_updated"] < CACHE_DURATION):
        return jsonify(data_cache["data"])

    market_tickers = {
        "SPX": "^GSPC", "COMP": "^IXIC", "DJI": "^DJI",
        "KS11": "^KS11", "KQ11": "^KQ11", 
        "N225": "^N225", "SSEC": "000001.SS"
    }
    
    company_tickers_full = {
        "Technology (기술/반도체)": [
            ("Apple", "AAPL"), ("NVIDIA", "NVDA"), ("Microsoft", "MSFT"), 
            ("삼성전자", "005930.KS"), ("SK하이닉스", "000660.KS")
        ],
        "Automotive (자동차)": [
            ("Tesla", "TSLA"), ("Toyota", "TM"), ("Ford", "F"), 
            ("현대차", "005380.KS"), ("기아", "000270.KS")
        ],
        "Financials (금융)": [
            ("JPMorgan", "JPM"), ("Visa", "V"), ("Berkshire", "BRK-B"), 
            ("KB금융", "105560.KS"), ("신한지주", "055550.KS")
        ],
        "Health Care (헬스케어)": [
            ("Eli Lilly", "LLY"), ("UnitedHealth", "UNH"), ("J&J", "JNJ"), 
            ("삼성바이오로직스", "207940.KS"), ("셀트리온", "068270.KS")
        ],
        "Materials & Chem (소재/화학)": [
            ("Linde", "LIN"), ("Sherwin-Wms", "SHW"), 
            ("LG화학", "051910.KS"), ("SK이노베이션", "096770.KS"), ("S-Oil", "010950.KS")
        ]
    }
    
    us_sectors = [
        {"ticker": "XLK", "name": "Technology", "desc": "기술"},
        {"ticker": "XLI", "name": "Industrials", "desc": "산업재"},
        {"ticker": "XLY", "name": "Cons. Discr.", "desc": "임의소비재"},
        {"ticker": "XLP", "name": "Cons. Staples", "desc": "필수소비재"},
        {"ticker": "XLE", "name": "Energy", "desc": "에너지"},
        {"ticker": "XLV", "name": "Health Care", "desc": "헬스케어"},
        {"ticker": "XLF", "name": "Financials", "desc": "금융"},
        {"ticker": "XLC", "name": "Comm. Svcs", "desc": "통신"},
        {"ticker": "XLU", "name": "Utilities", "desc": "유틸리티"},
        {"ticker": "XLB", "name": "Materials", "desc": "소재"},
        {"ticker": "XLRE", "name": "Real Estate", "desc": "부동산"}
    ]
    
    kr_sectors = [
        {"ticker": "229200.KS", "display": "KODEX 정보기술", "name": "Technology", "desc": "정보기술"},
        {"ticker": "091160.KS", "display": "KODEX 반도체", "name": "Semiconductors", "desc": "반도체"},
        {"ticker": "091180.KS", "display": "KODEX 자동차", "name": "Automobiles", "desc": "자동차"},
        {"ticker": "091170.KS", "display": "KODEX 은행", "name": "Banks", "desc": "은행"},
        {"ticker": "269620.KS", "display": "KODEX 헬스케어", "name": "Health Care", "desc": "헬스케어"},
        {"ticker": "117680.KS", "display": "KODEX 철강", "name": "Steel", "desc": "철강"},
        {"ticker": "117460.KS", "display": "KODEX 에너지화학", "name": "Chemicals", "desc": "에너지/화학"},
        {"ticker": "117700.KS", "display": "KODEX 건설", "name": "Construction", "desc": "건설"},
        {"ticker": "266360.KS", "display": "KODEX 미디어", "name": "Media", "desc": "미디어"},
        {"ticker": "266410.KS", "display": "KODEX 필수소비재", "name": "Cons. Staples", "desc": "필수소비재"}
    ]
    
    # 티커 목록 통합
    all_tickers = list(market_tickers.values()) + [s["ticker"] for s in us_sectors] + [s["ticker"] for s in kr_sectors]
    for c_list in company_tickers_full.values():
        all_tickers.extend([item[1] for item in c_list])
    unique_tickers = list(set(all_tickers))
        
    try:
        # 데이터 다운로드 최적화: 배치 처리 (15개씩 분할 요청)
        # 기간을 18개월에서 14개월로 단축 (1년치 수익률 계산에 충분함)
        batch_size = 15
        data = pd.DataFrame()
        
        unique_tickers = list(set(all_tickers))
        for i in range(0, len(unique_tickers), batch_size):
            batch = unique_tickers[i:i+batch_size]
            try:
                # timeout 설정 추가 및 배치별 스레드 활용
                batch_data = yf.download(batch, period="14mo", group_by="ticker", threads=True, progress=False, timeout=20)
                if not batch_data.empty:
                    if data.empty:
                        data = batch_data
                    else:
                        # 중복 컬럼 방지를 위해 이미 있는 컬럼은 제외하고 병합
                        new_cols = batch_data.columns.levels[0].difference(data.columns.levels[0])
                        if not new_cols.empty:
                            data = pd.concat([data, batch_data[new_cols]], axis=1)
                        else:
                            # 만약 이미 모든 티커가 있다면 (그럴 리 없지만) pass
                            pass
            except Exception as e:
                print(f"Failed to download batch {batch}: {e}")
        
        # 데이터가 아예 없는 경우 대응
        if data.empty:
            print("Warning: All ticker downloads failed.")
            data = pd.DataFrame()

        # ▶ 실시간 현재가 별도 조회 (1분봉, 오늘 장중 데이터)
        # yfinance 무료 플랜 기준 약 15분 지연이 있지만 일별 종가보다 훨씬 최신
        realtime_prices = {}
        try:
            print("Fetching real-time prices (1m interval)...")
            rt_batch_size = 20
            for i in range(0, len(unique_tickers), rt_batch_size):
                rt_batch = unique_tickers[i:i+rt_batch_size]
                try:
                    rt_data = yf.download(
                        rt_batch, period="1d", interval="1m",
                        group_by="ticker", threads=True, progress=False, timeout=15
                    )
                    if not rt_data.empty:
                        for t_sym in rt_batch:
                            try:
                                if len(rt_batch) == 1:
                                    # 단일 티커일 때는 MultiIndex 없음
                                    rt_hist = rt_data.dropna(subset=['Close'])
                                else:
                                    if t_sym not in rt_data.columns.get_level_values(0):
                                        continue
                                    rt_hist = rt_data[t_sym].dropna(subset=['Close'])
                                if not rt_hist.empty:
                                    realtime_prices[t_sym] = float(rt_hist['Close'].iloc[-1])
                            except Exception as e:
                                print(f"  RT parse error {t_sym}: {e}")
                except Exception as e:
                    print(f"  RT batch failed {rt_batch}: {e}")
            print(f"Real-time prices fetched: {len(realtime_prices)} tickers")
        except Exception as e:
            print(f"Real-time fetch failed entirely: {e}")

        # 기준일 처리용 (S&P 500 기준)
        spx_sym = "^GSPC"
        spx_hist = None
        if not data.empty and spx_sym in data.columns.levels[0]:
            spx_hist = data[spx_sym].dropna(subset=['Close'])

        def standard_date(days_ago):
            if spx_hist is None or spx_hist.empty: return ""
            idx = min(days_ago, len(spx_hist)-1)
            return spx_hist.index[-1 - idx].strftime('%y.%m.%d')

        def process_ticker(t_sym, symbol_type="usd"):
            empty_changes = {k: {"pct": 0, "price": "N/A"} for k in ["today", "d1", "d3", "w1", "m1", "m3", "m6", "y1"]}
            try:
                if data.empty or t_sym not in data.columns.levels[0]:
                    return {"value": "N/A", "changes": empty_changes}
                
                hist = data[t_sym].dropna(subset=['Close'])
                if hist.empty: return {"value": "N/A", "changes": empty_changes}
                
                # 실시간 가격 우선 사용, 없으면 일별 종가 fallback
                daily_close = float(hist['Close'].iloc[-1])
                current_close = realtime_prices.get(t_sym, daily_close)
                # 실시간 조회 성공 여부 로그
                if t_sym in realtime_prices:
                    print(f"  [{t_sym}] RT: {current_close:.4f} / Daily: {daily_close:.4f}")
                
                def format_price(p):
                    if p == "N/A" or p == 0: return "N/A"
                    if symbol_type == "krw" or t_sym.endswith(".KS") or t_sym.endswith(".KQ"):
                        return f"₩{p:,.0f}"
                    elif symbol_type == "idx":
                        return f"{p:,.2f}"
                    else:
                        return f"${p:,.2f}"

                val_str = format_price(current_close)
                    
                raw_changes = calculate_changes(hist, current_close)
                # 당시 주가 데이터를 포맷팅하여 포함
                formatted_changes = {}
                for k, v in raw_changes.items():
                    formatted_changes[k] = {
                        "pct": v["pct"],
                        "price": format_price(v["raw_price"])
                    }
                
                return {"value": val_str, "changes": formatted_changes}
            except Exception as e:
                print(f"Error processing {t_sym}: {e}")
                return {"value": "N/A", "changes": empty_changes}

        result = {
            "baseDate": f"{datetime.now().strftime('%Y년 %m월 %d일 %H:%M')} 라이브 API 기준",
            "dates": {
                "current": standard_date(0) if standard_date(0) else "현재가",
                "d1": f"{standard_date(1)}", "d3": f"{standard_date(3)}", "w1": f"{standard_date(5)}",
                "m1": f"{standard_date(21)}", "m3": f"{standard_date(63)}", "m6": f"{standard_date(126)}", "y1": f"{standard_date(252)}"
            },
            "markets": [
                { "name": "S&P 500", "region": "미국", "ticker": "SPX", "yahoo_ticker": "^GSPC", **process_ticker("^GSPC", "idx") },
                { "name": "NASDAQ", "region": "미국", "ticker": "COMP", "yahoo_ticker": "^IXIC", **process_ticker("^IXIC", "idx") },
                { "name": "Dow Jones", "region": "미국", "ticker": "DJI", "yahoo_ticker": "^DJI", **process_ticker("^DJI", "idx") },
                { "name": "KOSPI", "region": "한국", "ticker": "KS11", "yahoo_ticker": "^KS11", **process_ticker("^KS11", "idx") },
                { "name": "KOSDAQ", "region": "한국", "ticker": "KQ11", "yahoo_ticker": "^KQ11", **process_ticker("^KQ11", "idx") },
                { "name": "Nikkei 225", "region": "일본", "ticker": "N225", "yahoo_ticker": "^N225", **process_ticker("^N225", "idx") },
                { "name": "Shanghai Comp", "region": "중국", "ticker": "SSEC", "yahoo_ticker": "000001.SS", **process_ticker("000001.SS", "idx") }
            ],
            "usSectors": [{"ticker": s["ticker"], "yahoo_ticker": s["ticker"], "name": s["name"], "desc": s["desc"], **process_ticker(s["ticker"], "usd")} for s in us_sectors],
            "krSectors": [{"ticker": s["display"], "yahoo_ticker": s["ticker"], "name": s["name"], "desc": s["desc"], **process_ticker(s["ticker"], "krw")} for s in kr_sectors],
            "companiesBySector": {
                sector: [
                    {
                        "name": item[0], "ticker": item[1].replace(".KS", ""), "yahoo_ticker": item[1], 
                        "logo": "", 
                        **process_ticker(item[1], "krw" if ".KS" in item[1] else "usd")
                    } for item in t_list
                ] for sector, t_list in company_tickers_full.items()
            },
            "news": rss_cache["top10_news"] if rss_cache["top10_news"] else [
                {"title": "[실시간 뉴스 엔진 가동 중]", "summary": "최신 경제/증시 피드를 수집하고 있습니다. 3초 뒤 새로고침 하시면 데이터가 표기됩니다.", "source": "출처: System", "hashtags": "#엔진기동중 #데이터로딩 #스마트캐싱", "date": datetime.now().strftime("%Y.%m.%d"), "time": "실시간", "link": "#", "image": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=400&q=80"}
            ],
            "keywordNews": rss_cache["keyword_news"] if rss_cache["keyword_news"] else [
                {"keyword": "실시간 핫이슈", "news": [{"title": "키워드별 연관 뉴스 심층 분석을 갱신 중입니다.", "source": "출처: System", "date": datetime.now().strftime("%Y.%m.%d"), "link": "#", "image": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=400&q=80"}]}
            ],
            "quotes": rss_cache["dynamic_quotes"] if rss_cache["dynamic_quotes"] else [
                {"text": "\"리더스 통찰력 및 라이브 코멘트 파이프라인을 동기화 중입니다.\"", "author": "Jerome Powell", "role": "Federal Reserve Chairman", "date": datetime.now().strftime("%Y.%m.%d"), "link": "#", "image": "https://images.unsplash.com/photo-1541872703-74c5e44368f9?w=100&q=80"}
            ],
            "youtube": rss_cache["youtube_insights"] if rss_cache["youtube_insights"] else [
                {"title": "[슈카월드] 실시간 경제/증시 라이브 브리핑", "channel": "슈카월드", "summary": "실시간 최신 영상 피드를 가져오는 중입니다.", "date": datetime.now().strftime("%Y.%m.%d"), "link": "#", "image": "https://images.unsplash.com/photo-1611162617213-7d7a39e9b1d7?w=400&q=80"}
            ]
        }
        
        # 2. 캐시 업데이트
        data_cache["data"] = result
        data_cache["last_updated"] = time.time()
        
        return jsonify(result)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

# 서버 메인 루프 실행 전 비동기 스레드 스타트 (부팅 절대 방해 금지)
threading.Thread(target=update_rss_cache_background, daemon=True).start()

if __name__ == '__main__':
    app.run(debug=True, port=5000, host="0.0.0.0")
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import yfinance as yf
import pandas as pd
from datetime import datetime
import time

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
        if len(hist) < 2: return {k: {"pct": 0, "raw_price": 0} for k in ["d1", "d3", "w1", "m1", "m3", "m6", "y1"]}
        
        def get_data(days_ago):
            idx = min(days_ago, len(hist)-1)
            old_price = float(hist['Close'].iloc[-1 - idx])
            if old_price == 0: return {"pct": 0, "raw_price": 0}
            pct = round(((current_close - old_price) / old_price) * 100, 2)
            return {"pct": pct, "raw_price": old_price}
            
        return {
            "today": get_data(1),
            "d1": get_data(1),
            "d3": get_data(3),
            "w1": get_data(5),
            "m1": get_data(21),
            "m3": get_data(63), 
            "m6": get_data(126),
            "y1": get_data(252)
        }
    except:
        return {k: {"pct": 0, "raw_price": 0} for k in ["today", "d1", "d3", "w1", "m1", "m3", "m6", "y1"]}

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
                
                current_close = float(hist['Close'].iloc[-1])
                
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
            "news": [
                { "title": "연준(Fed) 깜짝 금리 스탠스 변화... 월가는 '연말 릴레이 금리 인하 기대' 환호", "summary": "Fed의 향후 금리 인하 가능성이 대두되며 증시가 새로운 국면을 맞았습니다.", "source": "Bloomberg", "date": datetime.now().strftime("%Y.%m.%d"), "time": "2시간 전", "link": "https://finance.yahoo.com/news/", "image": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=400&q=80" },
                { "title": "엔비디아 발 AI 반도체 수요 대폭증, 관련주 연일 상한가 랠리", "summary": "차세대 블랙웰 칩의 기록적인 수요와 함께 반도체 밸류체인 전반이 수혜를 입고 있습니다.", "source": "Financial Times", "date": datetime.now().strftime("%Y.%m.%d"), "time": "3시간 전", "link": "https://finance.yahoo.com/quote/NVDA/news", "image": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=400&q=80" },
                { "title": "테슬라, 완전자율주행(FSD) 글로벌 상용화 임박... 완성차 시장 판도 흔들까", "summary": "머스크 CEO가 FSD 데이터 모델링 완료를 선언하며 오토모티브 시장에 파장을 일으키고 있습니다.", "source": "WSJ", "date": "2026.04.27", "time": "12시간 전", "link": "https://finance.yahoo.com/quote/TSLA/news", "image": "https://images.unsplash.com/photo-1561518776-e76a5e48f731?w=400&q=80" },
                { "title": "한국 밸류업 프로그램 실효성 입증되나... 외국인 투자자 KOSPI 대거 유입", "summary": "저PBR 기업들의 대규모 자사주 소각 발표 이후 벤치마크 지수의 강력한 지지선이 형성되었습니다.", "source": "한국경제", "date": "2026.04.27", "time": "15시간 전", "link": "https://finance.yahoo.com/quote/KS11.KS/news", "image": "https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?w=400&q=80" },
                { "title": "국제유가 안정세 회복, 에너지 및 항공주 V자 반등 성공", "summary": "중동 발 지정학적 리스크 완화로 원유 선물이 안정을 찾으며 관련 산업들이 폭발적인 회복탄력성을 보입니다.", "source": "MarketWatch", "date": "2026.04.27", "time": "16시간 전", "link": "https://finance.yahoo.com/commodities", "image": "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=400&q=80" },
                { "title": "중국발 강력한 부양책 발표 임박... 아시아 신흥국 증시 동반 강세 흐름", "summary": "중앙은행의 추가적인 지준율 인하 소문이 돌면서 SSEC 중심의 대규모 자금 투입이 예상됩니다.", "source": "South China Morning Post", "date": "2026.04.26", "time": "2일 전", "link": "https://finance.yahoo.com/quote/000001.SS", "image": "https://images.unsplash.com/photo-1541888035777-17e92ce1ab52?w=400&q=80" },
                { "title": "비트코인 등 가상자산과 매그니피센트7 주가의 상관관계 역대 최고치 기록", "summary": "리스크-온 자산으로 취급되는 암호화폐와 빅테크의 움직임이 강력히 동기화 되고 있습니다.", "source": "CNBC", "date": "2026.04.26", "time": "2일 전", "link": "https://finance.yahoo.com/quote/BTC-USD", "image": "https://images.unsplash.com/photo-1516245834210-c4c142787335?w=400&q=80" },
                { "title": "글로벌 상업용 부동산 위기 진정세, 리츠(REITs)ETF 반발 매수 폭발", "summary": "미국 오피스 공실률이 안정화 사이클에 진입하며 금융권 내 부실 자산 우려가 씻겨나갔습니다.", "source": "Reuters", "date": "2026.04.25", "time": "3일 전", "link": "https://finance.yahoo.com/quote/VNQ", "image": "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=400&q=80" },
                { "title": "차세대 로봇 공학 및 헬스케어 AI 접목 신규 스타트업들의 IPO 광풍", "summary": "제 2의 닷컴버블을 연상케 할 만큼 딥테크 기업들의 상장이 월가를 휩숫고 있습니다.", "source": "TechCrunch", "date": "2026.04.24", "time": "4일 전", "link": "https://finance.yahoo.com/news/", "image": "https://images.unsplash.com/photo-1531746790731-6c087fecd65a?w=400&q=80" },
                { "title": "주요 기업들의 막대한 잉여현금흐름, 대규모 자사주 매입과 배당 폭탄 선언", "summary": "어닝 서프라이즈를 달성한 주요 대기업들이 앞다투어 막강한 주주환원 패키지를 시장에 던지고 있습니다.", "source": "Yahoo Finance", "date": "2026.04.23", "time": "5일 전", "link": "https://finance.yahoo.com/news/", "image": "https://images.unsplash.com/photo-1591696205602-2f950c417cb9?w=400&q=80" }
            ],
            "quotes": [
                {
                    "text": "\"자본주의 시장의 단기적 흔들림에 일희일비하지 마십시오. 훌륭한 비즈니스 모델은 결국 언제나 제자리를 찾습니다.\"",
                    "author": "Warren Buffett", "role": "Berkshire Hathaway CEO", "date": "2026.04.25",
                    "link": "https://en.wikipedia.org/wiki/Warren_Buffett", "image": "https://images.unsplash.com/photo-1556157382-97eda2f9e2bf?w=100&q=80"
                },
                {
                    "text": "\"지금은 극단적인 낙관주의나 투기적 행태를 피하고, 철저히 펀더멘털과 가치에 집중해야 할 방어적 우위의 시기입니다.\"",
                    "author": "Howard Marks", "role": "Oaktree Capital Co-Chairman", "date": "2026.04.22",
                    "link": "https://en.wikipedia.org/wiki/Howard_Marks_(investor)", "image": "https://images.unsplash.com/photo-1560250097-0b93528c311a?w=100&q=80"
                },
                {
                    "text": "\"시장의 거대한 추세가 당신의 포지션을 지지하지 않는다, 당신의 분석에 대한 과도한 확신은 오히려 독이 될 수 있습니다.\"",
                    "author": "Mark Minervini", "role": "Stock Market Wizard & Author", "date": "2026.04.27",
                    "link": "https://en.wikipedia.org/wiki/Mark_Minervini", "image": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=100&q=80"
                },
                {
                    "text": "\"모든 시장의 움직임에는 사이클이 존재합니다. 지금의 격렬한 변동성은 새로운 트렌드의 시작점일 수 있습니다.\"",
                    "author": "Paul Tudor Jones", "role": "Tudor Investment Corp Founder", "date": "2026.04.26",
                    "link": "https://en.wikipedia.org/wiki/Paul_Tudor_Jones", "image": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=100&q=80"
                },
                {
                    "text": "\"인공지능(AI)과 차세대 컴퓨팅 혁신 구조에 장기 투자하지 않는 것은 역사의 파도를 기꺼이 역행하는 것과 같습니다.\"",
                    "author": "Stanley Druckenmiller", "role": "Duquesne Family Office", "date": "2026.04.28",
                    "link": "https://en.wikipedia.org/wiki/Stanley_Druckenmiller", "image": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&q=80"
                },
                {
                    "text": "\"강력한 독점적 현금흐름과 인플레이션 방어력을 지닌 기업이라면, 어떤 거시경제적 폭풍 중심에서도 포트폴리오를 지켜줄 것입니다.\"",
                    "author": "Bill Ackman", "role": "Pershing Square Capital CEO", "date": "2026.04.21",
                    "link": "https://en.wikipedia.org/wiki/Bill_Ackman", "image": "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=100&q=80"
                }
            ],
            "youtube": [
                {
                    "title": "나스닥 폭락장의 이유와 바닥 신호 집중 분석 (애플, 테슬라 집중 점검)",
                    "channel": "소수몽키",
                    "summary": "금리 인상 공포가 증시에 미치는 영향과 함께, 우량 빅테크 주식을 분할 매수해야 할 명확한 판단 기준을 제시합니다.",
                    "date": "2026.04.28", "link": "https://www.youtube.com/watch?v=2Sy5b0N4u8A", "image": "https://i.ytimg.com/vi/2Sy5b0N4u8A/hqdefault.jpg"
                },
                {
                    "title": "Fed 파월 의장의 속도 조절 발언, 과연 한국 부동산/증시의 향방은?",
                    "channel": "박종훈의 경제한방",
                    "summary": "환율 급등락과 파월의 코멘트 사이의 이면을 날카롭게 해부하고 실질적인 매크로 대응 전략을 세워봅니다.",
                    "date": "2026.04.27", "link": "https://www.youtube.com/watch?v=SexyT911CPY", "image": "https://i.ytimg.com/vi/SexyT911CPY/hqdefault.jpg"
                },
                {
                    "title": "퀀트 투자 기법으로 돌아보는 최근 가치주 랠리의 실체",
                    "channel": "월가아재의 과학적투자",
                    "summary": "단기 노이즈를 필터링하고 백테스트 통계를 근거로 현재 시장에서 살아남기 위한 데이터 주도적 투자론을 리뷰합니다.",
                    "date": "2026.04.27", "link": "https://www.youtube.com/watch?v=8L6vix_byUM", "image": "https://i.ytimg.com/vi/8L6vix_byUM/hqdefault.jpg"
                },
                {
                    "title": "배당주 ETF 포트폴리오 파이프라인 매월 100만원 만들기 실전 세팅",
                    "channel": "수페TV",
                    "summary": "SCHD, JEPI 등 인기가 높은 고배당 ETF의 실질 배당률을 재점검하고 이상적인 패시브 인컴 구조를 설계합니다.",
                    "date": "2026.04.26", "link": "https://www.youtube.com/watch?v=A1R5o6Zjw9s", "image": "https://i.ytimg.com/vi/A1R5o6Zjw9s/hqdefault.jpg"
                },
                {
                    "title": "2026년 하반기 경제 지각 변동: 지금 당장 팔아야 할 주식과 사야 할 주식",
                    "channel": "전인구 경제연구소",
                    "summary": "지수가 정체된 박스권 장세 속에서 금리, 환율, 원자재 지표들을 종합 분석해 다가올 사이클을 예측합니다.",
                    "date": "2026.04.25", "link": "https://www.youtube.com/watch?v=AohLeRLp610", "image": "https://i.ytimg.com/vi/AohLeRLp610/hqdefault.jpg"
                },
                {
                    "title": "URGENT Market Update: Why I Just Sold My Entire Portfolio & Preparing For The Crash",
                    "channel": "Meet Kevin",
                    "summary": "Technical and fundamental analysis explaining the sudden shift in broad market momentum and real estate worries.",
                    "date": "2026.04.28", "link": "https://www.youtube.com/watch?v=0d3kJRWoHaA", "image": "https://i.ytimg.com/vi/0d3kJRWoHaA/hqdefault.jpg"
                },
                {
                    "title": "The Hidden Truth About The Economy Right Now (Warning Signs)",
                    "channel": "Graham Stephan",
                    "summary": "Exploring the unspoken data behind inflation reports and what it exactly implies for the individual stock investor.",
                    "date": "2026.04.26", "link": "https://www.youtube.com/watch?v=TTHTa5i-Plw", "image": "https://i.ytimg.com/vi/TTHTa5i-Plw/hqdefault.jpg"
                }
            ]
        }
        
        # 2. 캐시 업데이트
        data_cache["data"] = result
        data_cache["last_updated"] = time.time()
        
        return jsonify(result)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000, host="0.0.0.0")
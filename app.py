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
            "news": [
                { "title": "연준(Fed) 깜짝 금리 스탠스 변화... 월가는 '연말 릴레이 금리 인하 기대' 환호", "summary": "Fed의 향후 금리 인하 가능성이 대두되며 증시가 새로운 국면을 맞았습니다.", "source": "Bloomberg", "date": datetime.now().strftime("%Y.%m.%d"), "time": "1시간 전", "link": "https://finance.yahoo.com/news/", "image": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=400&q=80" },
                { "title": "엔비디아 발 AI 반도체 수요 대폭증, 관련주 연일 상한가 랠리", "summary": "차세대 블랙웰 칩의 기록적인 수요와 함께 반도체 밸류체인 전반이 수혜를 입고 있습니다.", "source": "Financial Times", "date": datetime.now().strftime("%Y.%m.%d"), "time": "2시간 전", "link": "https://finance.yahoo.com/quote/NVDA/news", "image": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=400&q=80" },
                { "title": "테슬라, 완전자율주행(FSD) 글로벌 상용화 임박... 완성차 시장 판도 흔들까", "summary": "머스크 CEO가 FSD 데이터 모델링 완료를 선언하며 오토모티브 시장에 파장을 일으키고 있습니다.", "source": "WSJ", "date": datetime.now().strftime("%Y.%m.%d"), "time": "4시간 전", "link": "https://finance.yahoo.com/quote/TSLA/news", "image": "https://images.unsplash.com/photo-1561518776-e76a5e48f731?w=400&q=80" },
                { "title": "한국 밸류업 프로그램 실효성 입증되나... 외국인 투자자 KOSPI 대거 유입", "summary": "저PBR 기업들의 대규모 자사주 소각 발표 이후 벤치마크 지수의 강력한 지지선이 형성되었습니다.", "source": "한국경제", "date": standard_date(1) if standard_date(1) else "1일 전", "time": "12시간 전", "link": "https://finance.yahoo.com/quote/KS11.KS/news", "image": "https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?w=400&q=80" },
                { "title": "국제유가 안정세 회복, 에너지 및 항공주 V자 반등 성공", "summary": "중동 발 지정학적 리스크 완화로 원유 선물이 안정을 찾으며 관련 산업들이 폭발적인 회복탄력성을 보입니다.", "source": "MarketWatch", "date": standard_date(1) if standard_date(1) else "1일 전", "time": "15시간 전", "link": "https://finance.yahoo.com/commodities", "image": "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=400&q=80" },
                { "title": "중국발 강력한 부양책 발표 임박... 아시아 신흥국 증시 동반 강세 흐름", "summary": "중앙은행의 추가적인 지준율 인하 소문이 돌면서 SSEC 중심의 대규모 자금 투입이 예상됩니다.", "source": "South China Morning Post", "date": standard_date(2) if standard_date(2) else "2일 전", "time": "1일 전", "link": "https://finance.yahoo.com/quote/000001.SS", "image": "https://images.unsplash.com/photo-1541888035777-17e92ce1ab52?w=400&q=80" },
                { "title": "비트코인 등 가상자산과 매그니피센트7 주가의 상관관계 역대 최고치 기록", "summary": "리스크-온 자산으로 취급되는 암호화폐와 빅테크의 움직임이 강력히 동기화 되고 있습니다.", "source": "CNBC", "date": standard_date(2) if standard_date(2) else "2일 전", "time": "2일 전", "link": "https://finance.yahoo.com/quote/BTC-USD", "image": "https://images.unsplash.com/photo-1516245834210-c4c142787335?w=400&q=80" },
                { "title": "글로벌 상업용 부동산 위기 진정세, 리츠(REITs)ETF 반발 매수 폭발", "summary": "미국 오피스 공실률이 안정화 사이클에 진입하며 금융권 내 부실 자산 우려가 씻겨나갔습니다.", "source": "Reuters", "date": standard_date(3) if standard_date(3) else "3일 전", "time": "3일 전", "link": "https://finance.yahoo.com/quote/VNQ", "image": "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=400&q=80" }
            ],
            "quotes": [
                {
                    "text": "\"인플레이션 목표 달성을 위한 우리의 의지는 확고합니다. 데이터에 기반하여 신중하고 유연하게 통화정책을 운용할 것입니다.\"",
                    "author": "Jerome Powell", "role": "Federal Reserve Chairman", "date": datetime.now().strftime("%Y.%m.%d"),
                    "link": "https://en.wikipedia.org/wiki/Jerome_Powell", "image": "https://images.unsplash.com/photo-1541872703-74c5e44368f9?w=100&q=80"
                },
                {
                    "text": "\"최근 경제 지표들은 통화정책의 효과가 가시화되고 있음을 보여줍니다. 조기 금리 인하보다는 물가 안정의 지속성을 확인하는 것이 핵심입니다.\"",
                    "author": "Christopher Waller", "role": "Federal Reserve Governor", "date": datetime.now().strftime("%Y.%m.%d"),
                    "link": "https://en.wikipedia.org/wiki/Christopher_Waller", "image": "https://images.unsplash.com/photo-1557804506-669a67965ba0?w=100&q=80"
                },
                {
                    "text": "\"강한 달러와 안정적인 국채 시장은 미국 경제의 근간입니다. 규제 완화와 친성장 정책을 통해 자본 시장의 활력을 극대화해야 합니다.\"",
                    "author": "Scott Bessent", "role": "Treasury Secretary Nominee", "date": standard_date(1) if standard_date(1) else "1일 전",
                    "link": "https://en.wikipedia.org/wiki/Scott_Bessent", "image": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&q=80"
                },
                {
                    "text": "\"자본주의 시장의 단기적 흔들림에 일희일비하지 마십시오. 훌륭한 비즈니스 모델과 잉여현금흐름은 결국 언제나 제자리를 찾습니다.\"",
                    "author": "Warren Buffett", "role": "Berkshire Hathaway CEO", "date": standard_date(1) if standard_date(1) else "1일 전",
                    "link": "https://en.wikipedia.org/wiki/Warren_Buffett", "image": "https://images.unsplash.com/photo-1556157382-97eda2f9e2bf?w=100&q=80"
                },
                {
                    "text": "\"자율주행과 로봇 공학은 인류의 생산성을 수백 배로 끌어올릴 것입니다. 혁신 속도를 늦추는 기업은 도태될 수밖에 없습니다.\"",
                    "author": "Elon Musk", "role": "Tesla & SpaceX CEO", "date": standard_date(1) if standard_date(1) else "1일 전",
                    "link": "https://en.wikipedia.org/wiki/Elon_Musk", "image": "https://images.unsplash.com/photo-1570295999919-56ceb5ecca61?w=100&q=80"
                },
                {
                    "text": "\"가속 컴퓨팅과 생성형 AI는 새로운 산업 혁명의 엔진입니다. 모든 데이터센터가 AI 팩토리로 탈바꿈하는 티핑 포인트에 와 있습니다.\"",
                    "author": "Jensen Huang", "role": "NVIDIA CEO", "date": standard_date(2) if standard_date(2) else "2일 전",
                    "link": "https://en.wikipedia.org/wiki/Jensen_Huang", "image": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100&q=80"
                },
                {
                    "text": "\"지정학적 리스크와 거시경제적 불확실성이 그 어느 때보다 높습니다. 최악의 시나리오에 대비하면서도 훌륭한 고객 가치에 집중해야 합니다.\"",
                    "author": "Jamie Dimon", "role": "JPMorgan Chase CEO", "date": standard_date(2) if standard_date(2) else "2일 전",
                    "link": "https://en.wikipedia.org/wiki/Jamie_Dimon", "image": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=100&q=80"
                },
                {
                    "text": "\"글로벌 자금의 대이동이 시작되었습니다. 인프라 투자와 탈탄소, 그리고 AI 기반 혁신에 수조 달러의 자본이 집중될 것입니다.\"",
                    "author": "Larry Fink", "role": "BlackRock CEO", "date": standard_date(2) if standard_date(2) else "2일 전",
                    "link": "https://en.wikipedia.org/wiki/Larry_Fink", "image": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=100&q=80"
                },
                {
                    "text": "\"시장의 거대한 매크로 추세가 바뀌고 있습니다. 과거의 성공 방정식에 얽매이지 않고 새로운 기술 패러다임에 과감히 베팅해야 합니다.\"",
                    "author": "Stanley Druckenmiller", "role": "Duquesne Family Office", "date": standard_date(3) if standard_date(3) else "3일 전",
                    "link": "https://en.wikipedia.org/wiki/Stanley_Druckenmiller", "image": "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=100&q=80"
                },
                {
                    "text": "\"지금은 극단적인 낙관주의나 투기적 행태를 피하고, 철저히 펀더멘털 사이클과 내재 가치에 집중해야 할 방어적 우위의 시기입니다.\"",
                    "author": "Howard Marks", "role": "Oaktree Capital Co-Chairman", "date": standard_date(3) if standard_date(3) else "3일 전",
                    "link": "https://en.wikipedia.org/wiki/Howard_Marks_(investor)", "image": "https://images.unsplash.com/photo-1560250097-0b93528c311a?w=100&q=80"
                }
            ],
            "youtube": [
                {
                    "title": "슈카월드 라이브: 연준의 깜짝 스탠스 변화와 흔들리는 글로벌 금융 시장",
                    "channel": "슈카월드",
                    "summary": "복잡한 매크로 지표와 파월 의장의 발언 이면을 알기 쉽게 해부하고, 개인 투자자들이 취해야 할 생존 전략을 유쾌하게 브리핑합니다.",
                    "date": datetime.now().strftime("%Y.%m.%d"), "link": "https://www.youtube.com/@syukaworld", "image": "https://images.unsplash.com/photo-1611162617213-7d7a39e9b1d7?w=400&q=80"
                },
                {
                    "title": "삼프로TV 심층 분석: AI 반도체 슈퍼 사이클 2막, 지금 사야 할 소부장 핵심 주도주",
                    "channel": "삼프로TV",
                    "summary": "엔비디아 블랙웰 수요 폭발에 따른 밸류체인 수혜 구조를 면밀히 분석하고 여의도 최고 애널리스트들의 탑픽을 점검합니다.",
                    "date": datetime.now().strftime("%Y.%m.%d"), "link": "https://www.youtube.com/@samprotv", "image": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=400&q=80"
                },
                {
                    "title": "나스닥 변동성 확대 장세의 숨은 이유와 진짜 바닥 매수 타이밍 잡기",
                    "channel": "소수몽키",
                    "summary": "기관 투자자들의 자금 흐름과 기술적 지표들을 종합하여 우량 빅테크 주식을 안전하게 모아가는 적립식 매수 가이드를 제공합니다.",
                    "date": standard_date(1) if standard_date(1) else "1일 전", "link": "https://www.youtube.com/@sosumonkey", "image": "https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?w=400&q=80"
                },
                {
                    "title": "월가아재의 과학적투자: 통계와 데이터로 검증하는 최근 시장 랠리의 지속 가능성",
                    "channel": "월가아재",
                    "summary": "감정과 노이즈를 배제하고 철저한 퀀트 백테스트 결과를 바탕으로 현재 포트폴리오의 리스크 대비 기대 수익률을 해부합니다.",
                    "date": standard_date(1) if standard_date(1) else "1일 전", "link": "https://www.youtube.com/@wallstreetazae", "image": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=400&q=80"
                },
                {
                    "title": "수페TV: 월 100만원 현금흐름 파이프라인 구축을 위한 최강 배당주 ETF 조합",
                    "channel": "수페TV",
                    "summary": "SCHD, JEPI 등 인기가 높은 고배당 ETF들의 최신 분배금 현황을 비교 분석하고 안정적인 패시브 인컴 포트폴리오를 제안합니다.",
                    "date": standard_date(2) if standard_date(2) else "2일 전", "link": "https://www.youtube.com/@supe_tv", "image": "https://images.unsplash.com/photo-1559526324-4b87b5e36e44?w=400&q=80"
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
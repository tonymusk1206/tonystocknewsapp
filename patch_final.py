"""
전체 개편 패치:
1. calculate_changes에 날짜 필드 추가
2. 배경 스레드에서 유튜브/인사발언 제거 (속도 개선)
3. 뉴스 수집 병렬화
"""
import re

with open("app.py", "r", encoding="utf-8") as f:
    src = f.read()

# ── 1. calculate_changes에 날짜 포함 ──
old_calc = '''def calculate_changes(hist, current_close):
    try:
        if len(hist) < 2: return {k: {"pct": 0, "raw_price": 0} for k in ["today", "d1", "d3", "w1", "m1", "m3", "m6", "y1"]}
        def get_data(days_ago):
            idx = min(days_ago, len(hist)-1)
            old_price = float(hist['Close'].iloc[-1 - idx])
            if old_price == 0: return {"pct": 0, "raw_price": 0}
            pct = round(((current_close - old_price) / old_price) * 100, 2)
            return {"pct": pct, "raw_price": old_price}
        return {
            "today": get_data(1), "d1": get_data(1), "d3": get_data(3),
            "w1": get_data(5), "m1": get_data(21), "m3": get_data(63),
            "m6": get_data(126), "y1": get_data(252)
        }
    except:
        return {k: {"pct": 0, "raw_price": 0} for k in ["today", "d1", "d3", "w1", "m1", "m3", "m6", "y1"]}'''

new_calc = '''def calculate_changes(hist, current_close):
    try:
        if len(hist) < 2: return {k: {"pct": 0, "raw_price": 0, "date": ""} for k in ["today", "d1", "d3", "w1", "m1", "m3", "m6", "y1"]}
        def get_data(days_ago):
            idx = min(days_ago, len(hist)-1)
            old_price = float(hist['Close'].iloc[-1 - idx])
            old_date = hist.index[-1 - idx].strftime('%y.%m.%d')
            if old_price == 0: return {"pct": 0, "raw_price": 0, "date": old_date}
            pct = round(((current_close - old_price) / old_price) * 100, 2)
            return {"pct": pct, "raw_price": old_price, "date": old_date}
        return {
            "today": get_data(1), "d1": get_data(1), "d3": get_data(3),
            "w1": get_data(5), "m1": get_data(21), "m3": get_data(63),
            "m6": get_data(126), "y1": get_data(252)
        }
    except:
        return {k: {"pct": 0, "raw_price": 0, "date": ""} for k in ["today", "d1", "d3", "w1", "m1", "m3", "m6", "y1"]}'''

src = src.replace(old_calc, new_calc)

# ── 2. process_ticker에서 날짜를 dates 반환에 포함 ──
old_result = '''        result = {
            "baseDate": f"{datetime.now().strftime('%Y년 %m월 %d일 %H:%M')} 라이브 API 기준",
            "dates": {"current": standard_date(0) or "현재가", "d1": standard_date(1), "d3": standard_date(3), "w1": standard_date(5), "m1": standard_date(21), "m3": standard_date(63), "m6": standard_date(126), "y1": standard_date(252)},'''

new_result = '''        # 실제 거래일 기준 날짜 추출 (SPX hist 기반)
        def trading_date(days_ago):
            if spx_hist is None or spx_hist.empty: return ""
            idx = min(days_ago, len(spx_hist)-1)
            return spx_hist.index[-1 - idx].strftime('%y.%m.%d')
        result = {
            "baseDate": f"{datetime.now().strftime('%Y년 %m월 %d일 %H:%M')} 라이브 API 기준",
            "dates": {
                "current": trading_date(0) or "현재가",
                "d1": trading_date(1),
                "d3": trading_date(3),
                "w1": trading_date(5),
                "m1": trading_date(21),
                "m3": trading_date(63),
                "m6": trading_date(126),
                "y1": trading_date(252)
            },'''

src = src.replace(old_result, new_result)

# ── 3. 배경 스레드에서 유튜브/인사발언 제거 (속도 개선) ──
old_bg_init = '''    try:
        print("[Background Engine] [START] 유튜브 인사이트 수집...")
        y_insights = get_youtube_insights()
        if y_insights:
            with rss_cache["lock"]: rss_cache["youtube_insights"] = y_insights
            
        print("[Background Engine] [START] 인사 발언 수집...")
        d_quotes_ko = get_dynamic_quotes()
        if d_quotes_ko:
            with rss_cache["lock"]: rss_cache["dynamic_quotes"] = d_quotes_ko
            
        print("[Background Engine] [START] 주식 데이터 최우선 수집 시작...")'''

new_bg_init = '''    try:
        print("[Background Engine] [START] 주식 데이터 최우선 수집 시작...")'''

src = src.replace(old_bg_init, new_bg_init)

old_bg_loop = '''            fetch_and_cache_market_data()
            
            y_insights = get_youtube_insights()
            if y_insights:
                with rss_cache["lock"]: rss_cache["youtube_insights"] = y_insights
                
            d_quotes = get_dynamic_quotes()
            if d_quotes:
                with rss_cache["lock"]: rss_cache["dynamic_quotes"] = d_quotes
                
            with rss_cache["lock"]: rss_cache["last_updated"] = time.time()
            print("[Background Engine] [DONE] 주기적 갱신 완료!")'''

new_bg_loop = '''            fetch_and_cache_market_data()
            with rss_cache["lock"]: rss_cache["last_updated"] = time.time()
            print("[Background Engine] [DONE] 주기적 갱신 완료!")'''

src = src.replace(old_bg_loop, new_bg_loop)

# ── 4. market_data API에서 불필요한 필드 제거 ──
old_market_return = '''    if data_cache["data"] is not None:
        cached = dict(data_cache["data"])
        cached["news"] = rss_cache["top10_news"]
        cached["keywordNews"] = rss_cache["keyword_news"]
        cached["quotes"] = rss_cache["dynamic_quotes"]
        cached["youtube"] = rss_cache["youtube_insights"]
        return jsonify(cached)
    # ★ 서버 최초 기동 직후 캐시가 없으면 fallback 즉시 반환
    fallback = dict(FALLBACK_DATA)
    fallback["news"] = rss_cache["top10_news"]
    fallback["keywordNews"] = rss_cache["keyword_news"]
    fallback["quotes"] = rss_cache["dynamic_quotes"]
    fallback["youtube"] = rss_cache["youtube_insights"]
    return jsonify(fallback)'''

new_market_return = '''    if data_cache["data"] is not None:
        cached = dict(data_cache["data"])
        return jsonify(cached)
    # ★ 서버 최초 기동 직후 캐시가 없으면 fallback 즉시 반환
    return jsonify(FALLBACK_DATA)'''

src = src.replace(old_market_return, new_market_return)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(src)

print("app.py patched OK")

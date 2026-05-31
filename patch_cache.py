import re

with open("app.py", "r", encoding="utf-8") as f:
    text = f.read()

# 1. Insert imports and cache loading logic
startup_logic = """    "last_updated": time.time(),
    "lock": threading.Lock()
}

CACHE_FILE = "market_cache.json"
import os

if os.path.exists(CACHE_FILE):
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            cache_data = json.load(f)
            data_cache["data"] = cache_data.get("market_data")
            data_cache["last_updated"] = os.path.getmtime(CACHE_FILE)
            if "rss_data" in cache_data:
                rss_cache.update(cache_data["rss_data"])
            print("[Startup] Loaded all data from local cache file.")
    except Exception as e:
        print(f"[Startup] Error loading cache file: {e}")

import pytz

def is_any_market_open():
    try:
        now_utc = datetime.now(pytz.utc)
        
        # US Market (09:30 to 16:00 ET, Mon-Fri)
        et_tz = pytz.timezone('US/Eastern')
        now_et = now_utc.astimezone(et_tz)
        us_open = False
        if now_et.weekday() < 5:
            if datetime.strptime("09:30", "%H:%M").time() <= now_et.time() <= datetime.strptime("16:00", "%H:%M").time():
                us_open = True

        # KR Market (09:00 to 15:30 KST, Mon-Fri)
        kst_tz = pytz.timezone('Asia/Seoul')
        now_kst = now_utc.astimezone(kst_tz)
        kr_open = False
        if now_kst.weekday() < 5:
            if datetime.strptime("09:00", "%H:%M").time() <= now_kst.time() <= datetime.strptime("15:30", "%H:%M").time():
                kr_open = True

        return us_open or kr_open
    except Exception as e:
        print("Error checking market hours:", e)
        return True # Default to fetching if error

"""
text = text.replace("""    "last_updated": time.time(),
    "lock": threading.Lock()
}""", startup_logic)


# 2. Update initial fetch logic in update_rss_cache_background
old_initial_fetch = """        print("[Background Engine] [START] 시장 데이터 최우선 로딩 시작...")
        fetch_and_cache_market_data()
        print("[Background Engine] [DONE] 시장 데이터 로딩 완료!")
            
        with rss_cache["lock"]: rss_cache["last_updated"] = time.time()
        print("[Background Engine] [DONE] 초기 업데이트 모두 완료!")
    except Exception as e:
        print(f"[Background Engine] [ERROR] 초기 업데이트 오류: {e}")"""

new_initial_fetch = """        print("[Background Engine] [START] 시장 데이터 최우선 로딩 시작...")
        if data_cache["data"] is None or is_any_market_open():
            fetch_and_cache_market_data()
            print("[Background Engine] [DONE] 시장 데이터 로딩 완료!")
        else:
            print("[Background Engine] 시장이 닫혀있고 로컬 캐시가 존재하므로 초기 1회 로딩을 건너뜁니다.")
            
        with rss_cache["lock"]: rss_cache["last_updated"] = time.time()
        print("[Background Engine] [DONE] 초기 업데이트 모두 완료!")

        if data_cache["data"] is not None:
            cache_data = {
                "market_data": data_cache["data"],
                "rss_data": {
                    "top10_news": rss_cache["top10_news"],
                    "keyword_news": rss_cache["keyword_news"],
                    "youtube_insights": rss_cache["youtube_insights"],
                    "dynamic_quotes": rss_cache["dynamic_quotes"]
                }
            }
            try:
                with open(CACHE_FILE, "w", encoding="utf-8") as f:
                    json.dump(cache_data, f, ensure_ascii=False)
            except Exception as e:
                print(f"[Background Engine] Cache write error: {e}")

    except Exception as e:
        print(f"[Background Engine] [ERROR] 초기 업데이트 오류: {e}")"""
text = text.replace(old_initial_fetch, new_initial_fetch)


# 3. Update loop fetch logic in update_rss_cache_background
old_loop_fetch = """            print("[Background Engine] [START] 주기적 RSS/시장 데이터 업데이트...")
            fetch_and_cache_market_data()
            
            y_insights = get_youtube_insights()
            if y_insights:
                with rss_cache["lock"]: rss_cache["youtube_insights"] = y_insights
                
            d_quotes = get_dynamic_quotes()
            if d_quotes:
                with rss_cache["lock"]: rss_cache["dynamic_quotes"] = d_quotes
                
            with rss_cache["lock"]: rss_cache["last_updated"] = time.time()
            print("[Background Engine] [DONE] 주기적 업데이트 완료!")"""

new_loop_fetch = """            print("[Background Engine] [START] 주기적 RSS/시장 데이터 업데이트...")
            if data_cache["data"] is not None and not is_any_market_open():
                print("[Background Engine] 시장이 모두 닫혀있어 시장 데이터 업데이트를 건너뜁니다.")
            else:
                fetch_and_cache_market_data()
            
            y_insights = get_youtube_insights()
            if y_insights:
                with rss_cache["lock"]: rss_cache["youtube_insights"] = y_insights
                
            d_quotes = get_dynamic_quotes()
            if d_quotes:
                with rss_cache["lock"]: rss_cache["dynamic_quotes"] = d_quotes
                
            with rss_cache["lock"]: rss_cache["last_updated"] = time.time()
            print("[Background Engine] [DONE] 주기적 업데이트 완료!")
            
            if data_cache["data"] is not None:
                cache_data = {
                    "market_data": data_cache["data"],
                    "rss_data": {
                        "top10_news": rss_cache["top10_news"],
                        "keyword_news": rss_cache["keyword_news"],
                        "youtube_insights": rss_cache["youtube_insights"],
                        "dynamic_quotes": rss_cache["dynamic_quotes"]
                    }
                }
                try:
                    with open(CACHE_FILE, "w", encoding="utf-8") as f:
                        json.dump(cache_data, f, ensure_ascii=False)
                except Exception as e:
                    print(f"[Background Engine] Cache write error: {e}")"""
text = text.replace(old_loop_fetch, new_loop_fetch)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(text)

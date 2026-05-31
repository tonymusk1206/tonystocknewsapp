import re

with open("app.py", "r", encoding="utf-8") as f:
    text = f.read()

# remove the old threading start at the bottom
text = text.replace("threading.Thread(target=update_rss_cache_background, daemon=True).start()", "")

lazy_start = """
_thread_started = False

@app.route('/api/market-data')
def market_data():
    global data_cache, _thread_started
    if not _thread_started:
        _thread_started = True
        import threading
        threading.Thread(target=update_rss_cache_background, daemon=True).start()
"""

text = text.replace("@app.route('/api/market-data')\ndef market_data():\n    global data_cache", lazy_start)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(text)

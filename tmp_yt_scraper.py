import urllib.request
import re
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

channels = ["소수몽키 나스닥 테슬라 애플", "박종훈 경제한방 파월", "월가아재 퀀트 가치주", "수페TV 배당주 ETF", "전인구 경제연구소", "Meet Kevin Market Update Crash", "Graham Stephan Warning Signs"]

for q in channels:
    query = urllib.parse.quote(q)
    url = f"https://www.youtube.com/results?search_query={query}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        html = urllib.request.urlopen(req, context=ctx).read().decode('utf-8')
        video_ids = re.findall(r'"videoId":"(.*?)"', html)
        if video_ids:
            # removing duplicates preserving order
            seen = set()
            ids = [x for x in video_ids if not (x in seen or seen.add(x))]
            print(f"{q}: {ids[0]}")
        else:
            print(f"{q}: NOT FOUND")
    except Exception as e:
        print(f"{q}: ERROR {e}")

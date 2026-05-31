import urllib.request
import urllib.parse
import re

channels = [
    "월가아재의과학적투자",
    "박종훈지식한방",
    "소수몽키",
    "전인구경제연구소",
    "수페TV",
    "이효석아카데미"
]

for ch in channels:
    url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(ch)}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            html = response.read().decode('utf-8')
            match = re.search(r'"channelId":"(UC[^"]+)"', html)
            if match:
                print(ch, "->", match.group(1))
            else:
                print(ch, "-> NOT FOUND")
    except Exception as e:
        print(ch, "-> ERROR:", e)

import urllib.request
import re

channels = [
    {"name": "슈카월드", "id": "UCsJ6RuBiTVWRX156FVbeaGg"},
    {"name": "월가아재의과학적투자", "id": "UCJptR2r0YqXv1628J0pXpCw"},
    {"name": "박종훈지식한방", "id": "UC5cKPnu2NpaxKjU2UBuvVxA"},
    {"name": "소수몽키", "id": "UC_t11S41W6N6hA4FqM3Bwbw"},
    {"name": "전인구경제연구소", "id": "UCznImSIaxZR7fdLCICLdgaQ"},
    {"name": "수페TV", "id": "UCiM27z7jO8O8xntKzF6Lh1A"},
    {"name": "이효석아카데미", "id": "UCn6a15h1H1Z61K8Pj_66G-A"}
]
for ch in channels:
    url = f"https://www.youtube.com/feeds/videos.xml?channel_id={ch['id']}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            xml_data = response.read().decode('utf-8')
            if '<entry>' in xml_data:
                print(ch['name'], "SUCCESS")
            else:
                print(ch['name'], "FAILED: No entry found")
    except Exception as e:
        print(ch['name'], "ERROR:", e)

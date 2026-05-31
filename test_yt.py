import urllib.request
import re

channels = [
    {"name": "슈카월드", "id": "UCsJ6RuBiTVWRX156FVbeaGg"},
    {"name": "월가아재의과학적투자", "id": "UCJptR2r0YqXv1628J0pXpCw"}
]
for ch in channels:
    url = f"https://www.youtube.com/feeds/videos.xml?channel_id={ch['id']}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            xml_data = response.read().decode('utf-8')
            entry_match = re.search(r'<entry>(.*?)</entry>', xml_data, re.DOTALL)
            if entry_match:
                entry_text = entry_match.group(1)
                print("ENTRY TEXT FOUND")
                title_match = re.search(r'<title>(.*?)</title>', entry_text)
                title = title_match.group(1) if title_match else ""
                vid_match = re.search(r'<yt:videoId>(.*?)</yt:videoId>', entry_text)
                video_id = vid_match.group(1) if vid_match else ""
                if title and video_id:
                    print(ch['name'], "SUCCESS:", title)
                else:
                    print(ch['name'], "FAILED: No title or video_id")
            else:
                print(ch['name'], "FAILED: No entry found")
    except Exception as e:
        print(ch['name'], "ERROR:", e)

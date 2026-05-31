import urllib.request
import re
import xml.etree.ElementTree as ET

def test_youtube():
    ch_id = "UCsJ6RuBiTVWRX156FVbeaGg" # 슈카월드
    url = f"https://www.youtube.com/feeds/videos.xml?channel_id={ch_id}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = resp.read().decode('utf-8')
            print("YouTube Fetch SUCCESS, length:", len(data))
            
            entry_match = re.search(r'<entry>(.*?)</entry>', data, re.DOTALL)
            if entry_match:
                entry = entry_match.group(1)
                title = re.search(r'<title>(.*?)</title>', entry).group(1)
                print("Title:", title)
                vid = re.search(r'<yt:videoId>(.*?)</yt:videoId>', entry).group(1)
                print("Video ID:", vid)
                date = re.search(r'<published>(.*?)</published>', entry).group(1)
                print("Published:", date)
            else:
                print("No <entry> found!")
    except Exception as e:
        print("YouTube Fetch ERROR:", e)

def test_news():
    query = "Warren Buffett"
    url = f"https://news.google.com/rss/search?q={urllib.parse.quote(query)}+when:7d&hl=en-US&gl=US&ceid=US:en"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = resp.read()
            root = ET.fromstring(data.strip())
            items = root.findall('.//item')
            print("News Fetch SUCCESS, found items:", len(items))
            if items:
                print("First title:", items[0].findtext('title'))
                print("First link:", items[0].findtext('link'))
    except Exception as e:
        print("News Fetch ERROR:", e)

test_youtube()
test_news()

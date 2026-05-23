import urllib.request
import json
import re

def test_google_trends():
    print("--- Google Trends Test ---")
    url = "https://trends.google.com/trends/api/realtimetrends?hl=ko&tz=-540&cat=b&fi=0&fs=0&geo=KR&ri=300&rs=20&sort=0"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            text = response.read().decode('utf-8')
            clean_text = text.replace(")]}',\n", "")
            data = json.loads(clean_text)
            stories = data.get("storySummaries", {}).get("trendingStories", [])
            keywords = []
            for s in stories:
                # entityNames are usually the keywords
                entities = s.get("entityNames", [])
                keywords.extend(entities)
            print("Keywords KR:", keywords[:10])
    except Exception as e:
        print("Trends error:", e)

def test_youtube():
    print("--- YouTube RSS Test ---")
    channel_id = "UCsJ6RuBiTVWRX156FVbeaGg" # 슈카월드
    url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            xml_data = response.read().decode('utf-8')
            entry_match = re.search(r'<entry>(.*?)</entry>', xml_data, re.DOTALL)
            if entry_match:
                entry_text = entry_match.group(1)
                title = re.search(r'<title>(.*?)</title>', entry_text).group(1)
                video_id = re.search(r'<yt:videoId>(.*?)</yt:videoId>', entry_text).group(1)
                print(f"YouTube success: {title}, {video_id}")
            else:
                print("No entry found in YouTube RSS")
    except Exception as e:
        print("YouTube error:", e)

test_google_trends()
test_youtube()

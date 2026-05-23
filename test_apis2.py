import urllib.request
import xml.etree.ElementTree as ET

def test_google_trends_rss():
    print("--- Google Trends RSS Test ---")
    # KR doesn't have a specific Business category in daily RSS, but we can just use US business or fetch KR and filter.
    url = "https://trends.google.com/trends/trendingsearches/daily/rss?geo=KR"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            xml_data = response.read().strip()
            root = ET.fromstring(xml_data)
            keywords = []
            for item in root.findall('.//item'):
                title = item.findtext('title', '')
                if title:
                    keywords.append(title)
            print("Keywords KR Daily:", keywords[:10])
    except Exception as e:
        print("Trends error:", e)

    url_us = "https://trends.google.com/trends/trendingsearches/daily/rss?geo=US"
    req = urllib.request.Request(url_us, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            xml_data = response.read().strip()
            root = ET.fromstring(xml_data)
            keywords = []
            for item in root.findall('.//item'):
                title = item.findtext('title', '')
                if title:
                    keywords.append(title)
            print("Keywords US Daily:", keywords[:10])
    except Exception as e:
        print("Trends error:", e)

test_google_trends_rss()

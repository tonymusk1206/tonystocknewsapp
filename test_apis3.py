import urllib.request
import xml.etree.ElementTree as ET
import re
from collections import Counter

def extract_keywords_from_news():
    feeds = [
        "https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=ko&gl=KR&ceid=KR:ko",
        "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx6TVdZU0FtdHZLQUFQAQ?hl=ko&gl=KR&ceid=KR:ko",
        "https://news.google.com/rss/search?q=증시+경제+금융&hl=ko&gl=KR&ceid=KR:ko"
    ]
    
    stopwords = set(["주식", "증시", "경제", "금융", "투자", "시장", "기업", "실적", "오늘", "내일", "이번", "주가", "상승", "하락", "급등", "급락", "돌파", "마감", "코스피", "코스닥", "미국", "한국", "뉴욕", "특징주", "단독", "종합", "속보"])
    
    words = []
    
    for url in feeds:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                root = ET.fromstring(response.read().strip())
                for item in root.findall('.//item'):
                    title = item.findtext('title', '')
                    # Remove source like " - 연합뉴스"
                    if " - " in title:
                        title = title.rsplit(" - ", 1)[0]
                    # Extract words using regex
                    tokens = re.findall(r'[가-힣A-Za-z0-9]+', title)
                    for t in tokens:
                        if len(t) > 1 and t not in stopwords:
                            words.append(t)
        except Exception as e:
            pass
            
    counter = Counter(words)
    print("Top 10 Keywords:", counter.most_common(10))

extract_keywords_from_news()

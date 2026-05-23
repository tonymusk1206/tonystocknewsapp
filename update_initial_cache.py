import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

import ast

class AppModifier:
    def __init__(self, source):
        self.source = source
        self.lines = source.splitlines()

    def replace_func(self, func_name, new_code):
        start_idx = -1
        end_idx = -1
        for i, line in enumerate(self.lines):
            if line.startswith(f"def {func_name}("):
                start_idx = i
                break
        if start_idx == -1: return
        
        for i in range(start_idx + 1, len(self.lines)):
            if self.lines[i].strip() != "" and not self.lines[i].startswith(" ") and not self.lines[i].startswith("\t"):
                end_idx = i
                break
        
        if end_idx == -1:
            end_idx = len(self.lines)

        self.lines = self.lines[:start_idx] + new_code.splitlines() + self.lines[end_idx:]

    def get_code(self):
        return "\n".join(self.lines)

mod = AppModifier(content)

# remove unused fast methods
mod.replace_func("_get_news_fast", "")
mod.replace_func("_get_quotes_fast", "")

new_bg = """def update_rss_cache_background():
    global rss_cache
    time.sleep(1)  # 서버 부팅 완료 대기
    try:
        print("[Background Engine] [START] 주식 데이터 최우선 수집 시작...")
        fetch_and_cache_market_data()
        print("[Background Engine] [DONE] 주식 데이터 완료!")

        print("[Background Engine] [START] 유튜브 인사이트 수집...")
        y_insights = get_youtube_insights()
        if y_insights:
            with rss_cache["lock"]: rss_cache["youtube_insights"] = y_insights
            
        print("[Background Engine] [START] 인사 발언 수집...")
        d_quotes_ko = get_dynamic_quotes()
        if d_quotes_ko:
            with rss_cache["lock"]: rss_cache["dynamic_quotes"] = d_quotes_ko
            
        with rss_cache["lock"]: rss_cache["last_updated"] = time.time()
        print("[Background Engine] [DONE] 초기 갱신 완료!")
    except Exception as e:
        print(f"[Background Engine] [ERROR] 최초 갱신 오류: {e}")

    while True:
        time.sleep(600)  # 10분 대기
        try:
            print("[Background Engine] [START] 주기적 RSS/주식 데이터 갱신...")
            fetch_and_cache_market_data()
            
            y_insights = get_youtube_insights()
            if y_insights:
                with rss_cache["lock"]: rss_cache["youtube_insights"] = y_insights
                
            d_quotes = get_dynamic_quotes()
            if d_quotes:
                with rss_cache["lock"]: rss_cache["dynamic_quotes"] = d_quotes
                
            with rss_cache["lock"]: rss_cache["last_updated"] = time.time()
            print("[Background Engine] [DONE] 주기적 갱신 완료!")
        except Exception as e:
            print(f"[Background Engine] [ERROR] 주기적 갱신 오류: {e}")"""

mod.replace_func("update_rss_cache_background", new_bg)

new_content = mod.get_code()

new_cache = """rss_cache = {
    "top10_news": [],
    "keyword_news": [],
    "youtube_insights": [
        {"title": "[슈카월드] 최신 업로드 영상", "channel": "슈카월드", "date": datetime.now().strftime("%Y.%m.%d"), "link": "https://www.youtube.com/channel/UCsJ6RuBiTVWRX156FVbeaGg"},
        {"title": "[월가아재의과학적투자] 최신 업로드 영상", "channel": "월가아재의과학적투자", "date": datetime.now().strftime("%Y.%m.%d"), "link": "https://www.youtube.com/channel/UCJptR2r0YqXv1628J0pXpCw"},
        {"title": "[박종훈지식한방] 최신 업로드 영상", "channel": "박종훈지식한방", "date": datetime.now().strftime("%Y.%m.%d"), "link": "https://www.youtube.com/channel/UC5cKPnu2NpaxKjU2UBuvVxA"},
        {"title": "[소수몽키] 최신 업로드 영상", "channel": "소수몽키", "date": datetime.now().strftime("%Y.%m.%d"), "link": "https://www.youtube.com/channel/UC_t11S41W6N6hA4FqM3Bwbw"},
        {"title": "[전인구경제연구소] 최신 업로드 영상", "channel": "전인구경제연구소", "date": datetime.now().strftime("%Y.%m.%d"), "link": "https://www.youtube.com/channel/UCznImSIaxZR7fdLCICLdgaQ"},
        {"title": "[수페TV] 최신 업로드 영상", "channel": "수페TV", "date": datetime.now().strftime("%Y.%m.%d"), "link": "https://www.youtube.com/channel/UCiM27z7jO8O8xntKzF6Lh1A"},
        {"title": "[이효석아카데미] 최신 업로드 영상", "channel": "이효석아카데미", "date": datetime.now().strftime("%Y.%m.%d"), "link": "https://www.youtube.com/channel/UCn6a15h1H1Z61K8Pj_66G-A"}
    ],
    "dynamic_quotes": [
        {"text": '"시장이 탐욕스러울 때 두려워하고, 시장이 두려워할 때 탐욕스러워져야 합니다."', "author": "Warren Buffett", "role": "Berkshire Hathaway CEO", "date": datetime.now().strftime("%Y.%m.%d"), "link": "https://www.google.com/search?q=%EC%9B%8C%EB%9F%B0+%EB%B2%84%ED%95%8F"},
        {"text": '"최고의 투자는 위기 상황에서 인내심을 갖고 가치 있는 자산을 헐값에 매입하는 것입니다."', "author": "Bill Ackman", "role": "Pershing Square Capital CEO", "date": datetime.now().strftime("%Y.%m.%d"), "link": "https://www.google.com/search?q=%EB%B9%8C+%EC%97%90%ED%81%AC%EB%A8%BC"},
        {"text": '"가장 중요한 것은 무엇을 아느냐가 아니라 우리가 모른다는 사실을 아는 것입니다."', "author": "Howard Marks", "role": "Oaktree Capital Co-Chairman", "date": datetime.now().strftime("%Y.%m.%d"), "link": "https://www.google.com/search?q=%ED%95%98%EC%9B%8C%EB%93%9C+%EB%A7%89%EC%8A%A4"},
        {"text": '"성공적인 트레이딩의 핵심은 손실은 짧게 끊고 이익은 길게 가져가는 규율에 있습니다."', "author": "Mark Minervini", "role": "Author & Trader", "date": datetime.now().strftime("%Y.%m.%d"), "link": "https://www.google.com/search?q=%EB%A7%88%ED%81%AC+%EB%AF%B8%EB%84%88%EB%B9%84%EB%8B%88"},
        {"text": '"맞고 틀리는 것이 중요한 게 아니라, 맞았을 때 얼마나 많이 벌고 틀렸을 때 얼마나 적게 잃는지가 중요합니다."', "author": "Stanley Druckenmiller", "role": "Duquesne Family Office", "date": datetime.now().strftime("%Y.%m.%d"), "link": "https://www.google.com/search?q=%EC%8A%A4%ED%83%A0%EB%A6%AC+%EB%93%9C%EB%9F%AC%EC%BC%84%EB%B0%80%EB%9F%AC"},
        {"text": '"당신이 할 수 있는 가장 중요한 룰은 방어적인 플레이를 하는 것입니다. 결코 공격적인 플레이가 아닙니다."', "author": "Paul Tudor Jones", "role": "Tudor Investment Corp", "date": datetime.now().strftime("%Y.%m.%d"), "link": "https://www.google.com/search?q=%ED%8F%B4+%ED%8A%9C%EB%8D%94+%EC%A1%B4%EC%8A%A4"},
        {"text": '"연준의 통화정책은 시장의 기대에 끌려다니기보다 선제적으로 실물 경제의 펀더멘털을 반영해야 합니다."', "author": "Kevin Warsh", "role": "Former Federal Reserve Governor", "date": datetime.now().strftime("%Y.%m.%d"), "link": "https://www.google.com/search?q=%EC%BC%80%EB%B9%88+%EC%9B%8C%EC%8B%9C"}
    ],
    "last_updated": time.time(),
    "lock": threading.Lock()
}"""

new_content = re.sub(
    r'rss_cache = \{.*?\"lock\": threading\.Lock\(\)\n\}',
    new_cache,
    new_content, flags=re.DOTALL
)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

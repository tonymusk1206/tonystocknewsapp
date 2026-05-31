import re

with open("index.html", "r", encoding="utf-8") as f:
    text = f.read()

old_html = """                    <div id="search-price-card" style="margin-bottom:2rem;"></div>

                    <!-- TradingView 차트 -->"""

new_html = """                    <div id="search-price-card" style="margin-bottom:2rem;"></div>

                    <!-- 기업 개요 -->
                    <div id="company-profile-container" style="margin-bottom:2rem;"></div>

                    <!-- TradingView 차트 -->"""

text = text.replace(old_html, new_html)

# Also remove Naver Cafe link from index.html if it's there
old_links = """                        <div id="search-links" style="display:flex;gap:1rem;">
                            <!-- JS에서 동적 주입 -->
                        </div>"""

text = text.replace(old_links, old_links)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(text)

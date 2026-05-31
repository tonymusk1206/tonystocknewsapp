import re

# Update index.html
with open("index.html", "r", encoding="utf-8") as f:
    text = f.read()

# Remove cafe link block
cafe_link_pattern = r'<a id="link-naver-cafe".*?</a>'
text = re.sub(cafe_link_pattern, '', text, flags=re.DOTALL)

# Change title of the links box
text = text.replace("종목 토론방 및 카페", "종목 토론방")

with open("index.html", "w", encoding="utf-8") as f:
    f.write(text)

# Update js/app.js
with open("js/app.js", "r", encoding="utf-8") as f:
    js_text = f.read()

# Remove line: document.getElementById('link-naver-cafe').href  = data.links.naver_cafe;
js_text = re.sub(r"document\.getElementById\('link-naver-cafe'\)\.href\s*=\s*data\.links\.naver_cafe;", "", js_text)

# Change link-naver-board text to Yahoo Finance for US Stocks if needed, or just let it be. But wait, we can just say "종목 토론방" instead of "네이버 종목 토론방" since it links to Yahoo for US.
# It is defined as <span>💬</span> 네이버 종목 토론방 in index.html. I will change that.

# Also we need to render the company profile above the chart
profile_render_code = """
        // 기업 개요 렌더링
        const profileContainer = document.getElementById('company-profile-container');
        if (data.profile && Object.keys(data.profile).length > 0) {
            profileContainer.innerHTML = `
                <div class="glass-card" style="padding:1.5rem;">
                    <div style="display:flex;gap:10px;flex-wrap:wrap;margin-bottom:1rem;">
                        <span style="background:rgba(255,255,255,0.1);padding:6px 12px;border-radius:20px;font-size:0.9rem;color:#e2e8f0;font-weight:600;">#${data.name}</span>
                        <span style="background:rgba(255,255,255,0.1);padding:6px 12px;border-radius:20px;font-size:0.9rem;color:#e2e8f0;font-weight:600;">#시가총액_${data.profile.marketCap}</span>
                        <span style="background:rgba(255,255,255,0.1);padding:6px 12px;border-radius:20px;font-size:0.9rem;color:#e2e8f0;font-weight:600;">#${data.profile.sector}</span>
                        <span style="background:rgba(255,255,255,0.1);padding:6px 12px;border-radius:20px;font-size:0.9rem;color:#e2e8f0;font-weight:600;">#${data.profile.industry}</span>
                    </div>
                    <div style="font-size:0.95rem;line-height:1.6;color:#cbd5e1;">
                        ${data.profile.summary.replace(/\\n/g, '<br>')}
                    </div>
                </div>
            `;
            profileContainer.style.display = 'block';
        } else {
            profileContainer.style.display = 'none';
        }
"""

js_text = js_text.replace("renderTradingViewWidget(data.symbol);", profile_render_code + "\n        renderTradingViewWidget(data.symbol);")

# Change link text to be generic
with open("index.html", "r", encoding="utf-8") as f:
    html_text = f.read()
html_text = html_text.replace("네이버 종목 토론방", "해당 종목 토론방")

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_text)

with open("js/app.js", "w", encoding="utf-8") as f:
    f.write(js_text)


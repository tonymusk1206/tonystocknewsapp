import re

with open("app.py", "r", encoding="utf-8") as f:
    text = f.read()

# 1. Update YouTube logic
old_youtube = """    def fetch_channel(ch):
        url = f"https://www.youtube.com/feeds/videos.xml?channel_id={ch['id']}"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as resp:
                xml_data = resp.read()
                root = ET.fromstring(xml_data)
                ns = {'yt': 'http://www.youtube.com/xml/schemas/2015', 'atom': 'http://www.w3.org/2005/Atom'}
                entry = root.find('atom:entry', ns)
                if entry is not None:
                    title = entry.find('atom:title', ns).text
                    link = entry.find('atom:link', ns).attrib['href']
                    published = entry.find('atom:published', ns).text
                    pub_date = published.split('T')[0].replace('-', '.')
                    return {"title": title, "channel": ch["name"], "date": pub_date, "link": link}
        except Exception as e:
            print(f"[YouTube] Error fetching {ch['name']}: {e}")"""

new_youtube = """    def fetch_channel(ch):
        url = f"https://api.rss2json.com/v1/api.json?rss_url=https://www.youtube.com/feeds/videos.xml?channel_id={ch['id']}"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())
                item = data['items'][0]
                title = item['title']
                link = item['link']
                # pubDate format: 2026-05-22 13:42:48
                pub_date = item['pubDate'].split(' ')[0].replace('-', '.')
                return {"title": title, "channel": ch["name"], "date": pub_date, "link": link}
        except Exception as e:
            print(f"[YouTube] Error fetching {ch['name']}: {e}")"""

text = text.replace(old_youtube, new_youtube)

# 2. Update Profile & Add EPS
old_profile = """        # summary fetching via Wikipedia API
        summary = ""
        try:
            # removing 'Inc.', 'Corp.', 'Co., Ltd.' for better wiki match
            clean_name = short_name.split(',')[0].replace(' Inc.', '').replace(' Corp.', '').replace(' Co.', '').replace(' Ltd.', '')
            wiki_url = f"https://ko.wikipedia.org/w/api.php?action=query&prop=extracts&exintro=True&explaintext=True&format=json&redirects=1&titles={urllib.parse.quote(clean_name)}"
            req = urllib.request.Request(wiki_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=3) as resp:
                summary = json.loads(resp.read().decode('utf-8')).get('query', {}).get('pages', {})
                summary = list(summary.values())[0].get('extract', '')
        except:
            pass"""

new_profile = """        # summary fetching via Naver API & Wikipedia
        summary = ""
        clean_name = short_name.split(',')[0].replace(' Inc.', '').replace(' Corp.', '').replace(' Co.', '').replace(' Ltd.', '')
        
        try:
            if not is_kr:
                base_sym = symbol.split('.')[0]
                for suffix in ['.O', '.N', '']:
                    url = f'https://api.stock.naver.com/stock/{base_sym}{suffix}/integration'
                    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                    try:
                        with urllib.request.urlopen(req, timeout=3) as resp:
                            data = json.loads(resp.read().decode())
                            if 'corporateOverview' in data:
                                summary = data['corporateOverview']
                                break
                    except:
                        continue
            
            if not summary:
                wiki_url = f"https://ko.wikipedia.org/w/api.php?action=query&prop=extracts&exintro=True&explaintext=True&format=json&redirects=1&titles={urllib.parse.quote(clean_name)}"
                req = urllib.request.Request(wiki_url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=3) as resp:
                    summary_dict = json.loads(resp.read().decode('utf-8')).get('query', {}).get('pages', {})
                    summary = list(summary_dict.values())[0].get('extract', '')
        except:
            pass

        # EPS Fetching (최근 5년 = 20분기)
        eps_data = []
        try:
            df_eps = ticker.earnings_dates
            if df_eps is not None and not df_eps.empty:
                df_eps = df_eps.dropna(subset=['EPS Estimate', 'Reported EPS'])
                # DataFrame index is datetime, we want to sort it chronologically
                df_eps = df_eps.sort_index(ascending=True)
                df_eps = df_eps.tail(20) # 5 years = 20 quarters
                for date, row in df_eps.iterrows():
                    eps_data.append({
                        "date": date.strftime('%Y-%m-%d'),
                        "estimate": float(row['EPS Estimate']),
                        "reported": float(row['Reported EPS']),
                        "surprise": float(row.get('Surprise(%)', 0.0))
                    })
        except Exception as e:
            print(f"[EPS Error] {e}")"""

text = text.replace(old_profile, new_profile)

# Add eps_data to the JSON response
old_return = """        return jsonify({
            "name": short_name,
            "symbol": symbol,
            "exchange": exchange,
            "current": current_price,
            "changes": changes,
            "profile": {
                "sector": sector_val,
                "industry": industry_val,
                "market_cap": mc_str,
                "summary": summary
            },
            "news": news_items,
            "history": history_data
        })"""

new_return = """        return jsonify({
            "name": short_name,
            "symbol": symbol,
            "exchange": exchange,
            "current": current_price,
            "changes": changes,
            "profile": {
                "sector": sector_val,
                "industry": industry_val,
                "market_cap": mc_str,
                "summary": summary
            },
            "news": news_items,
            "history": history_data,
            "eps": eps_data
        })"""

text = text.replace(old_return, new_return)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(text)

# 3. Update js/app.js to render EPS chart
with open("js/app.js", "r", encoding="utf-8") as f:
    js = f.read()

# Add a placeholder for EPS section in search_stock() HTML
old_search_html = """            </div>
        `;
        document.getElementById('search-chart').innerHTML = ''; // Placeholder for chart

        renderInteractiveChart(data);
    }"""

new_search_html = """            </div>
        `;
        document.getElementById('search-chart').innerHTML = '';

        renderInteractiveChart(data);
        renderEPSSection(data);
    }"""
js = js.replace(old_search_html, new_search_html)

# Add renderEPSSection function
eps_func = """
function renderEPSSection(data) {
    if(!data.eps || data.eps.length === 0) return;

    let tableRows = '';
    data.eps.forEach(e => {
        const surColor = e.surprise > 0 ? '#22c55e' : e.surprise < 0 ? '#f87171' : '#94a3b8';
        tableRows += `
            <tr style="border-bottom:1px solid rgba(255,255,255,0.05);">
                <td style="padding:10px;text-align:left;">${e.date}</td>
                <td style="padding:10px;text-align:right;">${e.estimate.toFixed(2)}</td>
                <td style="padding:10px;text-align:right;font-weight:bold;">${e.reported.toFixed(2)}</td>
                <td style="padding:10px;text-align:right;color:${surColor};">${e.surprise > 0 ? '+' : ''}${e.surprise.toFixed(1)}%</td>
            </tr>
        `;
    });

    const epsHtml = `
        <div class="glass-card" style="margin-top:20px;padding:20px;">
            <h3 style="font-size:1.1rem;font-weight:700;margin-bottom:15px;color:#a78bfa;">최근 5년 분기별 EPS (주당순이익)</h3>
            
            <div style="width:100%; height:300px; margin-bottom:20px;">
                <canvas id="epsChartCanvas"></canvas>
            </div>
            
            <div style="overflow-x:auto;">
                <table style="width:100%; border-collapse:collapse; font-size:0.9rem;">
                    <thead>
                        <tr style="border-bottom:1px solid rgba(255,255,255,0.1);color:#a78bfa;">
                            <th style="padding:10px;text-align:left;">발표일</th>
                            <th style="padding:10px;text-align:right;">예측치(Est)</th>
                            <th style="padding:10px;text-align:right;">발표치(Act)</th>
                            <th style="padding:10px;text-align:right;">어닝 서프라이즈</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${tableRows}
                    </tbody>
                </table>
            </div>
        </div>
    `;
    
    // Append to search-content
    const el = document.getElementById('search-content');
    const div = document.createElement('div');
    div.innerHTML = epsHtml;
    el.appendChild(div);

    // Draw Chart
    const ctx = document.getElementById('epsChartCanvas').getContext('2d');
    const labels = data.eps.map(e => e.date);
    const estData = data.eps.map(e => e.estimate);
    const actData = data.eps.map(e => e.reported);

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: '예측치',
                    data: estData,
                    backgroundColor: 'rgba(148, 163, 184, 0.5)',
                    borderColor: 'rgba(148, 163, 184, 1)',
                    borderWidth: 1
                },
                {
                    label: '발표치',
                    data: actData,
                    backgroundColor: 'rgba(167, 139, 250, 0.8)',
                    borderColor: 'rgba(167, 139, 250, 1)',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { labels: { color: '#e2e8f0' } }
            },
            scales: {
                y: {
                    grid: { color: 'rgba(255,255,255,0.05)' },
                    ticks: { color: '#94a3b8' }
                },
                x: {
                    grid: { display: false },
                    ticks: { color: '#94a3b8', maxRotation: 45, minRotation: 45 }
                }
            }
        }
    });
}
"""

if "function renderEPSSection(data)" not in js:
    js += eps_func

with open("js/app.js", "w", encoding="utf-8") as f:
    f.write(js)

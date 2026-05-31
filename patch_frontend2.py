import re

# 1. Update index.html
with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

# Add Chart.js CDN before closing </head>
html = html.replace('</head>', '    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>\n</head>')

# Add Modal HTML just before </body>
modal_html = """
    <!-- 관련주 모달 -->
    <div id="related-stocks-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.6); backdrop-filter:blur(5px); z-index:9999; justify-content:center; align-items:center;">
        <div class="glass-card" style="padding:2rem; max-width:400px; width:90%; position:relative; max-height:80vh; display:flex; flex-direction:column;">
            <button onclick="document.getElementById('related-stocks-modal').style.display='none'" style="position:absolute; top:15px; right:20px; background:transparent; border:none; color:white; font-size:1.5rem; cursor:pointer;">&times;</button>
            <h3 style="margin-bottom:1rem; color:var(--accent-brand);">동일 산업군 기업 리스트</h3>
            <div id="related-stocks-list" style="display:flex; flex-direction:column; gap:10px; overflow-y:auto; flex-grow:1;">
            </div>
        </div>
    </div>
"""
html = html.replace('</body>', modal_html + '\n</body>')

# Add EPS Container after TradingView Container
eps_html = """
                    <!-- EPS 실적 컨테이너 -->
                    <div id="eps-container" class="glass-card" style="margin-bottom:2rem;padding:1.5rem; display:none;">
                        <h3 style="margin-bottom:1rem;color:var(--accent-brand);">📈 최근 5년 분기별 실적 (EPS)</h3>
                        <div style="overflow-x:auto; margin-bottom:1.5rem;">
                            <table style="width:100%; border-collapse:collapse; text-align:center; color:#e2e8f0; font-size:0.9rem;">
                                <thead>
                                    <tr style="border-bottom:1px solid rgba(255,255,255,0.1);">
                                        <th style="padding:10px;">날짜</th>
                                        <th style="padding:10px;">예상치</th>
                                        <th style="padding:10px;">실제발표</th>
                                        <th style="padding:10px;">결과(Surprise)</th>
                                    </tr>
                                </thead>
                                <tbody id="eps-table-body">
                                </tbody>
                            </table>
                        </div>
                        <div style="height:300px; position:relative;">
                            <canvas id="eps-chart"></canvas>
                        </div>
                    </div>
"""
html = html.replace('</div>\n                    </div>\n\n                    <!-- 최신 글로벌 뉴스 -->', '</div>\n                    </div>\n' + eps_html + '\n                    <!-- 최신 글로벌 뉴스 -->')

# One thing to check: did I use replacing on the exact string? The original string was:
#                    <!-- 최신 글로벌 뉴스 -->

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

# 2. Update app.js
with open("js/app.js", "r", encoding="utf-8") as f:
    js = f.read()

old_profile_render = """        const profileContainer = document.getElementById('company-profile-container');
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
        }"""

new_profile_render = """        // 기업 개요 렌더링
        const profileContainer = document.getElementById('company-profile-container');
        if (data.profile && Object.keys(data.profile).length > 0) {
            let relatedStocksHtml = '';
            let popupListHtml = '';
            if (data.profile.related_stocks && data.profile.related_stocks.length > 0) {
                // 상단 해시태그에는 3개까지만 노출
                const topRelated = data.profile.related_stocks.slice(0, 3);
                topRelated.forEach(s => {
                    relatedStocksHtml += `<span onclick="searchStock('${s.symbol}')" style="cursor:pointer; background:linear-gradient(135deg, rgba(139,92,246,0.3), rgba(56,189,248,0.3));padding:6px 12px;border-radius:20px;font-size:0.9rem;color:#e2e8f0;font-weight:600;transition:all 0.2s;" onmouseover="this.style.opacity=0.8" onmouseout="this.style.opacity=1">#관련주_${s.name}</span>`;
                });
                
                // 팝업 리스트 HTML 생성
                data.profile.related_stocks.forEach(s => {
                    popupListHtml += `<div onclick="searchStock('${s.symbol}'); document.getElementById('related-stocks-modal').style.display='none'" style="cursor:pointer; padding:12px; background:rgba(255,255,255,0.05); border-radius:8px; border:1px solid rgba(255,255,255,0.1); transition:background 0.2s;" onmouseover="this.style.background='rgba(255,255,255,0.1)'" onmouseout="this.style.background='rgba(255,255,255,0.05)'"><div style="font-weight:bold; color:white;">${s.name}</div><div style="font-size:0.8rem; color:#94a3b8;">${s.symbol}</div></div>`;
                });
            }

            window.showRelatedModal = function() {
                if(popupListHtml) {
                    document.getElementById('related-stocks-list').innerHTML = popupListHtml;
                    document.getElementById('related-stocks-modal').style.display = 'flex';
                }
            };

            profileContainer.innerHTML = `
                <div class="glass-card" style="padding:1.5rem;">
                    <div style="display:flex;gap:10px;flex-wrap:wrap;margin-bottom:1rem;">
                        <span style="background:rgba(255,255,255,0.1);padding:6px 12px;border-radius:20px;font-size:0.9rem;color:#e2e8f0;font-weight:600;">#${data.name}</span>
                        <span onclick="showRelatedModal()" style="cursor:pointer; background:rgba(255,255,255,0.1);padding:6px 12px;border-radius:20px;font-size:0.9rem;color:#e2e8f0;font-weight:600;transition:all 0.2s;" onmouseover="this.style.background='rgba(255,255,255,0.2)'" onmouseout="this.style.background='rgba(255,255,255,0.1)'">#${data.profile.sector}</span>
                        <span onclick="showRelatedModal()" style="cursor:pointer; background:rgba(255,255,255,0.1);padding:6px 12px;border-radius:20px;font-size:0.9rem;color:#e2e8f0;font-weight:600;transition:all 0.2s;" onmouseover="this.style.background='rgba(255,255,255,0.2)'" onmouseout="this.style.background='rgba(255,255,255,0.1)'">#${data.profile.industry}</span>
                        ${relatedStocksHtml}
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
        
        // EPS 렌더링
        const epsContainer = document.getElementById('eps-container');
        if (data.earnings && data.earnings.length > 0) {
            epsContainer.style.display = 'block';
            let tbodyHtml = '';
            let labels = [];
            let estimates = [];
            let reported = [];
            
            data.earnings.forEach(e => {
                labels.push(e.date);
                estimates.push(e.estimate || 0);
                reported.push(e.reported || 0);
                
                let surpHtml = '-';
                if(e.surprise !== null && e.surprise !== undefined) {
                    let sVal = e.surprise;
                    if(sVal > 0) surpHtml = `<span style="color:#10b981;font-weight:bold;">Beat (+${sVal.toFixed(2)}%)</span>`;
                    else if(sVal < 0) surpHtml = `<span style="color:#ef4444;font-weight:bold;">Miss (${sVal.toFixed(2)}%)</span>`;
                    else surpHtml = `<span>Meet (0%)</span>`;
                }
                
                tbodyHtml += `<tr style="border-bottom:1px solid rgba(255,255,255,0.05);">
                    <td style="padding:10px;">${e.date}</td>
                    <td style="padding:10px;">${e.estimate !== null ? e.estimate.toFixed(2) : '-'}</td>
                    <td style="padding:10px;">${e.reported !== null ? e.reported.toFixed(2) : '-'}</td>
                    <td style="padding:10px;">${surpHtml}</td>
                </tr>`;
            });
            document.getElementById('eps-table-body').innerHTML = tbodyHtml;
            
            // Draw Chart.js
            const ctx = document.getElementById('eps-chart').getContext('2d');
            if(window.epsChartInstance) {
                window.epsChartInstance.destroy();
            }
            window.epsChartInstance = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: '예상치 (Estimate)',
                            data: estimates,
                            backgroundColor: 'rgba(148, 163, 184, 0.5)',
                            borderColor: 'rgba(148, 163, 184, 1)',
                            borderWidth: 1
                        },
                        {
                            label: '실제발표 (Reported)',
                            data: reported,
                            backgroundColor: 'rgba(139, 92, 246, 0.7)',
                            borderColor: 'rgba(139, 92, 246, 1)',
                            borderWidth: 1
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            grid: { color: 'rgba(255,255,255,0.1)' },
                            ticks: { color: '#cbd5e1' }
                        },
                        x: {
                            grid: { display: false },
                            ticks: { color: '#cbd5e1' }
                        }
                    },
                    plugins: {
                        legend: { labels: { color: '#cbd5e1' } }
                    }
                }
            });
            
        } else {
            if(epsContainer) epsContainer.style.display = 'none';
        }"""

if old_profile_render in js:
    js = js.replace(old_profile_render, new_profile_render)
else:
    print("WARNING: Old profile render string not found in app.js!")

if 'async function searchStock(' in js:
    js = js.replace('async function searchStock(', 'window.searchStock = async function(')
elif 'const searchStock = async (' in js:
    js = js.replace('const searchStock = async (', 'window.searchStock = async function(')

with open("js/app.js", "w", encoding="utf-8") as f:
    f.write(js)

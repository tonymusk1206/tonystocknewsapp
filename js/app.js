let mockData = null; 

document.addEventListener("DOMContentLoaded", () => {
    console.log("Tony's Stock Dashboard: DOMContentLoaded");
    const statusDisplay = document.getElementById('base-date-display');
    if (statusDisplay) statusDisplay.innerText = '상태: 자바스크립트 로드됨 (연결 시도 중...)';
    
    updateTime();
    fetchMarketData();
});

async function fetchMarketData() {
    const statusDisplay = document.getElementById('base-date-display');
    
    // 로딩 표시 (DOM 교체 없이 오버레이 방식)
    const loadingEl = document.createElement('div');
    loadingEl.id = 'loading-overlay';
    loadingEl.style.cssText = `position:fixed;inset:0;background:rgba(10,15,30,0.92);z-index:9999;
        display:flex;flex-direction:column;align-items:center;justify-content:center;color:white;`;
    loadingEl.innerHTML = `
        <div class="pulse-dot" style="width:60px;height:60px;box-shadow:0 0 25px var(--accent-brand);
            background:var(--accent-brand);animation-duration:1.2s;margin-bottom:2rem;"></div>
        <h2 style="font-family:var(--font-heading);font-size:2rem;text-shadow:0 0 15px rgba(59,130,246,0.6);">
            데이터 연결 중...</h2>
        <p style="color:var(--text-secondary);margin-top:15px;font-size:1.1rem;">
            Bloomberg · WSJ · Yahoo Finance 데이터 수신 중</p>`;
    document.body.appendChild(loadingEl);
    
    try {
        const apiUrl = window.location.origin.includes('http') 
            ? `${window.location.origin}/api/market-data`
            : 'https://tony-stock-news.onrender.com/api/market-data';
            
        const res = await fetch(apiUrl);
        if (!res.ok) throw new Error(`서버 응답 오류 (HTTP ${res.status})`);
        
        mockData = await res.json();
        if (mockData.error) throw new Error(`백엔드 오류: ${mockData.error}`);
        
        if (statusDisplay) statusDisplay.innerText = `업데이트: ${mockData.baseDate || '성공'}`;
        
        // 데이터 렌더링 (DOM 유지, 내용만 교체)
        renderMarkets();
        renderSectors();
        renderCompanies();
        renderNews();
        renderQuotes();
        renderYoutube();
        
    } catch (err) {
        console.error("Fetch Error:", err);
        if (statusDisplay) statusDisplay.innerText = '연결 실패 - 재시도 중...';
        // 5초 후 자동 재시도
        setTimeout(fetchMarketData, 5000);
    } finally {
        const ol = document.getElementById('loading-overlay');
        if (ol) ol.remove();
    }
}

function updateTime() {
    const timeDisplay = document.getElementById('time-display');
    if (!timeDisplay) return;

    setInterval(() => {
        const now = new Date();
        timeDisplay.textContent = now.toLocaleTimeString('ko-KR');
    }, 1000);
}


// ── Search 기능 ──
const SEARCH_API = window.location.origin.includes('http')
    ? `${window.location.origin}/api/search`
    : 'https://tony-stock-news.onrender.com/api/search';

async function doSearch() {
    const q = (document.getElementById('search-input').value || '').trim();
    if (!q) return;

    const elLoading = document.getElementById('search-loading');
    const elError   = document.getElementById('search-error');
    const elResult  = document.getElementById('search-result');
    const elBtn     = document.getElementById('search-btn');

    elLoading.style.display = 'block';
    elError.style.display   = 'none';
    elResult.style.display  = 'none';
    elBtn.disabled          = true;
    elBtn.textContent       = '검색 중...';

    try {
        const res  = await fetch(`${SEARCH_API}?q=${encodeURIComponent(q)}`);
        const data = await res.json();

        if (data.error) throw new Error(data.error);

        renderSearchPriceCard(data);
        
        // 기업 개요 렌더링
        // 기업 개요 렌더링
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
                        ${data.profile.summary.replace(/\n/g, '<br>')}
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
        }

        renderTradingViewWidget(data.symbol);
        renderSearchNews(data.news);
        document.getElementById('link-naver-board').href = data.links.naver_board;
        

        elResult.style.display = 'block';
    } catch (err) {
        elError.style.display   = 'block';
        elError.textContent     = `❌ ${err.message}`;
    } finally {
        elLoading.style.display = 'none';
        elBtn.disabled          = false;
        elBtn.textContent       = '검색';
    }
}

function renderSearchPriceCard(data) {
    const ch = data.changes;
    const pct = (v) => {
        const cls = v.pct > 0 ? '#22c55e' : v.pct < 0 ? '#f87171' : '#94a3b8';
        const sign = v.pct > 0 ? '+' : '';
        return `<span style="color:${cls};font-weight:700;">${sign}${v.pct}%</span>
                <div style="font-size:0.82rem;color:#94a3b8;margin-top:2px;">${v.price}</div>`;
    };
    const box = (label, sub, change) => `
        <div style="background:rgba(255,255,255,0.05);border-radius:10px;padding:14px 16px;min-width:110px;">
            <div style="font-size:0.75rem;color:#94a3b8;margin-bottom:6px;">${label}<br/><span style="font-size:0.7rem;">${sub}</span></div>
            ${pct(change)}
        </div>`;

    document.getElementById('search-price-card').innerHTML = `
        <div class="glass-card" style="padding:1.5rem;">
            <div style="font-size:1.2rem;font-weight:700;margin-bottom:4px;">${data.name}
                <span style="font-size:0.9rem;color:#94a3b8;font-weight:400;"> (${data.symbol} · ${data.exchange})</span>
            </div>
            <div style="font-size:2.2rem;font-weight:800;margin-bottom:1rem;">${data.price}</div>
            <div style="display:flex;gap:10px;flex-wrap:wrap;">
                ${box('1일전比','(1일전)', ch.d1)}
                ${box('3일전比','(3일전)', ch.d3)}
                ${box('1주전比','(1주전)', ch.w1)}
                ${box('1달전比','(1달전)', ch.m1)}
                ${box('3달전比','(3달전)', ch.m3)}
                ${box('6달전比','(6달전)', ch.m6)}
                ${box('1년전比','(1년전)', ch.y1)}
            </div>
        </div>`;
}

function renderTradingViewWidget(symbol) {
    // 한국 주식 티커 변환 (예: 005930.KS → KRX:005930)
    let tvSymbol = symbol;
    if (symbol.endsWith('.KS')) tvSymbol = 'KRX:' + symbol.replace('.KS','');
    else if (symbol.endsWith('.KQ')) tvSymbol = 'KOSDAQ:' + symbol.replace('.KQ','');

    const container = document.getElementById('tradingview-container');
    container.innerHTML = '';

    const script = document.createElement('script');
    script.src = 'https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js';
    script.type = 'text/javascript';
    script.async = true;
    script.innerHTML = JSON.stringify({
        autosize: true,
        symbol: tvSymbol,
        interval: "D",
        timezone: "Asia/Seoul",
        theme: "dark",
        style: "1",
        locale: "kr",
        allow_symbol_change: true,
        calendar: false,
        support_host: "https://www.tradingview.com",
        height: 500,
    });

    const wrapper = document.createElement('div');
    wrapper.className = 'tradingview-widget-container';
    wrapper.style.height = '500px';
    const inner = document.createElement('div');
    inner.className = 'tradingview-widget-container__widget';
    inner.style.height = '100%';
    wrapper.appendChild(inner);
    wrapper.appendChild(script);
    container.appendChild(wrapper);
}

function renderSearchNews(news) {
    const el = document.getElementById('search-news-list');
    if (!news || news.length === 0) {
        el.innerHTML = '<p style="color:#94a3b8;">뉴스를 찾을 수 없습니다.</p>';
        return;
    }
    el.innerHTML = news.map(n => `
        <a href="${n.link}" target="_blank" style="display:block;text-decoration:none;color:inherit;
           padding:1rem;background:rgba(255,255,255,0.03);border-radius:10px;
           border:1px solid rgba(255,255,255,0.07);transition:background 0.2s;"
           onmouseover="this.style.background='rgba(255,255,255,0.07)'"
           onmouseout="this.style.background='rgba(255,255,255,0.03)'">
            <div style="font-size:0.8rem;color:#94a3b8;margin-bottom:6px;">
                ${n.date} &nbsp;|&nbsp; <span style="color:var(--accent-brand);">${n.source}</span>
            </div>
            <div style="font-weight:600;font-size:1rem;line-height:1.4;margin-bottom:4px;">${n.title}</div>
            <div style="font-size:0.82rem;color:#94a3b8;">${n.original_title}</div>
        </a>`).join('');
}

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

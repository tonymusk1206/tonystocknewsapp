// 공통 유틸리티
function formatPercent(data) {
    const value = data.pct;
    const price = data.price;
    let html = '';
    
    if (value > 0) html = `<span class="val-up">▲ ${value.toFixed(1)}%</span>`;
    else if (value < 0) html = `<span class="val-down">▼ ${Math.abs(value).toFixed(1)}%</span>`;
    else html = `<span class="val-neutral">- ${value.toFixed(1)}%</span>`;
    
    if (price && price !== 'N/A') {
        html += `<div class="hist-price">${price}</div>`;
    }
    return html;
}

function getPercentClass(data) {
    const value = typeof data === 'object' ? data.pct : data;
    if (value > 0) return 'val-up';
    if (value < 0) return 'val-down';
    return 'val-neutral';
}

function createMarketCard(market) {
    if (!mockData) return '';
    const renderMetric = (label, date, change) => `
        <div class="metric-box">
            <span class="metric-label">${label}<br/>(${date})</span>
            <span class="metric-value ${getPercentClass(change)}">${change.pct > 0 ? '+' : ''}${change.pct}%</span>
            <span class="metric-hist-price">${change.price}</span>
        </div>
    `;

    return `
        <div class="glass-card" onclick="window.open('https://finance.yahoo.com/quote/' + '${market.yahoo_ticker}', '_blank')" style="cursor: pointer; transition: transform 0.2s, background 0.2s;" onmouseover="this.style.background='rgba(255,255,255,0.06)'" onmouseout="this.style.background=''">
            <div class="c-name" style="margin-bottom: 8px; display: flex; justify-content: space-between;">
                <span>${market.name} 
                    <span style="font-size: 0.8rem; color: var(--text-secondary);">(${market.ticker})</span>
                </span>
            </div>
            <div class="company-metrics">
                <div class="metric-box current-box">
                    <span class="metric-label">현재가 (${mockData.dates.current})</span>
                    <div class="metric-content">
                        <span class="metric-value highlight">${market.value}</span>
                        <span class="metric-pct ${getPercentClass(market.changes.today)}">
                            ${market.changes.today.pct > 0 ? '▲' : market.changes.today.pct < 0 ? '▼' : ''} ${Math.abs(market.changes.today.pct)}%
                        </span>
                    </div>
                </div>
                ${renderMetric('1일전比', mockData.dates.d1, market.changes.d1)}
                ${renderMetric('3일전比', mockData.dates.d3, market.changes.d3)}
                ${renderMetric('1주전比', mockData.dates.w1, market.changes.w1)}
                ${renderMetric('1달전比', mockData.dates.m1, market.changes.m1)}
                ${renderMetric('3달전比', mockData.dates.m3, market.changes.m3)}
                ${renderMetric('6달전比', mockData.dates.m6, market.changes.m6)}
                ${renderMetric('1년전比', mockData.dates.y1, market.changes.y1)}
            </div>
        </div>
    `;
}

// 1. 글로벌 주요 증시 현황 렌더링 (원래대로 단독 라인 원복)
function renderMarkets() {
    if (!mockData) return;
    document.getElementById('market-title').innerText = `🌎 글로벌 주요 증시 현황 (${mockData.baseDate})`;

    const container = document.getElementById('market-overview-container');
    
    // Group by region
    const grouped = mockData.markets.reduce((acc, market) => {
        if (!acc[market.region]) acc[market.region] = [];
        acc[market.region].push(market);
        return acc;
    }, {});

    let html = '';
    
    // 미국, 한국 동일한 구조로 단독 라벨링
    ['미국', '한국'].forEach(region => {
        if (!grouped[region]) return;
        html += `<div class="region-group">
            <h3 class="region-title">${region} 증시</h3>
            <div class="grid-container" style="margin-bottom: 2rem;">`;
            
        html += grouped[region].map(market => createMarketCard(market)).join('');
        html += `</div></div>`;
    });
    
    // 일본, 중국은 한 영역(그리드)으로 병합하여 한국 증시의 카드 크기와 일치시킴
    if (grouped['일본'] || grouped['중국']) {
        html += `<div class="region-group">
            <h3 class="region-title">일본 및 중국 증시</h3>
            <div class="grid-container" style="margin-bottom: 2rem;">`;
            
        if (grouped['일본']) html += grouped['일본'].map(market => createMarketCard(market)).join('');
        if (grouped['중국']) html += grouped['중국'].map(market => createMarketCard(market)).join('');
        
        html += `</div></div>`;
    }
    
    container.innerHTML = html;
}

// 2. 한/미 섹터별 등락 렌더링
function createSectorTableHTML(sectors) {
    if (!mockData) return '';
    let rows = sectors.map(sector => `
        <tr onclick="window.open('https://finance.yahoo.com/quote/' + '${sector.yahoo_ticker}', '_blank')" style="cursor: pointer; transition: background 0.2s;" onmouseover="this.style.background='rgba(255,255,255,0.08)'" onmouseout="this.style.background=''">
            <td>
                <div class="ticker-name">${sector.name} <span style="font-size: 0.85em; font-weight: normal; color: var(--text-secondary);">(${sector.desc})</span></div>
                <span class="ticker-desc" style="display: block; margin-top: 4px; color: var(--text-muted); font-size: 0.8em; font-weight: 500;">(${sector.ticker})</span>
            </td>
            <td style="font-weight: 600;">
                <div style="font-size: 1rem; margin-bottom: 4px;">${sector.value}</div>
                <div style="font-weight: 500;">${formatPercent(sector.changes.today)}</div>
            </td>
            <td>${formatPercent(sector.changes.d1)}</td>
            <td>${formatPercent(sector.changes.d3)}</td>
            <td>${formatPercent(sector.changes.w1)}</td>
            <td>${formatPercent(sector.changes.m1)}</td>
            <td>${formatPercent(sector.changes.m3)}</td>
            <td>${formatPercent(sector.changes.m6)}</td>
            <td>${formatPercent(sector.changes.y1)}</td>
        </tr>
    `).join('');

    return `
        <thead>
            <tr>
                <th>자산 (ETF)</th>
                <th>현재가<br/>(${mockData.dates.current})</th>
                <th>1일전比<br/>(${mockData.dates.d1})</th>
                <th>3일전比<br/>(${mockData.dates.d3})</th>
                <th>1주전比<br/>(${mockData.dates.w1})</th>
                <th>1달전比<br/>(${mockData.dates.m1})</th>
                <th>3달전比<br/>(${mockData.dates.m3})</th>
                <th>6달전比<br/>(${mockData.dates.m6})</th>
                <th>1년전比<br/>(${mockData.dates.y1})</th>
            </tr>
        </thead>
        <tbody>
            ${rows}
        </tbody>
    `;
}

function renderSectors() {
    if (!mockData) return;
    document.getElementById('sector-title').innerText = `📊 섹터별 성과 분석 (${mockData.baseDate})`;
    document.getElementById('us-sectors-table').innerHTML = createSectorTableHTML(mockData.usSectors);
    document.getElementById('kr-sectors-table').innerHTML = createSectorTableHTML(mockData.krSectors);
}

function createCompanyCard(company) {
    const renderMetric = (label, date, change) => `
        <div class="metric-box">
            <span class="metric-label">${label}<br/>(${date})</span>
            <span class="metric-value ${getPercentClass(change)}">${change.pct > 0 ? '+' : ''}${change.pct}%</span>
            <span class="metric-hist-price">${change.price}</span>
        </div>
    `;

    return `
        <div class="glass-card company-card" onclick="window.open('https://finance.yahoo.com/quote/' + '${company.yahoo_ticker}', '_blank')" style="cursor: pointer; transition: transform 0.2s, background 0.2s;" onmouseover="this.style.background='rgba(255,255,255,0.08)'" onmouseout="this.style.background=''">
            <div class="company-header" style="align-items: center; margin-bottom: 12px;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    ${company.logo ? `<div style="width: 30px; height: 30px; background: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; padding: 4px;"><img src="${company.logo}" style="max-width: 100%; max-height: 100%;" /></div>` : '<div style="width: 30px; height: 30px; background: rgba(255,255,255,0.1); border-radius: 50%;"></div>'}
                    <div class="company-info">
                        <div class="c-name">${company.name}</div>
                        <div class="c-sector">${company.ticker}</div>
                    </div>
                </div>
            </div>
            
            <div class="company-metrics">
                <div class="metric-box current-box">
                    <span class="metric-label">현재가 (${mockData.dates.current})</span>
                    <div class="metric-content">
                        <span class="metric-value highlight">${company.value}</span>
                        <span class="metric-pct ${getPercentClass(company.changes.today)}">
                            ${company.changes.today.pct > 0 ? '▲' : company.changes.today.pct < 0 ? '▼' : ''} ${Math.abs(company.changes.today.pct)}%
                        </span>
                    </div>
                </div>
                ${renderMetric('1일전比', mockData.dates.d1, company.changes.d1)}
                ${renderMetric('3일전比', mockData.dates.d3, company.changes.d3)}
                ${renderMetric('1주전比', mockData.dates.w1, company.changes.w1)}
                ${renderMetric('1개월전比', mockData.dates.m1, company.changes.m1)}
                ${renderMetric('3개월전比', mockData.dates.m3, company.changes.m3)}
                ${renderMetric('6개월전比', mockData.dates.m6, company.changes.m6)}
                ${renderMetric('1년전比', mockData.dates.y1, company.changes.y1)}
            </div>
        </div>
    `;
}

// 3. 주요 대표 기업 현황 렌더링 (미/한 분리)
function renderCompanies() {
    if (!mockData) return;
    const container = document.getElementById('companies-container');
    let html = '';

    for (const [sector, companies] of Object.entries(mockData.companiesBySector)) {
        html += `
            <div class="sector-group" style="margin-bottom: 3.5rem;">
                <h3 class="region-title" style="margin-bottom: 1rem; color: var(--accent-brand); border-left: 4px solid var(--accent-brand); padding-left: 10px;">${sector}</h3>
        `;

        // 티커의 숫자 여부로 한국주식과 미국주식 판별
        const usComps = companies.filter(c => isNaN(c.ticker[0])); 
        const krComps = companies.filter(c => !isNaN(c.ticker[0]));

        if (usComps.length > 0) {
            html += `<h4 style="margin-top: 1.5rem; margin-bottom: 0.8rem; color: var(--text-secondary); font-size: 1rem; font-weight: 500;">🇺🇸 미국 대표 주식</h4>
                     <div class="grid-container" style="margin-bottom: 1.5rem;">`;
            html += usComps.map(company => createCompanyCard(company)).join('');
            html += `</div>`;
        }

        if (krComps.length > 0) {
            html += `<h4 style="margin-top: 1.5rem; margin-bottom: 0.8rem; color: var(--text-secondary); font-size: 1rem; font-weight: 500;">🇰🇷 한국 대표 주식</h4>
                     <div class="grid-container">`;
            html += krComps.map(company => createCompanyCard(company)).join('');
            html += `</div>`;
        }

        html += `</div>`;
    }
    container.innerHTML = html;
}

// 4. 주요 뉴스 렌더링
function renderNews() {
    if (!mockData) return;
    const container = document.getElementById('news-container');
    if (container && mockData.news) {
        container.innerHTML = mockData.news.map(news => `
            <a href="${news.link}" target="_blank" class="news-item" style="text-decoration: none; color: inherit; display: flex; gap: 1.5rem; align-items: stretch; padding: 1.2rem; background: rgba(255,255,255,0.02); border-radius: 8px; border: 1px solid transparent; transition: all 0.2s;">

                <div class="news-content" style="flex: 1; display: flex; flex-direction: column; justify-content: space-between;">
                    <div>
                        <h3 style="transition: color 0.2s; font-size: 1.1rem; line-height: 1.3; margin-bottom: 8px;">${news.title}</h3>
                        <div style="display: flex; flex-wrap: wrap; gap: 6px; margin-top: 6px;">
                            ${news.hashtags ? news.hashtags.split(' ').map(tag => `<span style="font-size: 0.75rem; color: #38bdf8; background: rgba(56, 189, 248, 0.12); padding: 3px 8px; border-radius: 6px; font-weight: 500;">${tag}</span>`).join('') : ''}
                        </div>
                    </div>
                    <div class="news-meta" style="margin-top: 12px; display: flex; gap: 10px; align-items: center; font-size: 0.8rem;">
                        <span style="color: var(--accent-brand); font-weight: bold;">${news.source}</span>
                        <span>|</span>
                        <span style="color: var(--text-secondary);">${news.date}</span>
                    </div>
                </div>
            </a>
        `).join('');
    }
    
    // 키워드 뉴스 함께 호출
    renderKeywordNews();
}

// 4-2. 실시간 키워드별 뉴스 렌더링
function renderKeywordNews() {
    if (!mockData || !mockData.keywordNews) return;
    const container = document.getElementById('keyword-news-container');
    if (!container) return;
    
    container.innerHTML = mockData.keywordNews.map(kwObj => `
        <div class="glass-card keyword-group-card" style="padding: 1.5rem; background: rgba(20, 22, 31, 0.6);">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 1.2rem; border-bottom: 1px solid var(--border-highlight); padding-bottom: 0.8rem;">
                <span style="font-size: 1.2rem; background: rgba(59, 130, 246, 0.15); padding: 4px 10px; border-radius: 8px; color: var(--accent-brand); font-weight: bold;">
                    # ${kwObj.keyword}
                </span>
                <span style="font-size: 0.85rem; color: var(--text-secondary);">관련 인기 뉴스 TOP 3</span>
            </div>
            <div class="news-list" style="gap: 1rem;">
                ${kwObj.news.map(n => `
                    <a href="${n.link}" target="_blank" class="news-item" style="text-decoration: none; color: inherit; display: flex; gap: 1rem; align-items: stretch; padding: 1rem; background: rgba(0,0,0,0.25);">

                        <div style="flex: 1; display: flex; flex-direction: column; justify-content: center;">
                            <h4 style="font-size: 1rem; transition: color 0.2s; line-height: 1.3;">${n.title}</h4>
                            <div style="margin-top: 8px; display: flex; gap: 8px; font-size: 0.75rem; color: var(--text-secondary);">
                                <span style="color: var(--accent-brand);">${n.source}</span>
                                <span>|</span>
                                <span>${n.date}</span>
                            </div>
                        </div>
                    </a>
                `).join('')}
            </div>
        </div>
    `).join('');
}

// 5. 주요 인사 발언 렌더링
function renderQuotes() {
    if (!mockData) return;
    const container = document.getElementById('quotes-container');
    container.innerHTML = mockData.quotes.map(quote => `
        <a href="${quote.link}" target="_blank" class="glass-card quote-card" style="text-decoration: none; color: inherit; display: block;">
            <div class="quote-icon">"</div>
            <p class="quote-text">${quote.text}</p>
            <div class="quote-author">
                <div class="author-avatar" style="background: url('${quote.image}') center/cover; color: transparent; border: 1px solid var(--border-highlight);"></div>
                <div class="author-info">
                    <strong>${quote.author}</strong>
                    <span>${quote.role} · ${quote.date}</span>
                </div>
            </div>
        </a>
    `).join('');
}

// 6. 유튜브 인사이트 렌더링
function renderYoutube() {
    if (!mockData || !mockData.youtube) return;
    const container = document.getElementById('youtube-container');
    if (!container) return;
    
    container.innerHTML = mockData.youtube.map(video => `
        <a href="${video.link}" target="_blank" class="news-item" style="text-decoration: none; color: inherit; display: flex; gap: 1.5rem; align-items: stretch; background: rgba(220, 38, 38, 0.05); border-color: rgba(220, 38, 38, 0.2);">
            ${video.image && video.image.includes('ytimg.com') ? `
            <div style="flex: 0 0 180px; border-radius: 8px; overflow: hidden; position: relative;">
                <img src="${video.image}" alt="Youtube thumbnail" style="width: 100%; height: 100%; object-fit: cover;" />
                <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); background: rgba(0,0,0,0.6); padding: 8px 12px; border-radius: 4px; color: white; display:flex; align-items:center; gap: 5px;">
                   <span style="color: #ef4444; font-weight: bold; font-size: 1.2rem;">▶</span> Play
                </div>
            </div>` : ''}
            <div class="news-content" style="flex: 1; display: flex; flex-direction: column; justify-content: center;">
                <h3 style="transition: color 0.2s;">${video.title}</h3>
                <p style="margin-top: 8px;">${video.summary}</p>
                <div class="news-meta" style="margin-top: 12px; display: flex; gap: 10px; align-items: center;">
                    <span style="color:#ef4444; font-weight: 700;">${video.channel}</span>
                    <span>|</span>
                    <span>업로드: ${video.date}</span>
                </div>
            </div>
        </a>
    `).join('');
}

// ── 7. 탭 전환 제어 로직 (Navigation Tabs) ──
function initTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    if (!tabBtns.length) return;

    // 각 탭별 표시할 섹션 ID 맵핑
    const tabSectionMap = {
        'tab-market': ['market-overview-section', 'sector-performance-section'],
        'tab-companies': ['company-performance-section'],
        'tab-news': ['news-section'],
        'tab-insights': ['quotes-section', 'youtube-section']
    };

    function switchTab(targetTabId) {
        // 버튼 활성화 상태 업데이트
        tabBtns.forEach(btn => {
            if (btn.dataset.tab === targetTabId) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });

        // 모든 섹션을 검사하여 탭 대상에 속하면 표시, 아니면 숨김
        const allSections = document.querySelectorAll('.dashboard-section');
        const activeSectionIds = tabSectionMap[targetTabId] || [];

        allSections.forEach(section => {
            if (activeSectionIds.includes(section.id)) {
                section.classList.remove('hidden-tab');
            } else {
                section.classList.add('hidden-tab');
            }
        });
    }

    // 클릭 리스너 등록
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabId = btn.dataset.tab;
            if (tabId) switchTab(tabId);
        });
    });

    // 초기 상태 셋팅 (기본 active 탭인 tab-market 섹션만 표시)
    switchTab('tab-market');
}

// DOM이 준비되거나 스크립트가 로드되었을 때 탭 기능 활성화
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initTabs);
} else {
    initTabs();
}


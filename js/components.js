// 공통 유틸리티
function formatPercent(data, hidePrice = false) {
    const value = data.pct;
    const price = data.price;
    let html = '';
    
    if (value > 0) html = `<span class="val-up">▲ ${value.toFixed(1)}%</span>`;
    else if (value < 0) html = `<span class="val-down">▼ ${Math.abs(value).toFixed(1)}%</span>`;
    else html = `<span class="val-neutral">- ${value.toFixed(1)}%</span>`;
    
    if (!hidePrice && price && price !== 'N/A') {
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
            <span class="metric-label">${label}<br/><span style="font-size: 0.85em; font-weight: normal; color: #94a3b8;">(${date})</span></span>
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
                    <span class="metric-label">현재가<br/><span style="font-size: 0.85em; font-weight: normal; color: #94a3b8;">(${mockData.dates.current})</span></span>
                    <div class="metric-content">
                        <span class="metric-pct ${getPercentClass(market.changes.today)}" style="margin-bottom: 2px;">
                            ${market.changes.today.pct > 0 ? '▲' : market.changes.today.pct < 0 ? '▼' : ''} ${Math.abs(market.changes.today.pct)}%
                        </span>
                        <span class="metric-value highlight">${market.value}</span>
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
                <div style="font-weight: 500;">${formatPercent(sector.changes.today, true)}</div>
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
                <th style="text-align:left;">자산 (ETF)</th>
                <th>현재가<br/><span style="font-size:0.78em;font-weight:normal;color:#94a3b8;">(${mockData.dates.current})</span></th>
                <th>1일전比<br/><span style="font-size:0.78em;font-weight:normal;color:#94a3b8;">(${mockData.dates.d1})</span></th>
                <th>3일전比<br/><span style="font-size:0.78em;font-weight:normal;color:#94a3b8;">(${mockData.dates.d3})</span></th>
                <th>1주전比<br/><span style="font-size:0.78em;font-weight:normal;color:#94a3b8;">(${mockData.dates.w1})</span></th>
                <th>1달전比<br/><span style="font-size:0.78em;font-weight:normal;color:#94a3b8;">(${mockData.dates.m1})</span></th>
                <th>3달전比<br/><span style="font-size:0.78em;font-weight:normal;color:#94a3b8;">(${mockData.dates.m3})</span></th>
                <th>6달전比<br/><span style="font-size:0.78em;font-weight:normal;color:#94a3b8;">(${mockData.dates.m6})</span></th>
                <th>1년전比<br/><span style="font-size:0.78em;font-weight:normal;color:#94a3b8;">(${mockData.dates.y1})</span></th>
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
            <span class="metric-label">${label}<br/><span style="font-size: 0.85em; font-weight: normal; color: #94a3b8;">(${date})</span></span>
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
                    <span class="metric-label">현재가<br/><span style="font-size: 0.85em; font-weight: normal; color: #94a3b8;">(${mockData.dates.current})</span></span>
                    <div class="metric-content">
                        <span class="metric-pct ${getPercentClass(company.changes.today)}" style="margin-bottom: 2px;">
                            ${company.changes.today.pct > 0 ? '▲' : company.changes.today.pct < 0 ? '▼' : ''} ${Math.abs(company.changes.today.pct)}%
                        </span>
                        <span class="metric-value highlight">${company.value}</span>
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

// ── 탭 전환 제어 로직 (Navigation Tabs) ──
function initTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    if (!tabBtns.length) return;

    const tabSectionMap = {
        'tab-market': ['market-overview-section', 'sector-performance-section'],
        'tab-companies': ['company-performance-section'],
    };

    function switchTab(targetTabId) {
        tabBtns.forEach(btn => {
            btn.classList.toggle('active', btn.dataset.tab === targetTabId);
        });
        const allSections = document.querySelectorAll('.dashboard-section');
        const activeSectionIds = tabSectionMap[targetTabId] || [];
        allSections.forEach(section => {
            section.classList.toggle('hidden-tab', !activeSectionIds.includes(section.id));
        });
    }

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            if (btn.dataset.tab) switchTab(btn.dataset.tab);
        });
    });

    switchTab('tab-market');
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initTabs);
} else {
    initTabs();
}

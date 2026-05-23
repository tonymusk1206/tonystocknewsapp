let mockData = null; 

document.addEventListener("DOMContentLoaded", () => {
    console.log("Tony's Stock Dashboard: DOMContentLoaded");
    const statusDisplay = document.getElementById('base-date-display');
    if (statusDisplay) statusDisplay.innerText = '상태: 자바스크립트 로드됨 (연결 시도 중...)';
    
    updateTime();
    fetchMarketData();
});

async function fetchMarketData() {
    const mainContent = document.querySelector('.main-content');
    const statusDisplay = document.getElementById('base-date-display');
    const originalContent = mainContent.innerHTML;
    
    // 로딩 UI 표시 (더 강력하게)
    mainContent.innerHTML = `
        <div id="loading-overlay" style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 60vh; color: white; background: rgba(0,0,0,0.2); border-radius: 20px;">
            <div class="pulse-dot" style="width: 60px; height: 60px; box-shadow: 0 0 25px var(--accent-brand); background: var(--accent-brand); animation-duration: 1.2s; margin-bottom: 2rem;"></div>
            <h2 style="font-family: var(--font-heading); font-size: 2rem; text-shadow: 0 0 15px rgba(59, 130, 246, 0.6);">통합 네트워크 데이터 분석 중...</h2>
            <p style="color: var(--text-secondary); margin-top: 15px; font-size: 1.1rem;">Render 서버 및 Yahoo Finance와 통신을 시작했습니다. (예상 대기: 5~15초)</p>
            <div style="margin-top: 2rem; padding: 10px 20px; background: rgba(255,255,255,0.05); border-radius: 30px; font-size: 0.9rem; color: #94a3b8;">
                Network: Checking /api/market-data
            </div>
        </div>
    `;
    
    try {
        // 안드로이드 WebView 내부에서 상대 경로 파싱 에러 방지를 위해 절대 경로 우선 적용
        const apiUrl = window.location.origin.includes('http') 
            ? `${window.location.origin}/api/market-data`
            : 'https://tony-stock-news.onrender.com/api/market-data';
            
        console.log("Fetching from:", apiUrl);
        const res = await fetch(apiUrl);
        
        if (!res.ok) {
            throw new Error(`서버 응답 오류 (HTTP ${res.status}) - 서버가 아직 준비되지 않았거나 경로가 잘못되었습니다.`);
        }
        
        mockData = await res.json();
        console.log("Data received:", mockData);
        
        if (mockData.error) throw new Error(`백엔드 내부 오류: ${mockData.error}`);
        
        // 데이터 로드 성공 시
        mainContent.innerHTML = originalContent;
        if (statusDisplay) statusDisplay.innerText = `업데이트: ${mockData.baseDate || '성공'}`;
        
        renderMarkets();
        renderSectors();
        renderCompanies();
        renderNews();
        renderQuotes();
        renderYoutube();
        
    } catch (err) {
        console.error("Fetch Error:", err);
        if (statusDisplay) statusDisplay.innerText = '상태: 연결 실패';
        
        mainContent.innerHTML = `
            <div style="padding: 4rem; background: rgba(239, 68, 68, 0.08); border: 2px dashed rgba(239, 68, 68, 0.3); border-radius: 24px; text-align: center; color: #fca5a5; max-width: 800px; margin: 2rem auto;">
                <div style="font-size: 3rem; margin-bottom: 1.5rem;">⚠️</div>
                <h2 style="margin-bottom: 1rem; color: #ef4444; font-family: var(--font-heading);">데이터를 가져오지 못했습니다</h2>
                <p style="font-size: 1.1rem; line-height: 1.6; margin-bottom: 2rem;">
                    네트워크 연결에 문제가 있거나, 서버(Render)의 초기 가동 시간이 지연되고 있습니다.<br>
                    <strong>상세 에러:</strong> ${err.message}
                </p>
                <button onclick="location.reload()" style="padding: 12px 30px; background: #ef4444; color: white; border: none; border-radius: 50px; font-weight: 600; cursor: pointer; transition: 0.3s; box-shadow: 0 4px 15px rgba(239, 68, 68, 0.4);">다시 시도하기</button>
            </div>
        `;
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

// ── 탭 전환 ──
(function initTabs() {
    const TAB_MAP = {
        'tab-market':    ['market-overview-section', 'sector-performance-section'],
        'tab-companies': ['company-performance-section'],
        'tab-news':      ['news-section'],
        'tab-insights':  ['quotes-section', 'youtube-section'],
        'tab-search':    ['search-section'],
    };
    const ALL_SECTIONS = [
        'market-overview-section','sector-performance-section',
        'company-performance-section','news-section',
        'quotes-section','youtube-section','search-section'
    ];

    function switchTab(tabId) {
        // 탭 버튼 강조
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.tab === tabId);
        });
        // 섹션 표시/숨김
        ALL_SECTIONS.forEach(id => {
            const el = document.getElementById(id);
            if (el) el.style.display = 'none';
        });
        const visible = TAB_MAP[tabId] || [];
        visible.forEach(id => {
            const el = document.getElementById(id);
            if (el) el.style.display = 'block';
        });
    }

    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => switchTab(btn.dataset.tab));
    });
})();

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
        renderTradingViewWidget(data.symbol);
        renderSearchNews(data.news);
        document.getElementById('link-naver-board').href = data.links.naver_board;
        document.getElementById('link-naver-cafe').href  = data.links.naver_cafe;

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

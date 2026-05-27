let mockData = null; 

document.addEventListener("DOMContentLoaded", () => {
    console.log("Tony's Stock Dashboard: DOMContentLoaded");
    const statusDisplay = document.getElementById('base-date-display');
    if (statusDisplay) statusDisplay.innerText = '연결 중...';
    
    fetchMarketData();
});

async function fetchMarketData() {
    const statusDisplay = document.getElementById('base-date-display');
    
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
            Yahoo Finance 데이터 수신 중</p>`;
    document.body.appendChild(loadingEl);
    
    try {
        const apiUrl = `${window.location.origin}/api/market-data`;
            
        const res = await fetch(apiUrl);
        if (!res.ok) throw new Error(`서버 응답 오류 (HTTP ${res.status})`);
        
        mockData = await res.json();
        if (mockData.error) throw new Error(`백엔드 오류: ${mockData.error}`);
        
        if (statusDisplay) statusDisplay.innerText = `업데이트: ${mockData.baseDate || '성공'}`;
        
        renderMarkets();
        renderSectors();
        renderCompanies();
        
    } catch (err) {
        console.error("Fetch Error:", err);
        if (statusDisplay) statusDisplay.innerText = '연결 실패 - 재시도 중...';
        setTimeout(fetchMarketData, 5000);
    } finally {
        const ol = document.getElementById('loading-overlay');
        if (ol) ol.remove();
    }
}

function searchStock(symbol) {
    window.open(`https://finance.yahoo.com/quote/${symbol}`, '_blank');
}

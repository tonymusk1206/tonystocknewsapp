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
        console.log("Fetching from: /api/market-data");
        const res = await fetch('/api/market-data');
        
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

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

// ── 게시판 API 연동 함수들 ──
async function fetchBoardPosts() {
    const container = document.getElementById('board-posts-container');
    if (!container) return;
    
    try {
        container.innerHTML = '<div style="text-align:center; padding:2rem; color:var(--text-secondary);">의견을 불러오는 중...</div>';
        const res = await fetch(`${window.location.origin}/api/board`);
        if (!res.ok) throw new Error('API 응답 실패');
        const posts = await res.json();
        renderBoard(posts);
    } catch (err) {
        console.error("Board Fetch Error:", err);
        container.innerHTML = '<div style="text-align:center; padding:2rem; color:var(--accent-down);">불러오기 실패 (연결 오류)</div>';
    }
}

async function handleBoardSubmit(e) {
    e.preventDefault();
    const nickEl = document.getElementById('board-nickname');
    const pwEl = document.getElementById('board-password');
    const titleEl = document.getElementById('board-post-title');
    const contentEl = document.getElementById('board-post-content');
    
    if (!nickEl || !pwEl || !titleEl || !contentEl) return;
    
    const body = {
        nickname: nickEl.value,
        password: pwEl.value,
        title: titleEl.value,
        content: contentEl.value
    };
    
    try {
        const res = await fetch(`${window.location.origin}/api/board`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });
        const resData = await res.json();
        if (res.ok && resData.success) {
            titleEl.value = '';
            contentEl.value = '';
            fetchBoardPosts();
        } else {
            alert(resData.error || '글 작성에 실패했습니다.');
        }
    } catch (err) {
        console.error("Board Submit Error:", err);
        alert('서버 연결 실패');
    }
}

function openDeleteModal(postId) {
    const modal = document.getElementById('delete-post-modal');
    const idEl = document.getElementById('delete-post-id');
    const pwEl = document.getElementById('delete-post-password');
    
    if (!modal || !idEl || !pwEl) return;
    idEl.value = postId;
    pwEl.value = '';
    modal.style.display = 'flex';
}

async function confirmDeletePost() {
    const idEl = document.getElementById('delete-post-id');
    const pwEl = document.getElementById('delete-post-password');
    const modal = document.getElementById('delete-post-modal');
    
    if (!idEl || !pwEl || !modal) return;
    
    const body = {
        id: idEl.value,
        password: pwEl.value
    };
    
    try {
        const res = await fetch(`${window.location.origin}/api/board/delete`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });
        const resData = await res.json();
        if (res.ok && resData.success) {
            modal.style.display = 'none';
            fetchBoardPosts();
        } else {
            alert(resData.error || '삭제 실패');
        }
    } catch (err) {
        console.error("Board Delete Error:", err);
        alert('서버 연결 실패');
    }
}

document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById('board-write-form');
    if (form) {
        form.addEventListener('submit', handleBoardSubmit);
    }
});

const mockData = {
    baseDate: "2026년 4월 28일 종가 기준",
    // 2. 등락 기간별 구체적 날짜 매핑
    dates: {
        current: "26.04.28",
        d1: "26.04.27",
        d3: "26.04.25",
        w1: "26.04.21",
        m1: "26.03.28",
        m3: "26.01.28",
        m6: "25.10.28",
        y1: "25.04.28"
    },

    // 4. 주요국 증시 현황 (국가별 그룹화용 데이터 구조)
    markets: [
        { name: "S&P 500", region: "미국", ticker: "SPX", value: "5,123.41", changes: { d1: 1.2, d3: -0.5, w1: 2.1, m1: 5.4, m3: 12.3, m6: 15.6, y1: 24.5 } },
        { name: "NASDAQ", region: "미국", ticker: "COMP", value: "16,211.85", changes: { d1: 1.8, d3: -0.8, w1: 3.2, m1: 7.1, m3: 15.2, m6: 18.9, y1: 32.1 } },
        { name: "Dow Jones", region: "미국", ticker: "DJI", value: "38,981.42", changes: { d1: 0.5, d3: -0.2, w1: 1.1, m1: 3.5, m3: 8.7, m6: 11.2, y1: 17.8 } },
        { name: "KOSPI", region: "한국", ticker: "KS11", value: "2,746.51", changes: { d1: -0.4, d3: -1.2, w1: 0.5, m1: -2.1, m3: 3.4, m6: 5.8, y1: 12.3 } },
        { name: "KOSDAQ", region: "한국", ticker: "KQ11", value: "880.20", changes: { d1: 0.2, d3: -1.5, w1: 1.2, m1: -1.5, m3: 5.6, m6: 7.2, y1: 15.4 } },
        { name: "Nikkei 225", region: "일본", ticker: "N225", value: "39,520.10", changes: { d1: 0.9, d3: 1.1, w1: 2.5, m1: 4.8, m3: 10.2, m6: 22.1, y1: 35.6 } },
        { name: "Shanghai Composite", region: "중국", ticker: "SSEC", value: "3,065.25", changes: { d1: -0.8, d3: 0.4, w1: -1.2, m1: 2.5, m3: 6.8, m6: 1.5, y1: -5.4 } }
    ],

    // 1. 미국 전체 11개 스파이더 섹터 적용
    usSectors: [
        { ticker: "XLK", name: "Technology", desc: "기술", value: "215.30", changes: { d1: 2.1, d3: 0.5, w1: 4.2, m1: 8.5, m3: 16.2, m6: 21.5, y1: 42.1 } },
        { ticker: "XLI", name: "Industrials", desc: "산업재", value: "118.42", changes: { d1: 0.5, d3: 1.2, w1: 2.4, m1: 4.5, m3: 11.2, m6: 15.8, y1: 22.5 } },
        { ticker: "XLY", name: "Cons. Discr.", desc: "임의소비재", value: "185.12", changes: { d1: 1.1, d3: -1.2, w1: 1.8, m1: 4.2, m3: 9.5, m6: 12.8, y1: 25.6 } },
        { ticker: "XLP", name: "Cons. Staples", desc: "필수소비재", value: "78.40", changes: { d1: -0.2, d3: 0.5, w1: -1.1, m1: 1.5, m3: 3.2, m6: 5.8, y1: 8.4 } },
        { ticker: "XLE", name: "Energy", desc: "에너지", value: "95.60", changes: { d1: -1.2, d3: -2.5, w1: 1.1, m1: -3.2, m3: -5.6, m6: 2.1, y1: 8.5 } },
        { ticker: "XLV", name: "Health Care", desc: "헬스케어", value: "145.80", changes: { d1: 0.4, d3: 1.2, w1: -0.5, m1: 2.1, m3: 4.5, m6: 5.2, y1: 11.2 } },
        { ticker: "XLF", name: "Financials", desc: "금융", value: "42.10", changes: { d1: 1.5, d3: 0.8, w1: 2.5, m1: 5.6, m3: 12.1, m6: 16.5, y1: 22.4 } },
        { ticker: "XLC", name: "Comm. Svcs", desc: "통신", value: "85.20", changes: { d1: 1.8, d3: -0.5, w1: 3.4, m1: 9.5, m3: 18.2, m6: 25.1, y1: 35.8 } },
        { ticker: "XLU", name: "Utilities", desc: "유틸리티", value: "65.30", changes: { d1: -0.8, d3: 0.2, w1: -1.5, m1: 1.2, m3: -2.5, m6: 1.8, y1: 5.6 } },
        { ticker: "XLB", name: "Materials", desc: "소재", value: "88.90", changes: { d1: 0.7, d3: 1.5, w1: 2.1, m1: 3.8, m3: 8.5, m6: 11.2, y1: 18.5 } },
        { ticker: "XLRE", name: "Real Estate", desc: "부동산", value: "41.50", changes: { d1: -1.5, d3: -2.5, w1: -3.2, m1: 1.5, m3: 5.6, m6: 8.2, y1: 12.5 } }
    ],
    
    // 6. 한국 섹터 ETF 목록 확대 (기존 5->10종)
    krSectors: [
        { ticker: "229200", name: "IT (KODEX)", desc: "정보기술", value: "42,100", changes: { d1: 1.2, d3: -1.2, w1: 2.8, m1: 5.5, m3: 12.1, m6: 15.8, y1: 28.5 } },
        { ticker: "091160", name: "Semi (KODEX)", desc: "반도체", value: "38,500", changes: { d1: 1.5, d3: -2.1, w1: 3.5, m1: 6.2, m3: 14.5, m6: 18.2, y1: 35.6 } },
        { ticker: "091180", name: "Auto (KODEX)", desc: "자동차", value: "24,500", changes: { d1: 0.8, d3: 1.5, w1: -1.2, m1: 4.5, m3: 11.2, m6: 15.6, y1: 28.5 } },
        { ticker: "091170", name: "Bank (KODEX)", desc: "은행", value: "8,950", changes: { d1: 2.1, d3: 3.5, w1: 5.6, m1: 12.5, m3: 21.4, m6: 18.5, y1: 38.6 } },
        { ticker: "269620", name: "Health (KODEX)", desc: "헬스케어", value: "28,200", changes: { d1: -0.5, d3: 0.2, w1: 1.5, m1: 5.2, m3: 8.5, m6: 9.2, y1: -2.5 } },
        { ticker: "117680", name: "Steel (KODEX)", desc: "철강", value: "18,400", changes: { d1: 0.5, d3: 1.2, w1: 2.1, m1: -1.5, m3: 3.5, m6: 5.8, y1: 12.5 } },
        { ticker: "117460", name: "Chem (KODEX)", desc: "에너지화학", value: "21,500", changes: { d1: -1.2, d3: -2.5, w1: -1.2, m1: 2.5, m3: 8.2, m6: -5.4, y1: -8.5 } },
        { ticker: "117700", name: "Const (KODEX)", desc: "건설", value: "11,200", changes: { d1: -0.8, d3: -1.5, w1: -2.5, m1: -5.6, m3: -8.5, m6: -12.4, y1: -18.5 } },
        { ticker: "266360", name: "Media (KODEX)", desc: "미디어", value: "15,800", changes: { d1: 1.1, d3: 2.5, w1: -0.5, m1: 3.2, m3: 5.6, m6: -2.1, y1: -5.4 } },
        { ticker: "266410", name: "Staples (KODEX)", desc: "필수소비재", value: "12,100", changes: { d1: 0.2, d3: 0.5, w1: -0.2, m1: 1.5, m3: 2.8, m6: 4.5, y1: 6.8 } }
    ],

    // 7. 섹터별 주요 대표 기업 (큰 그룹 섹터 안 5개씩)
    companiesBySector: {
        "Technology (기술/반도체)": [
            { name: "Apple", ticker: "AAPL", value: "$173.50", changes: { d1: 1.5, d3: -1.2, w1: 2.4, m1: 5.6, m3: 12.4, m6: 8.5, y1: 22.1 }, logo: "https://upload.wikimedia.org/wikipedia/commons/f/fa/Apple_logo_black.svg" },
            { name: "NVIDIA", ticker: "NVDA", value: "$852.12", changes: { d1: 4.2, d3: 8.5, w1: 15.2, m1: 32.5, m3: 85.6, m6: 124.5, y1: 285.6 }, logo: "https://upload.wikimedia.org/wikipedia/commons/2/21/Nvidia_logo.svg" },
            { name: "Microsoft", ticker: "MSFT", value: "$415.20", changes: { d1: 1.1, d3: 0.5, w1: 3.2, m1: 6.5, m3: 14.2, m6: 21.5, y1: 55.4 }, logo: "https://upload.wikimedia.org/wikipedia/commons/4/44/Microsoft_logo.svg" },
            { name: "삼성전자", ticker: "005930", value: "₩78,500", changes: { d1: 1.5, d3: -0.8, w1: 2.5, m1: 5.6, m3: 11.2, m6: -2.5, y1: 18.5 }, logo: "https://upload.wikimedia.org/wikipedia/commons/2/24/Samsung_Logo.svg" },
            { name: "SK하이닉스", ticker: "000660", value: "₩175,000", changes: { d1: 2.8, d3: 4.5, w1: 8.5, m1: 18.2, m3: 42.5, m6: 65.2, y1: 115.8 }, logo: null }
        ],
        "Automotive (자동차)": [
            { name: "Tesla", ticker: "TSLA", value: "$373.00", changes: { d1: -2.5, d3: -5.6, w1: -8.5, m1: -15.2, m3: -25.6, m6: -35.2, y1: -12.5 }, logo: "https://upload.wikimedia.org/wikipedia/commons/b/bd/Tesla_Motors.svg" },
            { name: "현대차", ticker: "005380", value: "₩245,500", changes: { d1: -1.2, d3: 2.5, w1: -0.5, m1: 8.5, m3: 28.5, m6: 35.6, y1: 58.2 }, logo: null },
            { name: "기아", ticker: "000270", value: "₩118,500", changes: { d1: -0.8, d3: 3.2, w1: 1.5, m1: 12.5, m3: 32.5, m6: 42.1, y1: 65.8 }, logo: null },
            { name: "Toyota", ticker: "TM", value: "$235.40", changes: { d1: 1.5, d3: 2.8, w1: 5.6, m1: 12.4, m3: 25.6, m6: 45.2, y1: 68.5 }, logo: null },
            { name: "Ford", ticker: "F", value: "$12.80", changes: { d1: 0.5, d3: 1.2, w1: -1.5, m1: 2.5, m3: 8.5, m6: 11.2, y1: 5.6 }, logo: null }
        ],
        "Financials (금융)": [
            { name: "JPMorgan", ticker: "JPM", value: "$195.50", changes: { d1: 1.2, d3: 2.5, w1: 3.8, m1: 8.5, m3: 18.5, m6: 25.6, y1: 38.5 }, logo: null },
            { name: "Berkshire H.", ticker: "BRK.B", value: "$415.80", changes: { d1: 0.8, d3: 1.5, w1: 2.1, m1: 5.6, m3: 12.5, m6: 18.5, y1: 28.5 }, logo: null },
            { name: "KB금융", ticker: "105560", value: "₩68,200", changes: { d1: 2.5, d3: 4.5, w1: 6.8, m1: 15.2, m3: 35.6, m6: 28.5, y1: 45.2 }, logo: null },
            { name: "신한지주", ticker: "055550", value: "₩48,500", changes: { d1: 1.8, d3: 3.2, w1: 5.1, m1: 12.8, m3: 28.5, m6: 22.1, y1: 38.5 }, logo: null },
            { name: "Visa", ticker: "V", value: "$278.40", changes: { d1: 0.5, d3: 1.2, w1: 2.5, m1: 4.8, m3: 11.2, m6: 15.6, y1: 25.8 }, logo: null }
        ]
    },

    // 8. 날짜 및 링크가 적용된 뉴스 (10번: 이미지 추가 반영)
    news: [
        { 
            title: "연준(Fed) 금리 동결 결정, 시장은 신중론", 
            summary: "미국 연방준비제도(Fed)가 기준금리를 현행으로 동결하며 인플레 대책에 대한 매파적 시그널을 확인했습니다.", 
            source: "Bloomberg", 
            date: "2026.04.28",
            time: "2시간 전",
            link: "https://www.bloomberg.com",
            image: "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=400&q=80"
        },
        { 
            title: "AI 반도체 수요 폭발, 관련주 랠리 돌풍", 
            summary: "글로벌 빅테크 기업들의 AI 반도체 수급 전쟁이 심화되면서 주요 공급망 관련주들이 연일 신고가를 경신중입니다.", 
            source: "Financial Times", 
            date: "2026.04.28",
            time: "4시간 전",
            link: "https://www.ft.com",
            image: "https://images.unsplash.com/photo-1518770660439-4636190af475?w=400&q=80"
        },
        { 
            title: "K-밸류업 실효성 논란, 투심 향방은?", 
            summary: "정부 주도의 밸류업 지수 발표 이후 실제 시장의 반응과 기관 투자자들의 평가가 극명하게 엇갈리고 있습니다.", 
            source: "한국경제", 
            date: "2026.04.27",
            time: "15시간 전",
            link: "https://www.hankyung.com",
            image: "https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?w=400&q=80"
        }
    ],

    // 9. 날짜 및 원문 링크가 적용된 인사 발언
    quotes: [
        {
            text: "\"인플레이션이라는 야수가 아직 완전히 길들여지지 않았습니다. 우리는 데이터를 기반으로 신중을 기할 것입니다.\"",
            author: "Jerome Powell",
            role: "Fed Chair",
            date: "2026.04.27",
            link: "https://www.federalreserve.gov",
            image: "https://images.unsplash.com/photo-1558222218-b7b54eede3f3?w=100&q=80" // Placeholder for avatar
        },
        {
            text: "\"범용 인공지능(AGI)의 도래는 상상보다 빠를 것이며, 모든 산업은 이를 대비해 구조를 바꿔야 합니다.\"",
            author: "Sam Altman",
            role: "OpenAI CEO",
            date: "2026.04.25",
            link: "https://openai.com",
            image: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&q=80" // Placeholder
        },
        {
            text: "\"시장의 단기적 흔들림에 일희일비하지 마십시오. 훌륭한 비즈니스 모델은 결국 제자리를 찾습니다.\"",
            author: "Warren Buffett",
            role: "Berkshire Hathaway CEO",
            date: "2026.04.21",
            link: "https://www.berkshirehathaway.com",
            image: "https://images.unsplash.com/photo-1556157382-97eda2f9e2bf?w=100&q=80" // Placeholder
        }
    ]
};

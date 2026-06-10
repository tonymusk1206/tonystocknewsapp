const mockData = {
    baseDate: "2026년 4월 28일 종가 기준",
    // 2. 등락 기간별 구체적 날짜 매핑 (미국 / 한국 분리)
    dates: {
        us: {
            current: "26.04.28",
            d3: "26.04.25",
            w1: "26.04.21",
            m1: "26.03.28",
            m3: "26.01.28",
            m6: "25.10.28",
            y1: "25.04.28", y3: "23.04.28"
        },
        kr: {
            current: "26.04.28",
            d3: "26.04.25",
            w1: "26.04.21",
            m1: "26.03.28",
            m3: "26.01.28",
            m6: "25.10.28",
            y1: "25.04.28", y3: "23.04.28"
        }
    },

    // 4. 주요국 증시 현황 (국가별 그룹화용 데이터 구조)
    markets: [
        { name: "S&P 500", region: "미국", ticker: "SPX", value: "5,123.41", changes: { today: {pct: 0.8, price: "5,082.50"}, d3: {pct: -0.5, price: "5,148.91"}, w1: {pct: 2.1, price: "5,018.23"}, m1: {pct: 5.4, price: "4,861.42"}, m3: {pct: 12.3, price: "4,562.18"}, m6: {pct: 15.6, price: "4,431.25"}, y1: {pct: 24.5, price: "4,115.52"}, y3: {pct: 24.5, price: "4,115.52"} } },
        { name: "NASDAQ", region: "미국", ticker: "COMP", value: "16,211.85", changes: { today: {pct: 1.1, price: "16,035.20"}, d3: {pct: -0.8, price: "16,342.22"}, w1: {pct: 3.2, price: "15,709.30"}, m1: {pct: 7.1, price: "15,137.58"}, m3: {pct: 15.2, price: "14,071.92"}, m6: {pct: 18.9, price: "13,634.02"}, y1: {pct: 32.1, price: "12,271.40"}, y3: {pct: 32.1, price: "12,271.40"} } },
        { name: "Dow Jones", region: "미국", ticker: "DJI", value: "38,981.42", changes: { today: {pct: 0.3, price: "38,864.52"}, d3: {pct: -0.2, price: "39,059.32"}, w1: {pct: 1.1, price: "38,557.28"}, m1: {pct: 3.5, price: "37,664.18"}, m3: {pct: 8.7, price: "35,860.48"}, m6: {pct: 11.2, price: "35,054.34"}, y1: {pct: 17.8, price: "33,091.22"}, y3: {pct: 17.8, price: "33,091.22"} } },
        { name: "KOSPI", region: "한국", ticker: "KS11", value: "2,746.51", changes: { today: {pct: -0.2, price: "2,752.00"}, d3: {pct: -1.2, price: "2,779.88"}, w1: {pct: 0.5, price: "2,732.84"}, m1: {pct: -2.1, price: "2,804.40"}, m3: {pct: 3.4, price: "2,656.41"}, m6: {pct: 5.8, price: "2,596.89"}, y1: {pct: 12.3, price: "2,445.68"}, y3: {pct: 12.3, price: "2,445.68"} } },
        { name: "KOSDAQ", region: "한국", ticker: "KQ11", value: "880.20", changes: { today: {pct: 0.1, price: "879.32"}, d3: {pct: -1.5, price: "893.62"}, w1: {pct: 1.2, price: "869.76"}, m1: {pct: -1.5, price: "893.62"}, m3: {pct: 5.6, price: "833.52"}, m6: {pct: 7.2, price: "820.99"}, y1: {pct: 15.4, price: "762.74"}, y3: {pct: 15.4, price: "762.74"} } },
        { name: "Nikkei 225", region: "일본", ticker: "N225", value: "39,520.10", changes: { today: {pct: 0.5, price: "39,322.60"}, d3: {pct: 1.1, price: "39,083.58"}, w1: {pct: 2.5, price: "38,556.68"}, m1: {pct: 4.8, price: "37,709.92"}, m3: {pct: 10.2, price: "35,862.88"}, m6: {pct: 22.1, price: "32,366.18"}, y1: {pct: 35.6, price: "29,144.02"}, y3: {pct: 35.6, price: "29,144.02"} } },
        { name: "Shanghai Composite", region: "중국", ticker: "SSEC", value: "3,065.25", changes: { today: {pct: -0.4, price: "3,077.48"}, d3: {pct: 0.4, price: "3,052.98"}, w1: {pct: -1.2, price: "3,102.48"}, m1: {pct: 2.5, price: "2,990.48"}, m3: {pct: 6.8, price: "2,870.08"}, m6: {pct: 1.5, price: "3,019.96"}, y1: {pct: -5.4, price: "3,240.90"}, y3: {pct: -5.4, price: "3,240.90"} } }
    ],

    // 1. 미국 전체 11개 스파이더 섹터 적용
    usSectors: [
        { ticker: "SOXX", name: "Semiconductors", desc: "반도체", value: "220.50", changes: { today: {pct: 1.8, price: "216.60"}, d3: {pct: 1.2, price: "217.88"}, w1: {pct: 5.5, price: "209.00"}, m1: {pct: 10.2, price: "200.09"}, m3: {pct: 18.5, price: "186.08"}, m6: {pct: 25.8, price: "175.28"}, y1: {pct: 48.2, price: "148.78"}, y3: {pct: 48.2, price: "148.78"} } },
        { ticker: "IGV", name: "Software", desc: "소프트웨어", value: "95.80", changes: { today: {pct: 1.2, price: "94.66"}, d3: {pct: 0.8, price: "95.04"}, w1: {pct: 3.8, price: "92.29"}, m1: {pct: 7.5, price: "89.12"}, m3: {pct: 14.8, price: "83.45"}, m6: {pct: 20.2, price: "79.70"}, y1: {pct: 38.5, price: "69.17"}, y3: {pct: 38.5, price: "69.17"} } },
        { ticker: "XLK", name: "Technology", desc: "기술", value: "215.30", changes: { today: {pct: 1.4, price: "212.33"}, d3: {pct: 0.5, price: "214.22"}, w1: {pct: 4.2, price: "206.62"}, m1: {pct: 8.5, price: "198.43"}, m3: {pct: 16.2, price: "185.28"}, m6: {pct: 21.5, price: "177.11"}, y1: {pct: 42.1, price: "151.51"}, y3: {pct: 42.1, price: "151.51"} } },
        { ticker: "XLI", name: "Industrials", desc: "산업재", value: "118.42", changes: { today: {pct: 0.3, price: "118.07"}, d3: {pct: 1.2, price: "117.02"}, w1: {pct: 2.4, price: "115.64"}, m1: {pct: 4.5, price: "113.34"}, m3: {pct: 11.2, price: "106.49"}, m6: {pct: 15.8, price: "102.26"}, y1: {pct: 22.5, price: "96.67"}, y3: {pct: 22.5, price: "96.67"} } },
        { ticker: "XLY", name: "Cons. Discr.", desc: "임의소비재", value: "185.12", changes: { today: {pct: 0.7, price: "183.83"}, d3: {pct: -1.2, price: "187.38"}, w1: {pct: 1.8, price: "181.85"}, m1: {pct: 4.2, price: "177.66"}, m3: {pct: 9.5, price: "169.06"}, m6: {pct: 12.8, price: "164.11"}, y1: {pct: 25.6, price: "147.39"}, y3: {pct: 25.6, price: "147.39"} } },
        { ticker: "XLP", name: "Cons. Staples", desc: "필수소비재", value: "78.40", changes: { today: {pct: -0.1, price: "78.48"}, d3: {pct: 0.5, price: "77.99"}, w1: {pct: -1.1, price: "79.28"}, m1: {pct: 1.5, price: "77.24"}, m3: {pct: 3.2, price: "75.97"}, m6: {pct: 5.8, price: "74.10"}, y1: {pct: 8.4, price: "72.33"}, y3: {pct: 8.4, price: "72.33"} } },
        { ticker: "XLE", name: "Energy", desc: "에너지", value: "95.60", changes: { today: {pct: -0.8, price: "96.37"}, d3: {pct: -2.5, price: "98.05"}, w1: {pct: 1.1, price: "94.56"}, m1: {pct: -3.2, price: "98.76"}, m3: {pct: -5.6, price: "101.27"}, m6: {pct: 2.1, price: "93.63"}, y1: {pct: 8.5, price: "88.11"}, y3: {pct: 8.5, price: "88.11"} } },
        { ticker: "XLV", name: "Health Care", desc: "헬스케어", value: "145.80", changes: { today: {pct: 0.2, price: "145.51"}, d3: {pct: 1.2, price: "144.07"}, w1: {pct: -0.5, price: "146.53"}, m1: {pct: 2.1, price: "142.80"}, m3: {pct: 4.5, price: "139.52"}, m6: {pct: 5.2, price: "138.59"}, y1: {pct: 11.2, price: "131.12"}, y3: {pct: 11.2, price: "131.12"} } },
        { ticker: "XLF", name: "Financials", desc: "금융", value: "42.10", changes: { today: {pct: 0.9, price: "41.72"}, d3: {pct: 0.8, price: "41.76"}, w1: {pct: 2.5, price: "41.07"}, m1: {pct: 5.6, price: "39.87"}, m3: {pct: 12.1, price: "37.56"}, m6: {pct: 16.5, price: "36.14"}, y1: {pct: 22.4, price: "34.39"}, y3: {pct: 22.4, price: "34.39"} } },
        { ticker: "XLC", name: "Comm. Svcs", desc: "통신", value: "85.20", changes: { today: {pct: 1.2, price: "84.19"}, d3: {pct: -0.5, price: "85.63"}, w1: {pct: 3.4, price: "82.40"}, m1: {pct: 9.5, price: "77.81"}, m3: {pct: 18.2, price: "72.08"}, m6: {pct: 25.1, price: "68.11"}, y1: {pct: 35.8, price: "62.74"}, y3: {pct: 35.8, price: "62.74"} } },
        { ticker: "XLU", name: "Utilities", desc: "유틸리티", value: "65.30", changes: { today: {pct: -0.5, price: "65.63"}, d3: {pct: 0.2, price: "65.17"}, w1: {pct: -1.5, price: "66.29"}, m1: {pct: 1.2, price: "64.52"}, m3: {pct: -2.5, price: "66.97"}, m6: {pct: 1.8, price: "64.14"}, y1: {pct: 5.6, price: "61.84"}, y3: {pct: 5.6, price: "61.84"} } },
        { ticker: "XLB", name: "Materials", desc: "소재", value: "88.90", changes: { today: {pct: 0.4, price: "88.55"}, d3: {pct: 1.5, price: "87.59"}, w1: {pct: 2.1, price: "87.07"}, m1: {pct: 3.8, price: "85.65"}, m3: {pct: 8.5, price: "81.94"}, m6: {pct: 11.2, price: "79.95"}, y1: {pct: 18.5, price: "75.02"}, y3: {pct: 18.5, price: "75.02"} } },
        { ticker: "XLRE", name: "Real Estate", desc: "부동산", value: "41.50", changes: { today: {pct: -0.9, price: "41.87"}, d3: {pct: -2.5, price: "42.56"}, w1: {pct: -3.2, price: "42.87"}, m1: {pct: 1.5, price: "40.89"}, m3: {pct: 5.6, price: "39.30"}, m6: {pct: 8.2, price: "38.35"}, y1: {pct: 12.5, price: "36.89"}, y3: {pct: 12.5, price: "36.89"} } }
    ],

    // 미국 시가총액 분류별 추이 (Vanguard ETF)
    usMarketCap: [
        { ticker: "VV", yahoo_ticker: "VV", name: "Large Cap", desc: "대형주", capRange: "시가총액 상위 85%", topCompanies: "NVIDIA, Apple, Microsoft, Amazon, Alphabet", value: "235.40", changes: { today: {pct: 0.9, price: "233.28"}, d3: {pct: 0.6, price: "234.00"}, w1: {pct: 3.2, price: "228.10"}, m1: {pct: 6.8, price: "220.41"}, m3: {pct: 13.5, price: "207.40"}, m6: {pct: 18.2, price: "199.15"}, y1: {pct: 28.5, price: "183.27"}, y3: {pct: 28.5, price: "183.27"} } },
        { ticker: "VO", yahoo_ticker: "VO", name: "Mid Cap", desc: "중형주", capRange: "시가총액 70~85%", topCompanies: "Smurfit WestRock, Williams-Sonoma, Deckers, Carlisle, Targa Resources", value: "248.60", changes: { today: {pct: 0.5, price: "247.36"}, d3: {pct: 1.2, price: "245.66"}, w1: {pct: 2.1, price: "243.48"}, m1: {pct: 4.5, price: "237.89"}, m3: {pct: 9.8, price: "226.41"}, m6: {pct: 14.5, price: "217.12"}, y1: {pct: 22.1, price: "203.60"}, y3: {pct: 22.1, price: "203.60"} } },
        { ticker: "VB", yahoo_ticker: "VB", name: "Small Cap", desc: "소형주", capRange: "시가총액 하위 15%", topCompanies: "Vaxcyte, Comfort Systems, FTAI Aviation, Sprouts Farmers, Saia", value: "215.80", changes: { today: {pct: 0.3, price: "215.15"}, d3: {pct: 1.5, price: "212.61"}, w1: {pct: 1.8, price: "212.00"}, m1: {pct: 3.2, price: "209.12"}, m3: {pct: 7.5, price: "200.74"}, m6: {pct: 11.8, price: "193.02"}, y1: {pct: 18.5, price: "182.11"}, y3: {pct: 18.5, price: "182.11"} } }
    ],
    
    // 미국 투자 스타일 및 대표 주식 추이 (Vanguard/iShares)
    usStyle: [
        {
            etf: { ticker: "VUG", yahoo_ticker: "VUG", name: "Growth ETF", desc: "대형 성장주 ETF", strategy: "성장/기술/혁신", value: "290.50", changes: { today: {pct: 1.2, price: "287.05"}, d3: {pct: 0.8, price: "288.20"}, w1: {pct: 2.5, price: "283.41"}, m1: {pct: 6.2, price: "273.54"}, m3: {pct: 12.5, price: "258.22"}, m6: {pct: 18.2, price: "245.72"}, y1: {pct: 28.5, price: "226.07"}, y3: {pct: 28.5, price: "226.07"} } },
            stocks: [
                { ticker: "MSFT", yahoo_ticker: "MSFT", name: "Microsoft", value: "415.20", changes: { today: {pct: 0.6, price: "412.72"}, d3: {pct: 0.5, price: "413.13"}, w1: {pct: 3.2, price: "402.32"}, m1: {pct: 6.5, price: "389.86"}, m3: {pct: 14.2, price: "363.57"}, m6: {pct: 21.5, price: "341.73"}, y1: {pct: 55.4, price: "267.18"}, y3: {pct: 55.4, price: "267.18"} } },
                { ticker: "AAPL", yahoo_ticker: "AAPL", name: "Apple", value: "173.50", changes: { today: {pct: 0.9, price: "171.95"}, d3: {pct: -1.2, price: "175.62"}, w1: {pct: 2.4, price: "169.44"}, m1: {pct: 5.6, price: "164.30"}, m3: {pct: 12.4, price: "154.36"}, m6: {pct: 8.5, price: "159.91"}, y1: {pct: 22.1, price: "142.10"}, y3: {pct: 22.1, price: "142.10"} } },
                { ticker: "NVDA", yahoo_ticker: "NVDA", name: "NVIDIA", value: "852.12", changes: { today: {pct: 2.8, price: "828.92"}, d3: {pct: 8.5, price: "785.40"}, w1: {pct: 15.2, price: "740.02"}, m1: {pct: 32.5, price: "643.11"}, m3: {pct: 85.6, price: "459.44"}, m6: {pct: 124.5, price: "379.65"}, y1: {pct: 285.6, price: "221.22"}, y3: {pct: 285.6, price: "221.22"} } }
            ]
        },
        {
            etf: { ticker: "VTV", yahoo_ticker: "VTV", name: "Value ETF", desc: "대형 가치주 ETF", strategy: "금융/에너지/가치", value: "155.40", changes: { today: {pct: 0.4, price: "154.78"}, d3: {pct: 0.5, price: "154.62"}, w1: {pct: 1.2, price: "153.55"}, m1: {pct: 3.8, price: "149.71"}, m3: {pct: 7.5, price: "144.55"}, m6: {pct: 11.2, price: "139.75"}, y1: {pct: 16.5, price: "133.39"}, y3: {pct: 16.5, price: "133.39"} } },
            stocks: [
                { ticker: "BRK-B", yahoo_ticker: "BRK-B", name: "Berkshire H.", value: "415.80", changes: { today: {pct: 0.4, price: "414.14"}, d3: {pct: 1.5, price: "409.66"}, w1: {pct: 2.1, price: "407.25"}, m1: {pct: 5.6, price: "393.75"}, m3: {pct: 12.5, price: "369.60"}, m6: {pct: 18.5, price: "350.97"}, y1: {pct: 28.5, price: "323.58"}, y3: {pct: 28.5, price: "323.58"} } },
                { ticker: "JPM", yahoo_ticker: "JPM", name: "JPMorgan", value: "195.50", changes: { today: {pct: 0.7, price: "194.14"}, d3: {pct: 2.5, price: "190.73"}, w1: {pct: 3.8, price: "188.34"}, m1: {pct: 8.5, price: "180.28"}, m3: {pct: 18.5, price: "164.98"}, m6: {pct: 25.6, price: "155.65"}, y1: {pct: 38.5, price: "141.16"}, y3: {pct: 38.5, price: "141.16"} } },
                { ticker: "XOM", yahoo_ticker: "XOM", name: "Exxon Mobil", value: "115.30", changes: { today: {pct: 0.5, price: "114.72"}, d3: {pct: -1.2, price: "116.70"}, w1: {pct: 1.8, price: "113.26"}, m1: {pct: 4.5, price: "110.33"}, m3: {pct: 6.8, price: "107.95"}, m6: {pct: 8.2, price: "106.56"}, y1: {pct: 12.5, price: "102.48"}, y3: {pct: 12.5, price: "102.48"} } }
            ]
        },
        {
            etf: { ticker: "USMV", yahoo_ticker: "USMV", name: "Min Vol ETF", desc: "경기 방어주 ETF", strategy: "저변동성/헬스/생필품", value: "78.20", changes: { today: {pct: 0.2, price: "78.04"}, d3: {pct: -0.5, price: "78.59"}, w1: {pct: 1.1, price: "77.34"}, y1: {pct: 8.5, price: "72.07"}, y3: {pct: 8.5, price: "72.07"}, m1: {pct: 2.5, price: "76.29"}, m3: {pct: 5.2, price: "74.33"}, m6: {pct: 6.8, price: "73.22"} } },
            stocks: [
                { ticker: "JNJ", yahoo_ticker: "JNJ", name: "Johnson & Johnson", value: "155.20", changes: { today: {pct: 0.1, price: "155.04"}, d3: {pct: 0.5, price: "154.42"}, w1: {pct: -0.8, price: "156.45"}, m1: {pct: 1.5, price: "152.90"}, m3: {pct: 3.2, price: "150.38"}, m6: {pct: 5.4, price: "147.24"}, y1: {pct: 6.8, price: "145.31"}, y3: {pct: 6.8, price: "145.31"} } },
                { ticker: "PG", yahoo_ticker: "PG", name: "Procter & Gamble", value: "160.40", changes: { today: {pct: 0.3, price: "159.92"}, d3: {pct: 0.8, price: "159.12"}, w1: {pct: -0.5, price: "161.20"}, m1: {pct: 2.1, price: "157.09"}, m3: {pct: 4.5, price: "153.49"}, m6: {pct: 5.8, price: "151.60"}, y1: {pct: 9.2, price: "146.88"}, y3: {pct: 9.2, price: "146.88"} } },
                { ticker: "KO", yahoo_ticker: "KO", name: "Coca-Cola", value: "60.20", changes: { today: {pct: 0.1, price: "60.14"}, d3: {pct: 0.5, price: "59.90"}, w1: {pct: -0.2, price: "60.32"}, m1: {pct: 1.2, price: "59.48"}, m3: {pct: 2.5, price: "58.73"}, m6: {pct: 4.2, price: "57.77"}, y1: {pct: 6.8, price: "56.36"}, y3: {pct: 6.8, price: "56.36"} } }
            ]
        }
    ],

    // 6. 한국 섹터 ETF 목록 확대 (기존 5->10종)
    krSectors: [
        { ticker: "229200", name: "IT (KODEX)", desc: "정보기술", value: "42,100", changes: { today: {pct: 0.8, price: "41,763"}, d3: {pct: -1.2, price: "42,614"}, w1: {pct: 2.8, price: "40,953"}, m1: {pct: 5.5, price: "39,905"}, m3: {pct: 12.1, price: "37,555"}, m6: {pct: 15.8, price: "36,358"}, y1: {pct: 28.5, price: "32,763"}, y3: {pct: 28.5, price: "32,763"} } },
        { ticker: "091160", name: "Semi (KODEX)", desc: "반도체", value: "38,500", changes: { today: {pct: 1.0, price: "38,118"}, d3: {pct: -2.1, price: "39,326"}, w1: {pct: 3.5, price: "37,198"}, m1: {pct: 6.2, price: "36,253"}, m3: {pct: 14.5, price: "33,624"}, m6: {pct: 18.2, price: "32,572"}, y1: {pct: 35.6, price: "28,392"}, y3: {pct: 35.6, price: "28,392"} } },
        { ticker: "091180", name: "Auto (KODEX)", desc: "자동차", value: "24,500", changes: { today: {pct: 0.5, price: "24,378"}, d3: {pct: 1.5, price: "24,137"}, w1: {pct: -1.2, price: "24,797"}, m1: {pct: 4.5, price: "23,445"}, m3: {pct: 11.2, price: "22,032"}, m6: {pct: 15.6, price: "21,194"}, y1: {pct: 28.5, price: "19,066"}, y3: {pct: 28.5, price: "19,066"} } },
        { ticker: "091170", name: "Bank (KODEX)", desc: "은행", value: "8,950", changes: { today: {pct: 1.4, price: "8,826"}, d3: {pct: 3.5, price: "8,647"}, w1: {pct: 5.6, price: "8,476"}, m1: {pct: 12.5, price: "7,956"}, m3: {pct: 21.4, price: "7,372"}, m6: {pct: 18.5, price: "7,551"}, y1: {pct: 38.6, price: "6,455"}, y3: {pct: 38.6, price: "6,455"} } },
        { ticker: "269620", name: "Health (KODEX)", desc: "헬스케어", value: "28,200", changes: { today: {pct: -0.3, price: "28,285"}, d3: {pct: 0.2, price: "28,144"}, w1: {pct: 1.5, price: "27,783"}, m1: {pct: 5.2, price: "26,806"}, m3: {pct: 8.5, price: "25,990"}, m6: {pct: 9.2, price: "25,825"}, y1: {pct: -2.5, price: "28,923"}, y3: {pct: -2.5, price: "28,923"} } },
        { ticker: "117680", name: "Steel (KODEX)", desc: "철강", value: "18,400", changes: { today: {pct: 0.2, price: "18,363"}, d3: {pct: 1.2, price: "18,182"}, w1: {pct: 2.1, price: "18,021"}, m1: {pct: -1.5, price: "18,680"}, m3: {pct: 3.5, price: "17,778"}, m6: {pct: 5.8, price: "17,391"}, y1: {pct: 12.5, price: "16,356"}, y3: {pct: 12.5, price: "16,356"} } },
        { ticker: "117460", name: "Chem (KODEX)", desc: "에너지화학", value: "21,500", changes: { today: {pct: -0.7, price: "21,651"}, d3: {pct: -2.5, price: "22,051"}, w1: {pct: -1.2, price: "21,761"}, m1: {pct: 2.5, price: "20,976"}, m3: {pct: 8.2, price: "19,872"}, m6: {pct: -5.4, price: "22,726"}, y1: {pct: -8.5, price: "23,497"}, y3: {pct: -8.5, price: "23,497"} } },
        { ticker: "117700", name: "Const (KODEX)", desc: "건설", value: "11,200", changes: { today: {pct: -0.5, price: "11,256"}, d3: {pct: -1.5, price: "11,372"}, w1: {pct: -2.5, price: "11,487"}, m1: {pct: -5.6, price: "11,864"}, m3: {pct: -8.5, price: "12,240"}, m6: {pct: -12.4, price: "12,784"}, y1: {pct: -18.5, price: "13,742"}, y3: {pct: -18.5, price: "13,742"} } },
        { ticker: "266360", name: "Media (KODEX)", desc: "미디어", value: "15,800", changes: { today: {pct: 0.7, price: "15,690"}, d3: {pct: 2.5, price: "15,415"}, w1: {pct: -0.5, price: "15,879"}, m1: {pct: 3.2, price: "15,310"}, m3: {pct: 5.6, price: "14,962"}, m6: {pct: -2.1, price: "16,139"}, y1: {pct: -5.4, price: "16,703"}, y3: {pct: -5.4, price: "16,703"} } },
        { ticker: "266410", name: "Staples (KODEX)", desc: "필수소비재", value: "12,100", changes: { today: {pct: 0.1, price: "12,088"}, d3: {pct: 0.5, price: "12,040"}, w1: {pct: -0.2, price: "12,124"}, m1: {pct: 1.5, price: "11,921"}, m3: {pct: 2.8, price: "11,771"}, m6: {pct: 4.5, price: "11,579"}, y1: {pct: 6.8, price: "11,330"}, y3: {pct: 6.8, price: "11,330"} } }
    ],

    // 7. 섹터별 주요 대표 기업 (큰 그룹 섹터 안 5개씩)
    companiesBySector: {
        "Technology (기술/반도체)": [
            { name: "Apple", ticker: "AAPL", value: "$173.50", changes: { today: {pct: 0.9, price: "$171.95"}, d3: {pct: -1.2, price: "$175.62"}, w1: {pct: 2.4, price: "$169.44"}, m1: {pct: 5.6, price: "$164.30"}, m3: {pct: 12.4, price: "$154.36"}, m6: {pct: 8.5, price: "$159.91"}, y1: {pct: 22.1, price: "$142.10"}, y3: {pct: 22.1, price: "$142.10"} }, logo: "https://upload.wikimedia.org/wikipedia/commons/f/fa/Apple_logo_black.svg" },
            { name: "NVIDIA", ticker: "NVDA", value: "$852.12", changes: { today: {pct: 2.8, price: "$828.92"}, d3: {pct: 8.5, price: "$785.40"}, w1: {pct: 15.2, price: "$740.02"}, m1: {pct: 32.5, price: "$643.11"}, m3: {pct: 85.6, price: "$459.44"}, m6: {pct: 124.5, price: "$379.65"}, y1: {pct: 285.6, price: "$221.22"}, y3: {pct: 285.6, price: "$221.22"} }, logo: "https://upload.wikimedia.org/wikipedia/commons/2/21/Nvidia_logo.svg" },
            { name: "Microsoft", ticker: "MSFT", value: "$415.20", changes: { today: {pct: 0.6, price: "$412.72"}, d3: {pct: 0.5, price: "$413.13"}, w1: {pct: 3.2, price: "$402.32"}, m1: {pct: 6.5, price: "$389.86"}, m3: {pct: 14.2, price: "$363.57"}, m6: {pct: 21.5, price: "$341.73"}, y1: {pct: 55.4, price: "$267.18"}, y3: {pct: 55.4, price: "$267.18"} }, logo: "https://upload.wikimedia.org/wikipedia/commons/4/44/Microsoft_logo.svg" },
            { name: "삼성전자", ticker: "005930", value: "₩78,500", changes: { today: {pct: 0.8, price: "₩77,875"}, d3: {pct: -0.8, price: "₩79,135"}, w1: {pct: 2.5, price: "₩76,585"}, m1: {pct: 5.6, price: "₩74,337"}, m3: {pct: 11.2, price: "₩70,594"}, m6: {pct: -2.5, price: "₩80,513"}, y1: {pct: 18.5, price: "₩66,245"}, y3: {pct: 18.5, price: "₩66,245"} }, logo: "https://upload.wikimedia.org/wikipedia/commons/2/24/Samsung_Logo.svg" },
            { name: "SK하이닉스", ticker: "000660", value: "₩175,000", changes: { today: {pct: 1.6, price: "₩172,247"}, d3: {pct: 4.5, price: "₩167,464"}, w1: {pct: 8.5, price: "₩161,290"}, m1: {pct: 18.2, price: "₩148,055"}, m3: {pct: 42.5, price: "₩122,807"}, m6: {pct: 65.2, price: "₩105,963"}, y1: {pct: 115.8, price: "₩81,093"}, y3: {pct: 115.8, price: "₩81,093"} }, logo: null }
        ],
        "Automotive (자동차)": [
            { name: "Tesla", ticker: "TSLA", value: "$373.00", changes: { today: {pct: -1.5, price: "$378.71"}, d3: {pct: -5.6, price: "$395.13"}, w1: {pct: -8.5, price: "$407.65"}, m1: {pct: -15.2, price: "$440.09"}, m3: {pct: -25.6, price: "$501.35"}, m6: {pct: -35.2, price: "$575.62"}, y1: {pct: -12.5, price: "$426.29"}, y3: {pct: -12.5, price: "$426.29"} }, logo: "https://upload.wikimedia.org/wikipedia/commons/b/bd/Tesla_Motors.svg" },
            { name: "현대차", ticker: "005380", value: "₩245,500", changes: { today: {pct: -0.7, price: "₩247,227"}, d3: {pct: 2.5, price: "₩239,512"}, w1: {pct: -0.5, price: "₩246,728"}, m1: {pct: 8.5, price: "₩226,267"}, m3: {pct: 28.5, price: "₩191,051"}, m6: {pct: 35.6, price: "₩181,048"}, y1: {pct: 58.2, price: "₩155,182"}, y3: {pct: 58.2, price: "₩155,182"} }, logo: null },
            { name: "기아", ticker: "000270", value: "₩118,500", changes: { today: {pct: -0.4, price: "₩118,975"}, d3: {pct: 3.2, price: "₩114,807"}, w1: {pct: 1.5, price: "₩116,749"}, m1: {pct: 12.5, price: "₩105,333"}, m3: {pct: 32.5, price: "₩89,434"}, m6: {pct: 42.1, price: "₩83,392"}, y1: {pct: 65.8, price: "₩71,471"}, y3: {pct: 65.8, price: "₩71,471"} }, logo: null },
            { name: "Toyota", ticker: "TM", value: "$235.40", changes: { today: {pct: 0.9, price: "$233.30"}, d3: {pct: 2.8, price: "$229.00"}, w1: {pct: 5.6, price: "$222.92"}, m1: {pct: 12.4, price: "$209.43"}, m3: {pct: 25.6, price: "$187.42"}, m6: {pct: 45.2, price: "$162.12"}, y1: {pct: 68.5, price: "$139.70"}, y3: {pct: 68.5, price: "$139.70"} }, logo: null },
            { name: "Ford", ticker: "F", value: "$12.80", changes: { today: {pct: 0.2, price: "$12.77"}, d3: {pct: 1.2, price: "$12.65"}, w1: {pct: -1.5, price: "$12.99"}, m1: {pct: 2.5, price: "$12.49"}, m3: {pct: 8.5, price: "$11.80"}, m6: {pct: 11.2, price: "$11.51"}, y1: {pct: 5.6, price: "$12.12"}, y3: {pct: 5.6, price: "$12.12"} }, logo: null }
        ],
        "Financials (금융)": [
            { name: "JPMorgan", ticker: "JPM", value: "$195.50", changes: { today: {pct: 0.7, price: "$194.14"}, d3: {pct: 2.5, price: "$190.73"}, w1: {pct: 3.8, price: "$188.34"}, m1: {pct: 8.5, price: "$180.28"}, m3: {pct: 18.5, price: "$164.98"}, m6: {pct: 25.6, price: "$155.65"}, y1: {pct: 38.5, price: "$141.16"}, y3: {pct: 38.5, price: "$141.16"} }, logo: null },
            { name: "Berkshire H.", ticker: "BRK.B", value: "$415.80", changes: { today: {pct: 0.4, price: "$414.14"}, d3: {pct: 1.5, price: "$409.66"}, w1: {pct: 2.1, price: "$407.25"}, m1: {pct: 5.6, price: "$393.75"}, m3: {pct: 12.5, price: "$369.60"}, m6: {pct: 18.5, price: "$350.97"}, y1: {pct: 28.5, price: "$323.58"}, y3: {pct: 28.5, price: "$323.58"} }, logo: null },
            { name: "KB금융", ticker: "105560", value: "₩68,200", changes: { today: {pct: 1.6, price: "₩67,122"}, d3: {pct: 4.5, price: "₩65,311"}, w1: {pct: 6.8, price: "₩63,857"}, m1: {pct: 15.2, price: "₩59,201"}, m3: {pct: 35.6, price: "₩50,295"}, m6: {pct: 28.5, price: "₩53,073"}, y1: {pct: 45.2, price: "₩46,970"}, y3: {pct: 45.2, price: "₩46,970"} }, logo: null },
            { name: "신한지주", ticker: "055550", value: "₩48,500", changes: { today: {pct: 1.1, price: "₩47,973"}, d3: {pct: 3.2, price: "₩47,005"}, w1: {pct: 5.1, price: "₩46,147"}, m1: {pct: 12.8, price: "₩42,996"}, m3: {pct: 28.5, price: "₩37,743"}, m6: {pct: 22.1, price: "₩39,722"}, y1: {pct: 38.5, price: "₩35,018"}, y3: {pct: 38.5, price: "₩35,018"} }, logo: null },
            { name: "Visa", ticker: "V", value: "$278.40", changes: { today: {pct: 0.3, price: "$277.56"}, d3: {pct: 1.2, price: "$275.10"}, w1: {pct: 2.5, price: "$271.61"}, m1: {pct: 4.8, price: "$265.65"}, m3: {pct: 11.2, price: "$250.36"}, m6: {pct: 15.6, price: "$240.83"}, y1: {pct: 25.8, price: "$221.30"}, y3: {pct: 25.8, price: "$221.30"} }, logo: null }
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

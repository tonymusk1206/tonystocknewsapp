from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import threading
import time
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import re
from collections import Counter
import json
from deep_translator import GoogleTranslator
try:
    from pytrends.request import TrendReq
    PYTRENDS_AVAILABLE = True
except ImportError:
    PYTRENDS_AVAILABLE = False

app = Flask(__name__, static_url_path='', static_folder='.')
CORS(app)

# ── 서버 초기화 중 즉각 응답용 기본 Fallback 데이터 ──
base_dt = datetime.now().strftime("%Y.%m.%d")
FALLBACK_DATA = {
    "baseDate": "서버 초기화 중 (최초 1회 수집 진행 중...)",
    "dates": {
        "current": "현재가", "d1": "1일전", "d3": "3일전", "w1": "1주전",
        "m1": "1달전", "m3": "3달전", "m6": "6달전", "y1": "1년전"
    },
    "markets": [
        { "name": "S&P 500", "region": "미국", "ticker": "SPX", "yahoo_ticker": "^GSPC", "value": "5,123.41", "changes": { "today": {"pct": 0.8, "price": "5,082.50"}, "d1": {"pct": 1.2, "price": "5,061.78"}, "d3": {"pct": -0.5, "price": "5,148.91"}, "w1": {"pct": 2.1, "price": "5,018.23"}, "m1": {"pct": 5.4, "price": "4,861.42"}, "m3": {"pct": 12.3, "price": "4,562.18"}, "m6": {"pct": 15.6, "price": "4,431.25"}, "y1": {"pct": 24.5, "price": "4,115.52"} } },
        { "name": "NASDAQ", "region": "미국", "ticker": "COMP", "yahoo_ticker": "^IXIC", "value": "16,211.85", "changes": { "today": {"pct": 1.1, "price": "16,035.20"}, "d1": {"pct": 1.8, "price": "15,924.18"}, "d3": {"pct": -0.8, "price": "16,342.22"}, "w1": {"pct": 3.2, "price": "15,709.30"}, "m1": {"pct": 7.1, "price": "15,137.58"}, "m3": {"pct": 15.2, "price": "14,071.92"}, "m6": {"pct": 18.9, "price": "13,634.02"}, "y1": {"pct": 32.1, "price": "12,271.40"} } },
        { "name": "Dow Jones", "region": "미국", "ticker": "DJI", "yahoo_ticker": "^DJI", "value": "38,981.42", "changes": { "today": {"pct": 0.3, "price": "38,864.52"}, "d1": {"pct": 0.5, "price": "38,787.18"}, "d3": {"pct": -0.2, "price": "39,059.32"}, "w1": {"pct": 1.1, "price": "38,557.28"}, "m1": {"pct": 3.5, "price": "37,664.18"}, "m3": {"pct": 8.7, "price": "35,860.48"}, "m6": {"pct": 11.2, "price": "35,054.34"}, "y1": {"pct": 17.8, "price": "33,091.22"} } },
        { "name": "KOSPI", "region": "한국", "ticker": "KS11", "yahoo_ticker": "^KS11", "value": "2,746.51", "changes": { "today": {"pct": -0.2, "price": "2,752.00"}, "d1": {"pct": -0.4, "price": "2,757.52"}, "d3": {"pct": -1.2, "price": "2,779.88"}, "w1": {"pct": 0.5, "price": "2,732.84"}, "m1": {"pct": -2.1, "price": "2,804.40"}, "m3": {"pct": 3.4, "price": "2,656.41"}, "m6": {"pct": 5.8, "price": "2,596.89"}, "y1": {"pct": 12.3, "price": "2,445.68"} } },
        { "name": "KOSDAQ", "region": "한국", "ticker": "KQ11", "yahoo_ticker": "^KQ11", "value": "880.20", "changes": { "today": {"pct": 0.1, "price": "879.32"}, "d1": {"pct": 0.2, "price": "878.44"}, "d3": {"pct": -1.5, "price": "893.62"}, "w1": {"pct": 1.2, "price": "869.76"}, "m1": {"pct": -1.5, "price": "893.62"}, "m3": {"pct": 5.6, "price": "833.52"}, "m6": {"pct": 7.2, "price": "820.99"}, "y1": {"pct": 15.4, "price": "762.74"} } },
        { "name": "Nikkei 225", "region": "일본", "ticker": "N225", "yahoo_ticker": "^N225", "value": "39,520.10", "changes": { "today": {"pct": 0.5, "price": "39,322.60"}, "d1": {"pct": 0.9, "price": "39,162.38"}, "d3": {"pct": 1.1, "price": "39,083.58"}, "w1": {"pct": 2.5, "price": "38,556.68"}, "m1": {"pct": 4.8, "price": "37,709.92"}, "m3": {"pct": 10.2, "price": "35,862.88"}, "m6": {"pct": 22.1, "price": "32,366.18"}, "y1": {"pct": 35.6, "price": "29,144.02"} } },
        { "name": "Shanghai Comp", "region": "중국", "ticker": "SSEC", "yahoo_ticker": "000001.SS", "value": "3,065.25", "changes": { "today": {"pct": -0.4, "price": "3,077.48"}, "d1": {"pct": -0.8, "price": "3,089.88"}, "d3": {"pct": 0.4, "price": "3,052.98"}, "w1": {"pct": -1.2, "price": "3,102.48"}, "m1": {"pct": 2.5, "price": "2,990.48"}, "m3": {"pct": 6.8, "price": "2,870.08"}, "m6": {"pct": 1.5, "price": "3,019.96"}, "y1": {"pct": -5.4, "price": "3,240.90"} } }
    ],
    "usSectors": [
        { "ticker": "XLK", "yahoo_ticker": "XLK", "name": "Technology", "desc": "기술", "value": "215.30", "changes": { "today": {"pct": 1.4, "price": "212.33"}, "d1": {"pct": 2.1, "price": "210.87"}, "d3": {"pct": 0.5, "price": "214.22"}, "w1": {"pct": 4.2, "price": "206.62"}, "m1": {"pct": 8.5, "price": "198.43"}, "m3": {"pct": 16.2, "price": "185.28"}, "m6": {"pct": 21.5, "price": "177.11"}, "y1": {"pct": 42.1, "price": "151.51"} } },
        { "ticker": "XLI", "yahoo_ticker": "XLI", "name": "Industrials", "desc": "산업재", "value": "118.42", "changes": { "today": {"pct": 0.3, "price": "118.07"}, "d1": {"pct": 0.5, "price": "117.83"}, "d3": {"pct": 1.2, "price": "117.02"}, "w1": {"pct": 2.4, "price": "115.64"}, "m1": {"pct": 4.5, "price": "113.34"}, "m3": {"pct": 11.2, "price": "106.49"}, "m6": {"pct": 15.8, "price": "102.26"}, "y1": {"pct": 22.5, "price": "96.67"} } },
        { "ticker": "XLY", "yahoo_ticker": "XLY", "name": "Cons. Discr.", "desc": "임의소비재", "value": "185.12", "changes": { "today": {"pct": 0.7, "price": "183.83"}, "d1": {"pct": 1.1, "price": "183.11"}, "d3": {"pct": -1.2, "price": "187.38"}, "w1": {"pct": 1.8, "price": "181.85"}, "m1": {"pct": 4.2, "price": "177.66"}, "m3": {"pct": 9.5, "price": "169.06"}, "m6": {"pct": 12.8, "price": "164.11"}, "y1": {"pct": 25.6, "price": "147.39"} } },
        { "ticker": "XLP", "yahoo_ticker": "XLP", "name": "Cons. Staples", "desc": "필수소비재", "value": "78.40", "changes": { "today": {"pct": -0.1, "price": "78.48"}, "d1": {"pct": -0.2, "price": "78.56"}, "d3": {"pct": 0.5, "price": "77.99"}, "w1": {"pct": -1.1, "price": "79.28"}, "m1": {"pct": 1.5, "price": "77.24"}, "m3": {"pct": 3.2, "price": "75.97"}, "m6": {"pct": 5.8, "price": "74.10"}, "y1": {"pct": 8.4, "price": "72.33"} } },
        { "ticker": "XLE", "yahoo_ticker": "XLE", "name": "Energy", "desc": "에너지", "value": "95.60", "changes": { "today": {"pct": -0.8, "price": "96.37"}, "d1": {"pct": -1.2, "price": "96.76"}, "d3": {"pct": -2.5, "price": "98.05"}, "w1": {"pct": 1.1, "price": "94.56"}, "m1": {"pct": -3.2, "price": "98.76"}, "m3": {"pct": -5.6, "price": "101.27"}, "m6": {"pct": 2.1, "price": "93.63"}, "y1": {"pct": 8.5, "price": "88.11"} } },
        { "ticker": "XLV", "yahoo_ticker": "XLV", "name": "Health Care", "desc": "헬스케어", "value": "145.80", "changes": { "today": {"pct": 0.2, "price": "145.51"}, "d1": {"pct": 0.4, "price": "145.22"}, "d3": {"pct": 1.2, "price": "144.07"}, "w1": {"pct": -0.5, "price": "146.53"}, "m1": {"pct": 2.1, "price": "142.80"}, "m3": {"pct": 4.5, "price": "139.52"}, "m6": {"pct": 5.2, "price": "138.59"}, "y1": {"pct": 11.2, "price": "131.12"} } },
        { "ticker": "XLF", "yahoo_ticker": "XLF", "name": "Financials", "desc": "금융", "value": "42.10", "changes": { "today": {"pct": 0.9, "price": "41.72"}, "d1": {"pct": 1.5, "price": "41.49"}, "d3": {"pct": 0.8, "price": "41.76"}, "w1": {"pct": 2.5, "price": "41.07"}, "m1": {"pct": 5.6, "price": "39.87"}, "m3": {"pct": 12.1, "price": "37.56"}, "m6": {"pct": 16.5, "price": "36.14"}, "y1": {"pct": 22.4, "price": "34.39"} } },
        { "ticker": "XLC", "yahoo_ticker": "XLC", "name": "Comm. Svcs", "desc": "통신", "value": "85.20", "changes": { "today": {"pct": 1.2, "price": "84.19"}, "d1": {"pct": 1.8, "price": "83.69"}, "d3": {"pct": -0.5, "price": "85.63"}, "w1": {"pct": 3.4, "price": "82.40"}, "m1": {"pct": 9.5, "price": "77.81"}, "m3": {"pct": 18.2, "price": "72.08"}, "m6": {"pct": 25.1, "price": "68.11"}, "y1": {"pct": 35.8, "price": "62.74"} } },
        { "ticker": "XLU", "yahoo_ticker": "XLU", "name": "Utilities", "desc": "유틸리티", "value": "65.30", "changes": { "today": {"pct": -0.5, "price": "65.63"}, "d1": {"pct": -0.8, "price": "65.82"}, "d3": {"pct": 0.2, "price": "65.17"}, "w1": {"pct": -1.5, "price": "66.29"}, "m1": {"pct": 1.2, "price": "64.52"}, "m3": {"pct": -2.5, "price": "66.97"}, "m6": {"pct": 1.8, "price": "64.14"}, "y1": {"pct": 5.6, "price": "61.84"} } },
        { "ticker": "XLB", "yahoo_ticker": "XLB", "name": "Materials", "desc": "소재", "value": "88.90", "changes": { "today": {"pct": 0.4, "price": "88.55"}, "d1": {"pct": 0.7, "price": "88.28"}, "d3": {"pct": 1.5, "price": "87.59"}, "w1": {"pct": 2.1, "price": "87.07"}, "m1": {"pct": 3.8, "price": "85.65"}, "m3": {"pct": 8.5, "price": "81.94"}, "m6": {"pct": 11.2, "price": "79.95"}, "y1": {"pct": 18.5, "price": "75.02"} } },
        { "ticker": "XLRE", "yahoo_ticker": "XLRE", "name": "Real Estate", "desc": "부동산", "value": "41.50", "changes": { "today": {"pct": -0.9, "price": "41.87"}, "d1": {"pct": -1.5, "price": "42.13"}, "d3": {"pct": -2.5, "price": "42.56"}, "w1": {"pct": -3.2, "price": "42.87"}, "m1": {"pct": 1.5, "price": "40.89"}, "m3": {"pct": 5.6, "price": "39.30"}, "m6": {"pct": 8.2, "price": "38.35"}, "y1": {"pct": 12.5, "price": "36.89"} } }
    ],
    "krSectors": [
        { "ticker": "KODEX 정보기술", "yahoo_ticker": "229200.KS", "name": "Technology", "desc": "정보기술", "value": "₩42,100", "changes": { "today": {"pct": 0.8, "price": "₩41,763"}, "d1": {"pct": 1.2, "price": "₩41,602"}, "d3": {"pct": -1.2, "price": "₩42,614"}, "w1": {"pct": 2.8, "price": "₩40,953"}, "m1": {"pct": 5.5, "price": "₩39,905"}, "m3": {"pct": 12.1, "price": "₩37,555"}, "m6": {"pct": 15.8, "price": "₩36,358"}, "y1": {"pct": 28.5, "price": "₩32,763"} } },
        { "ticker": "KODEX 반도체", "yahoo_ticker": "091160.KS", "name": "Semiconductors", "desc": "반도체", "value": "₩38,500", "changes": { "today": {"pct": 1.0, "price": "₩38,118"}, "d1": {"pct": 1.5, "price": "₩37,931"}, "d3": {"pct": -2.1, "price": "₩39,326"}, "w1": {"pct": 3.5, "price": "₩37,198"}, "m1": {"pct": 6.2, "price": "₩36,253"}, "m3": {"pct": 14.5, "price": "₩33,624"}, "m6": {"pct": 18.2, "price": "₩32,572"}, "y1": {"pct": 35.6, "price": "₩28,392"} } },
        { "ticker": "KODEX 자동차", "yahoo_ticker": "091180.KS", "name": "Automobiles", "desc": "자동차", "value": "₩24,500", "changes": { "today": {"pct": 0.5, "price": "₩24,378"}, "d1": {"pct": 0.8, "price": "₩24,304"}, "d3": {"pct": 1.5, "price": "₩24,137"}, "w1": {"pct": -1.2, "price": "₩24,797"}, "m1": {"pct": 4.5, "price": "₩23,445"}, "m3": {"pct": 11.2, "price": "₩22,032"}, "m6": {"pct": 15.6, "price": "₩21,194"}, "y1": {"pct": 28.5, "price": "₩19,066"} } },
        { "ticker": "KODEX 은행", "yahoo_ticker": "091170.KS", "name": "Banks", "desc": "은행", "value": "₩8,950", "changes": { "today": {"pct": 1.4, "price": "₩8,826"}, "d1": {"pct": 2.1, "price": "₩8,765"}, "d3": {"pct": 3.5, "price": "₩8,647"}, "w1": {"pct": 5.6, "price": "₩8,476"}, "m1": {"pct": 12.5, "price": "₩7,956"}, "m3": {"pct": 21.4, "price": "₩7,372"}, "m6": {"pct": 18.5, "price": "₩7,551"}, "y1": {"pct": 38.6, "price": "₩6,455"} } },
        { "ticker": "KODEX 헬스케어", "yahoo_ticker": "269620.KS", "name": "Health Care", "desc": "헬스케어", "value": "₩28,200", "changes": { "today": {"pct": -0.3, "price": "₩28,285"}, "d1": {"pct": -0.5, "price": "₩28,341"}, "d3": {"pct": 0.2, "price": "₩28,144"}, "w1": {"pct": 1.5, "price": "₩27,783"}, "m1": {"pct": 5.2, "price": "₩26,806"}, "m3": {"pct": 8.5, "price": "₩25,990"}, "m6": {"pct": 9.2, "price": "₩25,825"}, "y1": {"pct": -2.5, "price": "₩28,923"} } },
        { "ticker": "KODEX 철강", "yahoo_ticker": "117680.KS", "name": "Steel", "desc": "철강", "value": "₩18,400", "changes": { "today": {"pct": 0.2, "price": "₩18,363"}, "d1": {"pct": 0.5, "price": "₩18,308"}, "d3": {"pct": 1.2, "price": "₩18,182"}, "w1": {"pct": 2.1, "price": "₩18,021"}, "m1": {"pct": -1.5, "price": "₩18,680"}, "m3": {"pct": 3.5, "price": "₩17,778"}, "m6": {"pct": 5.8, "price": "₩17,391"}, "y1": {"pct": 12.5, "price": "₩16,356"} } },
        { "ticker": "KODEX 에너지화학", "yahoo_ticker": "117460.KS", "name": "Chemicals", "desc": "에너지/화학", "value": "₩21,500", "changes": { "today": {"pct": -0.7, "price": "₩21,651"}, "d1": {"pct": -1.2, "price": "₩21,761"}, "d3": {"pct": -2.5, "price": "₩22,051"}, "w1": {"pct": -1.2, "price": "₩21,761"}, "m1": {"pct": 2.5, "price": "₩20,976"}, "m3": {"pct": 8.2, "price": "₩19,872"}, "m6": {"pct": -5.4, "price": "₩22,726"}, "y1": {"pct": -8.5, "price": "₩23,497"} } },
        { "ticker": "KODEX 건설", "yahoo_ticker": "117700.KS", "name": "Construction", "desc": "건설", "value": "₩11,200", "changes": { "today": {"pct": -0.5, "price": "₩11,256"}, "d1": {"pct": -0.8, "price": "₩11,290"}, "d3": {"pct": -1.5, "price": "₩11,372"}, "w1": {"pct": -2.5, "price": "₩11,487"}, "m1": {"pct": -5.6, "price": "₩11,864"}, "m3": {"pct": -8.5, "price": "₩12,240"}, "m6": {"pct": -12.4, "price": "₩12,784"}, "y1": {"pct": -18.5, "price": "₩13,742"} } },
        { "ticker": "KODEX 미디어", "yahoo_ticker": "266360.KS", "name": "Media", "desc": "미디어", "value": "₩15,800", "changes": { "today": {"pct": 0.7, "price": "₩15,690"}, "d1": {"pct": 1.1, "price": "₩15,628"}, "d3": {"pct": 2.5, "price": "₩15,415"}, "w1": {"pct": -0.5, "price": "₩15,879"}, "m1": {"pct": 3.2, "price": "₩15,310"}, "m3": {"pct": 5.6, "price": "₩14,962"}, "m6": {"pct": -2.1, "price": "₩16,139"}, "y1": {"pct": -5.4, "price": "₩16,703"} } },
        { "ticker": "KODEX 필수소비재", "yahoo_ticker": "266410.KS", "name": "Cons. Staples", "desc": "필수소비재", "value": "₩12,100", "changes": { "today": {"pct": 0.1, "price": "₩12,088"}, "d1": {"pct": 0.2, "price": "₩12,076"}, "d3": {"pct": 0.5, "price": "₩12,040"}, "w1": {"pct": -0.2, "price": "₩12,124"}, "m1": {"pct": 1.5, "price": "₩11,921"}, "m3": {"pct": 2.8, "price": "₩11,771"}, "m6": {"pct": 4.5, "price": "₩11,579"}, "y1": {"pct": 6.8, "price": "₩11,330"} } }
    ],
    "companiesBySector": {
        "Technology (기술/반도체)": [
            { "name": "Apple", "ticker": "AAPL", "yahoo_ticker": "AAPL", "logo": "", "value": "$173.50", "changes": { "today": {"pct": 0.9, "price": "$171.95"}, "d1": {"pct": 1.5, "price": "$170.95"}, "d3": {"pct": -1.2, "price": "$175.62"}, "w1": {"pct": 2.4, "price": "$169.44"}, "m1": {"pct": 5.6, "price": "$164.30"}, "m3": {"pct": 12.4, "price": "$154.36"}, "m6": {"pct": 8.5, "price": "$159.91"}, "y1": {"pct": 22.1, "price": "$142.10"} } },
            { "name": "NVIDIA", "ticker": "NVDA", "yahoo_ticker": "NVDA", "logo": "", "value": "$852.12", "changes": { "today": {"pct": 2.8, "price": "$828.92"}, "d1": {"pct": 4.2, "price": "$818.00"}, "d3": {"pct": 8.5, "price": "$785.40"}, "w1": {"pct": 15.2, "price": "$740.02"}, "m1": {"pct": 32.5, "price": "$643.11"}, "m3": {"pct": 85.6, "price": "$459.44"}, "m6": {"pct": 124.5, "price": "$379.65"}, "y1": {"pct": 285.6, "price": "$221.22"} } },
            { "name": "Microsoft", "ticker": "MSFT", "yahoo_ticker": "MSFT", "logo": "", "value": "$415.20", "changes": { "today": {"pct": 0.6, "price": "$412.72"}, "d1": {"pct": 1.1, "price": "$410.69"}, "d3": {"pct": 0.5, "price": "$413.13"}, "w1": {"pct": 3.2, "price": "$402.32"}, "m1": {"pct": 6.5, "price": "$389.86"}, "m3": {"pct": 14.2, "price": "$363.57"}, "m6": {"pct": 21.5, "price": "$341.73"}, "y1": {"pct": 55.4, "price": "$267.18"} } },
            { "name": "삼성전자", "ticker": "005930", "yahoo_ticker": "005930.KS", "logo": "", "value": "₩78,500", "changes": { "today": {"pct": 0.8, "price": "₩77,875"}, "d1": {"pct": 1.5, "price": "₩77,340"}, "d3": {"pct": -0.8, "price": "₩79,135"}, "w1": {"pct": 2.5, "price": "₩76,585"}, "m1": {"pct": 5.6, "price": "₩74,337"}, "m3": {"pct": 11.2, "price": "₩70,594"}, "m6": {"pct": -2.5, "price": "₩80,513"}, "y1": {"pct": 18.5, "price": "₩66,245"} } },
            { "name": "SK하이닉스", "ticker": "000660", "yahoo_ticker": "000660.KS", "logo": "", "value": "₩175,000", "changes": { "today": {"pct": 1.6, "price": "₩172,247"}, "d1": {"pct": 2.8, "price": "₩170,234"}, "d3": {"pct": 4.5, "price": "₩167,464"}, "w1": {"pct": 8.5, "price": "₩161,290"}, "m1": {"pct": 18.2, "price": "₩148,055"}, "m3": {"pct": 42.5, "price": "₩122,807"}, "m6": {"pct": 65.2, "price": "₩105,963"}, "y1": {"pct": 115.8, "price": "₩81,093"} } }
        ],
        "Automotive (자동차)": [
            { "name": "Tesla", "ticker": "TSLA", "yahoo_ticker": "TSLA", "logo": "", "value": "$373.00", "changes": { "today": {"pct": -1.5, "price": "$378.71"}, "d1": {"pct": -2.5, "price": "$382.56"}, "d3": {"pct": -5.6, "price": "$395.13"}, "w1": {"pct": -8.5, "price": "$407.65"}, "m1": {"pct": -15.2, "price": "$440.09"}, "m3": {"pct": -25.6, "price": "$501.35"}, "m6": {"pct": -35.2, "price": "$575.62"}, "y1": {"pct": -12.5, "price": "$426.29"} } },
            { "name": "현대차", "ticker": "005380", "yahoo_ticker": "005380.KS", "logo": "", "value": "₩245,500", "changes": { "today": {"pct": -0.7, "price": "₩247,227"}, "d1": {"pct": -1.2, "price": "₩248,479"}, "d3": {"pct": 2.5, "price": "₩239,512"}, "w1": {"pct": -0.5, "price": "₩246,728"}, "m1": {"pct": 8.5, "price": "₩226,267"}, "m3": {"pct": 28.5, "price": "₩191,051"}, "m6": {"pct": 35.6, "price": "₩181,048"}, "y1": {"pct": 58.2, "price": "₩155,182"} } },
            { "name": "기아", "ticker": "000270", "yahoo_ticker": "000270.KS", "logo": "", "value": "₩118,500", "changes": { "today": {"pct": -0.4, "price": "₩118,975"}, "d1": {"pct": -0.8, "price": "₩119,456"}, "d3": {"pct": 3.2, "price": "₩114,807"}, "w1": {"pct": 1.5, "price": "₩116,749"}, "m1": {"pct": 12.5, "price": "₩105,333"}, "m3": {"pct": 32.5, "price": "₩89,434"}, "m6": {"pct": 42.1, "price": "₩83,392"}, "y1": {"pct": 65.8, "price": "₩71,471"} } },
            { "name": "Toyota", "ticker": "TM", "yahoo_ticker": "TM", "logo": "", "value": "$235.40", "changes": { "today": {"pct": 0.9, "price": "$233.30"}, "d1": {"pct": 1.5, "price": "$231.89"}, "d3": {"pct": 2.8, "price": "$229.00"}, "w1": {"pct": 5.6, "price": "$222.92"}, "m1": {"pct": 12.4, "price": "$209.43"}, "m3": {"pct": 25.6, "price": "$187.42"}, "m6": {"pct": 45.2, "price": "$162.12"}, "y1": {"pct": 68.5, "price": "$139.70"} } },
            { "name": "Ford", "ticker": "F", "yahoo_ticker": "F", "logo": "", "value": "$12.80", "changes": { "today": {"pct": 0.2, "price": "$12.77"}, "d1": {"pct": 0.5, "price": "$12.74"}, "d3": {"pct": 1.2, "price": "$12.65"}, "w1": {"pct": -1.5, "price": "$12.99"}, "m1": {"pct": 2.5, "price": "$12.49"}, "m3": {"pct": 8.5, "price": "$11.80"}, "m6": {"pct": 11.2, "price": "$11.51"}, "y1": {"pct": 5.6, "price": "$12.12"} } }
        ],
        "Financials (금융)": [
            { "name": "JPMorgan", "ticker": "JPM", "yahoo_ticker": "JPM", "logo": "", "value": "$195.50", "changes": { "today": {"pct": 0.7, "price": "$194.14"}, "d1": {"pct": 1.2, "price": "$193.20"}, "d3": {"pct": 2.5, "price": "$190.73"}, "w1": {"pct": 3.8, "price": "$188.34"}, "m1": {"pct": 8.5, "price": "$180.28"}, "m3": {"pct": 18.5, "price": "$164.98"}, "m6": {"pct": 25.6, "price": "$155.65"}, "y1": {"pct": 38.5, "price": "$141.16"} } },
            { "name": "Berkshire H.", "ticker": "BRK-B", "yahoo_ticker": "BRK-B", "logo": "", "value": "$415.80", "changes": { "today": {"pct": 0.4, "price": "$414.14"}, "d1": {"pct": 0.8, "price": "$412.49"}, "d3": {"pct": 1.5, "price": "$409.66"}, "w1": {"pct": 2.1, "price": "$407.25"}, "m1": {"pct": 5.6, "price": "$393.75"}, "m3": {"pct": 12.5, "price": "$369.60"}, "m6": {"pct": 18.5, "price": "$350.97"}, "y1": {"pct": 28.5, "price": "$323.58"} } },
            { "name": "KB금융", "ticker": "105560", "yahoo_ticker": "105560.KS", "logo": "", "value": "₩68,200", "changes": { "today": {"pct": 1.6, "price": "₩67,122"}, "d1": {"pct": 2.5, "price": "₩66,537"}, "d3": {"pct": 4.5, "price": "₩65,311"}, "w1": {"pct": 6.8, "price": "₩63,857"}, "m1": {"pct": 15.2, "price": "₩59,201"}, "m3": {"pct": 35.6, "price": "₩50,295"}, "m6": {"pct": 28.5, "price": "₩53,073"}, "y1": {"pct": 45.2, "price": "₩46,970"} } },
            { "name": "신한지주", "ticker": "055550", "yahoo_ticker": "055550.KS", "logo": "", "value": "₩48,500", "changes": { "today": {"pct": 1.1, "price": "₩47,973"}, "d1": {"pct": 1.8, "price": "₩47,643"}, "d3": {"pct": 3.2, "price": "₩47,005"}, "w1": {"pct": 5.1, "price": "₩46,147"}, "m1": {"pct": 12.8, "price": "₩42,996"}, "m3": {"pct": 28.5, "price": "₩37,743"}, "m6": {"pct": 22.1, "price": "₩39,722"}, "y1": {"pct": 38.5, "price": "₩35,018"} } },
            { "name": "Visa", "ticker": "V", "yahoo_ticker": "V", "logo": "", "value": "$278.40", "changes": { "today": {"pct": 0.3, "price": "$277.56"}, "d1": {"pct": 0.5, "price": "$276.91"}, "d3": {"pct": 1.2, "price": "$275.10"}, "w1": {"pct": 2.5, "price": "$271.61"}, "m1": {"pct": 4.8, "price": "$265.65"}, "m3": {"pct": 11.2, "price": "$250.36"}, "m6": {"pct": 15.6, "price": "$240.83"}, "y1": {"pct": 25.8, "price": "$221.30"} } }
        ],
        "Health Care (헬스케어)": [
            { "name": "Eli Lilly", "ticker": "LLY", "yahoo_ticker": "LLY", "logo": "", "value": "$780.00", "changes": { "today": {"pct": 0.5, "price": "$776.10"}, "d1": {"pct": 0.8, "price": "$773.76"}, "d3": {"pct": 1.2, "price": "$770.72"}, "w1": {"pct": 2.1, "price": "$763.96"}, "m1": {"pct": 5.0, "price": "$742.86"}, "m3": {"pct": 10.2, "price": "$707.80"}, "m6": {"pct": 18.5, "price": "$658.23"}, "y1": {"pct": 55.2, "price": "$502.58"} } },
            { "name": "삼성바이오로직스", "ticker": "207940", "yahoo_ticker": "207940.KS", "logo": "", "value": "₩850,000", "changes": { "today": {"pct": 0.5, "price": "₩845,750"}, "d1": {"pct": 0.8, "price": "₩843,200"}, "d3": {"pct": 1.2, "price": "₩839,800"}, "w1": {"pct": 2.1, "price": "₩832,517"}, "m1": {"pct": 5.0, "price": "₩809,524"}, "m3": {"pct": 10.2, "price": "₩771,325"}, "m6": {"pct": 15.5, "price": "₩735,931"}, "y1": {"pct": 22.3, "price": "₩694,932"} } }
        ],
        "Materials & Chem (소재/화학)": [
            { "name": "LG화학", "ticker": "051910", "yahoo_ticker": "051910.KS", "logo": "", "value": "₩320,000", "changes": { "today": {"pct": -0.5, "price": "₩321,600"}, "d1": {"pct": -0.8, "price": "₩322,560"}, "d3": {"pct": -1.5, "price": "₩324,873"}, "w1": {"pct": -2.1, "price": "₩326,862"}, "m1": {"pct": 2.5, "price": "₩312,195"}, "m3": {"pct": 8.2, "price": "₩295,750"}, "m6": {"pct": -5.4, "price": "₩338,122"}, "y1": {"pct": -8.5, "price": "₩349,727"} } }
        ]
    },
    "news": [],
    "keywordNews": [],
    "quotes": [],
    "youtube": []
}

# 글로벌 데이터 캐시
data_cache = {
    "data": None,
    "last_updated": 0
}
CACHE_DURATION = 600  # 10분

def calculate_changes(hist, current_close):
    try:
        if len(hist) < 2: return {k: {"pct": 0, "raw_price": 0} for k in ["today", "d1", "d3", "w1", "m1", "m3", "m6", "y1"]}
        def get_data(days_ago):
            idx = min(days_ago, len(hist)-1)
            old_price = float(hist['Close'].iloc[-1 - idx])
            if old_price == 0: return {"pct": 0, "raw_price": 0}
            pct = round(((current_close - old_price) / old_price) * 100, 2)
            return {"pct": pct, "raw_price": old_price}
        return {
            "today": get_data(1), "d1": get_data(1), "d3": get_data(3),
            "w1": get_data(5), "m1": get_data(21), "m3": get_data(63),
            "m6": get_data(126), "y1": get_data(252)
        }
    except:
        return {k: {"pct": 0, "raw_price": 0} for k in ["today", "d1", "d3", "w1", "m1", "m3", "m6", "y1"]}

# ── 실시간 뉴스 & 유튜브 RSS 파싱 엔진 ──
def fetch_rss(url, timeout=10):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cache-Control': 'no-cache'
        }
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return ET.fromstring(response.read().strip())
    except Exception as e:
        print(f"RSS fetch error for {url}: {e}")
        return None

def verify_economic_news(title):
    econ_keywords = ['주식', '증시', '금리', '달러', '환율', '투자', '주가', '시장', '기업', '실적',
        '경제', '금융', '반도체', 'AI', '배당', '코스피', '나스닥', '연준', '인플레이션',
        '수출', '매수', '매도', '합병', '테슬라', '엔비디아', '삼성', 'SK', '펀드', '채권', '지수']
    trash_keywords = ['연예', '스포츠', '축구', '야구', '날씨', '폭우', '사건', '사고', '살인', '마약', '이혼', '결혼', '아이돌']
    if any(tk in title for tk in trash_keywords): return False
    return any(ek in title for ek in econ_keywords)

def generate_news_hashtags(title):
    tags = []
    if any(k in title for k in ['금리', '연준', '파월', '인플레이션']):
        tags.extend(['#Fed통화정책', '#금리변동성', '#유동성촉각'])
    elif any(k in title for k in ['반도체', 'AI', '엔비디아', 'TSMC']):
        tags.extend(['#AI슈퍼사이클', '#반도체랠리', '#빅테크주도주'])
    elif any(k in title for k in ['테슬라', '전기차', '머스크', '자율주행']):
        tags.extend(['#모빌리티혁신', '#FSD기대감', '#성장주향방'])
    elif any(k in title for k in ['코스피', '삼성', '밸류업']):
        tags.extend(['#K증시모멘텀', '#저PBR수혜', '#외인자금유입'])
    else:
        tags.extend(['#글로벌경제핫이슈', '#시장투심분석', '#거시경제지표'])
    return " ".join(tags[:3])

def parse_google_news_verified(url, required_count=10):
    root = fetch_rss(url)
    items = []
    if root is None: return items
    for item in root.findall('.//item'):
        title = item.findtext('title', '')
        link = item.findtext('link', '')
        pub_date = item.findtext('pubDate', '')
        source = "Google News"
        if " - " in title:
            parts = title.rsplit(" - ", 1)
            title = parts[0]
            source = parts[1]
        if not verify_economic_news(title): continue
        hashtags = generate_news_hashtags(title)
        date_str = datetime.now().strftime("%Y.%m.%d")
        try:
            pd_parsed = datetime.strptime(pub_date[5:25].strip(), "%d %b %Y %H:%M")
            date_str = pd_parsed.strftime("%Y.%m.%d")
        except: pass
        items.append({
            "title": title, "summary": title, "source": f"출처: {source}",
            "hashtags": hashtags, "date": date_str, "time": "실시간",
            "link": link, "image": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=400&q=80"
        })
        if len(items) >= required_count: break
    return items

def get_top10_news():
    """
    Bloomberg Five Things + WSJ What's News + Investing.com 주요 뉴스
    에디터들이 엄선한 핵심 뉴스 제공
    """
    feeds = [
        # Bloomberg Markets RSS
        "https://feeds.bloomberg.com/markets/news.rss",
        # Bloomberg Top News
        "https://feeds.bloomberg.com/politics/news.rss",
        # WSJ Markets
        "https://feeds.content.dowjones.io/public/rss/mw_topstories",
        # MarketWatch Top Stories
        "https://feeds.marketwatch.com/marketwatch/topstories/",
        # Financial Times
        "https://www.ft.com/rss/home",
        # Investing.com (fallback)
        "https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=en&gl=US&ceid=US:en",
        "https://news.google.com/rss/search?q=stock+market+economy+finance&hl=en&gl=US&ceid=US:en",
    ]
    translator = GoogleTranslator(source='auto', target='ko')
    collected_news = []
    seen_titles = set()

    for feed_url in feeds:
        try:
            req = urllib.request.Request(feed_url, headers={
                'User-Agent': 'Mozilla/5.0 (compatible; NewsBot/1.0)',
                'Accept': 'application/rss+xml, application/xml, text/xml, */*'
            })
            with urllib.request.urlopen(req, timeout=8) as resp:
                raw = resp.read()
            root = ET.fromstring(raw.strip())
            for item in root.findall('.//item'):
                raw_title = item.findtext('title', '').strip()
                link = item.findtext('link', '').strip()
                pub_date = item.findtext('pubDate', '')
                source_tag = item.findtext('source', '')

                # 언론사 제거
                clean_title = re.sub(r'\s-\s[^-]+$', '', raw_title).strip()
                if not clean_title or len(clean_title) < 10:
                    continue

                # 중복 제거
                title_key = clean_title[:40].lower()
                if title_key in seen_titles:
                    continue
                seen_titles.add(title_key)

                # 날짜 파싱
                date_str = datetime.now().strftime("%Y.%m.%d")
                try:
                    dt = datetime.strptime(pub_date[:25], "%a, %d %b %Y %H:%M:%S")
                    date_str = dt.strftime("%Y.%m.%d")
                except:
                    pass

                # 한글 번역
                try:
                    translated = translator.translate(clean_title[:500])
                except:
                    translated = clean_title

                hashtags = generate_news_hashtags(translated)
                collected_news.append({
                    "title": translated,
                    "summary": translated,
                    "source": source_tag or feed_url.split('/')[2],
                    "hashtags": hashtags,
                    "date": date_str,
                    "time": "실시간",
                    "link": link,
                    "image": ""
                })
                if len(collected_news) >= 10:
                    return collected_news[:10]
        except Exception as e:
            print(f"[News] Feed error {feed_url}: {e}")
            continue

    # 부족 시 한국어 구글 뉴스로 보완
    if len(collected_news) < 10:
        try:
            kr_url = "https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=ko&gl=KR&ceid=KR:ko"
            kr_items = parse_google_news_verified(kr_url, required_count=10 - len(collected_news))
            for it in kr_items:
                if it['title'][:30].lower() not in seen_titles:
                    collected_news.append(it)
                    if len(collected_news) >= 10:
                        break
        except:
            pass

    return collected_news[:10]

def extract_trending_keywords():
    """
    구글 트렌드 비즈니스·금융 섬터 실시간 방화벽 키워드 TOP10
    """
    # 1. pytrends로 구글 트렌드 실시간 트렌드 다운로드 시도
    if PYTRENDS_AVAILABLE:
        try:
            pytrends = TrendReq(hl='ko-KR', tz=540, timeout=(10, 25), retries=2, backoff_factor=0.5)
            # 카테고리 7 = Finance (Business & Finance)
            trending = pytrends.trending_searches(pn='south_korea')
            keywords = [kw for kw in trending[0].tolist() if len(kw) > 1][:10]
            if keywords:
                print(f"[Trends] pytrends 성공: {keywords}")
                return keywords
        except Exception as e:
            print(f"[Trends] pytrends 실패: {e}")

    # 2. 구글 뉴스 헤드라인 텍스트 마이닝 fallback
    feeds = [
        "https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=ko&gl=KR&ceid=KR:ko",
        "https://news.google.com/rss/search?q=증시+경제+금융&hl=ko&gl=KR&ceid=KR:ko",
        "https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=en&gl=US&ceid=US:en",
    ]
    stopwords = set(["주식", "증시", "경제", "금융", "투자", "시장", "기업", "실적", "오늘",
                     "주가", "상승", "하락", "코스피", "코스닥", "특징주", "단독",
                     "속보", "says", "new", "the", "and", "for", "its", "has", "are", "this", "that", "with"])
    words = []
    for url in feeds:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=6) as response:
                root = ET.fromstring(response.read().strip())
                for item in root.findall('.//item'):
                    title = item.findtext('title', '')
                    if " - " in title:
                        title = title.rsplit(" - ", 1)[0]
                    tokens = re.findall(r'[가-힣A-Za-z0-9]+', title)
                    for t in tokens:
                        if len(t) > 1 and t.lower() not in stopwords:
                            words.append(t)
        except:
            pass
    if not words:
        return ["엔비디아", "금리인하", "비트코인", "테슬라", "에플", "삼성전자", "반도체", "AI", "배당", "환율"]
    return [w for w, _ in Counter(words).most_common(10)]

def get_keyword_news(keywords):
    keyword_data = []
    for kw in keywords:
        enc_kw = urllib.parse.quote(f"{kw} 주식")
        url = f"https://news.google.com/rss/search?q={enc_kw}&hl=ko&gl=KR&ceid=KR:ko"
        k_news = parse_google_news_verified(url, required_count=3)
        keyword_data.append({"keyword": kw, "news": k_news})
    return keyword_data

def get_youtube_insights():
    channels = [
        {"name": "슈카월드",   "id": "UCsJ6RuBiTVWRX156FVbeaGg"},
        {"name": "삼프로TV",  "id": "UChbqbQB09zM4YwLIfk35Nzw"},
        {"name": "소수몵키",  "id": "UCb5iL51DrmB_qN6Wc3Gj04Q"},
        {"name": "월가아재",  "id": "UC-w3l14sA0t9P-eXm71lE_A"},
        {"name": "수페TV",   "id": "UCYp6Xj6o1k4aA4o7z7yEGEw"},
    ]
    global rss_cache
    videos = []
    old_videos_map = {v['channel']: v for v in rss_cache.get("youtube_insights", [])}
    base_dt_now = datetime.now().strftime("%Y.%m.%d")
    fallback_data = {
        "슈카월드": {"title": "[슈카월드] 최근 글로벌 증시 및 주요 경제 이슈 분석", "link": "https://www.youtube.com/channel/UCsJ6RuBiTVWRX156FVbeaGg"},
        "삼프로TV": {"title": "[삼프로TV] 오늘장 핵심 이슈와 월가 거물들의 포트폴리오 전략", "link": "https://www.youtube.com/channel/UChbEQXDcwPEyP3rC18H_3oQ"},
        "소수몽키": {"title": "[소수몽키] 서학개미 필독! 이번 주 실적 발표 및 주요 테크주 체크리스트", "link": "https://www.youtube.com/channel/UC_t11S41W6N6hA4FqM3Bwbw"},
        "월가아재": {"title": "[월가아재] 퀀트 분석으로 바라본 현재 시장의 버블 지수와 안전마진", "link": "https://www.youtube.com/channel/UCJptR2r0YqXv1628J0pXpCw"},
        "수페TV": {"title": "[수페TV] 장기 투자자를 위한 배당성장주 탑픽 및 섹터별 자산 배분 가이드", "link": "https://www.youtube.com/channel/UCiM27z7jO8O8xntKzF6Lh1A"}
    }
    for ch in channels:
        url = f"https://www.youtube.com/feeds/videos.xml?channel_id={ch['id']}"
        success = False
        for attempt in range(1): # Reduced from 3 to 1 to prevent blocking thread for minutes
            try:
                headers = {'User-Agent': 'Mozilla/5.0', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Language': 'ko-KR,ko;q=0.9', 'Cache-Control': 'no-cache'}
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=3) as response: # Reduced timeout to 3s
                    xml_data = response.read().decode('utf-8')
                    entry_match = re.search(r'<entry>(.*?)</entry>', xml_data, re.DOTALL)
                    if entry_match:
                        entry_text = entry_match.group(1)
                        title_match = re.search(r'<title>(.*?)</title>', entry_text)
                        title = title_match.group(1) if title_match else ""
                        vid_match = re.search(r'<yt:videoId>(.*?)</yt:videoId>', entry_text)
                        video_id = vid_match.group(1) if vid_match else ""
                        if title and video_id:
                            title = title.replace('<![CDATA[', '').replace(']]>', '').strip()
                            videos.append({"title": title, "channel": ch['name'], "summary": f"{ch['name']} 채널의 실시간 최신 분석 영상입니다.", "date": base_dt_now, "link": f"https://www.youtube.com/watch?v={video_id}", "image": f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"})
                            success = True
                            break
            except Exception as e:
                pass
        if not success:
            print(f"YouTube parse error for {ch['name']} after 3 attempts.")
            if ch['name'] in old_videos_map:
                videos.append(old_videos_map[ch['name']])
            else:
                fb = fallback_data.get(ch['name'], {"title": f"[{ch['name']}] 주요 경제 분석 영상", "link": f"https://www.youtube.com/channel/{ch['id']}"})
                videos.append({"title": fb["title"], "channel": ch['name'], "summary": f"{ch['name']} 채널의 주요 분석 영상입니다.", "date": base_dt_now, "link": fb["link"], "image": ch['img']})
    return videos

def get_dynamic_quotes():
    leaders = [
        {"author": "Jerome Powell", "role": "Federal Reserve Chairman",
         "query": "제롬 파월 연준", "en_query": "Jerome Powell Fed",
         "fallback_quote": '"인플레이션이 목표치인 2%를 향해 지속적으로 둔화하고 있다는 확신이 들 때까지 제약적인 통화정책을 유지할 것입니다."',
         "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8d/Jerome_H._Powell%2C_Federal_Reserve_portrait_%28cropped%29.jpg/120px-Jerome_H._Powell%2C_Federal_Reserve_portrait_%28cropped%29.jpg"},
        {"author": "Warren Buffett", "role": "Berkshire Hathaway CEO",
         "query": "워런 버핏 버크셔", "en_query": "Warren Buffett Berkshire",
         "fallback_quote": '"시장이 탐욕스러울 때 두려워하고, 시장이 두려워할 때 탐욕스러워져야 합니다."',
         "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/51/Warren_Buffett_KU_Visit.jpg/120px-Warren_Buffett_KU_Visit.jpg"},
        {"author": "Elon Musk", "role": "Tesla & SpaceX CEO",
         "query": "일론 머스크 테슬라", "en_query": "Elon Musk Tesla SpaceX",
         "fallback_quote": '"자율주행과 AI는 테슬라의 미래이자, 세상을 바꿀 가장 중요한 기술적 진보입니다."',
         "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/34/Elon_Musk_Royal_Society_%28crop2%29.jpg/120px-Elon_Musk_Royal_Society_%28crop2%29.jpg"},
        {"author": "Jensen Huang", "role": "NVIDIA CEO",
         "query": "젠슨 황 엔비디아", "en_query": "Jensen Huang NVIDIA",
         "fallback_quote": '"생성형 AI는 새로운 산업 혁명의 시작이며, 모든 비즈니스는 AI 공장이 될 것입니다."',
         "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/35/Jensen_Huang_CES_2018.jpg/120px-Jensen_Huang_CES_2018.jpg"},
        {"author": "Jamie Dimon", "role": "JPMorgan Chase CEO",
         "query": "제이미 다이먼 JP모건", "en_query": "Jamie Dimon JPMorgan economy",
         "fallback_quote": '"지정학적 리스크와 인플레이션 고착화 가능성에 대비해 경제의 불확실성을 예의주시해야 합니다."',
         "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d6/JamieDimon.jpg/120px-JamieDimon.jpg"},
        {"author": "Larry Fink", "role": "BlackRock CEO",
         "query": "래리 핑크 블랙록", "en_query": "Larry Fink BlackRock markets",
         "fallback_quote": '"장기적인 관점에서 자본 시장은 여전히 부를 창출하는 가장 강력한 엔진입니다."',
         "img": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=120&q=80"},
        {"author": "Ray Dalio", "role": "Bridgewater Associates Founder",
         "query": "레이 달리오 브리지워터", "en_query": "Ray Dalio economy markets",
         "fallback_quote": '"변화하는 세계 질서 속에서 투자자들은 포트폴리오의 다각화와 현금의 가치 하락에 대비해야 합니다."',
         "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7b/Ray_Dalio_Davos_2019_%28cropped%29.jpg/120px-Ray_Dalio_Davos_2019_%28cropped%29.jpg"},
        {"author": "Mark Zuckerberg", "role": "Meta CEO",
         "query": "마크 저커버그 메타", "en_query": "Mark Zuckerberg Meta AI",
         "fallback_quote": '"오픈소스 AI와 메타버스는 우리가 사람들을 연결하고 미래의 디지털 환경을 구축하는 핵심입니다."',
         "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/18/Mark_Zuckerberg_F8_2019_Keynote_%2832830578717%29_%28cropped%29.jpg/120px-Mark_Zuckerberg_F8_2019_Keynote_%2832830578717%29_%28cropped%29.jpg"},
        {"author": "Tim Cook", "role": "Apple CEO",
         "query": "팀 쿡 애플", "en_query": "Tim Cook Apple earnings",
         "fallback_quote": '"우리는 AI가 우리의 일상적인 기기에서 사용자의 프라이버시를 보호하면서 삶을 어떻게 풍요롭게 할 수 있는지에 집중합니다."',
         "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b9/Tim_Cook_2009_cropped.jpg/120px-Tim_Cook_2009_cropped.jpg"},
        {"author": "Bill Gates", "role": "Bill & Melinda Gates Foundation",
         "query": "빌 게이츠", "en_query": "Bill Gates technology economy",
         "fallback_quote": '"AI 발전은 인터넷이나 스마트폰의 등장만큼이나 혁명적이며, 모든 지식 노동의 생산성을 근본적으로 바꿀 것입니다."',
         "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a8/Bill_Gates_2017_%28cropped%29.jpg/120px-Bill_Gates_2017_%28cropped%29.jpg"},
    ]
    quotes_list = []
    translator_inst = GoogleTranslator(source='auto', target='ko')
    for ld in leaders:
        # 영어 구글 뉴스 우선 (1주일 이내)
        enc_q = urllib.parse.quote(ld['en_query'])
        url = f"https://news.google.com/rss/search?q={enc_q}+when:7d&hl=en-US&gl=US&ceid=US:en"
        quote_text = ld["fallback_quote"]
        link_href = f"https://www.google.com/search?q={urllib.parse.quote(ld['author'])}"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=6) as resp:
                root = ET.fromstring(resp.read().strip())
            for item in root.findall('.//item'):
                raw = item.findtext('title', '')
                clean = re.sub(r'\s-\s[^-]+$', '', raw).strip()
                if len(clean) > 15:
                    try:
                        clean_ko = translator_inst.translate(clean[:500])
                    except:
                        clean_ko = clean
                    quote_text = f'"{clean_ko}"'
                    link_href = item.findtext('link', link_href)
                    break
        except Exception as e:
            # 영어 실패 시 한국어 재시도
            try:
                enc_q2 = urllib.parse.quote(ld['query'])
                url2 = f"https://news.google.com/rss/search?q={enc_q2}+when:7d&hl=ko&gl=KR&ceid=KR:ko"
                req2 = urllib.request.Request(url2, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req2, timeout=5) as resp2:
                    root2 = ET.fromstring(resp2.read().strip())
                for item2 in root2.findall('.//item'):
                    raw2 = item2.findtext('title', '')
                    clean2 = re.sub(r'\s-\s[^-]+$', '', raw2).strip()
                    if len(clean2) > 10:
                        quote_text = f'"{clean2}"'
                        link_href = item2.findtext('link', link_href)
                        break
            except:
                pass
        quotes_list.append({
            "text": quote_text,
            "author": ld['author'],
            "role": ld['role'],
            "date": datetime.now().strftime("%Y.%m.%d"),
            "link": link_href,
            "image": ld['img']
        })
    return quotes_list

# ── RSS 초기 캐시 ──
rss_cache = {
    "top10_news": [{"title": "美 연준 이사진, 인플레이션 둔화세에 연내 금리 인하 가능성 시사", "summary": "통화정책 방향성을 가늠할 핵심 매크로 지표 발표 속 증시 자금 유입이 지속됩니다.", "source": "출처: WSJ", "hashtags": "#Fed통화정책 #금리인하 #유동성촉각", "date": base_dt, "time": "실시간", "link": "https://www.wsj.com", "image": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=400&q=80"}, {"title": "엔비디아 차세대 AI 칩 수요 폭발... 반도체 밸류체인 전반 슈퍼사이클 진입", "summary": "빅테크 기업들의 인프라 투자 확대로 관련 장비 및 부품주들의 실적 상향이 기대됩니다.", "source": "출처: Bloomberg", "hashtags": "#AI슈퍼사이클 #반도체랠리 #빅테크주도주", "date": base_dt, "time": "실시간", "link": "https://www.bloomberg.com", "image": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=400&q=80"}],
    "keyword_news": [{"keyword": "엔비디아", "news": []}, {"keyword": "금리인하", "news": []}, {"keyword": "비트코인", "news": []}, {"keyword": "테슬라", "news": []}, {"keyword": "밸류업", "news": []}],
    "youtube_insights": [{"title": "[슈카월드] 끝없이 오르는 미국 증시와 AI 반도체 전쟁의 승자는?", "channel": "슈카월드", "summary": "글로벌 매크로 지표 분석", "date": base_dt, "link": "https://www.youtube.com/watch?v=1", "image": "https://images.unsplash.com/photo-1611162617213-7d7a39e9b1d7?w=400&q=80"}],
    "dynamic_quotes": [{"text": "\"인플레이션 목표치 달성을 향한 경로에 확신이 들 때까지 통화정책의 인내심을 유지할 것입니다.\"", "author": "Jerome Powell", "role": "Federal Reserve Chairman", "date": base_dt, "link": "https://www.federalreserve.gov", "image": "https://images.unsplash.com/photo-1541872703-74c5e44368f9?w=100&q=80"}],
    "last_updated": time.time(),
    "lock": threading.Lock()
}

# ── 백그라운드 주식 데이터 수집 함수 (API 핸들러에서 절대 호출 금지) ──
def fetch_and_cache_market_data():
    global data_cache
    market_tickers = {"SPX": "^GSPC", "COMP": "^IXIC", "DJI": "^DJI", "KS11": "^KS11", "KQ11": "^KQ11", "N225": "^N225", "SSEC": "000001.SS"}
    company_tickers_full = {
        "Technology (기술/반도체)": [("Apple", "AAPL"), ("NVIDIA", "NVDA"), ("Microsoft", "MSFT"), ("삼성전자", "005930.KS"), ("SK하이닉스", "000660.KS")],
        "Automotive (자동차)": [("Tesla", "TSLA"), ("Toyota", "TM"), ("Ford", "F"), ("현대차", "005380.KS"), ("기아", "000270.KS")],
        "Financials (금융)": [("JPMorgan", "JPM"), ("Visa", "V"), ("Berkshire", "BRK-B"), ("KB금융", "105560.KS"), ("신한지주", "055550.KS")],
        "Health Care (헬스케어)": [("Eli Lilly", "LLY"), ("UnitedHealth", "UNH"), ("J&J", "JNJ"), ("삼성바이오로직스", "207940.KS"), ("셀트리온", "068270.KS")],
        "Materials & Chem (소재/화학)": [("Linde", "LIN"), ("Sherwin-Wms", "SHW"), ("LG화학", "051910.KS"), ("SK이노베이션", "096770.KS"), ("S-Oil", "010950.KS")]
    }
    us_sectors = [
        {"ticker": "XLK", "name": "Technology", "desc": "기술"}, {"ticker": "XLI", "name": "Industrials", "desc": "산업재"},
        {"ticker": "XLY", "name": "Cons. Discr.", "desc": "임의소비재"}, {"ticker": "XLP", "name": "Cons. Staples", "desc": "필수소비재"},
        {"ticker": "XLE", "name": "Energy", "desc": "에너지"}, {"ticker": "XLV", "name": "Health Care", "desc": "헬스케어"},
        {"ticker": "XLF", "name": "Financials", "desc": "금융"}, {"ticker": "XLC", "name": "Comm. Svcs", "desc": "통신"},
        {"ticker": "XLU", "name": "Utilities", "desc": "유틸리티"}, {"ticker": "XLB", "name": "Materials", "desc": "소재"},
        {"ticker": "XLRE", "name": "Real Estate", "desc": "부동산"}
    ]
    kr_sectors = [
        {"ticker": "229200.KS", "display": "KODEX 정보기술", "name": "Technology", "desc": "정보기술"},
        {"ticker": "091160.KS", "display": "KODEX 반도체", "name": "Semiconductors", "desc": "반도체"},
        {"ticker": "091180.KS", "display": "KODEX 자동차", "name": "Automobiles", "desc": "자동차"},
        {"ticker": "091170.KS", "display": "KODEX 은행", "name": "Banks", "desc": "은행"},
        {"ticker": "269620.KS", "display": "KODEX 헬스케어", "name": "Health Care", "desc": "헬스케어"},
        {"ticker": "117680.KS", "display": "KODEX 철강", "name": "Steel", "desc": "철강"},
        {"ticker": "117460.KS", "display": "KODEX 에너지화학", "name": "Chemicals", "desc": "에너지/화학"},
        {"ticker": "117700.KS", "display": "KODEX 건설", "name": "Construction", "desc": "건설"},
        {"ticker": "266360.KS", "display": "KODEX 미디어", "name": "Media", "desc": "미디어"},
        {"ticker": "266410.KS", "display": "KODEX 필수소비재", "name": "Cons. Staples", "desc": "필수소비재"}
    ]
    all_tickers = list(market_tickers.values()) + [s["ticker"] for s in us_sectors] + [s["ticker"] for s in kr_sectors]
    for c_list in company_tickers_full.values():
        all_tickers.extend([item[1] for item in c_list])
    unique_tickers = list(set(all_tickers))
    try:
        data = pd.DataFrame()
        for i in range(0, len(unique_tickers), 15):
            batch = unique_tickers[i:i+15]
            try:
                batch_data = yf.download(batch, period="14mo", group_by="ticker", threads=True, progress=False, timeout=20)
                if not batch_data.empty:
                    if data.empty: data = batch_data
                    else:
                        new_cols = batch_data.columns.levels[0].difference(data.columns.levels[0])
                        if not new_cols.empty: data = pd.concat([data, batch_data[new_cols]], axis=1)
            except Exception as e:
                print(f"[BG Market] 배치 실패 {batch}: {e}")
        if data.empty:
            print("[BG Market] 모든 티커 다운로드 실패, 스킵")
            return
        realtime_prices = {}
        try:
            for i in range(0, len(unique_tickers), 20):
                rt_batch = unique_tickers[i:i+20]
                try:
                    rt_data = yf.download(rt_batch, period="1d", interval="1m", group_by="ticker", threads=True, progress=False, timeout=15)
                    if not rt_data.empty:
                        for t_sym in rt_batch:
                            try:
                                if len(rt_batch) == 1: rt_hist = rt_data.dropna(subset=['Close'])
                                else:
                                    if t_sym not in rt_data.columns.get_level_values(0): continue
                                    rt_hist = rt_data[t_sym].dropna(subset=['Close'])
                                if not rt_hist.empty: realtime_prices[t_sym] = float(rt_hist['Close'].iloc[-1])
                            except: pass
                except: pass
        except Exception as e:
            print(f"[BG Market] 실시간 가격 실패: {e}")
        spx_hist = data["^GSPC"].dropna(subset=['Close']) if "^GSPC" in data.columns.levels[0] else None
        def standard_date(days_ago):
            if spx_hist is None or spx_hist.empty: return ""
            idx = min(days_ago, len(spx_hist)-1)
            return spx_hist.index[-1 - idx].strftime('%y.%m.%d')
        def process_ticker(t_sym, symbol_type="usd"):
            empty_changes = {k: {"pct": 0, "price": "N/A"} for k in ["today", "d1", "d3", "w1", "m1", "m3", "m6", "y1"]}
            try:
                if data.empty or t_sym not in data.columns.levels[0]: return {"value": "N/A", "changes": empty_changes}
                hist = data[t_sym].dropna(subset=['Close'])
                if hist.empty: return {"value": "N/A", "changes": empty_changes}
                daily_close = float(hist['Close'].iloc[-1])
                current_close = realtime_prices.get(t_sym, daily_close)
                def format_price(p):
                    if p == "N/A" or p == 0: return "N/A"
                    if symbol_type == "krw" or t_sym.endswith(".KS") or t_sym.endswith(".KQ"): return f"₩{p:,.0f}"
                    elif symbol_type == "idx": return f"{p:,.2f}"
                    else: return f"${p:,.2f}"
                raw_changes = calculate_changes(hist, current_close)
                return {"value": format_price(current_close), "changes": {k: {"pct": v["pct"], "price": format_price(v["raw_price"])} for k, v in raw_changes.items()}}
            except:
                return {"value": "N/A", "changes": empty_changes}
        result = {
            "baseDate": f"{datetime.now().strftime('%Y년 %m월 %d일 %H:%M')} 라이브 API 기준",
            "dates": {"current": standard_date(0) or "현재가", "d1": standard_date(1), "d3": standard_date(3), "w1": standard_date(5), "m1": standard_date(21), "m3": standard_date(63), "m6": standard_date(126), "y1": standard_date(252)},
            "markets": [
                {"name": "S&P 500", "region": "미국", "ticker": "SPX", "yahoo_ticker": "^GSPC", **process_ticker("^GSPC", "idx")},
                {"name": "NASDAQ", "region": "미국", "ticker": "COMP", "yahoo_ticker": "^IXIC", **process_ticker("^IXIC", "idx")},
                {"name": "Dow Jones", "region": "미국", "ticker": "DJI", "yahoo_ticker": "^DJI", **process_ticker("^DJI", "idx")},
                {"name": "KOSPI", "region": "한국", "ticker": "KS11", "yahoo_ticker": "^KS11", **process_ticker("^KS11", "idx")},
                {"name": "KOSDAQ", "region": "한국", "ticker": "KQ11", "yahoo_ticker": "^KQ11", **process_ticker("^KQ11", "idx")},
                {"name": "Nikkei 225", "region": "일본", "ticker": "N225", "yahoo_ticker": "^N225", **process_ticker("^N225", "idx")},
                {"name": "Shanghai Comp", "region": "중국", "ticker": "SSEC", "yahoo_ticker": "000001.SS", **process_ticker("000001.SS", "idx")}
            ],
            "usSectors": [{"ticker": s["ticker"], "yahoo_ticker": s["ticker"], "name": s["name"], "desc": s["desc"], **process_ticker(s["ticker"], "usd")} for s in us_sectors],
            "krSectors": [{"ticker": s["display"], "yahoo_ticker": s["ticker"], "name": s["name"], "desc": s["desc"], **process_ticker(s["ticker"], "krw")} for s in kr_sectors],
            "companiesBySector": {
                sector: [{"name": item[0], "ticker": item[1].replace(".KS", ""), "yahoo_ticker": item[1], "logo": "", **process_ticker(item[1], "krw" if ".KS" in item[1] else "usd")} for item in t_list]
                for sector, t_list in company_tickers_full.items()
            },
            "news": rss_cache["top10_news"], "keywordNews": rss_cache["keyword_news"],
            "quotes": rss_cache["dynamic_quotes"], "youtube": rss_cache["youtube_insights"]
        }
        data_cache["data"] = result
        data_cache["last_updated"] = time.time()
        print("[BG Market] [SUCCESS] 주식 데이터 캐시 갱신 완료!")
    except Exception as e:
        print(f"[BG Market] [ERROR] 오류: {e}")

# ── 번역 없는 빠른 뉴스 (초기 로딩용) ──
def _get_news_fast():
    """번역 없이 영어 제목 그대로 반환 - 빠른 초기 로딩용"""
    feeds = [
        "https://feeds.bloomberg.com/markets/news.rss",
        "https://feeds.marketwatch.com/marketwatch/topstories/",
        "https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=en&gl=US&ceid=US:en",
    ]
    collected, seen = [], set()
    for feed_url in feeds:
        try:
            req = urllib.request.Request(feed_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=6) as resp:
                root = ET.fromstring(resp.read().strip())
            for item in root.findall('.//item'):
                raw = item.findtext('title', '').strip()
                link = item.findtext('link', '').strip()
                clean = re.sub(r'\s-\s[^-]+$', '', raw).strip()
                if len(clean) < 10: continue
                key = clean[:40].lower()
                if key in seen: continue
                seen.add(key)
                collected.append({
                    "title": clean, "summary": clean,
                    "source": item.findtext('source', feed_url.split('/')[2]),
                    "hashtags": generate_news_hashtags(clean),
                    "date": datetime.now().strftime("%Y.%m.%d"),
                    "time": "실시간", "link": link, "image": ""
                })
                if len(collected) >= 10: return collected
        except: pass
    return collected

# ── 번역 없는 빠른 인사 발언 (초기 로딩용) ──
def _get_quotes_fast():
    """번역 없이 영어 기사 제목 그대로 - 빠른 초기 로딩용"""
    leaders_simple = [
        ("Jerome Powell", "Federal Reserve Chairman", "Jerome Powell Fed"),
        ("Warren Buffett", "Berkshire Hathaway CEO", "Warren Buffett Berkshire"),
        ("Elon Musk", "Tesla & SpaceX CEO", "Elon Musk Tesla"),
        ("Jensen Huang", "NVIDIA CEO", "Jensen Huang NVIDIA"),
        ("Jamie Dimon", "JPMorgan Chase CEO", "Jamie Dimon JPMorgan"),
        ("Larry Fink", "BlackRock CEO", "Larry Fink BlackRock"),
        ("Ray Dalio", "Bridgewater Founder", "Ray Dalio economy"),
        ("Mark Zuckerberg", "Meta CEO", "Mark Zuckerberg Meta"),
        ("Tim Cook", "Apple CEO", "Tim Cook Apple"),
        ("Bill Gates", "Gates Foundation", "Bill Gates technology"),
    ]
    results = []
    for author, role, query in leaders_simple:
        enc = urllib.parse.quote(query)
        url = f"https://news.google.com/rss/search?q={enc}+when:7d&hl=en-US&gl=US&ceid=US:en"
        text = f'"{author}의 최신 시장 동향과 경제적 관점을 주목하십시오."'
        link = f"https://www.google.com/search?q={urllib.parse.quote(author)}"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as resp:
                root = ET.fromstring(resp.read().strip())
            for item in root.findall('.//item'):
                raw = item.findtext('title', '')
                clean = re.sub(r'\s-\s[^-]+$', '', raw).strip()
                if len(clean) > 15:
                    text = f'"{clean}"'
                    link = item.findtext('link', link)
                    break
        except: pass
        results.append({"text": text, "author": author, "role": role,
                        "date": datetime.now().strftime("%Y.%m.%d"), "link": link,
                        "image": f"https://www.google.com/search?q={urllib.parse.quote(author)}"})
    return results

# ── 백그라운드 RSS + 주식 데이터 통합 갱신 스레드 ──
def update_rss_cache_background():
    global rss_cache
    time.sleep(2)  # 서버 부팅 완료 대기
    try:
        # ① 주식 데이터를 가장 먼저 수집 (사용자가 주가를 먼저 보도록)
        print("[Background Engine] [START] 주식 데이터 최우선 수집 시작...")
        fetch_and_cache_market_data()
        print("[Background Engine] [DONE] 주식 데이터 완료!")

        # ② 번역 없는 빠른 뉴스/발언 캐시 (개별 갱신으로 사용자 대기 최소화)
        print("[Background Engine] [START] 빠른 RSS 수집 (번역 전)...")
        t_news_fast = _get_news_fast()
        if t_news_fast:
            with rss_cache["lock"]: rss_cache["top10_news"] = t_news_fast
            
        d_quotes_fast = _get_quotes_fast()
        if d_quotes_fast:
            with rss_cache["lock"]: rss_cache["dynamic_quotes"] = d_quotes_fast
            
        keywords = extract_trending_keywords()
        k_news = get_keyword_news(keywords)
        if k_news:
            with rss_cache["lock"]: rss_cache["keyword_news"] = k_news
            
        y_insights = get_youtube_insights()
        if y_insights:
            with rss_cache["lock"]: rss_cache["youtube_insights"] = y_insights
        print("[Background Engine] [DONE] 빠른 RSS 완료!")

        # ③ 한글 번역 포함 정확한 버전으로 교체
        print("[Background Engine] [START] 한글 번역 뉴스/발언 수집...")
        t_news_ko = get_top10_news()
        if t_news_ko:
            with rss_cache["lock"]: rss_cache["top10_news"] = t_news_ko
            
        d_quotes_ko = get_dynamic_quotes()
        if d_quotes_ko:
            with rss_cache["lock"]: rss_cache["dynamic_quotes"] = d_quotes_ko
            
        with rss_cache["lock"]: rss_cache["last_updated"] = time.time()
        print("[Background Engine] [DONE] 한글 번역 완료!")
    except Exception as e:
        print(f"[Background Engine] [ERROR] 최초 갱신 오류: {e}")

    while True:
        time.sleep(600)  # 10분 대기
        try:
            print("[Background Engine] [START] 주기적 RSS/주식 데이터 갱신...")
            fetch_and_cache_market_data()
            
            t_news = get_top10_news()
            if t_news:
                with rss_cache["lock"]: rss_cache["top10_news"] = t_news
                
            keywords = extract_trending_keywords()
            k_news = get_keyword_news(keywords)
            if k_news:
                with rss_cache["lock"]: rss_cache["keyword_news"] = k_news
                
            y_insights = get_youtube_insights()
            if y_insights:
                with rss_cache["lock"]: rss_cache["youtube_insights"] = y_insights
                
            d_quotes = get_dynamic_quotes()
            if d_quotes:
                with rss_cache["lock"]: rss_cache["dynamic_quotes"] = d_quotes
                
            with rss_cache["lock"]: rss_cache["last_updated"] = time.time()
            print("[Background Engine] [DONE] 주기적 갱신 완료!")
        except Exception as e:
            print(f"[Background Engine] [ERROR] 주기적 갱신 오류: {e}")


@app.route("/")
def home():
    return send_from_directory(".", "index.html")

@app.route("/ping")
def ping():
    """슬립 방지 전용 초경량 엔드포인트 — 즉시 200 응답, 연산 없음"""
    return jsonify({"status": "alive", "ts": time.time()}), 200

@app.route('/api/market-data')
def market_data():
    global data_cache
    # ★ 캐시가 있으면 즉시 반환 (yfinance 호출 없음, 0.1초 이내, 절대 502 없음)
    if data_cache["data"] is not None:
        cached = dict(data_cache["data"])
        cached["news"] = rss_cache["top10_news"]
        cached["keywordNews"] = rss_cache["keyword_news"]
        cached["quotes"] = rss_cache["dynamic_quotes"]
        cached["youtube"] = rss_cache["youtube_insights"]
        return jsonify(cached)
    # ★ 서버 최초 기동 직후 캐시가 없으면 fallback 즉시 반환
    fallback = dict(FALLBACK_DATA)
    fallback["news"] = rss_cache["top10_news"]
    fallback["keywordNews"] = rss_cache["keyword_news"]
    fallback["quotes"] = rss_cache["dynamic_quotes"]
    fallback["youtube"] = rss_cache["youtube_insights"]
    return jsonify(fallback)

# ── /api/search 엔드포인트 ──
@app.route('/api/search')
def search_stock():
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({"error": "검색어를 입력해주세요."}), 400

    # 1. 야후 파이낸스로 티커 자동 변환
    try:
        search_url = f"https://query2.finance.yahoo.com/v1/finance/search?q={urllib.parse.quote(query)}&quotesCount=5"
        req = urllib.request.Request(search_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=6) as resp:
            data = json.loads(resp.read().decode())
        quotes_list = data.get('quotes', [])
        if not quotes_list:
            return jsonify({"error": "검색 결과가 없습니다."}), 404
        equity = next((q for q in quotes_list if q.get('quoteType') in ['EQUITY', 'ETF']), quotes_list[0])
        symbol    = equity['symbol']
        short_name = equity.get('shortname') or equity.get('longname', symbol)
        exchange  = equity.get('exchange', '')
    except Exception as e:
        return jsonify({"error": f"종목 검색 실패: {e}"}), 500

    # 2. yfinance로 과거 주가 등락률 계산
    try:
        ticker = yf.Ticker(symbol)
        hist   = ticker.history(period="2y")
        if hist.empty:
            return jsonify({"error": "주가 데이터를 찾을 수 없습니다."}), 404
        current_price = float(hist['Close'].iloc[-1])

        def get_past_price(days_ago):
            target_str = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
            past = hist.loc[:target_str]
            return float(past['Close'].iloc[-1]) if not past.empty else None

        def safe_pct(past_price):
            if past_price is None or past_price == 0:
                return {"pct": 0.0, "price": "N/A"}
            return {"pct": round(((current_price - past_price) / past_price) * 100, 1),
                    "price": f"{past_price:,.2f}"}

        changes = {
            "today": safe_pct(get_past_price(1)),
            "d1":    safe_pct(get_past_price(1)),
            "d3":    safe_pct(get_past_price(3)),
            "w1":    safe_pct(get_past_price(7)),
            "m1":    safe_pct(get_past_price(30)),
            "m3":    safe_pct(get_past_price(90)),
            "m6":    safe_pct(get_past_price(180)),
            "y1":    safe_pct(get_past_price(365)),
        }
    except Exception as e:
        return jsonify({"error": f"주가 데이터 수집 실패: {e}"}), 500

    # 3. 구글 뉴스 크롤링 + 한글 번역
    news_items = []
    try:
        news_q   = urllib.parse.quote(f"{short_name} OR {symbol} stock")
        news_url = f"https://news.google.com/rss/search?q={news_q}&hl=en-US&gl=US&ceid=US:en"
        req = urllib.request.Request(news_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=6) as resp:
            root = ET.fromstring(resp.read().strip())
        translator = GoogleTranslator(source='auto', target='ko')
        for item in root.findall('.//item')[:7]:
            raw_title = item.findtext('title', '')
            # 언론사 이름 제거 (" - 언론사" 패턴)
            clean_title = re.sub(r'\s-\s[^-]+$', '', raw_title).strip()
            link     = item.findtext('link', '')
            pub_date = item.findtext('pubDate', '')
            source   = item.findtext('source', 'Google News')
            try:
                dt = datetime.strptime(pub_date[:25], "%a, %d %b %Y %H:%M:%S")
                date_str = dt.strftime("%Y-%m-%d %H:%M")
            except Exception:
                date_str = pub_date[:16]
            try:
                translated = translator.translate(clean_title[:500])
            except Exception:
                translated = clean_title
            news_items.append({
                "title":          translated,
                "original_title": clean_title,
                "link":           link,
                "date":           date_str,
                "source":         source,
            })
    except Exception as e:
        print(f"[Search] News fetch failed: {e}")

    # 4. 네이버 링크 생성
    is_kr       = symbol.endswith('.KS') or symbol.endswith('.KQ')
    base_symbol = symbol.split('.')[0]
    if is_kr:
        naver_board_url = f"https://finance.naver.com/item/board.naver?code={base_symbol}"
    else:
        naver_board_url = f"https://finance.naver.com/world/sise.naver?symbol={base_symbol}"
    naver_cafe_url = (f"https://search.naver.com/search.naver?where=article"
                      f"&query={urllib.parse.quote(short_name + ' ' + base_symbol)}"
                      f"&ds=&de=&nso=so%3Add%2Cp%3Aall&ie=utf8")

    return jsonify({
        "symbol":   symbol,
        "name":     short_name,
        "exchange": exchange,
        "price":    f"{current_price:,.2f}",
        "changes":  changes,
        "news":     news_items,
        "links": {
            "naver_board": naver_board_url,
            "naver_cafe":  naver_cafe_url,
        },
    })

# 서버 메인 루프 실행 전 비동기 스레드 스타트
threading.Thread(target=update_rss_cache_background, daemon=True).start()

if __name__ == '__main__':
    app.run(debug=True, port=5000, host="0.0.0.0")
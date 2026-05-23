import concurrent.futures
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

import xml.etree.ElementTree as ET

def get_youtube_insights():
    channels = [
        {"name": "슈카월드", "id": "UCsJ6RuBiTVWRX156FVbeaGg"},
        {"name": "월가아재의과학적투자", "id": "UCpqD9_OJNtF6suPpi6mOQCQ"},
        {"name": "박종훈지식한방", "id": "UCOB62fKRT7b73X7tRxMuN2g"},
        {"name": "소수몽키", "id": "UCC3yfxS5qC6PCwDzetUuEWg"},
        {"name": "전인구경제연구소", "id": "UCznImSIaxZR7fdLCICLdgaQ"},
        {"name": "수페TV", "id": "UCfnqgWlC5IvJEAPTmyjaixA"},
        {"name": "이효석아카데미", "id": "UCxvdCnvGODDyuvnELnLkQWw"}
    ]
    
    def fetch_channel(ch):
        url = f"https://api.rss2json.com/v1/api.json?rss_url=https://www.youtube.com/feeds/videos.xml?channel_id={ch['id']}"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())
                item = data['items'][0]
                title = item['title']
                link = item['link']
                # pubDate format: 2026-05-22 13:42:48
                pub_date = item['pubDate'].split(' ')[0].replace('-', '.')
                return {"title": title, "channel": ch["name"], "date": pub_date, "link": link}
        except Exception as e:
            print(f"[YouTube] Error fetching {ch['name']}: {e}")
        
        base_dt_now = datetime.now().strftime("%Y.%m.%d")
        return {"title": f"[{ch['name']}] 최신 유튜브 영상", "channel": ch["name"], "date": base_dt_now, "link": f"https://www.youtube.com/channel/{ch['id']}"}

    results = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_ch = {executor.submit(fetch_channel, ch): ch for ch in channels}
        for future in as_completed(future_to_ch):
            res = future.result()
            if res:
                results.append(res)
    return results

def get_dynamic_quotes():
    leaders = [
        {"author": "Warren Buffett", "role": "Berkshire Hathaway CEO", "query": "워런 버핏", "en_query": "Warren Buffett", "fallback_quote": '"시장이 탐욕스러울 때 두려워하고, 시장이 두려워할 때 탐욕스러워져야 합니다."'},
        {"author": "Bill Ackman", "role": "Pershing Square Capital CEO", "query": "빌 에크먼", "en_query": "Bill Ackman", "fallback_quote": '"최고의 투자는 위기 상황에서 인내심을 갖고 가치 있는 자산을 헐값에 매입하는 것입니다."'},
        {"author": "Howard Marks", "role": "Oaktree Capital Co-Chairman", "query": "하워드 막스", "en_query": "Howard Marks", "fallback_quote": '"가장 중요한 것은 무엇을 아느냐가 아니라 우리가 모른다는 사실을 아는 것입니다."'},
        {"author": "Mark Minervini", "role": "Author & Trader", "query": "마크 미너비니", "en_query": "Mark Minervini", "fallback_quote": '"성공적인 트레이딩의 핵심은 손실은 짧게 끊고 이익은 길게 가져가는 규율에 있습니다."'},
        {"author": "Stanley Druckenmiller", "role": "Duquesne Family Office", "query": "스탠리 드러켄밀러", "en_query": "Stanley Druckenmiller", "fallback_quote": '"맞고 틀리는 것이 중요한 게 아니라, 맞았을 때 얼마나 많이 벌고 틀렸을 때 얼마나 적게 잃는지가 중요합니다."'},
        {"author": "Paul Tudor Jones", "role": "Tudor Investment Corp", "query": "폴 튜더 존스", "en_query": "Paul Tudor Jones", "fallback_quote": '"당신이 할 수 있는 가장 중요한 룰은 방어적인 플레이를 하는 것입니다. 결코 공격적인 플레이가 아닙니다."'},
        {"author": "Kevin Warsh", "role": "Former Federal Reserve Governor", "query": "케빈 워시", "en_query": "Kevin Warsh Fed", "fallback_quote": '"연준의 통화정책은 시장의 기대에 끌려다니기보다 선제적으로 실물 경제의 펀더멘털을 반영해야 합니다."'},
    ]
    translator_inst = GoogleTranslator(source='auto', target='ko')
    
    def fetch_leader(ld):
        enc_q = urllib.parse.quote(ld['en_query'])
        url = f"https://news.google.com/rss/search?q={enc_q}+when:180d&hl=en-US&gl=US&ceid=US:en"
        quote_text = ld["fallback_quote"]
        link_href = f"https://www.google.com/search?q={urllib.parse.quote(ld['author'])}"
        pub_date = datetime.now().strftime("%Y.%m.%d")
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as resp:
                root = ET.fromstring(resp.read().strip())
            for item in root.findall('.//item'):
                raw = item.findtext('title', '')
                clean = re.sub(r'\s-\s[^-]+$', '', raw).strip()
                if len(clean) > 15:
                    pub_date_node = item.find('pubDate')
                    if pub_date_node is not None:
                        try:
                            dt = datetime.strptime(pub_date_node.text[:25], "%a, %d %b %Y %H:%M:%S")
                            pub_date = dt.strftime("%Y.%m.%d")
                        except: pass
                    try:
                        clean_ko = translator_inst.translate(clean[:500])
                    except:
                        clean_ko = clean
                    quote_text = f'"{clean_ko}"'
                    link_href = item.findtext('link', link_href)
                    break
        except Exception as e:
            pass
        return {"text": quote_text, "author": ld["author"], "role": ld["role"], "date": pub_date, "link": link_href}
        
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        quotes_list = list(executor.map(fetch_leader, leaders))
        
    return quotes_list
# ── RSS 초기 캐시 ──
rss_cache = {
    "top10_news": [],
    "keyword_news": [],
    "youtube_insights": [
        {"title": "[슈카월드] 최신 업로드 영상", "channel": "슈카월드", "date": datetime.now().strftime("%Y.%m.%d"), "link": "https://www.youtube.com/channel/UCsJ6RuBiTVWRX156FVbeaGg"},
        {"title": "[월가아재의과학적투자] 최신 업로드 영상", "channel": "월가아재의과학적투자", "date": datetime.now().strftime("%Y.%m.%d"), "link": "https://www.youtube.com/channel/UCJptR2r0YqXv1628J0pXpCw"},
        {"title": "[박종훈지식한방] 최신 업로드 영상", "channel": "박종훈지식한방", "date": datetime.now().strftime("%Y.%m.%d"), "link": "https://www.youtube.com/channel/UC5cKPnu2NpaxKjU2UBuvVxA"},
        {"title": "[소수몽키] 최신 업로드 영상", "channel": "소수몽키", "date": datetime.now().strftime("%Y.%m.%d"), "link": "https://www.youtube.com/channel/UC_t11S41W6N6hA4FqM3Bwbw"},
        {"title": "[전인구경제연구소] 최신 업로드 영상", "channel": "전인구경제연구소", "date": datetime.now().strftime("%Y.%m.%d"), "link": "https://www.youtube.com/channel/UCznImSIaxZR7fdLCICLdgaQ"},
        {"title": "[수페TV] 최신 업로드 영상", "channel": "수페TV", "date": datetime.now().strftime("%Y.%m.%d"), "link": "https://www.youtube.com/channel/UCiM27z7jO8O8xntKzF6Lh1A"},
        {"title": "[이효석아카데미] 최신 업로드 영상", "channel": "이효석아카데미", "date": datetime.now().strftime("%Y.%m.%d"), "link": "https://www.youtube.com/channel/UCn6a15h1H1Z61K8Pj_66G-A"}
    ],
    "dynamic_quotes": [
        {"text": '"시장이 탐욕스러울 때 두려워하고, 시장이 두려워할 때 탐욕스러워져야 합니다."', "author": "Warren Buffett", "role": "Berkshire Hathaway CEO", "date": datetime.now().strftime("%Y.%m.%d"), "link": "https://www.google.com/search?q=%EC%9B%8C%EB%9F%B0+%EB%B2%84%ED%95%8F"},
        {"text": '"최고의 투자는 위기 상황에서 인내심을 갖고 가치 있는 자산을 헐값에 매입하는 것입니다."', "author": "Bill Ackman", "role": "Pershing Square Capital CEO", "date": datetime.now().strftime("%Y.%m.%d"), "link": "https://www.google.com/search?q=%EB%B9%8C+%EC%97%90%ED%81%AC%EB%A8%BC"},
        {"text": '"가장 중요한 것은 무엇을 아느냐가 아니라 우리가 모른다는 사실을 아는 것입니다."', "author": "Howard Marks", "role": "Oaktree Capital Co-Chairman", "date": datetime.now().strftime("%Y.%m.%d"), "link": "https://www.google.com/search?q=%ED%95%98%EC%9B%8C%EB%93%9C+%EB%A7%89%EC%8A%A4"},
        {"text": '"성공적인 트레이딩의 핵심은 손실은 짧게 끊고 이익은 길게 가져가는 규율에 있습니다."', "author": "Mark Minervini", "role": "Author & Trader", "date": datetime.now().strftime("%Y.%m.%d"), "link": "https://www.google.com/search?q=%EB%A7%88%ED%81%AC+%EB%AF%B8%EB%84%88%EB%B9%84%EB%8B%88"},
        {"text": '"맞고 틀리는 것이 중요한 게 아니라, 맞았을 때 얼마나 많이 벌고 틀렸을 때 얼마나 적게 잃는지가 중요합니다."', "author": "Stanley Druckenmiller", "role": "Duquesne Family Office", "date": datetime.now().strftime("%Y.%m.%d"), "link": "https://www.google.com/search?q=%EC%8A%A4%ED%83%A0%EB%A6%AC+%EB%93%9C%EB%9F%AC%EC%BC%84%EB%B0%80%EB%9F%AC"},
        {"text": '"당신이 할 수 있는 가장 중요한 룰은 방어적인 플레이를 하는 것입니다. 결코 공격적인 플레이가 아닙니다."', "author": "Paul Tudor Jones", "role": "Tudor Investment Corp", "date": datetime.now().strftime("%Y.%m.%d"), "link": "https://www.google.com/search?q=%ED%8F%B4+%ED%8A%9C%EB%8D%94+%EC%A1%B4%EC%8A%A4"},
        {"text": '"연준의 통화정책은 시장의 기대에 끌려다니기보다 선제적으로 실물 경제의 펀더멘털을 반영해야 합니다."', "author": "Kevin Warsh", "role": "Former Federal Reserve Governor", "date": datetime.now().strftime("%Y.%m.%d"), "link": "https://www.google.com/search?q=%EC%BC%80%EB%B9%88+%EC%9B%8C%EC%8B%9C"}
    ],
    "last_updated": time.time(),
    "lock": threading.Lock()
}

CACHE_FILE = "market_cache.json"
import os

if os.path.exists(CACHE_FILE):
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            cache_data = json.load(f)
            data_cache["data"] = cache_data.get("market_data")
            data_cache["last_updated"] = os.path.getmtime(CACHE_FILE)
            if "rss_data" in cache_data:
                rss_cache.update(cache_data["rss_data"])
            print("[Startup] Loaded all data from local cache file.")
    except Exception as e:
        print(f"[Startup] Error loading cache file: {e}")

import pytz

def is_any_market_open():
    try:
        now_utc = datetime.now(pytz.utc)
        
        # US Market (09:30 to 16:00 ET, Mon-Fri)
        et_tz = pytz.timezone('US/Eastern')
        now_et = now_utc.astimezone(et_tz)
        us_open = False
        if now_et.weekday() < 5:
            if datetime.strptime("09:30", "%H:%M").time() <= now_et.time() <= datetime.strptime("16:00", "%H:%M").time():
                us_open = True

        # KR Market (09:00 to 15:30 KST, Mon-Fri)
        kst_tz = pytz.timezone('Asia/Seoul')
        now_kst = now_utc.astimezone(kst_tz)
        kr_open = False
        if now_kst.weekday() < 5:
            if datetime.strptime("09:00", "%H:%M").time() <= now_kst.time() <= datetime.strptime("15:30", "%H:%M").time():
                kr_open = True

        return us_open or kr_open
    except Exception as e:
        print("Error checking market hours:", e)
        return True # Default to fetching if error



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
# ── 번역 없는 빠른 인사 발언 (초기 로딩용) ──
# ── 백그라운드 RSS + 주식 데이터 통합 갱신 스레드 ──
def update_rss_cache_background():
    global rss_cache
    time.sleep(1)  # 서버 부팅 완료 대기
    try:
        print("[Background Engine] [START] 유튜브 인사이트 수집...")
        y_insights = get_youtube_insights()
        if y_insights:
            with rss_cache["lock"]: rss_cache["youtube_insights"] = y_insights
            
        print("[Background Engine] [START] 인사 발언 수집...")
        d_quotes_ko = get_dynamic_quotes()
        if d_quotes_ko:
            with rss_cache["lock"]: rss_cache["dynamic_quotes"] = d_quotes_ko
            
        print("[Background Engine] [START] 주식 데이터 최우선 수집 시작...")
        fetch_and_cache_market_data()
        print("[Background Engine] [DONE] 주식 데이터 완료!")
            
        with rss_cache["lock"]: rss_cache["last_updated"] = time.time()
        print("[Background Engine] [DONE] 초기 갱신 완료!")
    except Exception as e:
        print(f"[Background Engine] [ERROR] 최초 갱신 오류: {e}")

    while True:
        time.sleep(600)  # 10분 대기
        try:
            print("[Background Engine] [START] 주기적 RSS/주식 데이터 갱신...")
            fetch_and_cache_market_data()
            
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


_thread_started = False

@app.route('/api/market-data')
def market_data():
    global data_cache, _thread_started
    if not _thread_started:
        _thread_started = True
        import threading
        threading.Thread(target=update_rss_cache_background, daemon=True).start()

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
        sector_val = equity.get('sectorDisp') or equity.get('sector', 'N/A')
        industry_val = equity.get('industryDisp') or equity.get('industry', 'N/A')
    except Exception as e:
        return jsonify({"error": f"종목 검색 실패: {e}"}), 500

    # 2. yfinance로 과거 주가 등락률 계산
    try:
        ticker = yf.Ticker(symbol)
        hist   = ticker.history(period="2y")
        if hist.empty:
            return jsonify({"error": "주가 데이터를 찾을 수 없습니다."}), 404
        current_price = float(hist['Close'].iloc[-1])

        def get_past_data(days_ago):
            target_str = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
            past = hist.loc[:target_str]
            if not past.empty:
                return float(past['Close'].iloc[-1]), past.index[-1].strftime('%y.%m.%d')
            return None, ""

        def safe_pct(past_data):
            past_price, past_date = past_data
            if past_price is None or past_price == 0:
                return {"pct": 0.0, "price": "N/A", "date": ""}
            return {"pct": round(((current_price - past_price) / past_price) * 100, 1),
                    "price": f"{past_price:,.2f}", "date": past_date}

        changes = {
            "today": safe_pct(get_past_data(1)),
            "d1":    safe_pct(get_past_data(1)),
            "d3":    safe_pct(get_past_data(3)),
            "w1":    safe_pct(get_past_data(7)),
            "m1":    safe_pct(get_past_data(30)),
            "m3":    safe_pct(get_past_data(90)),
            "m6":    safe_pct(get_past_data(180)),
            "y1":    safe_pct(get_past_data(365)),
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

    # 4. 토론방 링크 생성 및 기업 정보 가져오기
    is_kr       = symbol.endswith('.KS') or symbol.endswith('.KQ')
    base_symbol = symbol.split('.')[0]
    if is_kr:
        naver_board_url = f"https://finance.naver.com/item/board.naver?code={base_symbol}"
    else:
        # 미국 주식은 야후 파이낸스 토론방으로 연결
        naver_board_url = f"https://finance.yahoo.com/quote/{base_symbol}/community"

    # 기업 개요 가져오기
    company_profile = {}
    try:
        # yfinance info 가 렌더에서 차단되므로 fast_info 사용
        try:
            market_cap = ticker_obj.fast_info['market_cap']
        except:
            market_cap = 0
            
        # 시총 포맷팅
        if market_cap == 0:
            mc_str = "N/A"
        elif is_kr:
            if market_cap >= 1_000_000_000_000:
                mc_str = f"{market_cap / 1_000_000_000_000:.1f}조 원"
            else:
                mc_str = f"{market_cap / 100_000_000:.0f}억 원"
        else:
            if market_cap >= 1_000_000_000_000:
                mc_str = f"${market_cap / 1_000_000_000_000:.2f}T"
            else:
                mc_str = f"${market_cap / 1_000_000_000:.2f}B"
                
        # summary fetching via Wikipedia API
        summary = ""
        try:
            # removing 'Inc.', 'Corp.', 'Co., Ltd.' for better wiki match
            clean_name = short_name.split(',')[0].replace(' Inc.', '').replace(' Corp.', '').replace(' Co.', '').replace(' Ltd.', '')
            wiki_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(clean_name)}"
            req = urllib.request.Request(wiki_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=3) as resp:
                summary = json.loads(resp.read().decode('utf-8')).get('extract', '')
        except:
            pass
            
        # 번역
        translator = GoogleTranslator(source='auto', target='ko')
        try:
            sector_ko = translator.translate(sector_val) if sector_val != "N/A" else "N/A"
            industry_ko = translator.translate(industry_val) if industry_val != "N/A" else "N/A"
            summary_ko = translator.translate(summary[:1500]) if summary else "기업 설명이 제공되지 않습니다."
        except:
            sector_ko = sector_val
            industry_ko = industry_val
            summary_ko = summary

        # 관련 기업 가져오기 (Naver API)
        related_stocks = []
        try:
            if is_kr:
                naver_url = f"https://m.stock.naver.com/api/stock/{base_symbol}/integration"
                req_n = urllib.request.Request(naver_url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req_n, timeout=3) as resp_n:
                    n_data = json.loads(resp_n.read().decode('utf-8'))
                compare_list = n_data.get('industryCompareInfo', [])
                for s in compare_list:
                    # add up to 10
                    if len(related_stocks) >= 10: break
                    if s.get('itemCode') != base_symbol:
                        related_stocks.append({"name": s.get('stockName'), "symbol": s.get('itemCode') + ".KS"})
            else:
                naver_url = f"https://api.stock.naver.com/stock/{base_symbol}.O/integration"
                req_n = urllib.request.Request(naver_url, headers={'User-Agent': 'Mozilla/5.0'})
                try:
                    with urllib.request.urlopen(req_n, timeout=3) as resp_n:
                        n_data = json.loads(resp_n.read().decode('utf-8'))
                except:
                    # fallback to .N
                    naver_url = f"https://api.stock.naver.com/stock/{base_symbol}.N/integration"
                    req_n = urllib.request.Request(naver_url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req_n, timeout=3) as resp_n:
                        n_data = json.loads(resp_n.read().decode('utf-8'))
                
                compare_info = n_data.get('industryCompareInfo', {})
                global_stocks = compare_info.get('globalStocks', [])
                for s in global_stocks:
                    if len(related_stocks) >= 10: break
                    if s.get('symbolCode') != base_symbol:
                        related_stocks.append({"name": s.get('stockName'), "symbol": s.get('symbolCode')})
        except Exception as e:
            print(f"[Search] Related stocks fetch failed: {e}")

        company_profile = {
            "marketCap": mc_str, # Will be removed in frontend
            "sector": sector_ko,
            "industry": industry_ko,
            "summary": summary_ko,
            "related_stocks": related_stocks
        }
    except Exception as e:
        print(f"[Search] Info fetch failed: {e}")

    # EPS 실적 가져오기
    earnings_list = []
    try:
        ed = ticker.earnings_dates
        if ed is not None and not ed.empty:
            ed = ed.reset_index()
            # Earnings Date가 과거인 것만 필터링, Event Type이 Earnings인 것만
            ed['Earnings Date'] = pd.to_datetime(ed['Earnings Date'], utc=True)
            now_utc = pd.Timestamp.now(tz='UTC')
            past_ed = ed[(ed['Earnings Date'] < now_utc) & ((ed['Event Type'] == 'Earnings') | (ed['Event Type'].isna()))].copy()
            past_ed = past_ed.sort_values(by='Earnings Date', ascending=False).head(20) # 5년 * 4분기 = 20개
            past_ed = past_ed.sort_values(by='Earnings Date', ascending=True) # 오름차순 (과거->현재)
            
            for _, row in past_ed.iterrows():
                try:
                    dt_str = row['Earnings Date'].strftime('%Y-%m-%d')
                    est = row.get('EPS Estimate')
                    rep = row.get('Reported EPS')
                    surp = row.get('Surprise(%)')
                    if pd.isna(est) and pd.isna(rep): continue
                    
                    earnings_list.append({
                        "date": dt_str,
                        "estimate": float(est) if not pd.isna(est) else None,
                        "reported": float(rep) if not pd.isna(rep) else None,
                        "surprise": float(surp) if not pd.isna(surp) else None
                    })
                except Exception as inner_e:
                    print(f"Error parsing row: {inner_e}")
    except Exception as e:
        print(f"[Search] Earnings fetch failed: {e}")

    return jsonify({
        "symbol":   symbol,
        "name":     short_name,
        "exchange": exchange,
        "price":    f"{current_price:,.2f}",
        "changes":  changes,
        "news":     news_items,
        "profile":  company_profile,
        "links": {
            "naver_board": naver_board_url
        },
    })

# 서버 메인 루프 실행 전 비동기 스레드 스타트


if __name__ == '__main__':
    app.run(debug=True, port=5000, host="0.0.0.0")
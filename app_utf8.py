from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import yfinance as yf
import pandas as pd
from datetime import datetime
import time

app = Flask(__name__, static_url_path='', static_folder='.')
CORS(app)

# 湲濡쒕쾶 ?곗씠??罹먯떆 (5遺??좏슚)
data_cache = {
    "data": None,
    "last_updated": 0
}
CACHE_DURATION = 300 # 5遺?
def calculate_changes(hist, current_close):
    try:
        if len(hist) < 2: return {"d1":0, "d3":0, "w1":0, "m1":0, "m3":0, "m6":0, "y1":0}
        
        def get_pct(days_ago):
            # ?곸뾽??湲곗? ?몃뜳??異붿텧 (洹쇱궗移?
            idx = min(days_ago, len(hist)-1)
            old_price = float(hist['Close'].iloc[-1 - idx])
            if old_price == 0: return 0
            return round(((current_close - old_price) / old_price) * 100, 2)
            
        return {
            "d1": get_pct(1),
            "d3": get_pct(3),
            "w1": get_pct(5),
            "m1": get_pct(21),
            "m3": get_pct(63), 
            "m6": get_pct(126),
            "y1": get_pct(252)
        }
    except:
        return {"d1":0, "d3":0, "w1":0, "m1":0, "m3":0, "m6":0, "y1":0}

@app.route("/")
def home():
    return send_from_directory(".", "index.html")

@app.route('/api/market-data')
def market_data():
    global data_cache
    
    # 1. 罹먯떆 泥댄겕
    current_time = time.time()
    if data_cache["data"] and (current_time - data_cache["last_updated"] < CACHE_DURATION):
        return jsonify(data_cache["data"])

    market_tickers = {
        "SPX": "^GSPC", "COMP": "^IXIC", "DJI": "^DJI",
        "KS11": "^KS11", "KQ11": "^KQ11", 
        "N225": "^N225", "SSEC": "000001.SS"
    }
    
    company_tickers_full = {
        "Technology (湲곗닠/諛섎룄泥?": [
            ("Apple", "AAPL"), ("NVIDIA", "NVDA"), ("Microsoft", "MSFT"), 
            ("?쇱꽦?꾩옄", "005930.KS"), ("SK?섏씠?됱뒪", "000660.KS")
        ],
        "Automotive (?먮룞李?": [
            ("Tesla", "TSLA"), ("Toyota", "TM"), ("Ford", "F"), 
            ("?꾨?李?, "005380.KS"), ("湲곗븘", "000270.KS")
        ],
        "Financials (湲덉쑖)": [
            ("JPMorgan", "JPM"), ("Visa", "V"), ("Berkshire", "BRK-B"), 
            ("KB湲덉쑖", "105560.KS"), ("?좏븳吏二?, "055550.KS")
        ],
        "Health Care (?ъ뒪耳??": [
            ("Eli Lilly", "LLY"), ("UnitedHealth", "UNH"), ("J&J", "JNJ"), 
            ("?쇱꽦諛붿씠?ㅻ줈吏곸뒪", "207940.KS"), ("??몃━??, "068270.KS")
        ],
        "Materials & Chem (?뚯옱/?뷀븰)": [
            ("Linde", "LIN"), ("Sherwin-Wms", "SHW"), 
            ("LG?뷀븰", "051910.KS"), ("SK?대끂踰좎씠??, "096770.KS"), ("S-Oil", "010950.KS")
        ]
    }
    
    us_sectors = [
        {"ticker": "XLK", "name": "Technology", "desc": "湲곗닠"},
        {"ticker": "XLI", "name": "Industrials", "desc": "?곗뾽??},
        {"ticker": "XLY", "name": "Cons. Discr.", "desc": "?꾩쓽?뚮퉬??},
        {"ticker": "XLP", "name": "Cons. Staples", "desc": "?꾩닔?뚮퉬??},
        {"ticker": "XLE", "name": "Energy", "desc": "?먮꼫吏"},
        {"ticker": "XLV", "name": "Health Care", "desc": "?ъ뒪耳??},
        {"ticker": "XLF", "name": "Financials", "desc": "湲덉쑖"},
        {"ticker": "XLC", "name": "Comm. Svcs", "desc": "?듭떊"},
        {"ticker": "XLU", "name": "Utilities", "desc": "?좏떥由ы떚"},
        {"ticker": "XLB", "name": "Materials", "desc": "?뚯옱"},
        {"ticker": "XLRE", "name": "Real Estate", "desc": "遺?숈궛"}
    ]
    
    kr_sectors = [
        {"ticker": "229200.KS", "display": "KODEX ?뺣낫湲곗닠", "name": "Technology", "desc": "?뺣낫湲곗닠"},
        {"ticker": "091160.KS", "display": "KODEX 諛섎룄泥?, "name": "Semiconductors", "desc": "諛섎룄泥?},
        {"ticker": "091180.KS", "display": "KODEX ?먮룞李?, "name": "Automobiles", "desc": "?먮룞李?},
        {"ticker": "091170.KS", "display": "KODEX ???, "name": "Banks", "desc": "???},
        {"ticker": "269620.KS", "display": "KODEX ?ъ뒪耳??, "name": "Health Care", "desc": "?ъ뒪耳??},
        {"ticker": "117680.KS", "display": "KODEX 泥좉컯", "name": "Steel", "desc": "泥좉컯"},
        {"ticker": "117460.KS", "display": "KODEX ?먮꼫吏?뷀븰", "name": "Chemicals", "desc": "?먮꼫吏/?뷀븰"},
        {"ticker": "117700.KS", "display": "KODEX 嫄댁꽕", "name": "Construction", "desc": "嫄댁꽕"},
        {"ticker": "266360.KS", "display": "KODEX 誘몃뵒??, "name": "Media", "desc": "誘몃뵒??},
        {"ticker": "266410.KS", "display": "KODEX ?꾩닔?뚮퉬??, "name": "Cons. Staples", "desc": "?꾩닔?뚮퉬??}
    ]
    
    # ?곗빱 紐⑸줉 ?듯빀
    all_tickers = list(market_tickers.values()) + [s["ticker"] for s in us_sectors] + [s["ticker"] for s in kr_sectors]
    for c_list in company_tickers_full.values():
        all_tickers.extend([item[1] for item in c_list])
    unique_tickers = list(set(all_tickers))
        
    try:
        # 理쒖쟻?? 湲곌컙??1.5?꾩쑝濡??⑥텞 (?곌컙 ?섏씡瑜?怨꾩궛???꾩슂)
        data = yf.download(unique_tickers, period="18mo", group_by="ticker", threads=True, progress=False)
        
        # ?ㅼ슫濡쒕뱶媛 鍮꾩뼱?덈뒗吏 ?뺤씤
        if data.empty: raise Exception("Yahoo Finance returned no data")

        # 湲곗???泥섎━??(S&P 500 湲곗?)
        spx_sym = "^GSPC"
        spx_hist = data[spx_sym].dropna(subset=['Close']) if spx_sym in data.columns.levels[0] else None

        def standard_date(days_ago):
            if spx_hist is None or spx_hist.empty: return ""
            idx = min(days_ago, len(spx_hist)-1)
            return spx_hist.index[-1 - idx].strftime('%y.%m.%d')

        def process_ticker(t_sym, symbol_type="usd"):
            try:
                if t_sym not in data.columns.levels[0]: return {"value": "N/A", "changes": {"d1":0, "d3":0, "w1":0, "m1":0, "m3":0, "m6":0, "y1":0}}
                
                hist = data[t_sym].dropna(subset=['Close'])
                if hist.empty: raise Exception("No data")
                
                current_close = float(hist['Close'].iloc[-1])
                
                if symbol_type == "krw" or t_sym.endswith(".KS") or t_sym.endswith(".KQ"):
                    val_str = f"??current_close:,.0f}"
                elif symbol_type == "idx":
                    val_str = f"{current_close:,.2f}"
                else:
                    val_str = f"${current_close:,.2f}"
                    
                changes = calculate_changes(hist, current_close)
                return {"value": val_str, "changes": changes}
            except:
                return {"value": "N/A", "changes": {"d1":0, "d3":0, "w1":0, "m1":0, "m3":0, "m6":0, "y1":0}}

        result = {
            "baseDate": f"{datetime.now().strftime('%Y??%m??%d??%H:%M')} ?쇱씠釉?API 湲곗?",
            "dates": {
                "current": standard_date(0) if standard_date(0) else "?꾩옱媛",
                "d1": f"{standard_date(1)}", "d3": f"{standard_date(3)}", "w1": f"{standard_date(5)}",
                "m1": f"{standard_date(21)}", "m3": f"{standard_date(63)}", "m6": f"{standard_date(126)}", "y1": f"{standard_date(252)}"
            },
            "markets": [
                { "name": "S&P 500", "region": "誘멸뎅", "ticker": "SPX", "yahoo_ticker": "^GSPC", **process_ticker("^GSPC", "idx") },
                { "name": "NASDAQ", "region": "誘멸뎅", "ticker": "COMP", "yahoo_ticker": "^IXIC", **process_ticker("^IXIC", "idx") },
                { "name": "Dow Jones", "region": "誘멸뎅", "ticker": "DJI", "yahoo_ticker": "^DJI", **process_ticker("^DJI", "idx") },
                { "name": "KOSPI", "region": "?쒓뎅", "ticker": "KS11", "yahoo_ticker": "^KS11", **process_ticker("^KS11", "idx") },
                { "name": "KOSDAQ", "region": "?쒓뎅", "ticker": "KQ11", "yahoo_ticker": "^KQ11", **process_ticker("^KQ11", "idx") },
                { "name": "Nikkei 225", "region": "?쇰낯", "ticker": "N225", "yahoo_ticker": "^N225", **process_ticker("^N225", "idx") },
                { "name": "Shanghai Comp", "region": "以묎뎅", "ticker": "SSEC", "yahoo_ticker": "000001.SS", **process_ticker("000001.SS", "idx") }
            ],
            "usSectors": [{"ticker": s["ticker"], "yahoo_ticker": s["ticker"], "name": s["name"], "desc": s["desc"], **process_ticker(s["ticker"], "usd")} for s in us_sectors],
            "krSectors": [{"ticker": s["display"], "yahoo_ticker": s["ticker"], "name": s["name"], "desc": s["desc"], **process_ticker(s["ticker"], "krw")} for s in kr_sectors],
            "companiesBySector": {
                sector: [
                    {
                        "name": item[0], "ticker": item[1].replace(".KS", ""), "yahoo_ticker": item[1], 
                        "logo": "", 
                        **process_ticker(item[1], "krw" if ".KS" in item[1] else "usd")
                    } for item in t_list
                ] for sector, t_list in company_tickers_full.items()
            },
            "news": [
                { "title": "?곗?(Fed) 源쒖쭩 湲덈━ ?ㅽ깲??蹂??.. ?붽???'?곕쭚 由대젅??湲덈━ ?명븯 湲곕?' ?섑샇", "summary": "Fed???ν썑 湲덈━ ?명븯 媛?μ꽦????먮릺硫?利앹떆媛 ?덈줈??援?㈃??留욎븯?듬땲??", "source": "Bloomberg", "date": datetime.now().strftime("%Y.%m.%d"), "time": "2?쒓컙 ??, "link": "https://finance.yahoo.com/news/", "image": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=400&q=80" },
                { "title": "?붾퉬?붿븘 諛?AI 諛섎룄泥??섏슂 ???쬆, 愿?⑥＜ ?곗씪 ?곹븳媛 ?좊━", "summary": "李⑥꽭? 釉붾옓??移⑹쓽 湲곕줉?곸씤 ?섏슂? ?④퍡 諛섎룄泥?諛몃쪟泥댁씤 ?꾨컲???섑삙瑜??낃퀬 ?덉뒿?덈떎.", "source": "Financial Times", "date": datetime.now().strftime("%Y.%m.%d"), "time": "3?쒓컙 ??, "link": "https://finance.yahoo.com/quote/NVDA/news", "image": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=400&q=80" },
                { "title": "?뚯뒳?? ?꾩쟾?먯쑉二쇳뻾(FSD) 湲濡쒕쾶 ?곸슜???꾨컯... ?꾩꽦李??쒖옣 ?먮룄 ?붾뱾源?, "summary": "癒몄뒪??CEO媛 FSD ?곗씠??紐⑤뜽留??꾨즺瑜??좎뼵?섎ŉ ?ㅽ넗紐⑦떚釉??쒖옣???뚯옣???쇱쑝?ㅺ퀬 ?덉뒿?덈떎.", "source": "WSJ", "date": "2026.04.27", "time": "12?쒓컙 ??, "link": "https://finance.yahoo.com/quote/TSLA/news", "image": "https://images.unsplash.com/photo-1561518776-e76a5e48f731?w=400&q=80" },
                { "title": "?쒓뎅 諛몃쪟???꾨줈洹몃옩 ?ㅽ슚???낆쬆?섎굹... ?멸뎅???ъ옄??KOSPI ?嫄??좎엯", "summary": "?PBR 湲곗뾽?ㅼ쓽 ?洹쒕え ?먯궗二??뚭컖 諛쒗몴 ?댄썑 踰ㅼ튂留덊겕 吏?섏쓽 媛뺣젰??吏吏?좎씠 ?뺤꽦?섏뿀?듬땲??", "source": "?쒓뎅寃쎌젣", "date": "2026.04.27", "time": "15?쒓컙 ??, "link": "https://finance.yahoo.com/quote/KS11.KS/news", "image": "https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?w=400&q=80" },
                { "title": "援?젣?좉? ?덉젙???뚮났, ?먮꼫吏 諛???났二?V??諛섎벑 ?깃났", "summary": "以묐룞 諛?吏?뺥븰??由ъ뒪???꾪솕濡??먯쑀 ?좊Ъ???덉젙??李얠쑝硫?愿???곗뾽?ㅼ씠 ??컻?곸씤 ?뚮났?꾨젰?깆쓣 蹂댁엯?덈떎.", "source": "MarketWatch", "date": "2026.04.27", "time": "16?쒓컙 ??, "link": "https://finance.yahoo.com/commodities", "image": "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=400&q=80" },
                { "title": "以묎뎅諛?媛뺣젰??遺?묒콉 諛쒗몴 ?꾨컯... ?꾩떆???좏씎援?利앹떆 ?숇컲 媛뺤꽭 ?먮쫫", "summary": "以묒븰??됱쓽 異붽??곸씤 吏以???명븯 ?뚮Ц???뚮㈃??SSEC 以묒떖???洹쒕え ?먭툑 ?ъ엯???덉긽?⑸땲??", "source": "South China Morning Post", "date": "2026.04.26", "time": "2????, "link": "https://finance.yahoo.com/quote/000001.SS", "image": "https://images.unsplash.com/photo-1541888035777-17e92ce1ab52?w=400&q=80" },
                { "title": "鍮꾪듃肄붿씤 ??媛?곸옄?곌낵 留ㅺ렇?덊뵾?쇳듃7 二쇨????곴?愿怨???? 理쒓퀬移?湲곕줉", "summary": "由ъ뒪?????먯궛?쇰줈 痍④툒?섎뒗 ?뷀샇?뷀룓? 鍮낇뀒?ъ쓽 ?吏곸엫??媛뺣젰???숆린???섍퀬 ?덉뒿?덈떎.", "source": "CNBC", "date": "2026.04.26", "time": "2????, "link": "https://finance.yahoo.com/quote/BTC-USD", "image": "https://images.unsplash.com/photo-1516245834210-c4c142787335?w=400&q=80" },
                { "title": "湲濡쒕쾶 ?곸뾽??遺?숈궛 ?꾧린 吏꾩젙?? 由ъ툩(REITs)ETF 諛섎컻 留ㅼ닔 ??컻", "summary": "誘멸뎅 ?ㅽ뵾??怨듭떎瑜좎씠 ?덉젙???ъ씠?댁뿉 吏꾩엯?섎ŉ 湲덉쑖沅???遺???먯궛 ?곕젮媛 ?산꺼?섍컮?듬땲??", "source": "Reuters", "date": "2026.04.25", "time": "3????, "link": "https://finance.yahoo.com/quote/VNQ", "image": "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=400&q=80" },
                { "title": "李⑥꽭? 濡쒕큸 怨듯븰 諛??ъ뒪耳??AI ?묐ぉ ?좉퇋 ?ㅽ??몄뾽?ㅼ쓽 IPO 愿묓뭾", "summary": "??2???룹뺨踰꾨툝???곗긽耳 ??留뚰겮 ?ν뀒??湲곗뾽?ㅼ쓽 ?곸옣???붽?瑜??⑹닽怨??덉뒿?덈떎.", "source": "TechCrunch", "date": "2026.04.24", "time": "4????, "link": "https://finance.yahoo.com/news/", "image": "https://images.unsplash.com/photo-1531746790731-6c087fecd65a?w=400&q=80" },
                { "title": "二쇱슂 湲곗뾽?ㅼ쓽 留됰????됱뿬?꾧툑?먮쫫, ?洹쒕え ?먯궗二?留ㅼ엯怨?諛곕떦 ??깂 ?좎뼵", "summary": "?대떇 ?쒗봽?쇱씠利덈? ?ъ꽦??二쇱슂 ?湲곗뾽?ㅼ씠 ?욌떎?ъ뼱 留됯컯??二쇱＜?섏썝 ?⑦궎吏瑜??쒖옣???섏?怨??덉뒿?덈떎.", "source": "Yahoo Finance", "date": "2026.04.23", "time": "5????, "link": "https://finance.yahoo.com/news/", "image": "https://images.unsplash.com/photo-1591696205602-2f950c417cb9?w=400&q=80" }
            ],
            "quotes": [
                {
                    "text": "\"?먮낯二쇱쓽 ?쒖옣???④린???붾뱾由쇱뿉 ?쇳씗?쇰퉬?섏? 留덉떗?쒖삤. ?뚮???鍮꾩쫰?덉뒪 紐⑤뜽? 寃곌뎅 ?몄젣???쒖옄由щ? 李얠뒿?덈떎.\"",
                    "author": "Warren Buffett", "role": "Berkshire Hathaway CEO", "date": "2026.04.25",
                    "link": "https://en.wikipedia.org/wiki/Warren_Buffett", "image": "https://images.unsplash.com/photo-1556157382-97eda2f9e2bf?w=100&q=80"
                },
                {
                    "text": "\"吏湲덉? 洹밸떒?곸씤 ?숆?二쇱쓽???ш린???됲깭瑜??쇳븯怨? 泥좎?????붾찘?멸낵 媛移섏뿉 吏묒쨷?댁빞 ??諛⑹뼱???곗쐞???쒓린?낅땲??\"",
                    "author": "Howard Marks", "role": "Oaktree Capital Co-Chairman", "date": "2026.04.22",
                    "link": "https://en.wikipedia.org/wiki/Howard_Marks_(investor)", "image": "https://images.unsplash.com/photo-1560250097-0b93528c311a?w=100&q=80"
                },
                {
                    "text": "\"?쒖옣??嫄곕???異붿꽭媛 ?뱀떊???ъ??섏쓣 吏吏?섏? ?딅뒗?? ?뱀떊??遺꾩꽍?????怨쇰룄???뺤떊? ?ㅽ엳???낆씠 ?????덉뒿?덈떎.\"",
                    "author": "Mark Minervini", "role": "Stock Market Wizard & Author", "date": "2026.04.27",
                    "link": "https://en.wikipedia.org/wiki/Mark_Minervini", "image": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=100&q=80"
                },
                {
                    "text": "\"紐⑤뱺 ?쒖옣???吏곸엫?먮뒗 ?ъ씠?댁씠 議댁옱?⑸땲?? 吏湲덉쓽 寃⑸젹??蹂?숈꽦? ?덈줈???몃젋?쒖쓽 ?쒖옉?먯씪 ???덉뒿?덈떎.\"",
                    "author": "Paul Tudor Jones", "role": "Tudor Investment Corp Founder", "date": "2026.04.26",
                    "link": "https://en.wikipedia.org/wiki/Paul_Tudor_Jones", "image": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=100&q=80"
                },
                {
                    "text": "\"?멸났吏??AI)怨?李⑥꽭? 而댄벂???곸떊 援ъ“???κ린 ?ъ옄?섏? ?딅뒗 寃껋? ??궗???뚮룄瑜?湲곌볼????뻾?섎뒗 寃껉낵 媛숈뒿?덈떎.\"",
                    "author": "Stanley Druckenmiller", "role": "Duquesne Family Office", "date": "2026.04.28",
                    "link": "https://en.wikipedia.org/wiki/Stanley_Druckenmiller", "image": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&q=80"
                },
                {
                    "text": "\"媛뺣젰???낆젏???꾧툑?먮쫫怨??명뵆?덉씠??諛⑹뼱?μ쓣 吏??湲곗뾽?대씪硫? ?대뼡 嫄곗떆寃쎌젣????뭾 以묒떖?먯꽌???ы듃?대━?ㅻ? 吏耳쒖쨪 寃껋엯?덈떎.\"",
                    "author": "Bill Ackman", "role": "Pershing Square Capital CEO", "date": "2026.04.21",
                    "link": "https://en.wikipedia.org/wiki/Bill_Ackman", "image": "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=100&q=80"
                }
            ],
            "youtube": [
                {
                    "title": "?섏뒪????씫?μ쓽 ?댁쑀? 諛붾떏 ?좏샇 吏묒쨷 遺꾩꽍 (?좏뵆, ?뚯뒳??吏묒쨷 ?먭?)",
                    "channel": "?뚯닔紐쏀궎",
                    "summary": "湲덈━ ?몄긽 怨듯룷媛 利앹떆??誘몄튂???곹뼢怨??④퍡, ?곕웾 鍮낇뀒??二쇱떇??遺꾪븷 留ㅼ닔?댁빞 ??紐낇솗???먮떒 湲곗????쒖떆?⑸땲??",
                    "date": "2026.04.28", "link": "https://www.youtube.com/watch?v=2Sy5b0N4u8A", "image": "https://i.ytimg.com/vi/2Sy5b0N4u8A/hqdefault.jpg"
                },
                {
                    "title": "Fed ?뚯썡 ?섏옣???띾룄 議곗젅 諛쒖뼵, 怨쇱뿰 ?쒓뎅 遺?숈궛/利앹떆???λ갑??",
                    "channel": "諛뺤쥌?덉쓽 寃쎌젣?쒕갑",
                    "summary": "?섏쑉 湲됰벑?쎄낵 ?뚯썡??肄붾찘???ъ씠???대㈃???좎뭅濡?쾶 ?대??섍퀬 ?ㅼ쭏?곸씤 留ㅽ겕濡?????꾨왂???몄썙遊낅땲??",
                    "date": "2026.04.27", "link": "https://www.youtube.com/watch?v=SexyT911CPY", "image": "https://i.ytimg.com/vi/SexyT911CPY/hqdefault.jpg"
                },
                {
                    "title": "????ъ옄 湲곕쾿?쇰줈 ?뚯븘蹂대뒗 理쒓렐 媛移섏＜ ?좊━???ㅼ껜",
                    "channel": "?붽??꾩옱??怨쇳븰?곹닾??,
                    "summary": "?④린 ?몄씠利덈? ?꾪꽣留곹븯怨?諛깊뀒?ㅽ듃 ?듦퀎瑜?洹쇨굅濡??꾩옱 ?쒖옣?먯꽌 ?댁븘?④린 ?꾪븳 ?곗씠??二쇰룄???ъ옄濡좎쓣 由щ럭?⑸땲??",
                    "date": "2026.04.27", "link": "https://www.youtube.com/watch?v=8L6vix_byUM", "image": "https://i.ytimg.com/vi/8L6vix_byUM/hqdefault.jpg"
                },
                {
                    "title": "諛곕떦二?ETF ?ы듃?대━???뚯씠?꾨씪??留ㅼ썡 100留뚯썝 留뚮뱾湲??ㅼ쟾 ?명똿",
                    "channel": "?섑럹TV",
                    "summary": "SCHD, JEPI ???멸린媛 ?믪? 怨좊같??ETF???ㅼ쭏 諛곕떦瑜좎쓣 ?ъ젏寃?섍퀬 ?댁긽?곸씤 ?⑥떆釉??몄뺨 援ъ“瑜??ㅺ퀎?⑸땲??",
                    "date": "2026.04.26", "link": "https://www.youtube.com/watch?v=A1R5o6Zjw9s", "image": "https://i.ytimg.com/vi/A1R5o6Zjw9s/hqdefault.jpg"
                },
                {
                    "title": "2026???섎컲湲?寃쎌젣 吏媛?蹂?? 吏湲??뱀옣 ?붿븘????二쇱떇怨??ъ빞 ??二쇱떇",
                    "channel": "?꾩씤援?寃쎌젣?곌뎄??,
                    "summary": "吏?섍? ?뺤껜??諛뺤뒪沅??μ꽭 ?띿뿉??湲덈━, ?섏쑉, ?먯옄??吏?쒕뱾??醫낇빀 遺꾩꽍???ㅺ????ъ씠?댁쓣 ?덉륫?⑸땲??",
                    "date": "2026.04.25", "link": "https://www.youtube.com/watch?v=AohLeRLp610", "image": "https://i.ytimg.com/vi/AohLeRLp610/hqdefault.jpg"
                },
                {
                    "title": "URGENT Market Update: Why I Just Sold My Entire Portfolio & Preparing For The Crash",
                    "channel": "Meet Kevin",
                    "summary": "Technical and fundamental analysis explaining the sudden shift in broad market momentum and real estate worries.",
                    "date": "2026.04.28", "link": "https://www.youtube.com/watch?v=0d3kJRWoHaA", "image": "https://i.ytimg.com/vi/0d3kJRWoHaA/hqdefault.jpg"
                },
                {
                    "title": "The Hidden Truth About The Economy Right Now (Warning Signs)",
                    "channel": "Graham Stephan",
                    "summary": "Exploring the unspoken data behind inflation reports and what it exactly implies for the individual stock investor.",
                    "date": "2026.04.26", "link": "https://www.youtube.com/watch?v=TTHTa5i-Plw", "image": "https://i.ytimg.com/vi/TTHTa5i-Plw/hqdefault.jpg"
                }
            ]
        }
        
        # 2. 罹먯떆 ?낅뜲?댄듃
        data_cache["data"] = result
        data_cache["last_updated"] = time.time()
        
        return jsonify(result)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000, host="0.0.0.0")
듭쓣 ?몄썙遊낅땲??",
                    "date": "2026.04.27", "link": "https://www.youtube.com/watch?v=SexyT911CPY", "image": "https://i.ytimg.com/vi/SexyT911CPY/hqdefault.jpg"
                },
                {
                    "title": "????ъ옄 湲곕쾿?쇰줈 ?뚯븘蹂대뒗 理쒓렐 媛移섏＜ ?좊━???ㅼ껜",
                    "channel": "?붽??꾩옱??怨쇳븰?곹닾??,
                    "summary": "?④린 ?몄씠利덈? ?꾪꽣留곹븯怨?諛깊뀒?ㅽ듃 ?듦퀎瑜?洹쇨굅濡??꾩옱 ?쒖옣?먯꽌 ?댁븘?④린 ?꾪븳 ?곗씠??二쇰룄???ъ옄濡좎쓣 由щ럭?⑸땲??",
                    "date": "2026.04.27", "link": "https://www.youtube.com/watch?v=8L6vix_byUM", "image": "https://i.ytimg.com/vi/8L6vix_byUM/hqdefault.jpg"
                },
                {
                    "title": "諛곕떦二?ETF ?ы듃?대━???뚯씠?꾨씪??留ㅼ썡 100留뚯썝 留뚮뱾湲??ㅼ쟾 ?명똿",
                    "channel": "?섑럹TV",
                    "summary": "SCHD, JEPI ???멸린媛 ?믪? 怨좊같??ETF???ㅼ쭏 諛곕떦瑜좎쓣 ?ъ젏寃?섍퀬 ?댁긽?곸씤 ?⑥떆釉??몄뺨 援ъ“瑜??ㅺ퀎?⑸땲??",
                    "date": "2026.04.26", "link": "https://www.youtube.com/watch?v=A1R5o6Zjw9s", "image": "https://i.ytimg.com/vi/A1R5o6Zjw9s/hqdefault.jpg"
                },
                {
                    "title": "2026???섎컲湲?寃쎌젣 吏媛?蹂?? 吏湲??뱀옣 ?붿븘????二쇱떇怨??ъ빞 ??二쇱떇",
                    "channel": "?꾩씤援?寃쎌젣?곌뎄??,
                    "summary": "吏?섍? ?뺤껜??諛뺤뒪沅??μ꽭 ?띿뿉??湲덈━, ?섏쑉, ?먯옄??吏?쒕뱾??醫낇빀 遺꾩꽍???ㅺ????ъ씠?댁쓣 ?덉륫?⑸땲??",
                    "date": "2026.04.25", "link": "https://www.youtube.com/watch?v=AohLeRLp610", "image": "https://i.ytimg.com/vi/AohLeRLp610/hqdefault.jpg"
                },
                {
                    "title": "URGENT Market Update: Why I Just Sold My Entire Portfolio & Preparing For The Crash",
                    "channel": "Meet Kevin",
                    "summary": "Technical and fundamental analysis explaining the sudden shift in broad market momentum and real estate worries.",
                    "date": "2026.04.28", "link": "https://www.youtube.com/watch?v=0d3kJRWoHaA", "image": "https://i.ytimg.com/vi/0d3kJRWoHaA/hqdefault.jpg"
                },
                {
                    "title": "The Hidden Truth About The Economy Right Now (Warning Signs)",
                    "channel": "Graham Stephan",
                    "summary": "Exploring the unspoken data behind inflation reports and what it exactly implies for the individual stock investor.",
                    "date": "2026.04.26", "link": "https://www.youtube.com/watch?v=TTHTa5i-Plw", "image": "https://i.ytimg.com/vi/TTHTa5i-Plw/hqdefault.jpg"
                }
            ]
        }
        return jsonify(response)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000, host="0.0.0.0")

import re

with open("app.py", "r", encoding="utf-8") as f:
    text = f.read()

# 1. Modify the search_stock to save sector and industry
# Currently:
# symbol     = quotes[0].get('symbol')
# short_name = quotes[0].get('shortname', symbol)
# exchange   = quotes[0].get('exchange', '')

new_quotes = """                symbol     = quotes[0].get('symbol')
                short_name = quotes[0].get('shortname', symbol)
                exchange   = quotes[0].get('exchange', '')
                sector_val = quotes[0].get('sectorDisp') or quotes[0].get('sector', 'N/A')
                industry_val = quotes[0].get('industryDisp') or quotes[0].get('industry', 'N/A')"""

text = text.replace("                symbol     = quotes[0].get('symbol')\n                short_name = quotes[0].get('shortname', symbol)\n                exchange   = quotes[0].get('exchange', '')", new_quotes)


# 2. Modify the company_profile block
old_profile = """    # 기업 개요 가져오기
    company_profile = {}
    try:
        info = ticker_obj.info
        market_cap = info.get("marketCap", 0)
        # 시총 포맷팅 (조/억 단위 또는 Trillion/Billion)
        if is_kr:
            if market_cap >= 1_000_000_000_000:
                mc_str = f"{market_cap / 1_000_000_000_000:.1f}조 원"
            else:
                mc_str = f"{market_cap / 100_000_000:.0f}억 원"
        else:
            if market_cap >= 1_000_000_000_000:
                mc_str = f"${market_cap / 1_000_000_000_000:.2f}T"
            else:
                mc_str = f"${market_cap / 1_000_000_000:.2f}B"
                
        sector = info.get("sector", "N/A")
        industry = info.get("industry", "N/A")
        summary = info.get("longBusinessSummary", "")
        
        # 번역
        translator = GoogleTranslator(source='auto', target='ko')
        try:
            sector_ko = translator.translate(sector) if sector != "N/A" else "N/A"
            industry_ko = translator.translate(industry) if industry != "N/A" else "N/A"
            summary_ko = translator.translate(summary[:1500]) if summary else "기업 설명이 제공되지 않습니다."
        except:
            sector_ko = sector
            industry_ko = industry
            summary_ko = summary

        company_profile = {
            "marketCap": mc_str,
            "sector": sector_ko,
            "industry": industry_ko,
            "summary": summary_ko
        }
    except Exception as e:
        print(f"[Search] Info fetch failed: {e}")"""

new_profile = """    # 기업 개요 가져오기
    company_profile = {}
    try:
        # yfinance info 가 렌더에서 차단되므로 fast_info 사용
        try:
            market_cap = ticker_obj.fast_info.get("market_cap", 0)
        except:
            market_cap = 0
            
        # 시총 포맷팅
        if is_kr:
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

        company_profile = {
            "marketCap": mc_str,
            "sector": sector_ko,
            "industry": industry_ko,
            "summary": summary_ko
        }
    except Exception as e:
        print(f"[Search] Info fetch failed: {e}")"""

# We need to initialize sector_val and industry_val to 'N/A' at the top just in case.
# Actually, they are set inside the try block, but accessed later. 
# So I will inject their initialization right before the `try` block for search:

init_vars = """    symbol, short_name, exchange = None, None, None
    sector_val, industry_val = "N/A", "N/A"
    try:"""

text = text.replace("    symbol, short_name, exchange = None, None, None\n    try:", init_vars)
text = text.replace(old_profile, new_profile)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(text)

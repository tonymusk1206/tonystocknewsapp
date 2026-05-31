import re

with open("app.py", "r", encoding="utf-8") as f:
    text = f.read()

# 1. Modify the return structure and naver links
old_return = """    # 4. 네이버 링크 생성
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
    })"""

new_return = """    # 4. 토론방 링크 생성 및 기업 정보 가져오기
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
        print(f"[Search] Info fetch failed: {e}")

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
    })"""

text = text.replace(old_return, new_return)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(text)

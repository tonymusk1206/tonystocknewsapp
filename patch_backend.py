import re

with open("app.py", "r", encoding="utf-8") as f:
    text = f.read()

# I will add the fetching code before creating company_profile
# The old company_profile code:
old_company_profile = """        company_profile = {
            "marketCap": mc_str,
            "sector": sector_ko,
            "industry": industry_ko,
            "summary": summary_ko
        }"""

new_company_profile = """        # 관련 기업 가져오기 (Naver API)
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
        }"""

text = text.replace(old_company_profile, new_company_profile)

# Next, add EPS fetching logic after `company_profile = {}` block ends
# Right after:
#    except Exception as e:
#        print(f"[Search] Info fetch failed: {e}")
old_info_fetch_end = """    except Exception as e:
        print(f"[Search] Info fetch failed: {e}")"""

new_eps_logic = """    except Exception as e:
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
        print(f"[Search] Earnings fetch failed: {e}")"""

text = text.replace(old_info_fetch_end, new_eps_logic)

# Finally, return earnings_list in the JSON
old_return = """        return jsonify({
            "symbol": symbol,
            "name": short_name,
            "exchange": exchange,
            "current": current_price,
            "changes": changes,
            "news": news_items,
            "links": {
                "naver": naver_url,
                "naver_board": naver_board_url,
                "toss": toss_url
            },
            "profile": company_profile
        })"""

new_return = """        return jsonify({
            "symbol": symbol,
            "name": short_name,
            "exchange": exchange,
            "current": current_price,
            "changes": changes,
            "news": news_items,
            "links": {
                "naver": naver_url,
                "naver_board": naver_board_url,
                "toss": toss_url
            },
            "profile": company_profile,
            "earnings": earnings_list
        })"""

text = text.replace(old_return, new_return)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(text)

import re

# 1. Update app.py
with open("app.py", "r", encoding="utf-8") as f:
    text = f.read()

# Replace get_past_price with get_past_data and update safe_pct
old_get_past_price = """        def get_past_price(days_ago):
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
        }"""

new_get_past_price = """        def get_past_data(days_ago):
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
        }"""

text = text.replace(old_get_past_price, new_get_past_price)

# Add dates to the API response
old_return = """        return jsonify({
            "name": short_name,
            "symbol": symbol,
            "exchange": exchange,
            "current": current_price,
            "changes": changes,"""

new_return = """        return jsonify({
            "name": short_name,
            "symbol": symbol,
            "exchange": exchange,
            "current": current_price,
            "changes": changes,
            "dates": {
                "current": hist.index[-1].strftime('%y.%m.%d'),
                "d1": changes["d1"]["date"],
                "d3": changes["d3"]["date"],
                "w1": changes["w1"]["date"],
                "m1": changes["m1"]["date"],
                "m3": changes["m3"]["date"],
                "m6": changes["m6"]["date"],
                "y1": changes["y1"]["date"]
            },"""

text = text.replace(old_return, new_return)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(text)


# 2. Update js/components.js
with open("js/components.js", "r", encoding="utf-8") as f:
    comp = f.read()

# Update formatPercent
comp = comp.replace("function formatPercent(data) {", "function formatPercent(data, hidePrice = false) {")
comp = comp.replace("if (price && price !== 'N/A') {", "if (!hidePrice && price && price !== 'N/A') {")

# Update createSectorTableHTML
old_sector_table_th = """        <thead>
            <tr style="border-bottom: 1px solid rgba(255,255,255,0.1); color: var(--text-muted); font-size: 0.85em;">
                <th>자산 (ETF)</th>
                <th>현재가</th>
                <th>1일전比</th>
                <th>3일전比</th>
                <th>1주전比</th>
                <th>1달전比</th>
                <th>3달전比</th>
                <th>6달전比</th>
                <th>1년전比</th>
            </tr>
        </thead>"""

new_sector_table_th = """        <thead style="text-align: center;">
            <tr style="border-bottom: 1px solid rgba(255,255,255,0.1); color: var(--text-muted); font-size: 0.85em;">
                <th style="text-align: left;">자산 (ETF)</th>
                <th>현재가<br/><span style="font-size:0.8em;font-weight:normal;color:#94a3b8;">(${mockData.dates.current})</span></th>
                <th>1일전比<br/><span style="font-size:0.8em;font-weight:normal;color:#94a3b8;">(${mockData.dates.d1})</span></th>
                <th>3일전比<br/><span style="font-size:0.8em;font-weight:normal;color:#94a3b8;">(${mockData.dates.d3})</span></th>
                <th>1주전比<br/><span style="font-size:0.8em;font-weight:normal;color:#94a3b8;">(${mockData.dates.w1})</span></th>
                <th>1달전比<br/><span style="font-size:0.8em;font-weight:normal;color:#94a3b8;">(${mockData.dates.m1})</span></th>
                <th>3달전比<br/><span style="font-size:0.8em;font-weight:normal;color:#94a3b8;">(${mockData.dates.m3})</span></th>
                <th>6달전比<br/><span style="font-size:0.8em;font-weight:normal;color:#94a3b8;">(${mockData.dates.m6})</span></th>
                <th>1년전比<br/><span style="font-size:0.8em;font-weight:normal;color:#94a3b8;">(${mockData.dates.y1})</span></th>
            </tr>
        </thead>"""
comp = comp.replace(old_sector_table_th, new_sector_table_th)

comp = comp.replace("<td>${formatPercent(sector.changes.today)}</td>", "<td>${formatPercent(sector.changes.today, true)}</td>")
comp = comp.replace("""            <td style="font-weight: 600;">
                <div style="font-size: 1rem; margin-bottom: 4px;">${sector.value}</div>
                <div style="font-weight: 500;">${formatPercent(sector.changes.today)}</div>
            </td>""", """            <td style="font-weight: 600;">
                <div style="font-size: 1rem; margin-bottom: 4px;">${sector.value}</div>
                <div style="font-weight: 500;">${formatPercent(sector.changes.today, true)}</div>
            </td>""")

# Update createMarketCard
old_market_price = """            <div class="market-price-area">
                <span class="m-price">${market.value}</span>
                <span class="m-change ${getPercentClass(market.changes.today)}">${market.changes.today.pct > 0 ? '+' : ''}${market.changes.today.pct}%</span>
            </div>"""

new_market_price = """            <div class="market-price-area">
                <div style="display: flex; flex-direction: column;">
                    <span class="m-price">${market.value}</span>
                    <span style="font-size: 0.75rem; color: #94a3b8; margin-top: 2px;">현재가 (${mockData.dates.current})</span>
                </div>
                <span class="m-change ${getPercentClass(market.changes.today)}">${market.changes.today.pct > 0 ? '+' : ''}${market.changes.today.pct}%</span>
            </div>"""
comp = comp.replace(old_market_price, new_market_price)

old_market_metric = """    const renderMetric = (label, date, change) => `
        <div class="metric-box">
            <span class="metric-label">${label}</span>
            <span class="metric-value ${getPercentClass(change)}">${change.pct > 0 ? '+' : ''}${change.pct}%</span>
            <span class="metric-hist-price">${change.price}</span>
        </div>
    `;"""

new_market_metric = """    const renderMetric = (label, date, change) => `
        <div class="metric-box">
            <span class="metric-label">${label}<br/><span style="font-size: 0.85em; font-weight: normal; color: #94a3b8;">(${date})</span></span>
            <span class="metric-value ${getPercentClass(change)}">${change.pct > 0 ? '+' : ''}${change.pct}%</span>
            <span class="metric-hist-price">${change.price}</span>
        </div>
    `;"""
comp = comp.replace(old_market_metric, new_market_metric)

with open("js/components.js", "w", encoding="utf-8") as f:
    f.write(comp)


# 3. Update js/app.js search card
with open("js/app.js", "r", encoding="utf-8") as f:
    app_js = f.read()

old_search_box = """    const box = (label, sub, change) => `
        <div style="background:rgba(255,255,255,0.05);border-radius:10px;padding:14px 16px;min-width:110px;">
            <div style="font-size:0.75rem;color:#94a3b8;margin-bottom:6px;">${label}<br/><span style="font-size:0.7rem;">${sub}</span></div>
            ${pct(change)}
        </div>`;"""

new_search_box = """    const box = (label, sub, change) => `
        <div style="background:rgba(255,255,255,0.05);border-radius:10px;padding:14px 16px;min-width:110px;text-align:center;">
            <div style="font-size:0.8rem;color:#e2e8f0;font-weight:600;margin-bottom:6px;">${label}<br/><span style="font-size:0.75rem;font-weight:normal;color:#94a3b8;">(${sub})</span></div>
            ${pct(change)}
        </div>`;"""
app_js = app_js.replace(old_search_box, new_search_box)

old_search_render = """        <div style="margin-bottom:20px;">
            <div style="font-size:2rem;font-weight:800;letter-spacing:-1px;">${data.price}</div>
            <div style="font-size:1.1rem;font-weight:600;margin-top:4px;" class="${data.changes.today.pct > 0 ? 'text-up' : (data.changes.today.pct < 0 ? 'text-down' : '')}">
                ${data.changes.today.pct > 0 ? '▲' : (data.changes.today.pct < 0 ? '▼' : '')} ${Math.abs(data.changes.today.pct)}% (1일전比)
            </div>
        </div>

        <div style="display:flex;gap:10px;overflow-x:auto;padding-bottom:10px;" class="hide-scroll">
            ${box('3일전', '3D', data.changes.d3)}
            ${box('1주전', '1W', data.changes.w1)}
            ${box('1달전', '1M', data.changes.m1)}
            ${box('3달전', '3M', data.changes.m3)}
            ${box('6달전', '6M', data.changes.m6)}
            ${box('1년전', '1Y', data.changes.y1)}
        </div>"""

new_search_render = """        <div style="margin-bottom:20px;">
            <div style="font-size:2rem;font-weight:800;letter-spacing:-1px;">${data.price}</div>
            <div style="font-size:0.8rem; color:#94a3b8; margin-top:2px;">현재가 (${data.dates ? data.dates.current : '오늘'})</div>
            <div style="font-size:1.1rem;font-weight:600;margin-top:4px;" class="${data.changes.today.pct > 0 ? 'text-up' : (data.changes.today.pct < 0 ? 'text-down' : '')}">
                ${data.changes.today.pct > 0 ? '▲' : (data.changes.today.pct < 0 ? '▼' : '')} ${Math.abs(data.changes.today.pct)}% (1일전比)
            </div>
        </div>

        <div style="display:flex;gap:10px;overflow-x:auto;padding-bottom:10px;" class="hide-scroll">
            ${box('3일전比', data.dates ? data.dates.d3 : '3D', data.changes.d3)}
            ${box('1주전比', data.dates ? data.dates.w1 : '1W', data.changes.w1)}
            ${box('1달전比', data.dates ? data.dates.m1 : '1M', data.changes.m1)}
            ${box('3달전比', data.dates ? data.dates.m3 : '3M', data.changes.m3)}
            ${box('6달전比', data.dates ? data.dates.m6 : '6M', data.changes.m6)}
            ${box('1년전比', data.dates ? data.dates.y1 : '1Y', data.changes.y1)}
        </div>"""
app_js = app_js.replace(old_search_render, new_search_render)

# For search component, we need to pass hidePrice=true if we want to remove the historical price from box?
# Let's check `pct` definition in js/app.js
old_pct_func = """    const pct = c => {
        if (!c || c.pct === undefined) return '<div style="color:#94a3b8;">-</div>';
        const v = c.pct;
        const color = v > 0 ? '#22c55e' : (v < 0 ? '#f87171' : '#e2e8f0');
        const sign = v > 0 ? '+' : '';
        return `
            <div style="color:${color};font-weight:700;font-size:1.1rem;margin-bottom:2px;">${sign}${v}%</div>
            <div style="color:#94a3b8;font-size:0.8rem;">${c.price}</div>
        `;
    };"""

new_pct_func = """    const pct = c => {
        if (!c || c.pct === undefined) return '<div style="color:#94a3b8;">-</div>';
        const v = c.pct;
        const color = v > 0 ? '#22c55e' : (v < 0 ? '#f87171' : '#e2e8f0');
        const sign = v > 0 ? '+' : '';
        return `
            <div style="color:${color};font-weight:700;font-size:1.1rem;margin-bottom:2px;">${sign}${v}%</div>
            <div style="color:#94a3b8;font-size:0.8rem;">${c.price}</div>
        `;
    };"""
# Nothing to change here, historical price in search is fine, or do they want to remove it there too?
# User said: "그리고 서치에서 값을 나타낼때도 똑같이 나타내도록 해줘". So search should have dates. The historical prices in search are actually useful. If they want it removed, I will remove it. Let's keep it for now.

with open("js/app.js", "w", encoding="utf-8") as f:
    f.write(app_js)

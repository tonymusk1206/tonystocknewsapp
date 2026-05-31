import urllib.request, re, json
def test():
    url = "https://www.google.com/finance/quote/AAPL:NASDAQ"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    resp = urllib.request.urlopen(req)
    html = resp.read().decode('utf-8')
    match = re.search(r'<div class="bPIre">(.*?)</div>', html)
    if match: print("Summary:", match.group(1))
    else: print("No summary")

test()

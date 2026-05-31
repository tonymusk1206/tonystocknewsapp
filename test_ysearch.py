import urllib.request, json, urllib.parse

def test():
    url = f"https://query2.finance.yahoo.com/v1/finance/search?q={urllib.parse.quote('TSLA')}&quotesCount=1"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    resp = urllib.request.urlopen(req)
    data = json.loads(resp.read().decode('utf-8'))
    quote = data.get('quotes', [{}])[0]
    print(quote.keys())
    print('Industry:', quote.get('industry'))
    print('Sector:', quote.get('sector'))

test()

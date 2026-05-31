import xml.etree.ElementTree as ET

with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip = False
for i, line in enumerate(lines):
    if line.startswith('def get_youtube_insights():'):
        new_lines.append('import xml.etree.ElementTree as ET\n\ndef get_youtube_insights():\n')
        skip = True
        continue
    
    if skip and 'def get_dynamic_quotes():' in line:
        skip = False
        new_body = """    channels = [
        {"name": "슈카월드", "id": "UCsJ6RuBiTVWRX156FVbeaGg"},
        {"name": "월가아재의과학적투자", "id": "UCpqD9_OJNtF6suPpi6mOQCQ"},
        {"name": "박종훈지식한방", "id": "UCOB62fKRT7b73X7tRxMuN2g"},
        {"name": "소수몽키", "id": "UCC3yfxS5qC6PCwDzetUuEWg"},
        {"name": "전인구경제연구소", "id": "UCznImSIaxZR7fdLCICLdgaQ"},
        {"name": "수페TV", "id": "UCfnqgWlC5IvJEAPTmyjaixA"},
        {"name": "이효석아카데미", "id": "UCxvdCnvGODDyuvnELnLkQWw"}
    ]
    
    def fetch_channel(ch):
        url = f"https://www.youtube.com/feeds/videos.xml?channel_id={ch['id']}"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as resp:
                xml_data = resp.read()
                root = ET.fromstring(xml_data)
                ns = {'yt': 'http://www.youtube.com/xml/schemas/2015', 'atom': 'http://www.w3.org/2005/Atom'}
                entry = root.find('atom:entry', ns)
                if entry is not None:
                    title = entry.find('atom:title', ns).text
                    link = entry.find('atom:link', ns).attrib['href']
                    published = entry.find('atom:published', ns).text
                    pub_date = published.split('T')[0].replace('-', '.')
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

"""
        new_lines.append(new_body)
    
    if not skip:
        new_lines.append(line)

with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

import re

with open("app.py", "r", encoding="utf-8") as f:
    text = f.read()

old_func = """    def fetch_channel(ch):
        url = f"https://www.youtube.com/feeds/videos.xml?channel_id={ch['id']}"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as resp:
                root = ET.fromstring(resp.read().strip())
            entry = root.find('{http://www.w3.org/2005/Atom}entry')
            if entry is not None:
                raw_title = entry.findtext('{http://www.w3.org/2005/Atom}title', '')
                vid = entry.findtext('{http://www.youtube.com/xml/schemas/2015}videoId', '')
                pub_date = entry.findtext('{http://www.w3.org/2005/Atom}published', '')
                
                clean_title = raw_title
                if pub_date:
                    try:
                        dt = datetime.strptime(pub_date[:19], "%Y-%m-%dT%H:%M:%S")
                        date_str = dt.strftime("%Y.%m.%d")
                    except:
                        date_str = base_dt_now
                else:
                    date_str = base_dt_now
                    
                link_href = f"https://www.youtube.com/watch?v={vid}"
                return {"title": clean_title, "channel": ch['name'], "date": date_str, "link": link_href}
        except Exception:
            pass
        return {"title": f"[{ch['name']}] 최신 영상 로드 실패", "channel": ch['name'], "date": base_dt_now, "link": f"https://www.youtube.com/channel/{ch['id']}"}"""

new_func = """    def fetch_channel(ch):
        # Render에서 YouTube RSS가 429 에러로 막히는 문제를 우회하기 위해 DecAPI 사용
        url = f"https://decapi.me/youtube/latest_video?id={ch['id']}"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as resp:
                result = resp.read().decode('utf-8').strip()
                # 결과 형식: "제목 - https://youtu.be/..."
                if " - https://youtu.be/" in result:
                    parts = result.rsplit(" - https://youtu.be/", 1)
                    title = parts[0].strip()
                    link_href = "https://youtu.be/" + parts[1].strip()
                    return {"title": title, "channel": ch['name'], "date": base_dt_now, "link": link_href}
                elif " - https://youtube.com/watch?v=" in result:
                    parts = result.rsplit(" - https://youtube.com/watch?v=", 1)
                    title = parts[0].strip()
                    link_href = "https://youtube.com/watch?v=" + parts[1].strip()
                    return {"title": title, "channel": ch['name'], "date": base_dt_now, "link": link_href}
        except Exception:
            pass
        return {"title": f"[{ch['name']}] 최신 영상 로드 실패", "channel": ch['name'], "date": base_dt_now, "link": f"https://www.youtube.com/channel/{ch['id']}"}"""

text = text.replace(old_func, new_func)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(text)

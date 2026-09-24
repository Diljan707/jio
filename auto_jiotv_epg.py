import urllib.request
import json
import datetime

def generate_automated_epg():
    print("🚀 ਆਟੋਮੈਟਿਕ JioTV EPG ਅਤੇ ਚੈਨਲ ਜਨਰੇਟਰ ਸ਼ੁਰੂ ਹੋ ਗਿਆ ਹੈ...")
    
    url = "https://jiotv.com/"
    
    # ਇੱਥੇ ਹੈਡਰਸ ਨੂੰ ਹੋਰ ਬਿਹਤਰ ਬਣਾਇਆ ਗਿਆ ਹੈ
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://jiotv.com/"
    }
    
    try:
        print("📡 ਜਿਓਟੀਵੀ ਸਰਵਰ ਤੋਂ ਲੇਟਸਟ ਡਾਟਾ ਲਿਆ ਜਾ ਰਿਹਾ ਹੈ...")
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            
            marker = '<script id="__NEXT_DATA__" type="application/json">'
            start_idx = html.find(marker)
            if start_idx == -1:
                print("❌ ਗਲਤੀ: ਵੈੱਬਸਾਈਟ ਤੋਂ ਡਾਟਾ ਨਹੀਂ ਮਿਲ ਸਕਿਆ।")
                return
                
            start_idx += len(marker)
            end_idx = html.find('</script>', start_idx)
            json_str = html[start_idx:end_idx]
            data = json.loads(json_str)
            
            page_data = data.get("props", {}).get("pageProps", {}).get("pageData", {})
            featured = page_data.get("featuredNewData", [])
            
            channels_dict = {}
            programmes_list = []
            
            for cat in featured:
                items = cat.get("data", [])
                for item in items:
                    ch_id = str(item.get("channel_id", item.get("id", "")))
                    ch_name = item.get("channel_name", item.get("name", ""))
                    
                    if ch_id and ch_name:
                        if ch_id not in channels_dict:
                            channels_dict[ch_id] = ch_name
                        
                        shows = item.get("shows", item.get("programmeList", []))
                        for show in shows:
                            show_title = show.get("name", show.get("title", "Live Broadcast"))
                            show_desc = show.get("description", show.get("desc", ""))
                            start_time = show.get("startEpoch", show.get("startTime"))
                            end_time = show.get("endEpoch", show.get("endTime"))
                            
                            if start_time and end_time:
                                programmes_list.append({
                                    "ch_id": ch_id,
                                    "title": show_title,
                                    "desc": show_desc,
                                    "start": start_time,
                                    "end": end_time
                                })
            
            print(f"📊 ਕੁੱਲ {len(channels_dict)} ਵਿਲੱਖਣ ਚੈਨਲ ਅਤੇ {len(programmes_list)} ਪ੍ਰੋਗਰਾਮ ਮਿਲ ਗਏ ਹਨ।")
            
            xml_data = '<?xml version="1.0" encoding="UTF-8"?>\n<tv generator-info-name="DiljanCustomAutoEPG">\n'
            
            for ch_id, ch_name in channels_dict.items():
                safe_name = ch_name.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                xml_data += f'  <channel id="{ch_id}">\n'
                xml_data += f'    <display-name lang="en">{safe_name}</display-name>\n'
                xml_data += f'  </channel>\n'
            
            for prog in programmes_list:
                try:
                    s_val = int(prog["start"])
                    e_val = int(prog["end"])
                    if s_val > 10000000000: s_val //= 1000
                    if e_val > 10000000000: e_val //= 1000
                    
                    start_dt = datetime.datetime.fromtimestamp(s_val)
                    end_dt = datetime.datetime.fromtimestamp(e_val)
                    
                    start_str = start_dt.strftime('%Y%m%d%H%M%S +0530')
                    end_str = end_dt.strftime('%Y%m%d%H%M%S +0530')
                    
                    title = prog["title"].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                    desc = prog["desc"].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                    
                    xml_data += f'  <programme start="{start_str}" stop="{end_str}" channel="{prog["ch_id"]}">\n'
                    xml_data += f'    <title lang="en">{title}</title>\n'
                    if desc:
                        xml_data += f'    <desc lang="en">{desc}</desc>\n'
                    xml_data += f'  </programme>\n'
                except:
                    pass
            
            xml_data += '</tv>'
            
            filename = "jiotv_auto_epg.xml"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(xml_data)
                
            print(f"✅ ਸਫਲਤਾ! EPG ਫ਼ਾਈਲ ਤਿਆਰ ਹੋ ਗਈ ਹੈ: {filename}")
            
    except Exception as e:
        print(f"❌ ਗਲਤੀ ਆਈ: {e}")

if __name__ == "__main__":
    generate_automated_epg()

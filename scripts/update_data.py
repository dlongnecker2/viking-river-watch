#!/usr/bin/env python3
import json, re, html
from datetime import datetime, timezone
from urllib.request import Request, urlopen

UA = {"User-Agent":"Mozilla/5.0 VikingRiverWatch/1.0"}

def get_text(url):
    req = Request(url, headers=UA)
    with urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", errors="replace")

def get_json(url):
    return json.loads(get_text(url))

def find_station(stations, name):
    name_l = name.lower()
    for s in stations:
        if s.get("longname","").lower() == name_l or s.get("shortname","").lower() == name_l:
            return s
    for s in stations:
        if name_l in s.get("longname","").lower() or name_l in s.get("shortname","").lower():
            return s
    return None

def current_w(station):
    if not station:
        return None
    for ts in station.get("timeseries", []):
        if ts.get("shortname") == "W":
            cm = ts.get("currentMeasurement") or {}
            return {
                "value_cm": cm.get("value"),
                "timestamp": cm.get("timestamp"),
                "station": station.get("longname") or station.get("shortname")
            }
    return None

def pegelonline():
    url = "https://www.pegelonline.wsv.de/webservices/rest-api/v2/stations.json?waters=RHEIN,MAIN,DONAU&includeTimeseries=true&includeCurrentMeasurement=true"
    stations = get_json(url)
    out = {}
    for key, name in [("kaub","KAUB"),("wuerzburg","WUERZBURG"),("pfelling","PFELLING")]:
        out[key] = current_w(find_station(stations, name))
    return out

def viadonau():
    text = get_text("https://www.viadonau.org/fileadmin/doris_iframe/OnePageInfo_en.html")
    plain = re.sub(r"<[^>]+>", " ", text)
    plain = html.unescape(re.sub(r"\s+", " ", plain))
    names = ["Achleiten","Kienstock","Wildungsmauer"]
    out = {}
    for n in names:
        m = re.search(rf"{n}\s+(-?\d+)\s+\((-?\d+)\)", plain, re.I)
        if m:
            out[n.lower()] = {"value_cm": float(m.group(1)), "hour_change_cm": float(m.group(2))}
    tm = re.search(r"(\d{1,2}/\d{1,2}/\d{4})\s+(\d{1,2}:\d{2}\s*[AP]M)", plain, re.I)
    if tm:
        out["source_time"] = tm.group(1)+" "+tm.group(2)
    return out

def viking():
    url = "https://www.vikingrivercruises.com/my-trip/current-sailings/index.html"
    raw = get_text(url)
    text = html.unescape(re.sub(r"<[^>]+>", " ", raw))
    text = re.sub(r"\s+", " ", text)
    m = re.search(r"Danube, Elbe & Rhine Rivers\s*[–-]\s*([A-Za-z]+\s+\d{1,2},\s+\d{4})(.*?)(?:For Further Assistance|$)", text, re.I)
    if not m:
        return {"checked": True, "notice_date": None, "summary": "Official Viking current-sailings page checked; no Rhine/Danube advisory section was parsed."}
    body = m.group(2)
    body = body[:1800].strip()
    return {
        "checked": True,
        "notice_date": m.group(1),
        "summary": body
    }

data = {
    "updated_utc": datetime.now(timezone.utc).isoformat().replace("+00:00","Z"),
    "sources": {
        "pegelonline": "https://www.pegelonline.wsv.de/",
        "viadonau": "https://www.viadonau.org/en/economy/services-transport-planning/water-levels",
        "viking": "https://www.vikingrivercruises.com/my-trip/current-sailings/index.html"
    }
}

errors = []
try:
    data["germany"] = pegelonline()
except Exception as e:
    errors.append("PEGELONLINE: "+repr(e))
    data["germany"] = {}

try:
    data["austria"] = viadonau()
except Exception as e:
    errors.append("viadonau: "+repr(e))
    data["austria"] = {}

try:
    data["viking"] = viking()
except Exception as e:
    errors.append("Viking: "+repr(e))
    data["viking"] = {"checked": False}

data["errors"] = errors

with open("data.json","w",encoding="utf-8") as f:
    json.dump(data,f,indent=2,ensure_ascii=False)
    f.write("\n")

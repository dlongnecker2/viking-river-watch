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

def shipfinder():
    url = "https://www.shipfinder.com/vessels/details/269057517"
    raw = get_text(url)
    text = html.unescape(re.sub(r"<[^>]+>", " ", raw))
    text = re.sub(r"\s+", " ", text)

    out = {"checked": True, "source": url, "mmsi": "269057517"}

    # ShipFinder commonly renders coordinates like:
    # Lat: 48-30.156N   Lon: 13-44.166E
    m = re.search(r"Lat:\s*(\d+)[-°](\d+(?:\.\d+)?)\s*([NS]).*?Lon:\s*(\d+)[-°](\d+(?:\.\d+)?)\s*([EW])", text, re.I)
    if m:
        lat = float(m.group(1)) + float(m.group(2))/60.0
        lon = float(m.group(4)) + float(m.group(5))/60.0
        if m.group(3).upper() == "S": lat = -lat
        if m.group(6).upper() == "W": lon = -lon
        out["latitude"] = lat
        out["longitude"] = lon

    m = re.search(r"Dest:\s*([A-Z0-9_-]+)", text, re.I)
    if m:
        out["destination"] = m.group(1).strip()

    m = re.search(r"Status:\s*([^|]+?)(?:Length:|Width:|Draught:|$)", text, re.I)
    if m:
        out["status"] = m.group(1).strip()

    m = re.search(r"Speed:\s*([0-9.]+)\s*kn", text, re.I)
    if m:
        out["speed_kn"] = float(m.group(1))

    m = re.search(r"Course:\s*([0-9.]+)\s*Deg", text, re.I)
    if m:
        out["course_deg"] = float(m.group(1))

    m = re.search(r"Last Update:\s*(20\d{2}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})", text, re.I)
    if m:
        out["position_time"] = m.group(1)

    return out

def shipradar():
    url = "https://marinetraffic.live/en/vessels/viking-ve-position/269057517/"
    raw = get_text(url)
    text = html.unescape(re.sub(r"<[^>]+>", " ", raw))
    text = re.sub(r"\s+", " ", text)

    out = {"checked": True, "source": url, "mmsi": "269057517"}

    # Position appears as e.g. "Position 48.32965°, 16.33016°"
    m = re.search(r"Position\s+(-?\d+(?:\.\d+)?)\s*°?\s*[,/]\s*(-?\d+(?:\.\d+)?)\s*°?", text, re.I)
    if m:
        out["latitude"] = float(m.group(1))
        out["longitude"] = float(m.group(2))

    m = re.search(r"Status\s+([A-Za-z ]+?)(?:Last ports|Letzte Häfen|Departure|Arrival|MMSI|$)", text, re.I)
    if m:
        out["status"] = m.group(1).strip()

    m = re.search(r"(?:Speed|Tempo)\s+([0-9.]+)\s*(?:kn|knots?)", text, re.I)
    if m:
        out["speed_kn"] = float(m.group(1))

    m = re.search(r"(?:Course|Courses|Kurs)\s+([0-9.]+)\s*°", text, re.I)
    if m:
        out["course_deg"] = float(m.group(1))

    m = re.search(r"(?:last update|Letzte Aktualisierung)\s+(?:[^\d]{0,30})?(20\d{2}-\d{2}-\d{2}\s+\d{1,2}:\d{2})", text, re.I)
    if m:
        out["position_time"] = m.group(1)

    return out

def vesselfinder():
    url = "https://www.vesselfinder.com/vessels/details/269057517"
    raw = get_text(url)
    text = html.unescape(re.sub(r"<[^>]+>", " ", raw))
    text = re.sub(r"\s+", " ", text)

    out = {"checked": True, "source": url, "mmsi": "269057517"}

    m = re.search(r"current position of VIKING VE is at ([^.]+?) reported ([^.]+?) by AIS", text, re.I)
    if m:
        out["area"] = m.group(1).strip()
        out["reported_ago"] = m.group(2).strip()

    m = re.search(r"vessel is en route to ([A-Z0-9_-]+)", text, re.I)
    if m:
        out["destination"] = m.group(1).strip()

    m = re.search(r"Navigation Status\s+([A-Za-z ]+?)\s+Position Received", text, re.I)
    if m:
        out["status"] = m.group(1).strip()

    m = re.search(r"Current draught\s+([0-9.]+\s*m)", text, re.I)
    if m:
        out["draught"] = m.group(1).strip()

    m = re.search(r"Last Port\s+([^\n]+?)\s+ATD:", text, re.I)
    if m:
        out["last_port"] = m.group(1).strip()

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

try:
    ship = vesselfinder()
except Exception as e:
    errors.append("VesselFinder: "+repr(e))
    ship = {"checked": False, "mmsi": "269057517"}

try:
    sf = shipfinder()
    for k, v in sf.items():
        if v is not None and k not in ("checked",):
            ship[k] = v
    ship["checked"] = True
except Exception as e:
    errors.append("ShipFinder: "+repr(e))

try:
    radar = shipradar()
    for k, v in radar.items():
        if v is not None and k not in ("checked","latitude","longitude","position_time"):
            ship[k] = v
    ship["checked"] = True
except Exception as e:
    errors.append("ShipRadar: "+repr(e))

data["ship"] = ship

data["errors"] = errors

with open("data.json","w",encoding="utf-8") as f:
    json.dump(data,f,indent=2,ensure_ascii=False)
    f.write("\n")

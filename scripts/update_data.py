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
    if not any(v and v.get("value_cm") is not None for v in out.values()):
        raise ValueError("No German gauge readings returned")
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
    if not any(out.get(n, {}).get("value_cm") is not None for n in names if isinstance(out.get(n.lower()), dict)):
        if not any(isinstance(out.get(n.lower()), dict) for n in names):
            raise ValueError("No Austrian gauge readings parsed")
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


def egdir_position():
    """Try dated public AIS; retain the last verified observation, never invent a live fix."""
    mmsi = "269057766"
    url = "https://aisvesseltracker.com/vessel/viking-egdir-mmsi-269057766-imo-0"
    fallback = {
        "checked": False, "mmsi": mmsi, "latitude": 50.954150,
        "longitude": 6.972260, "position_time": "2026-10-30T13:44:00Z",
        "coordinate_quality": "historical_manually_verified",
        "coordinate_source": "AIS Vessel Tracker, October 30 observation",
        "coordinate_note": "Last verified observation; not a live AIS position.",
        "source": url
    }
    try:
        raw = get_text(url)
        plain = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", raw)))
        if "VIKING EGDIR" not in plain.upper():
            return fallback
        match = re.search(r"Latitude\s+(-?\d{1,2}\.\d+)\s+Longitude\s+(-?\d{1,3}\.\d+)", plain, re.I)
        stamp = re.search(r"Last Update\s*\(UTC\)\s*(\d{1,2} [A-Za-z]{3} 20\d{2}, \d{2}:\d{2} UTC)", plain, re.I)
        if match and stamp:
            lat, lon = float(match.group(1)), float(match.group(2))
            observed = datetime.strptime(stamp.group(1), "%d %b %Y, %H:%M UTC").replace(tzinfo=timezone.utc)
            if 45 <= lat <= 55 and 3 <= lon <= 20 and observed <= datetime.now(timezone.utc):
                return {
                    "checked": True, "mmsi": mmsi, "latitude": lat, "longitude": lon,
                    "position_time": observed.isoformat().replace("+00:00", "Z"),
                    "coordinate_quality": "live_machine_readable",
                    "coordinate_source": "AIS Vessel Tracker", "source": url
                }
    except Exception:
        pass
    return fallback

# AIS positions are accepted only with vessel identity, coordinates and a dated observation.
# A successful website request is NOT evidence of a new AIS report.
def parse_utc(value):
    if not value:
        return None
    value = value.strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%SZ", "%b %d, %Y %H:%M UTC", "%d %b %Y, %H:%M UTC"):
        try:
            return datetime.strptime(value, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            pass
    return None

def ais_shipfinder(mmsi, name):
    url = "https://www.shipfinder.com/ship/detail/mmsi/" + mmsi
    raw = get_text(url)
    plain = re.sub(r"\\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", raw)))
    if name.upper() not in plain.upper() or mmsi not in plain:
        raise ValueError("ShipFinder vessel identity mismatch")
    # ShipFinder displays degrees and decimal minutes, not decimal degrees.
    match = re.search(r"(\\d{1,2})-(\\d{1,2}\\.\\d+)\\s*([NS])\\s*[,;/ ]+\\s*(\\d{1,3})-(\\d{1,2}\\.\\d+)\\s*([EW])", plain, re.I)
    if not match:
        match = re.search(r"Lat\\s*:?\\s*(\\d{1,2})[-°](\\d{1,2}\\.\\d+)\\s*([NS]).{0,90}?Lon\\s*:?\\s*(\\d{1,3})[-°](\\d{1,2}\\.\\d+)\\s*([EW])", plain, re.I)
    stamp = re.search(r"(?:reported at|Last Update\\s*:?)\\s*(20\\d{2}-\\d{2}-\\d{2}\\s+\\d{2}:\\d{2}:\\d{2})", plain, re.I)
    if not match or not stamp:
        raise ValueError("ShipFinder did not expose timestamped coordinates")
    lat = (int(match[1]) + float(match[2])/60) * (-1 if match[3].upper()=="S" else 1)
    lon = (int(match[4]) + float(match[5])/60) * (-1 if match[6].upper()=="W" else 1)
    observed = parse_utc(stamp[1])
    return make_ais_position(mmsi, lat, lon, observed, url, "ShipFinder (timestamp treated as UTC)")

def ais_trackipi(mmsi, name):
    url = "https://www.trackipi.com/et/vessel/mmsi-" + mmsi + "/"
    raw = get_text(url)
    plain = re.sub(r"\\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", raw)))
    if name.upper() not in plain.upper() or mmsi not in plain:
        raise ValueError("Trackipi vessel identity mismatch")
    match = re.search(r"(?:Latitud|Latitude|Laiuskraad)\\s*(-?\\d{1,2}\\.\\d+)\\s*[,; ]+\\s*(?:Longitud|Longitude|Pikkuskraad)\\s*(-?\\d{1,3}\\.\\d+)", plain, re.I)
    # Trackipi's prose can put labels between coordinates and timestamp.
    if not match:
        match = re.search(r"\\(\\s*(?:Latitud|Latitude|Laiuskraad)\\s*(-?\\d{1,2}\\.\\d+)\\s*[,;]\\s*(?:Longitud|Longitude|Pikkuskraad)\\s*(-?\\d{1,3}\\.\\d+)\\s*\\)", plain, re.I)
    stamp = re.search(r"(?:Position report|Positsiooniaruanne|Laporan Kedudukan)\\s*(?:Oct|okt)\\s*(\\d{1,2}),?\\s*(2026)\\s*(\\d{2}:\\d{2})\\s*UTC", plain, re.I)
    if not match or not stamp:
        raise ValueError("Trackipi did not expose timestamped coordinates")
    observed = parse_utc(stamp[2]+"-10-"+stamp[1].zfill(2)+" "+stamp[3]+":00")
    return make_ais_position(mmsi, float(match[1]), float(match[2]), observed, url, "Trackipi UTC report")

def make_ais_position(mmsi, lat, lon, observed, source, label):
    now=datetime.now(timezone.utc)
    if observed is None or observed > now + __import__("datetime").timedelta(minutes=15) or observed < now - __import__("datetime").timedelta(days=30):
        raise ValueError("AIS observation timestamp invalid or older than 30 days")
    if not (45 <= lat <= 55 and 3 <= lon <= 20):
        raise ValueError("AIS coordinates outside expected European river region")
    age=(now-observed).total_seconds()/3600
    return {"checked":True,"mmsi":mmsi,"latitude":round(lat,6),"longitude":round(lon,6),
            "position_time":observed.isoformat().replace("+00:00","Z"),
            "coordinate_quality":"live_machine_readable" if age<=6 else "historical_timestamped",
            "coordinate_source":label,"coordinate_note":"AIS report age %.1f hours; not continuous GPS."%max(age,0),
            "source":source,"age_hours":round(max(age,0),1)}

def ais_aprs(mmsi, name):
    url="https://aprs.fi/info/i/"+mmsi
    raw=get_text(url)
    plain=re.sub(r"\\s+"," ",html.unescape(re.sub(r"<[^>]+>"," ",raw)))
    if mmsi not in plain or name.upper() not in plain.upper():
        raise ValueError("APRS vessel identity mismatch")
    match=re.search(r"(\\d{1,2})°\\s*(\\d{1,2}\\.\\d+)['’]?\\s*([NS])\\s+(\\d{1,3})°\\s*(\\d{1,2}\\.\\d+)['’]?\\s*([EW])",plain,re.I)
    stamp=re.search(r"Last position\\s*:\\s*(20\\d{2}-\\d{2}-\\d{2}\\s+\\d{2}:\\d{2}:\\d{2})\\s*UTC",plain,re.I)
    if not match or not stamp:
        raise ValueError("APRS has no dated readable position")
    lat=(int(match[1])+float(match[2])/60)*(-1 if match[3].upper()=="S" else 1)
    lon=(int(match[4])+float(match[5])/60)*(-1 if match[6].upper()=="W" else 1)
    return make_ais_position(mmsi,lat,lon,parse_utc(stamp[1]),url,"APRS.fi timestamped AIS")

def latest_ais(mmsi, name, previous=None):
    candidates=[]
    failures=[]
    for reader in (ais_shipfinder, ais_aprs, ais_trackipi):
        try:
            candidates.append(reader(mmsi,name))
        except Exception as e:
            failures.append(reader.__name__+": "+str(e))
    if previous and previous.get("mmsi")==mmsi and previous.get("latitude") is not None:
        stamp=parse_utc(previous.get("position_time","").replace("T"," ").replace("Z",""))
        if stamp:
            try:
                candidates.append(make_ais_position(mmsi,float(previous["latitude"]),float(previous["longitude"]),stamp,
                    previous.get("source","Previous verified AIS report"),previous.get("coordinate_source","Previous AIS report")))
            except ValueError:
                pass
    if not candidates:
        return {"checked":False,"mmsi":mmsi,"coordinate_quality":"unavailable",
                "coordinate_note":"No dated AIS coordinates available; position deliberately omitted.",
                "source":"https://www.shipfinder.com/ship/detail/mmsi/"+mmsi,"feed_errors":failures}
    best=max(candidates,key=lambda x:x["position_time"])
    best["feed_errors"]=failures
    best["checked"]=len(failures)<3
    return best

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

# Preserve the latest dated observation across temporary public AIS outages.
try:
    with open("data.json",encoding="utf-8") as f:
        previous_data=json.load(f)
except (OSError,ValueError):
    previous_data={}
data["ship"]=latest_ais("269057517","VIKING VE",previous_data.get("ship"))
data["ship"]["marine_traffic_url"]="https://www.marinetraffic.com/en/ais/home/shipid:3227728/zoom:14"
data["ship_egdir"]=latest_ais("269057766","VIKING EGDIR",previous_data.get("ship_egdir"))
for label,key in (("Viking Ve","ship"),("Viking Egdir","ship_egdir")):
    if data[key].get("coordinate_quality")=="unavailable":
        errors.append(label+": no dated AIS observation available")


data["errors"] = errors
# The refresh timestamp is not proof that every source succeeded.
data["feed_health"] = {
    "german_gauges": "ok" if any(isinstance(v,dict) and v.get("value_cm") is not None for v in data.get("germany",{}).values()) else "unavailable",
    "austrian_gauges": "ok" if any(isinstance(v,dict) and v.get("value_cm") is not None for v in data.get("austria",{}).values()) else "unavailable",
    "viking_public_notice": "ok" if data.get("viking",{}).get("checked") else "unavailable",
    "egdir_ais": "ok" if data.get("ship_egdir",{}).get("coordinate_quality") == "live_machine_readable" else "historical_only",
    "errors_count": len(errors)
}

with open("data.json","w",encoding="utf-8") as f:
    json.dump(data,f,indent=2,ensure_ascii=False)
    f.write("\n")

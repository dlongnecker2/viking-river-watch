#!/usr/bin/env python3
"""Render public AIS pages using a normal Chromium browser, without stealth or CAPTCHA bypass."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

SHIPS={"269057517":"viking-ve","269057766":"viking-egdir"}
URLS=[]
for mmsi,slug in SHIPS.items():
    URLS.extend([
        "https://www.shipfinder.com/ship/detail/mmsi/"+mmsi,
        "https://myshiptracking.com/vessels/"+slug+"-mmsi-"+mmsi+"-imo-0",
        "https://www.trackipi.com/et/vessel/mmsi-"+mmsi+"/",
        "https://aprs.fi/info/i/"+mmsi
    ])
results={}
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True)
    context=browser.new_context(locale="en-US",timezone_id="UTC")
    for url in URLS:
        try:
            page=context.new_page()
            response=page.goto(url,wait_until="domcontentloaded",timeout=18000)
            if response and response.status in (401,403,429):
                print("Access restricted:",response.status,url)
            elif response and response.ok:
                page.wait_for_timeout(1000)
                results[url]={"html":page.content()}
                print("Rendered:",url)
            else:
                print("Unavailable:",url)
            page.close()
        except Exception as exc:
            print("Browser source unavailable:",url,str(exc)[:150])
    browser.close()
Path("ais-browser-results.json").write_text(json.dumps(results),encoding="utf-8")

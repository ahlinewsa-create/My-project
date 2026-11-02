import datetime as dt
import json, os, urllib.parse, urllib.request
from zoneinfo import ZoneInfo

token = os.environ["GOATCOUNTER_API_TOKEN"]
day = dt.datetime.now(ZoneInfo("Asia/Riyadh")).date() - dt.timedelta(days=1)
start = dt.datetime.combine(day, dt.time(), ZoneInfo("Asia/Riyadh"))
end = start + dt.timedelta(days=1)
params = urllib.parse.urlencode({"start":start.isoformat(),"end":end.isoformat(),"limit":100})
url = "https://tal3d-stats.goatcounter.com/api/v0/stats/hits?" + params
request = urllib.request.Request(url, headers={"Authorization":"Bearer "+token,"Accept":"application/json"})
try:
    with urllib.request.urlopen(request, timeout=30) as response:
        result = json.load(response)
except Exception as error:
    raise SystemExit("Could not read GoatCounter API ("+type(error).__name__+"). Check token and Read statistics permission.") from None
hits = result.get("hits")
if not isinstance(hits,list):
    raise SystemExit("Unexpected API response: missing hits")
if result.get("more"):
    raise SystemExit("API result has additional pages; report stopped to avoid incomplete counts")
links = {name:0 for name in ("cults3d","telegram","paypal","instagram","whatsapp","tiktok")}
pages = 0
for hit in hits:
    path = str(hit.get("path","")).lstrip("/").lower()
    count = int(hit.get("count") or 0)
    if path.startswith("outbound/"):
        name = path.partition("/")[2]
        if name in links:
            links[name] += count
    elif not hit.get("event"):
        pages += count
lines = ["# TaL 3D — "+day.isoformat(), "", "Page visits: "+str(pages), "Link clicks: "+str(sum(links.values())), ""]
lines += [name+": "+str(count) for name,count in links.items()]
lines += ["", "Clicks are not confirmed purchases or donations."]
report = "\n".join(lines)+"\n"
os.makedirs("reports",exist_ok=True)
with open("reports/daily.md","w") as f: f.write(report)
if os.environ.get("GITHUB_STEP_SUMMARY"):
    with open(os.environ["GITHUB_STEP_SUMMARY"],"a") as f: f.write(report)
print(report)

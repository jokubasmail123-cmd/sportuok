#!/usr/bin/env python3
"""Prakaituok (sportuok) build.

Šaltinis: data/renginiai.json (rankomis / savaitinės užduoties pildomas sąrašas).
Rezultatai:
  events.json              – svetainė jį pasiima iš GitHub (atnaujinama be perkėlimo į hostingą)
  dist/sportuok/index.html – pilnas puslapis (su įmontuota atsargine duomenų kopija)
  dist/sportuok.zip        – įkėlimui į hostingą

Naudojimas: python3 build.py --owner GITHUB_VARTOTOJAS [--updated YYYY-MM-DD]
"""
import argparse, datetime, json, os, re, shutil, unicodedata, zipfile

ROOT = os.path.dirname(os.path.abspath(__file__))
SPORTS = {"begimas","trail","ultra","plentas","gravel","mtb","cx","plaukimas","triatlonas","duatlonas","akvatlonas",
          "swimrun","orientavimasis","ocr","slidinejimas","nuotykiu","baidares","siaurietiskas","funkcinis"}
REG = {
 "Vilniaus kraštas":["Vilnius","Vilniaus r.","Nemenčinė","Trakai","Trakų r.","Elektrėnai","Vievis","Šilėnai","Ukmergė","Ukmergės r.","Širvintos","Švenčionys","Švenčionių r."],
 "Kauno kraštas":["Kaunas","Kauno r.","Jonava","Kaišiadorys","Kėdainiai","Prienai","Birštonas","Raseiniai"],
 "Klaipėdos kraštas":["Klaipėda","Klaipėdos r.","Palanga","Gargždai","Neringa","Šilutė","Šilutės r.","Kretinga","Šventoji"],
 "Šiaulių kraštas":["Šiauliai","Šiaulių r.","Kuršėnai","Radviliškis","Kelmė","Joniškis","Pakruojis"],
 "Panevėžio kraštas":["Panevėžys","Panevėžio r.","Pasvalys","Biržai","Rokiškis","Kupiškis"],
 "Utenos kraštas":["Utena","Molėtai","Ignalina","Anykščiai","Visaginas","Zarasai","Baltieji Lakajai"],
 "Alytaus kraštas":["Alytus","Alytaus r.","Druskininkai","Varėna","Varėnos r.","Veisiejai","Lazdijai"],
 "Marijampolės kraštas":["Marijampolė","Vištytis","Vilkaviškis","Kazlų Rūdos sav.","Kalvarija","Šakiai","Gelgaudiškis"],
 "Tauragės kraštas":["Tauragė","Skaudvilė","Jurbarkas","Pagėgiai"],
 "Telšių kraštas":["Telšiai","Plungė","Plungės r.","Mažeikiai","Rietavas"],
}
C2R = {c: r for r, cs in REG.items() for c in cs}
REG_HINTS = ("lbmaregistracija", "raceadmin", "manobegimas", "register", "registr", "dbsportas", "myrace")

def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:48]

def enrich(src):
    out, seen, problems = [], set(), []
    for e in src:
        e = dict(e)
        datetime.date.fromisoformat(e["date"])
        if e.get("endDate"): datetime.date.fromisoformat(e["endDate"])
        if e["sport"] not in SPORTS: problems.append(f"nežinoma sporto šaka: {e['sport']} ({e['title']})")
        e["region"] = e.get("region") or C2R.get(e.get("city") or "")
        if not e["region"]:
            problems.append(f"nėra regiono miestui: {e.get('city')} ({e['title']}) – pridėk į REG build.py")
            e["region"] = "Kita"
        u = (e.get("url") or "").lower()
        e["reg"] = e.get("status") == "patvirtinta" and any(h in u for h in REG_HINTS)
        e["distances"] = [re.sub(r"\s*/\s*", " / ", d) for d in e.get("distances") or []]
        i = slug(e["date"][:4] + "-" + e["title"]); b, n = i, 2
        while i in seen: i, n = f"{b}-{n}", n + 1
        seen.add(i); e["id"] = "e-" + i
        out.append(e)
    out.sort(key=lambda e: (e["date"], e["title"]))
    return out, problems

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--owner", default=os.environ.get("SPORTUOK_OWNER", "__OWNER__"))
    ap.add_argument("--updated", default=datetime.date.today().isoformat())
    a = ap.parse_args()
    src = json.load(open(os.path.join(ROOT, "data/renginiai.json"), encoding="utf-8"))
    ev, problems = enrich(src)
    for p in problems: print("ĮSPĖJIMAS:", p)
    json.dump({"updated": a.updated, "count": len(ev), "events": ev},
              open(os.path.join(ROOT, "events.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    t = open(os.path.join(ROOT, "site/template.html"), encoding="utf-8").read()
    t = (t.replace("/*__DATA__*/[]", json.dumps(ev, ensure_ascii=False))
          .replace("/*__UPDATED__*/", a.updated).replace("__OWNER__", a.owner))
    i = t.index("</style>") + len("</style>")
    head, body = t[:i], t[i:]
    doc = f'''<!doctype html>
<html lang="lt">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="description" content="Visi artėjantys sporto renginiai Lietuvoje: bėgimas, dviračiai, gravel, MTB, plaukimas, triatlonas ir kt.">
<meta property="og:title" content="Prakaituok – rask startą">
<meta property="og:description" content="Rask startą. Užsiregistruok. Prakaituok. Visi artėjantys sporto renginiai Lietuvoje.">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='8' fill='%230F1E26'/%3E%3Ccircle cx='23' cy='22' r='4' fill='%23D8402A'/%3E%3C/svg%3E">
{head}
<style>[hidden]{{display:none!important}} body{{margin:0}} img{{max-width:100%}}</style>
</head>
<body>
{body}
</body>
</html>
'''
    d = os.path.join(ROOT, "dist/sportuok"); os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(doc)
    shutil.copy(os.path.join(ROOT, "site/SKAITYK.txt"), d)
    z = os.path.join(ROOT, "dist/sportuok.zip")
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in ("index.html", "SKAITYK.txt"): zf.write(os.path.join(d, f), "sportuok/" + f)
    print(f"OK: {len(ev)} renginiai, atnaujinta {a.updated}, owner={a.owner}")

if __name__ == "__main__":
    main()

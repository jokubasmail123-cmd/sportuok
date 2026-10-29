"""Prakaituok – statinės svetainės generatorius (SEO + GEO).

Iš praturtinto renginių sąrašo sugeneruoja public/ katalogą: pagrindinį puslapį su iš anksto
atvaizduotu sąrašu, renginių, sporto šakų, miestų ir mėnesių puslapius, JSON-LD, sitemap.xml,
robots.txt, llms.txt, .ics kalendorius, .htaccess ir OG paveikslėlį.
"""
import datetime, html, json, os, re, shutil, unicodedata

SITE = "https://prakaituok.lt"
BRAND = "Prakaituok"
SLOGAN = "Rask startą. Užsiregistruok. Prakaituok."

SPORTS = {
 "begimas": ("Bėgimas", "run", "run"), "trail": ("Trail", "trail", "run"), "ultra": ("Ultra", "trail", "run"),
 "plentas": ("Plentas", "road", "bike"), "gravel": ("Gravel", "gravel", "bike"), "mtb": ("MTB", "mtb", "bike"), "cx": ("Cyclocross", "cx", "bike"),
 "plaukimas": ("Plaukimas", "swim", "multi"), "triatlonas": ("Triatlonas", "tri", "multi"), "duatlonas": ("Duatlonas", "tri", "multi"),
 "akvatlonas": ("Akvatlonas", "swim", "multi"), "swimrun": ("Swimrun", "swim", "multi"),
 "orientavimasis": ("Orientavimasis", "other", "other"), "ocr": ("Kliūčių ruožas", "other", "other"), "slidinejimas": ("Slidinėjimas", "other", "other"),
 "nuotykiu": ("Nuotykių lenktynės", "other", "other"), "baidares": ("Baidarės / SUP", "other", "other"),
 "siaurietiskas": ("Šiaurietiškas ėjimas", "other", "other"), "funkcinis": ("Funkcinis / HYROX", "other", "other"),
}
# Puslapiai sporto šakoms: slug -> (sporto raktai, H1, title, aprašymas)
SPORT_PAGES = {
 "begimas": (["begimas", "trail", "ultra"], "Bėgimo varžybos Lietuvoje", "Bėgimo varžybos ir maratonai Lietuvoje {y}",
             "Artėjančios bėgimo varžybos Lietuvoje: maratonai, pusmaratoniai, 5 ir 10 km bėgimai, trail ir ultra. Datos, miestai, distancijos ir registracija."),
 "trail": (["trail"], "Trail bėgimo varžybos", "Trail bėgimo varžybos Lietuvoje {y}", "Trail (miško takų) bėgimo varžybos Lietuvoje: datos, trasos, distancijos ir registracija."),
 "ultra": (["ultra"], "Ultra bėgimai", "Ultra maratonai ir bėgimai Lietuvoje {y}", "Ultra maratonai, backyard ir daugiadieniai bėgimai Lietuvoje."),
 "dviraciai": (["plentas", "gravel", "mtb", "cx"], "Dviračių varžybos Lietuvoje", "Dviračių varžybos ir maratonai Lietuvoje {y}",
               "Artėjančios dviračių varžybos Lietuvoje: plentas, gravel, MTB maratonai ir cyclocross. Datos, distancijos ir registracija."),
 "plentas": (["plentas"], "Plento dviračių renginiai", "Plento dviračių varžybos ir gran fondo Lietuvoje {y}", "Plento dviračių varžybos, gran fondo ir velomaratonai Lietuvoje."),
 "gravel": (["gravel"], "Gravel lenktynės", "Gravel lenktynės Lietuvoje {y}", "Gravel dviračių lenktynės ir žvyrkelių maratonai Lietuvoje: datos, distancijos, registracija."),
 "mtb": (["mtb"], "MTB varžybos", "MTB dviračių maratonai ir varžybos Lietuvoje {y}", "Kalnų dviračių (MTB) maratonai, XC ir gravity varžybos Lietuvoje."),
 "cyclocross": (["cx"], "Cyclocross varžybos", "Cyclocross (dviračių kroso) varžybos Lietuvoje {y}", "Dviračių kroso (cyclocross) varžybos Lietuvoje."),
 "triatlonas": (["triatlonas", "duatlonas", "akvatlonas", "swimrun"], "Triatlono varžybos Lietuvoje", "Triatlono ir akvatlono varžybos Lietuvoje {y}",
                "Triatlono, akvatlono ir duatlono varžybos Lietuvoje: sprintas, olimpinė distancija, 70.3. Datos ir distancijos."),
 "plaukimas": (["plaukimas"], "Plaukimo varžybos", "Plaukimo varžybos mėgėjams Lietuvoje {y}", "Atviro vandens, žiemos ir baseino plaukimo varžybos mėgėjams ir meistrams Lietuvoje."),
 "baidares": (["baidares"], "Baidarių ir SUP maratonai", "Baidarių ir SUP maratonai Lietuvoje {y}", "Baidarių, kanojų ir SUP maratonai bei irklavimo iššūkiai Lietuvoje."),
 "slidinejimas": (["slidinejimas"], "Slidinėjimo renginiai", "Slidinėjimo maratonai ir riedslidžių varžybos Lietuvoje {y}", "Lygumų slidinėjimo ir riedslidžių varžybos mėgėjams Lietuvoje."),
 "orientavimasis": (["orientavimasis", "nuotykiu"], "Orientavimosi varžybos ir nuotykių lenktynės", "Orientavimosi, rogaino ir nuotykių lenktynės Lietuvoje {y}", "Orientavimosi sporto, rogaino ir nuotykių lenktynių renginiai Lietuvoje."),
 "kliuciu-ruozas": (["ocr"], "Kliūčių ruožo lenktynės (OCR)", "Kliūčių ruožo (OCR) lenktynės Lietuvoje {y}", "Kliūčių ruožo (OCR) lenktynės Lietuvoje."),
}
LOC = {"Vilnius": "Vilniuje", "Kaunas": "Kaune", "Klaipėda": "Klaipėdoje", "Panevėžys": "Panevėžyje", "Šiauliai": "Šiauliuose",
 "Alytus": "Alytuje", "Druskininkai": "Druskininkuose", "Trakai": "Trakuose", "Molėtai": "Molėtuose", "Palanga": "Palangoje",
 "Utena": "Utenoje", "Anykščiai": "Anykščiuose", "Ignalina": "Ignalinoje", "Jonava": "Jonavoje", "Kėdainiai": "Kėdainiuose",
 "Nemenčinė": "Nemenčinėje", "Neringa": "Neringoje", "Plungė": "Plungėje", "Ukmergė": "Ukmergėje", "Elektrėnai": "Elektrėnuose",
 "Tauragė": "Tauragėje", "Marijampolė": "Marijampolėje", "Kaišiadorys": "Kaišiadoryse", "Gargždai": "Gargžduose", "Vievis": "Vievyje",
 "Veisiejai": "Veisiejuose", "Skaudvilė": "Skaudvilėje", "Visaginas": "Visagine"}
MON_NOM = ["Sausis","Vasaris","Kovas","Balandis","Gegužė","Birželis","Liepa","Rugpjūtis","Rugsėjis","Spalis","Lapkritis","Gruodis"]
MON_GEN = ["sausio","vasario","kovo","balandžio","gegužės","birželio","liepos","rugpjūčio","rugsėjo","spalio","lapkričio","gruodžio"]
MON_LOC = ["sausį","vasarį","kovą","balandį","gegužę","birželį","liepą","rugpjūtį","rugsėjį","spalį","lapkritį","gruodį"]
WD = ["Pr","An","Tr","Kt","Pn","Št","Sk"]
WD_LONG = ["pirmadienis","antradienis","trečiadienis","ketvirtadienis","penktadienis","šeštadienis","sekmadienis"]
WD_LOC = ["pirmadienį","antradienį","trečiadienį","ketvirtadienį","penktadienį","šeštadienį","sekmadienį"]

_OG = ["/og.png"]
OG_JOBS = []
OG_COL = {"run": "#FF7A5E", "trail": "#E39363", "road": "#6EA2FF", "gravel": "#E2B44E", "mtb": "#6CC27A", "cx": "#B9C65A", "swim": "#4CC7DE", "tri": "#A98BF0", "other": "#9CB0C2"}

def og_set(name, kicker, title, line, chips=(), color="#FF6A4D", badge=""):
    """Užregistruoja atskirą nuorodos peržiūros paveikslėlį šiam puslapiui."""
    OG_JOBS.append(dict(name=name, kicker=kicker, title=title, line=line, chips=list(chips)[:5], color=color, badge=badge))
    _OG[0] = f"/og/{name}.jpg"

def og_reset(): _OG[0] = "/og.png"

esc = lambda s: html.escape(str(s or ""), quote=True)
D = lambda s: datetime.date.fromisoformat(s)

def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")

def city_loc(c):
    if c in LOC: return LOC[c]
    if c.endswith(" r."): return c[:-3] + " rajone"
    return c

def lc(s): return s if s[1:2].isupper() else s[:1].lower() + s[1:]

def iso_short(e):
    s = e['date']
    if e.get('endDate') and e['endDate'] != e['date']: s += '–' + e['endDate'][8:]
    return s

def plural(n, a, b, c):
    return a if n % 10 == 1 and n % 100 != 11 else b if 2 <= n % 10 <= 9 and not 11 <= n % 100 <= 19 else c

def ev_url(e): return f"/renginiai/{e['id'][2:]}/"

def date_lt(e, weekday=True):
    a = D(e["date"]); s = f"{a.year} m. {MON_GEN[a.month-1]} {a.day} d."
    if e.get("endDate") and e["endDate"] != e["date"]:
        b = D(e["endDate"])
        s = f"{a.year} m. {MON_GEN[a.month-1]} {a.day}–{b.day} d." if a.month == b.month else f"{s} – {MON_GEN[b.month-1]} {b.day} d."
    return s + (f" ({WD_LONG[a.weekday()]})" if weekday else "")

def link_label(e): return "Registruotis" if e.get("reg") else "Renginio puslapis"

# ---------- HTML dalys ----------
def card(e):
    a = D(e["date"]); s = SPORTS[e["sport"]]
    multi = ""
    if e.get("endDate") and e["endDate"] != e["date"]:
        b = D(e["endDate"]); multi = f"<small>iki {b.day} {MON_GEN[b.month-1][:3]}.</small>"
    pill = '<span class="pill" title="Organizatoriai datos dar nepaskelbė">Data tikslinama</span>' if e["status"] == "preliminari" else ""
    dist = ('<div class="dist">' + "".join(f"<span>{esc(d)}</span>" for d in e["distances"]) + "</div>") if e.get("distances") else ""
    note = f'<p class="note">{esc(e["note"])}</p>' if e.get("note") else ""
    venue = f" · {esc(e['venue'])}" if e.get("venue") else ""
    prim = f'<a class="btn primary" href="{esc(e["url"])}" target="_blank" rel="noopener">{link_label(e)} ↗</a>' if e.get("url") else ""
    return f'''<article class="ev" style="--c:var(--{s[1]})">
    <div class="bib"><div class="d"><time datetime="{e["date"]}">{a.day}</time>{multi}</div><div class="wd">{WD[a.weekday()]} · {MON_GEN[a.month-1][:3]}.</div></div>
    <div class="body">
      <div class="meta"><span class="tag">{s[0]}</span>{pill}<span>{esc(e["city"])}{venue}</span></div>
      <h3><a href="{ev_url(e)}" data-open="{e["id"]}">{esc(e["title"])}</a></h3>
      {dist}{note}
    </div>
    <div class="side">
      <div class="left" data-left="{e["date"]}"></div>
      <div class="acts"><a class="btn" href="{ev_url(e)}">Plačiau</a>{prim}</div>
    </div>
  </article>'''

def month_groups(evs):
    out, cur = [], None
    for e in evs:
        k = e["date"][:7]
        if k != cur: out.append((k, [])); cur = k
        out[-1][1].append(e)
    return out

def list_html(evs, empty="Šiuo metu artėjančių renginių nėra. Užsuk vėliau – kalendorius pildomas kas savaitę."):
    if not evs: return f'<div class="empty"><b>Renginių nėra</b>{empty}</div>'
    parts = []
    for k, g in month_groups(evs):
        y, m = k.split("-"); m = int(m)
        parts.append(f'<section class="month"><h2><a href="/kalendorius/{k}/" style="color:inherit;text-decoration:none">{MON_NOM[m-1]}</a><span class="yr">{y}</span>'
                     f'<span class="cnt">{len(g)} {plural(len(g),"renginys","renginiai","renginių")}</span></h2><div class="list">{"".join(card(e) for e in g)}</div></section>')
    return "".join(parts)

def table_html(evs, n=15, cap="Artimiausi renginiai"):
    if not evs: return ""
    rows = "".join(f'<tr><td><time datetime="{e["date"]}">{iso_short(e)}</time>{" <span class=pill>tikslinama</span>" if e["status"]=="preliminari" else ""}</td><td><a href="{ev_url(e)}">{esc(e["title"])}</a></td><td>{esc(e["city"])}</td><td>{esc(", ".join(e.get("distances") or []))}</td></tr>' for e in evs[:n])
    return f'<div class="tbl"><table><caption>{cap}</caption><thead><tr><th>Data</th><th>Renginys</th><th>Miestas</th><th>Distancijos</th></tr></thead><tbody>{rows}</tbody></table></div>'

def faq_html(faq):
    return '<section class="faq"><h2>Dažni klausimai</h2>' + "".join(f"<h3>{esc(q)}</h3><p>{esc(a)}</p>" for q, a in faq) + "</section>"

def faq_ld(faq):
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}

FONT = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600;9..40,700&display=swap">'
ICON = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='8' fill='%230F1E26'/%3E%3Ccircle cx='23' cy='22' r='4' fill='%23D8402A'/%3E%3C/svg%3E"

def head(title, desc, path, jsonld=None, extra=""):
    ld = "".join(f'<script type="application/ld+json">{json.dumps(j, ensure_ascii=False)}</script>' for j in (jsonld or []))
    return f'''<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{SITE}{path}">
<meta name="robots" content="index,follow,max-image-preview:large">
<meta property="og:type" content="website"><meta property="og:site_name" content="{BRAND}"><meta property="og:locale" content="lt_LT">
<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{SITE}{path}"><meta property="og:image" content="{SITE}{_OG[0]}"><meta property="og:image:alt" content="{esc(title)}"><meta name="twitter:image" content="{SITE}{_OG[0]}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0F1E26">
<link rel="icon" href="{ICON}"><link rel="apple-touch-icon" href="/icon-512.png"><link rel="manifest" href="/manifest.webmanifest">
<link rel="alternate" type="text/calendar" title="Prakaituok renginių kalendorius" href="/kalendorius.ics">
{FONT}{extra}{ld}'''

def footlinks(sport_pages, city_pages, months):
    sp = " ".join(f'<a href="/{s}/">{SPORT_PAGES[s][1]}</a>' for s in sport_pages)
    ct = " ".join(f'<a href="/miestai/{slug(c)}/">Renginiai {city_loc(c)}</a>' for c in city_pages)
    mo = " ".join(f'<a href="/kalendorius/{k}/">{MON_NOM[int(k[5:])-1]} {k[:4]}</a>' for k in months[:14])
    return f'<nav class="seolinks" aria-label="Renginių katalogas"><div><b>Sportas:</b> {sp}</div><div><b>Miestai:</b> {ct}</div><div><b>Mėnesiai:</b> {mo}</div></nav>'

STATIC_JS = '''<script>
(function(){const t=new Date();t.setHours(0,0,0,0);const pl=(n,a,b,c)=>n%10===1&&n%100!==11?a:(n%10>=2&&n%10<=9&&(n%100<11||n%100>19))?b:c;
document.querySelectorAll("[data-left]").forEach(el=>{const[y,m,d]=el.dataset.left.split("-").map(Number);const n=Math.round((new Date(y,m-1,d)-t)/864e5);
el.innerHTML=n<0?"<b>Įvyko</b>":n===0?"<b>Šiandien</b>":n===1?"<b>Rytoj</b>":`liko<b>${n}</b>${pl(n,"diena","dienos","dienų")}`;if(n<0){const c=el.closest(".ev");c&&(c.style.opacity=".55")}});})();
</script>'''

def page(title, desc, path, crumbs, h1, intro, body, jsonld, foot, upd, extra_head=""):
    bc = " › ".join([f'<a href="{u}">{esc(n)}</a>' for n, u in crumbs[:-1]] + [esc(crumbs[-1][0])])
    bc_ld = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + u} for i, (n, u) in enumerate(crumbs)]}
    return f'''<!doctype html>
<html lang="lt">
<head>
{head(title, desc, path, [bc_ld] + (jsonld or []), extra_head + '<link rel="stylesheet" href="/assets/site.css">')}
</head>
<body>
<div class="wrap">
  <header class="top">
    <div><a href="/" style="text-decoration:none;color:inherit"><span class="h1like">{BRAND}<span class="dot">.</span></span></a>
      <p class="slogan sm">{SLOGAN}</p></div>
    <nav class="topnav" aria-label="Svetainė"><a href="/">Visi renginiai</a><a href="/apie/">Apie</a><a href="/apie/#prideti">Pridėk renginį</a></nav>
  </header>
  <nav class="crumbs" aria-label="Kelias">{bc}</nav>
  <h1 class="ph1">{esc(h1)}</h1>
  <div class="intro">{intro}</div>
  <main>{body}</main>
  <footer>
    {foot}
    <div>Atnaujinta {upd}. Renginių datos surinktos iš organizatorių, federacijų ir registracijos sistemų puslapių. „Data tikslinama“ – organizatoriai datos dar nepaskelbė, rodome tikėtiną datą pagal ankstesnius metus.</div>
    <div class="flinks"><a href="/apie/">Apie</a><a href="/privatumas.html">Privatumo politika</a><a href="/kalendorius.ics">Prenumeruoti kalendorių (.ics)</a></div>
  </footer>
</div>
{STATIC_JS}
</body>
</html>'''

def sports_event_ld(e):
    loc_name = e.get("venue") or e["city"]
    j = {"@context": "https://schema.org", "@type": "SportsEvent", "name": e["title"], "startDate": e["date"],
         "endDate": e.get("endDate") or e["date"], "eventStatus": "https://schema.org/EventScheduled",
         "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
         "location": {"@type": "Place", "name": loc_name, "address": {"@type": "PostalAddress", "addressLocality": e["city"].replace(" r.", " rajonas"), "addressCountry": "LT"}},
         "image": [SITE + _OG[0]], "url": SITE + ev_url(e), "inLanguage": "lt",
         "sport": SPORTS[e["sport"]][0],
         "description": (e.get("note") or f"{e['title']} – {SPORTS[e['sport']][0].lower()} renginys {city_loc(e['city'])}.") +
                        (" Distancijos: " + ", ".join(e["distances"]) + "." if e.get("distances") else "")}
    if e.get("url"): j["sameAs"] = e["url"]
    if e.get("reg") and e.get("url"): j["offers"] = {"@type": "Offer", "url": e["url"], "availability": "https://schema.org/InStock", "validFrom": e["date"][:4] + "-01-01"}
    return j

def event_sentence(e):
    s = SPORTS[e["sport"]][0].lower()
    d = D(e["date"])
    when = date_lt(e, weekday=False)
    wd = WD_LOC[d.weekday()]
    place = city_loc(e["city"]) + (f" ({e['venue']})" if e.get("venue") else "")
    if e["status"] == "preliminari":
        first = f"{e['title']} tikėtina vyks {when} ({wd}) {place}. Organizatoriai tikslios datos dar nepaskelbė – data nustatyta pagal ankstesnius metus."
    else:
        first = f"{e['title']} vyks {when} ({wd}) {place}."
    dist = f" Distancijos: {', '.join(e['distances'])}." if e.get("distances") else ""
    return first + dist

def ics_escape(s): return str(s).replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")
def ics_fold(line):
    b = line.encode("utf-8"); out = []
    while len(b) > 74:
        cut = 74
        while (b[cut] & 0xC0) == 0x80: cut -= 1
        out.append(b[:cut].decode()); b = b[cut:]; b = b" " + b
    out.append(b.decode()); return "\r\n".join(out)

def ics(evs, name, upd):
    stamp = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    L = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Prakaituok//LT", "CALSCALE:GREGORIAN", "METHOD:PUBLISH",
         f"X-WR-CALNAME:{ics_escape(name)}", "X-WR-TIMEZONE:Europe/Vilnius", "REFRESH-INTERVAL;VALUE=DURATION:P1D", "X-PUBLISHED-TTL:P1D"]
    for e in evs:
        if e["status"] != "patvirtinta": continue
        end = D(e.get("endDate") or e["date"]) + datetime.timedelta(days=1)
        L += ["BEGIN:VEVENT", f"UID:{e['id'][2:]}@prakaituok.lt", f"DTSTAMP:{stamp}",
              f"DTSTART;VALUE=DATE:{e['date'].replace('-', '')}", f"DTEND;VALUE=DATE:{end.strftime('%Y%m%d')}",
              f"SUMMARY:{ics_escape(e['title'])}", f"LOCATION:{ics_escape(', '.join(x for x in [e.get('venue'), e['city'], 'Lietuva'] if x))}",
              f"DESCRIPTION:{ics_escape(event_sentence(e) + ' ' + SITE + ev_url(e))}", f"URL:{SITE}{ev_url(e)}", "END:VEVENT"]
    L.append("END:VCALENDAR")
    return "\r\n".join(ics_fold(l) for l in L) + "\r\n"

EXTRA_CSS = '''
.h1like{font-weight:700;font-size:30px;letter-spacing:-.03em}.h1like .dot{color:var(--accent)}
.slogan.sm{font-size:15px;margin-top:2px}
.crumbs{font-size:13px;color:var(--muted);margin:10px 0 4px}.crumbs a{color:var(--muted)}
.ph1{font-weight:700;font-size:clamp(28px,4.4vw,40px);line-height:1.1;margin:8px 0 6px;letter-spacing:-.025em;text-wrap:balance}
.intro{max-width:72ch;color:var(--ink);font-size:16px}.intro p{margin:6px 0}
.facts{display:grid;grid-template-columns:140px 1fr;gap:8px 16px;background:var(--surface);border:1px solid var(--line);border-radius:var(--r);padding:16px;margin:16px 0;max-width:760px}
.facts dt{color:var(--muted);font-size:14px}.facts dd{margin:0;min-width:0;overflow-wrap:anywhere}
.cta{display:flex;flex-wrap:wrap;gap:8px;margin:12px 0 4px}
.faq h2{font-size:22px;margin:28px 0 8px}.faq h3{font-size:17px;margin:16px 0 4px}.faq p{margin:0 0 8px;max-width:72ch}
.tbl{overflow-x:auto;margin:16px 0;border:1px solid var(--line);border-radius:var(--r);background:var(--surface)}
.tbl table{border-collapse:collapse;width:100%;font-size:14px;min-width:560px}
.tbl caption{text-align:left;font-weight:700;padding:12px 14px 4px}
.tbl th,.tbl td{text-align:left;padding:8px 14px;border-top:1px solid var(--line);vertical-align:top}
.tbl th{font-size:13px;color:var(--muted);font-weight:600}
.tbl td:first-child{white-space:nowrap}
.chips-links{display:flex;flex-wrap:wrap;gap:6px;margin:12px 0}.chips-links a{border:1px solid var(--line);background:var(--surface);border-radius:999px;padding:8px 14px;font-weight:600;font-size:14px;text-decoration:none;color:var(--ink)}
@media (max-width:640px){.facts{grid-template-columns:1fr}.facts dt{margin-top:6px}}
'''

def build_site(ev, tpl_index, css, out, upd, cfg, owner):
    today = D(upd)
    OG_JOBS.clear(); og_reset()
    if os.path.exists(out): shutil.rmtree(out)
    os.makedirs(out + "/assets")
    upcoming = [e for e in ev if D(e.get("endDate") or e["date"]) >= today]
    upd_lt = f"{today.year} m. {MON_GEN[today.month-1]} {today.day} d."
    years = sorted({e["date"][:4] for e in upcoming}) or [str(today.year)]
    yr = f"{years[0]}–{years[-1]}" if len(years) > 1 else years[0]

    open(out + "/assets/site.css", "w").write(css + EXTRA_CSS)
    by_sport_page = {s: [e for e in upcoming if e["sport"] in v[0]] for s, v in SPORT_PAGES.items()}
    sport_pages = [s for s, l in by_sport_page.items() if l]
    from collections import Counter
    cc = Counter(e["city"] for e in upcoming)
    city_pages = [c for c, n in cc.most_common() if n >= 2]
    months = sorted({e["date"][:7] for e in upcoming})
    foot = footlinks(sport_pages, city_pages, months)
    urls = [("/", "daily", "1.0")]

    org = {"@context": "https://schema.org", "@type": "Organization", "name": BRAND, "url": SITE + "/", "logo": SITE + "/icon-512.png", "slogan": SLOGAN}
    if cfg.get("contact_email"): org["email"] = cfg["contact_email"]

    # --- renginių puslapiai ---
    for e in ev:
        p = ev_url(e); s = SPORTS[e["sport"]]
        sp_slug = next((k for k, v in SPORT_PAGES.items() if e["sport"] in v[0] and len(v[0]) == 1), None) or \
                  next((k for k, v in SPORT_PAGES.items() if e["sport"] in v[0]), "")
        past = D(e.get("endDate") or e["date"]) < today
        rel = [x for x in upcoming if x["id"] != e["id"] and x["sport"] in SPORT_PAGES.get(sp_slug, ([e["sport"]],))[0]][:6]
        relc = [x for x in upcoming if x["id"] != e["id"] and x["city"] == e["city"] and x not in rel][:4]
        facts = f'''<dl class="facts">
  <dt>Kada</dt><dd>{date_lt(e)}{' · <b>data tikslinama</b>' if e['status']=='preliminari' else ''}{' · <b>renginys jau įvyko</b>' if past else ''}</dd>
  <dt>Kur</dt><dd>{esc(", ".join(x for x in [e.get("venue"), e["city"]] if x))}<br><span class="muted">{esc(e.get("region",""))}</span></dd>
  <dt>Sportas</dt><dd><a href="/{sp_slug}/">{s[0]}</a></dd>
  {'<dt>Distancijos</dt><dd><div class="dist">' + "".join(f"<span>{esc(d)}</span>" for d in e["distances"]) + '</div></dd>' if e.get("distances") else ''}
  {f'<dt>Pastaba</dt><dd>{esc(e["note"])}</dd>' if e.get("note") else ''}
  {f'<dt>Šaltinis</dt><dd><a href="{esc(e["source"])}" rel="nofollow noopener" target="_blank">Duomenų šaltinis ↗</a></dd>' if e.get("source") else ''}
</dl>'''
        gq = ("https://calendar.google.com/calendar/render?action=TEMPLATE&text=" + _q(e["title"]) + "&dates=" + e["date"].replace("-", "") + "/" +
              (D(e.get("endDate") or e["date"]) + datetime.timedelta(days=1)).strftime("%Y%m%d") + "&location=" + _q(", ".join(x for x in [e.get("venue"), e["city"], "Lietuva"] if x)) +
              "&details=" + _q(SITE + p))
        cta = '<div class="cta">' + (f'<a class="btn primary" href="{esc(e["url"])}" target="_blank" rel="noopener">{link_label(e)} ↗</a>' if e.get("url") else "") + \
              f'<a class="btn" href="{esc(gq)}" target="_blank" rel="noopener">Į Google kalendorių ↗</a>' + \
              (f'<a class="btn" href="/renginiai/{e["id"][2:]}.ics">Atsisiųsti .ics</a>' if e["status"] == "patvirtinta" else "") + "</div>"
        body = facts + cta
        if rel: body += f'<h2 class="dayhead">Kiti artimiausi renginiai: {(SPORT_PAGES[sp_slug][1] if sp_slug else s[0]).lower()}</h2><div class="list">{"".join(card(x) for x in rel)}</div>'
        if relc: body += f'<h2 class="dayhead">Kiti renginiai {city_loc(e["city"])}</h2><div class="list">{"".join(card(x) for x in relc)}</div>'
        y = e["date"][:4]
        title = f"{e['title']}{'' if y in e['title'] else ' ' + y} – data, distancijos, registracija | {BRAND}"
        desc = event_sentence(e)[:300]
        og_set("e-" + e["id"][2:], s[0] + (" · " + e["region"] if e.get("region") else ""), e["title"] + ('' if y in e['title'] else f" {y}"),
               date_lt(e, False) + " · " + e["city"], e.get("distances") or [], OG_COL.get(s[1], "#FF6A4D"),
               "Data tikslinama" if e["status"] == "preliminari" else ("Registracija atidaryta" if e.get("reg") else ""))
        ld = [sports_event_ld(e)] if e["status"] == "patvirtinta" else []
        intro = f"<p>{esc(event_sentence(e))}</p>"
        open_mk(out + p).write(page(title, desc, p, [("Renginiai", "/"), (SPORT_PAGES[sp_slug][1] if sp_slug else s[0], f"/{sp_slug}/"), (e["title"], p)],
                                     e["title"] + ('' if y in e['title'] else f" {y}"), intro, body, ld, foot, upd_lt))
        og_reset()
        if e["status"] == "patvirtinta":
            open(out + f"/renginiai/{e['id'][2:]}.ics", "w", newline="").write(ics([e], e["title"], upd))
        urls.append((p, "weekly", "0.6" if past else "0.8"))

    # --- sporto šakų puslapiai ---
    for s, (keys, h1, ttl, desc) in SPORT_PAGES.items():
        l = by_sport_page[s]
        if not l: continue
        conf = [e for e in l if e["status"] == "patvirtinta"]
        nxt = l[0]
        subs = [k for k, v in SPORT_PAGES.items() if k != s and set(v[0]) < set(keys) and by_sport_page[k]]
        intro = (f"<p>{esc(desc)} Šiuo metu kalendoriuje – {len(l)} {plural(len(l),'renginys','renginiai','renginių')}, iš jų {len(conf)} su patvirtinta data. "
                 f"Artimiausias – <a href=\"{ev_url(nxt)}\">{esc(nxt['title'])}</a>, {date_lt(nxt, False)} {city_loc(nxt['city'])}.</p>")
        if subs: intro += '<div class="chips-links">' + "".join(f'<a href="/{k}/">{SPORT_PAGES[k][1]}</a>' for k in subs) + '</div>'
        il = {"@context": "https://schema.org", "@type": "ItemList", "name": h1, "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "url": SITE + ev_url(e), "name": e["title"]} for i, e in enumerate(l[:50])]}
        low = (h1[0].lower() + h1[1:]) if h1[1:2].islower() else h1
        adj = 'artimiausios' if re.search(r'varžybos|lenktynės', h1) else 'artimiausi'
        biggest = next((e for e in conf if any(x in " ".join(e.get("distances") or []) for x in ("42", "100 km", "70.3", "1,9"))), conf[0] if conf else nxt)
        cities = Counter(e["city"] for e in l).most_common(3)
        fq = [(f"Kada vyks {adj} {low.replace(' Lietuvoje','')}?", f"Artimiausias renginys – {nxt['title']}, {date_lt(nxt)} {city_loc(nxt['city'])}." + (f" Po jo – {l[1]['title']} ({date_lt(l[1], False)}, {l[1]['city']})." if len(l) > 1 else "")),
              (f"Kiek renginių yra kalendoriuje?", f"Šiuo metu – {len(l)} {plural(len(l),'renginys','renginiai','renginių')}, iš jų {len(conf)} su organizatorių patvirtinta data. Daugiausia renginių vyksta: {', '.join(f'{c} ({n})' for c, n in cities)}. Kalendorius atnaujinamas kas savaitę."),
              ("Kur registruotis?", "Registracija vyksta organizatorių sistemose. Kiekvieno renginio puslapyje yra mygtukas „Registruotis“ arba „Renginio puslapis“, vedantis pas organizatorių, taip pat galima įsidėti renginį į Google kalendorių ar atsisiųsti .ics failą.")]
        if biggest: fq.insert(1, ("Koks didžiausias artėjantis renginys?", f"{biggest['title']} – {date_lt(biggest, False)} {city_loc(biggest['city'])}" + (f", distancijos: {', '.join(biggest['distances'])}." if biggest.get('distances') else ".")))
        body = table_html(l) + list_html(l) + faq_html(fq) + f'<p style="margin-top:18px"><a href="/{s}.ics">Prenumeruoti „{h1}“ kalendorių (.ics)</a></p>'
        og_set("s-" + s, "Kalendorius " + yr, h1, f"{len(l)} {plural(len(l),'renginys','renginiai','renginių')} · artimiausias {date_lt(nxt, False)}",
               sorted({e["city"] for e in l}, key=lambda c: -sum(x["city"] == c for x in l))[:4], OG_COL.get(SPORTS[keys[0]][1], "#FF6A4D"))
        open_mk(out + f"/{s}/").write(page(ttl.format(y=yr) + f" | {BRAND}", desc, f"/{s}/", [("Renginiai", "/"), (h1, f"/{s}/")], f"{h1} {yr}", intro, body, [il, faq_ld(fq)], foot, upd_lt))
        og_reset()
        open(out + f"/{s}.ics", "w", newline="").write(ics(l, f"{BRAND}: {h1}", upd))
        urls.append((f"/{s}/", "weekly", "0.9"))

    # --- miestų puslapiai ---
    for c in city_pages:
        l = [e for e in upcoming if e["city"] == c]
        sp = Counter(lc(SPORTS[e["sport"]][0]) for e in l)
        sl = "/miestai/" + slug(c) + "/"
        intro = f"<p>Artėjantys sporto renginiai {city_loc(c)}: {', '.join(k for k, _ in sp.most_common(5))}. Kalendoriuje – {len(l)} {plural(len(l),'renginys','renginiai','renginių')}.</p>"
        og_set("c-" + slug(c), "Kalendorius " + yr, f"Sporto renginiai {city_loc(c)}", f"{len(l)} {plural(len(l),'renginys','renginiai','renginių')} · artimiausias {date_lt(l[0], False)}", [k for k, _ in sp.most_common(4)])
        open_mk(out + sl).write(page(f"Sporto renginiai {city_loc(c)} {yr} – bėgimas, dviračiai, triatlonas | {BRAND}",
                                     f"Visi artėjantys sporto renginiai {city_loc(c)}: datos, distancijos ir registracija. {len(l)} renginiai kalendoriuje.",
                                     sl, [("Renginiai", "/"), (f"Renginiai {city_loc(c)}", sl)], f"Sporto renginiai {city_loc(c)}", intro, table_html(l, 20, f"Renginiai {city_loc(c)}") + list_html(l), [], foot, upd_lt))
        og_reset()
        urls.append((sl, "weekly", "0.7"))

    # --- mėnesių puslapiai ---
    for k in months:
        y, m = int(k[:4]), int(k[5:])
        l = [e for e in upcoming if e["date"][:7] == k]
        sl = f"/kalendorius/{k}/"
        sp = Counter(lc(SPORTS[e["sport"]][0]) for e in l)
        intro = f"<p>{y} m. {MON_LOC[m-1]} Lietuvoje vyks {len(l)} {plural(len(l),'sporto renginys','sporto renginiai','sporto renginių')}: {', '.join(f'{v} – {n}' for v, n in sp.most_common(6))}.</p>"
        i = months.index(k)
        nav = '<div class="chips-links">' + (f'<a href="/kalendorius/{months[i-1]}/">← {MON_NOM[int(months[i-1][5:])-1]}</a>' if i else "") + \
              (f'<a href="/kalendorius/{months[i+1]}/">{MON_NOM[int(months[i+1][5:])-1]} →</a>' if i + 1 < len(months) else "") + "</div>"
        og_set("m-" + k, "Mėnesio kalendorius", f"Sporto renginiai {y} m. {MON_LOC[m-1]}", f"{len(l)} {plural(len(l),'renginys','renginiai','renginių')} visoje Lietuvoje", [x for x, _ in sp.most_common(4)])
        open_mk(out + sl).write(page(f"Sporto renginiai {y} m. {MON_LOC[m-1]} – bėgimas, dviračiai, triatlonas | {BRAND}",
                                     f"Kokie sporto renginiai vyks Lietuvoje {y} m. {MON_LOC[m-1]}? {len(l)} renginiai: datos, miestai, distancijos ir registracija.",
                                     sl, [("Renginiai", "/"), (f"{MON_NOM[m-1]} {y}", sl)], f"Sporto renginiai {y} m. {MON_LOC[m-1]}", intro + nav, table_html(l, 40, f"{MON_NOM[m-1]} {y}: visi renginiai") + list_html(l) + nav, [], foot, upd_lt))
        og_reset()
        urls.append((sl, "weekly", "0.7"))

    # --- apie + DUK ---
    nconf = sum(e["status"] == "patvirtinta" for e in upcoming)
    faq = [
      ("Kas yra Prakaituok?", f"Prakaituok – nemokamas mėgėjų sporto renginių Lietuvoje kalendorius. Vienoje vietoje surinkti bėgimo, trail, dviračių (plento, gravel, MTB), triatlono, plaukimo, baidarių, slidinėjimo, orientavimosi ir kliūčių ruožo renginiai. Šiuo metu kalendoriuje – {len(upcoming)} artėjantys renginiai."),
      ("Iš kur imama renginių informacija?", "Iš viešų organizatorių puslapių, sporto federacijų kalendorių (pvz., Lietuvos triatlono federacijos, Lietuvos dviračių sporto federacijos, LTU Aquatics) ir registracijos sistemų (LBMA registracija, Mano bėgimas, RaceAdmin). Prie kiekvieno renginio nurodytas duomenų šaltinis."),
      ("Kaip dažnai atnaujinamas kalendorius?", f"Kas savaitę, pirmadieniais. Paskutinį kartą atnaujinta {upd_lt}."),
      ("Ką reiškia „Data tikslinama“?", f"Tai kasmetinis renginys, kurio kitų metų datos organizatoriai dar nepaskelbė. Rodome tikėtiną datą pagal ankstesnius metus (tą pačią savaitės dieną). Kai organizatoriai paskelbia datą, ji pažymima kaip patvirtinta. Dabar patvirtintų datų – {nconf}."),
      ("Ar galiu užsiregistruoti per Prakaituok?", "Ne – registracija vyksta organizatorių sistemose. Prie kiekvieno renginio yra mygtukas „Registruotis“ arba „Renginio puslapis“, vedantis tiesiai pas organizatorių."),
      ("Kaip įsidėti renginius į savo kalendorių?", "Kiekvieną renginį galima įsidėti į Google kalendorių arba atsisiųsti .ics failą. Taip pat galima prenumeruoti visą kalendorių ar atskiros sporto šakos kalendorių (.ics) – jis atsinaujins pats."),
      ("Kaip pridėti savo renginį?", "Parašyk mums el. paštu: renginio pavadinimą, datą, vietą, distancijas ir nuorodą į registraciją. Renginius įtraukiame nemokamai."),
    ]
    apie_ld = faq_ld(faq)
    email = cfg.get("contact_email") or ""
    add = f'<h2 id="prideti">Pridėk renginį</h2><p>Organizuoji sporto renginį Lietuvoje? Atsiųsk pavadinimą, datą, vietą, distancijas ir registracijos nuorodą{": <b>" + esc(email) + "</b>" if email else " – kontaktą rasi netrukus"}. Įtraukiame nemokamai.</p>'
    body = '<div class="faq">' + "".join(f"<h3>{esc(q)}</h3><p>{esc(a)}</p>" for q, a in faq) + add + \
           '<h2>Sporto šakos</h2><div class="chips-links">' + "".join(f'<a href="/{s}/">{SPORT_PAGES[s][1]}</a>' for s in sport_pages) + "</div></div>"
    open_mk(out + "/apie/").write(page(f"Apie {BRAND} – sporto renginių Lietuvoje kalendorius", faq[0][1][:300], "/apie/",
                                       [("Renginiai", "/"), ("Apie", "/apie/")], f"Apie {BRAND}", f"<p><b>{SLOGAN}</b></p>", body, [apie_ld, org], foot, upd_lt))
    urls.append(("/apie/", "monthly", "0.5"))

    # --- pagrindinis puslapis ---
    il = {"@context": "https://schema.org", "@type": "ItemList", "name": "Artėjantys sporto renginiai Lietuvoje", "numberOfItems": len(upcoming),
          "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": SITE + ev_url(e), "name": e["title"]} for i, e in enumerate(upcoming[:100])]}
    web = {"@context": "https://schema.org", "@type": "WebSite", "name": BRAND, "url": SITE + "/", "inLanguage": "lt", "description": SLOGAN}
    title = f"Sporto renginiai Lietuvoje {yr}: bėgimas, dviračiai, triatlonas | {BRAND}"
    desc = f"{SLOGAN} {len(upcoming)} artėjantys sporto renginiai Lietuvoje vienoje vietoje: maratonai, bėgimai, gravel, MTB, triatlonas, plaukimas. Atnaujinama kas savaitę."
    i = tpl_index.index("</style>") + len("</style>")
    hd, bd = tpl_index[:i], tpl_index[i:]
    hd = re.sub(r"^<title>.*?</title>\s*", "", hd)
    hd = re.sub(r'<link rel="preconnect"[^>]*>\s*', "", hd)
    hd = re.sub(r'<link rel="stylesheet" href="https://fonts.googleapis.com[^>]*>\s*', "", hd)
    bd = bd.replace("<!--__PRERENDER__-->", list_html(upcoming)).replace("<!--__FOOTLINKS__-->", foot)
    idx = f'''<!doctype html>
<html lang="lt">
<head>
{head(title, desc, "/", [web, org, il])}
{hd}
<style>[hidden]{{display:none!important}} body{{margin:0}} img{{max-width:100%}}</style>
</head>
<body>
{bd}
{STATIC_JS}
</body>
</html>
'''
    open(out + "/index.html", "w").write(idx)

    # --- 404 ---
    open(out + "/404.html", "w").write(page(f"Puslapis nerastas | {BRAND}", "Tokio puslapio nėra.", "/404.html", [("Renginiai", "/"), ("Puslapis nerastas", "/404.html")],
        "Puslapis nerastas", "<p>Galbūt renginys jau įvyko arba nuoroda pasikeitė.</p>", list_html(upcoming[:8]) + '<p><a class="btn primary" href="/">Visi renginiai</a></p>', [], foot, upd_lt)
        .replace('<meta name="robots" content="index,follow,max-image-preview:large">', '<meta name="robots" content="noindex">'))

    # --- failai robotams ---
    open(out + "/kalendorius.ics", "w", newline="").write(ics(upcoming, f"{BRAND}: sporto renginiai Lietuvoje", upd))
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u, f, pr in urls: sm.append(f"<url><loc>{SITE}{u}</loc><lastmod>{upd}</lastmod><changefreq>{f}</changefreq><priority>{pr}</priority></url>")
    sm.append("</urlset>")
    open(out + "/sitemap.xml", "w").write("\n".join(sm))
    open(out + "/robots.txt", "w").write(f"""User-agent: *
Allow: /
Disallow: /404.html

# AI paieškos ir asistentai – kviečiami
User-agent: GPTBot
Allow: /
User-agent: OAI-SearchBot
Allow: /
User-agent: ChatGPT-User
Allow: /
User-agent: ClaudeBot
Allow: /
User-agent: Claude-SearchBot
Allow: /
User-agent: PerplexityBot
Allow: /
User-agent: Google-Extended
Allow: /
User-agent: Applebot-Extended
Allow: /

Sitemap: {SITE}/sitemap.xml
""")
    llm = [f"# {BRAND}", "", f"> {BRAND} ({SITE}) – nemokamas mėgėjų sporto renginių Lietuvoje kalendorius: bėgimas, trail, dviračiai (plentas, gravel, MTB), triatlonas, plaukimas, baidarės, slidinėjimas, orientavimasis. Atnaujinama kas savaitę; paskutinį kartą {upd}.", "",
           f"Kalendoriuje {len(upcoming)} artėjantys renginiai ({nconf} su patvirtinta data). „Data tikslinama“ reiškia, kad data spėjama pagal ankstesnius metus.", "",
           "## Sporto šakos"] + [f"- [{SPORT_PAGES[s][1]}]({SITE}/{s}/): {len(by_sport_page[s])} renginiai" for s in sport_pages] + \
          ["", "## Miestai"] + [f"- [Renginiai {city_loc(c)}]({SITE}/miestai/{slug(c)}/)" for c in city_pages] + \
          ["", "## Mėnesiai"] + [f"- [{MON_NOM[int(k[5:])-1]} {k[:4]}]({SITE}/kalendorius/{k}/)" for k in months] + \
          ["", "## Duomenys", f"- [Visi renginiai tekstu]({SITE}/llms-full.txt)", f"- [Renginiai JSON]({SITE}/events.json)", f"- [Kalendorius .ics]({SITE}/kalendorius.ics)", f"- [Apie ir DUK]({SITE}/apie/)", ""]
    open(out + "/llms.txt", "w").write("\n".join(llm))
    full = [f"# {BRAND}: artėjantys sporto renginiai Lietuvoje (atnaujinta {upd})", ""]
    for k, g in month_groups(upcoming):
        full.append(f"## {MON_NOM[int(k[5:])-1]} {k[:4]}")
        for e in g:
            full.append(f"- {date_lt(e)} – {e['title']} ({SPORTS[e['sport']][0]}, {e['city']}){' – DATA TIKSLINAMA' if e['status']=='preliminari' else ''}. "
                        + (f"Distancijos: {', '.join(e['distances'])}. " if e.get('distances') else "") + f"{SITE}{ev_url(e)}")
        full.append("")
    open(out + "/llms-full.txt", "w").write("\n".join(full))
    json.dump({"updated": upd, "count": len(ev), "events": ev}, open(out + "/events.json", "w"), ensure_ascii=False)
    open(out + "/manifest.webmanifest", "w").write(json.dumps({"name": BRAND, "short_name": BRAND, "lang": "lt", "start_url": "/", "display": "standalone",
        "background_color": "#EDF0F1", "theme_color": "#0F1E26", "icons": [{"src": "/icon-512.png", "sizes": "512x512", "type": "image/png"}]}, ensure_ascii=False))
    open(out + "/.htaccess", "w").write("""# Prakaituok – Hostinger (LiteSpeed/Apache)
RewriteEngine On
# Vienas pagrindinis adresas: https://prakaituok.lt (be www, be hostingersite)
RewriteCond %{HTTPS} off [OR]
RewriteCond %{HTTP_HOST} !^prakaituok\\.lt$ [NC]
RewriteRule ^(.*)$ https://prakaituok.lt/$1 [R=301,L]
ErrorDocument 404 /404.html
DirectoryIndex index.html
AddType text/calendar .ics
AddType application/manifest+json .webmanifest
AddDefaultCharset utf-8
AddCharset utf-8 .txt .json .ics .xml
<IfModule mod_headers.c>
  Header always set X-Content-Type-Options "nosniff"
  Header always set Referrer-Policy "strict-origin-when-cross-origin"
  <FilesMatch "\\.(html|json|ics|xml|txt)$">
    Header set Cache-Control "public, max-age=600, must-revalidate"
  </FilesMatch>
  <FilesMatch "\\.(css|png|webmanifest)$">
    Header set Cache-Control "public, max-age=604800"
  </FilesMatch>
</IfModule>
""")
    return urls

def _q(s):
    from urllib.parse import quote
    return quote(s, safe="")

def open_mk(path):
    if path.endswith("/"): path += "index.html"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return open(path, "w", encoding="utf-8")

def _font_css():
    import base64
    d = os.path.join(os.path.dirname(os.path.abspath(__file__)), "site/fonts")
    css = ""
    for w in (400, 700):
        for sub, rng in (("latin", "U+0000-00FF,U+2000-206F,U+20AC"), ("latin-ext", "U+0100-02AF,U+1E00-1EFF")):
            p = os.path.join(d, f"dm-sans-{sub}-{w}-normal.woff2")
            if os.path.exists(p):
                b = base64.b64encode(open(p, "rb").read()).decode()
                css += f"@font-face{{font-family:DMS;font-weight:{w};src:url(data:font/woff2;base64,{b}) format('woff2');unicode-range:{rng}}}"
    return css

def _og_html(j, fcss):
    t = j["title"]; n = len(t)
    fs = 96 if n <= 22 else 80 if n <= 34 else 66 if n <= 50 else 54
    chips = "".join(f'<span class="c">{esc(c)}</span>' for c in j["chips"])
    badge = f'<span class="b">{esc(j["badge"])}</span>' if j["badge"] else ""
    return f"""<html><head><style>{fcss}
*{{box-sizing:border-box}}body{{margin:0;width:1200px;height:630px;background:#0F1E26;color:#E7EEF0;font-family:DMS,Arial,sans-serif;position:relative;overflow:hidden}}
.bar{{position:absolute;left:0;top:0;bottom:0;width:22px;background:{j["color"]}}}
.glow{{position:absolute;right:-180px;top:-180px;width:620px;height:620px;border-radius:50%;background:radial-gradient(circle,{j["color"]}33,transparent 65%)}}
.in{{position:absolute;left:84px;right:80px;top:64px;bottom:58px;display:flex;flex-direction:column}}
.top{{display:flex;align-items:center;gap:16px;font-size:30px;font-weight:700;letter-spacing:-.5px}}
.top .k{{font-weight:400;color:{j["color"]};font-size:26px;border:2px solid {j["color"]};border-radius:999px;padding:4px 16px}}
.dot{{color:#FF6A4D}}
h1{{font-size:{fs}px;line-height:1.04;letter-spacing:-2px;margin:auto 0 18px;font-weight:700;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}}
.l{{font-size:36px;font-weight:700;color:#fff}}
.row{{display:flex;gap:10px;flex-wrap:wrap;margin-top:22px;align-items:center}}
.c{{background:#1B2A31;border:1px solid #2A3B43;border-radius:10px;padding:8px 16px;font-size:26px;color:#cfdade}}
.b{{background:{j["color"]};color:#0F1E26;border-radius:999px;padding:8px 18px;font-size:24px;font-weight:700}}
.ft{{display:flex;justify-content:space-between;margin-top:30px;font-size:24px;color:#93A5AD}}
</style></head><body><div class="bar"></div><div class="glow"></div><div class="in">
<div class="top"><span>Prakaituok<span class="dot">.</span></span><span class="k">{esc(j["kicker"])}</span></div>
<h1>{esc(t)}</h1><div class="l">{esc(j["line"])}</div>
<div class="row">{badge}{chips}</div>
<div class="ft"><span>Rask startą. Užsiregistruok. Prakaituok.</span><span>prakaituok.lt</span></div></div></body></html>"""

def make_images(out):
    """Nuorodų peržiūros (OG 1200×630) paveikslėliai kiekvienam puslapiui ir ikona per Playwright."""
    try:
        from playwright.sync_api import sync_playwright
    except Exception as ex:
        print("ĮSPĖJIMAS: Playwright nėra, OG paveikslėliai nesugeneruoti", ex); return
    fcss = _font_css()
    main = dict(name="og", kicker="Sporto renginiai Lietuvoje", title="Visi sporto renginiai Lietuvoje vienoje vietoje",
                line="Bėgimas · dviračiai · gravel · triatlonas · plaukimas", chips=[], color="#FF6A4D", badge="Atnaujinama kas savaitę")
    icon = """<html><body style="margin:0;width:512px;height:512px;background:#0F1E26;display:flex;align-items:center;justify-content:center;font-family:DMS,Arial,sans-serif">
<style>""" + fcss + """</style><div style="font-size:330px;font-weight:700;color:#E7EEF0;letter-spacing:-20px;margin-top:-30px">P<span style="color:#FF6A4D">.</span></div></body></html>"""
    os.makedirs(os.path.join(out, "og"), exist_ok=True)
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1200, "height": 630})
            pg.set_content(_og_html(main, fcss)); pg.wait_for_timeout(150); pg.screenshot(path=os.path.join(out, "og.png"))
            for j in OG_JOBS:
                pg.set_content(_og_html(j, fcss)); pg.screenshot(path=os.path.join(out, "og", j["name"] + ".jpg"), type="jpeg", quality=82)
            pg.close(); ip = b.new_page(viewport={"width": 512, "height": 512}); ip.set_content(icon); ip.wait_for_timeout(100)
            ip.screenshot(path=os.path.join(out, "icon-512.png")); b.close()
        print(f"OG paveikslėliai: {len(OG_JOBS) + 1}")
    except Exception as ex:
        print("ĮSPĖJIMAS: paveikslėlių generavimas nepavyko:", ex)

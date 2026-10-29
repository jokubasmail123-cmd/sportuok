# Sportuok

Artėjančių mėgėjų sporto renginių Lietuvoje kalendorius: bėgimas, dviračiai, plaukimas, triatlonas ir kt.

- `data/renginiai.json` – renginių sąrašas (šaltinis)
- `events.json` – sugeneruotas failas, kurį svetainė pasiima tiesiogiai iš šios repozitorijos
- `site/template.html` – puslapis
- `build.py` – sugeneruoja `events.json`, `dist/sportuok/index.html` ir `dist/sportuok.zip`
- `SAVAITINIS-ATNAUJINIMAS.md` – instrukcija savaitiniam atnaujinimui
- `PAKEITIMAI.md` – kas ir kada pasikeitė

Repozitorija turi būti **vieša** (public), kad svetainė galėtų perskaityti `events.json`.

# Prakaituok.lt (repo: sportuok)

Artėjančių mėgėjų sporto renginių Lietuvoje kalendorius: bėgimas, dviračiai, plaukimas, triatlonas ir kt.

- `data/renginiai.json` – renginių sąrašas (šaltinis)
- `events.json` – sugeneruotas failas, kurį svetainė pasiima tiesiogiai iš šios repozitorijos
- `site/template.html` – puslapis
- `build.py` – sugeneruoja `events.json`, `dist/sportuok/index.html` ir `dist/sportuok.zip`
- `SAVAITINIS-ATNAUJINIMAS.md` – instrukcija savaitiniam atnaujinimui
- `PAKEITIMAI.md` – kas ir kada pasikeitė

Repozitorija turi būti **vieša** (public), kad svetainė galėtų perskaityti `events.json`.


## Reklama (config.json)
- `gads_id` – Google Ads žymos ID (AW-...)
- `gads_conversion_label` – konversijos „Renginio nuorodos paspaudimas“ etiketė
- `adsense_pub` – AdSense leidėjo ID (ca-pub-...), sugeneruoja ir `ads.txt`
- `google_cmp` – `true`, kai AdSense įjungtas Google sutikimo pranešimas (tada mūsų juosta nerodoma)
- `contact_email` – kontaktas privatumo politikoje

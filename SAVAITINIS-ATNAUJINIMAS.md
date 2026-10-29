# Savaitinis Sportuok atnaujinimas

Šią instrukciją kas savaitę vykdo suplanuota Claude užduotis. Tikslas: rasti naujus ar pasikeitusius
mėgėjų sporto renginius Lietuvoje ir atnaujinti `data/renginiai.json`. Svetainė pasiima `events.json` iš šios
repozitorijos pati, todėl į hostingą nieko kelti nereikia.

## Taisyklės
- Įtraukti tik renginius **Lietuvoje**, atvirus mėgėjams.
- Datą rašyti tik tokią, kokią radai šaltinyje. **Niekada neišgalvoti.**
- `status: "patvirtinta"` – data paskelbta organizatorių. `status: "preliminari"` – kasmetinis renginys, kurio
  naujų metų data nepaskelbta; data spėjama pagal ankstesnius metus (ta pati savaitės diena), `note` turi
  pasakyti „2026 m. vyko …“.
- Praėjusių renginių **netrinti** (svetainė juos slepia pati). Trinti tik tada, jei renginys atšauktas.
- Nekeisti `site/template.html` ir `build.py`, nebent build'as krenta.

## Žingsniai
1. Perskaityk `data/renginiai.json`.
2. Patikrink šaltinius (prioritetas – artimiausi 3 mėnesiai, tada kiti metai):
   - Bėgimas: lbmaregistracija.lt (kiekvieno renginio `/nuostatai/`), lbma.lt/files/races/, manobegimas.lt,
     kaunasmarathon.lt, vilniustrailrun.lt, trailokalve.lt, ahotu.com/calendar/running/lithuania, finishers.com
   - Dviračiai: ldsf.ldsf.lt/calendar, uzjudek.lt/events?sport=cycling, mtb.lt, grunto.lt, druskagravel.com,
     velomaratonas.lt, velocx.lt, raceadmin.eu
   - Triatlonas, plaukimas: triatlonas.lt, ltuaquatics.com (kalendorius, meistrai, atviras vanduo), trakutriatlonas.lt, swimltu.lt
   - Kita: bimt.lt/events (baidarės), skigo.lt, lnsa.lt (slidinėjimas), rogaining.lt, vilniuschallenge.lt,
     balticwarriors.lt (OCR), losf.lt (orientavimasis)
3. Kiekvienam radiniui:
   - **Naujas renginys** → pridėk įrašą.
   - **„preliminari“ renginiui paskelbta tikra data** → pakeisk `date`, `status: "patvirtinta"`, `url` į registraciją, atnaujink `note` ir `source`.
   - **Pasikeitė data, vieta ar distancijos** → pataisyk.
   - Dublikatų nekurk: tas pats renginys tais pačiais metais = vienas įrašas.
4. Paleisk `python3 build.py --owner <OWNER>`. Jei rodo „ĮSPĖJIMAS“ dėl regiono, pridėk miestą į `REG` sąrašą `build.py`.
5. Jei pakeitimų nėra, nieko necommitink ir baik.
6. Jei pakeitimai yra, papildyk `PAKEITIMAI.md` viršuje:
   `## YYYY-MM-DD` ir sąrašas: „+ Naujas: …“, „✓ Patvirtinta data: …“, „~ Pakeista: …“.
7. Commit ir push į `main` su žinute `Savaitinis atnaujinimas YYYY-MM-DD: +N nauji, M patvirtinti`.
8. Galutiniame atsakyme lietuviškai trumpai išvardyk pakeitimus.

## Įrašo formatas (`data/renginiai.json`)
```json
{"title":"Kauno Akropolio maratonas","date":"2027-04-25","endDate":null,"sport":"begimas",
 "city":"Kaunas","venue":"Kauno Akropolis","distances":["5 km","10 km","21,1 km","42,195 km"],
 "url":"https://www.kaunasmarathon.lt/","status":"patvirtinta","note":"Maratono startas 8:30.",
 "source":"https://www.kaunasmarathon.lt/"}
```
`sport`: begimas, trail, ultra, plentas, gravel, mtb, cx, plaukimas, triatlonas, duatlonas, akvatlonas, swimrun,
orientavimasis, ocr, slidinejimas, nuotykiu, baidares, siaurietiskas, funkcinis.
`city`: miestas arba „X r.“ (rajonas). Regionas priskiriamas automatiškai.

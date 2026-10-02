# Since — livedemonstration och presentation (utkast)

Utkast, T-048. Antaganden som inte är bekräftade: cirka 10 minuter plus frågor, på
att korta. Allt som står som siffra här finns i repot; källan anges i sista avsnittet.

## Före demon

Demofrågorna nedan är kontrollerade mot data till och med 2 oktober 2026. Ny data
ändrar svaren, eftersom "de senaste två veckorna" räknas från det senaste datumet i
samlingen. Gör därför så här:

**Dagen före:**

1. Uppdatera datan: starta appen, gå till sidan **Sources** och tryck **Update now**.
   Det tar några minuter, och längre om nya videor måste transkriberas.
2. Kontrollera demofrågorna mot den nya datan:
   `python scripts/t048_verify_demo_questions.py`. Läs svaren och rätta "Väntat svar"
   nedan om de har ändrats. Byt fråga 2 till det nya senaste datumet.

**15 minuter före:**

3. Starta Ollama och appen: `streamlit run app.py`.
4. Ställ en valfri fråga och vänta tills svaret kommer, så att båda modellerna är
   laddade. Därefter tar sökningen några sekunder och svaret 5–15 sekunder.
5. Ha `docs/screenshots/t042-ui-light-theme.png` öppen i en flik som reserv om modellen
   inte svarar.
6. Ha `docs/eval-results/2026-09-22-0027-t032-date-aware-vs-plain.md` öppen i en flik.

## 1. Problemet (1 min)

> Jag följer AI-forskning via Hugging Face Daily Papers och fyra YouTube-kanaler. Ingen
> av dem har något minne. Jag kan inte fråga "har någon tagit upp det här den senaste
> månaden?" utan att läsa om allt själv. De tjänster som kan det kostar pengar och
> skickar mina intressen till någon annans moln.

Since är ett litet, lokalt alternativ med öppen källkod. Allt körs på min egen dator,
utan konto och utan server.

## 2. Vad jag ville pröva (1 min)

Påståendet: om man filtrerar på datum **innan** man söker på likhet får man bättre svar
på tidsbundna frågor än med ren likhetssökning.

Två saker att säga tydligt:

- Datumet är det datum något dök upp i flödet, inte när det först publicerades. En
  artikel kan ha legat på arXiv i veckor innan Hugging Face lyfter fram den, och det är
  just "vad är nytt i flödet" jag vill kunna fråga om.
- Frågorna och facit skrevs innan sökningen byggdes, så att systemet inte kunde
  anpassas efter dem.

## 3. Livedemo (4 min)

Peka först på statusraden: antal dokument och senaste datum i samlingen.

Väntade svar nedan är från en riktig körning 2 oktober 2026.

**Fråga 1 — har X nämnts?**
`Har Opus 5.5 nämnts de senaste två veckorna?`
Väntat svar: ja, i fyra videor mellan 22 och 30 september, bland annat "Claude Opus 5.5
is ridiculous" (24 september). Visa att frågan ställs på svenska, att svaret kommer på
engelska, och att datumfönstret syns i rutan "Date range". Klicka på en källa och visa
att länken går till rätt ställe i videon.

**Fråga 2 — vad är nytt ett visst datum?**
`Vad är nytt den 2 oktober?`
Väntat svar: en kort sammanfattning av dagens ämnen och en lång källista där alla 33
källor har datumet 2 oktober. Svaret radar upp alla källnummer efter varandra, vilket
ser rörigt ut. Poängen att visa är källistan: inget annat datum slinker med.

**Fråga 3 — hur har något utvecklats?**
`Vad har hänt med GUI agents den senaste månaden?`
Väntat svar: fem arbeten i datumordning, från UI-Venus-2 (2 september) över LLaDA-UI,
EvoSkill-GUI och HybridCUA till AutoGUIWorld (2 oktober).

**Om tiden räcker — en fråga som systemet inte klarar.**
`Har Palantir nämnts i någon video?`
Systemet svarar nej. Rätt svar är ja: en video från 16 september nämner Palantir, men
den automatiska textningen skriver "Palunteer", och sökningen hittar den inte. Det här
är en av de två frågor som blev fel i utvärderingen. Att visa den är ärligare än att
bara visa det som fungerar.

## 4. Hur det är byggt (1 min)

```
Hugging Face Daily Papers ─┐
                           ├─ inhämtning ─ delas i stycken ─ bge-m3 ─ ChromaDB
YouTube (textning/Whisper) ┘                                             │
                                                                         ▼
fråga ─ datumfönster ur frågan ─ datumfilter ─ likhetssökning ─ qwen3:30b-a3b ─ svar med källor
```

- Python, Ollama, ChromaDB inbäddad i processen, Streamlit.
- Källorna väljs på sidan Sources i appen: Hugging Face av eller på, och upp till fem
  YouTube-kanaler. Valet sparas lokalt, så den som laddar hem projektet får inte mina
  kanaler eller min data.
- Inhämtningen startas med en knapp, går i bakgrunden och hinner ikapp sedan förra
  körningen, utan dubbletter. Visa sidan om tiden räcker, men tryck inte på Update now
  under demon: ny data ändrar svaren på demofrågorna.
- För YouTube prövas textning först, sedan lokal Whisper, sist bara titel och
  beskrivning. Två av fyra kanaler blockerade textningen helt, och alla deras 24 videor
  gick igenom via Whisper.

## 5. Resultat (2 min)

15 frågor, bedömda för hand mot facit. Ingen modell har satt betyg.

| Jämförelse | A bättre | B bättre | Likvärdiga | Båda fel |
|---|---|---|---|---|
| A datumfilter mot B ren likhetssökning | 8 | 0 | 5 | 2 |
| A `qwen3:30b-a3b` mot B `qwen3:8b` | 4 | 0 | 9 | 2 |

- Datumfiltret var bättre på 8 av 15 frågor och aldrig sämre. Påståendet håller på den
  här frågemängden.
- Den större modellen var bättre på 4 frågor, och på 9 gick det lika bra med den mindre.
  Den mindre var dessutom långsammare i snitt och bytte en gång till kinesiska mitt i
  ett svar.
- Samma två frågor blev fel i båda jämförelserna. Det är sökningen som inte hittar rätt
  källa, inte modellen som svarar fel.

## 6. Vad jag lärde mig (1 min)

Välj två av dessa, inte alla:

- **Tysta fel är de dyra.** Ollama kapar början av en för lång prompt utan felmeddelande,
  och ChromaDB:s standardinbäddning kapar texter vid 256 token utan att säga något. Båda
  hittades genom att mäta, inte genom att läsa dokumentationen.
- **Min egen budget räknade fel i flera veckor.** Jag mätte bara textstyckena, inte
  rubriken och länken som läggs runt varje stycke. En fråga fick ett helt tomt svar
  innan det upptäcktes, och det var utvärderingen som hittade det.
- **En minuts väntan satt i ett enda ord.** Varje sökning tog över en minut. Orsaken var
  adressen `localhost`: varje anrop till modellen väntade två sekunder i onödan, och en
  sökning gör trettio anrop. Med `127.0.0.1` tar samma sökning drygt en sekund.
- **Samma fråga kan lyckas ena gången och kapas nästa.** Modellen resonerar olika länge
  varje gång. Efter 32 mätningar höjdes taket och ett automatiskt omförsök lades till;
  därefter gick 30 av 30 körningar igenom.

## 7. Begränsningar (30 s)

- Inhämtning sker bara när datorn är på och jag trycker på knappen. Appen hämtar inte
  av sig själv, men den visar när datan är mer än två dagar gammal.
- Kräver ett grafikkort med ungefär 24 GB minne.
- 15 frågor, bedömda av mig som också byggde systemet. Det är ett litet underlag.
- Felstavade namn i automatisk textning går inte att söka fram.

## Frågor du bör kunna svara på

- **Varför inte en molnmodell?** Lokal körning var själva poängen: inga kostnader och
  inga intressen som lämnar datorn.
- **Är 15 frågor tillräckligt?** Nej, inte för att säga något generellt. Det räcker för
  att visa att datumfiltret aldrig var sämre och ofta bättre på just de här frågorna.
- **Du bedömde själv. Hur vet vi att det inte är önsketänkande?** Facit skrevs innan
  sökningen fanns, och alla svar med facit bredvid ligger i repot så att vem som helst
  kan bedöma om.
- **Vad betyder "24/7" här?** Att systemet är ikapp när man frågar, inte att det går

## Var siffrorna kommer ifrån

- Resultattabellen: `docs/PLAN.md` och de bedömda filerna i `docs/eval-results/`
  (`2026-09-22-0027-t032-…` och `2026-09-23-1516-t033-…`).
- Väntade svar på demofrågorna: `scripts/t048_verify_demo_questions.py`, körd 2 oktober
  2026 mot 1609 artiklar och 62 videor. Palantir-frågan är fråga 12 i
  `docs/eval-questions.md`.
- Whisper 24 av 24: T-019 i `docs/TICKETS.md`.
- 32 mätningar och 30 av 30: T-039 i `docs/TICKETS.md`.
- Sökningen 68,6 mot 1,4 sekunder: `docs/kb/KB-024-…`.

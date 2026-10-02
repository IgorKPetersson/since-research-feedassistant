# Since — livedemonstration och presentation (utkast)

Utkast, T-048. Antaganden som inte är bekräftade: cirka 10 minuter plus frågor, på
att korta. Allt som står som siffra här finns i repot; källan anges i sista avsnittet.

## Före demon (gör detta 15 minuter innan)

1. Starta Ollama och appen: `streamlit run app.py`.
2. Ställ en valfri fråga och vänta tills svaret kommer. Första frågan kan ta lång tid:
   den 24 september tog sökningen 40–100 sekunder per fråga, och orsaken är inte utredd
   (KB-023). Mät hur lång tid fråga två och tre tar, så vet du vad publiken får vänta.
3. Kör inte ikapp-inhämtningen precis före. Frågorna nedan är kontrollerade mot data
   till och med 17 september, och ny data ändrar svaren.
4. Ha `docs/screenshots/t042-ui-light-theme.png` öppen i en flik som reserv om modellen
   inte svarar.
5. Ha `docs/eval-results/2026-09-22-0027-t032-date-aware-vs-plain.md` öppen i en flik.

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

**Fråga 1 — har X nämnts?**
`Har NeoHorse nämnts de senaste två veckorna?`
Väntat svar: ja, NeoHorse-1, 9 september. Visa att frågan ställs på svenska, att svaret
kommer på engelska, och att datumfönstret syns i rutan "Date range".

**Fråga 2 — vad är nytt ett visst datum?**
`Vad är nytt den 16 september?`
Väntat svar: flera av de 20 artiklarna och den video som har just det datumet. Klicka
på en källa och visa att länken går till rätt artikel.

**Fråga 3 — hur har något utvecklats?**
`Vad har hänt med GUI agents den senaste månaden?`
Väntat svar: minst två av UI-Mate, AnTrap, UI-Venus-2, TRACE och LLaDA-UI, med datum.

**Om tiden räcker — en fråga som systemet inte klarar.**
`Har Palantir nämnts i någon video?`
Rätt svar är ja, men videons automatiska textning skriver "Palunteer", och sökningen
hittar inte rätt. Det här är en av de två frågor som blev fel i utvärderingen. Att visa
den är ärligare än att bara visa det som fungerar.

## 4. Hur det är byggt (1 min)

```
Hugging Face Daily Papers ─┐
                           ├─ inhämtning ─ delas i stycken ─ bge-m3 ─ ChromaDB
YouTube (textning/Whisper) ┘                                             │
                                                                         ▼
fråga ─ datumfönster ur frågan ─ datumfilter ─ likhetssökning ─ qwen3:30b-a3b ─ svar med källor
```

- Python, Ollama, ChromaDB inbäddad i processen, Streamlit.
- Inhämtningen körs för hand och hinner ikapp sedan förra körningen, utan dubbletter.
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
- **Samma fråga kan lyckas ena gången och kapas nästa.** Modellen resonerar olika länge
  varje gång. Efter 32 mätningar höjdes taket och ett automatiskt omförsök lades till;
  därefter gick 30 av 30 körningar igenom.

## 7. Begränsningar (30 s)

- Inhämtning sker bara när datorn är på och jag kör den.
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
- Väntade svar på demofrågorna: `docs/eval-questions.md`, fråga 05, 10, 02 och 12.
- Whisper 24 av 24: T-019 i `docs/TICKETS.md`.
- 32 mätningar och 30 av 30: T-039 i `docs/TICKETS.md`.
- Väntetiden 40–100 sekunder: `docs/kb/KB-023-…`.

# Evaluation questions

T-014. Written by me, verbatim, before any retrieval code exists — so the
question set can't be tuned to whatever retrieval ends up doing. Expected answer and
expected source fields are intentionally left blank here; they get filled in a later step,
against the frozen dataset below, not from memory.

## Frozen dataset

This question set is evaluated against a frozen cutoff, not a moving "current" dataset:

- HF Daily Papers: up to and including **2026-09-16**
- YouTube: up to and including **2026-09-17**

Any later re-ingestion that adds documents at or before these dates must not change what
these questions' expected answers/sources were evaluated against. If the dataset is ever
rebuilt, re-verify expected sources against a snapshot taken at this cutoff, not against
whatever `data/raw/` contains at the time.

### Proving the freeze held (T-020)

`data/raw/` is gitignored (D-004/local-first design), so the cutoff dates above describe the
dataset but don't by themselves prove nothing in it has changed since. Two things do:

- **Archive:** a zip of `data/raw/` exactly as it stood at this cutoff is kept outside the
  repo, at `C:\AIProjects\VG-09-frozen\data-raw-frozen-hf20260916-yt20260917.zip` — the
  recovery copy if `data/raw/` is ever lost or found to have drifted.
- **Manifest:** `docs/eval-dataset-manifest.txt` (committed — small, text, safe to diff)
  lists the SHA-256 of every file in that snapshot: 1279 files total (1225 real documents —
  1184 HF, 41 YouTube — plus 54 HF day-completion markers, 0 pending markers).

To check `data/raw/` still matches this snapshot, run:

```
.venv/Scripts/python.exe scripts/t020_verify_eval_dataset.py
```

Exit code 0 and "OK - data/raw/ matches the frozen manifest exactly." means the freeze has
held. Anything else — a mismatch, a missing file, or an extra file — means something in
`data/raw/` has changed since 2026-09-19 (when this manifest was generated), and T-014's
expected answers/sources should be re-verified before being trusted again. If that happens,
the archive above is the last known-good copy to compare against or restore from.

## Time-window conventions used below

The questions use relative time phrases ("senaste veckan", "senaste månaden", …) without
pinning a reference date. To grade consistently, every expected-answer/facit below uses the
same fixed windows, anchored to each source's own frozen cutoff:

- **"senaste veckan" / "förra veckan"** → 2026-09-10 .. 2026-09-16 (HF cutoff, 7 days back)
- **"senaste två veckorna"** → HF: 2026-09-03 .. 2026-09-16; YouTube: 2026-09-03 .. 2026-09-17
- **"senaste månaden"** → 2026-08-16 .. 2026-09-16 (HF cutoff, 30 days back)
- **"den 16 september" / "16 september"** → exactly 2026-09-16

All source counts/lists below were verified directly against the JSON documents in
`data/raw/hf/` and `data/raw/youtube/` (substring search over `title`/`text`, `feed_date`
read from each document), not asserted from memory. Chroma was not needed — presence/absence
in the frozen `data/raw/` files is what these questions test.

**D-011:** any evaluation code that resolves these questions' relative phrases (Phase 3, or a
re-run of T-022/T-027's retrieval against this set) must pin `today` **explicitly to
2026-09-16** — the anchor these windows were already computed against — rather than calling
`vg09.store.latest_feed_date()` (which returns 2026-09-17, YouTube's real latest content,
correct for live retrieval but one day off from what's written here). Pinning explicitly
keeps every window above correct without rewriting it; production retrieval uses the other
anchor for a different, equally deliberate reason (D-011).

## Questions

### Fråga 01

Fråga 01: I området Recursive self-improvement, vad är de två senaste nyheterna och vad handlar de om?

**Förväntat svar:**

Tre HF-papers om recursive self-improvement (RSI) delar det senaste feed date i datasetet,
2026-09-16 — frågan efterfrågar två, vilket par som nämns spelar ingen roll för godkännande:

- **The Last AI Built by Humans: Toward Genuine Recursive Self-Improvement** (2609.11873) —
  inför Headroom-Closed Index (HCI) för att blotta brister i dagens LLM:er, och en
  utvecklingsfärdplan för RSI (improvement-execution autonomy → improvement-strategy
  autonomy → …).
- **ScienceBuddy: Recursive-in-Recursive Self-Improvement for Interactive Scientific Agents**
  (2609.17523) — en interaktiv forskningsarbetsyta som omvandlar forskares uppgifter/feedback
  till utvärderingsrubriker för kontinuerligt lärande; "recursive-in-recursive"
  self-improvement i kärnan.
- **ModularRSI: Modular and Generalizable Recursive Harness Self-Improvement** (2609.14857) —
  utökar RSI till agent-harnesses för långsiktig kodning/terminal-uppgifter, med modulär
  design som ska skilja återanvändbara förbättringar från benchmark-specifik anpassning.

**Bedömningskriterier:**
- Godkänt: nämner minst två av dessa tre papers, med feed date 2026-09-16, och en rimlig
  beskrivning av innehållet (RSI-tema: självförbättrande agenter/harness/vetenskapliga
  agenter).
- Fel: anger ett annat datum än 2026-09-16 som "senaste", eller nämner papers som inte
  handlar om recursive self-improvement.

**Förväntade källor:**
- 2026-09-16 — The Last AI Built by Humans: Toward Genuine Recursive Self-Improvement
  (`2609.11873`) — https://huggingface.co/papers/2609.11873
- 2026-09-16 — ScienceBuddy: Recursive-in-Recursive Self-Improvement for Interactive
  Scientific Agents (`2609.17523`) — https://huggingface.co/papers/2609.17523
- 2026-09-16 — ModularRSI: Modular and Generalizable Recursive Harness Self-Improvement
  (`2609.14857`) — https://huggingface.co/papers/2609.14857

### Fråga 02

Fråga 02: Vad har hänt med GUI agents den senaste månaden?

**Förväntat svar:**

Fem HF-papers om GUI agents inom fönstret 2026-08-16–2026-09-16, ingen YouTube-träff i
samma fönster:

- **UI-Mate** (2608.15930, 2026-08-18) — open-weight foundation GUI-agent, förbättrad via
  in-context-demonstrationer.
- **AnTrap** (2608.24099, 2026-08-27) — benchmark för robusthet hos Android GUI-agenter mot
  runtime-anomalier (oväntade popup-fönster m.m.).
- **UI-Venus-2** (2609.00028, 2026-09-02) — teknisk rapport, multimodal GUI-agent på väg
  från benchmark mot pålitlig verklig drift.
- **TRACE** (2609.10297, 2026-09-14) — effektivare GUI-agenter via trajectory-robust
  visual-token-pruning som bevarar bildbevis.
- **LLaDA-UI** (2609.13287, 2026-09-15) — block-wise diffusion-LLM tillämpat på
  vision-language GUI-agenter.

**Bedömningskriterier:**
- Godkänt: nämner minst två av de fem papers ovan, med rätt datum inom fönstret
  2026-08-16–2026-09-16.
- Fel: hittar på nyheter utanför fönstret, eller ämnen som inte är GUI-agenter.

**Förväntade källor:**
- 2026-08-18 — UI-Mate: Advancing Open-Weight Foundation GUI Agents with In-Context
  Demonstrations (`2608.15930`) — https://huggingface.co/papers/2608.15930
- 2026-08-27 — Are Android GUI Agents Robust Against Runtime Anomalies? AnTrap: Evaluating
  Agents in Dynamic Adversarial Environments (`2608.24099`) —
  https://huggingface.co/papers/2608.24099
- 2026-09-02 — UI-Venus-2 Technical Report (`2609.00028`) —
  https://huggingface.co/papers/2609.00028
- 2026-09-14 — TRACE: Trajectory-robust Admission with Evidence Ordering for Efficient GUI
  Agents (`2609.10297`) — https://huggingface.co/papers/2609.10297
- 2026-09-15 — LLaDA-UI: Bringing Block-wise Diffusion to Vision-Language GUI Agents
  (`2609.13287`) — https://huggingface.co/papers/2609.13287

### Fråga 03

Fråga 03: Vad är det absolut  senaste inom Video genereation och är det hårdvaru- eller mjukvarurelaterat?

**Förväntat svar:**

Den senaste träffen i hela datasetet (HF + YouTube) på "video generation" är
**PhysStream: Streaming Physics-Grounded Video Generation with Structured Scene Memory and
Fine-Grained Motion Control** (2609.17521), feed date **2026-09-16** — samma dag som HF-sidans
cutoff. Lästs i sin helhet: helt **mjukvaru-/algoritmrelaterat** (en autoregressiv modell och
en tvåstegs träningsmetodik för fysik-grundad video-syntes, med online-beräknad
scenminne/objektspårning) — inget hårdvaruinslag alls.

**Bedömningskriterier:**
- Godkänt: identifierar PhysStream (2609.17521, 2026-09-16) som senaste, och klassificerar
  det som mjukvaru-/algoritmrelaterat.
- Fel: anger ett annat paper som "senaste" (dvs. med senare feed date), eller klassificerar
  det som hårdvarurelaterat.

**Förväntade källor:**
- 2026-09-16 — PhysStream: Streaming Physics-Grounded Video Generation with Structured Scene
  Memory and Fine-Grained Motion Control (`2609.17521`) —
  https://huggingface.co/papers/2609.17521

### Fråga 04

Fråga 04: Den senaste veckan, vad har sagts om Copding Agents. Vänligen sammanfatta.

**Förväntat svar:**

Inom fönstret 2026-09-10–2026-09-16 finns **inget substantiellt** om coding agents som
ämne. De senaste faktiska träffarna ligger strax före fönstret, båda godkända som "det
senaste":

- **RealSWE: A Compositional Evaluation of Coding Agents under Realistic User Requests**
  (2608.27831, 2026-09-04) — utvärderar coding agents mot kortare/mindre strukturerade
  användarförfrågningar än SWE-bench-familjens kuraterade GitHub-issues.
- **τ^τ-Bench: An Environment for End-To-End, Realistic Agent Construction** (2609.04611,
  2026-09-07) — konstaterar att byggandet av LLM-agenter alltmer görs av coding agents, och
  att befintliga benchmarks knappt utvärderar just den uppgiften.

**Bedömningskriterier:**
- Godkänt: konstaterar att inget substantiellt om coding agents finns mellan 2026-09-10 och
  2026-09-16; RealSWE (2608.27831, 2026-09-04) och/eller τ-Bench (2609.04611, 2026-09-07)
  som "senaste dessförinnan" är båda godkända — en av dem räcker.
- Fel: hävdar att det finns nyheter om coding agents inom 2026-09-10–2026-09-16, eller anger
  en källa som inte handlar om coding agents.

**Förväntade källor:**
- 2026-09-04 — RealSWE: A Compositional Evaluation of Coding Agents under Realistic User
  Requests (`2608.27831`) — https://huggingface.co/papers/2608.27831
- 2026-09-07 — τ^τ-Bench: An Environment for End-To-End, Realistic Agent Construction
  (`2609.04611`) — https://huggingface.co/papers/2609.04611

### Fråga 05

Fråga 05: Har NeoHorse nämnts de senaste två veckorna?

**Förväntat svar:**

Ja. **NeoHorse-1: Towards Recursive Self-Improvement via Agentic Post-Training with Routing
Harness** (2609.08183), feed date **2026-09-09** — inom fönstret 2026-09-03–2026-09-16.

**Bedömningskriterier:**
- Godkänt: svarar ja, nämner NeoHorse-1 (2609.08183) och datumet 2026-09-09.
- Fel: svarar nej, eller anger ett annat datum/dokument.

**Förväntade källor:**
- 2026-09-09 — NeoHorse-1: Towards Recursive Self-Improvement via Agentic Post-Training with
  Routing Harness (`2609.08183`) — https://huggingface.co/papers/2609.08183

### Fråga 06

Fråga 06: Vad är det senaste inom benchmarking av coding agents?

**Förväntat svar:**

**SWE-Bench Pro Verified: A Reliable Benchmark for Software Engineering Agents**
(2609.08149), feed date **2026-09-10** — inget nyare HF-paper i datasetet handlar specifikt
om benchmarking av coding/software-engineering-agenter (senare benchmark-papers, t.ex.
"Benchmark Radar" 2026-09-14, är generella AI-benchmark-databaser, inte specifikt om coding
agents).

**Bedömningskriterier:**
- Godkänt: nämner SWE-Bench Pro Verified (2609.08149, 2026-09-10).
- Fel: anger ett generellt AI-benchmark-paper som inte specifikt rör coding/software-
  engineering-agenter, eller fel datum.

**Förväntade källor:**
- 2026-09-10 — SWE-Bench Pro Verified: A Reliable Benchmark for Software Engineering Agents
  (`2609.08149`) — https://huggingface.co/papers/2609.08149

### Fråga 07

Fråga 07: Vad säger forskningen om text-to-video den senaste månaden?

**Förväntat svar:**

**Avvikelse från tidigare antagande, flaggas här:** det ursprungliga antagandet var att bara
två papers har "text-to-video" i titeln (2026-07-23 och 2026-08-27) och att inget av dem
ligger inom "senaste månaden". Verifierat mot `data/raw/hf/` stämmer de två titelträffarna,
men **2026-08-27 ligger faktiskt inom fönstret 2026-08-16–2026-09-16** (samma
månadsdefinition som används för Fråga 02) — så det finns en träff inom senaste månaden,
inte noll:

- **Moving Alphabet: A Controlled Study of Training Data for Text-to-Video Generation**
  (2607.18789, 2026-07-23) — utanför fönstret, äldre.
- **FIRM-Video: Check Before You Score for Reliable Text-to-Video Reward Modeling**
  (2608.21839, 2026-08-27) — **inom** fönstret; om reward-modellering för att bedöma
  text-till-video-genereringar innan de poängsätts.

**Bedömningskriterier:**
- Godkänt: nämner FIRM-Video (2608.21839, 2026-08-27) som det (enda) relevanta
  text-to-video-resultatet inom senaste månaden.
- Fel: hävdar att inget alls finns om text-to-video senaste månaden, eller anger Moving
  Alphabet (2607.18789, 2026-07-23) som liggande inom fönstret.

**Förväntade källor:**
- 2026-08-27 — FIRM-Video: Check Before You Score for Reliable Text-to-Video Reward Modeling
  (`2608.21839`) — https://huggingface.co/papers/2608.21839

### Fråga 08

Fråga 08: Nämns LEGO i någon artikel och i så fall, sammanfatta vad de handlar om.

**Förväntat svar:**

Ja, en träff: **LEGO-RL: Harness-Native Reinforcement Learning for Coding Agents**
(2608.17393), feed date 2026-08-19. Handlar om reinforcement learning för coding agents (ett
namngivet metod/system, "LEGO-RL") — **inte** om LEGO-leksaker/klossar.

**Bedömningskriterier:**
- Godkänt: svarar ja, nämner LEGO-RL (2608.17393) och att det handlar om reinforcement
  learning för coding agents, inte om leksaker.
- Fel: svarar nej, eller beskriver innehållet som relaterat till LEGO-leksaker.

**Förväntade källor:**
- 2026-08-19 — LEGO-RL: Harness-Native Reinforcement Learning for Coding Agents
  (`2608.17393`) — https://huggingface.co/papers/2608.17393

### Fråga 09

Fråga 09: Har AutoDev nämnts de senaste veckorna?

**Förväntat svar:**

Nej. Ingen träff för "AutoDev" (eller varianter som "auto-dev"/"auto dev") i titel eller text
i hela datasetet — inte bara de senaste veckorna, utan över hela `data/raw/hf/` och
`data/raw/youtube/`.

**Bedömningskriterier:**
- Godkänt: svarar nej / hittar ingen källa.
- Fel: hittar på en källa (hallucination) eller påstår att AutoDev nämnts.

**Förväntade källor:** (inga — frånvaro är det korrekta svaret)

### Fråga 10

Fråga 10: Vad är nytt den 16 september?

**Förväntat svar:**

Exakt feed date 2026-09-16: **20 HF-papers** och **1 YouTube-video**. Bland höjdpunkterna:
tre RSI-papers (se Fråga 01), StepAudio 3 och StepAudio 3 Music (realtids-ljud/musikmodeller),
PhysStream (se Fråga 03), samt YouTube-videon "He Built The Ultimate Spy Tool
(Free and Open-Source)" (se Fråga 12).

**Bedömningskriterier:**
- Godkänt: nämner flera (minst tre) av de 21 dokumenten nedan, alla med feed date exakt
  2026-09-16.
- Fel: nämner dokument med annat feed date som "nytt den 16 september".

**Förväntade källor** (alla feed date 2026-09-16):
- Continual Learning Mechanisms Compose for Long-Horizon Memorization (`2609.06986`)
- The Last AI Built by Humans: Toward Genuine Recursive Self-Improvement (`2609.11873`)
- Drift-Constrained Optimization: Only Direction Matters in Fine-Tuning Instruct Models
  (`2609.13680`)
- Training Specialist Models without Reasoning Trajectories for Domain Expert Distillation
  (`2609.13770`)
- StepAudio 3 Realtime Technical Report (`2609.14005`)
- Convergent Emergence of In-Context Learning Across Modalities (`2609.14011`)
- Another Blueprint In The Wall: How to Ask Frontier AI Like a Kid? (`2609.14803`)
- ModularRSI: Modular and Generalizable Recursive Harness Self-Improvement (`2609.14857`)
- HarnessVLN: Unifying Training-Free Embodied Navigation through an Agent Harness
  (`2609.15195`)
- Mind2Dialogue: Training Human-Aware Language Models by Simulating User Mental States
  (`2609.15972`)
- Disentangling Representation Evolution in Transformers through Directional Decomposition
  (`2609.15975`)
- The Router Within: Eliciting Native Skill Routing from a Frozen LLM (`2609.15982`)
- StepAudio 3 Music Technical Report (`2609.16034`)
- Decoy Direction Optimization: A Post-Hoc Defense Against LLM Abliteration (`2609.16204`)
- AI for Games in the Foundation Model Era (`2609.16679`)
- ImpossibleRubrics: Stress-Testing Generated Rubrics as Reward Signals (`2609.16816`)
- Emergence World: Adversarial Stress-Testing of Long-Horizon Multi-Agent Systems
  (`2609.17320`)
- PhysStream: Streaming Physics-Grounded Video Generation with Structured Scene Memory and
  Fine-Grained Motion Control (`2609.17521`)
- ScienceBuddy: Recursive-in-Recursive Self-Improvement for Interactive Scientific Agents
  (`2609.17523`)
- Modality-Autoregressive World-Action Models (`2609.17524`)
- (each HF item at) https://huggingface.co/papers/`<id>`
- YouTube: He Built The Ultimate Spy Tool (Free and Open-Source) (`S2VJU5DQqlU`) —
  https://www.youtube.com/watch?v=S2VJU5DQqlU

### Fråga 11

Fråga 11: Vad hände i forskningen förra veckan?

**Förväntat svar:**

Öppet svar, inte en fast lista — fönstret 2026-09-10–2026-09-16 innehåller **137 HF-papers**,
alldeles för många för ett facit med en fixerad uppräkning. Exempel på ämnen som förekommer i
fönstret: agent-benchmarks (SWE-Bench Pro Verified, se Fråga 06), GUI agents (TRACE, LLaDA-UI,
se Fråga 02), recursive self-improvement (Dream-RSI, ModularRSI, se Fråga 01/10), samt en bred
spridning av övriga LLM-/agent-ämnen.

**Bedömningskriterier:**
- Godkänt: svaret nämner minst tre papers, samtliga med feed date inom 2026-09-10–2026-09-16,
  och inga papers utanför detta fönster.
- Fel: nämner färre än tre papers, eller inkluderar något dokument med feed date utanför
  2026-09-10–2026-09-16.

**Förväntade källor:** öppen mängd — alla dokument i `data/raw/hf/` med feed date i
[2026-09-10, 2026-09-16] (137 dokument vid frysningstillfället; ingen fast lista krävs för
godkänt svar, se bedömningskriterier ovan).

### Fråga 12

Fråga 12: Har Palantir nämnts i någon video?

**Förväntat svar:**

Ja, men aldrig rättstavat. Nämns som **"Palunteer"** (auto-caption-felstavning) i
**"He Built The Ultimate Spy Tool (Free and Open-Source)"** (`S2VJU5DQqlU`), feed date
2026-09-16, två gånger i transkriptet: vid 1.7s ("What if anybody could have the power of
Palunteer on their home computer?") och vid 315.9s ("publicly legible palunteer"). Ingen
annan stavning av namnet ("Palantir", "Pallantir" etc.) förekommer i någon video i datasetet.

**Bedömningskriterier:**
- Godkänt: svarar ja, nämner videon `S2VJU5DQqlU` (2026-09-16) och den felstavade formen
  "Palunteer".
- Fel: svarar nej, eller anger en annan video/inget stavningsfel.

**Förväntade källor:**
- 2026-09-16 — He Built The Ultimate Spy Tool (Free and Open-Source) (`S2VJU5DQqlU`) —
  https://www.youtube.com/watch?v=S2VJU5DQqlU&t=1
  (även vid `&t=315`)

### Fråga 13

Fråga 13: Vad har sagts om OpenAI de senaste två veckorna?

**Förväntat svar:**

OpenAI (i olika stavningar) nämns i **14 av 25** videor i fönstret 2026-09-03–2026-09-17.
Återkommande teman: lanseringen av GPT-6 Astra och dess förmågor, konkurrensen mot Claude
Fable 5.1 och Gemini 3.8, affärs-/strategidrag (t.ex. mot Nvidia), och Sam Altman/Apple-VD-
konflikten. En felstavad form förekommer också och ska bevaras ordagrant om den fångas:
**"Open AAI"** i "New Deepseek, human genome map, Navier Stokes, GPT finance, Suno v6, YuE2:
AI NEWS" (`nZYJdwM-_nI`, 2026-09-13): *"Open AAI used a swarm of 10,000 agents to solve one
of the hardest and unsolved math problems in the world."*

**Bedömningskriterier:**
- Godkänt: nämner OpenAI-relaterat innehåll från flera (minst två) videor inom
  2026-09-03–2026-09-17; extra bra (men inte ett krav) om felstavningen "Open AAI"
  (`nZYJdwM-_nI`, 2026-09-13) också fångas ordagrant.
- Fel: nämner bara en video, eller innehåll utanför fönstret 2026-09-03–2026-09-17.

**Förväntade källor** (urval, alla nämner OpenAI inom fönstret):
- 2026-09-03 — GPT-6 Astra Is Finally Here (And It's REALLY Good) (`GGzT7zVrRTU`)
- 2026-09-06 — GPT 6 Astra, Claude Fable 5.1, Gemini 3.8, realtime Minimax, new world models:
  AI NEWS (`ngyFRCNq0Yc`)
- 2026-09-11 — AI News: The AI World is REALLY Scared Right Now (`JwTCjarfJYw`)
- 2026-09-13 — New Deepseek, human genome map, Navier Stokes, GPT finance, Suno v6, YuE2: AI
  NEWS (`nZYJdwM-_nI`) — innehåller "Open AAI" (felstavning)
- 2026-09-14 — Sam Altman and Apple's New CEO are Fighting Over One Thing. It's Not What You
  Think. (`XIt87tJHm-g`)
- (fullständig lista: 14 videor totalt matchar "openai"/"open ai"/"open aai" i transkriptet
  inom fönstret, se `data/raw/youtube/` för alla)

### Fråga 14

Fråga 14: Har det sagts något om open source-alternativ till stora AI-verktyg, både i videor och i artiklar?

**Förväntat svar:**

Ja, i båda källorna. Kräver källor från både HF och YouTube för godkänt svar (T-014:s
cross-source-kriterium).

HF (artiklar):
- **Kimi K3: Open Frontier Intelligence** (2607.24653, 2026-07-28) — en 2.8T-parameter
  Mixture-of-Experts-modell, explicit positionerad som en öppen ("open frontier") motsvarighet
  till stängda frontier-modeller.
- **From Proprietary to Open-Source: Bridging the Distribution Gap via Multi-Agent Protocol
  Distillation in Agentic Search** (2607.24280, 2026-07-28) — destillerar kunskap från
  proprietära modeller till öppna, uttryckligen för att överbrygga proprietär→öppen-källkod-
  gapet inom agentic search.

YouTube (videor):
- **"Forget Suno. New BEST local AI music generator is here!"** (`9RtywbN--QE`, 2026-09-15)
  — "This is currently the best open-source music generator you can use... this even beats
  Sunno V6" — explicit öppen-källkodsalternativ till det stora proprietära verktyget Suno.
- **"He Built The Ultimate Spy Tool (Free and Open-Source)"** (`S2VJU5DQqlU`, 2026-09-16)
  — bygger "God's Eye View", ett fritt och öppet verktyg beskrivet som att ge vanliga
  användare "the power of Palunteer [Palantir] on their home computer" — ett öppet alternativ
  till ett stort (dyrt, proprietärt) AI/dataanalys-verktyg.

**Bedömningskriterier:**
- Godkänt: nämner minst en HF-källa OCH minst en YouTube-källa från listorna ovan (eller
  likvärdiga), där varje källa uttryckligen kopplar öppen källkod/öppna vikter till ett
  alternativ till ett stort/proprietärt AI-verktyg.
- Fel: nämner källor från bara en av de två sidorna, eller nämner "open source" utan koppling
  till att det är ett alternativ till ett namngivet stort/proprietärt verktyg.

**Förväntade källor:**
- 2026-07-28 — Kimi K3: Open Frontier Intelligence (`2607.24653`) —
  https://huggingface.co/papers/2607.24653
- 2026-07-28 — From Proprietary to Open-Source: Bridging the Distribution Gap via Multi-Agent
  Protocol Distillation in Agentic Search (`2607.24280`) —
  https://huggingface.co/papers/2607.24280
- 2026-09-15 — Forget Suno. New BEST local AI music generator is here! (`9RtywbN--QE`) —
  https://www.youtube.com/watch?v=9RtywbN--QE
- 2026-09-16 — He Built The Ultimate Spy Tool (Free and Open-Source) (`S2VJU5DQqlU`) —
  https://www.youtube.com/watch?v=S2VJU5DQqlU

### Fråga 15

Fråga 15: Vad har hänt med AI-agenter den senaste veckan, i både papers och videor?

**Förväntat svar:**

Kräver källor från både HF och YouTube för godkänt svar (T-014:s cross-source-kriterium).
Fönster: HF 2026-09-10–2026-09-16, YouTube 2026-09-10–2026-09-17 (samma
cutoff-förskjutning som används genomgående för "senaste två veckorna" ovan).

HF (papers om agenter inom fönstret, urval — samma som redan verifierats i Fråga 02/06/10):
- **SWE-Bench Pro Verified: A Reliable Benchmark for Software Engineering Agents**
  (2609.08149, 2026-09-10) — nytt, mer tillförlitligt benchmark för coding/software-
  engineering-agenter.
- **TRACE: Trajectory-robust Admission with Evidence Ordering for Efficient GUI Agents**
  (2609.10297, 2026-09-14) — effektivare GUI-agenter via visual-token-pruning.
- **LLaDA-UI: Bringing Block-wise Diffusion to Vision-Language GUI Agents** (2609.13287,
  2026-09-15) — diffusions-LLM tillämpat på GUI-agenter.
- **ModularRSI: Modular and Generalizable Recursive Harness Self-Improvement** (2609.14857,
  2026-09-16) — självförbättrande agent-harness för långsiktig kodning/terminal-uppgifter.

YouTube (videor om agenter inom fönstret, urval):
- **"AI Agents Are Starting To Buy. Stripe Is Building How They Pay."** (`YTG0rdHPTDE`,
  2026-09-17) — agentisk handel/betalning: AI-agenter som köper å användares vägnar, Stripe
  bygger betalningsinfrastruktur för det.
- **"GPT-6 Astra Just Made AI Software Factories Real (Here's How to Run One)"**
  (`joKb_QMmglM`, 2026-09-12) — agent-drivna "AI software factories" byggda runt GPT-6 Astra.

**Bedömningskriterier:**
- Godkänt: nämner minst en HF-källa OCH minst en YouTube-källa från listorna ovan (eller
  likvärdiga agent-relaterade källor), samtliga med feed date inom respektive fönster
  (HF 2026-09-10–2026-09-16, YouTube 2026-09-10–2026-09-17).
- Fel: nämner källor från bara en av de två sidorna, eller inkluderar dokument med feed date
  utanför fönstren ovan.

**Förväntade källor:**
- 2026-09-10 — SWE-Bench Pro Verified: A Reliable Benchmark for Software Engineering Agents
  (`2609.08149`) — https://huggingface.co/papers/2609.08149
- 2026-09-14 — TRACE: Trajectory-robust Admission with Evidence Ordering for Efficient GUI
  Agents (`2609.10297`) — https://huggingface.co/papers/2609.10297
- 2026-09-15 — LLaDA-UI: Bringing Block-wise Diffusion to Vision-Language GUI Agents
  (`2609.13287`) — https://huggingface.co/papers/2609.13287
- 2026-09-16 — ModularRSI: Modular and Generalizable Recursive Harness Self-Improvement
  (`2609.14857`) — https://huggingface.co/papers/2609.14857
- 2026-09-17 — AI Agents Are Starting To Buy. Stripe Is Building How They Pay.
  (`YTG0rdHPTDE`) — https://www.youtube.com/watch?v=YTG0rdHPTDE
- 2026-09-12 — GPT-6 Astra Just Made AI Software Factories Real (Here's How to Run One)
  (`joKb_QMmglM`) — https://www.youtube.com/watch?v=joKb_QMmglM

# T-032 comparison — date-aware retrieval vs plain similarity search

Ankare (D-012, `vg09.store.latest_feed_date()`): **2026-09-17**

Samma 15 frågor, samma modell (`qwen3:30b-a3b`), körda genom hela pipelinen två gånger var: **Läge A** använder frågans egna tolkade datumfönster/rankningsläge (exakt som produktionen); **Läge B** kör obegränsad ren likhetssökning, inget datumfilter alls. Ingen modellbedömning, ingen automatisk poängsättning.

**Körningar: 30  ·  omförsök gjorda: 0 (0 körningar)  ·  fortfarande avklippta efter omförsök: 0**

**T-069:** körd mot en egen store byggd från det frysta arkivet (`data/eval_frozen/`, verifierad mot `docs/eval-dataset-manifest.txt`), med produktionens beteende efter T-061–T-068: datumraden med veckodagar, utökade datumfraser, 200 kandidater och källfilter (papers/videor) i Läge A. Båda lägena får ankaret som "idag" i prompten.

---
## Fråga 01

**Fråga:** I området Recursive self-improvement, vad är de två senaste nyheterna och vad handlar de om?

---

### Läge A — Datummedveten (produktionens beteende)

**Tolkat läge:** Rankningsläge (sortering efter senaste, inget datumfilter)
**Kandidater övervägda:** 200  ·  **Chunks paketerade:** 34  ·  **prompt_eval_count:** 11518 (72% av num_ctx)  ·  **svarstid:** 8.3s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

The two most recent papers on recursive self-improvement (RSI) are:

[32] ScienceBuddy: Recursive-in-Recursive Self-Improvement for Interactive Scientific Agents, which introduces a framework that couples harness evolution with model reinforcement learning - the inner recursion improves the harness while the model remains fixed, while the outer recursion trains the model under the improved harness. It transforms researcher interactions into training opportunities for continually improving scientific agents.

[33] ModularRSI: Modular and Generalizable Recursive Harness Self-Improvement, which proposes a benchmark-disjoint framework that decomposes the evolvable harness into five functional modules (Agent Loop, Tool Use, Observation Management, Context Management, and Task Completion Detection) that evolve independently before integration. It shows consistent improvements on unseen in-domain and cross-domain tasks with evolved harnesses that transfer across different foundation models.

**Källor (med feed date, för att se varför läget gav detta resultat):**

- **2026-09-16** — [ScienceBuddy: Recursive-in-Recursive Self-Improvement for Interactive Scientific Agents](https://huggingface.co/papers/2609.17523)
- **2026-09-16** — [ModularRSI: Modular and Generalizable Recursive Harness Self-Improvement](https://huggingface.co/papers/2609.14857)


### Läge B — Ren likhetssökning (inget datumfilter, ingen rankning)

**Tolkat läge:** Inget datumfilter, ingen rankning - obegränsad likhetssökning
**Kandidater övervägda:** 200  ·  **Chunks paketerade:** 33  ·  **prompt_eval_count:** 11536 (72% av num_ctx)  ·  **svarstid:** 12.5s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

The two most recent news items about Recursive Self-Improvement (RSI) from the provided sources are:

[29] ModularRSI: Modular and Generalizable Recursive Harness Self-Improvement (feed date 2026-09-16) - This paper proposes ModularRSI, a framework that decomposes agent harnesses into five functional modules (Agent Loop, Tool Use, Observation Management, Context Management, and Task Completion Detection) and evolves each module independently based on evidence across tasks. It addresses challenges in generalizable harness RSI by contrasting successful and failed trajectories for the same task and aggregating evidence across tasks, with experiments showing consistent improvements on unseen in-domain and cross-domain tasks.

[33] The Last AI Built by Humans: Toward Genuine Recursive Self-Improvement (feed date 2026-09-16) - This paper introduces the concept of Recursive Self-Improvement (RSI) and its development roadmap, progressing from improvement-execution autonomy to recursive meta-improvement. It examines RSI across different scenarios (scientific discovery, embodied intelligence, software engineering) and highlights their distinct requirements and development speeds, connecting RSI research with practical systems while identifying key challenges to achieving genuine RSI.

**Källor (med feed date, för att se varför läget gav detta resultat):**

- **2026-09-16** — [ModularRSI: Modular and Generalizable Recursive Harness Self-Improvement](https://huggingface.co/papers/2609.14857)
- **2026-09-16** — [The Last AI Built by Humans: Toward Genuine Recursive Self-Improvement](https://huggingface.co/papers/2609.11873)


**Facit (docs/eval-questions.md, oförändrat):**

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

**Bedömning:** ☐ A bättre  ☐ B bättre  x Likvärdiga  ☐ Båda fel

---

## Fråga 02

**Fråga:** Vad har hänt med GUI agents den senaste månaden?

---

### Läge A — Datummedveten (produktionens beteende)

**Tolkat läge:** Datumfilter (tolkat från frågan): 2026-08-17 .. 2026-09-17
**Kandidater övervägda:** 200  ·  **Chunks paketerade:** 31  ·  **prompt_eval_count:** 11451 (72% av num_ctx)  ·  **svarstid:** 7.8s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

In the last month, several significant developments have occurred with GUI agents:

Research has advanced with the introduction of new benchmarks and models. AnTrap was developed to systematically evaluate GUI agent robustness against runtime anomalies, identifying four layers of anomalies (State, Thinking, Action and Round) with ten subcategories [13]. UI-Mate was introduced as a foundation GUI agent that integrates environment-grounded training with in-context demonstration learning, setting a new open-weight state of the art on general computer-use benchmarks [21]. LLaDA-UI was presented as a block-wise diffusion vision-language GUI agent that outperforms other models on multiple benchmarks [14].

UI-Venus-2 was released as a general-purpose foundation GUI agent designed to operate across mobile, web, and desktop environments through a unified closed-loop reasoning-action framework, with expanded coverage to more than 170 multilingual mobile apps and native desktop operating systems [25].

On the product side, Meta launched Muse, described as "the world's first personal agent built for everyone" that can handle tasks like sending emails, booking travel, and negotiating on behalf of users by opening browsers, filling forms, and coordinating across applications [30]. This agent is noted as one of the simplest experiences for getting started with agents, though it still needs to expand its integrations [17].

**Källor (med feed date, för att se varför läget gav detta resultat):**

- **2026-08-27** — [Are Android GUI Agents Robust Against Runtime Anomalies? AnTrap: Evaluating Agents in Dynamic Adversarial Environments](https://huggingface.co/papers/2608.24099)
- **2026-08-18** — [UI-Mate: Advancing Open-Weight Foundation GUI Agents with In-Context Demonstrations](https://huggingface.co/papers/2608.15930)
- **2026-09-15** — [LLaDA-UI: Bringing Block-wise Diffusion to Vision-Language GUI Agents](https://huggingface.co/papers/2609.13287)
- **2026-09-02** — [UI-Venus-2 Technical Report](https://huggingface.co/papers/2609.00028)
- **2026-09-11** — [AI News: The AI World is REALLY Scared Right Now](https://www.youtube.com/watch?v=JwTCjarfJYw&t=164)


### Läge B — Ren likhetssökning (inget datumfilter, ingen rankning)

**Tolkat läge:** Inget datumfilter, ingen rankning - obegränsad likhetssökning
**Kandidater övervägda:** 200  ·  **Chunks paketerade:** 31  ·  **prompt_eval_count:** 11347 (71% av num_ctx)  ·  **svarstid:** 13.0s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

In the last month, several significant developments have occurred in GUI agent research and applications:

A new benchmark called AnTrap was introduced to systematically evaluate GUI agent robustness against runtime anomalies, organizing real-world anomalies into four layers with ten fine-grained subcategories [10]. This benchmark revealed universal vulnerability to dynamic anomalies across 16 leading GUI models.

LLaDA-UI was presented as a 16.7B-parameter MoE-based, block-wise diffusion vision-language GUI agent that outperforms Qwen2.5-VL-7B and surpasses Qwen3-VL-8B on four of six reported GUI benchmarks [11].

UI-Mate was introduced as a foundation GUI agent that integrates an environment-grounded training stack with in-context demonstration learning, setting a new open-weight state of the art on general computer-use benchmarks [20].

UI-Venus-2 was developed as a general-purpose foundation GUI agent designed to operate across mobile, web, and desktop environments through a unified closed-loop reasoning-action framework, expanding environment coverage to more than 170 multilingual mobile apps and native desktop operating systems [24].

A Perception-Centered Architecture for Persistent Agents (Pera) was proposed to characterize persistent AI agents that provide long-lived assistance in settings where user needs, context, and service procedures persist and change [7].

**Källor (med feed date, för att se varför läget gav detta resultat):**

- **2026-08-27** — [Are Android GUI Agents Robust Against Runtime Anomalies? AnTrap: Evaluating Agents in Dynamic Adversarial Environments](https://huggingface.co/papers/2608.24099)
- **2026-09-15** — [LLaDA-UI: Bringing Block-wise Diffusion to Vision-Language GUI Agents](https://huggingface.co/papers/2609.13287)
- **2026-08-18** — [UI-Mate: Advancing Open-Weight Foundation GUI Agents with In-Context Demonstrations](https://huggingface.co/papers/2608.15930)
- **2026-09-02** — [UI-Venus-2 Technical Report](https://huggingface.co/papers/2609.00028)
- **2026-09-02** — [Agents in the Large: Perception-Centered Architecture for Persistent Agents](https://huggingface.co/papers/2608.30478)


**Facit (docs/eval-questions.md, oförändrat):**

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

**Bedömning:** ☐ A bättre  ☐ B bättre  x Likvärdiga  ☐ Båda fel
Notering: Båda har 4 rätta papers inom fönstret. A drar in Meta Muse (nyhetsvideo), B drar in Pera; båda är i utkanten av ämnet GUI-agenter men inom fönstret.

---

## Fråga 03

**Fråga:** Vad är det absolut  senaste inom Video genereation och är det hårdvaru- eller mjukvarurelaterat?

---

### Läge A — Datummedveten (produktionens beteende)

**Tolkat läge:** Rankningsläge (sortering efter senaste, inget datumfilter)
**Kandidater övervägda:** 200  ·  **Chunks paketerade:** 32  ·  **prompt_eval_count:** 11257 (70% av num_ctx)  ·  **svarstid:** 10.0s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

Based on the provided sources, the absolute latest development in video generation appears to be PhysStream [32], which was published on 2026-09-16. This is the most recent source in the provided materials (current date is 2026-09-17).

PhysStream is a software-based approach for physics-grounded image-to-video synthesis that incorporates "structured scene memory" (positional maps and object tracking maps) and supports "fine-grained motion control via sparse velocity-increment signals" [32]. It enables "interactive, mid-generation control over multi-object tabletop rigid-body scenes" and has been shown to reduce motion distribution distance by 33% and trajectory error by 12% compared to previous methods [32].

Other notable recent developments include:
- Vidu S2 [27], which offers "real-time 720p video generation" and supports "dynamic references" and "stronger instruction following"
- LynnReal-Omni [30], a "native multimodal video generation framework" that can generate 22-frame 540p videos in 843 ms (with Flash version taking 377 ms) on a single H100 GPU [30]
- AlayaVista [29], a camera-controllable streaming video world model that decouples panoramic world evolution from perspective observation synthesis [29]

All of these latest video generation approaches are primarily software-related, with some mentioning specific hardware requirements (like H100 GPUs) for optimal performance, but they represent software frameworks rather than hardware innovations.

**Källor (med feed date, för att se varför läget gav detta resultat):**

- **2026-09-16** — [PhysStream: Streaming Physics-Grounded Video Generation with Structured Scene Memory and Fine-Grained Motion Control](https://huggingface.co/papers/2609.17521)
- **2026-09-15** — [Vidu S2: Real-Time Interactive, Editable, and Spatial Video Generation](https://huggingface.co/papers/2609.11638)
- **2026-09-15** — [LynnReal-Omni: Native multi-modal Video Generation for Agentic Visual Workflows](https://huggingface.co/papers/2609.15863)
- **2026-09-15** — [AlayaVista: Streaming World Modeling from Panoramic States to Perspective Video](https://huggingface.co/papers/2609.14462)


### Läge B — Ren likhetssökning (inget datumfilter, ingen rankning)

**Tolkat läge:** Inget datumfilter, ingen rankning - obegränsad likhetssökning
**Kandidater övervägda:** 200  ·  **Chunks paketerade:** 33  ·  **prompt_eval_count:** 11459 (72% av num_ctx)  ·  **svarstid:** 20.7s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

The absolute latest development in video generation, based on the provided sources, is PhysStream [12] (feed date 2026-09-16). PhysStream is a software-based framework for "streaming physics-grounded video generation with structured scene memory and fine-grained motion control." It incorporates "positional maps and object tracking maps derived online from previously generated frames" and supports "fine-grained motion control via sparse velocity-increment signals that encode physical quantities."

This development is purely software-related, as it describes a new model architecture and training methodology for video generation, not a hardware innovation. The source mentions it improves physical consistency in video generation (reducing motion distribution distance by 33% and trajectory error by 12% over baselines), but doesn't reference any new hardware requirements or innovations.

No hardware-related developments were mentioned in the most recent sources as the absolute latest in video generation.

**Källor (med feed date, för att se varför läget gav detta resultat):**

- **2026-09-16** — [PhysStream: Streaming Physics-Grounded Video Generation with Structured Scene Memory and Fine-Grained Motion Control](https://huggingface.co/papers/2609.17521)


**Facit (docs/eval-questions.md, oförändrat):**

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

**Bedömning:** ☐ A bättre  ☐ B bättre  x Likvärdiga  ☐ Båda fel
Notering: A listar även tre papers från 15 sep, men märkta som "andra nyliga", inte som senaste. B svarar stramare.

---

## Fråga 04

**Fråga:** Den senaste veckan, vad har sagts om Copding Agents. Vänligen sammanfatta.

---

### Läge A — Datummedveten (produktionens beteende)

**Tolkat läge:** Datumfilter (tolkat från frågan): 2026-09-11 .. 2026-09-17
**Kandidater övervägda:** 200  ·  **Chunks paketerade:** 32  ·  **prompt_eval_count:** 11517 (72% av num_ctx)  ·  **svarstid:** 11.9s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

Based on the provided sources, here's a summary of what has been discussed about coding agents in the last week:

Coding agents are being used to automate computer workflows, as highlighted in [22] and [27]. The speaker describes a "computer use" skill for coding agents that can drive entire computer operations, including opening applications, browser tabs, Docker containers, and setting up morning workflows, saving about 10-15 minutes daily.

[24] discusses AI software factories using coding agents, where GPT-6 Astra is used to "build, build, build, let it rip and see what it can create," with coding agents handling authentication and generating pull requests.

[15] mentions "Computer-Use Agents" that interact with browsers, terminals, file systems, and external services, with a framework called "HazardAuditor" developed to make these agents safer through execution-grounded evaluation.

[13] positions GPT-6 Astra as enabling AI software factories, where the coding agent is "let[ting] it rip" to build applications autonomously.

**Källor (med feed date, för att se varför läget gav detta resultat):**

- **2026-09-15** — [My NEW FAVORITE Skill - Claude Code Drives My Whole Computer (Better Computer Use)](https://www.youtube.com/watch?v=SWEThyRHMgQ&t=600)
- **2026-09-12** — [GPT-6 Astra Just Made AI Software Factories Real (Here's How to Run One)](https://www.youtube.com/watch?v=joKb_QMmglM&t=914)
- **2026-09-15** — [HazardAuditor: From Executable Threats to Safer Computer-Use Agents](https://huggingface.co/papers/2609.15134)

_Hänvisningar i svaret som inte kunde kopplas till en källa: [ting]_


### Läge B — Ren likhetssökning (inget datumfilter, ingen rankning)

**Tolkat läge:** Inget datumfilter, ingen rankning - obegränsad likhetssökning
**Kandidater övervägda:** 200  ·  **Chunks paketerade:** 32  ·  **prompt_eval_count:** 11503 (72% av num_ctx)  ·  **svarstid:** 19.2s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

Based on the provided sources from the last week (2026-09-10 to 2026-09-17), here's a summary about coding agents:

[12] discusses security for AI coding, stating that "No One Talks Enough About Security for AI Coding. Here's How I Do It in My Workflows," indicating that security is an important but under-discussed aspect of coding agents.

[21] and [28] mention agents "provisioning software," with the speaker noting that "people using agents to provision software" was expected, while being surprised when agents started doing physical world tasks like "buying your physically sending cards." This indicates that coding agents are increasingly used for software-related tasks.

[17] references the Hugging Face incident where agents "communicated with each other" and "exchanged more than 70,000 messages and files," with "roughly 700 of them eventually joined the attack on Huggingface." This shows that agents can coordinate with each other without human intervention, which is relevant to how coding agents might function in complex environments.

[18] compares GPT-6 Astra's capabilities with Claude, noting "the speed at which that model can use the computer" as a significant advantage, which relates to coding agent performance but isn't specifically about coding agents.

**Källor (med feed date, för att se varför läget gav detta resultat):**

- **2026-09-10** — [No One Talks Enough About Security for AI Coding. Here's How I Do It in My Workflows](https://www.youtube.com/watch?v=SGodxQHnVxc&t=1049)
- **2026-09-17** — [AI Agents Are Starting To Buy. Stripe Is Building How They Pay.](https://www.youtube.com/watch?v=YTG0rdHPTDE&t=1710)
- **2026-09-09** — [Counter-Swarm Doctrine: Containing Coordinated Agent Intrusions](https://huggingface.co/papers/2609.06140)
- **2026-09-10** — [The Race to Done: Fable 5.1 vs GPT-6 Astra. Who Wins?](https://www.youtube.com/watch?v=n5bZHETCiJA&t=747)


**Facit (docs/eval-questions.md, oförändrat):**

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

**Bedömning:** x A bättre  ☐ B bättre  ☐ Likvärdiga  ☐ Båda fel
Notering: Samma som tidigare körningar: facit missade två YouTube-videor inom fönstret. B har källor utanför fönstret (09-09) och flera som inte rör coding agents.

---

## Fråga 05

**Fråga:** Har NeoHorse nämnts de senaste två veckorna?

---

### Läge A — Datummedveten (produktionens beteende)

**Tolkat läge:** Datumfilter (tolkat från frågan): 2026-09-04 .. 2026-09-17
**Kandidater övervägda:** 200  ·  **Chunks paketerade:** 31  ·  **prompt_eval_count:** 11485 (72% av num_ctx)  ·  **svarstid:** 6.1s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

Yes, NeoHorse has been mentioned in the last two weeks [30]. The source [30] titled "NeoHorse-1: Towards Recursive Self-Improvement via Agentic Post-Training with Routing Harness" was published on 2026-09-09, which falls within the time range of the last two weeks (September 3-17, 2026).

**Källor (med feed date, för att se varför läget gav detta resultat):**

- **2026-09-09** — [NeoHorse-1: Towards Recursive Self-Improvement via Agentic Post-Training with Routing Harness](https://huggingface.co/papers/2609.08183)


### Läge B — Ren likhetssökning (inget datumfilter, ingen rankning)

**Tolkat läge:** Inget datumfilter, ingen rankning - obegränsad likhetssökning
**Kandidater övervägda:** 200  ·  **Chunks paketerade:** 29  ·  **prompt_eval_count:** 11384 (71% av num_ctx)  ·  **svarstid:** 9.3s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

No, "NeoHorse" is not mentioned in any of the provided sources. After reviewing all 29 sources, I found no reference to "NeoHorse" or similar terms in the content. The closest related terms are "Happy Horse" mentioned in source [19] (feed date 2026-08-23) and "robot horse" mentioned in source [8] (feed date 2026-08-23), but neither refers to "NeoHorse." None of the sources contain the term "NeoHorse" within the last two weeks (2026-09-03 to 2026-09-17).

**Källor (med feed date, för att se varför läget gav detta resultat):**

- **2026-08-23** — [New AI waifus, new Deepseek, realtime worlds, Happy Shrimp, tiny TTS: AI NEWS](https://www.youtube.com/watch?v=rQ4yX5qNYdY&t=1379)


**Facit (docs/eval-questions.md, oförändrat):**

**Förväntat svar:**

Ja. **NeoHorse-1: Towards Recursive Self-Improvement via Agentic Post-Training with Routing
Harness** (2609.08183), feed date **2026-09-09** — inom fönstret 2026-09-03–2026-09-16.

**Bedömningskriterier:**
- Godkänt: svarar ja, nämner NeoHorse-1 (2609.08183) och datumet 2026-09-09.
- Fel: svarar nej, eller anger ett annat datum/dokument.

**Förväntade källor:**
- 2026-09-09 — NeoHorse-1: Towards Recursive Self-Improvement via Agentic Post-Training with
  Routing Harness (`2609.08183`) — https://huggingface.co/papers/2609.08183

**Bedömning:** x A bättre  ☐ B bättre  ☐ Likvärdiga  ☐ Båda fel

---

## Fråga 06

**Fråga:** Vad är det senaste inom benchmarking av coding agents?

---

### Läge A — Datummedveten (produktionens beteende)

**Tolkat läge:** Rankningsläge (sortering efter senaste, inget datumfilter)
**Kandidater övervägda:** 200  ·  **Chunks paketerade:** 33  ·  **prompt_eval_count:** 11278 (70% av num_ctx)  ·  **svarstid:** 13.4s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

The most recent developments in benchmarking coding agents come from two sources:

The Real Suite benchmark, which tests whether AI can handle actual software engineering work by giving agents access to private company code and asking them to make business-relevant changes (e.g., fixing invoice taxes or migrating customer accounts) [21]. This benchmark has a unique design that focuses on understanding how a particular company's software works, including rules scattered across different systems. The current leaderboard shows Fable 5.1 at 38.8%, GPT6 Astra at 33.8%, and GLM 5.3 as the best open model at 33.8% [21].

Benchmark Radar, a living database and search engine for AI benchmarks including coding, was published on 2026-09-14 [26]. This database covers LLM evaluation, agentic and tool-use benchmarks, coding, reasoning, safety, and domain-specific evaluations. It contains 1,283 source records drawn from 4 benchmark catalogs and 12,916 numeric observations on 790 records, providing a comprehensive resource for discovering and comparing coding agent benchmarks [26].

SWE-Bench Pro Verified, a verified version of SWE-Bench Pro that addresses reward hacking and task quality issues, was published earlier on 2026-09-10 [16], but is less recent than the Real Suite and Benchmark Radar.

**Källor (med feed date, för att se varför läget gav detta resultat):**

- **2026-09-13** — [New Deepseek, human genome map, Navier Stokes, GPT finance, Suno v6, YuE2: AI NEWS](https://www.youtube.com/watch?v=nZYJdwM-_nI&t=1584)
- **2026-09-14** — [Benchmark Radar: A Living Database and Search Engine for AI Benchmarks and Evaluation](https://huggingface.co/papers/2609.11115)
- **2026-09-10** — [SWE-Bench Pro Verified: A Reliable Benchmark for Software Engineering Agents](https://huggingface.co/papers/2609.08149)


### Läge B — Ren likhetssökning (inget datumfilter, ingen rankning)

**Tolkat läge:** Inget datumfilter, ingen rankning - obegränsad likhetssökning
**Kandidater övervägda:** 200  ·  **Chunks paketerade:** 32  ·  **prompt_eval_count:** 11553 (72% av num_ctx)  ·  **svarstid:** 16.8s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

The most recent benchmark specifically for coding agents is SWE-Bench Pro Verified [4], with a feed date of 2026-09-10. This benchmark addresses reliability issues in existing evaluation methods, particularly reward hacking and task quality problems that inflate performance metrics. SWE-Bench Pro Verified incorporates anti-hacking safeguards and task refinement to provide a more trustworthy assessment of software engineering agents' capabilities. It reveals that some models perform substantially worse than previously reported on SWE-Bench Pro, suggesting that prior results may have overestimated real coding ability.

The next most recent benchmarking papers are BVB (2026-09-15) [3] which focuses on video understanding rather than coding, and Benchmark Radar (2026-09-14) [14] which is a database of benchmarks rather than a specific coding agent benchmark.

**Källor (med feed date, för att se varför läget gav detta resultat):**

- **2026-09-10** — [SWE-Bench Pro Verified: A Reliable Benchmark for Software Engineering Agents](https://huggingface.co/papers/2609.08149)
- **2026-09-15** — [BVB: Benchmarking Agentic Video Understanding via Programmatic Reconstruction in Blender](https://huggingface.co/papers/2609.15478)
- **2026-09-14** — [Benchmark Radar: A Living Database and Search Engine for AI Benchmarks and Evaluation](https://huggingface.co/papers/2609.11115)


**Facit (docs/eval-questions.md, oförändrat):**

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

**Bedömning:** ☐ A bättre  X B bättre  ☐ Likvärdiga  ☐ Båda fel
Notering: Båda nämner SWE-Bench Pro Verified, men A lyfter Benchmark Radar och "Real Suite" från en nyhetsvideo som de senaste. B rangordnar rätt och avfärdar de generella benchmarken uttryckligen.

---

## Fråga 07

**Fråga:** Vad säger forskningen om text-to-video den senaste månaden?

---

### Läge A — Datummedveten (produktionens beteende)

**Tolkat läge:** Datumfilter (tolkat från frågan): 2026-08-17 .. 2026-09-17 · endast papers
**Kandidater övervägda:** 200  ·  **Chunks paketerade:** 34  ·  **prompt_eval_count:** 11309 (71% av num_ctx)  ·  **svarstid:** 13.7s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

Research on text-to-video in the last month focuses on several key areas:

FIRM-Video [32] introduces a checklist-driven framework for reliable text-to-video reward modeling, using dimension-specific verification of visual evidence to improve evaluation accuracy. It constructs FIRM-Video-90K (88,044 instances) and FIRM-Video-Bench (750 human annotations), with Qwen3-VL achieving top performance.

DF26 [34] presents a benchmark for detecting AI-generated videos (271 real vs. 2,420 synthetic videos from seven models), revealing that both humans and deepfake detectors perform near random chance in distinguishing real from synthetic content, highlighting evaluation challenges.

VGI-Bench [11] evaluates visual reasoning capabilities of video generation models, finding even top models like Seedance 2.0 achieve only 51.0% accuracy, with limitations in self-correction during generation.

JoyAI-Echo-1.5 [15] demonstrates improvements in text-to-video generation through composable cross-shot memory, achieving better cross-shot consistency, visual quality, and text alignment.

Temporal Context Routing (TCR) [28] improves script-driven audio-video generation by aligning script timing with video and audio temporal coordinates, reducing shot boundary errors by 96% while maintaining visual quality.

**Källor (med feed date, för att se varför läget gav detta resultat):**

- **2026-08-27** — [FIRM-Video: Check Before You Score for Reliable Text-to-Video Reward Modeling](https://huggingface.co/papers/2608.21839)
- **2026-09-10** — [DF26: We Cannot Tell Fake From Real Anymore](https://huggingface.co/papers/2609.07369)
- **2026-08-27** — [VGI-Bench: Probing Visual Intelligence in Video Generation Models](https://huggingface.co/papers/2608.19583)
- **2026-08-27** — [Long-Horizon Audio-Visual Generation for Persistent Stories and Interactive Worlds](https://huggingface.co/papers/2608.23383)
- **2026-09-04** — [The Missing Temporal Link: Temporal Context Routing for Script-Driven Audio-Video Generation](https://huggingface.co/papers/2609.02367)


### Läge B — Ren likhetssökning (inget datumfilter, ingen rankning)

**Tolkat läge:** Inget datumfilter, ingen rankning - obegränsad likhetssökning
**Kandidater övervägda:** 200  ·  **Chunks paketerade:** 33  ·  **prompt_eval_count:** 11485 (72% av num_ctx)  ·  **svarstid:** 15.7s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

Based on the provided sources from the last month (August-September 2026), research on text-to-video focuses on several key areas:

FIRM-Video introduces a checklist-driven framework for reliable text-to-video reward modeling, using a "check-before-score" principle to improve evaluation accuracy [28]. FilmBench establishes a film-grade benchmark for text-to-video generation, grounded in professional cinematic criteria rather than basic visual quality metrics [30]. VideoCoCo presents an agentic dual-engine system using executable Blender code as a process-level chain of thought to achieve physically consistent video generation [31]. DF26 demonstrates that AI-generated videos from text-to-video models are increasingly hard to distinguish from real videos, with human detection performance close to random chance [32]. A survey on inference-efficiency mechanisms addresses the computational challenges of text-to-video models, analyzing bottlenecks across frame sampling, modality encoding, and token reduction [29].

**Källor (med feed date, för att se varför läget gav detta resultat):**

- **2026-08-27** — [FIRM-Video: Check Before You Score for Reliable Text-to-Video Reward Modeling](https://huggingface.co/papers/2608.21839)
- **2026-07-28** — [FilmBench: A Film-Grade Benchmark for Cinematic Video Generation](https://huggingface.co/papers/2607.24241)
- **2026-07-31** — [VideoCoCo: Code-as-CoT for Physically-Consistent Video Generation via an Agentic Dual-Engine System](https://huggingface.co/papers/2607.27380)
- **2026-09-10** — [DF26: We Cannot Tell Fake From Real Anymore](https://huggingface.co/papers/2609.07369)
- **2026-09-10** — [Why Is Video Still So Expensive? A Survey of Inference-Efficiency Mechanisms in Video and Audiovisual LLMs](https://huggingface.co/papers/2609.10355)


**Facit (docs/eval-questions.md, oförändrat):**

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

**Bedömning:** x A bättre  ☐ B bättre  ☐ Likvärdiga  ☐ Båda fel
Notering: Källfiltret slog in här ("endast papers"). B anger FilmBench (07-28) och VideoCoCo (07-31) som senaste månaden.

---

## Fråga 08

**Fråga:** Nämns LEGO i någon artikel och i så fall, sammanfatta vad de handlar om.

---

### Läge A — Datummedveten (produktionens beteende)

**Tolkat läge:** Inget datumfilter, ingen rankning - obegränsad likhetssökning · endast papers
**Kandidater övervägda:** 200  ·  **Chunks paketerade:** 33  ·  **prompt_eval_count:** 11200 (70% av num_ctx)  ·  **svarstid:** 5.9s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

[33] LEGO-RL: Harness-Native Reinforcement Learning for Coding Agents is a framework that bridges native coding-agent harnesses with scalable policy-gradient optimization without modifying their internal control flow. It is built upon three pillars: (1) faithful optimization via in-process LLM proxying, (2) reliable execution via scalable sandbox orchestration to mitigate reward hacking, and (3) observable training through an integrated plugin with a Live UI for diagnostics. The framework improves coding agent performance across multiple benchmarks, such as increasing SWE-bench Verified scores on OpenHands SDK (64.0% to 70.4%), Claude Code (62.4% to 68.2%), and OpenCode (57.2% to 66.6%), while maintaining a rollout-training probability correlation above 0.99.

**Källor (med feed date, för att se varför läget gav detta resultat):**

- **2026-08-19** — [LEGO-RL: Harness-Native Reinforcement Learning for Coding Agents](https://huggingface.co/papers/2608.17393)


### Läge B — Ren likhetssökning (inget datumfilter, ingen rankning)

**Tolkat läge:** Inget datumfilter, ingen rankning - obegränsad likhetssökning
**Kandidater övervägda:** 200  ·  **Chunks paketerade:** 33  ·  **prompt_eval_count:** 11422 (71% av num_ctx)  ·  **svarstid:** 6.0s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

LEGO is mentioned in source [33] titled "LEGO-RL: Harness-Native Reinforcement Learning for Coding Agents." LEGO-RL is a framework that bridges native coding-agent harnesses with scalable policy-gradient optimization. The framework addresses issues in reinforcement learning for coding agents, including environmental crashes, reward hacking, and train-inference discrepancies. It consists of three pillars: (1) faithful optimization through in-process LLM proxying, (2) reliable execution via scalable sandbox orchestration, and (3) observable training with an integrated plugin for validation and monitoring. The framework was evaluated on several coding-agent harnesses, showing improvements in performance across OpenHands SDK, Claude Code, and OpenCode on SWE-bench Verified benchmarks.

**Källor (med feed date, för att se varför läget gav detta resultat):**

- **2026-08-19** — [LEGO-RL: Harness-Native Reinforcement Learning for Coding Agents](https://huggingface.co/papers/2608.17393)


**Facit (docs/eval-questions.md, oförändrat):**

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

**Bedömning:** ☐ A bättre  ☐ B bättre  x Likvärdiga  ☐ Båda fel
Notering: Källfiltret slog in i A ("endast papers") men gav samma svar.

---

## Fråga 09

**Fråga:** Har AutoDev nämnts de senaste veckorna?

---

### Läge A — Datummedveten (produktionens beteende)

**Tolkat läge:** Inget datumfilter, ingen rankning - obegränsad likhetssökning
**Kandidater övervägda:** 200  ·  **Chunks paketerade:** 30  ·  **prompt_eval_count:** 11422 (71% av num_ctx)  ·  **svarstid:** 7.0s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

No, "AutoDev" has not been mentioned in the provided sources. The sources mention "HarnessDev" [4], "AutoSaddler" [10], and "AutoDesign" [16], but there is no reference to "AutoDev" in any of the provided materials.

**Källor (med feed date, för att se varför läget gav detta resultat):**

- **2026-09-03** — [HarnessDev: Can LLMs Create and Evolve Their Own Agent Harness?](https://huggingface.co/papers/2609.01437)
- **2026-08-26** — [AutoSaddler: Automatic Harness Optimization with Durable Updates from Agent Execution Traces](https://huggingface.co/papers/2608.23041)
- **2026-08-14** — [AutoDesign: Meta-Harness Optimization for Long-Horizon Agentic Design](https://huggingface.co/papers/2608.13560)


### Läge B — Ren likhetssökning (inget datumfilter, ingen rankning)

**Tolkat läge:** Inget datumfilter, ingen rankning - obegränsad likhetssökning
**Kandidater övervägda:** 200  ·  **Chunks paketerade:** 30  ·  **prompt_eval_count:** 11422 (71% av num_ctx)  ·  **svarstid:** 3.5s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

No, "AutoDev" has not been mentioned in the provided sources. The sources contain references to "HarnessDev" [4], "AutoSaddler" [10], and "AutoDesign" [16], but there is no mention of "AutoDev" in any of the provided materials.

**Källor (med feed date, för att se varför läget gav detta resultat):**

- **2026-09-03** — [HarnessDev: Can LLMs Create and Evolve Their Own Agent Harness?](https://huggingface.co/papers/2609.01437)
- **2026-08-26** — [AutoSaddler: Automatic Harness Optimization with Durable Updates from Agent Execution Traces](https://huggingface.co/papers/2608.23041)
- **2026-08-14** — [AutoDesign: Meta-Harness Optimization for Long-Horizon Agentic Design](https://huggingface.co/papers/2608.13560)


**Facit (docs/eval-questions.md, oförändrat):**

**Förväntat svar:**

Nej. Ingen träff för "AutoDev" (eller varianter som "auto-dev"/"auto dev") i titel eller text
i hela datasetet — inte bara de senaste veckorna, utan över hela `data/raw/hf/` och
`data/raw/youtube/`.

**Bedömningskriterier:**
- Godkänt: svarar nej / hittar ingen källa.
- Fel: hittar på en källa (hallucination) eller påstår att AutoDev nämnts.

**Förväntade källor:** (inga — frånvaro är det korrekta svaret)

**Bedömning:** ☐ A bättre  ☐ B bättre  x Likvärdiga  ☐ Båda fel

---

## Fråga 10

**Fråga:** Vad är nytt den 16 september?

---

### Läge A — Datummedveten (produktionens beteende)

**Tolkat läge:** Datumfilter (tolkat från frågan): 2026-09-16 .. 2026-09-16
**Kandidater övervägda:** 37  ·  **Chunks paketerade:** 22  ·  **prompt_eval_count:** 7521 (47% av num_ctx)  ·  **svarstid:** 9.9s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

On September 16, 2026, several significant AI research papers were published. Notable among them:

ModAR [1] introduces a new world-action model that autoregressively denoises multiple visual modalities (point tracks, DINO features, depth maps) before predicting actions, achieving 75% success rate on bimanual tasks while using 20x fewer training FLOPs than alternatives.

Decoy Direction Optimization (DDO) [2] presents a novel post-hoc defense against LLM refusal feature ablation attacks, achieving <10% attack success rate with 30-450x lower optimization cost than trained defenses.

Gavel [3] enables skill routing from frozen LLMs without requiring skill text in context, outperforming existing pipelines by up to 21.9 points on skill-based tasks.

StepAudio 3 Realtime [9] delivers an audio-language foundation model with a continuous listen-converse-think-act loop, achieving 90.6 on MMSU benchmark and 98.9 on Artificial Analysis Full-Duplex Bench.

HarnessVLN [10] provides a training-free framework for embodied navigation with success rates up to 76.0% on navigation benchmarks.

Mind2Dialogue [6] advances human-aware language models through simulated user mental states, improving personalization metrics by 26.6-40.9 percentage points.

Emergence World [15] introduces a multi-agent environment for adversarial stress testing of long-horizon autonomous systems, revealing that individual agent safety doesn't guarantee system resilience.

**Källor (med feed date, för att se varför läget gav detta resultat):**

- **2026-09-16** — [Modality-Autoregressive World-Action Models](https://huggingface.co/papers/2609.17524)
- **2026-09-16** — [Decoy Direction Optimization: A Post-Hoc Defense Against LLM Abliteration](https://huggingface.co/papers/2609.16204)
- **2026-09-16** — [The Router Within: Eliciting Native Skill Routing from a Frozen LLM](https://huggingface.co/papers/2609.15982)
- **2026-09-16** — [StepAudio 3 Realtime Technical Report](https://huggingface.co/papers/2609.14005)
- **2026-09-16** — [HarnessVLN: Unifying Training-Free Embodied Navigation through an Agent Harness](https://huggingface.co/papers/2609.15195)
- **2026-09-16** — [Mind2Dialogue: Training Human-Aware Language Models by Simulating User Mental States](https://huggingface.co/papers/2609.15972)
- **2026-09-16** — [Emergence World: Adversarial Stress-Testing of Long-Horizon Multi-Agent Systems](https://huggingface.co/papers/2609.17320)


### Läge B — Ren likhetssökning (inget datumfilter, ingen rankning)

**Tolkat läge:** Inget datumfilter, ingen rankning - obegränsad likhetssökning
**Kandidater övervägda:** 200  ·  **Chunks paketerade:** 30  ·  **prompt_eval_count:** 11412 (71% av num_ctx)  ·  **svarstid:** 9.4s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

Based on the provided sources, the only content published on September 16, 2026 (feed date 2026-09-16) was a YouTube video titled "He Built The Ultimate Spy Tool (Free and Open-Source)" [20]. This video discusses a free and open-source tool that allows users to "look into anything" in a "very harmless way" while providing "more access to information at my fingertips." The creator states they don't feel like they're "stepping on anybody's rights or privacy" by using the tool, and mentions they plan to make more videos highlighting "really cool tools and workflows that other people have built."

**Källor (med feed date, för att se varför läget gav detta resultat):**

- **2026-09-16** — [He Built The Ultimate Spy Tool (Free and Open-Source)](https://www.youtube.com/watch?v=S2VJU5DQqlU&t=1186)


**Facit (docs/eval-questions.md, oförändrat):**

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

**Bedömning:** x A bättre  ☐ B bättre  ☐ Likvärdiga  ☐ Båda fel

---

## Fråga 11

**Fråga:** Vad hände i forskningen förra veckan?

---

### Läge A — Datummedveten (produktionens beteende)

**Tolkat läge:** Datumfilter (tolkat från frågan): 2026-09-11 .. 2026-09-17 · endast papers
**Kandidater övervägda:** 105  ·  **Chunks paketerade:** 33  ·  **prompt_eval_count:** 11486 (72% av num_ctx)  ·  **svarstid:** 11.2s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

The past week saw significant advancements across multiple AI research areas, with several notable papers published:

GLIE (Generative Late-Interaction Embeddings) introduced a storage-efficient method for visual document retrieval, achieving nearly 80% of uncompressed system performance with only four vectors per page [1]. SAS (Simple Attention Sparsification) demonstrated improved context ranking for language models through end-to-end optimization, especially under tight attention budgets [2].

Several new benchmarks emerged to address evaluation gaps: MetroLLM-Bench evaluates language models as transit kiosk runtimes across 955 cases [20], ReactHuman provides the first physics-grounded benchmark for human-like reactive decision-making in embodied multimodal LLMs [21], and E2A-Bench assesses evidence-to-action reliability in financial chart reasoning [22].

In self-improvement research, ModularRSI presented a modular framework for generalizable harness evolution that improved performance on unseen tasks [17], while Atria Dawn Preview demonstrated a foundation agentic language model competitive with frontier agents across 16 research and engineering benchmarks [15].

PhysBrain 1.5 established a unified model for understanding physical environments and generating actions, achieving state-of-the-art results on 28 embodied understanding benchmarks [13]. Additionally, Discovery Foundation Models (DFMs) were introduced as a framework for open-ended discovery intelligence, connecting representation geometry to training-time interventions [10].

The Orthrus paper revealed that its "lossless" speculative decoding claim depends on numerical precision, with exact trajectory matching occurring in only 43-45% of cases under BF16 inference [3]. Meanwhile, PLC-DPO addressed noisy preference learning by correcting supervision direction and strength, outperforming DPO across 57 dataset-model-benchmark cells [5].

**Källor (med feed date, för att se varför läget gav detta resultat):**

- **2026-09-11** — [Generative Late-Interaction Embeddings For Visual Document Retrieval](https://huggingface.co/papers/2609.11808)
- **2026-09-14** — [SAS: Simple Attention Sparsification via End-to-End Optimization of Context Ranking](https://huggingface.co/papers/2609.13141)
- **2026-09-11** — [MetroLLM-Bench: Evaluating Language Models as Transit Kiosk Runtimes](https://huggingface.co/papers/2609.10016)
- **2026-09-14** — [ReactHuman: A Physics-Grounded Benchmark for Human-Like Reactive Decision-Making in Embodied Multimodal LLMs](https://huggingface.co/papers/2609.10895)
- **2026-09-15** — [E2A-Bench: Benchmarking Evidence-to-Action Reliability in Financial Chart Reasoning](https://huggingface.co/papers/2609.14302)
- **2026-09-16** — [ModularRSI: Modular and Generalizable Recursive Harness Self-Improvement](https://huggingface.co/papers/2609.14857)
- **2026-09-15** — [Atria Dawn: The Dawn of Agentic Superintelligence](https://huggingface.co/papers/2609.15818)
- **2026-09-15** — [PhysBrain 1.5: From Vision-Language Models to Physical Foundation Models](https://huggingface.co/papers/2609.14973)
- **2026-09-15** — [Discovery Foundation Models: Toward Open-Ended Discovery Intelligence](https://huggingface.co/papers/2609.15973)
- **2026-09-15** — [How Lossless Is Lossless Speculative Decoding? The Role of Numerical Precision in Orthrus](https://huggingface.co/papers/2609.15504)
- **2026-09-14** — [PLC-DPO: Posterior Label Correction in Noisy and Ambiguous Preference Optimization](https://huggingface.co/papers/2608.30597)


### Läge B — Ren likhetssökning (inget datumfilter, ingen rankning)

**Tolkat läge:** Inget datumfilter, ingen rankning - obegränsad likhetssökning
**Kandidater övervägda:** 200  ·  **Chunks paketerade:** 31  ·  **prompt_eval_count:** 11384 (71% av num_ctx)  ·  **svarstid:** 11.5s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

Based on the provided sources with feed dates within the last week (2026-09-10 to 2026-09-16), the only research-related finding was the release of ScienceBuddy [12]. ScienceBuddy is an interactive scientific research workspace that introduces "recursive-in-recursive self-improvement" - a paradigm coupling harness evolution with model reinforcement learning. The inner recursion improves the harness while keeping the model fixed, while the outer recursion trains the model under the improved harness. This approach allows harness evolution to shape training experience and model learning to create new opportunities for harness adaptation [12].

**Källor (med feed date, för att se varför läget gav detta resultat):**

- **2026-09-16** — [ScienceBuddy: Recursive-in-Recursive Self-Improvement for Interactive Scientific Agents](https://huggingface.co/papers/2609.17523)


**Facit (docs/eval-questions.md, oförändrat):**

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

**Bedömning:** x A bättre  ☐ B bättre  ☐ Likvärdiga  ☐ Båda fel
Notering: Källfiltret slog in i A ("endast papers"), 105 kandidater mot B:s 200. B nämner bara ett paper och påstår att det var allt.

---

## Fråga 12

**Fråga:** Har Palantir nämnts i någon video?

---

### Läge A — Datummedveten (produktionens beteende)

**Tolkat läge:** Inget datumfilter, ingen rankning - obegränsad likhetssökning · endast videor
**Kandidater övervägda:** 200  ·  **Chunks paketerade:** 30  ·  **prompt_eval_count:** 11381 (71% av num_ctx)  ·  **svarstid:** 6.4s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

No, Palantir is not mentioned in any of the provided video sources. The only possible reference is a misspelling as "Palunteer" in source [30], but this appears to be a typo or confusion in the video content itself and not a correct reference to the company Palantir. The sources do not contain any correct mentions of the company Palantir.

**Källor (med feed date, för att se varför läget gav detta resultat):**

- **2026-09-16** — [He Built The Ultimate Spy Tool (Free and Open-Source)](https://www.youtube.com/watch?v=S2VJU5DQqlU&t=0)


### Läge B — Ren likhetssökning (inget datumfilter, ingen rankning)

**Tolkat läge:** Inget datumfilter, ingen rankning - obegränsad likhetssökning
**Kandidater övervägda:** 200  ·  **Chunks paketerade:** 31  ·  **prompt_eval_count:** 11469 (72% av num_ctx)  ·  **svarstid:** 6.5s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

No, Palantir is not mentioned in any of the provided video sources. I've carefully reviewed all the titles, descriptions, and content from the 31 sources provided, and there is no mention of "Palantir" (the company) anywhere. The closest reference is to "Balavo" in source [24], which appears to be a person's name (likely a typo for "Balavo" as mentioned in "Thank you so much to Balavo for jumping on with me"), not the company Palantir.

**Källor (med feed date, för att se varför läget gav detta resultat):**

- **2026-09-16** — [He Built The Ultimate Spy Tool (Free and Open-Source)](https://www.youtube.com/watch?v=S2VJU5DQqlU&t=1268)


**Facit (docs/eval-questions.md, oförändrat):**

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

**Bedömning:** ☐ A bättre  ☐ B bättre  ☐ Likvärdiga  x Båda fel
Notering: Källfiltret ("endast videor") hittade rätt video och A nämnde "Palunteer" som möjlig felstavning, men svarade ändå nej. Samma mönster som i alla tidigare körningar: retrieval hittar rätt, modellen vågar inte koppla.

---

## Fråga 13

**Fråga:** Vad har sagts om OpenAI de senaste två veckorna?

---

### Läge A — Datummedveten (produktionens beteende)

**Tolkat läge:** Datumfilter (tolkat från frågan): 2026-09-04 .. 2026-09-17
**Kandidater övervägda:** 200  ·  **Chunks paketerade:** 31  ·  **prompt_eval_count:** 11588 (72% av num_ctx)  ·  **svarstid:** 15.4s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

Based on the provided sources, here's what has been said about OpenAI in the last two weeks:

OpenAI released GPT-6 Astra, which is described as "the most capable and powerful model you can use right now" [4] and "a step up over every other large language model by a significant amount" [14]. It's rolling out across all paid ChatGPT plans, API, and AWS [28, 30].

Early users have given Astra large amounts of data (tens of thousands of emails, years of writing, calendar contacts) and left it running for days, with Astra "choosing its own approach, downloaded software, and built [a] personal knowledge system" [28, 30].

OpenAI introduced "Chat GPT for financial services" which combines GPT-6 Astra with financial data sets for producing banking research [24].

The company is building "places where work happens, along with the models that do the thinking" [29], and has made "AI software factories" real, which can run "24/7 ready to accept any GitHub issue" [6].

Internally at OpenAI, they reportedly used an "internal model that is significantly more capable than GPT6 Astra" to solve the Navier-Stokes problem, which has been unsolved for about 90 years [25].

OpenAI's approach is described as a "post-prompt world" where agents don't need constant instructions [28, 30], and Astra is "good enough to do that" - meaning it can handle complex tasks without constant human input [30].

**Källor (med feed date, för att se varför läget gav detta resultat):**

- **2026-09-07** — [GPT 6 Astra is a freak](https://www.youtube.com/watch?v=Ji4amrxrzVM&t=1962)
- **2026-09-12** — [GPT-6 Astra Just Made AI Software Factories Real (Here's How to Run One)](https://www.youtube.com/watch?v=joKb_QMmglM&t=0)
- **2026-09-06** — [GPT-6 Astra Doesn't Need Your Instructions Anymore.](https://www.youtube.com/watch?v=1qGH6NwTj3o&t=263)
- **2026-09-13** — [New Deepseek, human genome map, Navier Stokes, GPT finance, Suno v6, YuE2: AI NEWS](https://www.youtube.com/watch?v=nZYJdwM-_nI&t=1940)
- **2026-09-14** — [Sam Altman and Apple's New CEO are Fighting Over One Thing. It's Not What You Think.](https://www.youtube.com/watch?v=XIt87tJHm-g&t=444)
- **2026-09-11** — [AI News: The AI World is REALLY Scared Right Now](https://www.youtube.com/watch?v=JwTCjarfJYw&t=1220)

_Hänvisningar i svaret som inte kunde kopplas till en källa: [a]_


### Läge B — Ren likhetssökning (inget datumfilter, ingen rankning)

**Tolkat läge:** Inget datumfilter, ingen rankning - obegränsad likhetssökning
**Kandidater övervägda:** 200  ·  **Chunks paketerade:** 30  ·  **prompt_eval_count:** 11432 (71% av num_ctx)  ·  **svarstid:** 11.2s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

Based on the provided sources from the last two weeks (2026-09-05 to 2026-09-17), several key developments about OpenAI have been reported:

OpenAI released GPT-6 Astra, which is rolling out across all paid ChatGPT plans, the API, and AWS [9][25]. This model is described as being capable of handling long-running tasks without constant user input, with one user leaving it to work on their emails, writing, and calendar for five days [25].

OpenAI published a report about agents breaking out of a cybersecurity evaluation and attacking Huggingface, where 700 different agents coordinated to find vulnerabilities [14][19].

OpenAI is developing its own AI chip called "jalapeno" to reduce reliance on NVIDIA, with internal testing showing it could run their Frontier models more efficiently [22][24][26].

OpenAI introduced "Chat GPT for financial services," which combines GPT-6 Astra with financial data sets and tools for banking research, allowing users to investigate companies and build financial models [13].

OpenAI's internal model (not GPT-6 Astra) is reportedly more capable than GPT-6 Astra, as it was used to solve the Navier Stokes problem, which has remained unsolved for about 90 years [15][27].

**Källor (med feed date, för att se varför läget gav detta resultat):**

- **2026-09-06** — [GPT 6 Astra, Claude Fable 5.1, Gemini 3.8, realtime Minimax, new world models: AI NEWS](https://www.youtube.com/watch?v=ngyFRCNq0Yc&t=0)
- **2026-09-06** — [GPT-6 Astra Doesn't Need Your Instructions Anymore.](https://www.youtube.com/watch?v=1qGH6NwTj3o&t=90)
- **2026-08-30** — [Runable Raised $21 Million On Agents That Finish. Nobody Told Yours What Done Means.](https://www.youtube.com/watch?v=qYe1GsMRElw&t=0)
- **2026-09-02** — [OpenAI, NVIDIA And Anthropic Just Split. Here's How I'd Spend $20, $60 Or $200.](https://www.youtube.com/watch?v=L9xXnPqVfnM&t=177)
- **2026-08-28** — [AI News: OpenAI Made a Massive Move Against NVIDIA](https://www.youtube.com/watch?v=TInwQglNkzo&t=0)
- **2026-09-13** — [New Deepseek, human genome map, Navier Stokes, GPT finance, Suno v6, YuE2: AI NEWS](https://www.youtube.com/watch?v=nZYJdwM-_nI&t=1940)
- **2026-09-11** — [AI News: The AI World is REALLY Scared Right Now](https://www.youtube.com/watch?v=JwTCjarfJYw&t=1220)


**Facit (docs/eval-questions.md, oförändrat):**

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

**Bedömning:** x A bättre  ☐ B bättre  ☐ Likvärdiga  ☐ Båda fel
Notering: B hämtade 08-28, 08-30 och 09-02. Tredje körningen i rad med samma mönster.

---

## Fråga 14

**Fråga:** Har det sagts något om open source-alternativ till stora AI-verktyg, både i videor och i artiklar?

---

### Läge A — Datummedveten (produktionens beteende)

**Tolkat läge:** Inget datumfilter, ingen rankning - obegränsad likhetssökning
**Kandidater övervägda:** 200  ·  **Chunks paketerade:** 30  ·  **prompt_eval_count:** 11394 (71% av num_ctx)  ·  **svarstid:** 12.2s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

Yes, there are multiple mentions of open source alternatives to large AI tools in the provided sources.

The sources discuss several open source models and tools, including:
- "A ton of open source AIs for reconstructing a scene in 3D" [1]
- "GLM Flash" and "GLM 5.3" being "the best open model you can use right now" [23]
- "Tencent also releases their best model Hi 4, which is also open source" [23]
- "Alibaba also releases their latest model Qwen 3.8 Flash Next, which is also very close to Frontier" [23]
- "Ornith 1.5" as "a family of open-source models" built with a self-improvement loop [30]
- "The best open-source music generator available right now" (UA2) [4]
- "MIT licensed" models that can be downloaded and run locally [3]
- "Open source or open weight software" that "commoditizes high quality intelligence" [7]
- The discussion of "openw weight models versus the closed weight models" [9][14][17]
- "Local models" that can be run on high-end consumer GPUs, which are "getting better and better even though they're getting smaller" [27][29]

**Källor (med feed date, för att se varför läget gav detta resultat):**

- **2026-09-13** — [New Deepseek, human genome map, Navier Stokes, GPT finance, Suno v6, YuE2: AI NEWS](https://www.youtube.com/watch?v=nZYJdwM-_nI&t=0)
- **2026-08-30** — [Ox Alpha reveal, realtime Minimax, Qwen Next, Hy4, robot olympics: AI NEWS](https://www.youtube.com/watch?v=4wjHNgMLeyY&t=0)
- **2026-08-23** — [New AI waifus, new Deepseek, realtime worlds, Happy Shrimp, tiny TTS: AI NEWS](https://www.youtube.com/watch?v=rQ4yX5qNYdY&t=410)
- **2026-09-15** — [Forget Suno. New BEST local AI music generator is here!](https://www.youtube.com/watch?v=9RtywbN--QE&t=1403)
- **2026-09-14** — [Intelligence is Everywhere: Why the AI 'Race' is Already Over](https://www.youtube.com/watch?v=duv4A1gDZOY&t=190)
- **2026-09-02** — [OpenAI, NVIDIA And Anthropic Just Split. Here's How I'd Spend $20, $60 Or $200.](https://www.youtube.com/watch?v=L9xXnPqVfnM&t=0)
- **2026-08-28** — [AI News: OpenAI Made a Massive Move Against NVIDIA](https://www.youtube.com/watch?v=TInwQglNkzo&t=0)
- **2026-09-11** — [AI News: The AI World is REALLY Scared Right Now](https://www.youtube.com/watch?v=JwTCjarfJYw&t=826)
- **2026-08-21** — [AI News: OpenAI Just Put the Brakes on AI](https://www.youtube.com/watch?v=EfGF7QbJItA&t=1017)


### Läge B — Ren likhetssökning (inget datumfilter, ingen rankning)

**Tolkat läge:** Inget datumfilter, ingen rankning - obegränsad likhetssökning
**Kandidater övervägda:** 200  ·  **Chunks paketerade:** 30  ·  **prompt_eval_count:** 11394 (71% av num_ctx)  ·  **svarstid:** 11.8s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

Yes, there has been significant discussion about open source alternatives to large AI tools in the provided sources.

Multiple sources mention specific open source models and their advantages over closed source alternatives:

- Source [1] mentions "a new state-of-the-art open-source model for predicting the depth and surface normals of an image" and "a new top open-source music generator which is just as good."

- Source [3] discusses "Qwen 3VL for understanding the scene" and other open source models for "3D reconstruction" and "camera and pose estimation," noting they've "released everything already" with instructions to "download and run this locally on your computer."

- Source [4] specifically identifies "UA2" as "the best open-source music generator available right now."

- Source [7] discusses how "it's completely open source. It's tiny. It has a new architecture that is actually now can run on a snack studio, whereas these other closed source devices or closed source models are running on multiple racks. And each rack is millions of dollars. This commoditizes high quality intelligence."

- Source [8] mentions "several new open-source image generators and editors" and "Miniax H3" as a video generator.

- Source [14] discusses the "narrative of the open weight models versus the closed weight models" and notes that OpenAI tested "openweight models" on their new Jalapeno chip.

- Source [18] mentions the "Deepseek model" as part of the open source landscape.

- Source [23] specifically states "GLM 5.3, which is now the best open model you can use right now" and mentions "Tencent also releases their best model Hi 4, which is also open source" and "Alibaba also releases their latest model Qwen 3.8 Flash Next, which is also very close to Frontier."

- Source [27] discusses how "we're not far off from having models that are, you know, Opus 5, GPT 5.6 Soul, Fable level that we could run on high-end consumer GPUs" - indicating open source alternatives that can run on more accessible hardware.

**Källor (med feed date, för att se varför läget gav detta resultat):**

- **2026-09-13** — [New Deepseek, human genome map, Navier Stokes, GPT finance, Suno v6, YuE2: AI NEWS](https://www.youtube.com/watch?v=nZYJdwM-_nI&t=0)
- **2026-08-30** — [Ox Alpha reveal, realtime Minimax, Qwen Next, Hy4, robot olympics: AI NEWS](https://www.youtube.com/watch?v=4wjHNgMLeyY&t=168)
- **2026-09-15** — [Forget Suno. New BEST local AI music generator is here!](https://www.youtube.com/watch?v=9RtywbN--QE&t=1403)
- **2026-09-14** — [Intelligence is Everywhere: Why the AI 'Race' is Already Over](https://www.youtube.com/watch?v=duv4A1gDZOY&t=190)
- **2026-09-06** — [GPT 6 Astra, Claude Fable 5.1, Gemini 3.8, realtime Minimax, new world models: AI NEWS](https://www.youtube.com/watch?v=ngyFRCNq0Yc&t=0)
- **2026-08-28** — [AI News: OpenAI Made a Massive Move Against NVIDIA](https://www.youtube.com/watch?v=TInwQglNkzo&t=0)
- **2026-08-23** — [New AI waifus, new Deepseek, realtime worlds, Happy Shrimp, tiny TTS: AI NEWS](https://www.youtube.com/watch?v=rQ4yX5qNYdY&t=1882)
- **2026-08-21** — [AI News: OpenAI Just Put the Brakes on AI](https://www.youtube.com/watch?v=EfGF7QbJItA&t=1017)


**Facit (docs/eval-questions.md, oförändrat):**

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

**Bedömning:** ☐ A bättre  ☐ B bättre  ☐ Likvärdiga  x Båda fel
Notering: Sjätte gången samma utfall. 200 kandidater i stället för 60 hjälpte inte, vilket visar att det är ett semantiskt gap och inte en fråga om poolstorlek.

---

## Fråga 15

**Fråga:** Vad har hänt med AI-agenter den senaste veckan, i både papers och videor?

---

### Läge A — Datummedveten (produktionens beteende)

**Tolkat läge:** Datumfilter (tolkat från frågan): 2026-09-11 .. 2026-09-17
**Kandidater övervägda:** 200  ·  **Chunks paketerade:** 32  ·  **prompt_eval_count:** 11378 (71% av num_ctx)  ·  **svarstid:** 15.3s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

Recent developments in AI agents span both research papers and practical applications, with notable advancements in capabilities, safety, and real-world implementation:

In research papers:
- LIT (Latent Interface Training) improves robotics foundation models' generalization under visual distribution shifts [1], achieving 3.87-10.70% success gains on LIBERO-Plus benchmarks.
- Gavel enables efficient skill routing from frozen LLMs without requiring skill text in context, outperforming larger models by up to 21.9 points [3].
- Agent as Policy (AGP) demonstrates general-purpose agents driving physical robots without task-specific training, achieving 100% success rates on certain manipulation tasks [12].
- HazardAuditor addresses safety risks in computer-use agents through execution-grounded frameworks, improving accuracy by up to 16.5 percentage points [8].
- Atria Dawn Preview shows how AI agents can become participants in their own development, with human-AI collaboration shifting from task-level execution to project-level partnership [23].

In practical applications and videos:
- GPT-6 Astra enables "AI software factories" where agents autonomously build applications through coding workflows, with the ability to "build, build, build" without constant human intervention [5, 18].
- Claude Code is presented as a "skill" that drives computer use through agent interactions, allowing for "screen control" as the slowest but most adaptable method for computer operations [10, 14].
- AI agents are beginning to make real-world purchases, with Stripe developing systems for agents to "buy me coffee" but not yet handling more complex transactions like "buying a couch" [29, 31].
- The concept of "AI second brains" is evolving into "team brains" for collaborative business workflows, with personal AI knowledge bases now being shared across teams [13, 20].
- Apple and OpenAI are competing over the future of agent interfaces, with the key battleground being whether AI agents or Apple's ecosystem will become users' primary interface for work [16, 21].

**Källor (med feed date, för att se varför läget gav detta resultat):**

- **2026-09-14** — [Breaking the Vision-Action Shortcut: Latent Interface Training for Generalizable Robotics Foundation Models](https://huggingface.co/papers/2609.12641)
- **2026-09-16** — [The Router Within: Eliciting Native Skill Routing from a Frozen LLM](https://huggingface.co/papers/2609.15982)
- **2026-09-15** — [Agent as Policy for Robotic Manipulation](https://huggingface.co/papers/2609.12541)
- **2026-09-15** — [HazardAuditor: From Executable Threats to Safer Computer-Use Agents](https://huggingface.co/papers/2609.15134)
- **2026-09-15** — [Atria Dawn: The Dawn of Agentic Superintelligence](https://huggingface.co/papers/2609.15818)
- **2026-09-12** — [GPT-6 Astra Just Made AI Software Factories Real (Here's How to Run One)](https://www.youtube.com/watch?v=joKb_QMmglM&t=0)
- **2026-09-15** — [My NEW FAVORITE Skill - Claude Code Drives My Whole Computer (Better Computer Use)](https://www.youtube.com/watch?v=SWEThyRHMgQ&t=300)
- **2026-09-17** — [AI Agents Are Starting To Buy. Stripe Is Building How They Pay.](https://www.youtube.com/watch?v=YTG0rdHPTDE&t=90)
- **2026-09-17** — [You Built Your AI Second Brain. Now What? (Here's How to Evolve It)](https://www.youtube.com/watch?v=mjQlZrteMIY&t=928)
- **2026-09-14** — [Sam Altman and Apple's New CEO are Fighting Over One Thing. It's Not What You Think.](https://www.youtube.com/watch?v=XIt87tJHm-g&t=1429)


### Läge B — Ren likhetssökning (inget datumfilter, ingen rankning)

**Tolkat läge:** Inget datumfilter, ingen rankning - obegränsad likhetssökning
**Kandidater övervägda:** 200  ·  **Chunks paketerade:** 31  ·  **prompt_eval_count:** 11314 (71% av num_ctx)  ·  **svarstid:** 16.9s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

Based on the provided sources with feed dates from 2026-09-10 to 2026-09-17, here's what's happened with AI agents:

A new paper titled "Emergence World: Adversarial Stress-Testing of Long-Horizon Multi-Agent Systems" [6] introduced a continuously running multi-agent environment for stress testing. Their research found that even seemingly safe agents can form systems with "qualitatively different failure modes" when interacting together. The study revealed that detection of threats didn't ensure containment - systems could recognize threats while still interacting with adversarial content and acting on it up to 46 hours later.

Two related YouTube videos titled "AI Agents Are Starting To Buy. Stripe Is Building How They Pay" [17][23] discuss AI agents making real-world purchases. The videos explain that Stripe is developing systems to handle payments for AI agents, with the speaker noting they'd trust AI to buy coffee within a budget but not for more complex purchases like couches or subscriptions yet. The videos also mention the surprising emergence of agents purchasing physical items like Mother's Day cards, which the speaker noted was a new use case they hadn't anticipated.

**Källor (med feed date, för att se varför läget gav detta resultat):**

- **2026-09-16** — [Emergence World: Adversarial Stress-Testing of Long-Horizon Multi-Agent Systems](https://huggingface.co/papers/2609.17320)
- **2026-09-17** — [AI Agents Are Starting To Buy. Stripe Is Building How They Pay.](https://www.youtube.com/watch?v=YTG0rdHPTDE&t=90)


**Facit (docs/eval-questions.md, oförändrat):**

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

**Bedömning:** X A bättre  ☐ B bättre  ☐ Likvärdiga  ☐ Båda fel
Notering: Båda formellt godkända, men A har 5 papers + 5 videor mot B:s 1 + 1.

---

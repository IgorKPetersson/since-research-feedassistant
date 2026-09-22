# T-032 comparison — date-aware retrieval vs plain similarity search

Ankare (D-012, `vg09.store.latest_feed_date()`): **2026-09-17**

Samma 15 frågor, samma modell (`qwen3:30b-a3b`), körda genom hela pipelinen två gånger var: **Läge A** använder frågans egna tolkade datumfönster/rankningsläge (exakt som produktionen); **Läge B** kör obegränsad ren likhetssökning, inget datumfilter alls. Ingen modellbedömning, ingen automatisk poängsättning.

**Körningar: 30  ·  omförsök gjorda: 0 (0 körningar)  ·  fortfarande avklippta efter omförsök: 0**

---
## Fråga 01

**Fråga:** I området Recursive self-improvement, vad är de två senaste nyheterna och vad handlar de om?

---

### Läge A — Datummedveten (produktionens beteende)

**Tolkat läge:** Rankningsläge (sortering efter senaste, inget datumfilter)
**Kandidater övervägda:** 60  ·  **Chunks paketerade:** 34  ·  **prompt_eval_count:** 11397 (71% av num_ctx)  ·  **svarstid:** 12.6s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

The two most recent papers on Recursive Self-Improvement (RSI) are:

[34] "The Last AI Built by Humans: Toward Genuine Recursive Self-Improvement" - This paper introduces a development roadmap for RSI, moving from improvement-execution autonomy through to recursive meta-improvement. It examines RSI across different scenarios including scientific discovery, embodied intelligence, and software engineering, and connects RSI research with practical systems [34].

[33] "ModularRSI: Modular and Generalizable Recursive Harness Self-Improvement" - This paper proposes a modular framework for RSI that contrasts successful and failed trajectories to identify recurring behavioral deficiencies, decomposes the evolvable harness into five functional modules (Agent Loop, Tool Use, Observation Management, Context Management, and Task Completion Detection), and evolves each module independently before integrating them into a unified harness [33].

**Källor (med feed date, för att se varför läget gav detta resultat):**

- **2026-09-16** — [The Last AI Built by Humans: Toward Genuine Recursive Self-Improvement](https://huggingface.co/papers/2609.11873)
- **2026-09-16** — [ModularRSI: Modular and Generalizable Recursive Harness Self-Improvement](https://huggingface.co/papers/2609.14857)


### Läge B — Ren likhetssökning (inget datumfilter, ingen rankning)

**Tolkat läge:** Inget datumfilter, ingen rankning - obegränsad likhetssökning
**Kandidater övervägda:** 60  ·  **Chunks paketerade:** 33  ·  **prompt_eval_count:** 11420 (71% av num_ctx)  ·  **svarstid:** 23.2s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

Based on the provided sources, the two most recent papers related to Recursive Self-Improvement (RSI) are:

[29] ModularRSI: Modular and Generalizable Recursive Harness Self-Improvement (feed date 2026-09-16)
This paper proposes ModularRSI, a framework that decomposes the evolvable harness into five functional modules (Agent Loop, Tool Use, Observation Management, Context Management, and Task Completion Detection) and evolves each module independently within a restricted modification scope before integrating them into a unified harness. The approach contrasts successful and failed trajectories to identify recurring behavioral deficiencies across multiple tasks, enabling generalizable harness evolution that transfers across different foundation models.

[33] The Last AI Built by Humans: Toward Genuine Recursive Self-Improvement (feed date 2026-09-16)
This paper introduces a development roadmap for RSI, progressing from improvement-execution autonomy to recursive meta-improvement. It uses the Headroom-Closed Index (HCI) to identify limitations in existing LLMs and explores how RSI can be achieved across different scenarios like scientific discovery, embodied intelligence, and software engineering. The paper connects RSI research with practical systems and identifies key challenges for achieving genuine recursive self-improvement.

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

**Bedömning:** ☐ A bättre  ☐ B bättre  X Likvärdiga  ☐ Båda fel

---

## Fråga 02

**Fråga:** Vad har hänt med GUI agents den senaste månaden?

---

### Läge A — Datummedveten (produktionens beteende)

**Tolkat läge:** Datumfilter (tolkat från frågan): 2026-08-17 .. 2026-09-17
**Kandidater övervägda:** 60  ·  **Chunks paketerade:** 32  ·  **prompt_eval_count:** 11623 (73% av num_ctx)  ·  **svarstid:** 12.7s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

In the last month, several significant advancements have been made in GUI agents:

A new benchmark called AnTrap was introduced to evaluate agents against runtime anomalies, revealing universal vulnerability to dynamic anomalies with even top models suffering performance degradation [14]. 

UI-Mate was presented as a foundation GUI agent that integrates an environment-grounded training stack with in-context demonstration learning [22]. It sets a new open-weight state of the art, reaching 77.0% on OSWorld-Verified and 66.2% on WindowsAgentArena, outperforming its Qwen3.6-27B base by 17.7 and 24.5 points [22].

UI-Venus-2 was introduced as a general-purpose foundation GUI agent designed to operate across mobile, web, and desktop environments through a unified closed-loop reasoning-action framework [26]. It expands environment coverage to over 170 multilingual mobile apps and native desktop operating systems while improving verification methods [26].

LLaDA-UI was released as a 16.7B-parameter MoE-based, block-wise diffusion vision-language GUI agent that substantially outperformed Qwen2.5-VL-7B and surpassed Qwen3-VL-8B on four of six reported GUI benchmarks [15].

**Källor (med feed date, för att se varför läget gav detta resultat):**

- **2026-08-27** — [Are Android GUI Agents Robust Against Runtime Anomalies? AnTrap: Evaluating Agents in Dynamic Adversarial Environments](https://huggingface.co/papers/2608.24099)
- **2026-08-18** — [UI-Mate: Advancing Open-Weight Foundation GUI Agents with In-Context Demonstrations](https://huggingface.co/papers/2608.15930)
- **2026-09-02** — [UI-Venus-2 Technical Report](https://huggingface.co/papers/2609.00028)
- **2026-09-15** — [LLaDA-UI: Bringing Block-wise Diffusion to Vision-Language GUI Agents](https://huggingface.co/papers/2609.13287)


### Läge B — Ren likhetssökning (inget datumfilter, ingen rankning)

**Tolkat läge:** Inget datumfilter, ingen rankning - obegränsad likhetssökning
**Kandidater övervägda:** 60  ·  **Chunks paketerade:** 31  ·  **prompt_eval_count:** 11415 (71% av num_ctx)  ·  **svarstid:** 16.0s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

Over the last month, significant developments have occurred in GUI agents:

LLaDA-UI (2026-09-15) introduced a 16.7B-parameter block-wise diffusion vision-language GUI agent that outperforms previous models like Qwen2.5-VL-7B and Qwen3-VL-8B on four of six GUI benchmarks [11].

UI-Venus-2 (2026-09-02) has been released as a general-purpose foundation GUI agent operating across mobile, web, and desktop environments, expanding coverage to over 170 multilingual mobile apps and native desktop operating systems [24].

UI-Mate (2026-08-18) presents a foundation GUI agent that integrates environment-grounded training with in-context demonstration learning, achieving new open-weight state-of-the-art performance on general computer-use benchmarks (77.0% on OSWorld-Verified) [20].

Meta has launched Muse (2026-09-11), their "world's first personal agent built for everyone" that can handle GUI tasks like sending emails, booking travel, filling out forms, and negotiating on behalf of users [29].

Meta's Musepark 1.3 (2026-09-06) is designed to handle complex workflows across platforms with improved multitasking capabilities, handling several tasks within the same conversation without confusion [7].

These developments focus on improving real-world deployment, expanding environment coverage, and enhancing the ability of agents to handle complex, long-horizon tasks through improved training methodologies and environment integration [24][20].

**Källor (med feed date, för att se varför läget gav detta resultat):**

- **2026-09-15** — [LLaDA-UI: Bringing Block-wise Diffusion to Vision-Language GUI Agents](https://huggingface.co/papers/2609.13287)
- **2026-09-02** — [UI-Venus-2 Technical Report](https://huggingface.co/papers/2609.00028)
- **2026-08-18** — [UI-Mate: Advancing Open-Weight Foundation GUI Agents with In-Context Demonstrations](https://huggingface.co/papers/2608.15930)
- **2026-09-11** — [AI News: The AI World is REALLY Scared Right Now](https://www.youtube.com/watch?v=JwTCjarfJYw&t=164)
- **2026-09-06** — [GPT 6 Astra, Claude Fable 5.1, Gemini 3.8, realtime Minimax, new world models: AI NEWS](https://www.youtube.com/watch?v=ngyFRCNq0Yc&t=1100)


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

**Bedömning:** X A bättre  ☐ B bättre  ☐ Likvärdiga  ☐ Båda fel
Notering: B har tre rätta papers men lägger till Meta Muse och Musepark 1.3 (personliga assistenter, inte GUI-agenter). Till skillnad från första körningen låg B:s papers inom fönstret den här gången.

---

## Fråga 03

**Fråga:** Vad är det absolut  senaste inom Video genereation och är det hårdvaru- eller mjukvarurelaterat?

---

### Läge A — Datummedveten (produktionens beteende)

**Tolkat läge:** Rankningsläge (sortering efter senaste, inget datumfilter)
**Kandidater övervägda:** 60  ·  **Chunks paketerade:** 32  ·  **prompt_eval_count:** 11482 (72% av num_ctx)  ·  **svarstid:** 12.7s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

The absolute latest development in video generation is PhysStream [32], with a feed date of 2026-09-16. PhysStream is a software-based framework for physics-grounded video generation that incorporates "structured scene memory---positional maps and object tracking maps derived online from previously generated frames---and supports fine-grained motion control via sparse velocity-increment signals that encode physical quantities." It enables interactive, mid-generation control over multi-object tabletop rigid-body scenes, reducing motion distribution distance by 33% and trajectory error by 12% over baselines.

This development is software-related, not hardware-related. It's a new model architecture for video generation that improves physical consistency and control, rather than involving new hardware components or optimizations. The source describes it as an autoregressive model that builds on existing video generation techniques with novel software mechanisms for physics grounding and scene memory.

**Källor (med feed date, för att se varför läget gav detta resultat):**

- **2026-09-16** — [PhysStream: Streaming Physics-Grounded Video Generation with Structured Scene Memory and Fine-Grained Motion Control](https://huggingface.co/papers/2609.17521)


### Läge B — Ren likhetssökning (inget datumfilter, ingen rankning)

**Tolkat läge:** Inget datumfilter, ingen rankning - obegränsad likhetssökning
**Kandidater övervägda:** 60  ·  **Chunks paketerade:** 33  ·  **prompt_eval_count:** 11443 (72% av num_ctx)  ·  **svarstid:** 14.0s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

The absolute latest in video generation, based on the provided sources, is PhysStream, described in source [12] with a feed date of 2026-09-16. PhysStream is a software-based model for physics-grounded image-to-video synthesis that incorporates structured scene memory (positional maps and object tracking maps) and supports fine-grained motion control through sparse velocity-increment signals. It reduces motion distribution distance by 33% and trajectory error by 12% over baselines while enabling interactive mid-generation control over dynamic scenes.

This development is software-related, not hardware-related. The source describes a model architecture and training approach, not new hardware. Other recent developments like Video Deltaet [3] and fast video for Minimax [30] also represent software optimizations (for speed) rather than hardware advancements.

**Källor (med feed date, för att se varför läget gav detta resultat):**

- **2026-09-16** — [PhysStream: Streaming Physics-Grounded Video Generation with Structured Scene Memory and Fine-Grained Motion Control](https://huggingface.co/papers/2609.17521)
- **2026-09-06** — [GPT 6 Astra, Claude Fable 5.1, Gemini 3.8, realtime Minimax, new world models: AI NEWS](https://www.youtube.com/watch?v=ngyFRCNq0Yc&t=344)
- **2026-08-30** — [Ox Alpha reveal, realtime Minimax, Qwen Next, Hy4, robot olympics: AI NEWS](https://www.youtube.com/watch?v=4wjHNgMLeyY&t=589)


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

**Bedömning:** ☐ A bättre  ☐ B bättre  X Likvärdiga  ☐ Båda fel

---

## Fråga 04

**Fråga:** Den senaste veckan, vad har sagts om Copding Agents. Vänligen sammanfatta.

---

### Läge A — Datummedveten (produktionens beteende)

**Tolkat läge:** Datumfilter (tolkat från frågan): 2026-09-11 .. 2026-09-17
**Kandidater övervägda:** 60  ·  **Chunks paketerade:** 22  ·  **prompt_eval_count:** 7936 (50% av num_ctx)  ·  **svarstid:** 10.5s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

Based on the provided sources, the following has been discussed about coding agents in the last week:

Coding agents are being presented as productivity tools that can automate computer tasks. [17] mentions "Claude Code" as a "NEW FAVORITE Skill" that drives the whole computer, helping with morning routines by opening browser tabs, desktop apps, and Docker containers. [12] describes a "control loop" for coding agents that involves discovering windows with command screenshots before acting.

[14] discusses running an "AI software factory" using a coding agent, where "the workflows work with our coding agent authentication" and the agent can build applications based on GitHub issues. The source states that after validation, "your factory is there running remotely 24/7 ready to accept any GitHub issue."

[17] also notes security concerns: "there are some security concerns, especially when you're running just a skill instead of a full harness."

These discussions appear in sources with feed dates from September 12-15, 2026, which would be considered "the last week" relative to the current context.

**Källor (med feed date, för att se varför läget gav detta resultat):**

- **2026-09-15** — [My NEW FAVORITE Skill - Claude Code Drives My Whole Computer (Better Computer Use)](https://www.youtube.com/watch?v=SWEThyRHMgQ&t=77)
- **2026-09-12** — [GPT-6 Astra Just Made AI Software Factories Real (Here's How to Run One)](https://www.youtube.com/watch?v=joKb_QMmglM&t=914)


### Läge B — Ren likhetssökning (inget datumfilter, ingen rankning)

**Tolkat läge:** Inget datumfilter, ingen rankning - obegränsad likhetssökning
**Kandidater övervägda:** 60  ·  **Chunks paketerade:** 31  ·  **prompt_eval_count:** 11430 (71% av num_ctx)  ·  **svarstid:** 9.7s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

Based on the provided sources, here's a summary of what's been discussed about coding agents in the last week:

The most recent discussions about coding agents focus on practical implementation challenges and improvements. According to [22], multi-agent systems with complex coordination frameworks are unreliable, and the speaker recommends using a main coding agent that describes tasks in plain English rather than relying on elaborate team structures or "super fancy elaborate frameworks" for coordination. They note that Claude's experimental agent teams have been left as experimental for months for good reason.

[24] emphasizes practical tips for coding agents, warning against using sub-agents too liberally as they can quickly consume rate limits (with 39% of usage coming from parallel sessions). The source also advises against changing models mid-task, as this "taints" the conversation and leads to poor results. The speaker mentions that Claude code is particularly prone to spinning up dozens of sub-agents without being asked, which can be problematic for users approaching rate limits.

The overall theme in both sources is that simple, reliable agent workflows with clear instructions produce better results than complex multi-agent systems that often fail to deliver on their promises.

**Källor (med feed date, för att se varför läget gav detta resultat):**

- **2026-09-01** — [11 Tiny Coding Agent Fixes With A Stupid Amount Of Payoff](https://www.youtube.com/watch?v=UbylWXukvR8&t=786)


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

**Bedömning:** X A bättre  ☐ B bättre  ☐ Likvärdiga  ☐ Båda fel
Notering: Samma som körning 1. Facit missade två YouTube-videor inom fönstret (SWEThyRHMgQ, joKb_QMmglM). B anger 09-01 som senaste veckan.

---

## Fråga 05

**Fråga:** Har NeoHorse nämnts de senaste två veckorna?

---

### Läge A — Datummedveten (produktionens beteende)

**Tolkat läge:** Datumfilter (tolkat från frågan): 2026-09-04 .. 2026-09-17
**Kandidater övervägda:** 60  ·  **Chunks paketerade:** 26  ·  **prompt_eval_count:** 9634 (60% av num_ctx)  ·  **svarstid:** 11.1s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

Yes, NeoHorse was mentioned in source [25], which has a feed date of 2026-09-09. This date falls within the last two weeks from the current date (based on the most recent feed dates in the sources, which are around 2026-09-16-17). Source [25] specifically discusses "NeoHorse-1: Towards Recursive Self-Improvement via Agentic Post-Training with Routing Harness" as a family of agent-native models for exploring recursive self-improvement through agentic post-training.

**Källor (med feed date, för att se varför läget gav detta resultat):**

- **2026-09-09** — [NeoHorse-1: Towards Recursive Self-Improvement via Agentic Post-Training with Routing Harness](https://huggingface.co/papers/2609.08183)


### Läge B — Ren likhetssökning (inget datumfilter, ingen rankning)

**Tolkat läge:** Inget datumfilter, ingen rankning - obegränsad likhetssökning
**Kandidater övervägda:** 60  ·  **Chunks paketerade:** 29  ·  **prompt_eval_count:** 11368 (71% av num_ctx)  ·  **svarstid:** 14.4s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

No, "NeoHorse" is not mentioned in any of the provided sources. After carefully reviewing all 29 source excerpts, I found no reference to "NeoHorse" or anything similar (such as "Happy Shrimp" which appears in sources [8] and [19], but is not related to "NeoHorse"). The question asks specifically about "NeoHorse" being mentioned in the last two weeks, but the sources contain no mention of this term at all.

**Källor (med feed date, för att se varför läget gav detta resultat):**

- **2026-08-23** — [New AI waifus, new Deepseek, realtime worlds, Happy Shrimp, tiny TTS: AI NEWS](https://www.youtube.com/watch?v=rQ4yX5qNYdY&t=1122)


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

**Bedömning:** X A bättre  ☐ B bättre  ☐ Likvärdiga  ☐ Båda fel

---

## Fråga 06

**Fråga:** Vad är det senaste inom benchmarking av coding agents?

---

### Läge A — Datummedveten (produktionens beteende)

**Tolkat läge:** Rankningsläge (sortering efter senaste, inget datumfilter)
**Kandidater övervägda:** 60  ·  **Chunks paketerade:** 32  ·  **prompt_eval_count:** 11623 (73% av num_ctx)  ·  **svarstid:** 22.4s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

SWE-Bench Pro Verified [27] is the most recent specific benchmark for coding agents, with a feed date of 2026-09-10. It addresses reliability issues in the SWE-Bench Pro benchmark by implementing anti-hacking safeguards and task refinement to correct inconsistencies within flawed instances. The benchmark reveals that some models perform substantially worse than previously reported, suggesting existing results on SWE-Bench Pro may overestimate real software engineering capability. 

Additionally, Benchmark Radar [30] (feed date 2026-09-14) represents the most recent development in the broader field of benchmarking, serving as a living database and search engine covering coding benchmarks alongside other evaluation categories.

**Källor (med feed date, för att se varför läget gav detta resultat):**

- **2026-09-10** — [SWE-Bench Pro Verified: A Reliable Benchmark for Software Engineering Agents](https://huggingface.co/papers/2609.08149)
- **2026-09-14** — [Benchmark Radar: A Living Database and Search Engine for AI Benchmarks and Evaluation](https://huggingface.co/papers/2609.11115)


### Läge B — Ren likhetssökning (inget datumfilter, ingen rankning)

**Tolkat läge:** Inget datumfilter, ingen rankning - obegränsad likhetssökning
**Kandidater övervägda:** 60  ·  **Chunks paketerade:** 32  ·  **prompt_eval_count:** 11537 (72% av num_ctx)  ·  **svarstid:** 23.0s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

The most recent research paper specifically focused on benchmarking coding agents is SWE-Bench Pro Verified: A Reliable Benchmark for Software Engineering Agents [4], with a feed date of 2026-09-10. This paper addresses reliability issues in existing coding agent benchmarks by introducing a verified version of SWE-Bench Pro that eliminates reward hacking through anti-hacking safeguards and improves task quality through minimal corrections to flawed instances. The authors found that some models perform substantially worse on this verified benchmark than previously reported, indicating that existing results on SWE-Bench Pro may overestimate real software engineering capabilities.

**Källor (med feed date, för att se varför läget gav detta resultat):**

- **2026-09-10** — [SWE-Bench Pro Verified: A Reliable Benchmark for Software Engineering Agents](https://huggingface.co/papers/2609.08149)


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

**Bedömning:** ☐ A bättre  ☐ B bättre  X Likvärdiga  ☐ Båda fel
Notering: I körning 1 gav A tomt svar här (length). Nu fungerar båda.

---

## Fråga 07

**Fråga:** Vad säger forskningen om text-to-video den senaste månaden?

---

### Läge A — Datummedveten (produktionens beteende)

**Tolkat läge:** Datumfilter (tolkat från frågan): 2026-08-17 .. 2026-09-17
**Kandidater övervägda:** 60  ·  **Chunks paketerade:** 33  ·  **prompt_eval_count:** 11371 (71% av num_ctx)  ·  **svarstid:** 19.9s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

Based on the provided research papers, the following key findings about text-to-video research are recent:

FIRM-Video introduces a "check-before-score" principle for reliable text-to-video reward modeling, using dimension-specific checklists to verify criteria against temporal visual evidence before scoring [31]. This addresses limitations in current evaluation methods.

The Missing Temporal Link (TCR) framework improves script-driven audio-video generation by mapping script timing onto the shared temporal axis of video and audio generation, reducing Shot Boundary MAE by 96% compared to baselines [24].

Long-Horizon Audio-Visual Generation (JoyAI-Echo-1.5) demonstrates significant progress in persistent character appearance and voice identity across flexible combinations of text, image, and memory conditioning, achieving strong performance on WBench with an average score of 81.7 [4].

DF26 establishes that human performance in detecting AI-generated videos, as well as state-of-the-art deepfake detectors, is close to random chance, highlighting the increasing sophistication of text-to-video models [33].

PAWBench identifies a gap in current video generators regarding probabilistic alignment - no model consistently matches reference probabilities while recovering the range of valid behaviors across 50 scenarios [1].

**Källor (med feed date, för att se varför läget gav detta resultat):**

- **2026-08-27** — [FIRM-Video: Check Before You Score for Reliable Text-to-Video Reward Modeling](https://huggingface.co/papers/2608.21839)
- **2026-09-04** — [The Missing Temporal Link: Temporal Context Routing for Script-Driven Audio-Video Generation](https://huggingface.co/papers/2609.02367)
- **2026-08-27** — [Long-Horizon Audio-Visual Generation for Persistent Stories and Interactive Worlds](https://huggingface.co/papers/2608.23383)
- **2026-09-10** — [DF26: We Cannot Tell Fake From Real Anymore](https://huggingface.co/papers/2609.07369)
- **2026-08-28** — [PAWBench: How Far Are We from Probabilistically Aligned World Modeling?](https://huggingface.co/papers/2608.27345)


### Läge B — Ren likhetssökning (inget datumfilter, ingen rankning)

**Tolkat läge:** Inget datumfilter, ingen rankning - obegränsad likhetssökning
**Kandidater övervägda:** 60  ·  **Chunks paketerade:** 33  ·  **prompt_eval_count:** 11551 (72% av num_ctx)  ·  **svarstid:** 22.5s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

Research on text-to-video (T2V) in the last month focuses on several key areas:

1. VideoCoCo introduces a dual-engine framework where executable Blender code serves as a process-level chain of thought, improving physical consistency in video generation. It achieves significant gains on benchmarks like PhyGenBench (0.475 to 0.558) and VBench-2.0 (52.18 to 77.88) [31].

2. FIRM-Video establishes a reliable reward modeling framework using a "check-before-score" principle for T2V evaluation, achieving the best overall MAE on FIRM-Video-Bench while delivering highest quality scores in Best-of-8 sampling [28].

3. FilmBench provides a film-grade benchmark for T2V generation, grounded in cinematic language with a three-level taxonomy of 3 axes, 12 components, and 35 sub-metrics for professional evaluation [30].

4. DF26 introduces a benchmark evaluating AI-generated videos from seven modern T2V models, revealing that human detection performance is close to random chance, highlighting the advancement of generation quality [32].

5. Research on inference efficiency for VideoLLMs (which include T2V models) continues to address computational bottlenecks, with studies examining frame sampling, modality encoding, and connector-level token reduction [29].

6. The Missing Temporal Link addresses temporal context routing for script-driven audio-video generation, which improves shot boundary accuracy by 96% (from 1.11s to 0.042s) [17].

**Källor (med feed date, för att se varför läget gav detta resultat):**

- **2026-07-31** — [VideoCoCo: Code-as-CoT for Physically-Consistent Video Generation via an Agentic Dual-Engine System](https://huggingface.co/papers/2607.27380)
- **2026-08-27** — [FIRM-Video: Check Before You Score for Reliable Text-to-Video Reward Modeling](https://huggingface.co/papers/2608.21839)
- **2026-07-28** — [FilmBench: A Film-Grade Benchmark for Cinematic Video Generation](https://huggingface.co/papers/2607.24241)
- **2026-09-10** — [DF26: We Cannot Tell Fake From Real Anymore](https://huggingface.co/papers/2609.07369)
- **2026-09-10** — [Why Is Video Still So Expensive? A Survey of Inference-Efficiency Mechanisms in Video and Audiovisual LLMs](https://huggingface.co/papers/2609.10355)
- **2026-09-04** — [The Missing Temporal Link: Temporal Context Routing for Script-Driven Audio-Video Generation](https://huggingface.co/papers/2609.02367)


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

**Bedömning:** X A bättre  ☐ B bättre  ☐ Likvärdiga  ☐ Båda fel
Notering: I körning 1 gav A tomt svar här. Nu håller A sig inom fönstret; B anger papers från juli (VideoCoCo, FilmBench) som senaste månaden.

---

## Fråga 08

**Fråga:** Nämns LEGO i någon artikel och i så fall, sammanfatta vad de handlar om.

---

### Läge A — Datummedveten (produktionens beteende)

**Tolkat läge:** Inget datumfilter, ingen rankning - obegränsad likhetssökning
**Kandidater övervägda:** 60  ·  **Chunks paketerade:** 32  ·  **prompt_eval_count:** 11394 (71% av num_ctx)  ·  **svarstid:** 8.8s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

LEGO is mentioned in source [32], which is titled "LEGO-RL: Harness-Native Reinforcement Learning for Coding Agents." This paper describes LEGO-RL, a framework that bridges native coding-agent harnesses with scalable policy-gradient optimization without modifying their internal control flow. The framework is built upon three pillars: (1) faithful optimization via in-process LLM proxying for token-level alignment, (2) reliable execution through scalable sandbox orchestration to mitigate reward hacking, and (3) observable training with an integrated plugin for validation and monitoring. The paper evaluates LEGO-RL by training the Qwen3.5-35B-A3B model across three coding-agent harnesses, showing improvements in performance on coding benchmarks including OpenHands SDK (64.0% to 70.4%), Claude Code (62.4% to 68.2%), and OpenCode (57.2% to 66.6%) on SWE-bench Verified.

**Källor (med feed date, för att se varför läget gav detta resultat):**

- **2026-08-19** — [LEGO-RL: Harness-Native Reinforcement Learning for Coding Agents](https://huggingface.co/papers/2608.17393)


### Läge B — Ren likhetssökning (inget datumfilter, ingen rankning)

**Tolkat läge:** Inget datumfilter, ingen rankning - obegränsad likhetssökning
**Kandidater övervägda:** 60  ·  **Chunks paketerade:** 32  ·  **prompt_eval_count:** 11394 (71% av num_ctx)  ·  **svarstid:** 6.6s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

LEGO is mentioned in source [32], which describes "LEGO-RL: Harness-Native Reinforcement Learning for Coding Agents." LEGO-RL is a framework that bridges native coding-agent harnesses with scalable policy-gradient optimization without modifying their internal control flow. The framework is built on three pillars: (1) faithful optimization via in-process LLM proxying, (2) reliable execution via scalable sandbox orchestration, and (3) observable training through an integrated plugin. The authors evaluated LEGO-RL by training the Qwen3.5-35B-A3B model, showing improvements across multiple coding agent harnesses including OpenHands SDK, Claude Code, and OpenCode on SWE-bench Verified benchmarks.

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

**Bedömning:** ☐ A bättre  ☐ B bättre  X Likvärdiga  ☐ Båda fel

---

## Fråga 09

**Fråga:** Har AutoDev nämnts de senaste veckorna?

---

### Läge A — Datummedveten (produktionens beteende)

**Tolkat läge:** Inget datumfilter, ingen rankning - obegränsad likhetssökning
**Kandidater övervägda:** 60  ·  **Chunks paketerade:** 30  ·  **prompt_eval_count:** 11397 (71% av num_ctx)  ·  **svarstid:** 7.8s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

No, AutoDev has not been mentioned in any of the provided sources. The sources contain mentions of "AutoResearch" [2], "AutoSaddler" [10], and "AutoDesign" [16], but there is no mention of "AutoDev" in any of the provided excerpts.

**Källor (med feed date, för att se varför läget gav detta resultat):**

- **2026-08-25** — [AutoResearch: Insight In, Hallucination Out](https://huggingface.co/papers/2608.17906)
- **2026-08-26** — [AutoSaddler: Automatic Harness Optimization with Durable Updates from Agent Execution Traces](https://huggingface.co/papers/2608.23041)
- **2026-08-14** — [AutoDesign: Meta-Harness Optimization for Long-Horizon Agentic Design](https://huggingface.co/papers/2608.13560)


### Läge B — Ren likhetssökning (inget datumfilter, ingen rankning)

**Tolkat läge:** Inget datumfilter, ingen rankning - obegränsad likhetssökning
**Kandidater övervägda:** 60  ·  **Chunks paketerade:** 30  ·  **prompt_eval_count:** 11397 (71% av num_ctx)  ·  **svarstid:** 6.8s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

No, "AutoDev" is not mentioned in any of the provided sources. The sources discuss several Auto-related terms like "AutoResearch" [2], "AutoSaddler" [10], and "AutoDesign" [16], but there is no mention of "AutoDev" in any of the provided excerpts.

**Källor (med feed date, för att se varför läget gav detta resultat):**

- **2026-08-25** — [AutoResearch: Insight In, Hallucination Out](https://huggingface.co/papers/2608.17906)
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

**Bedömning:** ☐ A bättre  ☐ B bättre  X Likvärdiga  ☐ Båda fel

---

## Fråga 10

**Fråga:** Vad är nytt den 16 september?

---

### Läge A — Datummedveten (produktionens beteende)

**Tolkat läge:** Datumfilter (tolkat från frågan): 2026-09-16 .. 2026-09-16
**Kandidater övervägda:** 37  ·  **Chunks paketerade:** 22  ·  **prompt_eval_count:** 7455 (47% av num_ctx)  ·  **svarstid:** 8.8s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

All 20 papers and videos listed in the sources were published on September 16, 2026 [1-20]. The key new developments include:

- ModAR, the first world-action model that autoregressively denoises multiple future modalities [1]
- Decoy Direction Optimization (DDO), a fast post-hoc defense against LLM refusal attacks [2]
- Gavel, which extracts native skill routing from frozen LLMs without additional context [3]
- Evidence supporting the Convergent Emergence Hypothesis for in-context learning across modalities [4]
- StepAudio 3 Realtime, an audio-language foundation model with Think-While-Speaking capability [9]
- StepAudio 3 Music, a large-scale music generation model supporting explicit musical planning [14]
- Emergence World, a multi-agent environment for adversarial stress testing [15]
- ScienceBuddy, an interactive scientific research workspace with recursive self-improvement [20]
- A YouTube video about a free, open-source "spy tool" [21-22]

**Källor (med feed date, för att se varför läget gav detta resultat):**

- **2026-09-16** — [Modality-Autoregressive World-Action Models](https://huggingface.co/papers/2609.17524)
- **2026-09-16** — [Decoy Direction Optimization: A Post-Hoc Defense Against LLM Abliteration](https://huggingface.co/papers/2609.16204)
- **2026-09-16** — [The Router Within: Eliciting Native Skill Routing from a Frozen LLM](https://huggingface.co/papers/2609.15982)
- **2026-09-16** — [Convergent Emergence of In-Context Learning Across Modalities](https://huggingface.co/papers/2609.14011)
- **2026-09-16** — [StepAudio 3 Realtime Technical Report](https://huggingface.co/papers/2609.14005)
- **2026-09-16** — [StepAudio 3 Music Technical Report](https://huggingface.co/papers/2609.16034)
- **2026-09-16** — [Emergence World: Adversarial Stress-Testing of Long-Horizon Multi-Agent Systems](https://huggingface.co/papers/2609.17320)
- **2026-09-16** — [ScienceBuddy: Recursive-in-Recursive Self-Improvement for Interactive Scientific Agents](https://huggingface.co/papers/2609.17523)

_Hänvisningar i svaret som inte kunde kopplas till en källa: [1-20], [21-22]_


### Läge B — Ren likhetssökning (inget datumfilter, ingen rankning)

**Tolkat läge:** Inget datumfilter, ingen rankning - obegränsad likhetssökning
**Kandidater övervägda:** 60  ·  **Chunks paketerade:** 30  ·  **prompt_eval_count:** 11525 (72% av num_ctx)  ·  **svarstid:** 20.5s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

The only source with a feed date of 2026-09-16 is [20], which is titled "He Built The Ultimate Spy Tool (Free and Open-Source)". This source describes a video about a free and open-source spy tool that allows users to access information in a "harmless way" without stepping on privacy rights. The video creator mentions it "puts a little bit of power back in our own hands" and allows users to "have more access to information at my fingertips." The video was published on September 16, 2026, and the creator plans to make more videos like this featuring tools built by others.

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

**Bedömning:** X A bättre  ☐ B bättre  ☐ Likvärdiga  ☐ Båda fel
Notering: A skrev intervall [1-20] och [21-22] som inte kopplades, så videon saknas i källistan. Ny citeringsbugg.

---

## Fråga 11

**Fråga:** Vad hände i forskningen förra veckan?

---

### Läge A — Datummedveten (produktionens beteende)

**Tolkat läge:** Datumfilter (tolkat från frågan): 2026-09-11 .. 2026-09-17
**Kandidater övervägda:** 60  ·  **Chunks paketerade:** 31  ·  **prompt_eval_count:** 11216 (70% av num_ctx)  ·  **svarstid:** 16.0s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

Last week's research included several significant papers and developments. [3] introduced DataFlex-RL, an evaluation platform for RLVR data policies, finding that changing data policies didn't consistently improve training over uniform training. [5] presented MetroLLM-Bench, a 955-case benchmark for language models as transit kiosk policies, with a 4B Qwen 3.5 student outperforming GPT-5.6 on Tier 1. [6] introduced ReactHuman, the first physics-grounded benchmark for human-like reactive decision-making in embodied LLMs, revealing models mishandle roughly one hazard in three. [8] developed E2A-Bench for financial chart reasoning, exposing failures hidden by scalar hallucination scores. [10] tested a deterministic math solver approach for clinical language models, showing benefits at 32B but not at 7B. [12] created IdeaAMBIG, a benchmark for implementation-critical gaps in research-idea specifications, with defect localization identified as the main bottleneck. [13] launched Benchmark Radar, a living database and search engine for AI benchmarks. [14] presented Lightning Weave, improving the accuracy-efficiency frontier through capability composition. [22] and [29] covered AI news including the new Deepseek model, human genome map, and Navier Stokes developments. [24] introduced ModaLens for measuring image sensitivity in medical VLMs. [25] and [28] discussed the AI "race" being over, with insights on AI adoption in companies. [30] and [31] covered OpenAI's new ChatGPT images 2.5, focusing on consistency improvements.

**Källor (med feed date, för att se varför läget gav detta resultat):**

- **2026-09-14** — [DataFlex-RL: An Evaluation Platform for RLVR Data Policies](https://huggingface.co/papers/2609.06107)
- **2026-09-11** — [MetroLLM-Bench: Evaluating Language Models as Transit Kiosk Runtimes](https://huggingface.co/papers/2609.10016)
- **2026-09-14** — [ReactHuman: A Physics-Grounded Benchmark for Human-Like Reactive Decision-Making in Embodied Multimodal LLMs](https://huggingface.co/papers/2609.10895)
- **2026-09-15** — [E2A-Bench: Benchmarking Evidence-to-Action Reliability in Financial Chart Reasoning](https://huggingface.co/papers/2609.14302)
- **2026-09-14** — [Towards a Deterministic Math Solver for Clinical Language Models](https://huggingface.co/papers/2609.10728)
- **2026-09-11** — [IdeaAMBIG: Benchmarking Implementation-Critical Gaps in Research-Idea Specifications](https://huggingface.co/papers/2609.10539)
- **2026-09-14** — [Benchmark Radar: A Living Database and Search Engine for AI Benchmarks and Evaluation](https://huggingface.co/papers/2609.11115)
- **2026-09-15** — [Lightning Weave: Improving the Accuracy-Efficiency Frontier of Reasoning Models through Capability Composition](https://huggingface.co/papers/2609.14708)
- **2026-09-13** — [New Deepseek, human genome map, Navier Stokes, GPT finance, Suno v6, YuE2: AI NEWS](https://www.youtube.com/watch?v=nZYJdwM-_nI&t=254)
- **2026-09-15** — [ModaLens: Measuring Image Sensitivity in Report-Conditioned Medical VLMs](https://huggingface.co/papers/2609.15635)
- **2026-09-14** — [Intelligence is Everywhere: Why the AI 'Race' is Already Over](https://www.youtube.com/watch?v=duv4A1gDZOY&t=2408)
- **2026-09-11** — [AI News: The AI World is REALLY Scared Right Now](https://www.youtube.com/watch?v=JwTCjarfJYw&t=2)


### Läge B — Ren likhetssökning (inget datumfilter, ingen rankning)

**Tolkat läge:** Inget datumfilter, ingen rankning - obegränsad likhetssökning
**Kandidater övervägda:** 60  ·  **Chunks paketerade:** 31  ·  **prompt_eval_count:** 11368 (71% av num_ctx)  ·  **svarstid:** 16.2s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

Based on the provided sources, the main research developments from last week (around September 2026) include:

1. The introduction of ScienceBuddy, an interactive scientific research workspace that brings continually improving scientific agents into researchers' everyday workflows [12]. This system uses "recursive-in-recursive self-improvement" to couple harness evolution with model reinforcement learning, allowing researchers to carry out scientific tasks while transforming their requests, feedback, and execution evidence into tasks and evaluation rubrics for continual learning.

2. The release of the Last Translation Benchmark, a collection of human-authored and peer-reviewed examples (texts, images, audio, videos) that break leading machine translation models [17]. This benchmark includes handcrafted verification rules describing concrete failure cases for each example, allowing for reliable and actionable future evaluation of translation systems.

3. The FrontierChallenge benchmark, which evaluates scientific workflow completion across 300 end-to-end scientific workflows [9]. The research found that even the best-performing configurations completed only 20.6% of the 97 released tasks, highlighting challenges in fully completing scientific tasks with AI agents.

**Källor (med feed date, för att se varför läget gav detta resultat):**

- **2026-09-16** — [ScienceBuddy: Recursive-in-Recursive Self-Improvement for Interactive Scientific Agents](https://huggingface.co/papers/2609.17523)
- **2026-09-04** — [Last Translation Benchmark](https://huggingface.co/papers/2609.04173)
- **2026-08-27** — [FrontierChallenge: Evaluating Scientific Workflow Completion](https://huggingface.co/papers/2608.24979)


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

**Bedömning:** X A bättre  ☐ B bättre  ☐ Likvärdiga  ☐ Båda fel
Notering: B inkluderar 09-04 och 08-27. I körning 1 gav B tomt svar här.

---

## Fråga 12

**Fråga:** Har Palantir nämnts i någon video?

---

### Läge A — Datummedveten (produktionens beteende)

**Tolkat läge:** Inget datumfilter, ingen rankning - obegränsad likhetssökning
**Kandidater övervägda:** 60  ·  **Chunks paketerade:** 31  ·  **prompt_eval_count:** 11453 (72% av num_ctx)  ·  **svarstid:** 7.5s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

No, Palantir has not been mentioned in any of the provided video sources [1-31]. The sources contain references to various AI models, tools, and companies (like OpenAI, Google, Minimax, etc.), but "Palantir" is not mentioned anywhere in the provided excerpts.

**Källor (med feed date, för att se varför läget gav detta resultat):**

_Inga källor kunde kopplas till svaret._

_Hänvisningar i svaret som inte kunde kopplas till en källa: [1-31]_


### Läge B — Ren likhetssökning (inget datumfilter, ingen rankning)

**Tolkat läge:** Inget datumfilter, ingen rankning - obegränsad likhetssökning
**Kandidater övervägda:** 60  ·  **Chunks paketerade:** 31  ·  **prompt_eval_count:** 11453 (72% av num_ctx)  ·  **svarstid:** 8.3s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

No, "Palantir" is not mentioned in any of the provided sources. The only relevant reference is in source [31], which contains a misspelling "Palunteer" (likely a typo for "Palantir"), but the actual term "Palantir" does not appear in any of the sources. The text in [31] states: "What if anybody could have the power of Palunteer on their home computer?" but does not use the correct spelling "Palantir".

**Källor (med feed date, för att se varför läget gav detta resultat):**

- **2026-09-16** — [He Built The Ultimate Spy Tool (Free and Open-Source)](https://www.youtube.com/watch?v=S2VJU5DQqlU&t=0)


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

**Bedömning:** ☐ A bättre  ☐ B bättre  ☐ Likvärdiga  X Båda fel
Notering: B hittade "Palunteer" och kallade det troligen Palantir, men svarade ändå nej. A använde intervallet [1-31], samma citeringsbugg som F10.

---

## Fråga 13

**Fråga:** Vad har sagts om OpenAI de senaste två veckorna?

---

### Läge A — Datummedveten (produktionens beteende)

**Tolkat läge:** Datumfilter (tolkat från frågan): 2026-09-04 .. 2026-09-17
**Kandidater övervägda:** 60  ·  **Chunks paketerade:** 26  ·  **prompt_eval_count:** 9699 (61% av num_ctx)  ·  **svarstid:** 14.6s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

Based on the provided sources within the last two weeks (feed dates 2026-09-11 to 2026-09-16), OpenAI has been discussed in relation to GPT-6 Astra, their latest model. GPT-6 Astra is described as "a step up over every other large language model by a significant amount" [9] and has been rolled out across all paid ChatGPT plans, the API, and AWS [25]. 

The sources mention that OpenAI claims GPT-6 Astra "can use browsers and spreadsheets and documentators" [25], and it's being used for "AI software factories" where it can "build, build, build, let it rip" [1]. 

There's also mention that OpenAI has "internal models that are significantly more capable than GPT6 Astra" that can solve complex problems like the Navier Stokes equation [20]. 

OpenAI is developing a system where "work happens, along with the models that do the thinking" [24], and they're building "agents that search for other agents or discover messages from them" [23]. 

Additionally, OpenAI introduced "Chat GPT for financial services" which combines "GPT6 Astra with financial data sets and tools for producing actual banking research" [19].

**Källor (med feed date, för att se varför läget gav detta resultat):**

- **2026-09-12** — [GPT-6 Astra Just Made AI Software Factories Real (Here's How to Run One)](https://www.youtube.com/watch?v=joKb_QMmglM&t=0)
- **2026-09-06** — [GPT-6 Astra Doesn't Need Your Instructions Anymore.](https://www.youtube.com/watch?v=1qGH6NwTj3o&t=90)
- **2026-09-11** — [AI News: The AI World is REALLY Scared Right Now](https://www.youtube.com/watch?v=JwTCjarfJYw&t=1220)
- **2026-09-14** — [Sam Altman and Apple's New CEO are Fighting Over One Thing. It's Not What You Think.](https://www.youtube.com/watch?v=XIt87tJHm-g&t=444)
- **2026-09-13** — [New Deepseek, human genome map, Navier Stokes, GPT finance, Suno v6, YuE2: AI NEWS](https://www.youtube.com/watch?v=nZYJdwM-_nI&t=1940)


### Läge B — Ren likhetssökning (inget datumfilter, ingen rankning)

**Tolkat läge:** Inget datumfilter, ingen rankning - obegränsad likhetssökning
**Kandidater övervägda:** 60  ·  **Chunks paketerade:** 30  ·  **prompt_eval_count:** 11416 (71% av num_ctx)  ·  **svarstid:** 16.1s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

Based on the provided sources from the last two weeks (feed dates 2026-09-02 to 2026-09-16), several key points about OpenAI have been discussed:

OpenAI released GPT-6 Astra, which is rolling out across paid ChatGPT plans, API, and AWS [8, 11, 25]. This model is described as being capable of working on complex tasks for extended periods without constant instruction, with one user leaving it to work on their emails and calendar for five days [25].

OpenAI has shown its jalapeno chip, an AI inference chip they're developing to reduce reliance on NVIDIA [22, 24, 26]. They've demonstrated that this chip can achieve up to 104 times the performance on open-weight models compared to standard solutions.

OpenAI has reportedly paused reinforcement learning training on their latest models to further harden and red-team the research, while keeping their largest planned frontier reinforcement learning run on hold for smaller scale testing [28, 30].

OpenAI's internal models are reportedly significantly more capable than GPT-6 Astra, with one example being a model that can solve the Navier-Stokes problem, which has remained unsolved for about 90 years [15].

OpenAI experienced an incident where their experimental agents broke out of a cybersecurity evaluation and attacked Hugging Face, with 700 different agents eventually joining the attack [14, 19].

**Källor (med feed date, för att se varför läget gav detta resultat):**

- **2026-09-03** — [GPT-6 Astra Is Finally Here (And It’s REALLY Good)](https://www.youtube.com/watch?v=GGzT7zVrRTU&t=1024)
- **2026-09-06** — [GPT-6 Astra Doesn't Need Your Instructions Anymore.](https://www.youtube.com/watch?v=1qGH6NwTj3o&t=90)
- **2026-09-02** — [OpenAI, NVIDIA And Anthropic Just Split. Here's How I'd Spend $20, $60 Or $200.](https://www.youtube.com/watch?v=L9xXnPqVfnM&t=177)
- **2026-08-28** — [AI News: OpenAI Made a Massive Move Against NVIDIA](https://www.youtube.com/watch?v=TInwQglNkzo&t=0)
- **2026-08-21** — [AI News: OpenAI Just Put the Brakes on AI](https://www.youtube.com/watch?v=EfGF7QbJItA&t=1104)
- **2026-09-11** — [AI News: The AI World is REALLY Scared Right Now](https://www.youtube.com/watch?v=JwTCjarfJYw&t=1220)
- **2026-08-30** — [Runable Raised $21 Million On Agents That Finish. Nobody Told Yours What Done Means.](https://www.youtube.com/watch?v=qYe1GsMRElw&t=0)


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

**Bedömning:** X A bättre  ☐ B bättre  ☐ Likvärdiga  ☐ Båda fel
Notering: B hämtade 08-21, 08-28, 08-30 och 09-02 som senaste två veckorna. Samma mönster som körning 1.

---

## Fråga 14

**Fråga:** Har det sagts något om open source-alternativ till stora AI-verktyg, både i videor och i artiklar?

---

### Läge A — Datummedveten (produktionens beteende)

**Tolkat läge:** Inget datumfilter, ingen rankning - obegränsad likhetssökning
**Kandidater övervägda:** 60  ·  **Chunks paketerade:** 30  ·  **prompt_eval_count:** 11378 (71% av num_ctx)  ·  **svarstid:** 15.3s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

Yes, multiple sources discuss open source alternatives to large AI tools:

Source [7] mentions "open source or open weight software" that "is tiny" and "can run on a snack studio," contrasting with "closed source models" that require "multiple racks" costing "millions of dollars," stating this "commoditizes high quality intelligence."

Source [8] refers to "open-source video generator, Miniax H3" as being used to create "interactive video game engine" called "H3 World."

Source [9] discusses "openw weight models versus the closed weight models" and notes OpenAI testing on "public models" like "GPT OSS or Deep Seagar 1" to verify performance.

Source [23] specifically mentions "GLM Flash" and "GLM 5.3" as "the best open model" and states "Tencent also releases their best model Hi 4, which is also open source" along with "Alibaba also releases their latest model Qwen 3.8 Flash Next."

Source [30] describes "new family of open models called Ornith 1.5" that uses "a self-improvement loop" where "the system proposes new problems and builds the tools or scaffolds needed to solve and verify those problems."

Source [4] identifies "the best open-source music generator available right now" as UA2, noting it's under "Apache 2 license" with model weights under "creative common non-commercial license."

**Källor (med feed date, för att se varför läget gav detta resultat):**

- **2026-09-14** — [Intelligence is Everywhere: Why the AI 'Race' is Already Over](https://www.youtube.com/watch?v=duv4A1gDZOY&t=190)
- **2026-09-06** — [GPT 6 Astra, Claude Fable 5.1, Gemini 3.8, realtime Minimax, new world models: AI NEWS](https://www.youtube.com/watch?v=ngyFRCNq0Yc&t=0)
- **2026-09-02** — [OpenAI, NVIDIA And Anthropic Just Split. Here's How I'd Spend $20, $60 Or $200.](https://www.youtube.com/watch?v=L9xXnPqVfnM&t=0)
- **2026-08-30** — [Ox Alpha reveal, realtime Minimax, Qwen Next, Hy4, robot olympics: AI NEWS](https://www.youtube.com/watch?v=4wjHNgMLeyY&t=0)
- **2026-08-23** — [New AI waifus, new Deepseek, realtime worlds, Happy Shrimp, tiny TTS: AI NEWS](https://www.youtube.com/watch?v=rQ4yX5qNYdY&t=410)
- **2026-09-15** — [Forget Suno. New BEST local AI music generator is here!](https://www.youtube.com/watch?v=9RtywbN--QE&t=1403)


### Läge B — Ren likhetssökning (inget datumfilter, ingen rankning)

**Tolkat läge:** Inget datumfilter, ingen rankning - obegränsad likhetssökning
**Kandidater övervägda:** 60  ·  **Chunks paketerade:** 30  ·  **prompt_eval_count:** 11378 (71% av num_ctx)  ·  **svarstid:** 16.7s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

Yes, the sources discuss several open source alternatives to large AI tools. Multiple videos mention open source models and tools:

- Source [1] mentions "a new state-of-the-art open-source model for predicting depth and surface normals," "a new top open-source music generator," and "a ton of open source AIs for reconstructing scenes in 3D."
- Source [3] discusses a project using multiple open models including "Kwen 3VL for understanding the scene, and then SAM 3 for segmentation, Flux 2 for filling in hidden parts of objects, and then finally High 3D Gen for 3D reconstruction."
- Source [4] states that "UA2 is definitely the best open-source music generator available right now."
- Source [7] mentions "open source or open weight software" that "is completely open source. It's tiny. It has a new architecture that is actually now can run on a snack studio."
- Source [8] references "several new open-source image generators and editors" and "new ways to make the best open video model miniacs run in real time."
- Source [9] discusses "the narrative of the open weight models versus the closed weight models."
- Source [14] mentions "openweight models" and how OpenAI tested "public models on purpose because it's much more verifiable."
- Source [18] mentions "new Deepseek" as an open source model.
- Source [23] states that "Tencent also releases their best model Hi 4, which is also open source" and "Alibaba also releases their latest model Qwen 3.8 Flash Next, which is also very close to Frontier."
- Source [25] references popular open source projects like "open claw with almost 400,000 stars or Hermes agent with 240,000 stars."
- Source [30] mentions "a new family of open models called Ornith 1.5" which uses a self-improvement loop for model development.

**Källor (med feed date, för att se varför läget gav detta resultat):**

- **2026-09-13** — [New Deepseek, human genome map, Navier Stokes, GPT finance, Suno v6, YuE2: AI NEWS](https://www.youtube.com/watch?v=nZYJdwM-_nI&t=0)
- **2026-08-30** — [Ox Alpha reveal, realtime Minimax, Qwen Next, Hy4, robot olympics: AI NEWS](https://www.youtube.com/watch?v=4wjHNgMLeyY&t=168)
- **2026-09-15** — [Forget Suno. New BEST local AI music generator is here!](https://www.youtube.com/watch?v=9RtywbN--QE&t=1403)
- **2026-09-14** — [Intelligence is Everywhere: Why the AI 'Race' is Already Over](https://www.youtube.com/watch?v=duv4A1gDZOY&t=190)
- **2026-09-06** — [GPT 6 Astra, Claude Fable 5.1, Gemini 3.8, realtime Minimax, new world models: AI NEWS](https://www.youtube.com/watch?v=ngyFRCNq0Yc&t=0)
- **2026-09-02** — [OpenAI, NVIDIA And Anthropic Just Split. Here's How I'd Spend $20, $60 Or $200.](https://www.youtube.com/watch?v=L9xXnPqVfnM&t=0)
- **2026-08-28** — [AI News: OpenAI Made a Massive Move Against NVIDIA](https://www.youtube.com/watch?v=TInwQglNkzo&t=0)
- **2026-08-23** — [New AI waifus, new Deepseek, realtime worlds, Happy Shrimp, tiny TTS: AI NEWS](https://www.youtube.com/watch?v=rQ4yX5qNYdY&t=1882)
- **2026-09-03** — [AI Software Factories Are the Next Big Thing (And I'm Building You One)](https://www.youtube.com/watch?v=DcLj_SO8JNk&t=464)


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

**Bedömning:** ☐ A bättre  ☐ B bättre  ☐ Likvärdiga  X Båda fel
Notering: Båda bara YouTube, ingen HF-källa. Kimi K3 och Proprietary-to-Open-Source saknas igen. Det semantiska gapet från Phase 2.

---

## Fråga 15

**Fråga:** Vad har hänt med AI-agenter den senaste veckan, i både papers och videor?

---

### Läge A — Datummedveten (produktionens beteende)

**Tolkat läge:** Datumfilter (tolkat från frågan): 2026-09-11 .. 2026-09-17
**Kandidater övervägda:** 60  ·  **Chunks paketerade:** 22  ·  **prompt_eval_count:** 7782 (49% av num_ctx)  ·  **svarstid:** 12.4s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

This week's AI agent developments include significant papers and videos on agent capabilities and applications:

Papers:
- Feyospace-v1 demonstrates an end-to-end framework for training open-weight cyber agents with 63.24% verified success rate on CyberGym [1].
- RSIAgent enables recursive self-improvement through autonomous exploration without training, allowing open-source models to outperform frontier closed-source models [9].
- Atria Dawn Preview is a foundation agentic model for scientific research and engineering workflows, achieving competitive performance across 16 benchmarks [13].
- Emergence World provides adversarial stress-testing for long-horizon multi-agent systems, revealing that individual agent safety doesn't guarantee system resilience [16].

Videos:
- AI agents are beginning to perform real-world transactions, with Stripe building systems for agents to make purchases within defined budgets (e.g., buying coffee) [19].
- "AI second brains" are evolving into "team brains" for collaborative productivity, saving approximately 20 hours weekly per user [3][10].
- Agents are moving beyond digital tasks to physical world interactions, including purchasing physical items like Mother's Day cards [21].
- Papers and videos discuss the growing trust in agents for routine tasks, with increasing capability to handle 100% reliable execution for specific tasks [19].

**Källor (med feed date, för att se varför läget gav detta resultat):**

- **2026-09-14** — [Feyospace-v1: How the Cyber Mercury Seven Trained Frontier Cyber Models](https://huggingface.co/papers/2609.08418)
- **2026-09-15** — [RSIAgent: Autonomous Exploration for Recursive Self-improvement in New Environments](https://huggingface.co/papers/2609.15364)
- **2026-09-15** — [Atria Dawn: The Dawn of Agentic Superintelligence](https://huggingface.co/papers/2609.15818)
- **2026-09-16** — [Emergence World: Adversarial Stress-Testing of Long-Horizon Multi-Agent Systems](https://huggingface.co/papers/2609.17320)
- **2026-09-17** — [AI Agents Are Starting To Buy. Stripe Is Building How They Pay.](https://www.youtube.com/watch?v=YTG0rdHPTDE&t=90)
- **2026-09-17** — [You Built Your AI Second Brain. Now What? (Here's How to Evolve It)](https://www.youtube.com/watch?v=mjQlZrteMIY&t=928)


### Läge B — Ren likhetssökning (inget datumfilter, ingen rankning)

**Tolkat läge:** Inget datumfilter, ingen rankning - obegränsad likhetssökning
**Kandidater övervägda:** 60  ·  **Chunks paketerade:** 32  ·  **prompt_eval_count:** 11662 (73% av num_ctx)  ·  **svarstid:** 19.4s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

Based on the provided sources, here's what has happened with AI agents in the past week:

GPT-6 Astra has been released and is rolling out on paid ChatGPT plans, API, and AWS [23]. Astra operates without specific instructions, as demonstrated when it was given "tens of thousands of emails, a calendar, a contact list, years of writing in a pile of unfinished work" and solved the problem on its own without being told how [27].

The Hugging Face incident (where 700 agents communicated and coordinated an attack) is being cited as a preview of what's to come with agents working together without human guidance [23].

Agents are creating more work for humans rather than taking jobs away - agent token usage is up 14-fold between February and August, and agents now burn more than five tokens for every single one a human burns [25].

A key problem identified is that "nobody told the agents what done means" before deployment - agents can do "an enormous amount of sophisticated, relentless work. And not one hour of that work was work that anybody wanted" [17].

Research papers show agents can complete engineering tasks but struggle with critical research elements like "poor judgment about the bar for publishable research" and "ineffective backtracking from dead ends" [10].

Agents are starting to make simple purchases (like buying coffee) with Stripe building systems for agents to pay, though they're not yet trusted for more complex transactions [18].

**Källor (med feed date, för att se varför läget gav detta resultat):**

- **2026-09-06** — [GPT-6 Astra Doesn't Need Your Instructions Anymore.](https://www.youtube.com/watch?v=1qGH6NwTj3o&t=263)
- **2026-08-26** — [Agents Aren't Taking Your Jobs. They're Creating More Work Instead.](https://www.youtube.com/watch?v=IpEaSa7tgfc&t=0)
- **2026-08-30** — [Runable Raised $21 Million On Agents That Finish. Nobody Told Yours What Done Means.](https://www.youtube.com/watch?v=qYe1GsMRElw&t=0)
- **2026-07-30** — [Can AI agents conduct open-ended AI research? Early evidence from two case studies](https://huggingface.co/papers/2607.27191)
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

---

# T-032 comparison — date-aware retrieval vs plain similarity search

Ankare (D-012, `vg09.store.latest_feed_date()`): **2026-09-17**

Samma 15 frågor, samma modell (`qwen3:30b-a3b`), körda genom hela pipelinen två gånger var: **Läge A** använder frågans egna tolkade datumfönster/rankningsläge (exakt som produktionen); **Läge B** kör obegränsad ren likhetssökning, inget datumfilter alls. Ingen modellbedömning, ingen automatisk poängsättning.

---
## Fråga 01

**Fråga:** I området Recursive self-improvement, vad är de två senaste nyheterna och vad handlar de om?

---

### Läge A — Datummedveten (produktionens beteende)

**Tolkat läge:** Rankningsläge (sortering efter senaste, inget datumfilter)
**Kandidater övervägda:** 60  ·  **Chunks paketerade:** 38  ·  **prompt_eval_count:** 12826 (80% av num_ctx)  ·  **svarstid:** 13.1s  ·  **done_reason:** stop

**Svar:**

The two most recent papers on Recursive Self-Improvement (RSI) are:

[37] ModularRSI: Modular and Generalizable Recursive Harness Self-Improvement - This paper proposes a modular framework for generalizable harness evolution. It decomposes the evolvable harness into five functional modules (Agent Loop, Tool Use, Observation Management, Context Management, and Task Completion Detection) that evolve independently within restricted modification scopes. The framework contrasts successful and failed trajectories to identify recurring behavioral deficiencies, aggregates evidence across tasks, and resolves conflicts during integration. Experiments show consistent improvements on unseen in-domain and cross-domain tasks, with the evolved harness transferring across different foundation models.

[38] The Last AI Built by Humans: Toward Genuine Recursive Self-Improvement - This paper introduces RSI concepts and its development roadmap, progressing from improvement-execution autonomy to recursive meta-improvement. It examines RSI across scenarios like scientific discovery, embodied intelligence, and software engineering, highlighting their distinct requirements and development speeds. The paper connects RSI research with practical systems, identifies key challenges to achieving genuine RSI, and uses the Headroom-Closed Index (HCI) to reveal problems with existing LLMs.

**Källor (med feed date, för att se varför läget gav detta resultat):**

- **2026-09-16** — [ModularRSI: Modular and Generalizable Recursive Harness Self-Improvement](https://huggingface.co/papers/2609.14857)
- **2026-09-16** — [The Last AI Built by Humans: Toward Genuine Recursive Self-Improvement](https://huggingface.co/papers/2609.11873)


### Läge B — Ren likhetssökning (inget datumfilter, ingen rankning)

**Tolkat läge:** Inget datumfilter, ingen rankning - obegränsad likhetssökning
**Kandidater övervägda:** 60  ·  **Chunks paketerade:** 37  ·  **prompt_eval_count:** 12864 (80% av num_ctx)  ·  **svarstid:** 17.2s  ·  **done_reason:** stop

**Svar:**

The two most recent news items about recursive self-improvement (RSI) are:

[24] ScienceBuddy: Recursive-in-Recursive Self-Improvement for Interactive Scientific Agents - This introduces ScienceBuddy, an interactive scientific research workspace that integrates continually improving scientific agents into researchers' workflows. It implements a recursive-in-recursive self-improvement paradigm that couples harness evolution (inner recursion) with model reinforcement learning (outer recursion), where the harness evolves while the model remains fixed, and the model is then trained under the improved harness.

[33] ModularRSI: Modular and Generalizable Recursive Harness Self-Improvement - This proposes a modular framework for generalizable harness evolution that contrasts successful and failed trajectories across tasks to identify recurring behavioral deficiencies. It decomposes the evolvable harness into five functional modules (Agent Loop, Tool Use, Observation Management, Context Management, and Task Completion Detection), each evolving independently within a restricted scope before integration, enabling consistent improvements on unseen in-domain and cross-domain tasks.

**Källor (med feed date, för att se varför läget gav detta resultat):**

- **2026-09-16** — [ScienceBuddy: Recursive-in-Recursive Self-Improvement for Interactive Scientific Agents](https://huggingface.co/papers/2609.17523)
- **2026-09-16** — [ModularRSI: Modular and Generalizable Recursive Harness Self-Improvement](https://huggingface.co/papers/2609.14857)


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
**Kandidater övervägda:** 60  ·  **Chunks paketerade:** 35  ·  **prompt_eval_count:** 12825 (80% av num_ctx)  ·  **svarstid:** 11.9s  ·  **done_reason:** stop

**Svar:**

Based on the provided sources, several significant developments have occurred with GUI agents in the past month:

A new benchmark called AnTrap was introduced to systematically evaluate GUI agent robustness against runtime anomalies, revealing universal vulnerability across models and proposing a taxonomy of four anomaly layers [17].

LLaDA-UI, a 16.7B-parameter block-wise diffusion vision-language GUI agent, was developed and shown to substantially outperform competitors like Qwen2.5-VL-7B and surpass Qwen3-VL-8B on four of six reported GUI benchmarks [18].

UI-Mate, a foundation GUI agent integrating environment-grounded training with in-context demonstration learning, set a new open-weight state of the art with 77.0% on OSWorld-Verified and 66.2% on WindowsAgentArena benchmarks [25].

UI-Venus-2 was presented as a general-purpose foundation GUI agent operating across mobile, web, and desktop environments with expanded coverage to over 170 multilingual mobile apps and native desktop systems, incorporating safety-aware mechanisms for controlled execution [29].

**Källor (med feed date, för att se varför läget gav detta resultat):**

- **2026-08-27** — [Are Android GUI Agents Robust Against Runtime Anomalies? AnTrap: Evaluating Agents in Dynamic Adversarial Environments](https://huggingface.co/papers/2608.24099)
- **2026-09-15** — [LLaDA-UI: Bringing Block-wise Diffusion to Vision-Language GUI Agents](https://huggingface.co/papers/2609.13287)
- **2026-08-18** — [UI-Mate: Advancing Open-Weight Foundation GUI Agents with In-Context Demonstrations](https://huggingface.co/papers/2608.15930)
- **2026-09-02** — [UI-Venus-2 Technical Report](https://huggingface.co/papers/2609.00028)


### Läge B — Ren likhetssökning (inget datumfilter, ingen rankning)

**Tolkat läge:** Inget datumfilter, ingen rankning - obegränsad likhetssökning
**Kandidater övervägda:** 60  ·  **Chunks paketerade:** 35  ·  **prompt_eval_count:** 12983 (81% av num_ctx)  ·  **svarstid:** 16.6s  ·  **done_reason:** stop

**Svar:**

In the last month, GUI agents have seen significant advancements with several new foundation models and techniques:

LLaDA-UI (2026-09-15) introduced a 16.7B-parameter block-wise diffusion vision-language GUI agent that outperforms existing models on GUI benchmarks [15]. UI-Mate (2026-08-18) established a new open-weight state-of-the-art with 77.0% on OSWorld-Verified and 66.2% on WindowsAgentArena, using in-context demonstration learning to improve long-horizon reliability [24]. 

UI-Venus-2 (2026-09-02) expanded environment coverage to over 170 multilingual mobile apps and native desktop systems, with a unified closed-loop reasoning-action framework for real-world deployment [28]. 

FocusMem (2026-08-06) improved latent memory for GUI agents by separating responsibilities within a compact interface, using role-aware content, state-conditioned readout, and a trust gate [17].

Qwen-UI-Agent (2026-07-31) achieved 82.1% on MobileWorld and 92.2% on MobileWorld-Real by combining diverse sandbox environments with a large-scale real-device mobile runtime [35]. 

Gated Hindsight Distillation (2026-08-11) improved task success by using next screenshots as privileged information during training, outperforming standard approaches on AndroidWorld and AndroidLab [18].

**Källor (med feed date, för att se varför läget gav detta resultat):**

- **2026-09-15** — [LLaDA-UI: Bringing Block-wise Diffusion to Vision-Language GUI Agents](https://huggingface.co/papers/2609.13287)
- **2026-08-18** — [UI-Mate: Advancing Open-Weight Foundation GUI Agents with In-Context Demonstrations](https://huggingface.co/papers/2608.15930)
- **2026-09-02** — [UI-Venus-2 Technical Report](https://huggingface.co/papers/2609.00028)
- **2026-08-06** — [FocusMem: Factorizing Content, Readout, and Trust in Latent GUI Memory](https://huggingface.co/papers/2608.04530)
- **2026-07-31** — [Qwen-UI-Agent Technical Report: Toward Next-Generation Real-World Centric Foundation GUI Agents](https://huggingface.co/papers/2607.28227)
- **2026-08-11** — [The Next Screenshot Knows: Gated Hindsight Distillation for Mobile GUI Agents](https://huggingface.co/papers/2608.06065)


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

---

## Fråga 03

**Fråga:** Vad är det absolut  senaste inom Video genereation och är det hårdvaru- eller mjukvarurelaterat?

---

### Läge A — Datummedveten (produktionens beteende)

**Tolkat läge:** Rankningsläge (sortering efter senaste, inget datumfilter)
**Kandidater övervägda:** 60  ·  **Chunks paketerade:** 36  ·  **prompt_eval_count:** 13005 (81% av num_ctx)  ·  **svarstid:** 13.7s  ·  **done_reason:** stop

**Svar:**

The absolute latest development in video generation is PhysStream [36], published on 2026-09-16. PhysStream is a software-based approach that enables physics-grounded image-to-video synthesis with structured scene memory and fine-grained motion control. It incorporates positional maps and object tracking derived from previously generated frames, and supports fine-grained motion control through sparse velocity-increment signals that encode physical quantities. This is a software innovation focused on improving physical consistency in video generation, not a hardware-related development. The approach achieves significant improvements over baselines in motion distribution distance and trajectory error while receiving strong human preference ratings.

**Källor (med feed date, för att se varför läget gav detta resultat):**

- **2026-09-16** — [PhysStream: Streaming Physics-Grounded Video Generation with Structured Scene Memory and Fine-Grained Motion Control](https://huggingface.co/papers/2609.17521)


### Läge B — Ren likhetssökning (inget datumfilter, ingen rankning)

**Tolkat läge:** Inget datumfilter, ingen rankning - obegränsad likhetssökning
**Kandidater övervägda:** 60  ·  **Chunks paketerade:** 37  ·  **prompt_eval_count:** 13056 (82% av num_ctx)  ·  **svarstid:** 15.2s  ·  **done_reason:** stop

**Svar:**

The absolute latest in video generation based on the provided sources is PhysStream, with a feed date of 2026-09-16 [16]. This is a software-based approach for physics-grounded video generation that incorporates structured scene memory and supports fine-grained motion control through sparse velocity-increment signals. It enables interactive, mid-generation control over multi-object tabletop rigid-body scenes without requiring the full control schedule before generation starts. The method achieves improvements in physical consistency (reducing motion distribution distance by 33% and trajectory error by 12% over baselines) and is preferred by human evaluators in over 85% of in-the-wild comparisons. This represents a software advancement in video generation rather than a hardware-related development.

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

**Bedömning:** ☐ A bättre  ☐ B bättre  X Likvärdiga  ☐ Båda fel

---

## Fråga 04

**Fråga:** Den senaste veckan, vad har sagts om Copding Agents. Vänligen sammanfatta.

---

### Läge A — Datummedveten (produktionens beteende)

**Tolkat läge:** Datumfilter (tolkat från frågan): 2026-09-11 .. 2026-09-17
**Kandidater övervägda:** 60  ·  **Chunks paketerade:** 22  ·  **prompt_eval_count:** 7936 (50% av num_ctx)  ·  **svarstid:** 11.4s  ·  **done_reason:** stop

**Svar:**

Based on the provided sources, here's a summary of what has been said about coding agents in the last week:

The YouTube video "My NEW FAVORITE Skill - Claude Code Drives My Whole Computer (Better Computer Use)" [17] discusses using coding agents for daily productivity, specifically mentioning that the speaker uses a coding agent to "get my morning set up" by opening browser tabs, desktop apps, Docker containers, and other applications, saving "a solid like 10, 15 minutes every single morning."

Another source, "GPT-6 Astra Just Made AI Software Factories Real" [14], describes a workflow where "coding agent authentication" is used with an AI software factory to build applications, with the speaker noting they "let it run through the whole thing off camera" to verify that "the triggering works and that all of the workflows work with our coding agent authentication."

The same video [12] also mentions security concerns when using coding agents, specifically warning about "prompt injection attacks" as a security consideration when operating with coding agents.

These sources (all with feed dates between September 11-15, 2026) present coding agents as tools for automating computer operations, with specific focus on practical productivity applications and security considerations.

**Källor (med feed date, för att se varför läget gav detta resultat):**

- **2026-09-15** — [My NEW FAVORITE Skill - Claude Code Drives My Whole Computer (Better Computer Use)](https://www.youtube.com/watch?v=SWEThyRHMgQ&t=77)
- **2026-09-12** — [GPT-6 Astra Just Made AI Software Factories Real (Here's How to Run One)](https://www.youtube.com/watch?v=joKb_QMmglM&t=914)


### Läge B — Ren likhetssökning (inget datumfilter, ingen rankning)

**Tolkat läge:** Inget datumfilter, ingen rankning - obegränsad likhetssökning
**Kandidater övervägda:** 60  ·  **Chunks paketerade:** 31  ·  **prompt_eval_count:** 11430 (71% av num_ctx)  ·  **svarstid:** 10.9s  ·  **done_reason:** stop

**Svar:**

Based on the provided sources from the last week, several key points about coding agents have been discussed:

Coding agents require careful configuration to be effective, with a focus on ensuring deterministic behavior through "hooks" that guarantee consistent execution rather than relying on probabilistic model behavior [14]. 

The most effective approach is to use a main coding agent that distributes work rather than complex multi-agent systems with communication, as these are deemed "not reliable" [22]. 

Overuse of sub-agents can lead to hitting rate limits, with one source noting 39% of usage coming from running multiple sessions in parallel [24]. 

Changing models mid-task ("escalating mid task") is discouraged as it taints the conversation context [24].

Experienced engineers initially viewed coding agents as "toys" but have become "addicted" to them as they've evolved, building skills and repositories of reusable agent workflows [25].

The field has progressed from initial skepticism to recognizing coding agents as valuable tools for completing actual work rather than just generating documentation [23].

**Källor (med feed date, för att se varför läget gav detta resultat):**

- **2026-08-27** — [Watch This If Your Coding Agent is Ignoring Your Rules (You Need Hooks)](https://www.youtube.com/watch?v=msfMqW92Y8Q&t=86)
- **2026-09-01** — [11 Tiny Coding Agent Fixes With A Stupid Amount Of Payoff](https://www.youtube.com/watch?v=UbylWXukvR8&t=786)
- **2026-08-25** — [BMAD's Founder on the Future of AI Coding (And the Slop Apocalypse)](https://www.youtube.com/watch?v=6XgSpFdD3EU&t=4952)
- **2026-08-30** — [Runable Raised $21 Million On Agents That Finish. Nobody Told Yours What Done Means.](https://www.youtube.com/watch?v=qYe1GsMRElw&t=258)


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
Notering: Facit missade två YouTube-videor inom fönstret (SWEThyRHMgQ 09-15, joKb_QMmglM 09-12). 
A:s källor är giltiga. 
B anger gamla källor som "senaste veckan"

---

## Fråga 05

**Fråga:** Har NeoHorse nämnts de senaste två veckorna?

---

### Läge A — Datummedveten (produktionens beteende)

**Tolkat läge:** Datumfilter (tolkat från frågan): 2026-09-04 .. 2026-09-17
**Kandidater övervägda:** 60  ·  **Chunks paketerade:** 26  ·  **prompt_eval_count:** 9634 (60% av num_ctx)  ·  **svarstid:** 8.0s  ·  **done_reason:** stop

**Svar:**

Yes, NeoHorse was mentioned in source [25] titled "NeoHorse-1: Towards Recursive Self-Improvement via Agentic Post-Training with Routing Harness" with a feed date of 2026-09-09. This date falls within the last two weeks relative to the latest feed dates provided in the sources (e.g., 2026-09-17 in source [19]).

**Källor (med feed date, för att se varför läget gav detta resultat):**

- **2026-09-09** — [NeoHorse-1: Towards Recursive Self-Improvement via Agentic Post-Training with Routing Harness](https://huggingface.co/papers/2609.08183)
- **2026-09-17** — [AI Agents Are Starting To Buy. Stripe Is Building How They Pay.](https://www.youtube.com/watch?v=YTG0rdHPTDE&t=257)


### Läge B — Ren likhetssökning (inget datumfilter, ingen rankning)

**Tolkat läge:** Inget datumfilter, ingen rankning - obegränsad likhetssökning
**Kandidater övervägda:** 60  ·  **Chunks paketerade:** 33  ·  **prompt_eval_count:** 12835 (80% av num_ctx)  ·  **svarstid:** 7.1s  ·  **done_reason:** stop

**Svar:**

No, "NeoHorse" is not mentioned in any of the provided sources. The sources discuss various AI models, news, and videos (like Claude Fable 5.1, Gemini 3.8, GPT-6 Astra, etc.), but there is no reference to "NeoHorse" in any of the provided excerpts.

**Källor (med feed date, för att se varför läget gav detta resultat):**

_Inga källor kunde kopplas till svaret._


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
**Kandidater övervägda:** 60  ·  **Chunks paketerade:** 35  ·  **prompt_eval_count:** 12701 (79% av num_ctx)  ·  **svarstid:** 19.8s  ·  **done_reason:** length ⚠ OFULLSTÄNDIGT

**Svar:**



**Källor (med feed date, för att se varför läget gav detta resultat):**

_Inga källor kunde kopplas till svaret._


### Läge B — Ren likhetssökning (inget datumfilter, ingen rankning)

**Tolkat läge:** Inget datumfilter, ingen rankning - obegränsad likhetssökning
**Kandidater övervägda:** 60  ·  **Chunks paketerade:** 36  ·  **prompt_eval_count:** 12986 (81% av num_ctx)  ·  **svarstid:** 18.4s  ·  **done_reason:** stop

**Svar:**

The most recent specific benchmark for coding agents is SWE-Bench Pro Verified [8], with a feed date of 2026-09-10. This verified version addresses reliability issues in the original SWE-Bench Pro benchmark, including reward hacking and task quality problems that inflated performance metrics. It introduces anti-hacking safeguards and task refinement to provide a more trustworthy evaluation of software engineering agents.

The most recent source overall is Benchmark Radar [18] (feed date 2026-09-14), which is a living database and search engine for AI benchmarks, including coding agent benchmarks, but it is not a new benchmark itself.

**Källor (med feed date, för att se varför läget gav detta resultat):**

- **2026-09-10** — [SWE-Bench Pro Verified: A Reliable Benchmark for Software Engineering Agents](https://huggingface.co/papers/2609.08149)
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
Notering: A gav tomt svar (done_reason: length). 
Resonemanget överskred num_predict trots fixen i T-028/T-038.

---

## Fråga 07

**Fråga:** Vad säger forskningen om text-to-video den senaste månaden?

---

### Läge A — Datummedveten (produktionens beteende)

**Tolkat läge:** Datumfilter (tolkat från frågan): 2026-08-17 .. 2026-09-17
**Kandidater övervägda:** 60  ·  **Chunks paketerade:** 37  ·  **prompt_eval_count:** 12748 (80% av num_ctx)  ·  **svarstid:** 19.6s  ·  **done_reason:** length ⚠ OFULLSTÄNDIGT

**Svar:**



**Källor (med feed date, för att se varför läget gav detta resultat):**

_Inga källor kunde kopplas till svaret._


### Läge B — Ren likhetssökning (inget datumfilter, ingen rankning)

**Tolkat läge:** Inget datumfilter, ingen rankning - obegränsad likhetssökning
**Kandidater övervägda:** 60  ·  **Chunks paketerade:** 38  ·  **prompt_eval_count:** 13023 (81% av num_ctx)  ·  **svarstid:** 18.3s  ·  **done_reason:** stop

**Svar:**

Based on the provided sources, the latest research on text-to-video (T2V) from the last month (as indicated by feed dates in September 2026) shows several key developments:

1. Researchers are developing more reliable evaluation methods for text-to-video models. FIRM-Video introduces a "check-before-score" framework that uses dimension-specific checklists to verify criteria against visual evidence before aggregation, improving evaluation accuracy for instruction following, world coherence, and perceptual quality [33].

2. Text-to-video models are becoming increasingly realistic, with DF26 showing human performance in detecting AI-generated videos is close to random chance (approximately 50% accuracy), highlighting how difficult it's becoming to distinguish synthetic videos from real ones [37].

3. New benchmarks are emerging that evaluate video generation beyond basic visual quality. FilmBench uses professional cinematic criteria (3 axes, 12 components, 35 metrics) to assess film-grade video generation, grounded in award-winning film prompts rather than web sources [35].

4. Research is addressing physical consistency in video generation. VideoCoCo introduces an agentic dual-engine system where executable Blender code serves as a chain-of-thought, significantly improving performance on benchmarks like PhyGenBench [36].

5. A controlled study (Moving Alphabet) confirms that training data distribution and caption quality significantly impact text-to-video model performance, with diverse data being critical for generalization [38].

**Källor (med feed date, för att se varför läget gav detta resultat):**

- **2026-08-27** — [FIRM-Video: Check Before You Score for Reliable Text-to-Video Reward Modeling](https://huggingface.co/papers/2608.21839)
- **2026-09-10** — [DF26: We Cannot Tell Fake From Real Anymore](https://huggingface.co/papers/2609.07369)
- **2026-07-28** — [FilmBench: A Film-Grade Benchmark for Cinematic Video Generation](https://huggingface.co/papers/2607.24241)
- **2026-07-31** — [VideoCoCo: Code-as-CoT for Physically-Consistent Video Generation via an Agentic Dual-Engine System](https://huggingface.co/papers/2607.27380)
- **2026-07-23** — [Moving Alphabet: A Controlled Study of Training Data for Text-to-Video Generation](https://huggingface.co/papers/2607.18789)


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

**Bedömning:** ☐ A bättre  ☐ B bättre  ☐ Likvärdiga  X Båda fel
Notering: A tomt svar (done_reason: length). 
B nämner FIRM-Video korrekt men anger juli-papers (Moving Alphabet m.fl.) som "senaste månaden".

---

## Fråga 08

**Fråga:** Nämns LEGO i någon artikel och i så fall, sammanfatta vad de handlar om.

---

### Läge A — Datummedveten (produktionens beteende)

**Tolkat läge:** Inget datumfilter, ingen rankning - obegränsad likhetssökning
**Kandidater övervägda:** 60  ·  **Chunks paketerade:** 38  ·  **prompt_eval_count:** 13015 (81% av num_ctx)  ·  **svarstid:** 8.5s  ·  **done_reason:** stop

**Svar:**

Yes, "LEGO" is mentioned in source [38], but it refers to "LEGO-RL" (not the toy brand), which is a framework for reinforcement learning for coding agents. 

LEGO-RL bridges native coding-agent harnesses with scalable policy-gradient optimization without modifying internal control flow. It's built on three pillars:
1) Faithful optimization via in-process LLM proxying for token-level alignment
2) Reliable execution via scalable sandbox orchestration to mitigate reward hacking
3) Observable training through integrated validation and monitoring tools

The framework was evaluated by training Qwen3.5-35B-A3B across three coding-agent harnesses, improving performance on SWE-bench Verified across all tested platforms (OpenHands SDK, Claude Code, and OpenCode) while maintaining high rollout-training probability correlation. [38]

**Källor (med feed date, för att se varför läget gav detta resultat):**

- **2026-08-19** — [LEGO-RL: Harness-Native Reinforcement Learning for Coding Agents](https://huggingface.co/papers/2608.17393)


### Läge B — Ren likhetssökning (inget datumfilter, ingen rankning)

**Tolkat läge:** Inget datumfilter, ingen rankning - obegränsad likhetssökning
**Kandidater övervägda:** 60  ·  **Chunks paketerade:** 38  ·  **prompt_eval_count:** 13015 (81% av num_ctx)  ·  **svarstid:** 7.1s  ·  **done_reason:** stop

**Svar:**

Yes, LEGO is mentioned in source [38]. The source is titled "LEGO-RL: Harness-Native Reinforcement Learning for Coding Agents" and describes LEGO-RL as a framework that bridges native coding-agent harnesses with scalable policy-gradient optimization without modifying their internal control flow. The framework addresses misalignment between coding agent harnesses and policy-gradient training through three pillars: (1) faithful optimization via in-process LLM proxying, (2) reliable execution via scalable sandbox orchestration, and (3) observable training through an integrated plugin. The evaluation showed LEGO-RL improved Qwen3.5-35B-A3B performance across multiple coding agent harnesses on SWE-bench Verified, while maintaining a high rollout-training probability correlation above 0.99.

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
**Kandidater övervägda:** 60  ·  **Chunks paketerade:** 34  ·  **prompt_eval_count:** 12824 (80% av num_ctx)  ·  **svarstid:** 7.6s  ·  **done_reason:** stop

**Svar:**

No, AutoDev is not mentioned in any of the provided sources. The sources mention several AI-related terms with "Auto" prefixes such as AutoResearch [6], AutoSaddler [14], and AutoDesign [20], but there is no reference to "AutoDev" in any of the provided excerpts.

**Källor (med feed date, för att se varför läget gav detta resultat):**

- **2026-08-25** — [AutoResearch: Insight In, Hallucination Out](https://huggingface.co/papers/2608.17906)
- **2026-08-26** — [AutoSaddler: Automatic Harness Optimization with Durable Updates from Agent Execution Traces](https://huggingface.co/papers/2608.23041)
- **2026-08-14** — [AutoDesign: Meta-Harness Optimization for Long-Horizon Agentic Design](https://huggingface.co/papers/2608.13560)


### Läge B — Ren likhetssökning (inget datumfilter, ingen rankning)

**Tolkat läge:** Inget datumfilter, ingen rankning - obegränsad likhetssökning
**Kandidater övervägda:** 60  ·  **Chunks paketerade:** 34  ·  **prompt_eval_count:** 12824 (80% av num_ctx)  ·  **svarstid:** 6.1s  ·  **done_reason:** stop

**Svar:**

No, "AutoDev" is not mentioned in any of the provided sources. The sources mention "AutoResearch" [6], "AutoSaddler" [14], and "AutoDesign" [20], but there is no mention of "AutoDev" in any of the provided excerpts.

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
**Kandidater övervägda:** 37  ·  **Chunks paketerade:** 22  ·  **prompt_eval_count:** 7455 (47% av num_ctx)  ·  **svarstid:** 8.2s  ·  **done_reason:** stop

**Svar:**

On September 16, 2026, 20 research papers were published on Hugging Face covering various AI topics, along with two YouTube videos about a "spy tool" (sources [21] and [22]).

Key research highlights include:
- ModAR: A world-action model that autoregressively denoises multiple future modalities [1]
- Decoy Direction Optimization (DDO): A post-hoc defense against LLM refusal feature ablation attacks [2]
- Gavel: A system that elicits native skill routing from frozen LLMs without context [3]
- StepAudio 3 Realtime: An audio-language foundation model with "Think-While-Speaking" capability [9]
- HarnessVLN: A training-free framework for embodied navigation [10]
- PhysStream: A physics-grounded video generation model with structured scene memory [11]
- ScienceBuddy: An interactive scientific research workspace with recursive self-improvement [20]

The YouTube videos ([21] and [22]) discuss a "free and open-source spy tool" that the creators describe as giving "power back in our own hands" for information gathering and understanding the world, with the creators emphasizing it's "harmless" and "doesn't step on anybody's rights or privacy."

**Källor (med feed date, för att se varför läget gav detta resultat):**

- **2026-09-16** — [He Built The Ultimate Spy Tool (Free and Open-Source)](https://www.youtube.com/watch?v=S2VJU5DQqlU&t=1268)
- **2026-09-16** — [Modality-Autoregressive World-Action Models](https://huggingface.co/papers/2609.17524)
- **2026-09-16** — [Decoy Direction Optimization: A Post-Hoc Defense Against LLM Abliteration](https://huggingface.co/papers/2609.16204)
- **2026-09-16** — [The Router Within: Eliciting Native Skill Routing from a Frozen LLM](https://huggingface.co/papers/2609.15982)
- **2026-09-16** — [StepAudio 3 Realtime Technical Report](https://huggingface.co/papers/2609.14005)
- **2026-09-16** — [HarnessVLN: Unifying Training-Free Embodied Navigation through an Agent Harness](https://huggingface.co/papers/2609.15195)
- **2026-09-16** — [PhysStream: Streaming Physics-Grounded Video Generation with Structured Scene Memory and Fine-Grained Motion Control](https://huggingface.co/papers/2609.17521)
- **2026-09-16** — [ScienceBuddy: Recursive-in-Recursive Self-Improvement for Interactive Scientific Agents](https://huggingface.co/papers/2609.17523)


### Läge B — Ren likhetssökning (inget datumfilter, ingen rankning)

**Tolkat läge:** Inget datumfilter, ingen rankning - obegränsad likhetssökning
**Kandidater övervägda:** 60  ·  **Chunks paketerade:** 35  ·  **prompt_eval_count:** 13102 (82% av num_ctx)  ·  **svarstid:** 8.2s  ·  **done_reason:** stop

**Svar:**

The only source with a feed date of 2026-09-16 is [4], which is about "He Built The Ultimate Spy Tool (Free and Open-Source)". According to this source, the video showcases a free and open-source spy tool that the creator (Balavo) built, with links to the GitHub repository provided in the description. The video was published on September 16, 2026, as indicated in the feed date.

**Källor (med feed date, för att se varför läget gav detta resultat):**

- **2026-09-16** — [He Built The Ultimate Spy Tool (Free and Open-Source)](https://www.youtube.com/watch?v=S2VJU5DQqlU&t=1268)


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

---

## Fråga 11

**Fråga:** Vad hände i forskningen förra veckan?

---

### Läge A — Datummedveten (produktionens beteende)

**Tolkat läge:** Datumfilter (tolkat från frågan): 2026-09-11 .. 2026-09-17
**Kandidater övervägda:** 60  ·  **Chunks paketerade:** 31  ·  **prompt_eval_count:** 11216 (70% av num_ctx)  ·  **svarstid:** 16.8s  ·  **done_reason:** stop

**Svar:**

Last week saw significant advancements in several AI research areas. Key developments include:

- A new benchmark (MetroLLM-Bench) was introduced for evaluating language models as transit kiosk runtimes, with a 4B Qwen 3.5 student model outperforming both GPT-5.6 tiers on Tier 1 scoring [5].

- ModularRSI was proposed as a benchmark-disjoint, contrastive, and modular framework for generalizable harness evolution in AI agents, showing consistent improvements on unseen tasks [2].

- ReactHuman, the first physics-grounded benchmark for human-like reactive decision-making, was introduced to test embodied multimodal LLMs' ability to respond to sudden physical hazards [6].

- Emergence World was presented as a continuously running multi-agent environment for adversarial stress-testing of long-horizon autonomous systems, revealing that model-level alignment is not compositional [9].

- Lightning Weave was introduced to improve the accuracy-efficiency frontier of reasoning models through capability composition, raising HMMT 2025 accuracy from 59.2% to 64.0% while using 10.7% fewer response tokens [14].

- E2A-Bench was created to evaluate evidence-to-action reliability in financial chart reasoning, highlighting failures hidden by traditional hallucination scores [8].

These research papers were published between September 11-17, 2026, with many appearing on September 16-17, 2026.

**Källor (med feed date, för att se varför läget gav detta resultat):**

- **2026-09-11** — [MetroLLM-Bench: Evaluating Language Models as Transit Kiosk Runtimes](https://huggingface.co/papers/2609.10016)
- **2026-09-16** — [ModularRSI: Modular and Generalizable Recursive Harness Self-Improvement](https://huggingface.co/papers/2609.14857)
- **2026-09-14** — [ReactHuman: A Physics-Grounded Benchmark for Human-Like Reactive Decision-Making in Embodied Multimodal LLMs](https://huggingface.co/papers/2609.10895)
- **2026-09-16** — [Emergence World: Adversarial Stress-Testing of Long-Horizon Multi-Agent Systems](https://huggingface.co/papers/2609.17320)
- **2026-09-15** — [Lightning Weave: Improving the Accuracy-Efficiency Frontier of Reasoning Models through Capability Composition](https://huggingface.co/papers/2609.14708)
- **2026-09-15** — [E2A-Bench: Benchmarking Evidence-to-Action Reliability in Financial Chart Reasoning](https://huggingface.co/papers/2609.14302)


### Läge B — Ren likhetssökning (inget datumfilter, ingen rankning)

**Tolkat läge:** Inget datumfilter, ingen rankning - obegränsad likhetssökning
**Kandidater övervägda:** 60  ·  **Chunks paketerade:** 36  ·  **prompt_eval_count:** 12913 (81% av num_ctx)  ·  **svarstid:** 18.9s  ·  **done_reason:** length ⚠ OFULLSTÄNDIGT

**Svar:**



**Källor (med feed date, för att se varför läget gav detta resultat):**

_Inga källor kunde kopplas till svaret._


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
Notering: B tomt svar (done_reason: length).

---

## Fråga 12

**Fråga:** Har Palantir nämnts i någon video?

---

### Läge A — Datummedveten (produktionens beteende)

**Tolkat läge:** Inget datumfilter, ingen rankning - obegränsad likhetssökning
**Kandidater övervägda:** 60  ·  **Chunks paketerade:** 35  ·  **prompt_eval_count:** 12887 (81% av num_ctx)  ·  **svarstid:** 9.4s  ·  **done_reason:** stop

**Svar:**

I've carefully reviewed all the provided sources and found no mention of "Har Palantir" or Palantir (the AI company) in any of the videos or papers listed. The question appears to be asking about Palantir, but none of the sources reference this company.

[1] [2] [3] [4] [5] [6] [7] [8] [9] [10] [11] [12] [13] [14] [15] [16] [17] [18] [19] [20] [21] [22] [23] [24] [25] [26] [27] [28] [29] [30] [31] [32] [33] [34] [35]

**Källor (med feed date, för att se varför läget gav detta resultat):**

- **2026-09-11** — [AI News: The AI World is REALLY Scared Right Now](https://www.youtube.com/watch?v=JwTCjarfJYw&t=2063)
- **2026-08-25** — [BMAD's Founder on the Future of AI Coding (And the Slop Apocalypse)](https://www.youtube.com/watch?v=6XgSpFdD3EU&t=1405)
- **2026-08-28** — [PAWBench: How Far Are We from Probabilistically Aligned World Modeling?](https://huggingface.co/papers/2608.27345)
- **2026-09-13** — [New Deepseek, human genome map, Navier Stokes, GPT finance, Suno v6, YuE2: AI NEWS](https://www.youtube.com/watch?v=nZYJdwM-_nI&t=574)
- **2026-09-06** — [GPT 6 Astra, Claude Fable 5.1, Gemini 3.8, realtime Minimax, new world models: AI NEWS](https://www.youtube.com/watch?v=ngyFRCNq0Yc&t=89)
- **2026-08-30** — [Ox Alpha reveal, realtime Minimax, Qwen Next, Hy4, robot olympics: AI NEWS](https://www.youtube.com/watch?v=4wjHNgMLeyY&t=168)
- **2026-09-04** — [RoboTok: An Internet-Scale Data Engine for Human Demonstration Retrieval and Dexterous Manipulation Learning](https://huggingface.co/papers/2609.03199)
- **2026-08-06** — [HelloWorld: Enabling Socially Interactive Characters in Video World Models](https://huggingface.co/papers/2608.05070)
- **2026-09-04** — [Scal3R: Learning Efficient Multi-Relative Pose Query for Scalable Online 3D Reconstruction](https://huggingface.co/papers/2609.04201)
- **2026-08-21** — [AI News: OpenAI Just Put the Brakes on AI](https://www.youtube.com/watch?v=EfGF7QbJItA&t=1104)
- **2026-08-26** — [I Built a FREE App That Runs Your Entire Business](https://www.youtube.com/watch?v=rKo9iLGjUbs&t=583)
- **2026-09-04** — [Everyone's Testing Claude Fable 5.1 On Code. It Made Me A 37-Second Film.](https://www.youtube.com/watch?v=55rDzRkUVdE&t=782)
- **2026-09-03** — [The Most Overhyped and Underhyped New AI Models](https://www.youtube.com/watch?v=Po_Dh7WLgmM&t=0)
- **2026-08-23** — [New AI waifus, new Deepseek, realtime worlds, Happy Shrimp, tiny TTS: AI NEWS](https://www.youtube.com/watch?v=rQ4yX5qNYdY&t=169)
- **2026-09-06** — [GPT-6 Astra Doesn't Need Your Instructions Anymore.](https://www.youtube.com/watch?v=1qGH6NwTj3o&t=1586)
- **2026-09-09** — [I Asked GPT-6 Astra to Build an AI Slop Detector](https://www.youtube.com/watch?v=-KcHn0QcSb0&t=791)
- **2026-09-07** — [GPT 6 Astra is a freak](https://www.youtube.com/watch?v=Ji4amrxrzVM&t=1112)
- **2026-09-15** — [BVB: Benchmarking Agentic Video Understanding via Programmatic Reconstruction in Blender](https://huggingface.co/papers/2609.15478)
- **2026-09-04** — [AI News: The Most Insane Week So Far This Year!](https://www.youtube.com/watch?v=GfPZm9yucQo&t=1788)
- **2026-08-28** — [AI News: OpenAI Made a Massive Move Against NVIDIA](https://www.youtube.com/watch?v=TInwQglNkzo&t=1535)
- **2026-09-16** — [He Built The Ultimate Spy Tool (Free and Open-Source)](https://www.youtube.com/watch?v=S2VJU5DQqlU&t=1268)
- **2026-09-03** — [GPT-6 Astra Is Finally Here (And It’s REALLY Good)](https://www.youtube.com/watch?v=GGzT7zVrRTU&t=0)


### Läge B — Ren likhetssökning (inget datumfilter, ingen rankning)

**Tolkat läge:** Inget datumfilter, ingen rankning - obegränsad likhetssökning
**Kandidater övervägda:** 60  ·  **Chunks paketerade:** 35  ·  **prompt_eval_count:** 12887 (81% av num_ctx)  ·  **svarstid:** 7.2s  ·  **done_reason:** stop

**Svar:**

No, Palantir has not been mentioned in any of the provided video sources. After reviewing all 35 sources, there is no mention of the company Palantir. There is a possible typo in source [35] where "Palunteer" appears in a quote ("I had to ask Baval and who is this even for? a lot of things. Like some people are using it for content creation. So they're using it in their like when they want those"), but this appears to be a mishearing or misspelling of something else and not a reference to the Palantir company.

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
Notering: B hittade "Palunteer" men avfärdade det som felhörning. 
A räknade upp [1]–[35] och fick 22 falska källor.

---

## Fråga 13

**Fråga:** Vad har sagts om OpenAI de senaste två veckorna?

---

### Läge A — Datummedveten (produktionens beteende)

**Tolkat läge:** Datumfilter (tolkat från frågan): 2026-09-04 .. 2026-09-17
**Kandidater övervägda:** 60  ·  **Chunks paketerade:** 26  ·  **prompt_eval_count:** 9699 (61% av num_ctx)  ·  **svarstid:** 11.1s  ·  **done_reason:** stop

**Svar:**

Based on the provided sources from the last two weeks (2026-09-04 to 2026-09-17), several key points have been made about OpenAI:

GPT-6 Astra was released by OpenAI and is rolling out across all paid ChatGPT plans, the API, and AWS [23][25]. This model is described as "destroying all the other models" [10][17] and has been tested for its ability to build AI software factories autonomously [1][9].

There is debate about whether Astra represents AGI (Artificial General Intelligence), with some claiming "we have AGI" but others noting that internally at OpenAI they have models significantly more capable than Astra [9][20].

OpenAI introduced "Chat GPT for financial services" which combines GPT6 Astra with financial data sets and tools for producing banking research [19].

The sources also mention that OpenAI's Astra system can handle complex tasks without constant human instruction, with examples of it building a personal knowledge system after being given "tens of thousands of emails, years of writing, calendar contacts" and left "alone for five days" [25].

**Källor (med feed date, för att se varför läget gav detta resultat):**

- **2026-09-06** — [GPT-6 Astra Doesn't Need Your Instructions Anymore.](https://www.youtube.com/watch?v=1qGH6NwTj3o&t=263)
- **2026-09-06** — [GPT 6 Astra, Claude Fable 5.1, Gemini 3.8, realtime Minimax, new world models: AI NEWS](https://www.youtube.com/watch?v=ngyFRCNq0Yc&t=2022)
- **2026-09-12** — [GPT-6 Astra Just Made AI Software Factories Real (Here's How to Run One)](https://www.youtube.com/watch?v=joKb_QMmglM&t=914)
- **2026-09-11** — [AI News: The AI World is REALLY Scared Right Now](https://www.youtube.com/watch?v=JwTCjarfJYw&t=1220)
- **2026-09-13** — [New Deepseek, human genome map, Navier Stokes, GPT finance, Suno v6, YuE2: AI NEWS](https://www.youtube.com/watch?v=nZYJdwM-_nI&t=1940)


### Läge B — Ren likhetssökning (inget datumfilter, ingen rankning)

**Tolkat läge:** Inget datumfilter, ingen rankning - obegränsad likhetssökning
**Kandidater övervägda:** 60  ·  **Chunks paketerade:** 34  ·  **prompt_eval_count:** 12825 (80% av num_ctx)  ·  **svarstid:** 18.6s  ·  **done_reason:** stop

**Svar:**

Based on the provided sources with feed dates within the last two weeks (2026-09-04 to 2026-09-16), the following has been said about OpenAI:

GPT-6 Astra was released on September 3, 2026, and is rolling out across all paid ChatGPT plans, the API, and AWS [12][15][23][29]. Early users have reported impressive capabilities, with one user (Ethan Mollett) giving Astra tens of thousands of emails, years of writing, and calendar contacts, then leaving it to work for five days. The system built a personal knowledge system without human intervention [23][29].

OpenAI has also developed a new AI inference chip called "jalapeno" to reduce reliance on NVIDIA, with tests showing up to 104 times performance improvement on open-weight models [26][28][30].

OpenAI is using a new training technique called "recurrent depth" or "looped transformer" for GPT-6 Astra, which processes the same text multiple times to improve answers, though it obscures the AI's reasoning process [25].

The company has paused reinforcement learning training on their latest models for safety reasons, with their largest planned frontier reinforcement learning run remaining on hold while they conduct smaller scale training and evaluation [32].

OpenAI introduced "ChatGPT images 2.5," an improved image model that's better at transforming familiar subjects, visual styles, and compositions with greater consistency [31].

OpenAI also launched "ChatGPT for financial services," combining GPT-6 Astra with financial datasets and tools for producing banking research [17].

**Källor (med feed date, för att se varför läget gav detta resultat):**

- **2026-09-03** — [GPT-6 Astra Is Finally Here (And It’s REALLY Good)](https://www.youtube.com/watch?v=GGzT7zVrRTU&t=1024)
- **2026-09-06** — [GPT-6 Astra Doesn't Need Your Instructions Anymore.](https://www.youtube.com/watch?v=1qGH6NwTj3o&t=263)
- **2026-09-02** — [OpenAI, NVIDIA And Anthropic Just Split. Here's How I'd Spend $20, $60 Or $200.](https://www.youtube.com/watch?v=L9xXnPqVfnM&t=177)
- **2026-08-28** — [AI News: OpenAI Made a Massive Move Against NVIDIA](https://www.youtube.com/watch?v=TInwQglNkzo&t=0)
- **2026-09-03** — [The Most Overhyped and Underhyped New AI Models](https://www.youtube.com/watch?v=Po_Dh7WLgmM&t=1246)
- **2026-08-21** — [AI News: OpenAI Just Put the Brakes on AI](https://www.youtube.com/watch?v=EfGF7QbJItA&t=1104)
- **2026-09-11** — [AI News: The AI World is REALLY Scared Right Now](https://www.youtube.com/watch?v=JwTCjarfJYw&t=2)
- **2026-09-13** — [New Deepseek, human genome map, Navier Stokes, GPT finance, Suno v6, YuE2: AI NEWS](https://www.youtube.com/watch?v=nZYJdwM-_nI&t=1940)


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
Notering: B hämtade innehåll från 08-21, 08-28 och 09-02 och angav det som senaste två veckorna.

---

## Fråga 14

**Fråga:** Har det sagts något om open source-alternativ till stora AI-verktyg, både i videor och i artiklar?

---

### Läge A — Datummedveten (produktionens beteende)

**Tolkat läge:** Inget datumfilter, ingen rankning - obegränsad likhetssökning
**Kandidater övervägda:** 60  ·  **Chunks paketerade:** 34  ·  **prompt_eval_count:** 12906 (81% av num_ctx)  ·  **svarstid:** 18.8s  ·  **done_reason:** length ⚠ OFULLSTÄNDIGT

**Svar:**



**Källor (med feed date, för att se varför läget gav detta resultat):**

_Inga källor kunde kopplas till svaret._


### Läge B — Ren likhetssökning (inget datumfilter, ingen rankning)

**Tolkat läge:** Inget datumfilter, ingen rankning - obegränsad likhetssökning
**Kandidater övervägda:** 60  ·  **Chunks paketerade:** 34  ·  **prompt_eval_count:** 12906 (81% av num_ctx)  ·  **svarstid:** 14.6s  ·  **done_reason:** stop

**Svar:**

Yes, several sources mention open source alternatives to large AI tools:

[3] Mentions OreoLook (formerly lixSearch), an open-source answer engine using automated browser agents and provider-routed LLM inference.

[6] References LM Studio and Ollama as options for running local models offline, allowing users to avoid cloud providers.

[7] Discusses multiple open source models including Kwen 3VL, SAM 3, Flux 2, and High 3D Gen, noting that "they've released everything already" for local use.

[8] Describes UA2 as "the best open-source music generator available right now" with Apache 2 licensing.

[10] Explicitly states the "Ultimate Spy Tool" is "Free and Open-Source."

[11] Mentions "It's completely open source. It's tiny. It has a new architecture that is actually now can run on a snack studio, whereas these other closed source devices or closed source models are running on multiple racks."

[27] Notes that GLM Flash and GLM 5.3 are "the best open model you can use right now" and that Tencent's Hi 4 and Alibaba's Qwen 3.8 Flash Next are "also open source."

[29] References popular open source projects like "open claw with almost 400,000 stars" and "Hermes agent with 240,000 stars."

[34] Discusses "Ornith 1.5" as "a family of open-source models" that use a self-improvement loop for training.

**Källor (med feed date, för att se varför läget gav detta resultat):**

- **2026-09-10** — [A Three-Layer Caching Architecture for Low-Latency LLM Web Search on Commodity CPU Hardware](https://huggingface.co/papers/2609.05463)
- **2026-08-26** — [I Built a FREE App That Runs Your Entire Business](https://www.youtube.com/watch?v=rKo9iLGjUbs&t=1407)
- **2026-08-30** — [Ox Alpha reveal, realtime Minimax, Qwen Next, Hy4, robot olympics: AI NEWS](https://www.youtube.com/watch?v=4wjHNgMLeyY&t=168)
- **2026-09-15** — [Forget Suno. New BEST local AI music generator is here!](https://www.youtube.com/watch?v=9RtywbN--QE&t=1403)
- **2026-09-16** — [He Built The Ultimate Spy Tool (Free and Open-Source)](https://www.youtube.com/watch?v=S2VJU5DQqlU&t=1186)
- **2026-09-14** — [Intelligence is Everywhere: Why the AI 'Race' is Already Over](https://www.youtube.com/watch?v=duv4A1gDZOY&t=190)
- **2026-09-03** — [AI Software Factories Are the Next Big Thing (And I'm Building You One)](https://www.youtube.com/watch?v=DcLj_SO8JNk&t=464)
- **2026-08-23** — [New AI waifus, new Deepseek, realtime worlds, Happy Shrimp, tiny TTS: AI NEWS](https://www.youtube.com/watch?v=rQ4yX5qNYdY&t=410)


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
Notering: A tomt svar (length). 
B klarar YouTube-sidan (9RtywbN--QE) men HF-källan kopplar inte till ett namngivet proprietärt verktyg. 
Kimi K3 och Proprietary-to-Open-Source hittades inte.

---

## Fråga 15

**Fråga:** Vad har hänt med AI-agenter den senaste veckan, i både papers och videor?

---

### Läge A — Datummedveten (produktionens beteende)

**Tolkat läge:** Datumfilter (tolkat från frågan): 2026-09-11 .. 2026-09-17
**Kandidater övervägda:** 60  ·  **Chunks paketerade:** 22  ·  **prompt_eval_count:** 7782 (49% av num_ctx)  ·  **svarstid:** 9.4s  ·  **done_reason:** stop

**Svar:**

This week has seen significant developments in AI agents across both papers and videos:

In papers, researchers demonstrated:
- Feyospace-v1's framework for training cyber agents with 164,269 verified trajectories, achieving 63.24% success rate on CyberGym [1]
- Agent as Policy (AGP) enabling general-purpose agents to drive physical robots without task-specific training, achieving 100% success on some manipulation tasks [2]
- RSIAgent's autonomous exploration framework for recursive self-improvement in new environments [9]
- Atria Dawn, a foundation agentic model designed for scientific research and engineering workflows [13]
- Emergence World's multi-agent environment for adversarial stress testing of long-horizon systems [16]

In videos, key developments include:
- AI second brains evolving into team brains for business collaboration, with claims of saving 20+ hours weekly [3][10]
- Agents capable of performing real-world tasks like buying coffee (though not yet couches or subscriptions) [19][21]
- Stripe building payment systems to enable agents to make transactions [19]
- GPT-6 Astra enabling 24/7 AI software factories for application development [8]
- Discussions about agents potentially becoming central to user workflows, shifting loyalty away from device manufacturers like Apple [6][11]

**Källor (med feed date, för att se varför läget gav detta resultat):**

- **2026-09-14** — [Feyospace-v1: How the Cyber Mercury Seven Trained Frontier Cyber Models](https://huggingface.co/papers/2609.08418)
- **2026-09-15** — [Agent as Policy for Robotic Manipulation](https://huggingface.co/papers/2609.12541)
- **2026-09-15** — [RSIAgent: Autonomous Exploration for Recursive Self-improvement in New Environments](https://huggingface.co/papers/2609.15364)
- **2026-09-15** — [Atria Dawn: The Dawn of Agentic Superintelligence](https://huggingface.co/papers/2609.15818)
- **2026-09-16** — [Emergence World: Adversarial Stress-Testing of Long-Horizon Multi-Agent Systems](https://huggingface.co/papers/2609.17320)
- **2026-09-17** — [You Built Your AI Second Brain. Now What? (Here's How to Evolve It)](https://www.youtube.com/watch?v=mjQlZrteMIY&t=928)
- **2026-09-17** — [AI Agents Are Starting To Buy. Stripe Is Building How They Pay.](https://www.youtube.com/watch?v=YTG0rdHPTDE&t=90)
- **2026-09-12** — [GPT-6 Astra Just Made AI Software Factories Real (Here's How to Run One)](https://www.youtube.com/watch?v=joKb_QMmglM&t=914)
- **2026-09-14** — [Sam Altman and Apple's New CEO are Fighting Over One Thing. It's Not What You Think.](https://www.youtube.com/watch?v=XIt87tJHm-g&t=1429)


### Läge B — Ren likhetssökning (inget datumfilter, ingen rankning)

**Tolkat läge:** Inget datumfilter, ingen rankning - obegränsad likhetssökning
**Kandidater övervägda:** 60  ·  **Chunks paketerade:** 35  ·  **prompt_eval_count:** 12794 (80% av num_ctx)  ·  **svarstid:** 18.7s  ·  **done_reason:** stop

**Svar:**

This week has seen significant developments in AI agents across both research papers and videos:

GPT-6 Astra represents a major advancement, described as "AGI is here" [30] because it can solve complex problems without specific instructions, operating autonomously for extended periods. This has been highlighted in multiple videos [26, 31].

A key focus is on defining "what done means" for agents, with Runable raising $21 million for this purpose [18]. The video explains that agents often do "enormous amounts of sophisticated, relentless work" that isn't actually what businesses want [20].

AI agents are starting to make real-world purchases, with Stripe building payment systems for agents to buy things like coffee or send physical cards [21, 27].

Research shows agents are "Creating More Work Instead" of taking jobs, with evidence that agent token usage has increased 14-fold between February and August [12]. OpenAI reports its heaviest codex users generate over 60 hours of agent activity daily [28].

New frameworks are emerging, including "ComBodied Agents" which focuses on human-centered AI that models and supports individual human-state trajectories [3], and "WikiSkill" which compiles agent experience into persistent knowledge for skill evolution [9].

Multi-agent systems are being stress-tested through "Emergence World," which runs eight parallel worlds of ten agents each to evaluate safety and resilience [10].

**Källor (med feed date, för att se varför läget gav detta resultat):**

- **2026-09-06** — [GPT-6 Astra Doesn't Need Your Instructions Anymore.](https://www.youtube.com/watch?v=1qGH6NwTj3o&t=0)
- **2026-09-03** — [GPT-6 Astra Is Finally Here (And It’s REALLY Good)](https://www.youtube.com/watch?v=GGzT7zVrRTU&t=1024)
- **2026-08-30** — [Runable Raised $21 Million On Agents That Finish. Nobody Told Yours What Done Means.](https://www.youtube.com/watch?v=qYe1GsMRElw&t=176)
- **2026-09-17** — [AI Agents Are Starting To Buy. Stripe Is Building How They Pay.](https://www.youtube.com/watch?v=YTG0rdHPTDE&t=90)
- **2026-08-26** — [Agents Aren't Taking Your Jobs. They're Creating More Work Instead.](https://www.youtube.com/watch?v=IpEaSa7tgfc&t=1785)
- **2026-08-12** — [ComBodied Agents: a New Paradigm of Human-Centric Agentic AI](https://huggingface.co/papers/2608.10915)
- **2026-08-28** — [WikiSkill: Compiling Agent Experience into Persistent Knowledge for Skill Evolution](https://huggingface.co/papers/2608.27454)
- **2026-09-16** — [Emergence World: Adversarial Stress-Testing of Long-Horizon Multi-Agent Systems](https://huggingface.co/papers/2609.17320)


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

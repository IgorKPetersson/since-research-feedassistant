# T-033 comparison — qwen3:30b-a3b vs qwen3:8b (D-005's VRAM-differentiated pair)

Ankare (D-012, `vg09.store.latest_feed_date()`): **2026-09-17**

Samma 15 frågor, samma verkliga produktions-retrieval (datummedveten, exakt som produktionen) - hämtningen körs EN gång per fråga, och exakt samma paketerade chunks skickas till båda modellerna: endast modellen varierar, inte vad den fick att arbeta med. Ingen modellbedömning, ingen automatisk poängsättning.

**Körningar: 30  ·  omförsök gjorda: 0 (0 körningar)  ·  fortfarande avklippta efter omförsök: 0**

**Svarstider per modell, inklusive eventuellt modellbyte (varje fråga växlar modell A→B, så varje anrop är en potentiell omladdning, KB-003): `qwen3:30b-a3b`: min 8.2s · max 18.5s · avg 12.4s  ·  `qwen3:8b`: min 9.5s · max 33.0s · avg 16.8s**

---
## Fråga 01

**Fråga:** I området Recursive self-improvement, vad är de två senaste nyheterna och vad handlar de om?

**Tolkat läge (delat mellan båda modellerna):** Rankningsläge (sortering efter senaste, inget datumfilter)
**Kandidater övervägda:** 60  ·  **Chunks paketerade:** 34 (identiska för båda modellerna nedan)

---

### Modell A — qwen3:30b-a3b (~20GB VRAM, MoE, D-005) (`qwen3:30b-a3b`)

**prompt_eval_count:** 11389 (71% av num_ctx)  ·  **svarstid (inkl. ev. modellbyte):** 11.7s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

The two most recent papers on recursive self-improvement (both with feed date 2026-09-16) are:

[33] ModularRSI: Modular and Generalizable Recursive Harness Self-Improvement, which proposes a framework that decomposes agent harnesses into five functional modules (Agent Loop, Tool Use, Observation Management, Context Management, and Task Completion Detection) and evolves each module independently before integrating them, enabling generalizable improvements across tasks.

[34] The Last AI Built by Humans: Toward Genuine Recursive Self-Improvement, which introduces a development roadmap for recursive self-improvement (RSI) from "improvement-execution autonomy" through "environment-adaptation autonomy" to "recursive meta-improvement," and examines RSI across different scenarios like scientific discovery, embodied intelligence, and software engineering.

**Källor:**

- **2026-09-16** — [ModularRSI: Modular and Generalizable Recursive Harness Self-Improvement](https://huggingface.co/papers/2609.14857)
- **2026-09-16** — [The Last AI Built by Humans: Toward Genuine Recursive Self-Improvement](https://huggingface.co/papers/2609.11873)


### Modell B — qwen3:8b (~6GB VRAM, dense, D-005) (`qwen3:8b`)

**prompt_eval_count:** 11389 (71% av num_ctx)  ·  **svarstid (inkl. ev. modellbyte):** 33.0s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

The two most recent developments in recursive self-improvement (RSI) are:  

1. **ModularRSI** [33]: This paper introduces a modular and generalizable framework for recursive harness self-improvement. It addresses challenges in generalizable RSI by decomposing the evolvable harness into five functional modules (Agent Loop, Tool Use, Observation Management, Context Management, Task Completion Detection). Each module evolves independently, enabling benchmark-disjoint improvements and cross-domain task performance.  

2. **The Last AI Built by Humans: Toward Genuine Recursive Self-Improvement** [34]: This work conceptualizes RSI as a pathway to "genuine" self-improvement, outlining a roadmap from improvement-execution autonomy to recursive meta-improvement. It emphasizes the need for RSI systems to autonomously adapt to environments, refine strategies, and sustain long-term progress, aligning with practical applications in scientific discovery and embodied intelligence.  

These advancements highlight modular design and conceptual frameworks to enable scalable, autonomous RSI.

**Källor:**

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

**Bedömning:** ☐ A bättre  ☐ B bättre  ☐ Likvärdiga  ☐ Båda fel

---

## Fråga 02

**Fråga:** Vad har hänt med GUI agents den senaste månaden?

**Tolkat läge (delat mellan båda modellerna):** Datumfilter (tolkat från frågan): 2026-08-17 .. 2026-09-17
**Kandidater övervägda:** 60  ·  **Chunks paketerade:** 32 (identiska för båda modellerna nedan)

---

### Modell A — qwen3:30b-a3b (~20GB VRAM, MoE, D-005) (`qwen3:30b-a3b`)

**prompt_eval_count:** 11623 (73% av num_ctx)  ·  **svarstid (inkl. ev. modellbyte):** 12.9s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

Based on the provided sources, several key developments have occurred with GUI agents in the last month:

Researchers have introduced AnTrap, a comprehensive benchmark evaluating GUI agents against runtime anomalies, revealing universal vulnerability to dynamic anomalies across 16 leading GUI models [14]. This work proposes a taxonomy organizing real-world anomalies into four layers with ten subcategories.

LLaDA-UI, a 16.7B-parameter block-wise diffusion vision-language GUI agent, has been presented as a practical generative paradigm for multimodal GUI agents, outperforming Qwen2.5-VL-7B and surpassing Qwen3-VL-8B on four of six reported GUI benchmarks [15].

UI-Mate has been developed as a foundation GUI agent integrating an environment-grounded training stack with in-context demonstration learning, setting a new open-weight state of the art on general computer-use benchmarks with 77.0% on OSWorld-Verified [22].

UI-Venus-2 has been released as a general-purpose foundation GUI agent designed to operate across mobile, web, and desktop environments through a unified closed-loop reasoning-action framework, expanding coverage to more than 170 multilingual mobile apps and native desktop operating systems [26].

**Källor:**

- **2026-08-27** — [Are Android GUI Agents Robust Against Runtime Anomalies? AnTrap: Evaluating Agents in Dynamic Adversarial Environments](https://huggingface.co/papers/2608.24099)
- **2026-09-15** — [LLaDA-UI: Bringing Block-wise Diffusion to Vision-Language GUI Agents](https://huggingface.co/papers/2609.13287)
- **2026-08-18** — [UI-Mate: Advancing Open-Weight Foundation GUI Agents with In-Context Demonstrations](https://huggingface.co/papers/2608.15930)
- **2026-09-02** — [UI-Venus-2 Technical Report](https://huggingface.co/papers/2609.00028)


### Modell B — qwen3:8b (~6GB VRAM, dense, D-005) (`qwen3:8b`)

**prompt_eval_count:** 11623 (73% av num_ctx)  ·  **svarstid (inkl. ev. modellbyte):** 16.0s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

Over the past month, several key developments have shaped GUI agents:  

1. **AnTrap Benchmark** [14]: A comprehensive benchmark was introduced to evaluate GUI agents' robustness against dynamic runtime anomalies (e.g., unexpected pop-ups, action misuse). It categorizes anomalies into four layers (State, Thinking, Action, Round) and tests 16 leading GUI models, revealing universal vulnerabilities to such issues.  

2. **LLaDA-UI** [15]: A 16.7B-parameter MoE-based vision-language GUI agent was released, excelling in multimodal tasks across mobile, desktop, and web platforms. It outperforms models like Qwen2.5-VL-7B and Qwen3-VL-8B on multiple GUI benchmarks.  

3. **UI-Mate** [22]: A foundation GUI agent focused on environment-grounded training and in-context demonstration learning, achieving 77.0% on OSWorld-Verified and 41.0% strict success on OSWorkerBench. It addresses challenges like scarce training data and ambiguous prompts.  

4. **UI-Venus-2** [26]: A general-purpose GUI agent designed for mobile, web, and desktop environments, emphasizing safety mechanisms, multi-environment coverage, and trace-level verification to ensure reliable reinforcement learning signals.  

These advancements highlight growing focus on robustness, scalability, and real-world applicability for GUI agents, alongside integration with open-weight models and collaborative frameworks.

**Källor:**

- **2026-08-27** — [Are Android GUI Agents Robust Against Runtime Anomalies? AnTrap: Evaluating Agents in Dynamic Adversarial Environments](https://huggingface.co/papers/2608.24099)
- **2026-09-15** — [LLaDA-UI: Bringing Block-wise Diffusion to Vision-Language GUI Agents](https://huggingface.co/papers/2609.13287)
- **2026-08-18** — [UI-Mate: Advancing Open-Weight Foundation GUI Agents with In-Context Demonstrations](https://huggingface.co/papers/2608.15930)
- **2026-09-02** — [UI-Venus-2 Technical Report](https://huggingface.co/papers/2609.00028)


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

**Bedömning:** ☐ A bättre  ☐ B bättre  ☐ Likvärdiga  ☐ Båda fel

---

## Fråga 03

**Fråga:** Vad är det absolut  senaste inom Video genereation och är det hårdvaru- eller mjukvarurelaterat?

**Tolkat läge (delat mellan båda modellerna):** Rankningsläge (sortering efter senaste, inget datumfilter)
**Kandidater övervägda:** 60  ·  **Chunks paketerade:** 32 (identiska för båda modellerna nedan)

---

### Modell A — qwen3:30b-a3b (~20GB VRAM, MoE, D-005) (`qwen3:30b-a3b`)

**prompt_eval_count:** 11482 (72% av num_ctx)  ·  **svarstid (inkl. ev. modellbyte):** 16.1s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

The absolute latest development in video generation appears to be PhysStream, as described in source [32] with a feed date of 2026-09-16. PhysStream is a software-based model for physics-grounded image-to-video synthesis that incorporates structured scene memory (positional maps and object tracking maps derived from previously generated frames) and supports fine-grained motion control through sparse velocity-increment signals that encode physical quantities. This allows for interactive, mid-generation control over multi-object tabletop rigid-body scenes, reducing motion distribution distance by 33% and trajectory error by 12% compared to baselines.

This is a software-related development, not hardware-related. The focus is on improving the generative model's ability to understand and control physical dynamics within video generation, rather than requiring new hardware. While some sources mention software optimizations for running video models more efficiently on specific hardware (like Minimax H3 being made "14 times faster" in [14]), the most recent development itself is a software model, not a hardware innovation.

**Källor:**

- **2026-09-16** — [PhysStream: Streaming Physics-Grounded Video Generation with Structured Scene Memory and Fine-Grained Motion Control](https://huggingface.co/papers/2609.17521)
- **2026-08-30** — [Ox Alpha reveal, realtime Minimax, Qwen Next, Hy4, robot olympics: AI NEWS](https://www.youtube.com/watch?v=4wjHNgMLeyY&t=589)


### Modell B — qwen3:8b (~6GB VRAM, dense, D-005) (`qwen3:8b`)

**prompt_eval_count:** 11482 (72% av num_ctx)  ·  **svarstid (inkl. ev. modellbyte):** 13.5s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

The absolute latest in video generation as of September 2026 is **software-driven innovations**, with key advancements including:  

1. **PhysStream** [32]: A physics-grounded video generation model enabling fine-grained motion control and structured scene memory, allowing interactive mid-generation adjustments for multi-object scenes.  
2. **LynnReal-Omni** [31]: A native multimodal framework combining text-to-video, image-conditioned generation, and game-state integration, optimized for real-time rendering with a 27B Flash model.  
3. **Programmable World Model** [25]: A framework decoupling world-state evolution from visual generation, enabling direct control over entities and interactions via natural language instructions.  
4. **MovieGrid** [24]: A post-training method for long-form multi-shot videos, improving intra/inter-shot consistency through spatial grid modeling.  

While hardware (e.g., GPUs) remains critical for performance, the **core advancements are software-centric**, focusing on controllability, realism, and efficiency. For example, **Minimax H3** [14] and **Solar WM** [23] highlight optimized software tools for real-time interactive worlds, reducing dependency on high-end hardware through techniques like distillation and lightweight adaptation.  

**Summary**: The latest trends prioritize **software innovations** (models, frameworks, and control mechanisms) over hardware, though hardware remains foundational for execution.

**Källor:**

- **2026-09-16** — [PhysStream: Streaming Physics-Grounded Video Generation with Structured Scene Memory and Fine-Grained Motion Control](https://huggingface.co/papers/2609.17521)
- **2026-09-15** — [LynnReal-Omni: Native multi-modal Video Generation for Agentic Visual Workflows](https://huggingface.co/papers/2609.15863)
- **2026-09-10** — [Programmable World Model](https://huggingface.co/papers/2609.10540)
- **2026-09-09** — [Multi-Grid Post-Training for Long-Form Multi-Shot Video Generation](https://huggingface.co/papers/2609.06373)
- **2026-08-30** — [Ox Alpha reveal, realtime Minimax, Qwen Next, Hy4, robot olympics: AI NEWS](https://www.youtube.com/watch?v=4wjHNgMLeyY&t=589)
- **2026-09-06** — [GPT 6 Astra, Claude Fable 5.1, Gemini 3.8, realtime Minimax, new world models: AI NEWS](https://www.youtube.com/watch?v=ngyFRCNq0Yc&t=89)


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

**Bedömning:** ☐ A bättre  ☐ B bättre  ☐ Likvärdiga  ☐ Båda fel

---

## Fråga 04

**Fråga:** Den senaste veckan, vad har sagts om Copding Agents. Vänligen sammanfatta.

**Tolkat läge (delat mellan båda modellerna):** Datumfilter (tolkat från frågan): 2026-09-11 .. 2026-09-17
**Kandidater övervägda:** 60  ·  **Chunks paketerade:** 22 (identiska för båda modellerna nedan)

---

### Modell A — qwen3:30b-a3b (~20GB VRAM, MoE, D-005) (`qwen3:30b-a3b`)

**prompt_eval_count:** 7936 (50% av num_ctx)  ·  **svarstid (inkl. ev. modellbyte):** 10.6s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

Based on the provided sources, here's a summary of what's been discussed about coding agents in the last week:

The most recent discussion about coding agents appears in sources [12] and [17], both dated 2026-09-15. The videos discuss using "Claude Code" as a coding agent that can drive computer operations. The creator reports significant productivity gains, saving "like a solid like 10, 15 minutes every single morning" by having the coding agent set up browser tabs, desktop applications, Docker containers, and other tools automatically [17].

The skill involves a "control loop" where the agent discovers windows, acts, and receives feedback on actions [12]. The creator emphasizes that users can customize the skill to their specific workflows rather than using a generic tool [12].

Security considerations are also mentioned, particularly about "prompt injection attacks" that need to be watched for when using coding agents [12]. The videos position this as a "new favorite skill" that users should "start dabbling with" to boost productivity [17].

These sources describe coding agents as tools that can automate computer use across multiple applications, not just limited to coding tasks but extending to general computer operation [17].

**Källor:**

- **2026-09-15** — [My NEW FAVORITE Skill - Claude Code Drives My Whole Computer (Better Computer Use)](https://www.youtube.com/watch?v=SWEThyRHMgQ&t=600)


### Modell B — qwen3:8b (~6GB VRAM, dense, D-005) (`qwen3:8b`)

**prompt_eval_count:** 7936 (50% av num_ctx)  ·  **svarstid (inkl. ev. modellbyte):** 16.8s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

In the past week, discussions around coding agents have focused on their expanding roles in automation, productivity, and real-world applications, with several key developments:  

1. **Enhanced Productivity Tools**: Coding agents like *Claude Code* are being used to automate daily workflows, such as morning setup tasks (e.g., opening browser tabs, launching apps, and managing Docker containers) through CLI and MCP integration. These tools save significant time and are described as "endless possibilities" for boosting productivity [12][17].  

2. **AI Software Factories**: Models like *GPT-6 Astra* are enabling 24/7 operation of AI software factories, where agents can autonomously handle GitHub issues, build applications, and execute coding workflows. This marks a shift toward scalable, continuous development powered by agents [14].  

3. **Specialized Co-Work Models**: *Occamy-1.0*, a cost-efficient co-work model, demonstrates advanced capabilities in handling complex workflows combining information gathering, tool use, coding, and file manipulation. It remains competitive with larger models on specific tasks while optimizing cost-performance [18].  

4. **Real-World Automation**: Agents are now being used for physical-world tasks, such as purchasing goods (e.g., sending Mother’s Day cards). This highlights their growing role in bridging digital and physical interactions, though concerns about security (e.g., prompt injection attacks) persist [21].  

5. **Security and Ethics**: While tools like *Feyospace-v1* and *HazardAuditor* focus on safety in agent execution, there is ongoing debate about balancing innovation with risks, including potential misuse by non-state actors [5][16].  

These developments underscore coding agents’ transition from niche tools to central players in both software development and broader automation ecosystems.

**Källor:**

- **2026-09-15** — [My NEW FAVORITE Skill - Claude Code Drives My Whole Computer (Better Computer Use)](https://www.youtube.com/watch?v=SWEThyRHMgQ&t=600)
- **2026-09-12** — [GPT-6 Astra Just Made AI Software Factories Real (Here's How to Run One)](https://www.youtube.com/watch?v=joKb_QMmglM&t=914)
- **2026-09-14** — [Occamy-1.0: Open Pareto-frontier 35B Intelligence for Co-work](https://huggingface.co/papers/2609.11977)
- **2026-09-17** — [AI Agents Are Starting To Buy. Stripe Is Building How They Pay.](https://www.youtube.com/watch?v=YTG0rdHPTDE&t=1710)
- **2026-09-15** — [HazardAuditor: From Executable Threats to Safer Computer-Use Agents](https://huggingface.co/papers/2609.15134)
- **2026-09-14** — [Intelligence is Everywhere: Why the AI 'Race' is Already Over](https://www.youtube.com/watch?v=duv4A1gDZOY&t=1152)


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

**Bedömning:** ☐ A bättre  ☐ B bättre  ☐ Likvärdiga  ☐ Båda fel

---

## Fråga 05

**Fråga:** Har NeoHorse nämnts de senaste två veckorna?

**Tolkat läge (delat mellan båda modellerna):** Datumfilter (tolkat från frågan): 2026-09-04 .. 2026-09-17
**Kandidater övervägda:** 60  ·  **Chunks paketerade:** 26 (identiska för båda modellerna nedan)

---

### Modell A — qwen3:30b-a3b (~20GB VRAM, MoE, D-005) (`qwen3:30b-a3b`)

**prompt_eval_count:** 9634 (60% av num_ctx)  ·  **svarstid (inkl. ev. modellbyte):** 10.5s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

Yes, NeoHorse is mentioned in source [25] titled "NeoHorse-1: Towards Recursive Self-Improvement via Agentic Post-Training with Routing Harness" with a feed date of 2026-09-09, which falls within the last two weeks (assuming current date is 2026-09-17 based on the latest source date in the provided materials).

**Källor:**

- **2026-09-09** — [NeoHorse-1: Towards Recursive Self-Improvement via Agentic Post-Training with Routing Harness](https://huggingface.co/papers/2609.08183)


### Modell B — qwen3:8b (~6GB VRAM, dense, D-005) (`qwen3:8b`)

**prompt_eval_count:** 9634 (60% av num_ctx)  ·  **svarstid (inkl. ev. modellbyte):** 10.2s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

Yes, NeoHorse was mentioned in the last two weeks. It is referenced in source [25], which has a feed date of 2026-09-09. The paper describes NeoHorse-1 as a family of agent-native models exploring recursive self-improvement through agentic post-training. No other sources in the provided list mention NeoHorse.

**Källor:**

- **2026-09-09** — [NeoHorse-1: Towards Recursive Self-Improvement via Agentic Post-Training with Routing Harness](https://huggingface.co/papers/2609.08183)


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

**Bedömning:** ☐ A bättre  ☐ B bättre  ☐ Likvärdiga  ☐ Båda fel

---

## Fråga 06

**Fråga:** Vad är det senaste inom benchmarking av coding agents?

**Tolkat läge (delat mellan båda modellerna):** Rankningsläge (sortering efter senaste, inget datumfilter)
**Kandidater övervägda:** 60  ·  **Chunks paketerade:** 32 (identiska för båda modellerna nedan)

---

### Modell A — qwen3:30b-a3b (~20GB VRAM, MoE, D-005) (`qwen3:30b-a3b`)

**prompt_eval_count:** 11623 (73% av num_ctx)  ·  **svarstid (inkl. ev. modellbyte):** 17.1s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

The latest development in benchmarking coding agents is SWE-Bench Pro Verified, introduced in [27] with a feed date of 2026-09-10. This benchmark addresses critical issues in existing evaluations of software engineering agents, specifically reward hacking (enabled by leakage of gold solutions or hidden evaluation information) and task quality problems (including misleading problem statements and improperly scoped tests). The paper demonstrates that some models perform substantially worse on this verified benchmark compared to previously reported results on SWE-Bench Pro, suggesting that existing benchmarks may overestimate real software engineering capability.

Another recent benchmark is RealSWE [17] (feed date 2026-09-04), which evaluates coding agents under realistic user requests by introducing a six-category information taxonomy and four linguistic style dimensions. It reveals that realistic inputs reduce resolution rates by 6.4 pp on average compared to formal benchmark problems, with explicitly stating desired behavior and motivation significantly improving performance.

The most recent meta-benchmark is Benchmark Radar [30] (feed date 2026-09-14), which serves as a living database and search engine for AI benchmarks, including coding agent evaluations.

**Källor:**

- **2026-09-10** — [SWE-Bench Pro Verified: A Reliable Benchmark for Software Engineering Agents](https://huggingface.co/papers/2609.08149)
- **2026-09-04** — [RealSWE: A Compositional Evaluation of Coding Agents under Realistic User Requests](https://huggingface.co/papers/2608.27831)
- **2026-09-14** — [Benchmark Radar: A Living Database and Search Engine for AI Benchmarks and Evaluation](https://huggingface.co/papers/2609.11115)


### Modell B — qwen3:8b (~6GB VRAM, dense, D-005) (`qwen3:8b`)

**prompt_eval_count:** 11623 (73% av num_ctx)  ·  **svarstid (inkl. ev. modellbyte):** 12.8s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

The latest advancements in coding agent benchmarking include:  

1. **RealSWE** (source [17]): A benchmark addressing the gap between real user requests (short, informal) and curated benchmark tasks (long, structured). It evaluates how well agents handle realistic, casual user prompts across 381 task families, emphasizing the importance of explicit *desired behavior* and *motivation* in improving performance.  

2. **Real Suite** (sources [28][29]): A new software engineering benchmark testing agents on real-world tasks like fixing invoice taxes or migrating customer accounts. It requires understanding business-specific rules across systems, with a leaderboard showing Fable 5.1 at 38.8%, GPT-6 Astra at 33.8%, and GLM 5.3 at 4th place.  

3. **Benchmark Radar** (source [30]): A living database and search engine for AI benchmarks, enabling researchers to discover, compare, and analyze benchmarks across domains (e.g., coding, reasoning, safety). It aggregates 1,283 source records and 12,916 numeric observations, offering tools for reproducible analysis and trend tracking.  

4. **SWE-Bench Pro Verified** (source [27]): A refined version of SWE-Bench Pro addressing reliability issues like reward hacking and task quality, providing a more trustworthy evaluation framework for software engineering agents.  

These benchmarks highlight the shift toward real-world, dynamic, and domain-specific evaluations, emphasizing both functional correctness and alignment with user intent.

**Källor:**

- **2026-09-04** — [RealSWE: A Compositional Evaluation of Coding Agents under Realistic User Requests](https://huggingface.co/papers/2608.27831)
- **2026-09-13** — [New Deepseek, human genome map, Navier Stokes, GPT finance, Suno v6, YuE2: AI NEWS](https://www.youtube.com/watch?v=nZYJdwM-_nI&t=1002)
- **2026-09-14** — [Benchmark Radar: A Living Database and Search Engine for AI Benchmarks and Evaluation](https://huggingface.co/papers/2609.11115)
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

**Bedömning:** ☐ A bättre  ☐ B bättre  ☐ Likvärdiga  ☐ Båda fel

---

## Fråga 07

**Fråga:** Vad säger forskningen om text-to-video den senaste månaden?

**Tolkat läge (delat mellan båda modellerna):** Datumfilter (tolkat från frågan): 2026-08-17 .. 2026-09-17
**Kandidater övervägda:** 60  ·  **Chunks paketerade:** 33 (identiska för båda modellerna nedan)

---

### Modell A — qwen3:30b-a3b (~20GB VRAM, MoE, D-005) (`qwen3:30b-a3b`)

**prompt_eval_count:** 11371 (71% av num_ctx)  ·  **svarstid (inkl. ev. modellbyte):** 18.5s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

Research on text-to-video models in the last month highlights several key developments and challenges:

Current text-to-video systems struggle with probabilistic alignment, failing to consistently reproduce the correct distribution of possible behaviors rather than just generating plausible individual videos [1]. A new benchmark (DF26) demonstrates that human performance and state-of-the-art deepfake detectors are nearly at random chance when distinguishing AI-generated videos from real ones, showing how advanced these models have become [33].

Several new models have emerged with improved capabilities: MiniMax can generate a 15-second video in just 13 seconds, enabling "infinite streams" where video generation outpaces playback [16, 28]. Gemini Omni 1.1 Flash offers improved text-to-video generation with up to 10 seconds of prior context analysis [17].

Researchers are developing better evaluation frameworks like FIRM-Video, which uses a "check-before-score" principle for more reliable text-to-video reward modeling [31], and Temporal Context Routing (TCR) to improve control over when shot transitions and dialogue occur in script-driven video generation [24].

The field also faces significant computational challenges, with video processing being expensive due to costs that grow with frame count and context length [32].

**Källor:**

- **2026-08-28** — [PAWBench: How Far Are We from Probabilistically Aligned World Modeling?](https://huggingface.co/papers/2608.27345)
- **2026-09-10** — [DF26: We Cannot Tell Fake From Real Anymore](https://huggingface.co/papers/2609.07369)
- **2026-09-04** — [AI News: The Most Insane Week So Far This Year!](https://www.youtube.com/watch?v=GfPZm9yucQo&t=1712)
- **2026-08-28** — [AI News: OpenAI Made a Massive Move Against NVIDIA](https://www.youtube.com/watch?v=TInwQglNkzo&t=695)
- **2026-08-27** — [FIRM-Video: Check Before You Score for Reliable Text-to-Video Reward Modeling](https://huggingface.co/papers/2608.21839)
- **2026-09-04** — [The Missing Temporal Link: Temporal Context Routing for Script-Driven Audio-Video Generation](https://huggingface.co/papers/2609.02367)
- **2026-09-10** — [Why Is Video Still So Expensive? A Survey of Inference-Efficiency Mechanisms in Video and Audiovisual LLMs](https://huggingface.co/papers/2609.10355)


### Modell B — qwen3:8b (~6GB VRAM, dense, D-005) (`qwen3:8b`)

**prompt_eval_count:** 11371 (71% av num_ctx)  ·  **svarstid (inkl. ev. modellbyte):** 21.1s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

The research on text-to-video in the past month highlights advancements in generation quality, efficiency, and evaluation. Key findings include:  

1. **Temporal Context Routing (TCR)** [24] improves script-driven audio-video generation by aligning structured prompts with temporal coordinates, reducing shot boundary errors by 96% and boosting dialogue accuracy to 84.1%.  
2. **Cross-modal Attention Mechanisms** [19] analyze how text, audio, and video interact, revealing bidirectional influences between audio-video edges, which can lead to semantic leakage if not controlled.  
3. **Reward Modeling for Text-to-Video** [31] introduces FIRM-Video, a framework for reliable evaluation, achieving the best MAE on benchmarks while ensuring perceptual quality and world coherence.  
4. **Efficiency Improvements** [32] address computational costs in video large language models (VideoLLMs), reducing parameter counts, latency, and memory usage through inference-efficiency mechanisms.  
5. **Detection Challenges** [33] show that AI-generated videos (including text-to-video models) are increasingly indistinguishable from real ones, underscoring the need for robust benchmarks like DF26.  

These studies emphasize progress in synchronization, controllability, and efficiency, while also highlighting persistent challenges in evaluation and authenticity detection.

**Källor:**

- **2026-09-04** — [The Missing Temporal Link: Temporal Context Routing for Script-Driven Audio-Video Generation](https://huggingface.co/papers/2609.02367)
- **2026-09-07** — [The Attention Triangle in Audio-Video Models](https://huggingface.co/papers/2609.03586)
- **2026-08-27** — [FIRM-Video: Check Before You Score for Reliable Text-to-Video Reward Modeling](https://huggingface.co/papers/2608.21839)
- **2026-09-10** — [Why Is Video Still So Expensive? A Survey of Inference-Efficiency Mechanisms in Video and Audiovisual LLMs](https://huggingface.co/papers/2609.10355)
- **2026-09-10** — [DF26: We Cannot Tell Fake From Real Anymore](https://huggingface.co/papers/2609.07369)


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

**Bedömning:** ☐ A bättre  ☐ B bättre  ☐ Likvärdiga  ☐ Båda fel

---

## Fråga 08

**Fråga:** Nämns LEGO i någon artikel och i så fall, sammanfatta vad de handlar om.

**Tolkat läge (delat mellan båda modellerna):** Inget datumfilter, ingen rankning - obegränsad likhetssökning
**Kandidater övervägda:** 60  ·  **Chunks paketerade:** 32 (identiska för båda modellerna nedan)

---

### Modell A — qwen3:30b-a3b (~20GB VRAM, MoE, D-005) (`qwen3:30b-a3b`)

**prompt_eval_count:** 11394 (71% av num_ctx)  ·  **svarstid (inkl. ev. modellbyte):** 9.2s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

Yes, LEGO is mentioned in source [32] titled "LEGO-RL: Harness-Native Reinforcement Learning for Coding Agents."

LEGO-RL is a framework that bridges native coding-agent harnesses with scalable policy-gradient optimization without modifying their internal control flow. The framework is built upon three pillars:

1) Faithful optimization via in-process LLM proxying that captures raw generation streams for token-level alignment
2) Reliable execution via scalable sandbox orchestration featuring image caching and stage-wise defenses to mitigate reward hacking
3) Observable training through an integrated plugin that automates validation and monitoring

The paper evaluates LEGO-RL by training the sparse MoE model Qwen3.5-35B-A3B with GSPO across three native coding-agent harnesses, showing improvements across platforms including OpenHands SDK (64.0% to 70.4%), Claude Code (62.4% to 68.2%), and OpenCode (57.2% to 66.6%) on SWE-bench Verified. The framework maintains a rollout-training probability correlation above 0.99.

**Källor:**

- **2026-08-19** — [LEGO-RL: Harness-Native Reinforcement Learning for Coding Agents](https://huggingface.co/papers/2608.17393)


### Modell B — qwen3:8b (~6GB VRAM, dense, D-005) (`qwen3:8b`)

**prompt_eval_count:** 11394 (71% av num_ctx)  ·  **svarstid (inkl. ev. modellbyte):** 11.6s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

LEGO is mentioned in source [32], which introduces **LEGO-RL** as a framework for **harness-native reinforcement learning for coding agents**. The framework aims to bridge native coding-agent harnesses (e.g., tools like Claude Code or OpenCode) with scalable policy-gradient optimization. It addresses challenges like environmental crashes, reward hacking, and train-inference discrepancies by incorporating three pillars:  
1. **Faithful optimization** via in-process LLM proxying for token-level alignment and log-probability recomputation.  
2. **Reliable execution** through sandbox orchestration with image caching and stage-wise defenses against reward hacking.  
3. **Observable training** via an integrated plugin with a Live UI for trajectory diagnostics.  

LEGO-RL improves performance on benchmarks like SWE-bench Verified, demonstrating strong results across harnesses like OpenHands SDK, Claude Code, and OpenCode. The term "LEGO" here likely refers to the modular, scalable, and component-based design of the framework rather than the toy brand.

**Källor:**

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

**Bedömning:** ☐ A bättre  ☐ B bättre  ☐ Likvärdiga  ☐ Båda fel

---

## Fråga 09

**Fråga:** Har AutoDev nämnts de senaste veckorna?

**Tolkat läge (delat mellan båda modellerna):** Inget datumfilter, ingen rankning - obegränsad likhetssökning
**Kandidater övervägda:** 60  ·  **Chunks paketerade:** 30 (identiska för båda modellerna nedan)

---

### Modell A — qwen3:30b-a3b (~20GB VRAM, MoE, D-005) (`qwen3:30b-a3b`)

**prompt_eval_count:** 11397 (71% av num_ctx)  ·  **svarstid (inkl. ev. modellbyte):** 8.2s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

No, AutoDev has not been mentioned in any of the provided sources. The sources mention similar terms like "AutoResearch" [2], "AutoSaddler" [10], and "AutoDesign" [16], but none reference "AutoDev" specifically.

**Källor:**

- **2026-08-25** — [AutoResearch: Insight In, Hallucination Out](https://huggingface.co/papers/2608.17906)
- **2026-08-26** — [AutoSaddler: Automatic Harness Optimization with Durable Updates from Agent Execution Traces](https://huggingface.co/papers/2608.23041)
- **2026-08-14** — [AutoDesign: Meta-Harness Optimization for Long-Horizon Agentic Design](https://huggingface.co/papers/2608.13560)


### Modell B — qwen3:8b (~6GB VRAM, dense, D-005) (`qwen3:8b`)

**prompt_eval_count:** 11397 (71% av num_ctx)  ·  **svarstid (inkl. ev. modellbyte):** 13.6s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

The term "AutoDev" is not mentioned in any of the provided sources from the past few weeks. The closest reference is **AutoDesign** [16], which is a framework for long-horizon agentic design, but this is distinct from "AutoDev." No other sources reference "AutoDev" or related terms. 

**Answer:** No, "AutoDev" is not mentioned in the provided sources from the past few weeks.

**Källor:**

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

**Bedömning:** ☐ A bättre  ☐ B bättre  ☐ Likvärdiga  ☐ Båda fel

---

## Fråga 10

**Fråga:** Vad är nytt den 16 september?

**Tolkat läge (delat mellan båda modellerna):** Datumfilter (tolkat från frågan): 2026-09-16 .. 2026-09-16
**Kandidater övervägda:** 37  ·  **Chunks paketerade:** 22 (identiska för båda modellerna nedan)

---

### Modell A — qwen3:30b-a3b (~20GB VRAM, MoE, D-005) (`qwen3:30b-a3b`)

**prompt_eval_count:** 7455 (47% av num_ctx)  ·  **svarstid (inkl. ev. modellbyte):** 8.2s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

Based on the provided sources, all 21 research papers and the YouTube video were published on September 16, 2026 (feed date 2026-09-16). Key highlights include:

- ModAR, a world-action model that autoregressively denoises multiple future modalities for improved action prediction [1]
- Decoy Direction Optimization (DDO), a post-hoc defense against LLM refusal feature ablation attacks [2]
- Gavel, which elicits native skill routing from a frozen LLM without requiring skill text in context [3]
- StepAudio 3 Realtime, an audio-language foundation model with Think-While-Speaking for real-time dialogue [9]
- StepAudio 3 Music, a large-scale music generation model supporting explicit musical planning [14]
- Emergence World, a framework for adversarial stress-testing of long-horizon multi-agent systems [15]
- ScienceBuddy, an interactive scientific research workspace implementing recursive-in-recursive self-improvement [20]

The YouTube video [21][22] features a "free and open-source spy tool" that the creators describe as giving users "more access to information at [their] fingertips" in a harmless way, with the video being part of a weekly AI news series.

**Källor:**

- **2026-09-16** — [Modality-Autoregressive World-Action Models](https://huggingface.co/papers/2609.17524)
- **2026-09-16** — [Decoy Direction Optimization: A Post-Hoc Defense Against LLM Abliteration](https://huggingface.co/papers/2609.16204)
- **2026-09-16** — [The Router Within: Eliciting Native Skill Routing from a Frozen LLM](https://huggingface.co/papers/2609.15982)
- **2026-09-16** — [StepAudio 3 Realtime Technical Report](https://huggingface.co/papers/2609.14005)
- **2026-09-16** — [StepAudio 3 Music Technical Report](https://huggingface.co/papers/2609.16034)
- **2026-09-16** — [Emergence World: Adversarial Stress-Testing of Long-Horizon Multi-Agent Systems](https://huggingface.co/papers/2609.17320)
- **2026-09-16** — [ScienceBuddy: Recursive-in-Recursive Self-Improvement for Interactive Scientific Agents](https://huggingface.co/papers/2609.17523)
- **2026-09-16** — [He Built The Ultimate Spy Tool (Free and Open-Source)](https://www.youtube.com/watch?v=S2VJU5DQqlU&t=1268)

_Hänvisningar i svaret som inte kunde kopplas till en källa: [their]_


### Modell B — qwen3:8b (~6GB VRAM, dense, D-005) (`qwen3:8b`)

**prompt_eval_count:** 7455 (47% av num_ctx)  ·  **svarstid (inkl. ev. modellbyte):** 9.5s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

On September 16, 2026, several new papers and projects were introduced, including:  
- **ModAR** (Modality-Autoregressive World-Action Models) for efficient multimodal prediction in robotics [1].  
- **Decoy Direction Optimization (DDO)**, a post-hoc defense against LLM ablation attacks [2].  
- **Gavel**, a skill-routing framework for frozen LLMs without context pollution [3].  
- **Convergent Emergence of In-Context Learning** across modalities like language, genomes, and images [4].  
- **ScienceBuddy**, an interactive scientific agent with recursive self-improvement [20].  
- **StepAudio 3 Realtime** for fluid audio-language interaction with Think-While-Speaking [9].  
- **PhysStream** for physics-grounded video generation with fine-grained motion control [11].  
- **ImpossibleRubrics** to stress-test rubrics as reward signals [12].  
- **HarnessVLN** for training-free embodied navigation via an agent harness [10].  

All these works were published on September 16, 2026, as indicated by their feed dates.

**Källor:**

- **2026-09-16** — [Modality-Autoregressive World-Action Models](https://huggingface.co/papers/2609.17524)
- **2026-09-16** — [Decoy Direction Optimization: A Post-Hoc Defense Against LLM Abliteration](https://huggingface.co/papers/2609.16204)
- **2026-09-16** — [The Router Within: Eliciting Native Skill Routing from a Frozen LLM](https://huggingface.co/papers/2609.15982)
- **2026-09-16** — [Convergent Emergence of In-Context Learning Across Modalities](https://huggingface.co/papers/2609.14011)
- **2026-09-16** — [ScienceBuddy: Recursive-in-Recursive Self-Improvement for Interactive Scientific Agents](https://huggingface.co/papers/2609.17523)
- **2026-09-16** — [StepAudio 3 Realtime Technical Report](https://huggingface.co/papers/2609.14005)
- **2026-09-16** — [PhysStream: Streaming Physics-Grounded Video Generation with Structured Scene Memory and Fine-Grained Motion Control](https://huggingface.co/papers/2609.17521)
- **2026-09-16** — [ImpossibleRubrics: Stress-Testing Generated Rubrics as Reward Signals](https://huggingface.co/papers/2609.16816)
- **2026-09-16** — [HarnessVLN: Unifying Training-Free Embodied Navigation through an Agent Harness](https://huggingface.co/papers/2609.15195)


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

**Bedömning:** ☐ A bättre  ☐ B bättre  ☐ Likvärdiga  ☐ Båda fel

---

## Fråga 11

**Fråga:** Vad hände i forskningen förra veckan?

**Tolkat läge (delat mellan båda modellerna):** Datumfilter (tolkat från frågan): 2026-09-11 .. 2026-09-17
**Kandidater övervägda:** 60  ·  **Chunks paketerade:** 31 (identiska för båda modellerna nedan)

---

### Modell A — qwen3:30b-a3b (~20GB VRAM, MoE, D-005) (`qwen3:30b-a3b`)

**prompt_eval_count:** 11216 (70% av num_ctx)  ·  **svarstid (inkl. ev. modellbyte):** 12.9s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

Last week's research included several notable papers:

DataFlex-RL was introduced as an evaluation platform for RLVR data policies, finding that changing data policies measurably affects training but doesn't consistently produce better results than uniform training [3].

ReactHuman was presented as the first physics-grounded benchmark for testing whether multimodal LLMs can make immediate, safety-critical decisions in response to physical hazards, revealing that models mishandle roughly one hazard in three [6].

Benchmark Radar was released as a living database and search engine for AI benchmarks, covering various evaluation types and containing 1,283 source records across 790 benchmark records [13].

ModaLens was developed to measure image sensitivity in report-conditioned medical VLMs through a paired image-swap audit, showing that report availability reduces image-swap sensitivity [24].

A deterministic math solver approach for clinical language models was tested, showing that larger models (Qwen2.5-32B) benefit from writing case-specific Python that's executed deterministically rather than performing direct arithmetic [10].

**Källor:**

- **2026-09-14** — [DataFlex-RL: An Evaluation Platform for RLVR Data Policies](https://huggingface.co/papers/2609.06107)
- **2026-09-14** — [ReactHuman: A Physics-Grounded Benchmark for Human-Like Reactive Decision-Making in Embodied Multimodal LLMs](https://huggingface.co/papers/2609.10895)
- **2026-09-14** — [Benchmark Radar: A Living Database and Search Engine for AI Benchmarks and Evaluation](https://huggingface.co/papers/2609.11115)
- **2026-09-15** — [ModaLens: Measuring Image Sensitivity in Report-Conditioned Medical VLMs](https://huggingface.co/papers/2609.15635)
- **2026-09-14** — [Towards a Deterministic Math Solver for Clinical Language Models](https://huggingface.co/papers/2609.10728)


### Modell B — qwen3:8b (~6GB VRAM, dense, D-005) (`qwen3:8b`)

**prompt_eval_count:** 11216 (70% av num_ctx)  ·  **svarstid (inkl. ev. modellbyte):** 28.2s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

Last week's research highlights include:  
- **Long-Horizon Memorization**: A study improved retention from 1.2% to 34.9% using composed continual learning mechanisms like merged LoRA [1].  
- **ModularRSI**: A framework for generalizable agent harness evolution showed consistent improvements on unseen tasks [2].  
- **DataFlex-RL**: Uniform GRPO improved domain-balanced accuracy by 7.76 percentage points, though no method outperformed uniform sampling consistently [3].  
- **MetroLLM-Bench**: A 4B Qwen model outperformed GPT-5.6 in Tier 1 scoring for transit kiosk policies [5].  
- **ReactHuman**: MLLMs struggled with safety-critical reactive decisions, failing ~1 in 3 hazards despite model scale [6].  
- **E2A-Bench**: Financial VLMs faced gaps in evidence-to-action reliability, with directional coverage critical for performance [8].  
- **Emergence World**: Multi-agent systems showed vulnerabilities to stress events like misinformation and memory exposure [9].  
- **Deterministic Math Solver**: A Python-executor approach improved clinical calculator accuracy for Qwen models [10].  
- **IdeaAMBIG**: Identified gaps in research-specification codification, with defect localization as a key bottleneck [12].  
- **Benchmark Radar**: A database for AI benchmarks aids researchers in discovering evaluations and datasets [13].  
- **Lightning Weave**: Enhanced reasoning accuracy-efficiency via capability composition, outperforming baselines in math and coding [14].  
- **Convergent Emergence**: Few-shot in-context learning (ICL) emerged across modalities like genomes, time series, and images [19].  
- **Drift-Constrained Optimization**: Fine-tuning instruct models prioritized directional efficiency over drift, improving scientific reasoning and translation [20].  
- **ModaLens**: Measured image sensitivity in medical VLMs, showing report availability reduced image-swap sensitivity [24].  
- **ScienceBuddy**: Introduced recursive self-improvement for scientific agents, enabling continual learning through feedback and task refinement [27].  

These advancements span continual learning, agent evolution, financial reasoning, and multi-modal ICL, reflecting diverse challenges in AI research.

**Källor:**

- **2026-09-16** — [Continual Learning Mechanisms Compose for Long-Horizon Memorization](https://huggingface.co/papers/2609.06986)
- **2026-09-16** — [ModularRSI: Modular and Generalizable Recursive Harness Self-Improvement](https://huggingface.co/papers/2609.14857)
- **2026-09-14** — [DataFlex-RL: An Evaluation Platform for RLVR Data Policies](https://huggingface.co/papers/2609.06107)
- **2026-09-11** — [MetroLLM-Bench: Evaluating Language Models as Transit Kiosk Runtimes](https://huggingface.co/papers/2609.10016)
- **2026-09-14** — [ReactHuman: A Physics-Grounded Benchmark for Human-Like Reactive Decision-Making in Embodied Multimodal LLMs](https://huggingface.co/papers/2609.10895)
- **2026-09-15** — [E2A-Bench: Benchmarking Evidence-to-Action Reliability in Financial Chart Reasoning](https://huggingface.co/papers/2609.14302)
- **2026-09-16** — [Emergence World: Adversarial Stress-Testing of Long-Horizon Multi-Agent Systems](https://huggingface.co/papers/2609.17320)
- **2026-09-14** — [Towards a Deterministic Math Solver for Clinical Language Models](https://huggingface.co/papers/2609.10728)
- **2026-09-11** — [IdeaAMBIG: Benchmarking Implementation-Critical Gaps in Research-Idea Specifications](https://huggingface.co/papers/2609.10539)
- **2026-09-14** — [Benchmark Radar: A Living Database and Search Engine for AI Benchmarks and Evaluation](https://huggingface.co/papers/2609.11115)
- **2026-09-15** — [Lightning Weave: Improving the Accuracy-Efficiency Frontier of Reasoning Models through Capability Composition](https://huggingface.co/papers/2609.14708)
- **2026-09-16** — [Convergent Emergence of In-Context Learning Across Modalities](https://huggingface.co/papers/2609.14011)
- **2026-09-16** — [Drift-Constrained Optimization: Only Direction Matters in Fine-Tuning Instruct Models](https://huggingface.co/papers/2609.13680)
- **2026-09-15** — [ModaLens: Measuring Image Sensitivity in Report-Conditioned Medical VLMs](https://huggingface.co/papers/2609.15635)
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

**Bedömning:** ☐ A bättre  ☐ B bättre  ☐ Likvärdiga  ☐ Båda fel

---

## Fråga 12

**Fråga:** Har Palantir nämnts i någon video?

**Tolkat läge (delat mellan båda modellerna):** Inget datumfilter, ingen rankning - obegränsad likhetssökning
**Kandidater övervägda:** 60  ·  **Chunks paketerade:** 31 (identiska för båda modellerna nedan)

---

### Modell A — qwen3:30b-a3b (~20GB VRAM, MoE, D-005) (`qwen3:30b-a3b`)

**prompt_eval_count:** 11453 (72% av num_ctx)  ·  **svarstid (inkl. ev. modellbyte):** 11.3s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

Based on the provided sources, there is no mention of "Palantir" in any of the videos or materials. The sources discuss various AI models, tools, and news items, but "Palantir" is not referenced in any of the titles, descriptions, or content excerpts provided. 

[24] and [31] discuss spy tools and "God's Eye View" (a spy satellite simulator), but neither mentions Palantir. 

No source contains the word "Palantir" or any reference to the company.

**Källor:**

- **2026-09-16** — [He Built The Ultimate Spy Tool (Free and Open-Source)](https://www.youtube.com/watch?v=S2VJU5DQqlU&t=1268)


### Modell B — qwen3:8b (~6GB VRAM, dense, D-005) (`qwen3:8b`)

**prompt_eval_count:** 11453 (72% av num_ctx)  ·  **svarstid (inkl. ev. modellbyte):** 9.6s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

The provided sources do not mention "Har Palantir" or any variation of that term. The closest reference is to "Palunteer" in source [31], which appears to be a distinct entity or typo, but no direct mention of Palantir or its associated technologies (e.g., data integration platforms) is found in the excerpts. [31]

**Källor:**

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

**Bedömning:** ☐ A bättre  ☐ B bättre  ☐ Likvärdiga  ☐ Båda fel

---

## Fråga 13

**Fråga:** Vad har sagts om OpenAI de senaste två veckorna?

**Tolkat läge (delat mellan båda modellerna):** Datumfilter (tolkat från frågan): 2026-09-04 .. 2026-09-17
**Kandidater övervägda:** 60  ·  **Chunks paketerade:** 26 (identiska för båda modellerna nedan)

---

### Modell A — qwen3:30b-a3b (~20GB VRAM, MoE, D-005) (`qwen3:30b-a3b`)

**prompt_eval_count:** 9699 (61% av num_ctx)  ·  **svarstid (inkl. ev. modellbyte):** 16.6s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

GPT-6 Astra has been the main focus regarding OpenAI in the last two weeks, with multiple sources discussing its release and capabilities [9] [10] [17] [20]. OpenAI released GPT-6 Astra on Thursday, rolling it out across all paid-chat GPT plans, the API, and AWS [23] [25]. The model is described as "the best model available" by many, with claims that it "just destroys all the other models" [10] [17].

Jensen Huang, CEO of NVIDIA, declared "we have AGI because of Astra" [9], and OpenAI claims "AGI era is here" [21]. However, some sources note that internally at OpenAI, they have models "significantly more capable than GPT6 Astra" for solving complex problems like the Navier Stokes problem [20].

The model is being tested for its ability to run autonomously for long periods, with one user giving it "tens of thousands of emails, years of writing, calendar contacts, and left it alone for five days" [25]. OpenAI's Astra system card mentions researchers noticing "agents associated with the same user communicating inside the same codec setup" [23].

The paper [6] also notes that GPT-6 Astra's architecture overlaps with the architecture sketched by GPT-5.6 Sol, raising questions about whether models are independently imagining the same architectural future or if motifs propagate between model families.

**Källor:**

- **2026-09-12** — [GPT-6 Astra Just Made AI Software Factories Real (Here's How to Run One)](https://www.youtube.com/watch?v=joKb_QMmglM&t=0)
- **2026-09-06** — [GPT 6 Astra, Claude Fable 5.1, Gemini 3.8, realtime Minimax, new world models: AI NEWS](https://www.youtube.com/watch?v=ngyFRCNq0Yc&t=2022)
- **2026-09-11** — [AI News: The AI World is REALLY Scared Right Now](https://www.youtube.com/watch?v=JwTCjarfJYw&t=1220)
- **2026-09-06** — [GPT-6 Astra Doesn't Need Your Instructions Anymore.](https://www.youtube.com/watch?v=1qGH6NwTj3o&t=263)
- **2026-09-09** — [I Asked GPT-6 Astra to Build an AI Slop Detector](https://www.youtube.com/watch?v=-KcHn0QcSb0&t=970)
- **2026-09-16** — [Another Blueprint In The Wall: How to Ask Frontier AI Like a Kid?](https://huggingface.co/papers/2609.14803)


### Modell B — qwen3:8b (~6GB VRAM, dense, D-005) (`qwen3:8b`)

**prompt_eval_count:** 9699 (61% av num_ctx)  ·  **svarstid (inkl. ev. modellbyte):** 25.0s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

OpenAI has been prominently discussed in the last two weeks, primarily围绕 its GPT-6 Astra model. Key points include:  

1. **GPT-6 Astra's Capabilities**:  
   - Astra is highlighted as a breakthrough, enabling AI software factories to automate coding workflows and build applications autonomously [1][9][13]. It reduces the need for explicit instructions, allowing agents to operate independently for extended periods [23][25].  
   - It is described as significantly more capable than prior models, excelling in tasks like solving complex problems (e.g., Navier Stokes equations) and handling diverse workloads [20][25].  

2. **Competitive Landscape**:  
   - Astra is compared to other models like Claude Fable 5.1 and Gemini 3.8, with some sources suggesting it outperforms them in benchmarks [9][17]. However, debates persist about whether its advancements signify true AGI or just superior engineering [6][21].  

3. **Industry Impact**:  
   - Astra’s release is tied to OpenAI’s strategy to position AI as a core economic infrastructure tool, with Stripe and others integrating AI agents into workflows [7][15].  
   - Its ability to handle tasks like financial analysis and software development is emphasized, with tools like "Chat GPT for financial services" combining Astra with financial data [19].  

4. **Ethical and Practical Concerns**:  
   - While Astra’s autonomy is praised, concerns about AI detecting AI-generated content (e.g., "slop detectors") highlight ongoing challenges in verifying authenticity [2][21].  

These discussions reflect OpenAI’s role in advancing AI capabilities and reshaping industries, though debates about AGI and ethical implications remain [6][13][21].

**Källor:**

- **2026-09-12** — [GPT-6 Astra Just Made AI Software Factories Real (Here's How to Run One)](https://www.youtube.com/watch?v=joKb_QMmglM&t=914)
- **2026-09-14** — [Intelligence is Everywhere: Why the AI 'Race' is Already Over](https://www.youtube.com/watch?v=duv4A1gDZOY&t=190)
- **2026-09-06** — [GPT-6 Astra Doesn't Need Your Instructions Anymore.](https://www.youtube.com/watch?v=1qGH6NwTj3o&t=263)
- **2026-09-11** — [AI News: The AI World is REALLY Scared Right Now](https://www.youtube.com/watch?v=JwTCjarfJYw&t=1220)
- **2026-09-06** — [GPT 6 Astra, Claude Fable 5.1, Gemini 3.8, realtime Minimax, new world models: AI NEWS](https://www.youtube.com/watch?v=ngyFRCNq0Yc&t=0)
- **2026-09-16** — [Another Blueprint In The Wall: How to Ask Frontier AI Like a Kid?](https://huggingface.co/papers/2609.14803)
- **2026-09-09** — [I Asked GPT-6 Astra to Build an AI Slop Detector](https://www.youtube.com/watch?v=-KcHn0QcSb0&t=970)
- **2026-09-17** — [AI Agents Are Starting To Buy. Stripe Is Building How They Pay.](https://www.youtube.com/watch?v=YTG0rdHPTDE&t=257)
- **2026-09-14** — [Sam Altman and Apple's New CEO are Fighting Over One Thing. It's Not What You Think.](https://www.youtube.com/watch?v=XIt87tJHm-g&t=1525)
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

**Bedömning:** ☐ A bättre  ☐ B bättre  ☐ Likvärdiga  ☐ Båda fel

---

## Fråga 14

**Fråga:** Har det sagts något om open source-alternativ till stora AI-verktyg, både i videor och i artiklar?

**Tolkat läge (delat mellan båda modellerna):** Inget datumfilter, ingen rankning - obegränsad likhetssökning
**Kandidater övervägda:** 60  ·  **Chunks paketerade:** 30 (identiska för båda modellerna nedan)

---

### Modell A — qwen3:30b-a3b (~20GB VRAM, MoE, D-005) (`qwen3:30b-a3b`)

**prompt_eval_count:** 11378 (71% av num_ctx)  ·  **svarstid (inkl. ev. modellbyte):** 13.5s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

Yes, the sources mention several open source alternatives to large AI tools. 

Open source models like DeepSeek, Qwen 3.8 Flash Next, GLM Flash, and Hi 4 are specifically mentioned as alternatives to proprietary models [1][3][23]. The sources discuss "open weight models" versus "closed weight models," with OpenAI developing their own Jalapeno chip to reduce reliance on NVIDIA [9][14].

The sources highlight that open source models are becoming more capable, with some able to run locally on consumer hardware: "these local models are getting better and better even though they're getting smaller and smaller in terms of like parameter count" [27]. 

Specific examples include:
- An open-source music generator described as "the best open-source music generator available right now" [4]
- Open-source 3D generators and world models [1][3][8]
- A "free and open-source" spy tool [6][16]

The sources also note that open source software is "commoditizing high quality intelligence" and that "software wants to be free" [7].

**Källor:**

- **2026-09-13** — [New Deepseek, human genome map, Navier Stokes, GPT finance, Suno v6, YuE2: AI NEWS](https://www.youtube.com/watch?v=nZYJdwM-_nI&t=0)
- **2026-08-30** — [Ox Alpha reveal, realtime Minimax, Qwen Next, Hy4, robot olympics: AI NEWS](https://www.youtube.com/watch?v=4wjHNgMLeyY&t=168)
- **2026-09-02** — [OpenAI, NVIDIA And Anthropic Just Split. Here's How I'd Spend $20, $60 Or $200.](https://www.youtube.com/watch?v=L9xXnPqVfnM&t=0)
- **2026-08-28** — [AI News: OpenAI Made a Massive Move Against NVIDIA](https://www.youtube.com/watch?v=TInwQglNkzo&t=0)
- **2026-08-21** — [AI News: OpenAI Just Put the Brakes on AI](https://www.youtube.com/watch?v=EfGF7QbJItA&t=1017)
- **2026-09-15** — [Forget Suno. New BEST local AI music generator is here!](https://www.youtube.com/watch?v=9RtywbN--QE&t=1403)
- **2026-09-06** — [GPT 6 Astra, Claude Fable 5.1, Gemini 3.8, realtime Minimax, new world models: AI NEWS](https://www.youtube.com/watch?v=ngyFRCNq0Yc&t=0)
- **2026-09-16** — [He Built The Ultimate Spy Tool (Free and Open-Source)](https://www.youtube.com/watch?v=S2VJU5DQqlU&t=1186)
- **2026-09-14** — [Intelligence is Everywhere: Why the AI 'Race' is Already Over](https://www.youtube.com/watch?v=duv4A1gDZOY&t=190)


### Modell B — qwen3:8b (~6GB VRAM, dense, D-005) (`qwen3:8b`)

**prompt_eval_count:** 11378 (71% av num_ctx)  ·  **svarstid (inkl. ev. modellbyte):** 12.5s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

Yes, several sources mention open-source alternatives to large AI tools, both in videos and articles:  

1. **Videos**:  
   - [1] Highlights open-source models for 3D depth prediction and a "top open-source music generator" [3].  
   - [3] Discusses open-source tools for 3D reconstruction, including code available for local download [3].  
   - [4] Reviews an open-source music generator under Apache 2 license (though model weights are non-commercial) [4].  
   - [8] Mentions "new open-source image generators and editors" and the open-source video generator Miniax H3 [8].  
   - [23] Notes open-source models like GLM 5.3 and Hi 4 [23].  

2. **Articles**:  
   - [9] and [14] contrast open-source ("open-weight") models with closed-source alternatives, emphasizing OpenAI’s and others’ efforts in this space [9][14].  
   - [27] Discusses local open-source models becoming more efficient and accessible on consumer GPUs [27].  

These examples show active coverage of open-source alternatives in both video and article formats.

**Källor:**

- **2026-09-13** — [New Deepseek, human genome map, Navier Stokes, GPT finance, Suno v6, YuE2: AI NEWS](https://www.youtube.com/watch?v=nZYJdwM-_nI&t=0)
- **2026-08-30** — [Ox Alpha reveal, realtime Minimax, Qwen Next, Hy4, robot olympics: AI NEWS](https://www.youtube.com/watch?v=4wjHNgMLeyY&t=168)
- **2026-09-15** — [Forget Suno. New BEST local AI music generator is here!](https://www.youtube.com/watch?v=9RtywbN--QE&t=1403)
- **2026-09-06** — [GPT 6 Astra, Claude Fable 5.1, Gemini 3.8, realtime Minimax, new world models: AI NEWS](https://www.youtube.com/watch?v=ngyFRCNq0Yc&t=0)
- **2026-09-02** — [OpenAI, NVIDIA And Anthropic Just Split. Here's How I'd Spend $20, $60 Or $200.](https://www.youtube.com/watch?v=L9xXnPqVfnM&t=0)
- **2026-08-28** — [AI News: OpenAI Made a Massive Move Against NVIDIA](https://www.youtube.com/watch?v=TInwQglNkzo&t=0)
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

**Bedömning:** ☐ A bättre  ☐ B bättre  ☐ Likvärdiga  ☐ Båda fel

---

## Fråga 15

**Fråga:** Vad har hänt med AI-agenter den senaste veckan, i både papers och videor?

**Tolkat läge (delat mellan båda modellerna):** Datumfilter (tolkat från frågan): 2026-09-11 .. 2026-09-17
**Kandidater övervägda:** 60  ·  **Chunks paketerade:** 22 (identiska för båda modellerna nedan)

---

### Modell A — qwen3:30b-a3b (~20GB VRAM, MoE, D-005) (`qwen3:30b-a3b`)

**prompt_eval_count:** 7782 (49% av num_ctx)  ·  **svarstid (inkl. ev. modellbyte):** 8.9s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

This week, several significant developments have occurred in AI agent research and application:

Research papers have introduced new frameworks for agent capabilities:
- Feyospace-v1 demonstrates a seven-person team training open-weight cyber models with 63.24% verified success rate on CyberGym [1]
- Agent as Policy (AGP) enables general-purpose agents to drive physical robots without task-specific training, achieving 100% success rates on some manipulation tasks [2]
- RSIAgent introduces a training-free multi-agent framework for recursive self-improvement, enabling open-source models to outperform frontier closed-source models [9]
- Atria Dawn Preview is a foundation agentic language model for scientific research with a Verifiable Experience Pipeline [13]
- Emergence World provides a continuous multi-agent environment for stress testing long-horizon autonomous systems [16]

Practical applications are emerging:
- AI agents are beginning to make transactions like buying coffee, with increasing trust in their reliability [19]
- "AI second brains" are evolving into "team brains" to extend productivity benefits to collaborative work [3][10]
- AI agents are driving computer operations through skills that validate environments and permissions [4]

Industry implications:
- OpenAI and Apple are competing over whether AI agents will become the primary interface for user interactions [6][11]
- Stripe is building payment systems for AI agents to make transactions [19][21]

**Källor:**

- **2026-09-14** — [Feyospace-v1: How the Cyber Mercury Seven Trained Frontier Cyber Models](https://huggingface.co/papers/2609.08418)
- **2026-09-15** — [Agent as Policy for Robotic Manipulation](https://huggingface.co/papers/2609.12541)
- **2026-09-15** — [RSIAgent: Autonomous Exploration for Recursive Self-improvement in New Environments](https://huggingface.co/papers/2609.15364)
- **2026-09-15** — [Atria Dawn: The Dawn of Agentic Superintelligence](https://huggingface.co/papers/2609.15818)
- **2026-09-16** — [Emergence World: Adversarial Stress-Testing of Long-Horizon Multi-Agent Systems](https://huggingface.co/papers/2609.17320)
- **2026-09-17** — [AI Agents Are Starting To Buy. Stripe Is Building How They Pay.](https://www.youtube.com/watch?v=YTG0rdHPTDE&t=90)
- **2026-09-17** — [You Built Your AI Second Brain. Now What? (Here's How to Evolve It)](https://www.youtube.com/watch?v=mjQlZrteMIY&t=928)
- **2026-09-15** — [My NEW FAVORITE Skill - Claude Code Drives My Whole Computer (Better Computer Use)](https://www.youtube.com/watch?v=SWEThyRHMgQ&t=448)
- **2026-09-14** — [Sam Altman and Apple's New CEO are Fighting Over One Thing. It's Not What You Think.](https://www.youtube.com/watch?v=XIt87tJHm-g&t=1429)


### Modell B — qwen3:8b (~6GB VRAM, dense, D-005) (`qwen3:8b`)

**prompt_eval_count:** 7782 (49% av num_ctx)  ·  **svarstid (inkl. ev. modellbyte):** 18.0s  ·  **done_reason:** stop  ·  **omförsök:** 0

**Svar:**

In the past week, AI agents have seen significant advancements across research and practical applications, as highlighted in the following sources:  

1. **Cyber and Robotic Capabilities**: The **Feyospace-v1** framework improved cyber agents' performance, achieving a **63.24% success rate** on CyberGym [1]. Meanwhile, **Agent as Policy (AGP)** enabled general-purpose agents to control physical robots without task-specific training, reaching **100% success** in block construction tasks [2].  

2. **Self-Improvement Frameworks**: **RSIAgent** introduced a training-free method for recursive self-improvement through autonomous memory construction, enhancing open-source models like Kimi-K3 and GLM-5.3 [9]. **Atria Dawn** demonstrated collaboration between humans and AI agents in scientific workflows, achieving top scores on 5/16 benchmarks [13].  

3. **Adversarial Testing**: **Emergence World** revealed vulnerabilities in persistent multi-agent systems, where stress events like prompt injection and misinformation led to failures despite detection [16].  

4. **Real-World Integration**: **Stripe** is developing payment systems to allow agents to perform transactions (e.g., buying coffee or gifts), signaling trust in AI-driven commerce [19][21].  

5. **Tooling and Collaboration**: Agents are now integrated into **computer control** (e.g., validating environments and permissions) [4], and strategies for evolving **AI second brains** into **team brains** were discussed, emphasizing scalability and collaboration [3][10].  

6. **Ethical and Economic Implications**: Debates emerged about agents displacing human roles, with concerns over job displacement for younger workers and shifts in business models [6][17].  

These developments underscore progress in agent autonomy, safety, and integration into real-world systems.

**Källor:**

- **2026-09-14** — [Feyospace-v1: How the Cyber Mercury Seven Trained Frontier Cyber Models](https://huggingface.co/papers/2609.08418)
- **2026-09-15** — [Agent as Policy for Robotic Manipulation](https://huggingface.co/papers/2609.12541)
- **2026-09-15** — [RSIAgent: Autonomous Exploration for Recursive Self-improvement in New Environments](https://huggingface.co/papers/2609.15364)
- **2026-09-15** — [Atria Dawn: The Dawn of Agentic Superintelligence](https://huggingface.co/papers/2609.15818)
- **2026-09-16** — [Emergence World: Adversarial Stress-Testing of Long-Horizon Multi-Agent Systems](https://huggingface.co/papers/2609.17320)
- **2026-09-17** — [AI Agents Are Starting To Buy. Stripe Is Building How They Pay.](https://www.youtube.com/watch?v=YTG0rdHPTDE&t=90)
- **2026-09-15** — [My NEW FAVORITE Skill - Claude Code Drives My Whole Computer (Better Computer Use)](https://www.youtube.com/watch?v=SWEThyRHMgQ&t=448)
- **2026-09-17** — [You Built Your AI Second Brain. Now What? (Here's How to Evolve It)](https://www.youtube.com/watch?v=mjQlZrteMIY&t=928)
- **2026-09-14** — [Sam Altman and Apple's New CEO are Fighting Over One Thing. It's Not What You Think.](https://www.youtube.com/watch?v=XIt87tJHm-g&t=1429)
- **2026-09-14** — [Intelligence is Everywhere: Why the AI 'Race' is Already Over](https://www.youtube.com/watch?v=duv4A1gDZOY&t=576)


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

**Bedömning:** ☐ A bättre  ☐ B bättre  ☐ Likvärdiga  ☐ Båda fel

---

# Date phrases

How Since turns time words in a question into the dates it searches (T-094, T-105,
`vg09/date_range.py`). Every case in the table at the end is a test in
`tests/test_date_matrix.py`; a test checks the two lists match.

## The reference date

All phrases count from the reference date: today's calendar date in your time zone
(`data/sources.json` `timezone`, Europe/Stockholm by default; D-022). The newest source in
the index never moves it. Both ends of every interval are included.

## What each kind of phrase means

| Kind | Meaning | Examples |
|---|---|---|
| **Single day** | One calendar day | today, idag, yesterday, igår, the day before yesterday, i förrgår, two days ago, för tre dagar sedan, on Friday, last Friday, i fredags, October 5, den 5 oktober, 2026-10-05, October 5, 2025 |
| **Rolling period** | A stretch ending on the reference date, the given number of days, weeks or calendar months long | the last 7 days, de senaste 5 dagarna, the past three weeks, de senaste två veckorna, in the last week, the past week, senaste veckan, in the last month, the past month, senaste månaden, the past year |
| **Since-period** | From a start day through the reference date | since yesterday, sedan igår, since Monday, since last Monday, sedan i måndags, since October 1, since 2026-10-01, sedan 1 oktober, since September |
| **Calendar period** | A named calendar unit, or the part of it up to today | last week, förra veckan, this week, denna vecka, last month, förra månaden, this month, denna månad, in September, i december, in September 2025, week 41, vecka 1, this year, i år |
| **Explicit range** | Two dates | between October 1 and October 5, mellan den 1 och den 5 oktober, from 2026-10-01 to 2026-10-05, from September 28 to October 2 |

## Rules

- **Weeks and months: calendar or rolling (T-105).** Weeks run Monday to Sunday.

  | Phrase | Meaning | On Friday 2026-10-09 |
  |---|---|---|
  | last week, previous week, förra veckan | the previous Monday to Sunday | Mon 2026-09-28 – Sun 2026-10-04 |
  | this week, denna vecka, den här veckan | this Monday through today | Mon 2026-10-05 – Fri 2026-10-09 |
  | last month, previous month, förra månaden | the previous whole calendar month | Tue 2026-09-01 – Wed 2026-09-30 |
  | this month, denna månad, den här månaden | the 1st through today | Thu 2026-10-01 – Fri 2026-10-09 |
  | the last 7 days, in the last week, the past week, this past week, senaste veckan | 7 days ending today | Sat 2026-10-03 – Fri 2026-10-09 |
  | in the last month, the past month, senaste månaden | one calendar month back to the same day number, through today | Wed 2026-09-09 – Fri 2026-10-09 |

  "The" makes the difference in English: "last week" is the calendar week before this one,
  "in the last week" is the 7 days ending today. In Swedish, "förra" is the calendar unit
  and "senaste" the rolling one. On a Monday, "this week" is that Monday alone. Until
  T-105 (2026-10-09), "last week", "this week" and "förra veckan" meant the last 7 days
  and "förra månaden" the past month; see "The evaluation questions" below.
- **"Since Monday" on a Monday** means today only. "Since last Monday" and "sedan i
  måndags" mean the Monday a week earlier.
- **A weekday on its own** ("on Friday") is the most recent one, today included. "Last
  Friday" and "i fredags" are strictly before today.
- **Rolling months** go back one calendar month to the same day number, moved to the
  month's last day when it is shorter (31 March gives 28 February). "In September" is the
  whole month.
- **Years left out.** A date or month without a year is this year's, unless that is still
  ahead of the reference date; then it is last year's. "December 24" asked in October 2026
  means 24 December 2025. A range without years takes its year from the start date, and
  runs into the next year when the end month comes earlier (December 28 to January 3).
- **Years given.** "October 5, 2025", "5 oktober 2025", "2026-10-05" and "September 2025"
  are taken as written.
- **Shown with weekdays.** The app shows every interval with its weekdays and length,
  for example "Mon 2026-09-28 – Sun 2026-10-04 (7 days)", so a calendar week and a rolling
  week can't be confused.
- **Week numbers** are ISO weeks, Monday to Sunday. Week 1 can start in December. A week
  number without a year is this year's, or last year's if it hasn't started yet. A week
  can end after today.
- **Numbers.** Digits or words up to ten, in both languages.

## When Since asks instead of searching

If a question asks about time but doesn't say which dates, Since does not search. It
names the words, offers the last 7 days, the last 30 days or all dates, and points to the
custom range in the sidebar. This happens for:

- vague words: recent, recently, lately, nowadays, these days, nyligen, på sistone, de
  senaste veckorna (no number);
- periods Since doesn't define: this weekend, i helgen, Q3, the quarter, i höstas, i
  våras, and a period relative to a named date, such as "the week after October 1";
- distances in weeks, months or years: two weeks ago, a month ago, för en månad sedan;
- "last year" and "förra året", which can mean the previous calendar year or the past 12
  months;
- dates that don't exist or don't fit: February 29 in a year without one, 2026-02-30,
  week 54, a range written backwards.

A question with no time words searches every date, as before. "The latest" or "det
senaste" sorts by date instead of filtering. A custom range set in the sidebar always wins.

## What the dates are compared with

The interval filters on each source's feed date: a paper's Daily Papers day, a video's
upload day in UTC (KB-040). Stored dates are never converted. Close to midnight a video
can therefore count for the neighbouring local day: a video uploaded at 00:30 in Stockholm
in summer is dated the day before. The app says so next to the interval whenever a date
filter includes videos.

## Not supported

Hours or times of day, holidays, dates in other languages, and numbers above ten written
as words. Weekends, quarters, seasons and periods relative to a named date are asked about
(above), not interpreted. "Earlier this week" is read as "this week", the last 7 days.

## The evaluation questions

The frozen dataset, its reference date (2026-09-17, D-012) and the graded results in
`docs/eval-results/` are unchanged. The phrase rules are not bent to keep old windows: the
evaluation questions are resolved under the rules above, and the differences are recorded
here. Checked on 2026-10-09 for all 15 questions in Swedish and English, comparing the
original code (tag `v1-pre-improvement`) with the current one.

- **Direct parser** is what `extract_date_range()` returns. The evaluation scripts call
  it directly, so this is what a re-run would search.
- **In the app** is what a user asking the same question sees. The app may also ask for
  a period (T-094), which the scripts never do.

| Question | Phrase | Direct parser, before | Direct parser, now | In the app, now |
|---|---|---|---|---|
| F11 sv | förra veckan | 2026-09-11 – 2026-09-17 | Mon 2026-09-07 – Sun 2026-09-13 | same as the parser |
| F11 en | last week | 2026-09-11 – 2026-09-17 | Mon 2026-09-07 – Sun 2026-09-13 | same as the parser |
| F09 sv | de senaste veckorna | no range | no range | asks for a period (until T-094: searched all dates) |
| F09 en | in recent weeks | no range | no range | asks for a period (until T-094: searched all dates) |

The other 26 resolve exactly as before: the rolling phrases in F02, F04, F05, F07, F13 and
F15 ("in the last week", "senaste månaden", "the last two weeks" …), the absolute date in
F10, and the rankings and plain questions.

F11's answer key grades against 2026-09-10 – 2026-09-16 and fails an answer citing a paper
dated outside it. A re-run under the current rules searches the previous calendar week
instead, so F11 must be graded against Mon 2026-09-07 – Sun 2026-09-13 in that run; the
historical F11 grades stay as they were, graded under the old convention.

## Test matrix

| Kind | Question | Reference date | Result |
|---|---|---|---|
| Single day | What came out today? | 2026-10-09 Fri | Fri 2026-10-09 (1 day) |
| Single day | Vad kom idag? | 2026-10-09 Fri | Fri 2026-10-09 (1 day) |
| Single day | What was published yesterday? | 2026-10-09 Fri | Thu 2026-10-08 (1 day) |
| Single day | Vad publicerades igår? | 2026-10-09 Fri | Thu 2026-10-08 (1 day) |
| Single day | What came out the day before yesterday? | 2026-10-09 Fri | Wed 2026-10-07 (1 day) |
| Single day | Vad kom i förrgår? | 2026-10-09 Fri | Wed 2026-10-07 (1 day) |
| Single day | What was posted two days ago? | 2026-10-09 Fri | Wed 2026-10-07 (1 day) |
| Single day | Vad kom för tre dagar sedan? | 2026-10-09 Fri | Tue 2026-10-06 (1 day) |
| Single day | What came out on Friday? | 2026-10-09 Fri | Fri 2026-10-09 (1 day) |
| Single day | What came out last Friday? | 2026-10-09 Fri | Fri 2026-10-02 (1 day) |
| Single day | Vad kom i fredags? | 2026-10-09 Fri | Fri 2026-10-02 (1 day) |
| Single day | Papers from October 5 | 2026-10-09 Fri | Mon 2026-10-05 (1 day) |
| Single day | Vad kom den 5 oktober? | 2026-10-09 Fri | Mon 2026-10-05 (1 day) |
| Single day | What was published on 2026-10-05? | 2026-10-09 Fri | Mon 2026-10-05 (1 day) |
| Single day | What was published on October 5, 2025? | 2026-10-09 Fri | Sun 2025-10-05 (1 day) |
| Single day | What came out on December 24? | 2026-10-09 Fri | Wed 2025-12-24 (1 day) |
| Single day | What came out on February 29? | 2026-10-09 Fri | asks for a period |
| Single day | What came out on February 29? | 2028-03-01 Wed | Tue 2028-02-29 (1 day) |
| Single day | What came out on 2026-02-30? | 2026-10-09 Fri | asks for a period |
| Rolling period | What happened in the last 7 days? | 2026-10-09 Fri | Sat 2026-10-03 – Fri 2026-10-09 (7 days) |
| Rolling period | Vad hände de senaste 5 dagarna? | 2026-10-09 Fri | Mon 2026-10-05 – Fri 2026-10-09 (5 days) |
| Rolling period | How did agents develop over the past three weeks? | 2026-10-09 Fri | Sat 2026-09-19 – Fri 2026-10-09 (21 days) |
| Rolling period | Vad hände de senaste två veckorna? | 2026-10-09 Fri | Sat 2026-09-26 – Fri 2026-10-09 (14 days) |
| Rolling period | What happened in the last week? | 2026-10-09 Fri | Sat 2026-10-03 – Fri 2026-10-09 (7 days) |
| Rolling period | What happened over the past week? | 2026-10-09 Fri | Sat 2026-10-03 – Fri 2026-10-09 (7 days) |
| Rolling period | Vad hände senaste veckan? | 2026-10-09 Fri | Sat 2026-10-03 – Fri 2026-10-09 (7 days) |
| Rolling period | What happened in the last month? | 2026-10-09 Fri | Wed 2026-09-09 – Fri 2026-10-09 (31 days) |
| Rolling period | What happened over the past month? | 2026-10-09 Fri | Wed 2026-09-09 – Fri 2026-10-09 (31 days) |
| Rolling period | Vad hände senaste månaden? | 2026-03-31 Tue | Sat 2026-02-28 – Tue 2026-03-31 (32 days) |
| Rolling period | What happened over the past year? | 2026-10-09 Fri | Thu 2025-10-09 – Fri 2026-10-09 (366 days) |
| Rolling period | What happened in the last 7 days? | 2026-01-03 Sat | Sun 2025-12-28 – Sat 2026-01-03 (7 days) |
| Since-period | What is new since yesterday? | 2026-10-09 Fri | Thu 2026-10-08 – Fri 2026-10-09 (2 days) |
| Since-period | Vad är nytt sedan igår? | 2026-10-09 Fri | Thu 2026-10-08 – Fri 2026-10-09 (2 days) |
| Since-period | What is new since Monday? | 2026-10-09 Fri | Mon 2026-10-05 – Fri 2026-10-09 (5 days) |
| Since-period | What is new since Monday? | 2026-10-12 Mon | Mon 2026-10-12 (1 day) |
| Since-period | What is new since last Monday? | 2026-10-12 Mon | Mon 2026-10-05 – Mon 2026-10-12 (8 days) |
| Since-period | Vad är nytt sedan i måndags? | 2026-10-12 Mon | Mon 2026-10-05 – Mon 2026-10-12 (8 days) |
| Since-period | What is new since October 1? | 2026-10-09 Fri | Thu 2026-10-01 – Fri 2026-10-09 (9 days) |
| Since-period | What is new since 2026-10-01? | 2026-10-09 Fri | Thu 2026-10-01 – Fri 2026-10-09 (9 days) |
| Since-period | Vad är nytt sedan 1 oktober? | 2026-10-09 Fri | Thu 2026-10-01 – Fri 2026-10-09 (9 days) |
| Since-period | What is new since December 20? | 2026-01-05 Mon | Sat 2025-12-20 – Mon 2026-01-05 (17 days) |
| Since-period | What is new since September? | 2026-10-09 Fri | Tue 2026-09-01 – Fri 2026-10-09 (39 days) |
| Calendar period | What happened last week? | 2026-10-09 Fri | Mon 2026-09-28 – Sun 2026-10-04 (7 days) |
| Calendar period | Vad hände förra veckan? | 2026-10-09 Fri | Mon 2026-09-28 – Sun 2026-10-04 (7 days) |
| Calendar period | What happened last week? | 2026-10-12 Mon | Mon 2026-10-05 – Sun 2026-10-11 (7 days) |
| Calendar period | Vad hände förra veckan? | 2026-01-05 Mon | Mon 2025-12-29 – Sun 2026-01-04 (7 days) |
| Calendar period | What's new this week? | 2026-10-09 Fri | Mon 2026-10-05 – Fri 2026-10-09 (5 days) |
| Calendar period | Vad är nytt denna vecka? | 2026-10-09 Fri | Mon 2026-10-05 – Fri 2026-10-09 (5 days) |
| Calendar period | What's new this week? | 2026-10-12 Mon | Mon 2026-10-12 (1 day) |
| Calendar period | What happened last month? | 2026-10-09 Fri | Tue 2026-09-01 – Wed 2026-09-30 (30 days) |
| Calendar period | Vad hände förra månaden? | 2026-10-09 Fri | Tue 2026-09-01 – Wed 2026-09-30 (30 days) |
| Calendar period | Vad hände förra månaden? | 2026-01-05 Mon | Mon 2025-12-01 – Wed 2025-12-31 (31 days) |
| Calendar period | What happened this month? | 2026-10-09 Fri | Thu 2026-10-01 – Fri 2026-10-09 (9 days) |
| Calendar period | Vad hände denna månad? | 2026-10-09 Fri | Thu 2026-10-01 – Fri 2026-10-09 (9 days) |
| Calendar period | Vad hände den här månaden? | 2026-10-09 Fri | Thu 2026-10-01 – Fri 2026-10-09 (9 days) |
| Calendar period | What happened in September? | 2026-10-09 Fri | Tue 2026-09-01 – Wed 2026-09-30 (30 days) |
| Calendar period | Vad hände i december? | 2026-01-05 Mon | Mon 2025-12-01 – Wed 2025-12-31 (31 days) |
| Calendar period | What happened in September 2025? | 2026-10-09 Fri | Mon 2025-09-01 – Tue 2025-09-30 (30 days) |
| Calendar period | What happened in week 41? | 2026-10-09 Fri | Mon 2026-10-05 – Sun 2026-10-11 (7 days) |
| Calendar period | Vad hände vecka 1? | 2026-10-09 Fri | Mon 2025-12-29 – Sun 2026-01-04 (7 days) |
| Calendar period | What happened this year? | 2026-10-09 Fri | Thu 2026-01-01 – Fri 2026-10-09 (282 days) |
| Calendar period | Vad har hänt i år? | 2026-10-09 Fri | Thu 2026-01-01 – Fri 2026-10-09 (282 days) |
| Explicit range | What happened between October 1 and October 5? | 2026-10-09 Fri | Thu 2026-10-01 – Mon 2026-10-05 (5 days) |
| Explicit range | Vad hände mellan den 1 och den 5 oktober? | 2026-10-09 Fri | Thu 2026-10-01 – Mon 2026-10-05 (5 days) |
| Explicit range | What happened from 2026-10-01 to 2026-10-05? | 2026-10-09 Fri | Thu 2026-10-01 – Mon 2026-10-05 (5 days) |
| Explicit range | What happened from September 28 to October 2? | 2026-10-09 Fri | Mon 2026-09-28 – Fri 2026-10-02 (5 days) |
| Explicit range | What happened between December 28 and January 3? | 2026-01-05 Mon | Sun 2025-12-28 – Sat 2026-01-03 (7 days) |
| Ask for a period | What are recent advances in agents? | 2026-10-09 Fri | asks for a period |
| Ask for a period | Vad har hänt nyligen? | 2026-10-09 Fri | asks for a period |
| Ask for a period | What came out two weeks ago? | 2026-10-09 Fri | asks for a period |
| Ask for a period | Vad kom för en månad sedan? | 2026-10-09 Fri | asks for a period |
| Ask for a period | What came out a month ago? | 2026-10-09 Fri | asks for a period |
| Ask for a period | What happened last year? | 2026-10-09 Fri | asks for a period |
| Ask for a period | Vad har hänt de senaste veckorna? | 2026-10-09 Fri | asks for a period |
| Ask for a period | What happened between October 5 and October 1? | 2026-10-09 Fri | asks for a period |
| Ask for a period | What happened in week 54? | 2026-10-09 Fri | asks for a period |
| Ask for a period | What happened this weekend? | 2026-10-09 Fri | asks for a period |
| Ask for a period | Vad hände i helgen? | 2026-10-09 Fri | asks for a period |
| Ask for a period | What happened the week after October 1? | 2026-10-09 Fri | asks for a period |
| Ask for a period | Vad hände veckan efter den 1 oktober? | 2026-10-09 Fri | asks for a period |
| Ask for a period | What came out in Q3? | 2026-10-09 Fri | asks for a period |
| Ask for a period | Vad hände i höstas? | 2026-10-09 Fri | asks for a period |
| Ranking | What are the latest papers on agents? | 2026-10-09 Fri | sorted by latest, no filter |
| Ranking | Vad är det senaste om agenter? | 2026-10-09 Fri | sorted by latest, no filter |
| No date (ordinary) | What is a transformer? | 2026-10-09 Fri | no date filter |
| No date (ordinary) | What may come next for agents? | 2026-10-09 Fri | no date filter |
| No date (ordinary) | Vad är RAG? | 2026-10-09 Fri | no date filter |

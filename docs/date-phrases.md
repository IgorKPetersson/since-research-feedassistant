# Date phrases

How Since turns time words in a question into the dates it searches (T-094,
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
| **Rolling period** | A stretch ending on the reference date, the given number of days, weeks or calendar months long | the last 7 days, de senaste 5 dagarna, the past three weeks, de senaste två veckorna, last week, förra veckan, this week, the last month, senaste månaden, förra månaden, the past year |
| **Since-period** | From a start day through the reference date | since yesterday, sedan igår, since Monday, since last Monday, sedan i måndags, since October 1, since 2026-10-01, sedan 1 oktober, since September |
| **Calendar period** | A named calendar unit | this month, den här månaden, in September, i december, in September 2025, week 41, vecka 1, this year, i år |
| **Explicit range** | Two dates | between October 1 and October 5, mellan den 1 och den 5 oktober, from 2026-10-01 to 2026-10-05, from September 28 to October 2 |

## Rules

- **Weeks.** "Last week", "this week", "förra veckan" and "senaste veckan" mean the last 7
  days, ending today. This is the convention the evaluation questions were written with
  (`docs/eval-questions.md`), so it is kept. A Monday-to-Sunday week is asked for by its
  ISO number, "week 41" or "vecka 41"; "since Monday" covers this week so far.
- **"Since Monday" on a Monday** means today only. "Since last Monday" and "sedan i
  måndags" mean the Monday a week earlier.
- **A weekday on its own** ("on Friday") is the most recent one, today included. "Last
  Friday" and "i fredags" are strictly before today.
- **Months.** "The last month", "senaste månaden" and "förra månaden" go back one calendar
  month to the same day number, moved to the month's last day when it is shorter
  (31 March gives 28 February). "This month" runs from the 1st to today. "In September"
  is the whole month.
- **Years left out.** A date or month without a year is this year's, unless that is still
  ahead of the reference date; then it is last year's. "December 24" asked in October 2026
  means 24 December 2025. A range without years takes its year from the start date, and
  runs into the next year when the end month comes earlier (December 28 to January 3).
- **Years given.** "October 5, 2025", "5 oktober 2025", "2026-10-05" and "September 2025"
  are taken as written.
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

## Test matrix

| Kind | Question | Reference date | Result |
|---|---|---|---|
| Single day | What came out today? | 2026-10-09 Fri | 2026-10-09 |
| Single day | Vad kom idag? | 2026-10-09 Fri | 2026-10-09 |
| Single day | What was published yesterday? | 2026-10-09 Fri | 2026-10-08 |
| Single day | Vad publicerades igår? | 2026-10-09 Fri | 2026-10-08 |
| Single day | What came out the day before yesterday? | 2026-10-09 Fri | 2026-10-07 |
| Single day | Vad kom i förrgår? | 2026-10-09 Fri | 2026-10-07 |
| Single day | What was posted two days ago? | 2026-10-09 Fri | 2026-10-07 |
| Single day | Vad kom för tre dagar sedan? | 2026-10-09 Fri | 2026-10-06 |
| Single day | What came out on Friday? | 2026-10-09 Fri | 2026-10-09 |
| Single day | What came out last Friday? | 2026-10-09 Fri | 2026-10-02 |
| Single day | Vad kom i fredags? | 2026-10-09 Fri | 2026-10-02 |
| Single day | Papers from October 5 | 2026-10-09 Fri | 2026-10-05 |
| Single day | Vad kom den 5 oktober? | 2026-10-09 Fri | 2026-10-05 |
| Single day | What was published on 2026-10-05? | 2026-10-09 Fri | 2026-10-05 |
| Single day | What was published on October 5, 2025? | 2026-10-09 Fri | 2025-10-05 |
| Single day | What came out on December 24? | 2026-10-09 Fri | 2025-12-24 |
| Single day | What came out on February 29? | 2026-10-09 Fri | asks for a period |
| Single day | What came out on February 29? | 2028-03-01 Wed | 2028-02-29 |
| Single day | What came out on 2026-02-30? | 2026-10-09 Fri | asks for a period |
| Rolling period | What happened in the last 7 days? | 2026-10-09 Fri | 2026-10-03 – 2026-10-09 |
| Rolling period | Vad hände de senaste 5 dagarna? | 2026-10-09 Fri | 2026-10-05 – 2026-10-09 |
| Rolling period | How did agents develop over the past three weeks? | 2026-10-09 Fri | 2026-09-19 – 2026-10-09 |
| Rolling period | Vad hände de senaste två veckorna? | 2026-10-09 Fri | 2026-09-26 – 2026-10-09 |
| Rolling period | What happened last week? | 2026-10-09 Fri | 2026-10-03 – 2026-10-09 |
| Rolling period | Vad hände förra veckan? | 2026-10-09 Fri | 2026-10-03 – 2026-10-09 |
| Rolling period | What's new this week? | 2026-10-09 Fri | 2026-10-03 – 2026-10-09 |
| Rolling period | What happened in the last month? | 2026-10-09 Fri | 2026-09-09 – 2026-10-09 |
| Rolling period | Vad hände senaste månaden? | 2026-03-31 Tue | 2026-02-28 – 2026-03-31 |
| Rolling period | Vad hände förra månaden? | 2026-10-09 Fri | 2026-09-09 – 2026-10-09 |
| Rolling period | What happened over the past year? | 2026-10-09 Fri | 2025-10-09 – 2026-10-09 |
| Rolling period | What happened in the last 7 days? | 2026-01-03 Sat | 2025-12-28 – 2026-01-03 |
| Since-period | What is new since yesterday? | 2026-10-09 Fri | 2026-10-08 – 2026-10-09 |
| Since-period | Vad är nytt sedan igår? | 2026-10-09 Fri | 2026-10-08 – 2026-10-09 |
| Since-period | What is new since Monday? | 2026-10-09 Fri | 2026-10-05 – 2026-10-09 |
| Since-period | What is new since Monday? | 2026-10-12 Mon | 2026-10-12 |
| Since-period | What is new since last Monday? | 2026-10-12 Mon | 2026-10-05 – 2026-10-12 |
| Since-period | Vad är nytt sedan i måndags? | 2026-10-12 Mon | 2026-10-05 – 2026-10-12 |
| Since-period | What is new since October 1? | 2026-10-09 Fri | 2026-10-01 – 2026-10-09 |
| Since-period | What is new since 2026-10-01? | 2026-10-09 Fri | 2026-10-01 – 2026-10-09 |
| Since-period | Vad är nytt sedan 1 oktober? | 2026-10-09 Fri | 2026-10-01 – 2026-10-09 |
| Since-period | What is new since December 20? | 2026-01-05 Mon | 2025-12-20 – 2026-01-05 |
| Since-period | What is new since September? | 2026-10-09 Fri | 2026-09-01 – 2026-10-09 |
| Calendar period | What happened this month? | 2026-10-09 Fri | 2026-10-01 – 2026-10-09 |
| Calendar period | Vad hände den här månaden? | 2026-10-09 Fri | 2026-10-01 – 2026-10-09 |
| Calendar period | What happened in September? | 2026-10-09 Fri | 2026-09-01 – 2026-09-30 |
| Calendar period | Vad hände i december? | 2026-01-05 Mon | 2025-12-01 – 2025-12-31 |
| Calendar period | What happened in September 2025? | 2026-10-09 Fri | 2025-09-01 – 2025-09-30 |
| Calendar period | What happened in week 41? | 2026-10-09 Fri | 2026-10-05 – 2026-10-11 |
| Calendar period | Vad hände vecka 1? | 2026-10-09 Fri | 2025-12-29 – 2026-01-04 |
| Calendar period | What happened this year? | 2026-10-09 Fri | 2026-01-01 – 2026-10-09 |
| Calendar period | Vad har hänt i år? | 2026-10-09 Fri | 2026-01-01 – 2026-10-09 |
| Explicit range | What happened between October 1 and October 5? | 2026-10-09 Fri | 2026-10-01 – 2026-10-05 |
| Explicit range | Vad hände mellan den 1 och den 5 oktober? | 2026-10-09 Fri | 2026-10-01 – 2026-10-05 |
| Explicit range | What happened from 2026-10-01 to 2026-10-05? | 2026-10-09 Fri | 2026-10-01 – 2026-10-05 |
| Explicit range | What happened from September 28 to October 2? | 2026-10-09 Fri | 2026-09-28 – 2026-10-02 |
| Explicit range | What happened between December 28 and January 3? | 2026-01-05 Mon | 2025-12-28 – 2026-01-03 |
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

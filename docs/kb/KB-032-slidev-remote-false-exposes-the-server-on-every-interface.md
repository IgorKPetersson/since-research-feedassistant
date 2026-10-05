# KB-032 — `slidev --remote false` turns remote access on, with "false" as the password

**Area:** Presentation (Slidev) — dev server
**Status:** verified
**Date:** 2026-10-05  ·  **From:** T-048

## Claim
`--remote` takes an optional password, not a boolean. `slidev --remote false` enables remote
control with the password `false` and binds the dev server to every interface. On this
machine that included a public address (<public IPv4>), so the deck and the Vite dev
server were reachable from outside.

## Evidence
`npx slidev --port 3030 --remote false` printed "remote control > http://<each interface
IP>:3030/entry?password=false/", and `netstat` showed `0.0.0.0:3030 LISTENING`. The process
was stopped about two minutes after it started. Without the flag, Slidev 52.20.1 printed
"remote control > pass --remote to enable" and listened on `[::1]:3030` only.

## Consequences
- Start the deck with `npm run dev` (plain `slidev --open`), never with `--remote`.
- To be explicit, `--bind 127.0.0.1` restricts it. Slidev still chose `[::1]` (localhost),
  so `curl http://127.0.0.1:3030` fails while `http://localhost:3030` works.
- After starting any dev server, check the bind address with `netstat`.

## Confidence and limits
Slidev 52.20.1 on Windows 11, seen once and checked against the run without the flag. Whether
anything reached the server in those two minutes is unknown; it served only the deck's
public content and the dev server's files.

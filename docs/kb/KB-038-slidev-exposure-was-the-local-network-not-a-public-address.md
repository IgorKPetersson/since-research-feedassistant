# KB-038 — The 2026-10-05 Slidev exposure reached the local network, not the internet over IPv4 (corrects KB-032)

**Area:** Presentation (Slidev) — dev server
**Status:** verified
**Date:** 2026-10-06  ·  **From:** T-071, T-048

## Claim
KB-032's mechanism holds (`--remote false` turns remote access on and binds every
interface), but its consequence was overstated. <public IPv4>, which Slidev and Streamlit
both print as an "External URL", is the router's public IPv4 address, not an address on
this machine. For the two minutes it ran, the dev server was reachable from the local
network, and over the machine's global IPv6 addresses if the router lets inbound IPv6
through, which was not tested. It was not reachable over IPv4 from the internet.

## Evidence
- `Get-NetIPAddress` (2026-10-05): IPv4 <LAN IPv4>, <virtual adapter IPv4>, <virtual adapter IPv4> and
  link-local addresses; no <public IPv4>. Global IPv6 <global IPv6> on Ethernet.
- Windows Firewall on, inbound default block; an enabled inbound allow rule for
  `C:\Program Files\nodejs\node.exe` on the Private profile; the Ethernet network is
  Private. Slidev runs on Node.

## Consequences
KB-032 is marked superseded. The rule stands: start the deck with `npm run dev`, never
with `--remote`, and check the bind address after starting any server.

## Confidence and limits
The router's IPv6 inbound policy is unknown.

# KB-037 — Streamlit by default listens on every interface and sends usage statistics

**Area:** UI (Streamlit) — server and browser defaults
**Status:** verified
**Date:** 2026-10-05  ·  **From:** T-071, T-074

## Claim
Streamlit 1.64 with no `server.address` binds `0.0.0.0` and `[::]`, and prints a Network
URL and an External URL. With no `browser.gatherUsageStats`, the default is `true`: the
browser sends usage statistics to Streamlit.

## Evidence
- `netstat` on a plain `streamlit run app.py`: `0.0.0.0:8501` and `[::]:8501 LISTENING`;
  the log listed `http://<LAN IPv4>:8501` and `http://<public IPv4>:8501` (the router's
  public IPv4, not on this machine). The machine has global IPv6 addresses, which `[::]`
  covered. Only Windows Firewall (no allow rule for Python 3.12) kept others out.
- `streamlit config show`: `# Default: true` / `gatherUsageStats = true`.
- After `server.address = "127.0.0.1"`: `127.0.0.1:8501` only, the LAN address refused.
  After `gatherUsageStats = false`: shown as false by `streamlit config show`.

## Consequences
Both are set in `.streamlit/config.toml` (D-020). A fresh clone gets them from the repo.

## Confidence and limits
Streamlit 1.64.0 on Windows 11. Whether the IPv6 port was reachable from the internet
through the router was not tested.

#!/usr/bin/env bash
# Daily data update for trade-helper-v1.
#
# Fetches the whole universe (idempotent upsert — safe to re-run) with polite
# pacing. Run it after market close so the newest bar is the final close.
#
# Cron example (weekdays, 6pm):
#   0 18 * * 1-5 /path/to/trade-helper-v1/scripts/daily.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LOG="$ROOT/data/daily-fetch.log"

echo "[$(date -Iseconds)] daily fetch start" >> "$LOG"
cd "$ROOT/backend"
"$ROOT/.venv/bin/python" -u -m app.fetch --universe --delay 1 >> "$LOG" 2>&1
echo "[$(date -Iseconds)] daily fetch done" >> "$LOG"

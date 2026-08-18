[Project home](../README.md) · [Docs](../docs/README.md) · [Roadmap](../docs/roadmap.md) · [Changelog](../CHANGELOG.md)

# data/

Local market-data store. **Gitignored — never commit files in this folder.**

- SQLite database(s) with daily bars live here.
- Updated through explicit CLI commands or the local Data Management page.
- Data Management separates Yahoo securities from FRED economic series, shows
  coverage/freshness, and reports each manual refresh result.
- Unattended cron is parked. The database remains local and a refresh job's
  in-memory progress does not survive a server restart.
- This README exists only so the folder shows up in the repo; the data itself does not.

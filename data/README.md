# Local data

This directory is Git-ignored except for this file. It contains SQLite databases and resumable research caches; never commit market data or generated caches.

Update data through explicit CLI commands or Data Management. Yahoo securities and non-tradable FRED context remain separate. Unattended refresh is parked, and current in-memory refresh progress does not survive server restart. See [the data contract](../docs/adr/0002-market-data-contract.md).

`market.db`'s `key_library` table (`0.61.0`) can hold locally-stored API credentials (e.g. `FRED_API_KEY`, via `app.store.set_key`) so they survive across sessions without an env var. This is exactly why this whole directory must never be committed — a credential in `key_library` is no different from one in an env var for that purpose, and this file is the only exception to the git-ignore.

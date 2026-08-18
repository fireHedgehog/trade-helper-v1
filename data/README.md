# Local data

This directory is Git-ignored except for this file. It contains SQLite databases and resumable research caches; never commit market data or generated caches.

Update data through explicit CLI commands or Data Management. Yahoo securities and non-tradable FRED context remain separate. Unattended refresh is parked, and current in-memory refresh progress does not survive server restart. See [the data contract](../docs/adr/0002-market-data-contract.md).

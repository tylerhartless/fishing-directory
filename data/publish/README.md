# Pipeline output drop zone

Files here are the source of truth for the frontend's canonical spot data.

## Layout

```
data/publish/
├── tx/
│   └── spots.json
├── fl/
│   └── spots.json
└── ...
```

One directory per state (lowercase 2-letter code). Each directory contains a single `spots.json` — a JSON array of canonical spot records produced by the `fishing-data-pipeline` repo.

## Adding or updating a state

1. Generate the state's `spots.json` from the pipeline
2. Drop it into `data/publish/<state-code>/spots.json` (overwrite the existing file if updating)
3. Commit (e.g. `git commit -m "Refresh TX spots, pipeline rev <short-sha>"`)
4. Push and deploy

No other wiring required — the build globs `data/publish/*/spots.json` automatically.

## Schema

The JSON shape is documented in the pipeline repo: `fishing-data-pipeline/publish/SCHEMA_DELTA.md`. The frontend's `FishingSpot` interface (`frontend/src/lib/database.ts`) mirrors that shape and derives a `canonical_id` from `{state}-{county-slug}-{name-slug}-{record-id-tail}` at load time.

## Empty drop zone

If no state directories exist (or none contain `spots.json`), the build runs cleanly and produces no per-spot pages. Useful for fresh clones before you've pulled the data over.

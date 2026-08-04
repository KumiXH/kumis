# FLUX metadata

This directory is the auditable source of truth for the FLUX reading library.

- `seed_papers.json`: canonical reading sequence and initial verified identifiers.
- `raw/`: cached API responses.
- `candidates.json`: discovered candidate papers before full-text screening.
- `flux_papers.json/csv`: final included papers with explicit FLUX-use evidence.
- `excluded_candidates.csv`: screened candidates and exclusion reasons.
- `download_manifest.json`: local files, source URLs, hashes, and validation status.

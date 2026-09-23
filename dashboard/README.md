# ORD Turnaround Reconstruction Audit

One-page, read-only Streamlit dashboard for the January 2024 MQ Phase 0 audit.
## Live Dashboard

**Phase 0 Reconstruction Audit:**  
https://ord-turnaround-audit.streamlit.app

This dashboard presents the data reconstruction and quality-audit stage of the project, including accepted turnaround pairs, rejection reasons, ground-gap distributions, and pair-level inspection.

The final ML risk-prediction dashboard will be developed in a later phase.

## Run locally

Use Python 3.11 or newer. From the project root, install the three direct dependencies in your chosen Python environment:

```sh
python -m pip install -r dashboard/requirements.txt
python -m streamlit run dashboard/app.py --server.address 127.0.0.1 --server.port 8501
```

Open http://127.0.0.1:8501. Run from the project root so Streamlit reads `.streamlit/config.toml`. Data paths resolve relative to the application file, independently of the working directory.

## Data sources

- `outputs/phase0_mq_arrival_audit.csv`: all focal arrivals; KPI totals and primary rejection reasons.
- `outputs/phase0_mq_observed_pairs.csv`: accepted observed pairs; ground-gap chart and explorer.

The app does not write data, run the audit script, or read raw BTS files. The two small CSVs are reread and validated on each rerun. Counts are calculated, never hardcoded.

## Validation

Before displaying results, the application verifies required columns, strict boolean parsing, January focal dates, unique inbound IDs, accepted inbound IDs and outbound assignments across files, unique accepted outbound IDs, mutually exclusive rejection reasons and totals, ground-gap category totals and numeric boundaries, explicit UTC timestamps, finite numeric fields, and consistency between timestamps, gaps, remaining time, and departure delay. A failure produces a clear error and stops the dashboard.

## Reading the dashboard

- KPIs and charts always describe the full January audit. Filters apply only to the accepted-pair table.
- Primary rejection reasons are mutually exclusive. Overlapping warnings are not added together.
- Ground-gap bins are `(0,15]`, `(15,180]`, `(180,360]`, and `>360` minutes. The zero-count bin is displayed.
- The inbound-date filter uses the original flight date, which can differ from the actual arrival date after overnight travel or delays.
- UTC timestamps remain unchanged in the sources. Display values use timezone-aware `America/Chicago` conversion and explicitly show the local timezone abbreviation.
- Negative remaining minutes and negative departure delays are retained.
- Acceptance is consistency under the documented reconstruction rules, not aircraft-assignment accuracy. High-confidence observed turnaround pairs are reconstructed from realized BTS aircraft movements and should not be interpreted as confirmed real-time aircraft assignments. Long observed gaps may still contain unobserved movements.

This dashboard has no modeling cohort, ML model, extra pages, API, authentication, or deployment configuration.

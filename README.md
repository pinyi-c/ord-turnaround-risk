# ORD Turnaround Risk Replay

A data-engineering portfolio project investigating one-step aircraft turnaround reconstruction at Chicago O'Hare. Its primary user is an **airline operations / network-control analyst** exploring whether observed aircraft movements can support a retrospective departure-risk study.

**Current milestone: Phase 0 — reconstruction feasibility and audit dashboard.** No model has been trained. This project does not optimize airline operations or recommend aircraft swaps.

## Scope

- Airport: Chicago O'Hare (**ORD**).
- Focal reporting carrier: **MQ**.
- Focal month: **January 2024**, using inbound flight date.
- December 2023 and February 2024 supply boundary context only.
- One step: inbound flight **A → turnaround at ORD → outbound flight B**.

A turnaround pair links A to the immediate next observed operated movement B of the same aircraft. A must arrive at ORD, B must depart ORD after A's actual gate arrival, and both must pass the documented reconstruction checks. The BTS tail number identifies the aircraft recorded as operating a flight and makes this linkage possible. Flight number alone does not uniquely identify an aircraft movement.

## Phase 0 methodology

1. Read the three BTS Reporting Carrier On-Time Performance files without modifying them.
2. Retain observed movements for tails used by MQ, including other-carrier records as potential intervening movements.
3. Reconstruct date-aware UTC departure and arrival timestamps from flight date, scheduled departure, signed departure delay, elapsed time, and airport timezones. Check the reconstructed clocks against reported actual times.
4. Order operated movements by tail and actual departure. Inspect the immediate successor without skipping observed movements.
5. Reject diversions, unresolved timestamps, discontinuities, overlaps, ambiguous ordering, and duplicate outbound use. Conservatively exclude same-tail cancellations scheduled during the ground interval and unresolved preceding movements.
6. Calculate actual ground gap, remaining time until scheduled departure, and the observed outbound departure delay. Preserve a row-level acceptance/rejection audit.

Detailed rules, examples, boundary cases, and source hashes are in [the feasibility notes](notes/feasibility.md). The standalone investigation is in [the Phase 0 audit script](work/phase0_mq_pair_audit.py).

## Key results

| January 2024 MQ result | Count / rate |
|---|---:|
| Non-cancelled ORD arrivals | 1,970 |
| Accepted high-confidence observed turnaround pairs | 1,872 |
| Acceptance under reconstruction rules | 95.03% |
| Rejected cases | 98 |
| Accepted pairs with actual ground gap >15 through 180 minutes | 1,693 |

Accepted ground-gap counts are 0 for `(0,15]`, 1,693 for `(15,180]`, 70 for `(180,360]`, and 109 for `>360` minutes. Bands include their upper endpoint. The three-month context recovers three accepted February successors for January arrivals, all outside the actual-short-turn cohort.

Primary rejection counts are 54 for a same-tail cancellation scheduled during the ground interval, 18 for a next movement originating elsewhere, 11 for diverted outbound flights, 9 for unresolved preceding movements, and 6 for diverted inbound flights. These primary reasons are mutually exclusive; additional warnings may overlap.

### Interpretation and limitations

**High-confidence observed turnaround pairs are reconstructed from realized BTS aircraft movements and should not be interpreted as confirmed real-time aircraft assignments.**

- Acceptance measures internal consistency under the reconstruction rules, not aircraft-assignment accuracy or an independently measured ground-truth match rate.
- Reported tail assignments and schedules do not establish what an analyst knew at inbound arrival.
- Long observed gaps may contain unobserved movements. The available data is not a complete aircraft movement history.
- Cancelled/diverted exclusions and conservative checks restrict the population represented by the accepted pairs.
- Actual ground gap depends on B's future departure event. It is a feasibility description, not an arrival-time modeling eligibility rule.
- An eventual delay association would not by itself establish that A caused B's delay.

## Audit dashboard

The single-page Streamlit dashboard uses Plotly and the existing Phase 0 outputs to show:

- Four data-derived KPI cards.
- Mutually exclusive rejection reasons.
- Accepted ground-gap distribution, including the zero-count band.
- An accepted-pair table filterable by inbound date, destination, ground gap, and tail.
- Timezone-aware ORD local timestamps and a methodology note.

Load-time checks validate schema, IDs, acceptance/rejection reconciliation, unique accepted outbound IDs, gap categories, UTC timestamps, and numeric/time consistency. The dashboard is read-only and does not access raw BTS files.

### Run locally

Use Python 3.11 or newer. From the repository root:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r dashboard/requirements.txt
python -m streamlit run dashboard/app.py --server.address 127.0.0.1 --server.port 8501
```

Open **http://127.0.0.1:8501**. On Windows, activate with `.venv\Scripts\activate` instead. Run from the repository root so Streamlit loads `.streamlit/config.toml`.

The two small generated CSVs are intended to accompany this milestone, allowing the dashboard to run without raw-data downloads. [Dashboard details](dashboard/README.md) describe the display and validation behavior.

## Repository layout

```text
.
├── README.md
├── .gitignore
├── .streamlit/config.toml
├── dashboard/
│   ├── app.py
│   ├── requirements.txt
│   └── README.md
├── notes/feasibility.md
├── outputs/
│   ├── phase0_mq_arrival_audit.csv
│   └── phase0_mq_observed_pairs.csv
├── work/
│   ├── phase0_mq_pair_audit.py
│   └── airport_timezones_reference.csv
└── data/raw/                         # local only; ignored by Git
```

The `work/` files are retained as reproducible Phase 0 analysis and its reference input; they are not a production pipeline.

## Data and reproduction

Raw source: BTS **Reporting Carrier On-Time Performance**. The raw files remain read-only and are excluded from Git:

- `data/raw/2023-12_reporting.csv`
- `data/raw/2024-01_reporting.csv`
- `data/raw/2024-02_reporting.csv`

Required export columns and raw-source hashes are recorded in the feasibility notes. Airport timezone reference provenance is recorded there and in the reference CSV; it includes OpenFlights data and BIH/XWA supplements.

The existing Phase 0 audit can be rerun, after obtaining those inputs, with:

```sh
python work/phase0_mq_pair_audit.py
```

This rerun requires pandas and numpy (numpy is installed with pandas) and **refreshes both generated CSVs and the marked section in the feasibility notes**. It does not modify raw CSVs. Running the dashboard does not rerun this audit. The script intentionally targets this fixed Phase 0 dataset rather than a general ingestion workflow.

## Status and next step

Phase 0 feasibility analysis and Dashboard v1 are complete. The current evidence supports **moving to modeling design**, not model training yet.

Next: define the eligible population using information available at inbound arrival, document permitted features and timing assumptions, and choose chronological evaluation periods and simple baselines. Preserve the distinction between actual-ground-gap and remaining-scheduled-time cohorts. No ML, live feed, API, cloud infrastructure, or deployment is part of this milestone.

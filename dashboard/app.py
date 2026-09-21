"""Read-only Streamlit view of the existing Phase 0 audit outputs."""
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
PAIR_PATH = ROOT / "outputs/phase0_mq_observed_pairs.csv"
AUDIT_PATH = ROOT / "outputs/phase0_mq_arrival_audit.csv"
BANDS = ["(0,15]", "(15,180]", "(180,360]", ">360"]
BAND_LABELS = dict(zip(BANDS, ["> 0–15", "> 15–180", "> 180–360", "> 360 minutes"]))
REASONS = {
    "cancelled_record_during_ground_interval": "Same-tail cancellation scheduled<br>during ground interval",
    "next_origin_not_ORD": "Immediate next movement<br>originates elsewhere",
    "diverted_outbound": "Diverted outbound",
    "unresolved_preceding_movement": "Unresolved preceding movement",
    "diverted_inbound": "Diverted inbound",
}
TIMES = ["actual_inbound_arrival_utc", "scheduled_outbound_departure_utc", "actual_outbound_departure_utc"]
NUMBERS = ["remaining_minutes_at_arrival", "actual_ground_gap_minutes", "outbound_departure_delay_minutes"]
PAIR_COLUMNS = ["inbound_id", "outbound_id", "accepted", "tail", "inbound_date", "inbound_flight",
                "inbound_origin", "outbound_flight", "outbound_destination", "gap_band", *TIMES, *NUMBERS]
AUDIT_COLUMNS = ["inbound_id", "outbound_id", "accepted", "primary_reason", "inbound_date"]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate_data(pairs, audit):
    """Return typed copies; never change input files or caller-owned frames."""
    pairs, audit = pairs.copy(), audit.copy()
    for frame, required, name in [(pairs, PAIR_COLUMNS, PAIR_PATH.name), (audit, AUDIT_COLUMNS, AUDIT_PATH.name)]:
        missing = sorted(set(required) - set(frame.columns))
        require(not missing, f"{name}: missing required columns: {', '.join(missing)}")
        require(len(frame) > 0, f"{name}: the file is empty.")
        normalized = frame["accepted"].astype(str).str.strip().str.lower()
        require(normalized.isin(["true", "false"]).all(), f"{name}: accepted must contain only True or False.")
        frame["accepted"] = normalized.eq("true")
        require(frame.inbound_id.ne("").all() and frame.inbound_id.is_unique, f"{name}: inbound IDs must be present and unique.")
        frame["inbound_date"] = pd.to_datetime(frame.inbound_date, format="%Y-%m-%d", errors="raise").dt.date
        require(all(v.year == 2024 and v.month == 1 for v in frame.inbound_date), f"{name}: expected January 2024 focal inbound dates.")
    require(pairs.accepted.all(), "The accepted-pairs file contains rejected records.")
    accepted = audit[audit.accepted]
    rejected = audit[~audit.accepted]
    require(len(accepted) + len(rejected) == len(audit), "Accepted and rejected counts do not reconcile with total arrivals.")
    require(set(pairs.inbound_id) == set(accepted.inbound_id), "Accepted inbound IDs differ between the two files.")
    left = pairs.set_index("inbound_id").outbound_id.sort_index()
    right = accepted.set_index("inbound_id").outbound_id.sort_index()
    require(left.equals(right), "Accepted outbound assignments differ between the two files.")
    require(pairs.outbound_id.ne("").all() and pairs.outbound_id.is_unique, "Accepted outbound IDs must be present and unique.")
    require(accepted.primary_reason.eq("accepted").all(), "Accepted audit rows have inconsistent primary reasons.")
    require(rejected.primary_reason.isin(REASONS).all(), "Rejected rows contain a missing or unrecognized primary_reason.")
    require(int(rejected.primary_reason.value_counts().sum()) == len(rejected), "Primary rejection counts do not reconcile.")
    for col in TIMES:
        # Source contract requires UTC; convert only after checking explicit offsets.
        require(pairs[col].str.contains(r"(?:Z|\+00:00)$", regex=True).all(), f"{col}: expected explicit UTC timestamps.")
        pairs[col] = pd.to_datetime(pairs[col], utc=True, errors="raise")
        require(pairs[col].notna().all(), f"{col}: missing timestamp.")
    for col in NUMBERS:
        pairs[col] = pd.to_numeric(pairs[col], errors="raise")
        require(pairs[col].notna().all() and ~pairs[col].isin([float("inf"), -float("inf")]).any(), f"{col}: missing or non-finite value.")
    require(pairs.actual_ground_gap_minutes.gt(0).all(), "Accepted ground gaps must be positive.")
    calculated = pd.cut(pairs.actual_ground_gap_minutes, [0, 15, 180, 360, float("inf")], labels=BANDS, right=True)
    require(calculated.astype(str).eq(pairs.gap_band).all(), "Ground-gap bands disagree with numeric gaps.")
    require(int(pairs.gap_band.value_counts().reindex(BANDS, fill_value=0).sum()) == len(pairs), "Accepted gap counts do not reconcile.")
    for start, end, value in [
        (TIMES[0], TIMES[2], NUMBERS[1]), (TIMES[0], TIMES[1], NUMBERS[0]), (TIMES[1], TIMES[2], NUMBERS[2])
    ]:
        actual = (pairs[end] - pairs[start]).dt.total_seconds() / 60
        require((actual - pairs[value]).abs().lt(0.000001).all(), f"{value}: values disagree with timestamps.")
    return pairs, audit


def load_data():
    # These small local files are reread on rerun, so edited outputs cannot hide behind a stale cache.
    return validate_data(pd.read_csv(PAIR_PATH, dtype=str, keep_default_na=False),
                         pd.read_csv(AUDIT_PATH, dtype=str, keep_default_na=False))


def chart_style(fig):
    fig.update_layout(template="plotly_white", height=320, margin=dict(l=0, r=30, t=15, b=30),
                      font=dict(family="Arial, sans-serif", color="#334155", size=12),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=False)
    fig.update_xaxes(fixedrange=True, zeroline=False)
    fig.update_yaxes(fixedrange=True, zeroline=False)
    return fig


def main():
    st.set_page_config(page_title="ORD Turnaround Reconstruction Audit", layout="wide")
    st.markdown("<style>.block-container{padding-top:2rem;padding-bottom:2rem;max-width:1500px}"
                "h1{letter-spacing:-.035em}div[data-testid='stMetricValue']{font-size:2rem}"
                "[data-testid='stMetricLabel']{min-height:2.6rem}"
                "[data-testid='stMetricLabel'] p{white-space:normal;overflow:visible;text-overflow:clip}</style>", unsafe_allow_html=True)
    st.title("ORD Turnaround Reconstruction Audit")
    st.caption("January 2024 · MQ · Chicago O'Hare (ORD)")
    try:
        pairs, audit = load_data()
    except (OSError, ValueError, KeyError) as exc:
        st.error(f"Audit data validation failed: {exc}")
        st.info("Check the two Phase 0 CSVs in outputs/. No data has been changed.")
        st.stop()
    accepted_count = int(audit.accepted.sum())
    rejected = audit[~audit.accepted]
    metrics = st.columns(4)
    for col, label, value in zip(metrics,
        ["January MQ non-cancelled ORD arrivals", "Accepted high-confidence observed pairs", "Acceptance rate", "Rejected cases"],
        [f"{len(audit):,}", f"{accepted_count:,}", f"{accepted_count / len(audit):.2%}", f"{len(rejected):,}"]):
        with col:
            with st.container(border=True):
                st.metric(label, value)
    st.caption("Acceptance measures consistency under the documented reconstruction rules—not aircraft-assignment accuracy. "
               "KPIs and charts cover the full January audit.")
    left, right = st.columns([1.15, 1], gap="large")
    with left:
        st.subheader("Why cases were rejected")
        st.caption("Mutually exclusive primary reasons · one reason per rejected arrival")
        counts = rejected.primary_reason.value_counts().sort_values(ascending=False)
        fig = go.Figure(go.Bar(x=counts.values, y=[REASONS[k] for k in counts.index], orientation="h",
                              marker_color="#55738C", text=counts.values, textposition="outside", cliponaxis=False,
                              hovertemplate="%{y}: %{x} cases<extra></extra>"))
        chart_style(fig).update_yaxes(autorange="reversed", showgrid=False)
        fig.update_xaxes(title="Rejected arrivals", rangemode="tozero", dtick=10,
                         range=[0, max(int(counts.max()) if len(counts) else 0, 1)*1.2])
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
    with right:
        st.subheader("Accepted ground gaps")
        st.caption("Actual inbound gate arrival → actual outbound gate departure")
        gaps = pairs.gap_band.value_counts().reindex(BANDS, fill_value=0)
        fig = go.Figure(go.Bar(x=[BAND_LABELS[b] for b in BANDS], y=gaps.values,
                              marker_color="#55738C", text=[f"{v:,}" for v in gaps.values],
                              textposition="outside", cliponaxis=False,
                              hovertemplate="%{x}: %{y:,} observed pairs<extra></extra>"))
        chart_style(fig).update_yaxes(title="Observed pairs", range=[0, max(int(gaps.max()),1)*1.2])
        fig.update_xaxes(title="Actual ground gap (minutes)", categoryorder="array", categoryarray=list(BAND_LABELS.values()))
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
    st.subheader("Accepted-pair explorer")
    st.caption("Filters apply only to this table. Inbound date is the source flight date; timestamps are displayed in ORD local time (America/Chicago).")
    filters = st.columns([1.2, 1, 1, 1])
    start, end = pairs.inbound_date.min(), pairs.inbound_date.max()
    dates = filters[0].date_input("Inbound date", value=(start,end), min_value=start, max_value=end)
    dest = filters[1].multiselect("Outbound destination", sorted(pairs.outbound_destination.unique()), placeholder="All destinations")
    bands = filters[2].multiselect("Ground-gap band", BANDS, format_func=BAND_LABELS.get, placeholder="All ground gaps")
    tails = filters[3].multiselect("Tail number", sorted(pairs['tail'].unique()), placeholder="All aircraft")
    mask = pd.Series(True, index=pairs.index)
    if len(dates) == 2:
        mask &= pairs.inbound_date.between(*dates)
    else:
        st.info("Select an end date to complete the date range.")
        mask &= False
    for values, col in [(dest,"outbound_destination"),(bands,"gap_band"),(tails,"tail")]:
        if values:
            mask &= pairs[col].isin(values)
    selected = pairs.loc[mask].sort_values("actual_inbound_arrival_utc")
    st.caption(f"{len(selected):,} matching rows of {len(pairs):,} accepted observed pairs")
    display = selected[["tail", "inbound_flight", "inbound_origin", TIMES[0], "outbound_flight", "outbound_destination", TIMES[1], TIMES[2], *NUMBERS]].copy()
    for col in TIMES:
        # Format explicit local strings to avoid a browser silently reinterpreting UTC.
        display[col] = display[col].dt.tz_convert("America/Chicago").dt.strftime("%Y-%m-%d %H:%M %Z")
    labels = {"tail":"Tail", "inbound_flight":"Inbound flight", "inbound_origin":"Inbound origin",
              TIMES[0]:"Inbound gate arrival · ORD local", "outbound_flight":"Outbound flight", "outbound_destination":"Outbound destination",
              TIMES[1]:"Scheduled departure · ORD local", TIMES[2]:"Actual departure · ORD local",
              NUMBERS[0]:"Remaining minutes at arrival", NUMBERS[1]:"Actual ground gap · min", NUMBERS[2]:"Departure delay · min"}
    config = {col: st.column_config.NumberColumn(labels[col], format="%d") if col in NUMBERS else
              st.column_config.TextColumn(labels[col], width="medium" if col in TIMES else None) for col in display.columns}
    st.dataframe(display, hide_index=True, width="stretch", height=390, column_config=config)
    st.caption("Negative remaining minutes mean scheduled departure had already passed. Negative departure delay means an early departure.")
    with st.container(border=True):
        st.markdown("**How to read this audit**")
        st.write("High-confidence observed turnaround pairs are reconstructed from realized BTS aircraft movements and should not be interpreted as confirmed real-time aircraft assignments.")
        st.write("Acceptance measures consistency under the audit rules. Long observed gaps may still contain unobserved movements. "
                 "Ground-gap bands include their upper endpoint: exactly 15 minutes belongs to the first band.")


if __name__ == "__main__":
    main()

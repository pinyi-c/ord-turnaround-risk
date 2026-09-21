"""Standalone Phase 0 audit. Reads raw CSVs; writes two audit CSVs only.

Run from project root with Python + pandas + numpy. No model or pipeline.
Reference: OpenFlights airports.dat; BIH/XWA AirNav timezone supplements.
All dates are December 2023–February 2024 (no US DST transition).
"""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from collections import Counter
import hashlib
import json
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FILES = sorted((ROOT / 'data/raw').glob('*_reporting.csv'))
assert {p.name for p in FILES} == {
    '2023-12_reporting.csv', '2024-01_reporting.csv', '2024-02_reporting.csv'}
def digest(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()
before = {p.name: digest(p) for p in FILES}
tails = set()
for p in FILES:
    for c in pd.read_csv(p, dtype=str, keep_default_na=False, chunksize=100000,
                         usecols=['OP_UNIQUE_CARRIER', 'TAIL_NUM']):
        tails.update(c.loc[c.OP_UNIQUE_CARRIER.eq('MQ'), 'TAIL_NUM'].str.strip())
tails.discard('')
parts = []
for p in FILES:
    offset = 0
    for c in pd.read_csv(p, dtype=str, keep_default_na=False, chunksize=100000):
        c['source_row'] = np.arange(offset + 2, offset + len(c) + 2)
        offset += len(c)
        c['TAIL_NUM'] = c.TAIL_NUM.str.strip().str.upper()
        c = c[c.TAIL_NUM.isin(tails) | c.OP_UNIQUE_CARRIER.eq('MQ')].copy()
        c['source_file'] = p.name
        c['id'] = c.source_file + ':' + c.source_row.astype(str)
        parts.append(c)
d = pd.concat(parts, ignore_index=True).set_index('id', drop=False)
ref = pd.read_csv(ROOT / 'work/airport_timezones_reference.csv')
offsets = {}
for a, z in zip(ref.airport, ref.iana_timezone):
    try:
        offsets[a] = datetime(2024, 1, 15, tzinfo=ZoneInfo(z)).utcoffset().total_seconds()/60
    except Exception:
        pass
def clock(col):
    v = pd.to_numeric(d[col], errors='coerce')
    return (v//100*60+v%100).where(v.eq(2400) | (v.ge(0)&v.lt(2400)&v.mod(100).lt(60)))
date = pd.to_datetime(d.FL_DATE, format='%m/%d/%Y %I:%M:%S %p', errors='coerce')
d['date'] = date.dt.strftime('%Y-%m-%d')
base = date.astype('int64') / 60000000000
d['scheduled'] = (base + clock('CRS_DEP_TIME') - d.ORIGIN.map(offsets)).where(date.notna())
delay = pd.to_numeric(d.DEP_DELAY, errors='coerce')
dep = d.scheduled + delay
dep_ok = (dep + d.ORIGIN.map(offsets)).mod(1440).eq(clock('DEP_TIME').mod(1440))
d['dep'] = dep.where(dep_ok & d.CANCELLED.eq('0.00'))
elapsed = pd.to_numeric(d.ACTUAL_ELAPSED_TIME, errors='coerce')
arr = d.dep + elapsed
arr_ok = (arr + d.DEST.map(offsets)).mod(1440).eq(clock('ARR_TIME').mod(1440))
d['arr'] = arr.where(arr_ok & elapsed.gt(0) & d.DIVERTED.eq('0.00'))
d['dep_clock_mismatch'] = dep.notna() & clock('DEP_TIME').notna() & ~dep_ok & d.CANCELLED.eq('0.00')
d['arr_clock_mismatch'] = arr.notna() & clock('ARR_TIME').notna() & ~arr_ok & d.CANCELLED.eq('0.00')
key = ['FL_DATE','OP_UNIQUE_CARRIER','OP_CARRIER_FL_NUM','ORIGIN','DEST','CRS_DEP_TIME']
d['duplicate'] = d.duplicated(key, keep=False)
operated = d[d.CANCELLED.eq('0.00') & d.TAIL_NUM.ne('')]
groups = {t:g.sort_values(['dep','source_file','source_row']) for t,g in operated[operated.dep.notna()].groupby('TAIL_NUM')}
unknown_tails = set(operated.loc[operated.dep.isna(),'TAIL_NUM'])
cancelgroups = {t:g for t,g in d[d.CANCELLED.eq('1.00') & d.TAIL_NUM.ne('')].groupby('TAIL_NUM')}
overlap = set()
next_ids = {}
previous_ids = {}
tie_ids = set()
for t,g in groups.items():
    rows = list(g.index)
    tie_ids.update(g.loc[g.dep.duplicated(keep=False)].index)
    for k,i in enumerate(rows):
        if k+1<len(rows): next_ids[i] = rows[k+1]
        if k: previous_ids[i] = rows[k-1]
    # Mark both participants of any known flight-interval overlap, not just adjacent rows.
    active = []
    for i,v in g.iterrows():
        active = [(j,end) for j,end in active if end>v.dep]
        for j,end in active:
            overlap.update([i,j])
        if pd.notna(v.arr): active.append((i,v.arr))

focal = d[d.source_file.eq('2024-01_reporting.csv') & d.OP_UNIQUE_CARRIER.eq('MQ') & d.DEST.eq('ORD') & d.CANCELLED.eq('0.00')]
def iso(x):
    return pd.to_datetime(x, unit='m', utc=True).isoformat() if pd.notna(x) else ''
def band(x):
    if pd.isna(x) or x<=0: return ''
    return '(0,15]' if x<=15 else '(15,180]' if x<=180 else '(180,360]' if x<=360 else '>360'
records = []
for i,a in focal.iterrows():
    flags=[]
    if not a.TAIL_NUM: flags.append('missing_tail')
    if a.DIVERTED=='1.00': flags.append('diverted_inbound')
    if pd.isna(a.dep) or pd.isna(a.arr): flags.append('unresolved_inbound_timestamp')
    if a.TAIL_NUM in unknown_tails: flags.append('unknown_order_on_tail')
    if a.duplicate: flags.append('duplicate_flight_key')
    if i in tie_ids: flags.append('tied_departure_sequence')
    if i in overlap: flags.append('overlapping_movement')
    b_id=next_ids.get(i)
    b=d.loc[b_id] if b_id else None
    prior=previous_ids.get(i)
    # An unknown preceding arrival could overlap A: conservatively flag proximity.
    if prior and pd.isna(d.loc[prior,'arr']): flags.append('unresolved_preceding_movement')
    gap=np.nan; remaining=np.nan
    if b is None:
        flags.extend(['no_next_observed_movement','month_boundary_uncertainty'])
    else:
        if b.ORIGIN!='ORD': flags.append('next_origin_not_ORD')
        if b.OP_UNIQUE_CARRIER!='MQ': flags.append('next_carrier_not_MQ')
        if b.DIVERTED=='1.00': flags.append('diverted_outbound')
        if pd.isna(b.dep) or pd.isna(b.arr) or pd.isna(b.scheduled): flags.append('unresolved_outbound_timestamp')
        if b.duplicate: flags.append('duplicate_flight_key')
        if b_id in tie_ids: flags.append('tied_departure_sequence')
        if b_id in overlap: flags.append('overlapping_movement')
        if pd.notna(a.arr) and pd.notna(b.dep):
            gap=b.dep-a.arr
            remaining=b.scheduled-a.arr
            if gap<=0: flags.append('outbound_not_after_arrival')
            cg=cancelgroups.get(a.TAIL_NUM)
            if cg is not None:
                if cg.scheduled.isna().any(): flags.append('unresolved_cancelled_record')
                if ((cg.scheduled>=a.arr)&(cg.scheduled<=b.dep)).any(): flags.append('cancelled_record_during_ground_interval')
    flags=list(dict.fromkeys(flags))
    records.append(dict(inbound_id=i, outbound_id=b_id or '', tail=a.TAIL_NUM,
        inbound_date=a.date, inbound_flight=a.OP_CARRIER_FL_NUM, inbound_origin=a.ORIGIN,
        outbound_date=b.date if b is not None else '', outbound_flight=b.OP_CARRIER_FL_NUM if b is not None else '',
        outbound_origin=b.ORIGIN if b is not None else '',outbound_destination=b.DEST if b is not None else '',
        actual_inbound_arrival_utc=iso(a.arr),actual_outbound_departure_utc=iso(b.dep) if b is not None else '',
        actual_ground_gap_minutes=gap, scheduled_outbound_departure_utc=iso(b.scheduled) if b is not None else '',
        remaining_minutes_at_arrival=remaining,outbound_departure_delay_minutes=float(b.DEP_DELAY) if b is not None and b.DEP_DELAY else np.nan,
        outbound_delay_ge_15=(float(b.DEP_DELAY)>=15) if b is not None and b.DEP_DELAY else None,
        gap_band=band(gap),has_next_observed=b is not None,
        feb_outbound=b is not None and b.source_file=='2024-02_reporting.csv',
        december_predecessor=bool(prior and d.loc[prior,'source_file']=='2023-12_reporting.csv'),
        flags=flags))
audit=pd.DataFrame(records)
reused=set(audit.loc[audit.outbound_id.ne('') & audit.outbound_id.duplicated(keep=False),'outbound_id'])
for k in audit.index:
    if audit.at[k,'outbound_id'] in reused: audit.at[k,'flags'].append('duplicate_outbound_use')
audit['accepted']=audit['flags'].map(lambda x:not x)
audit['primary_reason']=audit['flags'].map(lambda x:x[0] if x else 'accepted')
audit['warnings']=audit['flags'].map(lambda x:';'.join(x))
audit['short_turn']=audit.accepted & audit.gap_band.eq('(15,180]')
accepted=audit[audit.accepted].copy()
assert accepted.outbound_id.is_unique
assert (accepted.actual_ground_gap_minutes>0).all()
assert len(audit)==1970
assert len(accepted)+int((~audit.accepted).sum())==len(focal)
for _,r in accepted.iterrows():
    a=d.loc[r.inbound_id]; b=d.loc[r.outbound_id]
    assert a.TAIL_NUM==b.TAIL_NUM and a.DEST==b.ORIGIN=='ORD'
    assert next_ids[r.inbound_id]==r.outbound_id
    g=groups[a.TAIL_NUM]
    assert not ((g.dep>a.dep)&(g.dep<b.dep)).any()
assert before=={p.name:digest(p) for p in FILES}, 'Raw input changed'
(ROOT/'outputs').mkdir(exist_ok=True)
audit.drop(columns='flags').to_csv(ROOT/'outputs/phase0_mq_arrival_audit.csv',index=False)
accepted.drop(columns='flags').to_csv(ROOT/'outputs/phase0_mq_observed_pairs.csv',index=False)
summary=dict(raw_sha256=before,reference_sha256=digest(ROOT/'work/airport_timezones_reference.csv'),
    focal=len(focal),next_observed=int(audit.has_next_observed.sum()),accepted=len(accepted),short_turn=int(audit.short_turn.sum()),
    gap_bands=accepted.gap_band.value_counts().to_dict(),primary=audit.primary_reason.value_counts().to_dict(),
    warnings=dict(Counter(f for fs in audit['flags'] for f in fs)),
    feb_candidates=int(audit.feb_outbound.sum()),feb_accepted=int(accepted.feb_outbound.sum()),feb_short=int((accepted.feb_outbound&accepted.short_turn).sum()),
    december_predecessors=int(audit.december_predecessor.sum()),december_accepted=int(accepted.december_predecessor.sum()),
    missing_timezones=sorted(set(d.ORIGIN)-set(offsets)),unknown_departure_rows=len(operated[operated.dep.isna()]),
    clock_mismatches={'dep':int(d.dep_clock_mismatch.sum()),'arr':int(d.arr_clock_mismatch.sum())})
print(json.dumps(summary,indent=2))
print('EDGE EXAMPLES')
print(audit[~audit.accepted][['inbound_id','tail','inbound_date','outbound_id','actual_ground_gap_minutes','warnings']].head(15).to_string(index=False))

# Append/replace only this audit's section, retaining prior feasibility findings.
heading = '## MQ immediate-next-movement audit — three-month context'
lines = [heading, '',
    '### Scope and acceptance rules', '',
    'January 2024 MQ non-canceled records with reported destination ORD are focal. December 2023 and February 2024 are context only. Counts are by inbound FL_DATE/source month, including flights whose actual arrival rolls to February. All three files were read without modification.', '',
    'The analysis retains all carriers for every tail appearing on MQ records. It orders non-canceled movements by reconstructed actual departure UTC, and examines the immediate successor without skipping any observed operated movement. Acceptance requires MQ on both legs, matching tail, A destination ORD, B origin ORD, positive actual ground gap, nondiverted legs, valid timestamps, no interval overlaps or ties, and unique B use.', '',
    'Cancelled rows are not operated movements. A same-tail cancelled record with scheduled departure between A arrival and B departure causes conservative exclusion, regardless of its origin. Its tail assignment is not interpreted as an actual movement. An unresolved preceding movement also causes conservative exclusion because its arrival cannot be checked against A departure. An operated record with unresolved departure would make the entire tail ambiguous; none occurred here.', '',
    'Timestamp method: scheduled departure date/clock plus signed DEP_DELAY determines actual departure, converted from origin local time to UTC. ACTUAL_ELAPSED_TIME determines arrival. Both reported actual clocks must agree modulo midnight. 2400 is preserved as next-day midnight. January standard-time offsets also apply to this December–February US dataset. No schedule-only sort is used. Missing diverted-leg elapsed times are not guessed.', '',
    'High-confidence observed turnaround pairs means internally consistent immediate observed adjacency under these rules. It does not establish uninterrupted physical presence at ORD, a complete movement history, or confirmed real-time aircraft assignments. Long gaps can conceal unreported movements. Gate-return detail and historical assignment snapshots are absent.', '',
    '### Results', '',
    '| Measure | Count |', '|---|---:|',
    f'| January MQ non-canceled ORD arrivals | {len(audit):,} |',
    f'| With immediate next observed operated movement | {int(audit.has_next_observed.sum()):,} |',
    f'| High-confidence observed turnaround pairs | {len(accepted):,} |',
    f'| Rejected | {int((~audit.accepted).sum()):,} |',
    f'| Current (15,180]-minute short-turn cohort | {int(audit.short_turn.sum()):,} |', '',
    '| Accepted actual ground gap | Count |', '|---|---:|']
for b in ['(0,15]','(15,180]','(180,360]','>360']:
    lines.append(f'| {b} minutes | {int(accepted.gap_band.eq(b).sum()):,} |')
lines += ['', 'Gap is actual gate departure B minus actual gate arrival A. The bands include the upper endpoint; exactly 15 is outside the current short-turn cohort. Gap-based filtering was not used to accept pairs. Remaining time is scheduled B departure minus actual A arrival, so it can be negative. Outbound delay and its >=15-minute label come from B DEP_DELAY.', '',
    '### Rejections and flags', '',
    'Primary reasons are mutually exclusive, assigned in the rule order in the audit script. Warning counts overlap and must not be added.', '',
    '| Primary rejection reason | Count |', '|---|---:|']
for reason,count in audit.loc[~audit.accepted,'primary_reason'].value_counts().items():
    lines.append(f'| {reason} | {count} |')
lines += ['', '| Warning / condition | Affected focal inbounds |', '|---|---:|']
allflags = Counter(f for fs in audit['flags'] for f in fs)
for flag in ['missing_tail','diverted_inbound','unresolved_inbound_timestamp','next_origin_not_ORD',
             'next_carrier_not_MQ','diverted_outbound','unresolved_outbound_timestamp',
             'unresolved_preceding_movement','cancelled_record_during_ground_interval',
             'unresolved_cancelled_record','unknown_order_on_tail','duplicate_flight_key',
             'tied_departure_sequence','overlapping_movement','outbound_not_after_arrival',
             'duplicate_outbound_use','no_next_observed_movement','month_boundary_uncertainty']:
    lines.append(f'| {flag} | {allflags[flag]} |')
lines += ['',
    'All focal non-canceled arrivals have tails. Six diverted inbounds have unresolved arrival timestamps. Twelve successor legs are diverted and have unresolved arrival timestamps; these warning counts overlap other reasons. No clock mismatches, unknown departure order, tied departures, known interval overlaps, or duplicate B use were found in the retained MQ-tail context. Missing unreported movements cannot be ruled out by these checks.', '',
    'Cancelled January MQ destination-ORD rows are excluded before the focal denominator: '+str(int((d.source_file.eq('2024-01_reporting.csv') & d.OP_UNIQUE_CARRIER.eq('MQ') & d.DEST.eq('ORD') & d.CANCELLED.eq('1.00')).sum()))+'. The cancellation-during-ground exclusion is deliberately conservative and is not proof that a cancelled flight was physically assigned to that aircraft.', '',
    '### Boundary recovery', '',
    f'- February supplies immediate successors for {int(audit.feb_outbound.sum())} January inbounds. {int(accepted.feb_outbound.sum())} are accepted; none belong to the short-turn cohort. Thus accepted pairs increase from {len(accepted)-int(accepted.feb_outbound.sum()):,} to {len(accepted):,} when these February successors are available.',
    f'- December supplies the predecessor context for {int(audit.december_predecessor.sum())} focal inbounds; all {int(accepted.december_predecessor.sum())} pass. These are strengthened predecessor checks, not newly recovered January A → B pairs.',
    '- No focal arrival is left without a successor in the three-month file. This removes observed search-edge uncertainty for these inbounds, not the wider incomplete-coverage limitation.', '',
    '| Inbound ID | Tail | February successor ID | Gap min | Result |', '|---|---|---|---:|---|']
for _,v in audit[audit.feb_outbound].iterrows():
    lines.append(f'| {v.inbound_id} | {v["tail"]} | {v.outbound_id} | {v.actual_ground_gap_minutes:.0f} | {v.primary_reason} |')
lines += ['',
    'The rejected boundary example N761RW arrives ORD on January 31, but the immediate next observed movement starts at MQT on February 9. Searching onward for an ORD departure would conceal this discontinuity and is not allowed.', '',
    '### 20 accepted examples', '',
    'Purposeful coverage sample: 15 short turns spread through January, two medium-gap turns, and all three accepted February successors. It is not a random or representative evaluation sample. Full source IDs and all fields are in outputs/phase0_mq_observed_pairs.csv. All timestamps below are UTC; dates are explicit.', '',
    '| Tail | A flight / origin | B flight / destination | A arrival UTC | B departure UTC | Gap min | B scheduled UTC | Remaining min | B delay min | Delay >=15 |',
    '|---|---|---|---|---|---:|---|---:|---:|---|']
short = accepted[accepted.short_turn].sort_values('actual_inbound_arrival_utc')
medium = accepted[accepted.gap_band.eq('(180,360]')].sort_values('actual_inbound_arrival_utc')
examples = pd.concat([short.iloc[np.linspace(0,len(short)-1,15,dtype=int)],medium.iloc[[0,-1]],accepted[accepted.feb_outbound]])
assert len(examples)==20 and examples.inbound_id.is_unique
def compact(v):
    return v.replace('T',' ').replace('+00:00','').removesuffix(':00') if v else 'unresolved'
for _,v in examples.iterrows():
    lines.append(f'| {v["tail"]} | {v.inbound_flight} / {v.inbound_origin} | {v.outbound_flight} / {v.outbound_destination} | {compact(v.actual_inbound_arrival_utc)} | {compact(v.actual_outbound_departure_utc)} | {v.actual_ground_gap_minutes:.0f} | {compact(v.scheduled_outbound_departure_utc)} | {v.remaining_minutes_at_arrival:.0f} | {v.outbound_departure_delay_minutes:.0f} | {v.outbound_delay_ge_15} |')
lines += ['', '### 10 rejected / edge-case examples', '',
    'Eight rejected examples cover the primary reasons and additional cases; two accepted edge cases expose limits of the modeling cohort.', '',
    '| Inbound ID | Tail | A route / B route | Gap min | Result / reason |', '|---|---|---|---:|---|']
rejected = audit[~audit.accepted]
edge = rejected.groupby('primary_reason',sort=True).head(1)
edge = pd.concat([edge,rejected[~rejected.index.isin(edge.index)].head(8-len(edge))])
edge = pd.concat([edge,accepted.nlargest(1,'actual_ground_gap_minutes'),accepted.nsmallest(1,'remaining_minutes_at_arrival')])
assert len(edge)==10 and edge.inbound_id.is_unique
for _,v in edge.iterrows():
    note=v.warnings if not v.accepted else ('accepted: very long observed gap; unreported movement risk' if v.actual_ground_gap_minutes==accepted.actual_ground_gap_minutes.max() else 'accepted: already late at inbound arrival; not early warning')
    gap = f'{v.actual_ground_gap_minutes:.0f}' if pd.notna(v.actual_ground_gap_minutes) else 'unresolved'
    lines.append(f'| {v.inbound_id} | {v["tail"]} | {v.inbound_origin}→ORD / {v.outbound_origin}→{v.outbound_destination} | {gap} | {note} |')
eligible=accepted.remaining_minutes_at_arrival.between(15,180,inclusive='both')
lines += ['', '### GO / NO-GO', '',
    '**GO to modeling design on MQ: observed reconstruction is feasible. NO-GO to training on the actual-ground-gap cohort as if it were selected at arrival.** The 1,693 short turns establish sample availability, but actual ground gap includes the future departure event and selecting on it can bias the target distribution.', '',
    f'Before fitting a baseline, freeze an arrival-time eligibility rule using remaining time to scheduled departure and evaluate the full supported observed-pair population. For illustration, {int(eligible.sum()):,} accepted pairs have 15–180 minutes remaining at arrival, regardless of eventual actual gap. This is a diagnostic, not a finalized model cohort.', '',
    f'{int((accepted.remaining_minutes_at_arrival<=-15).sum())} accepted pairs are already at least 15 minutes beyond scheduled departure at inbound arrival; {int((short.remaining_minutes_at_arrival<0).sum())} actual-short-turn pairs are already past scheduled departure. These should not be presented as successful early warnings. Gate-return limitations and retrospective aircraft assignment remain explicit. No model was trained.', '',
    '### Reproducibility and verification', '',
    '- Run work/phase0_mq_pair_audit.py with Python, pandas, and numpy. It reads only the three raw files plus the saved timezone reference and refreshes the two output CSVs and this marked notes section.',
    '- Source row IDs include the filename and 1-based CSV line number (header is line 1). They are audit locators for these immutable files, not proposed production flight IDs.',
    '- Assertions verify 1,970 focal rows, exact accepted/rejected reconciliation, unique outbound use, same-tail ORD continuity, positive gap, and no observed operated departure between accepted A and B.',
    '- SHA-256 hashes before and after the run verify that raw files are unchanged.', '',
    '| Raw file | SHA-256 |', '|---|---|']
for filename,h in before.items(): lines.append(f'| {filename} | {h} |')
lines += ['', 'Timezone reference: [OpenFlights](https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports.dat), with BIH and XWA supplements from [BIH](https://www.airnav.com/airport/KBIH) and [XWA](https://www.airnav.com/airport/XWA). Saved in work/airport_timezones_reference.csv; SHA-256 '+digest(ROOT/'work/airport_timezones_reference.csv')+'. All required origins were covered. This reference is not a historical assignment or schedule snapshot.', '']
note=ROOT/'notes/feasibility.md'
old=note.read_text().split(heading)[0].rstrip()
note.write_text(old+'\n\n'+'\n'.join(lines))
print('Updated notes; 20 accepted and 10 rejected/edge examples verified.')

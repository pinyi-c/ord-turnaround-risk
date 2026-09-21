# Phase 0: ORD turnaround feasibility

Source: January 2024 BTS export, originally named `T_ONTIME_REPORTING.csv`, now stored at `data/raw/2024-01_reporting.csv`. Read-only inspection; source unchanged.

## Initial inspection finding

The initial visual inspection found that tail-based reconstruction appears worth investigating: several manually inspected histories show an inbound to ORD followed by an outbound on the same tail. This is not a measured pairing-success rate or proof of continuous aircraft coverage. At the initial inspection, no candidate search, pipeline, model, or application had been implemented. The carrier-level exploratory search is documented below.

## Schema and coverage

January 1–31, 2024; all 31 flight dates are present. The CSV has exactly 15 columns and no declared types. All requested fields exist; identifiers and HHMM clocks were preserved as strings during inspection. Dates include a midnight suffix that is not a departure timestamp. Delays and elapsed time are decimal minute values; flags contain 0.00/1.00. Carrier names are not included, so results use source codes.

| Requested field | Exact column | Blank rows |
|---|---|---:|
| Flight date | `FL_DATE` | 0 |
| Reporting/operating carrier | `OP_UNIQUE_CARRIER` | 0 |
| Tail number | `TAIL_NUM` | 5,293 |
| Flight number | `OP_CARRIER_FL_NUM` | 0 |
| Origin | `ORIGIN` | 0 |
| Destination | `DEST` | 0 |
| Scheduled departure | `CRS_DEP_TIME` | 0 |
| Actual departure | `DEP_TIME` | 19,784 |
| Departure delay | `DEP_DELAY` | 19,858 |
| Scheduled arrival | `CRS_ARR_TIME` | 0 |
| Actual arrival | `ARR_TIME` | 20,633 |
| Arrival delay | `ARR_DELAY` | 21,901 |
| Actual elapsed time | `ACTUAL_ELAPSED_TIME` | 21,901 |
| Cancelled | `CANCELLED` | 0 |
| Diverted | `DIVERTED` | 0 |

| Metric | Result |
|---|---:|
| Total data rows (header excluded) | 547,271 |
| Nonblank tail rows | 541,978 (99.0328%) |
| Blank tail rows | 5,293 |
| Distinct nonblank tails | 5,604 |
| Rows with DEST = ORD | 20,327 |
| Rows with ORIGIN = ORD | 20,321 |
| Rows touching ORD (either endpoint; counted once) | 40,648 |
| ORD-touching rows with blank tails | 1,035 |

Counts include canceled/diverted records. “Arriving/departing ORD” here means the reported destination/origin, not confirmation that the aircraft physically completed that movement. Non-null tail means nonempty after whitespace trimming. Common literal placeholders NULL, NA, N/A, NONE, UNKNOWN, and 0 were not found.

### Top 10 carriers touching ORD

| Carrier code | Rows |
|---|---:|
| UA | 13,362 |
| OO | 8,235 |
| AA | 7,373 |
| MQ | 4,276 |
| YX | 2,747 |
| WN | 1,526 |
| NK | 1,276 |
| DL | 1,174 |
| AS | 313 |
| B6 | 180 |

## Five complete sample histories

Selected manually from low-row-count tails touching ORD to display every record for each selected tail compactly, including gaps and difficult cases. This is a purposeful, nonrepresentative sample. All monthly rows for these five tails are shown below.

Rows are in departure chronology for these inspected examples, checked against dates, local clocks, route continuity and timezone offsets. No general timestamp reconstruction or pairing logic was built. Times are local to each endpoint; +1 means arrival on the next calendar day. The date column is FL_DATE (scheduled departure date). Scheduled and actual columns each show departure / arrival.

### N831AA — 5 rows

| Date | Carrier | Flight | Origin | Destination | Scheduled dep / arr | Actual dep / arr | Note |
|---|---|---|---|---|---|---|---|
| 2024-01-01 | AA | 328 | DFW | ORD | 08:25 / 10:50 | 08:43 / 10:57 |  |
| 2024-01-01 | AA | 1109 | ORD | DFW | 12:01 / 14:30 | 11:56 / 14:00 |  |
| 2024-01-05 | AA | 1702 | DFW | ORD | 12:30 / 14:55 | 12:24 / 14:31 |  |
| 2024-01-24 | AA | 2346 | ORD | DFW | 15:15 / 17:45 | 15:15 / 18:02 |  |
| 2024-01-27 | AA | 1988 | DFW | ORD | 12:30 / 14:55 | 18:02 / 20:29 |  |

### N244JQ — 6 rows

| Date | Carrier | Flight | Origin | Destination | Scheduled dep / arr | Actual dep / arr | Note |
|---|---|---|---|---|---|---|---|
| 2024-01-02 | YX | 5632 | MCI | BOS | 08:25 / 12:34 | 08:21 / 12:34 |  |
| 2024-01-02 | YX | 5652 | BOS | LGA | 18:00 / 19:43 | 18:09 / 19:27 |  |
| 2024-01-03 | YX | 5792 | LGA | BOS | 07:00 / 08:24 | 06:58 / 08:06 |  |
| 2024-01-03 | YX | 5673 | BOS | ORD | 09:20 / 11:27 | 09:11 / 11:03 |  |
| 2024-01-03 | YX | 5673 | ORD | BOS | 12:55 / 16:18 | 12:50 / 16:44 |  |
| 2024-01-03 | YX | 5785 | BOS | BNA | 17:25 / 19:45 | 17:21 / 19:41 |  |

### N12003 — 6 rows

| Date | Carrier | Flight | Origin | Destination | Scheduled dep / arr | Actual dep / arr | Note |
|---|---|---|---|---|---|---|---|
| 2024-01-04 | UA | 219 | ORD | HNL | 09:45 / 15:10 | 09:53 / 14:47 |  |
| 2024-01-04 | UA | 218 | HNL | ORD | 18:15 / 06:21 (+1) | 18:11 / 06:07 (+1) |  |
| 2024-01-05 | UA | 219 | ORD | HNL | 09:45 / 15:10 | 09:43 / 14:32 |  |
| 2024-01-05 | UA | 218 | HNL | ORD | 18:15 / 06:21 (+1) | 18:04 / 05:52 (+1) |  |
| 2024-01-06 | UA | 219 | ORD | HNL | 09:45 / 15:10 | 09:57 / 14:52 |  |
| 2024-01-06 | UA | 218 | HNL | ORD | 18:15 / 06:21 (+1) | 18:51 / 07:05 (+1) |  |

### N880UA — 4 rows

| Date | Carrier | Flight | Origin | Destination | Scheduled dep / arr | Actual dep / arr | Note |
|---|---|---|---|---|---|---|---|
| 2024-01-01 | UA | 462 | ABQ | IAH | 07:30 / 10:38 | 11:55 / 15:04 |  |
| 2024-01-02 | UA | 2128 | IAH | JAX | 12:21 / 15:28 | 12:14 / 15:08 |  |
| 2024-01-02 | UA | 1710 | JAX | ORD | 16:45 / 18:23 | 16:35 / 18:12 |  |
| 2024-01-02 | UA | 1811 | ORD | CLT | 18:33 / 21:43 | 18:55 / 00:05 | Diverted; arrival date unresolved |

### N835AN — 4 rows

| Date | Carrier | Flight | Origin | Destination | Scheduled dep / arr | Actual dep / arr | Note |
|---|---|---|---|---|---|---|---|
| 2024-01-03 | AA | 1702 | DFW | ORD | 12:30 / 14:55 | 12:25 / 14:29 |  |
| 2024-01-13 | AA | 2346 | ORD | DFW | 15:15 / 17:45 | 15:10 / 17:51 |  |
| 2024-01-28 | AA | 1988 | DFW | ORD | 12:30 / 14:55 | 12:29 / 14:50 |  |
| 2024-01-30 | AA | 2346 | ORD | DFW | 15:15 / 17:45 | 15:09 / 17:26 |  |

## Manually observed ORD examples

| Tail | Inbound | Subsequent observed outbound | Interpretation |
|---|---|---|---|
| N831AA | Jan 1 AA328 DFW → ORD, actual arrival 10:57 | Jan 1 AA1109 ORD → DFW, actual departure 11:56 | Plausible same-day turn: 59 minutes on ground; 64 minutes remained to scheduled departure. |
| N244JQ | Jan 3 YX5673 BOS → ORD, actual arrival 11:03 | Jan 3 YX5673 ORD → BOS, actual departure 12:50 | Plausible same-day turn: 107 minutes on ground; 112 minutes remained to scheduled departure. Same flight number on opposite legs shows why flight number alone is not a key. |
| N12003 | Jan 4 UA218 HNL → ORD, arriving Jan 5 at 06:07 | Jan 5 UA219 ORD → HNL, actual departure 09:43 | Plausible cross-date turn: 216 minutes on ground; 218 minutes remained to scheduled departure. Outside the previously proposed 180-minute scope. |
| N880UA | Jan 2 UA1710 JAX → ORD, actual arrival 18:12 | Jan 2 UA1811 ORD → CLT, actual departure 18:55 | Same-tail departure is visible, but outbound is diverted and lacks arrival delay/elapsed time. Only 21 minutes remained to its scheduled departure. Requires separate treatment. |
| N835AN | Jan 3 AA1702 DFW → ORD, actual arrival 14:29 | Jan 13 AA2346 ORD → DFW, actual departure 15:10 | Ten-day gap: not evidence of an ordinary turnaround. Unreported movements or inactivity cannot be distinguished here. |

These are visual observations and simple time differences for named examples, not automatically accepted pairs.

## Data-quality findings and limits

- No identical rows and no duplicate candidate keys (date, carrier, flight number, origin, destination, scheduled departure) were found. This does not validate aircraft continuity.
- All 5,293 missing tails occur on canceled records. Every non-canceled record has a tail. A populated tail on a canceled flight is not evidence of an operated movement.
- There are 20,389 canceled and 1,512 diverted rows. Among non-canceled rows, 244 lack actual arrival time; 1,512 lack arrival delay and actual elapsed time. Do not fill these with zero.
- All populated clock values passed basic HHMM range checks, allowing 2400. There are 40 actual-departure and 239 actual-arrival values of 2400. Date rollover still needs explicit treatment.
- The export lacks airport timezone metadata, scheduled elapsed time, detailed diversion fields, and gate-return fields. Missing from this export does not mean unavailable from BTS. Full timestamp and exceptional-movement validation has not been done.
- Sample tails have long gaps. This single domestic reporting extract cannot establish whether missing observations represent inactivity or other movements. Do not join blindly across gaps.
- January-only coverage leaves month-boundary histories incomplete. A reported origin/destination may not describe the actual endpoint of a diversion.
- Final tail assignments and reported schedules do not establish what an analyst knew at inbound arrival. Any later replay remains conditional on realized assignments.

## Initial inspection decision

Proceed to a bounded timestamp/coverage audit before considering automated pairing. The fields and clean examples justify further investigation; this inspection does not certify reconstruction reliability, estimate pair coverage, or select a carrier for the MVP.

Verification: headline counts and carrier rankings were independently reproduced with Python csv counters after the pandas inspection. Only this notes file was created.

## Carrier reconstruction feasibility — January 2024

### Method and denominator

- Focal population: rows with DEST = ORD, CANCELLED = 0, and reporting carrier UA, AA, OO, YX, or MQ. Reported-arrival counts also show canceled records separately.
- Reconstruct actual departure as FL_DATE + CRS_DEP_TIME + signed DEP_DELAY in the origin timezone, then convert to UTC. Check its local clock against DEP_TIME. Reconstruct actual arrival using ACTUAL_ELAPSED_TIME and check against ARR_TIME at ORD. Preserve date rollover and 2400. January timezone offsets are used only for this bounded inspection.
- Diverted inbounds lack actual elapsed time in this export and are unresolved: a reported destination of ORD does not prove a completed gate arrival at ORD. No arrival date is guessed from the clock alone.
- For each resolvable inbound, choose the earliest strictly later, non-canceled, timestamp-valid observed ORD departure on the same tail. Search all carriers and the whole supplied file. No maximum gap or one-to-one constraint is imposed. These are candidates, not confirmed pairs.
- Gap is actual outbound departure minus actual inbound gate arrival. Bands are (0,15], (15,180], (180,360], and >360 minutes. Exactly 15 belongs to the first band; exactly 180 belongs to the second. This is actual ground time, not remaining time to scheduled departure.
- Percentage denominator is ALL non-canceled focal ORD arrivals, including unresolved arrivals. Candidate count counts inbounds with a match, not distinct outbound flights. No-subsequent means no eligible departure in this file, not proof that none ever occurred. Unresolved timestamps are a separate category, not no-subsequent.

### Candidate gap distribution

| Carrier | Reported ORD arrivals | Non-canceled arrivals | Candidates | (0,15] | (15,180] | (180,360] | >360 | No subsequent | Unresolved | (15,180] / non-canceled |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| UA | 6,683 | 6,159 | 5,998 | 0 | 4,324 | 257 | 1,417 | 149 | 12 | 70.21% |
| AA | 3,687 | 3,612 | 3,550 | 0 | 2,525 | 148 | 877 | 54 | 8 | 69.91% |
| OO | 4,120 | 3,643 | 3,619 | 1 | 2,937 | 189 | 492 | 19 | 5 | 80.62% |
| YX | 1,371 | 1,285 | 1,263 | 0 | 938 | 64 | 261 | 17 | 5 | 73.00% |
| MQ | 2,138 | 1,970 | 1,956 | 0 | 1,734 | 78 | 144 | 8 | 6 | 88.02% |

All five carriers have 100% nonblank tail coverage among non-canceled ORD arrivals. Including canceled arrivals, tail coverage is UA 92.22%, AA 100%, OO 100%, YX 100%, MQ 99.95%. Canceled flights with populated tails are still excluded from movement matching.

### Cancellations, diversions, and timestamps

| Carrier | Canceled inbound rows | Diverted non-canceled inbound rows | Missing inbound ARR_TIME | Missing inbound elapsed time | Canceled ORD outbound rows | Diverted ORD outbound rows | Candidate links to diverted B |
|---|---:|---:|---:|---:|---:|---:|---:|
| UA | 524 | 12 | 1 | 12 | 507 | 20 | 20 |
| AA | 75 | 8 | 0 | 8 | 74 | 14 | 14 |
| OO | 477 | 5 | 0 | 5 | 438 | 35 | 33 |
| YX | 86 | 5 | 1 | 5 | 83 | 3 | 4 |
| MQ | 168 | 6 | 0 | 6 | 157 | 11 | 11 |

All unresolved focal arrival timestamps are the diverted inbounds shown above. No other focal non-canceled arrival has missing required timing fields or a reconstructed clock mismatch. There are zero invalid/missing actual departure timestamps among non-canceled ORD departures for each of the five carriers. Missing ARR_TIME and elapsed counts overlap; do not add them.

Candidate links to diverted B count links, whereas diverted outbound rows count source flights; a reused outbound can therefore be counted more than once. Non-canceled diverted outbound departures remain observable candidates and are flagged, not silently dropped. Canceled departures are excluded even if a departure clock is present. No claim is made that an intervening cancellation represented the originally assigned flight.

### Sequence warnings and temporal contradictions

| Carrier | Candidate links skipping an observed movement | Inbounds sharing a candidate B | Other tail departure during inbound flight | Tied earliest B timestamps | Cross-carrier candidates | (15,180] candidates without listed flags |
|---|---:|---:|---:|---:|---:|---:|
| UA | 223 | 378 | 0 | 0 | 0 | 4176 |
| AA | 37 | 74 | 0 | 0 | 0 | 2490 |
| OO | 29 | 58 | 0 | 0 | 0 | 2895 |
| YX | 72 | 115 | 0 | 0 | 0 | 896 |
| MQ | 13 | 26 | 0 | 0 | 0 | 1714 |

- Skipped movement: another timestamp-valid, non-canceled flight of that tail departs anywhere after A arrives but before candidate B. This disproves immediate observed adjacency, not necessarily the accuracy of the original source record. All such cases here have gaps above 180 minutes.
- Shared B: two or more focal inbounds select the same outbound. The count includes all affected inbound links, not only extras. This is a one-step reconstruction conflict. Flags overlap and must not be summed.
- Overlap check: another same-tail departure occurs from A departure inclusive to A arrival exclusive. No such overlap was found for resolvable focal inbounds. Zero is limited to this check; it is not a certification of all aircraft histories.
- The last column excludes candidate links with a diverted B, skipped movement, shared B, overlap, tied departure, or carrier change. It is a conservative diagnostic subset, not accepted/confirmed pairs. In particular, a short turn can be flagged because an older, long-gap inbound also points to its B.
- One OO candidate is exactly 15 minutes (tail N430SW). It is a short-turn review case, not automatically an impossible movement. No positive gap below 15 minutes was found.
- Example of misleading loose matching: N337PJ arrives ORD on AA635 on January 1 at 19:59, but its next observed ORD departure is AA562 on January 4 at 16:52. Between them, the tail has observed PHX → BNA and other flights. The January 1 → January 4 link must not be interpreted as an ORD turnaround.

### Month-boundary limitations

Among no-subsequent cases, counts whose inbound FL_DATE is January 31 are UA 53, AA 34, OO 15, YX 7, MQ 4. This is a boundary indicator, not a proven explanation for every unmatched flight. Actual arrivals can roll into February. December/February files were not available to this analysis, and unreported movements remain possible throughout the month.

### Recommendation: MQ for the first MVP cohort

MQ offers a sufficient January sample (1,970 non-canceled arrivals), the highest short-turn candidate share (1,734 / 1,970 = 88.02%), complete non-canceled tail coverage, and relatively few sequence warnings (13 links skipping movements; 26 inbounds sharing a B). There are 1,714 short-turn candidates without the listed warning flags. Only 6 inbound timestamps are unresolved, all diverted records.

OO is the strongest volume alternative (2,937 short-turn candidates), but has a lower short-turn share (80.62%), more canceled inbound records proportionally, more diverted outbound records, and more shared-candidate warnings. AA has fewer cancellation complications but more long gaps and a lower short-turn share. UA maximizes volume but has substantially more skipped/shared-candidate warnings. YX has the smallest short-turn sample and a larger shared-candidate burden. This recommendation uses sample size, tail coverage, reconstructability, and data quality only; no model was fitted or evaluated.

The recommendation is provisional to this January extract. Next validation should inspect MQ warnings and month boundaries before defining final pairing acceptance. Do not use actual-gap eligibility as the eventual early-warning cohort rule without reconsidering outcome-dependent selection.

### Verification and reference

Every carrier reconciles: four gap bands + no subsequent + unresolved = non-canceled arrivals. Candidate totals equal the four bands. Earliest-departure results were independently checked by filtering each tail to later departures and taking the minimum timestamp. No source values were changed; only this notes file was updated. Analysis ran in memory and no reusable pipeline or pairing implementation was saved.

Timezone reference: [OpenFlights airport data](https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports.dat), fetched September 15, 2026, SHA-256 9387cdb38df5bd664da823f8ccb69fdd9b33a1888f5b7cca09c34a3cd9ff59f9. Missing codes BIH and XWA were supplemented with America/Los_Angeles and America/Chicago respectively, consistent with [BIH standard-time information](https://www.airnav.com/airport/KBIH) and [XWA standard-time information](https://www.airnav.com/airport/XWA). All source origin codes were covered after supplementation. This current reference is not a historical airport-metadata snapshot; checked focal clocks reconcile for January.

## MQ immediate-next-movement audit — three-month context

### Scope and acceptance rules

January 2024 MQ non-canceled records with reported destination ORD are focal. December 2023 and February 2024 are context only. Counts are by inbound FL_DATE/source month, including flights whose actual arrival rolls to February. All three files were read without modification.

The analysis retains all carriers for every tail appearing on MQ records. It orders non-canceled movements by reconstructed actual departure UTC, and examines the immediate successor without skipping any observed operated movement. Acceptance requires MQ on both legs, matching tail, A destination ORD, B origin ORD, positive actual ground gap, nondiverted legs, valid timestamps, no interval overlaps or ties, and unique B use.

Cancelled rows are not operated movements. A same-tail cancelled record with scheduled departure between A arrival and B departure causes conservative exclusion, regardless of its origin. Its tail assignment is not interpreted as an actual movement. An unresolved preceding movement also causes conservative exclusion because its arrival cannot be checked against A departure. An operated record with unresolved departure would make the entire tail ambiguous; none occurred here.

Timestamp method: scheduled departure date/clock plus signed DEP_DELAY determines actual departure, converted from origin local time to UTC. ACTUAL_ELAPSED_TIME determines arrival. Both reported actual clocks must agree modulo midnight. 2400 is preserved as next-day midnight. January standard-time offsets also apply to this December–February US dataset. No schedule-only sort is used. Missing diverted-leg elapsed times are not guessed.

High-confidence observed turnaround pairs means internally consistent immediate observed adjacency under these rules. It does not establish uninterrupted physical presence at ORD, a complete movement history, or confirmed real-time aircraft assignments. Long gaps can conceal unreported movements. Gate-return detail and historical assignment snapshots are absent.

### Results

| Measure | Count |
|---|---:|
| January MQ non-canceled ORD arrivals | 1,970 |
| With immediate next observed operated movement | 1,970 |
| High-confidence observed turnaround pairs | 1,872 |
| Rejected | 98 |
| Current (15,180]-minute short-turn cohort | 1,693 |

| Accepted actual ground gap | Count |
|---|---:|
| (0,15] minutes | 0 |
| (15,180] minutes | 1,693 |
| (180,360] minutes | 70 |
| >360 minutes | 109 |

Gap is actual gate departure B minus actual gate arrival A. The bands include the upper endpoint; exactly 15 is outside the current short-turn cohort. Gap-based filtering was not used to accept pairs. Remaining time is scheduled B departure minus actual A arrival, so it can be negative. Outbound delay and its >=15-minute label come from B DEP_DELAY.

### Rejections and flags

Primary reasons are mutually exclusive, assigned in the rule order in the audit script. Warning counts overlap and must not be added.

| Primary rejection reason | Count |
|---|---:|
| cancelled_record_during_ground_interval | 54 |
| next_origin_not_ORD | 18 |
| diverted_outbound | 11 |
| unresolved_preceding_movement | 9 |
| diverted_inbound | 6 |

| Warning / condition | Affected focal inbounds |
|---|---:|
| missing_tail | 0 |
| diverted_inbound | 6 |
| unresolved_inbound_timestamp | 6 |
| next_origin_not_ORD | 19 |
| next_carrier_not_MQ | 0 |
| diverted_outbound | 12 |
| unresolved_outbound_timestamp | 12 |
| unresolved_preceding_movement | 9 |
| cancelled_record_during_ground_interval | 56 |
| unresolved_cancelled_record | 0 |
| unknown_order_on_tail | 0 |
| duplicate_flight_key | 0 |
| tied_departure_sequence | 0 |
| overlapping_movement | 0 |
| outbound_not_after_arrival | 0 |
| duplicate_outbound_use | 0 |
| no_next_observed_movement | 0 |
| month_boundary_uncertainty | 0 |

All focal non-canceled arrivals have tails. Six diverted inbounds have unresolved arrival timestamps. Twelve successor legs are diverted and have unresolved arrival timestamps; these warning counts overlap other reasons. No clock mismatches, unknown departure order, tied departures, known interval overlaps, or duplicate B use were found in the retained MQ-tail context. Missing unreported movements cannot be ruled out by these checks.

Cancelled January MQ destination-ORD rows are excluded before the focal denominator: 168. The cancellation-during-ground exclusion is deliberately conservative and is not proof that a cancelled flight was physically assigned to that aircraft.

### Boundary recovery

- February supplies immediate successors for 4 January inbounds. 3 are accepted; none belong to the short-turn cohort. Thus accepted pairs increase from 1,869 to 1,872 when these February successors are available.
- December supplies the predecessor context for 27 focal inbounds; all 27 pass. These are strengthened predecessor checks, not newly recovered January A → B pairs.
- No focal arrival is left without a successor in the three-month file. This removes observed search-edge uncertainty for these inbounds, not the wider incomplete-coverage limitation.

| Inbound ID | Tail | February successor ID | Gap min | Result |
|---|---|---|---:|---|
| 2024-01_reporting.csv:537739 | N218NN | 2024-02_reporting.csv:8104 | 872 | accepted |
| 2024-01_reporting.csv:538036 | N280NN | 2024-02_reporting.csv:8438 | 1215 | accepted |
| 2024-01_reporting.csv:538185 | N761RW | 2024-02_reporting.csv:149356 | 12378 | next_origin_not_ORD |
| 2024-01_reporting.csv:538246 | N776MS | 2024-02_reporting.csv:8657 | 836 | accepted |

The rejected boundary example N761RW arrives ORD on January 31, but the immediate next observed movement starts at MQT on February 9. Searching onward for an ORD departure would conceal this discontinuity and is not allowed.

### 20 accepted examples

Purposeful coverage sample: 15 short turns spread through January, two medium-gap turns, and all three accepted February successors. It is not a random or representative evaluation sample. Full source IDs and all fields are in outputs/phase0_mq_observed_pairs.csv. All timestamps below are UTC; dates are explicit.

| Tail | A flight / origin | B flight / destination | A arrival UTC | B departure UTC | Gap min | B scheduled UTC | Remaining min | B delay min | Delay >=15 |
|---|---|---|---|---|---:|---|---:|---:|---|
| N283NN | 3710 / GSP | 3703 / BOS | 2024-01-01 13:11 | 2024-01-01 13:46 | 35 | 2024-01-01 13:25 | 14 | 21 | True |
| N764JD | 3769 / ATL | 3748 / CID | 2024-01-03 02:24 | 2024-01-03 03:05 | 41 | 2024-01-03 02:30 | 6 | 35 | True |
| N776MS | 3790 / EYW | 3830 / GRB | 2024-01-05 00:48 | 2024-01-05 01:28 | 40 | 2024-01-05 00:53 | 5 | 35 | True |
| N874RW | 4129 / SGF | 3792 / OKC | 2024-01-07 13:53 | 2024-01-07 14:31 | 38 | 2024-01-07 14:36 | 43 | -5 | False |
| N240NN | 3392 / EWR | 3793 / FSD | 2024-01-09 15:24 | 2024-01-09 16:09 | 45 | 2024-01-09 16:10 | 46 | -1 | False |
| N205NN | 3680 / MSY | 3741 / SDF | 2024-01-11 20:01 | 2024-01-11 21:21 | 80 | 2024-01-11 21:28 | 87 | -7 | False |
| N770JM | 3369 / MCI | 3679 / BWI | 2024-01-15 13:56 | 2024-01-15 14:59 | 63 | 2024-01-15 14:35 | 39 | 24 | True |
| N287NN | 3932 / IND | 4084 / IAH | 2024-01-17 18:03 | 2024-01-17 19:14 | 71 | 2024-01-17 19:15 | 72 | -1 | False |
| N874RW | 3744 / COU | 3514 / FAR | 2024-01-19 15:11 | 2024-01-19 15:54 | 43 | 2024-01-19 15:50 | 39 | 4 | False |
| N762DT | 3782 / DSM | 3922 / BHM | 2024-01-21 15:00 | 2024-01-21 15:51 | 51 | 2024-01-21 15:50 | 50 | 1 | False |
| N783LC | 3812 / HPN | 3320 / SGF | 2024-01-23 20:13 | 2024-01-23 22:21 | 128 | 2024-01-23 21:43 | 90 | 38 | True |
| N208AN | 4088 / XNA | 3680 / MSY | 2024-01-26 13:09 | 2024-01-26 14:25 | 76 | 2024-01-26 14:30 | 81 | -5 | False |
| N451YX | 4088 / XNA | 3877 / ELP | 2024-01-28 13:16 | 2024-01-28 14:16 | 60 | 2024-01-28 14:19 | 63 | -3 | False |
| N826MD | 3760 / DSM | 3945 / MEM | 2024-01-29 23:15 | 2024-01-30 00:16 | 61 | 2024-01-30 00:20 | 65 | -4 | False |
| N779RN | 3790 / EYW | 4007 / ROC | 2024-02-01 00:05 | 2024-02-01 00:52 | 47 | 2024-02-01 00:53 | 48 | -1 | False |
| N258NN | 3673 / GSO | 3581 / XNA | 2024-01-01 14:27 | 2024-01-01 19:14 | 287 | 2024-01-01 19:15 | 288 | -1 | False |
| N771JV | 3845 / RDU | 3323 / EWR | 2024-01-31 20:40 | 2024-02-01 02:18 | 338 | 2024-02-01 02:20 | 340 | -2 | False |
| N218NN | 3808 / HPN | 3680 / MSY | 2024-01-31 23:54 | 2024-02-01 14:26 | 872 | 2024-02-01 14:30 | 876 | -4 | False |
| N280NN | 4084 / IAH | 3375 / XNA | 2024-02-01 01:21 | 2024-02-01 21:36 | 1215 | 2024-02-01 21:22 | 1201 | 14 | False |
| N776MS | 3862 / MSP | 3789 / EWR | 2024-02-01 00:32 | 2024-02-01 14:28 | 836 | 2024-02-01 14:30 | 838 | -2 | False |

### 10 rejected / edge-case examples

Eight rejected examples cover the primary reasons and additional cases; two accepted edge cases expose limits of the modeling cohort.

| Inbound ID | Tail | A route / B route | Gap min | Result / reason |
|---|---|---|---:|---|
| 2024-01_reporting.csv:25556 | N215NN | CMI→ORD / DFW→HSV | 1102 | next_origin_not_ORD |
| 2024-01_reporting.csv:116085 | N215NN | EWR→ORD / ORD→SDF | 634 | unresolved_preceding_movement |
| 2024-01_reporting.csv:134733 | N215NN | SDF→ORD / ORD→IAH | 63 | diverted_outbound;unresolved_outbound_timestamp |
| 2024-01_reporting.csv:135319 | N821MD | ICT→ORD / ORD→ICT | 352 | cancelled_record_during_ground_interval |
| 2024-01_reporting.csv:205767 | N282NN | XNA→ORD / TLH→DCA | unresolved | diverted_inbound;unresolved_inbound_timestamp;next_origin_not_ORD |
| 2024-01_reporting.csv:26101 | N769KW | EWR→ORD / BUF→ORD | 705 | next_origin_not_ORD |
| 2024-01_reporting.csv:44816 | N760MQ | PVD→ORD / XNA→ORD | 5511 | next_origin_not_ORD |
| 2024-01_reporting.csv:62704 | N264NN | CVG→ORD / TUL→DFW | 237 | next_origin_not_ORD |
| 2024-01_reporting.csv:328409 | N768RD | SGF→ORD / ORD→XNA | 7982 | accepted: very long observed gap; unreported movement risk |
| 2024-01_reporting.csv:257662 | N761RW | MEM→ORD / ORD→LIT | 40 | accepted: already late at inbound arrival; not early warning |

### GO / NO-GO

**GO to modeling design on MQ: observed reconstruction is feasible. NO-GO to training on the actual-ground-gap cohort as if it were selected at arrival.** The 1,693 short turns establish sample availability, but actual ground gap includes the future departure event and selecting on it can bias the target distribution.

Before fitting a baseline, freeze an arrival-time eligibility rule using remaining time to scheduled departure and evaluate the full supported observed-pair population. For illustration, 1,486 accepted pairs have 15–180 minutes remaining at arrival, regardless of eventual actual gap. This is a diagnostic, not a finalized model cohort.

101 accepted pairs are already at least 15 minutes beyond scheduled departure at inbound arrival; 140 actual-short-turn pairs are already past scheduled departure. These should not be presented as successful early warnings. Gate-return limitations and retrospective aircraft assignment remain explicit. No model was trained.

### Reproducibility and verification

- Run work/phase0_mq_pair_audit.py with Python, pandas, and numpy. It reads only the three raw files plus the saved timezone reference and refreshes the two output CSVs and this marked notes section.
- Source row IDs include the filename and 1-based CSV line number (header is line 1). They are audit locators for these immutable files, not proposed production flight IDs.
- Assertions verify 1,970 focal rows, exact accepted/rejected reconciliation, unique outbound use, same-tail ORD continuity, positive gap, and no observed operated departure between accepted A and B.
- SHA-256 hashes before and after the run verify that raw files are unchanged.

| Raw file | SHA-256 |
|---|---|
| 2023-12_reporting.csv | d208162200885e73a47f868666fafbabbe35a23182e79a8210a468ef0a246e5d |
| 2024-01_reporting.csv | 75a2e0b58658956444c3e7cd7e7137cfb0232bd98e9def99df096004feb609d2 |
| 2024-02_reporting.csv | 40f560c4f83add1c23e4e492a8312274608e4523e41e5f18007b2778750a2e5d |

Timezone reference: [OpenFlights](https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports.dat), with BIH and XWA supplements from [BIH](https://www.airnav.com/airport/KBIH) and [XWA](https://www.airnav.com/airport/XWA). Saved in work/airport_timezones_reference.csv; SHA-256 08c7d1fadf0f961201d5028ef26e45d2a55cfb719d60b811d1aee383d6b3d6d2. All required origins were covered. This reference is not a historical assignment or schedule snapshot.

# Rule-Based Evaluation Report

## Purpose
Track the current health/metrics rule logic, anomaly detection signals, and validation status in one place.

This document is intended to be updated whenever thresholds, scoring weights, or anomaly rules change.

## Source of Truth
- `backend/app/api/health.py`
- `backend/app/api/metrics.py`
- `backend/tests/unit/test_health_api.py`
- `backend/tests/unit/test_metrics_api.py`

## Current Rule Set

### 1. Availability Scoring (`health.py`)
- `Down` => `0`
- `Up` + no `http_status` => `85`
- `Up` + HTTP `2xx-3xx` => `100`
- `Up` + HTTP `4xx` => `70`
- `Up` + HTTP `5xx` => `30`

### 2. Latency Scoring + Label (`health.py`)
- `<= 200ms` => score `100`, label `Fast`
- `<= 500ms` => score `90`, label `Fast`
- `<= 1000ms` => score `75`, label `Moderate`
- `<= 2000ms` => score `55`, label `Slow`
- `<= 5000ms` => score `25`, label `Slow`
- `> 5000ms` => score `5`, label `Critical`
- missing latency => score `10`, label `Unknown`

### 3. Reliability Scoring + Label (`health.py`)
Based on latest 10 checks + current check:
- uptime `>= 99%` => score `100`, label `Stable`
- uptime `>= 95%` => score `85`, label `Mostly Stable`
- uptime `>= 90%` => score `65`, label `Flaky`
- uptime `< 90%` => score `35`, label `Unstable`

### 4. Metrics Risk Evaluation (`health.py` + `metrics.py`)
Penalty model starts at `100`, subtracts:
- p90 latency:
  - `> 500ms` => `-8`
  - `> 1000ms` => `-15`
  - `> 2000ms` => `-25`
- p99 latency:
  - `> 1500ms` => `-10`
  - `> 3000ms` => `-20`
- error rate:
  - `> 2%` => `-10`
  - `> 5%` => `-25`
  - `> 10%` => `-40`
- CPU (only when unit is `%` or `percent`):
  - `> 80%` => `-10`
  - `> 90%` => `-20`

Metric score floor: `0`.

### 5. Overall Score Composition (`health.py`)
- If service is `Down` => overall score `0`
- If no metrics score is available:
  - `availability * 0.45 + latency * 0.30 + reliability * 0.25`
- If metrics score is available:
  - `availability * 0.35 + latency * 0.25 + reliability * 0.20 + metrics * 0.20`

### 6. Metrics Scrape Evaluation Status (`metrics.py`)
- score `>= 85` => `Healthy`
- score `>= 70` and `< 85` => `Degraded`
- score `< 70` => `Critical`

## Anomaly/Event Detection Rules

### Health Check Path (`POST /api/health/services/{id}/check`)
- If `availability == Down` => event level `ERROR`
- Else if `latency_ms > 2000` => event level `WARNING` ("High latency detected")
- Else if `overall_score < 70` => event level `WARNING` ("Service health degraded ...")

### Metrics Scrape Path (`POST /api/metrics/services/{id}/scrape`)
- If metrics evaluation status is `Degraded` or `Critical` => event level `WARNING`
- If scrape fails => event level `WARNING` ("Metrics scrape failed ...")

## DB Constraint Compatibility Checklist
Ensure schema accepts current inserted values:

### `service_health.availability`
- `Up`, `Down`

### `service_health.responsiveness`
- `Fast`, `Moderate`, `Slow`, `Critical`, `Unknown`

### `service_health.reliability`
- `Stable`, `Mostly Stable`, `Flaky`, `Unstable`

### `service_events.event_level`
- `INFO`, `WARNING`, `ERROR`

## Testing Matrix (Manual/Automated)

### Health Rules
- [ ] Up + HTTP 200 + low latency => high score, no anomaly event
- [ ] Up + HTTP 404 => availability score reduced
- [ ] Timeout => `Down`, responsiveness `Critical`, overall `0`
- [ ] Degraded reliability trend (<90% uptime) lowers score
- [ ] Metrics penalties reduce overall score when metrics exist
- [ ] `overall_score < 70` triggers degraded warning event

### Metrics Rules
- [ ] p90 > 2000ms penalizes score
- [ ] p99 > 3000ms penalizes score
- [ ] error_rate > 10% strongly penalizes score
- [ ] CPU > 90% (percent unit) penalizes score
- [ ] score bucket maps to Healthy/Degraded/Critical correctly
- [ ] Degraded/Critical scrape emits warning event

## Report Log Template

### Evaluation Run
- Date:
- Branch/Commit:
- Evaluator:
- Environment:

### Results Summary
- Health rule checks: `PASS/FAIL`
- Metrics rule checks: `PASS/FAIL`
- Anomaly event checks: `PASS/FAIL`
- DB constraint compatibility: `PASS/FAIL`

### Findings
1. 
2. 
3. 

### Actions
1. 
2. 
3. 

---

## Change Log
- YYYY-MM-DD: Initial report created.

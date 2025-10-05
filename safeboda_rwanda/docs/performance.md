# Performance Report

## Setup
- MacBook Pro M-series, Python 3.13, Django 5, DRF
- LocMem cache; SQLite (dev); DEBUG=False
- Load test with `locust` (100 users, spawn rate 10/s) for 2 minutes

## Async vs Sync (Locations)
| Scenario | P50 (ms) | P95 (ms) | RPS | Error% |
|---------|---------:|---------:|----:|------:|
| **Sync** nearby drivers (no cache) | 120 | 280 | 85 | 0 |
| **Async** nearby + external map (mock) | 70 | 160 | 140 | 0 |
| **Async + Cache HIT** | 18 | 30 | 400 | 0 |

**Observation:** async cut P50 by ~40%. With cache hits, sub-20ms typical.

## Caching Impact
- Hit ratio after warmup: **0.82**
- Requests served from cache: 1,230 / 1,500
- Estimated data saved (mobile): ~65% fewer payload bytes for repeated routes.

## Mobile Data Optimization
- Pagination defaults: `limit=10`
- Slim JSON fields for nearby/ride lists
- Cache-Control headers allow client caching for 5m

## Methodology
- 3 runs each; discarded cold start
- Same dataset; identical query mix
<div align="center">

# Clinker-to-Cement Mix Proportioning Optimizer

**Lowest-cost blend of clinker, gypsum and additions that still meets target
composition** (C3S, C3A, SO₃, LOI, addition caps per EN 197-1 / ASTM C150)

[![Web UI](https://img.shields.io/badge/web%20UI-standalone-f59e0b)](#)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](#)
[![No deps](https://img.shields.io/badge/dependencies-none-blue)](#)
[![Tests](https://img.shields.io/badge/tests-3%20passing-green)](#)
[![License](https://img.shields.io/badge/license-MIT-green)](#)

</div>

---

## Why this exists

Every tonne of clinker you replace with a cheaper addition saves real money —
but over-do it and SO₃ drifts out of the setting-control window or fineness
slides. Finish-mill blending is a daily cost decision, and this tool makes the
trade-off explicit: find the cheapest blend that still passes every quality
gate.

## How it works

Each ingredient carries a composition (major phase / oxide %) and a cost per
tonne. The optimizer varies the blend fractions to minimise cost while holding
quality inside the target windows:

```
minimise   cost = Σ (x_i x price_i)
subject to Σ x_i = 1               (a whole tonne)
           0 ≤ x_i ≤ cap_i         (addition limits)
           C3S_min ≤ C3S ≤ C3S_max
           C3A_min ≤ C3A ≤ C3A_max
           SO3_min ≤ SO3 ≤ SO3_max
           LOI ≤ LOI_max
```

Clinker phases are tracked from oxide chemistry (Bogue-derived inputs), so the
same data drives both quality and cost. The engine uses a fast, dependency-free
coordinate-descent local search with restarts.

## Features

- Editable ingredient table (cost, chemistry, addition cap)
- Editable quality targets (C3S, C3A, SO₃ low/high, LOI)
- Live blend bar + cost-per-tonne result in the UI
- `optimiser.py` CLI that runs the bundled example instantly
- Unit-tested core (`test_optimiser.py`, 3 passing)

## Quick start

```bash
# web UI
open index.html            # or: python3 -m http.server 8000

# CLI
python3 optimiser.py
# -> Optimal blend @ 55.63 USD/t
#    Clinker 89.0%  Gypsum 5.5%  Limestone 5.0%  Fly ash 0.5%

# tests
python3 -m unittest test_optimiser -v
```

## Bundled example

| Ingredient | Cost (USD/t) | C3S % | C3A % | SO3 % | cap % |
|-----------|-------------|-------|-------|-------|-------|
| Clinker    | 60  | 62 | 8 | 0.8 | 100 |
| Gypsum     | 28  | 0  | 0 | 46 | 6   |
| Limestone  | 12  | 0  | 0 | 0  | 5   |
| Fly ash    | 18  | 0  | 0 | 1  | 25  |
| Slag       | 22  | 0  | 0 | 1.8| 30  |

Targets: C3S ≥ 55%, C3A ≤ 9%, SO₃ in 2.0–3.5%, LOI ≤ 5%. The optimizer
lowers cost from 60 USD/t (100% clinker) to ~55.6 USD/t while staying inside
every window.

## License

MIT.

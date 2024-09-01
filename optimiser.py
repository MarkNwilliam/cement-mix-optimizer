#!/usr/bin/env python3
"""Clinker-to-cement mix proportioning optimizer.

Finds a low-cost blend of clinker, gypsum and additions that meets target
composition (C3S, C3A, SO3, LOI) and addition caps. Uses a greedy + local
refinement so it runs instantly with no external dependencies.
"""

INGREDIENTS = {
    "Clinker":   {"cost": 60, "C3S": 62, "C3A": 8.0, "SO3": 0.8, "LOI": 0.5, "cap": 1.00},
    "Gypsum":    {"cost": 28, "C3S": 0,  "C3A": 0.0, "SO3": 46,  "LOI": 18,  "cap": 0.06},
    "Limestone": {"cost": 12, "C3S": 0,  "C3A": 0.0, "SO3": 0.0, "LOI": 43,  "cap": 0.05},
    "Fly ash":   {"cost": 18, "C3S": 0,  "C3A": 0.0, "SO3": 1.0, "LOI": 4,   "cap": 0.25},
    "Slag":      {"cost": 22, "C3S": 0,  "C3A": 0.0, "SO3": 1.8, "LOI": 1.0, "cap": 0.30},
}

TARGETS = {
    "C3S_min": 55.0, "C3A_max": 9.0,
    "SO3_min": 2.0,  "SO3_max": 3.5,
    "LOI_max": 5.0,
}


def blend_quality(frac):
    C3S = sum(INGREDIENTS[k]["C3S"] * f for k, f in frac.items())
    C3A = sum(INGREDIENTS[k]["C3A"] * f for k, f in frac.items())
    SO3 = sum(INGREDIENTS[k]["SO3"] * f for k, f in frac.items())
    LOI = sum(INGREDIENTS[k]["LOI"] * f for k, f in frac.items())
    cost = sum(INGREDIENTS[k]["cost"] * f for k, f in frac.items())
    return C3S, C3A, SO3, LOI, cost


def feasible(frac):
    if abs(sum(frac.values()) - 1.0) > 1e-6:
        return False
    for k, f in frac.items():
        if not (0 <= f <= INGREDIENTS[k]["cap"] + 1e-9):
            return False
    C3S, C3A, SO3, LOI, _ = blend_quality(frac)
    return (C3S >= TARGETS["C3S_min"] and C3A <= TARGETS["C3A_max"] and
            TARGETS["SO3_min"] <= SO3 <= TARGETS["SO3_max"] and
            LOI <= TARGETS["LOI_max"])


def optimise(iterations=4000):
    """Coordinate-descent local search with restarts. Fast and deterministic."""
    keys = [k for k in INGREDIENTS if k != "Clinker"]
    best = None

    def try_from(seed):
        frac = dict(seed)
        cur = dict(frac)
        # coordinate descent until no single tweak helps
        improved = True
        steps = 0
        while improved and steps < iterations:
            improved = False
            steps += 1
            for k in keys:
                # try nudging this ingredient up, then down
                for delta in (0.005, -0.005):
                    nxt = dict(cur)
                    nxt[k] = cur.get(k, 0) + delta
                    if nxt[k] < 0 or nxt[k] > INGREDIENTS[k]["cap"] + 1e-9:
                        continue
                    clinker = 1.0 - sum(nxt[k2] for k2 in nxt if k2 != "Clinker")
                    if clinker < -1e-9:
                        continue
                    nxt["Clinker"] = clinker
                    if not feasible(nxt):
                        continue
                    _, _, _, _, c1 = blend_quality(cur)
                    _, _, _, _, c2 = blend_quality(nxt)
                    if c2 < c1 - 1e-9:
                        cur = nxt
                        improved = True
                        break
            if not improved:
                break
        if feasible(cur):
            _, _, _, _, c = blend_quality(cur)
            if best is None or c < best[0]:
                return (c, cur)
        return None

    # restart from a few sensible starting points
    seeds = [
        {"Clinker": 1.0},
        {"Clinker": 0.90, "Gypsum": 0.05, "Limestone": 0.05},
        {"Clinker": 0.80, "Gypsum": 0.05, "Fly ash": 0.15},
        {"Clinker": 0.78, "Gypsum": 0.05, "Slag": 0.17},
    ]
    for s in seeds:
        r = try_from(s)
        if r:
            best = r
    return best


def main():
    best = optimise()
    if best is None:
        print("No feasible blend found within the caps and targets.")
        return
    cost, frac = best
    C3S, C3A, SO3, LOI, c = blend_quality(frac)
    print(f"Optimal blend @ {c:,.2f} USD/t")
    for k, f in sorted(frac.items(), key=lambda x: -x[1]):
        if f > 1e-6:
            print(f"  {k:10s} {f*100:6.1f} %")
    print(f"  C3S {C3S:.1f}%  C3A {C3A:.2f}%  SO3 {SO3:.2f}%  LOI {LOI:.2f}%")


if __name__ == "__main__":
    main()

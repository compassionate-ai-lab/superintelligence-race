"""M4. Robust compute allocation under disruption (Chapters 8, 11, 12, 14, 15, 19).

x_i  essential workload placed with provider/location i (service units)
K_i  capacity;  a_is usable fraction of i in disruption scenario s
D_s  essential demand in scenario s
U_s(x) = max(0, D_s - sum_i a_is x_i)  (unmet essential demand, fixed allocation)
Robust problem: min_x C(x) + eta * max_s U_s(x),  0 <= x_i <= K_i,
with life-critical floors imposed as constraints, not priced.
In the book's worked example capacity is contracted in blocks of 10 units, so each x_i is a
multiple of 10; `solve` searches that grid exhaustively (small, transparent example).
`continuous_optimum` solves the same problem with x_i allowed to take any value (exact
linear programme, by vertex enumeration in rational arithmetic), for comparison.
"""
import itertools
from fractions import Fraction


def unmet(x, a_s, D):
    return max(0.0, D - sum(ai * xi for ai, xi in zip(a_s, x)))


def solve(costs, caps, avail, D, eta, step=10, floor=None):
    best = None
    grids = [range(0, int(k) + 1, step) for k in caps]
    for x in itertools.product(*grids):
        worst = max(unmet(x, a_s, D) for a_s in avail)
        if floor is not None and worst > floor:
            continue
        val = sum(c * xi for c, xi in zip(costs, x)) + eta * worst
        if best is None or val < best[0]:
            best = (val, x, worst)
    return best


def _det3(m):
    return (m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
            - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
            + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]))


def continuous_optimum(costs, caps, avail, D):
    """Cheapest allocation with zero shortfall in every scenario, x_i continuous (3 options).
    Constraints a_s . x >= D for each scenario and 0 <= x_i <= K_i, all as rows g . x >= h."""
    F = Fraction
    rows = [([F(str(a)) for a in a_s], F(str(D))) for a_s in avail]
    for i in range(3):
        e = [F(0)] * 3; e[i] = F(1); rows.append((e, F(0)))
        e = [F(0)] * 3; e[i] = F(-1); rows.append((e, -F(str(caps[i]))))
    best = None
    for (g1, h1), (g2, h2), (g3, h3) in itertools.combinations(rows, 3):
        M = [g1, g2, g3]
        d = _det3(M)
        if d == 0:
            continue
        x = []
        for j in range(3):
            Mj = [list(r) for r in M]
            for r, h in zip(Mj, (h1, h2, h3)):
                r[j] = h
            x.append(_det3(Mj) / d)
        if all(sum(gi * xi for gi, xi in zip(g, x)) >= h for g, h in rows):
            c = sum(F(ci) * xi for ci, xi in zip([F(str(c)) for c in costs], x))
            if best is None or c < best[0]:
                best = (c, tuple(x))
    return best


def worked_example():
    # three options: foreign hyperscaler (cheap), regional pool (medium), sovereign (dear)
    costs = [1.0, 1.6, 2.5]            # cost units per MW-equivalent of essential service
    caps = [200, 120, 100]
    avail = [[1, 1, 1],                # normal
             [0, 1, 1],                # foreign access withdrawn
             [1, 0.5, 1],              # regional link cut
             [0.6, 0.6, 0.6],          # shared grid stress affects all
             [0, 0, 1]]                # conflict: foreign and regional both cut
    D = 100                            # essential demand, MW-equivalent
    cheapest = solve(costs, caps, avail[:1], D, eta=0, floor=0)
    without_conflict = solve(costs, caps, avail[:4], D, eta=0, floor=0)
    floor0 = solve(costs, caps, avail, D, eta=0, floor=0)
    cont4 = continuous_optimum(costs, caps, avail[:4], D)
    cont5 = continuous_optimum(costs, caps, avail, D)
    return {"cheapest_normal_only": cheapest,
            "zero_shortfall_without_conflict_scenario": without_conflict,
            "zero_shortfall_all_scenarios": floor0,
            "continuous_without_conflict": [float(cont4[0]), [float(v) for v in cont4[1]]],
            "continuous_all_scenarios": [float(cont5[0]), [float(v) for v in cont5[1]]]}

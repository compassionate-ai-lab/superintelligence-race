"""M2. Intervention margin for improving systems (Chapters 3, 6, 10, 13).

D0  current distance to an operational boundary (e.g. points on a held-out
    evaluation below a tripwire threshold)
m   required reserve, same unit
v   upper bound on the rate at which the distance can close (unit per day)
tau total intervention time: detection + authorization + effective action (days)

Constant-rate bound:     D0 - v*tau >= m   =>  tau <= (D0 - m) / v
Accelerating bound:      rate v(t) = v0 * exp(g t)
                          distance closed by tau = v0/g * (exp(g tau) - 1)
                          =>  tau <= ln(1 + g (D0 - m) / v0) / g
"""
import math


def max_tau_constant(D0, m, v):
    if D0 < m:
        return 0.0                       # reserve already breached
    if v <= 0:
        return math.inf
    return (D0 - m) / v


def max_tau_accelerating(D0, m, v0, g):
    if D0 < m:
        return 0.0
    if g == 0:
        return max_tau_constant(D0, m, v0)
    return math.log(1 + g * (D0 - m) / v0) / g


def budget_per_review(D0, m):
    """Largest cumulative capability gain that may be permitted between reviews."""
    return max(0.0, D0 - m)


def delayed_correction_stable(a, b, d, steps=4000):
    """Discrete check: x[t+1] = (1+a) x[t] - b x[t-d].
    a: per-cycle self-amplification of a deviation; b: corrective gain applied
    with a delay of d cycles. Returns True if a unit deviation decays."""
    x = [0.0] * (d + 1) + [1.0]
    for _ in range(steps):
        x.append((1 + a) * x[-1] - b * x[-1 - d])
        if abs(x[-1]) > 1e6:
            return False
    return abs(x[-1]) < 1e-3


def worked_example():
    D0, m = 18.0, 5.0            # points below the tripwire; reserve
    v = (1.0 * 1.5) / 2          # largest observed gain 1.0/cycle x safety factor 1.5, 2-day cycles
    g = math.log(2) / 30         # rate doubles every 30 days
    return {
        "tau_constant_days": max_tau_constant(D0, m, v),
        "tau_accelerating_days": max_tau_accelerating(D0, m, v, g),
        "budget_points": budget_per_review(D0, m),
        "stable_no_delay": delayed_correction_stable(0.05, 0.5, 0),
        "stable_delay_3": delayed_correction_stable(0.05, 0.5, 3),
        "stable_delay_3_gentler": delayed_correction_stable(0.05, 0.15, 3),
    }

"""Worked calculations in Chapters 2, 4, 5, 7-12, 14-19 and 21 that are not part of M1-M6.
All inputs are illustrative unless a chapter cites a source for them."""
import math


def ch02_verification_adjusted(s, v, r):
    """Expected human time per task with AI, relative to 1.0 without AI.
    s: AI success rate; v: verification time; r: extra rework after a failure."""
    return v + (1 - s) * (1 + r)


def ch02_threshold(v, r):
    return (v + r) / (1 + r)


def ch04_growth(power=1.15, efficiency=1.40, chips=1.80, algorithmic_halving_months=8):
    physical = min(chips, power * efficiency)
    algo = 2 ** (12 / algorithmic_halving_months)
    return dict(physical=physical, algorithmic=algo, effective=physical * algo)


def ch05_harm(p, h, extra):
    """Expected cost per consignment: error probability x harm + other per-unit costs."""
    return p * h + extra


def ch07_delay_cost(deaths_before=17, deaths_after=3, years=2, effect_fraction=1.0):
    return (deaths_before - deaths_after) * years * effect_fraction


def ch08_rebound(k, elasticity):
    """Total resource use multiplies by k**(elasticity - 1) when cost per task falls by factor k."""
    return k ** (elasticity - 1)


def ch10_two_proportion_z(x1, n1, x2, n2):
    """Pooled two-proportion z statistic for two independent samples (not for matched pairs)."""
    p1, p2 = x1 / n1, x2 / n2
    p = (x1 + x2) / (n1 + n2)
    se = math.sqrt(p * (1 - p) * (1 / n1 + 1 / n2))
    return (p1 - p2) / se


def ch10_rule_of_three(n):
    """Approximate 95% upper bound on an event rate after n trials with no events."""
    return 3 / n


def ch11_leontief(compute, talent, institutions):
    return min(compute, talent, institutions)


def ch14_detection(ps):
    q = 1.0
    for p in ps:
        q *= 1 - p
    return 1 - q


def ch15_amdahl(a, k):
    """Upper bound on output gain when a share a of tasks becomes k times cheaper and the rest is unchanged
    (strict complements)."""
    return 1 / ((1 - a) + a / k)


def ch15_bottleneck_share(a, k):
    return (1 - a) / ((1 - a) + a / k)


CH16_LOSS = {"narrow tool specialist": [2, 6, 9], "domain + evaluation": [0, 3, 6],
             "anchored accountable role": [3, 2, 3], "domain + evaluation + anchored": [1, 1, 4]}


def ch16_regret():
    best = [min(c) for c in zip(*CH16_LOSS.values())]
    reg = {a: [x - b for x, b in zip(v, best)] for a, v in CH16_LOSS.items()}
    return reg, min(reg, key=lambda a: max(reg[a]))


def ch17_reach(coverage, adequacy):
    return coverage * adequacy


def ch19_capacity(evaluators=40, per_evaluator=6, rho=0.8, full_share=0.15, systems=600, light_cost=0.1):
    capacity = evaluators * per_evaluator * rho
    demand_all_full = systems
    demand_tiered = systems * full_share + systems * (1 - full_share) * light_cost
    return dict(capacity=capacity, demand_all_full=demand_all_full, demand_tiered=demand_tiered)


def ch21_deterrence(p, penalty, gain):
    return p * penalty >= gain


def all_numbers():
    return {
        "ch02_A": ch02_verification_adjusted(0.66, 0.3, 0.2),
        "ch02_A_threshold": ch02_threshold(0.3, 0.2),
        "ch02_B": ch02_verification_adjusted(0.5, 0.5, 0.4),
        "ch04_base": ch04_growth(),
        "ch04_no_power_growth": ch04_growth(power=1.0),
        "ch04_slow_algorithms": ch04_growth(algorithmic_halving_months=16),
        "ch05_autonomy": ch05_harm(0.005, 2000, 0.9),
        "ch05_supervised": ch05_harm(0.0045, 2000, 216 + 12),
        "ch05_break_even_error": 0.0045 + (216 + 12 - 0.9) / 2000,
        "ch07_delay_lives": ch07_delay_cost(),
        "ch07_delay_lives_half_effect": ch07_delay_cost(effect_fraction=0.5),
        "ch08_rebound_e1.5": ch08_rebound(2, 1.5),
        "ch08_rebound_e0.7": ch08_rebound(2, 0.7),
        "ch10_z": ch10_two_proportion_z(52, 1800, 14, 1800),
        "ch10_rule_of_three_21400": ch10_rule_of_three(21400),
        "ch11_A": ch11_leontief(100, 40, 30),
        "ch11_A_more_compute": ch11_leontief(150, 40, 30),
        "ch11_A_more_institutions": ch11_leontief(100, 40, 40),
        "ch14_before": ch14_detection([0.05, 0.10, 0.20]),
        "ch14_after": ch14_detection([0.30, 0.70, 0.10, 0.20]),
        "ch15_a0.6_k10": ch15_amdahl(0.6, 10),
        "ch15_a0.6_kinf": ch15_amdahl(0.6, 1e12),
        "ch15_a0.9_k10": ch15_amdahl(0.9, 10),
        "ch15_bottleneck_share": ch15_bottleneck_share(0.6, 10),
        "ch16": ch16_regret(),
        "ch17_before": ch17_reach(0.82, 140 / 600),
        "ch17_after": ch17_reach(0.97, 1.0),
        "ch19": ch19_capacity(),
        "ch21_before": ch21_deterrence(0.32, 20, 10),
        "ch21_after": ch21_deterrence(0.85, 20, 10),
    }


if __name__ == "__main__":
    import json
    print(json.dumps(all_numbers(), indent=2, default=str))

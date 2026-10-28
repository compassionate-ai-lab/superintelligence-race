"""M5. Minimax regret, dominance thresholds and the timing of options (Chapters 3, 12, 16, 17, 20, 23).

L[a][s] loss of strategy a in scenario s (illustrative units, lower is better)
regret[a][s] = L[a][s] - min_b L[b][s]
minimax-regret strategy: argmin_a max_s regret[a][s]
No probabilities are needed; the expected-loss comparison is shown only to
locate the probability at which a different strategy would be preferred.
"""

SCENARIOS = ["fast", "moderate", "slow"]
LOSS = {   # Chapter 3 worked example ($ billion of foregone net benefit, illustrative)
    "S1 big bet now": [4, 9, 16],
    "S2 institutions and flexible access": [10, 5, 3],
    "S3 wait": [22, 10, 2],
    "S4 staged: institutions now, prepared option to scale": [7, 5, 4],
}


def regrets(loss):
    cols = list(zip(*loss.values()))
    best = [min(c) for c in cols]
    return {a: [l - b for l, b in zip(v, best)] for a, v in loss.items()}


def minimax_regret(loss):
    r = regrets(loss)
    return min(r, key=lambda a: max(r[a])), {a: max(v) for a, v in r.items()}


def expected(loss, p):
    # rounded so the printed values are identical on every Python version (3.12+ sums floats differently)
    return {a: round(sum(pi * li for pi, li in zip(p, v)), 10) for a, v in loss.items()}


def threshold_fast(loss, a, b):
    """P(fast) above which a beats b, with moderate and slow sharing the remainder equally."""
    la, lb = loss[a], loss[b]
    # E = p*L_f + (1-p)/2*(L_m + L_s)
    ma, mb = (la[1] + la[2]) / 2, (lb[1] + lb[2]) / 2
    # p*la_f + (1-p)ma = p*lb_f + (1-p)mb
    denom = (la[0] - ma) - (lb[0] - mb)
    return (mb - ma) / denom if denom else None


def timely(warning_years, lead_years, prepared_years):
    """A signpost-triggered option is timely if the warning it gives covers the
    remaining lead time after preparation."""
    return warning_years >= lead_years - prepared_years


def worked_example():
    choice, maxreg = minimax_regret(LOSS)
    return {
        "regrets": regrets(LOSS),
        "max_regret": maxreg,
        "minimax_choice": choice,
        "expected_p_.5_.3_.2": expected(LOSS, [0.5, 0.3, 0.2]),
        "expected_p_.8_.15_.05": expected(LOSS, [0.8, 0.15, 0.05]),
        "p_fast_threshold_S1_over_S4": threshold_fast(LOSS, "S1 big bet now",
                                                      "S4 staged: institutions now, prepared option to scale"),
        "timely_unprepared": timely(2, 3, 0),
        "timely_prepared": timely(2, 3, 1.5),
    }

import math, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from agi_models import m1_governance as m1, m2_intervention as m2, m3_dependency as m3, m4_compute as m4, m5_regret as m5, m6_compassion as m6, cases


def test_m1():
    e = m1.worked_example()
    assert abs(e["rho_today"] - 0.9722) < 1e-3 and round(e["n_max_today"]) == 8229 and e["n_max_r3"] == 19200


def test_m2_units_and_limits():
    assert m2.max_tau_constant(18, 5, 0.75) == 13 / 0.75
    assert m2.max_tau_constant(4, 5, 1) == 0.0                       # reserve breached
    assert abs(m2.max_tau_accelerating(18, 5, 0.75, 1e-9) - 13 / 0.75) < 1e-3   # g -> 0 limit
    assert m2.max_tau_accelerating(18, 5, 0.75, 0.05) < 13 / 0.75


def test_m3():
    assert abs(m3.both_checks_fail(0.05, 0) - 0.0025) < 1e-12
    assert m3.both_checks_fail(0.05, 0.2) > 4 * 0.0025


def test_m5():
    assert m5.minimax_regret(m5.LOSS)[0].startswith("S4")
    assert abs(m5.threshold_fast(m5.LOSS, "S1 big bet now", "S4 staged: institutions now, prepared option to scale") - 8 / 11) < 1e-9


def test_m6_heatwave():
    c = m6.campus_check()
    assert c["option_b_gap"] == 50 and c["hybrid_total"] == 1450 and c["hybrid_energy_mwh"] == 5800
    ev = {e["action"][:2]: e for e in (m6.evaluate(a) for a in m6.options())}
    assert ev["H:"]["all_floors_met"] and not ev["A:"]["all_floors_met"] and not ev["B:"]["feasible"]


def test_hospital_ledger():
    d = cases.hospital_derived()
    assert abs(d["pilot_reduction"] - 0.229167) < 1e-5 and abs(d["error_rate"] - 0.0074) < 1e-4


def test_review_corrections():
    from agi_models import worked_numbers as w
    d = cases.hospital_derived()
    assert d["agent_errors_total"] == 105 and abs(d["readmission_diff_ci95"][1] - 0.0069) < 5e-4
    assert 105 + 84 + 67 == 256
    sch = m6.hourly_schedule()
    assert sch["total_mwh"] == 5800 and sch["unstaggered_total_mwh"] == 5760
    assert all(v == 1450 for v in sch["totals_mw"].values())
    assert abs(w.ch10_two_proportion_z(52, 1800, 14, 1800) - 4.72) < 0.01
    assert w.ch19_capacity()["demand_tiered"] == 141 and w.ch19_capacity()["capacity"] == 192
    assert w.ch16_regret()[1] == "domain + evaluation + anchored"


def test_m4():
    e = m4.worked_example()
    assert e["cheapest_normal_only"][:2] == (100.0, (100, 0, 0))
    assert e["zero_shortfall_without_conflict_scenario"][:2] == (230.0, (70, 100, 0))
    assert e["zero_shortfall_all_scenarios"][:2] == (320.0, (70, 0, 100))
    assert all(e[k][2] == 0 for k in ("cheapest_normal_only", "zero_shortfall_without_conflict_scenario",
                                      "zero_shortfall_all_scenarios"))   # floor met in every case


def test_m4_continuous():
    from fractions import Fraction as F
    costs, caps = [1.0, 1.6, 2.5], [200, 120, 100]
    avail = [[1, 1, 1], [0, 1, 1], [1, 0.5, 1], [0.6, 0.6, 0.6], [0, 0, 1]]
    c4, x4 = m4.continuous_optimum(costs, caps, avail[:4], 100)
    c5, x5 = m4.continuous_optimum(costs, caps, avail, 100)
    assert (c4, x4) == (F(680, 3), (F(200, 3), F(100), F(0)))       # 66 2/3 foreign + 100 regional
    assert (c5, x5) == (F(950, 3), (F(200, 3), F(0), F(100)))        # 66 2/3 foreign + 100 sovereign
    assert 230 - c4 == 320 - c5 == F(10, 3)                          # blocks of 10 add 3 1/3 to each


def test_m5_expected_exact():
    e = m5.worked_example()
    assert e["expected_p_.5_.3_.2"]["S1 big bet now"] == 7.9          # same on every Python version
    assert e["expected_p_.8_.15_.05"]["S3 wait"] == 19.2


import unittest


class TestBook(unittest.TestCase):
    """Runs every test_ function above under unittest (python -m unittest discover -s tests -v)."""


for _n, _f in sorted(dict(globals()).items()):
    if _n.startswith("test_") and callable(_f):
        setattr(TestBook, _n, (lambda f: lambda self: f())(_f))


if __name__ == "__main__":
    for n, f in sorted(globals().items()):
        if n.startswith("test_"):
            f(); print("pass", n)

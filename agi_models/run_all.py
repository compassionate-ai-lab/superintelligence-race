"""Reproduce every model-derived number in the book: python -m agi_models.run_all"""
import json
from . import m1_governance, m2_intervention, m3_dependency, m4_compute, m5_regret, m6_compassion, cases, worked_numbers


def tidy(o):
    """Round floats to 12 significant digits so the printout has no binary-rounding noise."""
    if isinstance(o, float):
        return float(f"{o:.12g}")
    if isinstance(o, dict):
        return {k: tidy(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [tidy(v) for v in o]
    return o


def main():
    out = {
        "M1 governance-capacity boundary (Ch 1)": m1_governance.worked_example(),
        "M2 intervention margin (Ch 6)": m2_intervention.worked_example(),
        "M3 dependencies (Appendix F)": m3_dependency.worked_example(),
        "M4 robust compute allocation (Appendix F)": m4_compute.worked_example(),
        "M5 minimax regret (Ch 3)": m5_regret.worked_example(),
        "M6 heatwave (Ch 24)": m6_compassion.worked_example(),
        "Case ledger: hospital (Ch 20)": cases.hospital_derived(),
        "Other worked numbers (Ch 2, 4, 5, 7-12, 14-19, 21)": worked_numbers.all_numbers(),
    }
    print(json.dumps(tidy(out), indent=2, default=str))


if __name__ == "__main__":
    main()

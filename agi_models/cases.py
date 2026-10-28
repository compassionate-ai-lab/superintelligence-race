"""Canonical case ledger: one numerical record for every recurring illustrative case.
Chapters, figures and the Workbook must agree with these values."""

HOSPITAL = dict(  # Chapter 20 (referred to in 5, 10, 22)
    hospitals=14, claim_reduction=0.30,
    pilot_hospitals=2, pilot_period="1 May-31 Oct 2031", discharges=6240, bookings=5130,
    baseline_h=9.6, pilot_h=7.4, comparison_baseline_h=9.5, comparison_pilot_h=9.2,
    errors=38, errors_minor=31, errors_moderate=7, overrides=256,
    overrides_patient_preference=105, overrides_clinical_change=84, overrides_agent_error=67,
    readmission_baseline=0.070, readmission_pilot=0.068, noninferiority_margin=0.01,
    interpreter_patients=686, interpreter_baseline_h=11.2, interpreter_pilot_h=10.1,
    extended_to=5, failure_date="14 Feb 2032", first_duplicate="06:10", detected="08:05",
    contained="08:50", disruption_end="15:10", reconciled="08:10 15 Feb", duplicates=212,
    delayed_over_4h=31, discharges_reversed=1, restart="4 Mar 2032",
    post_restart_bookings=21400, post_restart_errors=64, interpreter_dec2032_reduction=0.17,
    final_hospitals=9,
)


def _ci(h):
    import math
    n = h["discharges"]
    p1, p2 = h["readmission_pilot"], h["readmission_baseline"]
    se = math.sqrt(p1 * (1 - p1) / n + p2 * (1 - p2) / n)
    d = p1 - p2
    return (round(d - 1.96 * se, 4), round(d + 1.96 * se, 4))


def hospital_derived(h=HOSPITAL):
    pilot = (h["baseline_h"] - h["pilot_h"]) / h["baseline_h"]
    comp = (h["comparison_baseline_h"] - h["comparison_pilot_h"]) / h["comparison_baseline_h"]
    interp = (h["interpreter_baseline_h"] - h["interpreter_pilot_h"]) / h["interpreter_baseline_h"]
    return dict(
        pilot_reduction=pilot,
        comparison_reduction=comp,
        attributable_reduction=pilot - comp,
        error_rate=h["errors"] / h["bookings"],
        override_rate=h["overrides"] / h["bookings"],
        agent_errors_total=h["errors"] + h["overrides_agent_error"],
        agent_proposal_error_rate=(h["errors"] + h["overrides_agent_error"]) / h["bookings"],
        readmission_diff_ci95=_ci(h),
        interpreter_reduction=interp,
        interpreter_share=h["interpreter_patients"] / h["discharges"],
        post_restart_error_rate=h["post_restart_errors"] / h["post_restart_bookings"],
        detection_to_containment_min=45, first_duplicate_to_containment="2 h 40 min",
    )

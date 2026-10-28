"""M6. Compassionate decisions under incompatible burdens: the Heatwave Night
(Chapter 24; also Chapters 7, 9, 17, 18, 22).

All inputs are illustrative and internally consistent; they describe no real city.
Power is in MW (a rate); energy is in MWh (power x time).

Method (lexicographic, not a weighted sum):
  1. physical feasibility: relief >= shortfall over the whole window
  2. floors that must hold in every case:
       - essential compute (dispatch triage, hospital coordination) >= its floor
       - registered life-dependent households never rotated
       - high-risk residents off supply at any moment <= reachable cooling places
  3. among actions meeting 1-2: fewest high-risk person-hours exposed to heat
     without supply, then fewest person-hours of water deferral beyond 2 h,
     then fairest distribution, then fastest recovery, then lowest cost.
If no action meets the floors, the infeasibility is reported, not hidden.
"""
from dataclasses import dataclass, field

CITY = dict(
    residents=14_000_000,
    kw_per_resident=0.42,          # residential-feeder load per resident in the window
    window_h=4,                    # 19:00-23:00
    shortfall_mw=1450,
    high_risk_share=0.06,          # older people living alone, chronic illness, infants
    campus_mw=2000,
    campus_essential_mw=150,       # dispatch triage + hospital coordination + telecom core
    reachable_cooling_places=8000, # centres within 15 minutes' walk of rotated feeders
    water_people_per_mw=20_000,    # residents whose supply is deferred per MW of pumping deferred
)


@dataclass
class Action:
    name: str
    campus_cut_mw: float = 0       # total campus reduction
    essential_cut_mw: float = 0    # part of the campus cut that falls on essential services
    external_flex_mw: float = 0    # pre-agreed: building cooling setpoints, industry, 2-h water deferral
    water_extra_mw: float = 0      # additional water-pumping deferral (4 h)
    residential_mw: float = 0
    block_h: float = 1             # rotation block length
    rotates_registered: bool = False
    notes: list = field(default_factory=list)


def evaluate(a: Action, city=CITY, cooling_places=None):
    c = dict(city)
    if cooling_places is not None:
        c["reachable_cooling_places"] = cooling_places
    relief = a.campus_cut_mw + a.external_flex_mw + a.water_extra_mw + a.residential_mw
    off_now = a.residential_mw * 1000 / c["kw_per_resident"]          # people without supply at any moment
    blocks = c["window_h"] / a.block_h if a.residential_mw else 0
    people_rotated = off_now * blocks
    hr_now = off_now * c["high_risk_share"]
    out = dict(
        action=a.name,
        relief_mw=relief,
        energy_mwh=relief * c["window_h"],
        feasible=relief >= c["shortfall_mw"],
        shortfall_left_mw=max(0, c["shortfall_mw"] - relief),
        essential_mw=c["campus_essential_mw"] - a.essential_cut_mw,
        essential_floor_met=a.essential_cut_mw == 0,
        registered_protected=not a.rotates_registered,
        people_off_at_once=round(off_now),
        people_rotated=round(people_rotated),
        person_hours_off=round(off_now * c["window_h"]),
        high_risk_off_at_once=round(hr_now),
        high_risk_person_hours=round(hr_now * c["window_h"]),
        cooling_floor_met=hr_now <= c["reachable_cooling_places"],
        water_people_4h=round(a.water_extra_mw * c["water_people_per_mw"]),
    )
    out["all_floors_met"] = out["feasible"] and out["essential_floor_met"] and out["registered_protected"] and out["cooling_floor_met"]
    return out


def options():
    A = Action("A: residential rotation only (2-h blocks)", residential_mw=1450, block_h=2)
    B = Action("B: campus cut 70% across the board", campus_cut_mw=1400, essential_cut_mw=105,
               residential_mw=0, block_h=1)
    B50 = Action("B + 50 MW residential", campus_cut_mw=1400, essential_cut_mw=105, residential_mw=50, block_h=1)
    H = Action("H: hybrid (protect 150, curtail 1,250, flex 150, residential 50)",
               campus_cut_mw=1250, external_flex_mw=150, residential_mw=50, block_h=1)
    HW = Action("H-water: hybrid, 50 MW extra water deferral instead of residential",
                campus_cut_mw=1250, external_flex_mw=150, water_extra_mw=50)
    return [A, B, B50, H, HW]


def sensitivity():
    s1 = Action("S1: migration delivers 950 not 1,250; +110 water, +190 residential",
                campus_cut_mw=950, external_flex_mw=150, water_extra_mw=110, residential_mw=240, block_h=1)
    s2 = Action("S2: a 30 MW block cannot be isolated from a dialysis feeder; replaced by water deferral",
                campus_cut_mw=1250, external_flex_mw=150, water_extra_mw=30, residential_mw=20, block_h=1)
    s3_h = Action("S3: only 14 reachable cooling centres (5,600 places); hybrid as planned",
                  campus_cut_mw=1250, external_flex_mw=150, residential_mw=50, block_h=1)
    s3_w = Action("S3 switch: replace residential 50 MW by water deferral",
                  campus_cut_mw=1250, external_flex_mw=150, water_extra_mw=50)
    return [(s1, None), (s2, None), (s3_h, 5600), (s3_w, 5600)]


def campus_check():
    c = CITY
    return dict(
        option_b_relief=0.7 * c["campus_mw"],
        option_b_gap=c["shortfall_mw"] - 0.7 * c["campus_mw"],
        hybrid_campus_load=c["campus_mw"] - 1250,
        hybrid_campus_reduction_pct=1250 / c["campus_mw"] * 100,
        hybrid_total=1250 + 150 + 50,
        hybrid_energy_mwh=(1250 + 150 + 50) * c["window_h"],
    )


def hourly_schedule():
    """Hybrid H, hour by hour (MW). Water pumping is staggered across two sets of wards,
    each paused for two hours, so 20 MW is saved in every hour."""
    hours = ["19-20", "20-21", "21-22", "22-23"]
    rows = {h: dict(campus=1250, cooling=80, industry=50, water=20, residential=50) for h in hours}
    totals_mw = {h: sum(r.values()) for h, r in rows.items()}
    energy = {k: sum(r[k] for r in rows.values()) for k in rows[hours[0]]}
    unstaggered_mwh = sum(energy.values()) - 2 * 20       # water paused only two hours
    return dict(totals_mw=totals_mw, energy_mwh=energy, total_mwh=sum(energy.values()),
                unstaggered_total_mwh=unstaggered_mwh)


def worked_example():
    return dict(campus=campus_check(), schedule=hourly_schedule(),
                options=[evaluate(a) for a in options()],
                sensitivity=[evaluate(a, cooling_places=cp) for a, cp in sensitivity()])

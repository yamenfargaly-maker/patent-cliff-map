"""
POS.PY — probability of success priors and risk-adjusted NPV.

Two things live here:

  1. A calibrated PRIOR model of clinical probability of success, built from the
     published phase-transition literature. This is what runs today.
  2. An rNPV engine that turns (phase, PoS, peak sales) into a fair value.

`pos_train.py` trains an empirical model on AACT trial data and writes
`pos_model.json`; if that file is present, `pos()` blends the trained estimate
with the prior below instead of using the prior alone.

CENTRAL PRIOR: BIO / Informa Pharma Intelligence / QLS Advisors, "Clinical
Development Success Rates and Contributing Factors 2011-2020" (Feb 2021).
12,728 transitions, 9,704 programs, 1,779 companies. Chosen over Wong/Siah/Lo
(2019) because it is the most recent complete phase-by-phase publication, uses a
four-transition structure matching how rNPV is actually built, and does not
impute unresolved trial outcomes. Wong is carried as the optimistic bound.
"""
import json, math, os

# ---------------------------------------------------------------------------
# PHASE TRANSITIONS — BIO 2011-2020, by therapeutic area
# order: P1->P2, P2->P3, P3->Filing, Filing->Approval
# ---------------------------------------------------------------------------
BIO_2011_2020 = {
    "Hematology":       (0.696, 0.481, 0.768, 0.931),   # LOA 23.9%
    "Metabolic":        (0.618, 0.450, 0.636, 0.875),   # 15.5%
    "Infectious":       (0.578, 0.384, 0.640, 0.929),   # 13.2%
    "Ophthalmology":    (0.716, 0.355, 0.512, 0.911),   # 11.9%
    "Immunology":       (0.552, 0.314, 0.653, 0.941),   # 10.7%
    "Vaccines":         (0.527, 0.316, 0.581, 1.000),   # 9.7%  (modality row)
    "Gastroenterology": (0.467, 0.342, 0.571, 0.909),   # 8.3%
    "ALL":              (0.520, 0.289, 0.578, 0.906),   # 7.9%
    "Respiratory":      (0.559, 0.219, 0.645, 0.956),   # 7.5%
    "Psychiatry":       (0.527, 0.268, 0.563, 0.912),   # 7.3%
    "Endocrine":        (0.433, 0.266, 0.662, 0.863),   # 6.6%
    "Neurology":        (0.477, 0.268, 0.531, 0.867),   # 5.9%
    "Oncology":         (0.488, 0.246, 0.477, 0.920),   # 5.3%
    "Cardiovascular":   (0.500, 0.210, 0.552, 0.825),   # 4.8%
    # oncology sub-segments, same source
    "Immuno-oncology":  (0.640, 0.402, 0.490, 0.984),   # 12.4%
    "Heme-oncology":    (0.501, 0.278, 0.600, 0.900),   # 7.5%
    "Solid tumor":      (0.489, 0.234, 0.429, 0.929),   # 4.6%
    # cohort rows
    "Rare disease":     (0.674, 0.446, 0.604, 0.936),   # 17.0%
}

# Industry LOA fell 7.9% (2011-20) -> 6.7% (2014-23) per Citeline/Biomedtracker.
# Applied as a uniform forward-looking haircut on the cumulative figure.
DRIFT = 0.85

# ---------------------------------------------------------------------------
# MODIFIERS — effect size, and which transitions each one actually touches.
# Naive multiplication is WRONG: these variables are strongly correlated and each
# was estimated marginally against the all-indication baseline. Stacking them
# raw would give a 49x uplift and a PoS above 1.0. Instead they are combined in
# LOG-ODDS space with a damping exponent and a hard cap on total uplift.
# ---------------------------------------------------------------------------
MODIFIERS = {
    # key: (odds multiplier, transitions affected (0-3), source)
    "lead_indication":   (3.10, (0,1,2,3), "Hay 2014: lead 15.3% vs non-lead 4.9% LOA"),
    "biomarker_select":  (2.10, (1,2),     "BIO 2011-20 fig.11: 15.9% vs 7.6% LOA; effect sits in P2->3 and P3->filing"),
    "genetic_evidence":  (2.60, (1,2),     "Minikel et al., Nature 2024, n=13,022 target-indication pairs; weak in P1"),
    "rare_disease":      (2.20, (0,1,2,3), "BIO 2011-20: 17.0% vs 7.9%. CONTRADICTED by Wong 2019 in oncology (1.2%)"),
    "chronic_prevalent": (0.75, (0,1,2,3), "BIO 2011-20: chronic high-prevalence 5.9% vs 7.9%"),
    "mab":               (1.60, (0,1,2,3), "BIO 2011-20: mAb 12.1% vs small molecule 7.5%"),
    "antisense":         (0.66, (0,1,2,3), "BIO 2011-20: antisense 5.2% LOA (n=162)"),
    "breakthrough":      (1.35, (2,3),     "DAMPED from the reported 72% BTD approval rate, which is severely selection-confounded"),
}

DAMPING = 0.55   # each modifier's log-odds effect is scaled by this before stacking
MAX_UPLIFT = 3.5 # hard ceiling on combined uplift vs the unmodified TA prior
PHASES = ["Preclinical", "Ph1", "Ph2", "Ph3", "Filed", "Commercial"]


# Several BIO cells report exactly 1.000 (vaccines, CAR-T, siRNA filing->approval).
# Those are small-sample artifacts, not certainties — clamp before taking log-odds.
EPS = 1e-3
def _clamp(p):  return min(max(p, EPS), 1 - EPS)
def _logit(p):  p = _clamp(p); return math.log(p / (1 - p))
def _expit(x):  return 1 / (1 + math.exp(-x))


def transitions(ta):
    """Four phase-transition probabilities for a therapeutic area."""
    return BIO_2011_2020.get(ta, BIO_2011_2020["ALL"])


def pos(ta, phase, mods=(), drift=True, trained=None):
    """
    Probability that an asset in `phase` within therapeutic area `ta` reaches approval.

    mods: iterable of MODIFIER keys.
    Returns (probability, explanation dict).
    """
    if phase == "Commercial":
        return 1.0, {"note": "approved and marketed"}
    base = list(transitions(ta))
    start = {"Preclinical": 0, "Ph1": 0, "Ph2": 1, "Ph3": 2, "Filed": 3}[phase]

    adj = list(base)
    applied = []
    for m in mods:
        if m not in MODIFIERS:
            raise KeyError(f"unknown modifier {m!r}")
        mult, which, src = MODIFIERS[m]
        applied.append((m, mult, src))
        for i in which:
            if i < start:
                continue
            adj[i] = _expit(_logit(adj[i]) + DAMPING * math.log(mult))

    raw = 1.0
    for p in base[start:]:
        raw *= p
    val = 1.0
    for p in adj[start:]:
        val *= p

    # cap combined uplift so correlated modifiers cannot compound without bound
    capped = False
    if raw > 0 and val / raw > MAX_UPLIFT:
        val, capped = raw * MAX_UPLIFT, True

    if drift:
        val *= DRIFT

    # blend with a trained empirical estimate if one exists
    blended = None
    if trained is not None:
        w = trained.get("weight", 0.5)
        blended = _expit((1 - w) * _logit(val) + w * _logit(trained["p"]))

    return (blended if blended is not None else min(val, 0.99)), {
        "ta": ta, "phase": phase, "base_transitions": base, "adjusted": adj,
        "unmodified": raw, "modified": val, "uplift_capped": capped,
        "drift_applied": drift, "modifiers": applied,
        "trained_blend": blended is not None,
    }


# ---------------------------------------------------------------------------
# rNPV
# Clinical risk is carried ENTIRELY in the PoS term. The discount rate is a
# WACC-style 10% -- Baras/Baras/Schulman (Nat Rev Drug Discov 2012, median 10%),
# DiMasi 2016 (10.5% real), Alacrita (10-13%), WIPO. Using a venture-style
# 20-40% rate AND PoS is double-counting and is the single most common error in
# published biotech valuations.
# ---------------------------------------------------------------------------
DISCOUNT = 0.10

# Median peak US sales and years-to-peak, by area.
# Tendler, Chaudhuri, Shukla, Kumar & Lo, Ther Innov Regul Sci 2026;
# n=391 NME launches 2000-2023. Median peak $462M overall; distribution is
# log-normal and heavily right-skewed, so the median is well below the $1,132M mean.
PEAK = {   # ($M, years to peak)
    "Psychiatry":      (1129, 8), "Respiratory":   (911, 5), "Immunology":     (852, 7),
    "Cardiovascular":  (790, 9),  "Vaccines":      (556, 7), "Metabolic":      (484, 6),
    "Neurology":       (484, 6),  "Oncology":      (419, 6), "Infectious":     (385, 5),
    "ALL":             (462, 6),
}
YEARS_TO_LAUNCH = {"Preclinical": 9, "Ph1": 7, "Ph2": 5, "Ph3": 3, "Filed": 1, "Commercial": 0}
PLATEAU = 7        # years at peak before appreciable decline (Tendler 2026)
OP_MARGIN = 0.50   # asset-level operating margin at peak: COGS 5-20%, SG&A 20-30%
TAX = 0.21


def rnpv(peak_sales_musd, years_to_launch, p_success, exclusivity_years=12,
         years_to_peak=6, plateau=PLATEAU, discount=DISCOUNT,
         op_margin=OP_MARGIN, tax=TAX):
    """
    Risk-adjusted NPV of a single asset, in $M.

    Revenue shape: linear ramp from launch to peak, flat plateau, then
    post-LOE decay to 15% of peak (FDA 2019 generic price data: with 6+ generic
    entrants price falls to ~6-10% of brand; revenue erosion is steeper than
    price erosion because volume shifts too).
    """
    total, yr = 0.0, years_to_launch
    for t in range(1, exclusivity_years + 1):
        if t <= years_to_peak:
            rev = peak_sales_musd * t / years_to_peak
        elif t <= years_to_peak + plateau:
            rev = peak_sales_musd
        else:
            rev = peak_sales_musd * 0.15
        cf = rev * op_margin * (1 - tax)
        total += cf / (1 + discount) ** (yr + t)
    return total * p_success


def fair_value(ta, phase, mods=(), peak_override=None, **kw):
    """rNPV in $B for an asset, using area-median commercial assumptions."""
    p, detail = pos(ta, phase, mods, **kw)
    peak, ytp = PEAK.get(ta, PEAK["ALL"])
    if peak_override:
        peak = peak_override
    v = rnpv(peak, YEARS_TO_LAUNCH[phase], p, years_to_peak=ytp)
    return v / 1000.0, p, detail


def load_trained(path="pos_model.json"):
    """Load pos_train.py output if the user has run it."""
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)


if __name__ == "__main__":
    print(f"{'area':<18}{'Ph1':>8}{'Ph2':>8}{'Ph3':>8}{'Filed':>8}   (cumulative PoS to approval, drift-adjusted)")
    for ta in ["ALL", "Oncology", "Neurology", "Psychiatry", "Immunology",
               "Cardiovascular", "Metabolic", "Rare disease", "Vaccines", "Immuno-oncology"]:
        row = "".join(f"{pos(ta, ph)[0]*100:>7.1f}%" for ph in ["Ph1", "Ph2", "Ph3", "Filed"])
        print(f"{ta:<18}{row}")

    print("\nModifier behaviour — Ph2 neurology asset, showing the damping and cap:")
    for mods in [(), ("lead_indication",), ("lead_indication", "biomarker_select"),
                 ("lead_indication", "biomarker_select", "genetic_evidence"),
                 ("lead_indication", "biomarker_select", "genetic_evidence", "rare_disease")]:
        p, d = pos("Neurology", "Ph2", mods)
        naive = pos("Neurology", "Ph2")[0]
        for m in mods:
            naive *= MODIFIERS[m][0]
        print(f"  {len(mods)} mods: modelled {p*100:5.1f}%   naive-stacked {naive*100:6.1f}%"
              f"{'   [CAPPED]' if d['uplift_capped'] else ''}")

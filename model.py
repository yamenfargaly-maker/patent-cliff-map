"""
THE 2030 PATENT CLIFF MAP
Acquirer urgency vs. BD firepower, mapped to a scored target universe.

All inputs sourced to company filings / Q2-2026 releases as of 17 Aug 2026.
See SOURCES.md for line-level attribution. Estimates flagged in `conf`.
"""
import json
import pos as POS

TARGET_LEVERAGE = 3.0   # net debt / LTM EBITDA an A-/BBB+ issuer can defend
WINDOW_START, WINDOW_END = 2027, 2032

# ---------------------------------------------------------------------------
# ACQUIRERS
# rev / at_risk in $B (FY2025 basis). net_debt / ebitda in $B (Q2-2026 LTM).
# pf_adj = incremental net debt from announced-but-unclosed deals.
# peak_yr = year the largest single LOE lands.
# ---------------------------------------------------------------------------
ACQ = [
 # name, ticker, rev, at_risk, net_debt, ebitda, pf_adj, peak_yr, conf, note
 ("Merck & Co",        "MRK",  65.0, 34.1, 46.77, 28.87,  0.0, 2028, "high",
  "Keytruda $31.6B / 48.7% of revenue, US LOE 2028. Vaccines (Gardasil, Vaxneuvance) EXCLUDED — no 351(k) biosimilar pathway has ever been used."),
 ("Bristol Myers",     "BMY",  48.2, 27.1, 32.05, 18.93,  0.0, 2028, "high",
  "Eliquis $14.4B (Apr-2028 settlement) + Opdivo $10.0B (2028). Cleanest dataset in the set — all dates from the 10-K exclusivity table."),
 ("Novo Nordisk",      "NVO",  46.8, 34.6, 14.50, 21.60,  0.0, 2031, "high",
  "Semaglutide 73.9% of revenue. US ~Dec-2031; EU SPCs stagger UK 2027 / Italy 2028 / Germany 2029; Canada, China, India, Brazil already off-patent."),
 ("Johnson & Johnson", "JNJ",  94.2, 25.9, 28.28, 33.20,  0.0, 2029, "med",
  "Darzalex $14.4B (2029) + Tremfya (2031). Revenues exact; LOE dates from J&J's portfolio disclosure, not a filings table."),
 ("Roche",             "RHHBY",75.1, 23.1, 27.26, 30.40,  0.0, 2029, "low",
  "Perjeta REMOVED — Roche states its primary patents expired Q2-2025. Roche discloses no expiry date for Ocrevus, Hemlibra, Tecentriq, Kadcyla or Alecensa. Dates are estimates."),
 ("Pfizer",            "PFE",  62.6, 20.8, 51.50, 25.38,  0.0, 2028, "high",
  "Eliquis alliance $8.0B + Ibrance $4.1B (2027) + Xtandi (2027). Vyndaqel now settled to 1 Jun 2031 — a 2031 event, not 2026-28."),
 ("AstraZeneca",       "AZN",  58.7, 20.7, 26.91, 20.25,  0.0, 2030, "high",
  "Imfinzi 2031, Tagrisso 2032, Lynparza 2027. Best-disclosed patent table in the sector. Farxiga $8.4B sits at 2026, just outside."),
 ("Novartis",          "NVS",  54.5, 20.2, 39.40, 22.40,  0.0, 2029, "low",
  "Revenues exact. Novartis publishes NO patent expiry table; only company statement is Cosentyx 'around the end of the decade'. Other four dates unknown."),
 ("Sanofi",            "SNY",  49.3, 19.8, 17.68, 15.47,  0.0, 2031, "high",
  "Dupixent EUR 15,714M = 36.0% of net sales, plus Fabrazyme and Nexviazyme. CoM Oct-2027, PTE to Mar-2031, formulation claims asserted to 2045."),
 ("Eli Lilly",         "LLY",  65.2, 18.0, 45.96, 36.40,  0.0, 2029, "high",
  "All five dates confirmed in the 10-K IP table: Trulicity 2027, Jardiance 2029, Taltz 2030, Verzenio 2031, Olumiant 2032. Denominator growing fast."),
 ("GSK",               "GSK",  43.4, 15.9, 20.01, 13.40, 10.6, 2028, "med",
  "Shingrix REMOVED — US patents run 2035-39, outside the window. Dolutegravir GBP 5,648M from Apr-2028 is the real event. Nuvalent $10.6B pending."),
 ("Amgen",             "AMGN", 36.8, 13.9, 43.32, 17.27,  0.0, 2028, "high",
  "Seven LOEs 2027-30 (Otezla, Enbrel, Repatha, Kyprolis, Nplate, Tepezza, Blincyto), all with exact dates in the 10-K. 2.5x levered, negative outlook."),
 ("AbbVie",            "ABBV", 61.2, 10.2, 64.25, 24.74, 10.9, 2032, "high",
  "Lowest in-window exposure. Rinvoq settled to Apr-2037, Skyrizi $17.6B hits 2033 — just outside. EBITDA corrected down 24% from the aggregator figure."),
 ("Gilead",            "GILD", 29.4,  9.7, 23.07, 14.60,  0.0, 2030, "high",
  "Biktarvy resettled 2033 -> 1 Apr 2036. EBITDA is pre-IPR&D: GAAP H1-26 shows an operating loss after $11.3B of acquired IPR&D."),
 ("Regeneron",         "REGN", 14.3,  5.9, -15.12, 4.70,  0.0, 2031, "high",
  "Total Sanofi collaboration revenue $5.9B (Dupixent + Kevzara), 2031. Eylea cliff already in the run-rate. Net cash $15.1B incl. long-term securities."),
 ("Takeda",            "TAK",  30.0,  5.7, 27.57,  9.50,  0.0, 2032, "med",
  "Entyvio date now VERIFIED at 2032 from the 20-F; Alvotech biosimilar blocked to May-2032. Revenue estimate unverified. FY ends 31 March."),
 ("Biogen",            "BIIB",  9.9,  1.5,  6.81,  3.36,  0.0, 2030, "med",
  "Total revenue, not product revenue. Cliff already happened (Tecfidera 2020, Tysabri 2023-25). A further $1.4B Ocrevus royalty is exposed but undateable."),
 ("Bayer",             "BAYRY",51.4,  0.8, 38.34, 11.58,  0.0, 2028, "high",
  "CORRECTED: Xarelto and Eylea LOEs have ALREADY happened per Bayer's own AR2025. Only Adempas remains in-window. Bayer is not a patent-cliff story."),
 ("Vertex",            "VRTX", 12.0,  0.6, -13.64, 5.10,  8.8, 2032, "high",
  "Trikafta protected to 2037. Least exposed name in the cohort. Zero borrowings — net cash falls to ~$2.8B pro forma for Crinetics."),
]

# ---------------------------------------------------------------------------
# PRECEDENT PREMIUMS — median, by target phase at announcement
# Rebuilt on ONE basis: premium to prior-day close (or the unaffected close where a
# leak is identifiable). Mixing prior-close and VWAP bases overstated every clinical
# bucket by 6-10 points. n=41 disclosed premiums; IQRs are wide and reported in the memo.
# ---------------------------------------------------------------------------
PREM = {"Ph1": 1.050, "Ph2": 0.540, "Ph3": 0.435, "Commercial": 0.365}

# ---------------------------------------------------------------------------
# TARGET UNIVERSE — market caps as of 14-17 Aug 2026
# fit = therapeutic areas this asset could backfill
# ---------------------------------------------------------------------------
TGT = [
 # ticker, name, mcap, cash, ta, asset, mechanism, phase, fit_acquirers, thesis
 ("RVMD","Revolution Medicines",45.28,3.94,"Oncology","Daraxonrasib","RAS(ON) inhibitor","Ph3",
  ["MRK","BMY","PFE","AZN"],"The only scaled RAS franchise. Merck talks collapsed on price in 2026."),
 ("ALNY","Alnylam",30.23,3.31,"Rare/Cardio","Amvuttra","RNAi vs. TTR","Commercial",
  ["NVS","RHHBY","PFE","REGN"],"Platform + commercial ATTR. Down 47% y/y on a guidance cut — cheapest it has been."),
 ("INSM","Insmed",27.61,1.16,"Respiratory","Brinsupri","Oral DPP1 inhibitor","Commercial",
  ["MRK","GSK","AZN"],"Merck bought Verona for COPD at 34x. Insmed is the next respiratory asset of scale."),
 ("BBIO","BridgeBio",15.61,0.72,"Cardio/Rare","Attruby","TTR stabiliser","Commercial",
  ["PFE","BMY","AZN"],"Direct Vyndaqel replacement for Pfizer. EV exceeds mcap — royalty stack on top."),
 ("ARWR","Arrowhead",12.53,1.60,"Cardiometabolic","Redemplo","RNAi vs. apoC-III","Commercial",
  ["NVO","LLY","NVS","AZN"],"Cardiometabolic RNAi platform; commercial in US and Germany."),
 ("MDGL","Madrigal",11.73,0.84,"Liver/Metabolic","Rezdiffra","THR-beta agonist","Commercial",
  ["NVO","AZN","RHHBY","LLY"],"Only approved MASH drug, >50k patients. Roche and Novo both bought MASH Ph3 assets."),
 ("AXSM","Axsome",11.19,0.32,"CNS","Auvelity","NMDA / sigma-1","Commercial",
  ["BMY","JNJ","ABBV","BIIB"],"CNS commercial platform. J&J paid $14.6B for Intra-Cellular on the same logic."),
 ("SMMT","Summit Therapeutics",10.65,0.69,"Oncology","Ivonescimab","PD-1 x VEGF bispecific","Ph3",
  ["MRK","BMY"],"The literal Keytruda-successor modality. Carries a going-concern warning at a $10.7B cap."),
 ("CYTK","Cytokinetics",10.31,1.70,"Cardio","Myqorzo","Cardiac myosin inhibitor","Commercial",
  ["BMY","NVS","JNJ"],"Camzyos competitor. BMS could buy the thing eating its own HCM franchise."),
 ("PRAX","Praxis Precision",10.85,1.40,"CNS","Ulixacaltamide","T-type Ca blocker","Ph3",
  ["ABBV","JNJ","BIIB","TAK"],"Essential tremor Ph3 + Breakthrough-designated SCN2A ASO. Up 892% y/y."),
 ("KYMR","Kymera",10.07,1.50,"Immunology","KT-621","Oral STAT6 degrader","Ph2",
  ["SNY","REGN","ABBV","PFE"],"An oral Dupixent. The single most obvious defensive buy for Sanofi/Regeneron."),
 ("IONS","Ionis",9.66,2.10,"Rare/Cardio","Tryngolza","ASO vs. apoC-III","Commercial",
  ["NVS","BIIB","AZN","RHHBY"],"ASO platform with three commercial assets. Long-standing Biogen partner."),
 ("PCVX","Vaxcyte",8.64,2.51,"Vaccines","VAX-31","31-valent pneumococcal","Ph3",
  ["MRK","PFE","GSK"],"Gardasil and Prevnar-13 both roll off. OPUS-1 topline Q4-2026 is the catalyst."),
 ("IMVT","Immunovant",8.64,0.80,"Immunology","IMVT-1402","Anti-FcRn mAb","Ph3",
  ["JNJ","NVS","SNY"],"Multi-indication FcRn. Roivant-controlled, which complicates but does not block."),
 ("RYTM","Rhythm Pharmaceuticals",7.95,0.33,"Metabolic","Imcivree","MC4R agonist","Commercial",
  ["NVO","LLY","PFE"],"Rare obesity beachhead for anyone who missed the GLP-1 wave."),
 ("SRRK","Scholar Rock",6.40,0.49,"Neuromuscular","Apitegromab","Anti-myostatin","Ph3",
  ["BIIB","NVS","RHHBY"],"FDA decision due by 30 Sep 2026 — the nearest hard catalyst in the universe."),
 ("TVTX","Travere",5.86,0.49,"Rare/Renal","Filspari","Dual ETA/AT1","Commercial",
  ["NVS","AZN","RHHBY"],"IgAN franchise; company has signalled >$3B peak. Novartis is building renal."),
 ("CELC","Celcuity",4.50,0.75,"Oncology","Revtorpyk","Pan-PI3K/mTOR","Commercial",
  ["PFE","NVS","AZN"],"Approved Jul-2026, launching Q3. Direct Ibrance-adjacent breast-cancer asset."),
 ("DNLI","Denali",3.91,0.94,"CNS/Rare","Avlayah","BBB-crossing ERT","Commercial",
  ["BIIB","TAK","SNY","BMY"],"BMS said out loud it wants blood-brain-barrier-penetrant neuro. This is the platform."),
 ("VKTX","Viking Therapeutics",3.87,0.50,"Obesity","VK2735","Dual GLP-1/GIP","Ph3",
  ["PFE","AZN","RHHBY","MRK"],"Ph3 fully enrolled. Pfizer paid >$10B for Metsera at Ph2b."),
 ("GPCR","Structure Therapeutics",3.87,1.34,"Obesity","Aleniglipron","Oral GLP-1RA","Ph3",
  ["PFE","AZN","NVS","MRK"],"Oral small-molecule GLP-1. Analyst peak-sales estimate $3.8B."),
 ("NUVB","Nuvation Bio",2.25,0.66,"Oncology","Ibtrozi","ROS1 TKI","Commercial",
  ["PFE","AZN","NVS"],"Commercial precision-oncology bolt-on at a sub-$2.5B cap."),
 ("KURA","Kura Oncology",0.97,0.52,"Oncology","Komzifti","Menin inhibitor","Commercial",
  ["MRK","PFE","ABBV"],"Approved drug, $293M enterprise value. Trades at a fraction of cash-adjusted worth."),
 ("JANX","Janux",0.99,0.97,"Oncology","JANX007","Masked PSMA TCE","Ph1",
  ["MRK","BMY","JNJ"],"$24.6M enterprise value — the market ascribes essentially zero to the pipeline."),
 ("MPLT","MapLight",0.54,0.35,"CNS","ML-007C-MA","M1/M4 muscarinic","Ph2",
  ["BMY","JNJ","ABBV"],"Muscarinic schizophrenia — the Cobenfy modality. Down ~72% after a mixed Ph2."),
]

# ---------------------------------------------------------------------------
# POS AND VALUATION INPUTS, per target
#   pos_ta    -> therapeutic area key in pos.BIO_2011_2020
#   pos_phase -> development phase for the PoS calculation (differs from the
#                premium bucket: an asset with a BLA under review is "Filed" for
#                PoS but still prices in the Ph3 premium bucket)
#   mods      -> PoS modifiers, see pos.MODIFIERS
#   peak      -> peak annual sales, $M. ESTIMATED BY ME unless noted. This is the
#                weakest input in the whole model: a real desk would take these
#                from FactSet or Evaluate consensus. Commercial-stage peaks are
#                scaled off reported TTM revenue; clinical-stage default to the
#                area median from Tendler et al. 2026 where I have no basis.
# ---------------------------------------------------------------------------
ASSET = {
 "RVMD": ("Solid tumor",   "Ph3",  ("lead_indication","genetic_evidence","biomarker_select"), 4000),
 "ALNY": ("Cardiovascular","Commercial", (),                                                  7000),
 "INSM": ("Respiratory",   "Commercial", (),                                                  5000),
 "BBIO": ("Cardiovascular","Commercial", (),                                                  3500),
 "ARWR": ("Metabolic",     "Commercial", (),                                                  1500),
 "MDGL": ("Metabolic",     "Commercial", (),                                                  4000),
 "AXSM": ("Psychiatry",    "Commercial", (),                                                  2500),
 "SMMT": ("Solid tumor",   "Ph3",  ("lead_indication","biomarker_select","mab"),              6000),
 "CYTK": ("Cardiovascular","Commercial", (),                                                  3000),
 "PRAX": ("Neurology",     "Filed",("lead_indication",),                                      1200),
 "KYMR": ("Immunology",    "Ph2",  ("lead_indication","genetic_evidence"),                    3000),
 "IONS": ("Cardiovascular","Commercial", (),                                                  3000),
 "PCVX": ("Vaccines",      "Ph3",  ("lead_indication",),                                      3000),
 "IMVT": ("Immunology",    "Ph3",  ("lead_indication","mab"),                                 2500),
 "RYTM": ("Metabolic",     "Commercial", (),                                                  1000),
 "SRRK": ("Neurology",     "Filed",("lead_indication","rare_disease","mab"),                  1200),
 "TVTX": ("Rare disease",  "Commercial", (),                                                  3000),
 "CELC": ("Solid tumor",   "Commercial", (),                                                  1500),
 "DNLI": ("Rare disease",  "Commercial", (),                                                   800),
 "VKTX": ("Metabolic",     "Ph3",  ("lead_indication",),                                      3000),
 "GPCR": ("Metabolic",     "Ph3",  ("lead_indication",),                                      3800),  # analyst consensus
 "NUVB": ("Solid tumor",   "Commercial", (),                                                   800),
 "JANX": ("Solid tumor",   "Ph1",  ("lead_indication",),                                      1000),
 "KURA": ("Heme-oncology", "Commercial", (),                                                   700),
 "MPLT": ("Psychiatry",    "Ph2",  ("lead_indication",),                                      1500),
}

TRAINED = POS.load_trained()   # None until the user runs pos_train.py

# ---------------------------------------------------------------------------
# MODEL
# ---------------------------------------------------------------------------
def urgency(pct, peak_yr):
    """0-100. 70% weight on exposure depth, 30% on how soon it lands."""
    exposure = min(pct / 75.0, 1.0) * 100
    span = WINDOW_END - WINDOW_START
    proximity = max(0.0, 1 - (min(max(peak_yr, WINDOW_START), WINDOW_END) - WINDOW_START) / span) * 100
    return round(0.70 * exposure + 0.30 * proximity, 1)

acquirers = []
for (name, tk, rev, risk, nd, ebitda, pf, yr, conf, note) in ACQ:
    pf_nd = nd + pf
    cap = max(0.0, TARGET_LEVERAGE * ebitda - pf_nd)
    pct = risk / rev * 100
    acquirers.append({
        "name": name, "ticker": tk, "rev": rev, "at_risk": risk,
        "pct_at_risk": round(pct, 1), "net_debt": nd, "pf_net_debt": round(pf_nd, 2),
        "ebitda": ebitda, "lev": round(nd / ebitda, 2) if ebitda else None,
        "pf_lev": round(pf_nd / ebitda, 2) if ebitda else None,
        "firepower": round(cap, 1), "peak_yr": yr,
        "urgency": urgency(pct, yr), "conf": conf, "note": note,
        # coverage: can firepower replace the revenue at risk, at precedent multiples?
        "coverage": round(cap / risk, 2) if risk else None,
    })

u_med = sorted(a["urgency"] for a in acquirers)[len(acquirers) // 2]
f_med = sorted(a["firepower"] for a in acquirers)[len(acquirers) // 2]
for a in acquirers:
    hi_u, hi_f = a["urgency"] >= u_med, a["firepower"] >= f_med
    a["quadrant"] = ("Must buy, can buy" if hi_u and hi_f else
                     "Must buy, can't buy" if hi_u else
                     "Can buy, needn't"   if hi_f else
                     "Sidelined")

import math

def size_factor(mcap):
    """Premiums compress as deal size rises — observable in the 2024->2026 tape
    (median 76.8% -> 40.2% as median deal size tripled). Flat below $5B,
    tapering to a 0.50x floor for mega-caps."""
    if mcap <= 5.0:
        return 1.0
    return max(0.50, 1 - 0.15 * math.log2(mcap / 5.0))

BY_TK = {a["ticker"]: a for a in acquirers}

targets = []
for (tk, name, mcap, cash, ta, asset, mech, phase, fits, thesis) in TGT:
    base = PREM[phase]
    prem = base * size_factor(mcap)
    ev = mcap - cash
    takeout = mcap * (1 + prem)
    fitted = [BY_TK[f] for f in fits if f in BY_TK]

    # 1. DEMAND — how badly do this asset's natural buyers need revenue? (40%)
    demand = sum(a["urgency"] for a in fitted) / len(fitted) if fitted else 0.0
    # 2. MATERIALITY — is it big enough to move the needle on those cliffs? (40%)
    #    An asset is fully material once its takeout cost reaches 40% of the
    #    average revenue hole it is being bought to fill.
    avg_hole = sum(a["at_risk"] for a in fitted) / len(fitted) if fitted else 0.0
    materiality = min(takeout / (0.40 * avg_hole), 1.0) * 100 if avg_hole else 0.0
    # 3. FUNDABILITY — can any natural buyer actually write the cheque? (20%)
    capable = [a["ticker"] for a in fitted if a["firepower"] >= takeout]
    fundability = min(len(capable) / 2.0, 1.0) * 100

    fit = round(0.40 * demand + 0.40 * materiality + 0.20 * fundability, 1)

    # --- PoS and rNPV -------------------------------------------------------
    pos_ta, pos_phase, mods, peak = ASSET[tk]
    fv, p_success, detail = POS.fair_value(pos_ta, pos_phase, mods,
                                           peak_override=peak, trained=TRAINED)
    # WHAT THIS RATIO IS, AND ISN'T.
    # rNPV here values ONE asset, on a lead-indication basis, over a single
    # exclusivity window. It is not a target price. Read it as: what share of the
    # precedent-multiple takeout price is explained by the lead asset alone?
    # High coverage -> you are buying a product. Low coverage -> you are buying a
    # platform, a pipeline, or optionality, and the lead asset does not justify
    # the price on its own. That is a statement about WHAT you are paying for,
    # not a claim that the market is wrong.
    cover = round(fv / takeout * 100, 1) if takeout > 0 else None

    targets.append({
        "pos": round(p_success * 100, 1), "pos_ta": pos_ta, "pos_phase": pos_phase,
        "mods": list(mods), "peak": peak, "rnpv": round(fv, 2), "cover": cover,
        "pos_capped": detail.get("uplift_capped", False),
        "ticker": tk, "name": name, "mcap": mcap, "cash": cash, "ev": round(ev, 2),
        "ta": ta, "asset": asset, "mech": mech, "phase": phase,
        "premium": round(prem * 100, 1), "takeout": round(takeout, 2),
        "fits": fits, "capable": capable, "demand": round(demand, 1),
        "materiality": round(materiality, 1), "fundability": round(fundability, 1),
        "fit": fit, "thesis": thesis,
    })

acquirers.sort(key=lambda a: -a["urgency"])
targets.sort(key=lambda t: -t["fit"])

out = {
    "asof": "2026-08-17",
    "params": {"target_leverage": TARGET_LEVERAGE, "window": [WINDOW_START, WINDOW_END],
               "premiums": PREM, "u_med": u_med, "f_med": f_med},
    "acquirers": acquirers, "targets": targets,
    "totals": {
        "rev": round(sum(a["rev"] for a in acquirers), 1),
        "at_risk": round(sum(a["at_risk"] for a in acquirers), 1),
        "firepower": round(sum(a["firepower"] for a in acquirers), 1),
        "takeout_universe": round(sum(t["takeout"] for t in targets), 1),
        # Partner double-counts removed for the PORTFOLIO figure only. Each company
        # genuinely loses its own line, but three franchises are booked twice across
        # the cohort: Pfizer's Eliquis alliance revenue ($7.96B) derives from BMS's
        # gross Eliquis sales; Merck's Lynparza alliance revenue ($1.45B) from AZ's;
        # Regeneron's Sanofi collaboration revenue ($5.9B) from Sanofi's Dupixent.
        "double_count": 15.3,
        "n_targets": len(targets),
    },
}
out["totals"]["at_risk_dedup"] = round(out["totals"]["at_risk"] - out["totals"]["double_count"], 1)
out["totals"]["pct_at_risk"] = round(out["totals"]["at_risk"] / out["totals"]["rev"] * 100, 1)
out["totals"]["pct_at_risk_dedup"] = round(out["totals"]["at_risk_dedup"] / out["totals"]["rev"] * 100, 1)

with open("data.json", "w") as f:
    json.dump(out, f, indent=1)

print(f"{'':22}{'%risk':>7}{'urg':>6}{'fire$B':>8}{'cov':>6}  quadrant")
for a in acquirers:
    print(f"{a['name']:22}{a['pct_at_risk']:>7}{a['urgency']:>6}{a['firepower']:>8}{a['coverage']:>6}  {a['quadrant']}")
print(f"\nAggregate: ${out['totals']['at_risk']}B at risk ({out['totals']['pct_at_risk']}% of "
      f"${out['totals']['rev']}B) vs ${out['totals']['firepower']}B firepower at {TARGET_LEVERAGE}x")
print(f"Target universe: {len(targets)} names, ${out['totals']['takeout_universe']}B at precedent premiums\n")
print(f"{'':24}{'phase':>12}{'mcap':>8}{'takeout':>9}{'fit':>6}")
for t in targets[:12]:
    print(f"{t['name']:24}{t['phase']:>12}{t['mcap']:>8}{t['takeout']:>9}{t['fit']:>6}")

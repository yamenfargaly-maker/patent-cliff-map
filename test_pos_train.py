"""
Smoke test for pos_train.py — proves the pipeline runs end to end without needing
network access, by generating synthetic trials with a KNOWN signal and checking
the model recovers it.

Synthetic ground truth: advancement probability depends on phase, therapeutic
area, randomisation and enrollment. If the CV AUC comes back near 0.5 the
pipeline is broken; if it recovers the planted ranking, the plumbing is sound.

    python3 test_pos_train.py
"""
import numpy as np, pandas as pd
import pos_train as P

RNG = np.random.default_rng(7)
N = 9000

TA_POOL = {
    "Solid tumor":   ("lung carcinoma", 0.55),
    "Heme-oncology": ("acute myeloid leukemia", 0.75),
    "Neurology":     ("alzheimer disease", 0.50),
    "Psychiatry":    ("major depressive disorder", 0.60),
    "Metabolic":     ("type 2 diabetes", 0.95),
    "Immunology":    ("rheumatoid arthritis", 0.85),
    "Cardiovascular":("heart failure", 0.45),
    "Infectious":    ("influenza", 0.90),
}
PHASE_BASE = {"PHASE1": 0.52, "PHASE2": 0.29, "PHASE3": 0.58}
SPONSORS = [f"sponsor{i:03d}" for i in range(180)]


def synth():
    rows = []
    for i in range(N):
        ta = RNG.choice(list(TA_POOL))
        cond, ta_mult = TA_POOL[ta]
        phase = RNG.choice(list(PHASE_BASE), p=[0.42, 0.38, 0.20])
        randomized = RNG.random() < 0.65
        enroll = int(np.exp(RNG.normal(4.6, 1.3)))
        sponsor = RNG.choice(SPONSORS)
        big = int(sponsor[-3:]) < 25          # 25 "large" sponsors
        p = PHASE_BASE[phase] * ta_mult
        p *= 1.22 if randomized else 0.85
        p *= 1.18 if enroll > 200 else 0.92
        p *= 1.15 if big else 1.0
        p = float(np.clip(p, 0.02, 0.95))
        advanced = RNG.random() < p
        drug = f"cmpd-{i:05d}"
        rows.append(dict(nct_id=f"NCT{i:08d}", phase=phase,
                         start_date=f"{RNG.integers(2008, 2021)}-06-01",
                         completion_date=None, overall_status="COMPLETED",
                         enrollment=enroll, number_of_arms=2 + int(randomized),
                         allocation="RANDOMIZED" if randomized else "NON_RANDOMIZED",
                         masking="DOUBLE" if randomized else "NONE",
                         primary_purpose="TREATMENT", study_type="INTERVENTIONAL",
                         sponsor=sponsor, agency_class="INDUSTRY",
                         conditions=cond, drugs=drug, n_primary=1,
                         _advanced=advanced))
        # a program that advanced gets a registered next-phase trial, which is
        # exactly the signal build_dataset() reconstructs
        if advanced:
            nxt = {"PHASE1": "PHASE2", "PHASE2": "PHASE3", "PHASE3": "PHASE4"}[phase]
            rows.append(dict(rows[-1], nct_id=f"NCT9{i:07d}", phase=nxt,
                             start_date=f"{RNG.integers(2010, 2022)}-06-01"))
    return pd.DataFrame(rows).drop(columns=["_advanced"])


def main():
    print("=" * 74)
    print("SMOKE TEST — pos_train.py on synthetic data with a planted signal")
    print("=" * 74)
    df = synth()
    print(f"\ngenerated {len(df):,} synthetic trial records")

    ds = P.build_dataset(df, censor_year=2021)
    assert len(ds) > 1000, "dataset collapsed"
    assert set(ds["advanced"].unique()) == {0, 1}, "labels not binary"
    print(f"  label base rate {ds['advanced'].mean():.3f}")

    X, tas = P.featurize(ds)
    assert list(X.columns) == P.FEATS, f"feature mismatch: {list(X.columns)}"
    assert not X.isna().any().any(), "NaNs in feature matrix"
    print(f"  featurized: {X.shape[0]:,} x {X.shape[1]} — {', '.join(P.FEATS)}")

    model, X, tas, auc, brier, oof = P.train(ds)

    print("\n" + "=" * 74)
    ok = True
    if auc < 0.60:
        print(f"FAIL  CV AUC {auc:.3f} — pipeline is not recovering the planted signal"); ok = False
    else:
        print(f"PASS  CV AUC {auc:.3f} — model recovers the planted signal")

    # does it recover the planted therapeutic-area ordering?
    planted = {k: v[1] for k, v in TA_POOL.items()}
    obs = ds.groupby("ta")["advanced"].mean().to_dict()
    common = [t for t in planted if t in obs]
    pr = [planted[t] for t in common]; ob = [obs[t] for t in common]
    rank_p = sorted(range(len(pr)), key=lambda i: pr[i])
    rank_o = sorted(range(len(ob)), key=lambda i: ob[i])
    conc = sum(1 for a, b in zip(rank_p, rank_o) if a == b)
    n = len(common)
    d2 = sum((rank_p.index(i) - rank_o.index(i)) ** 2 for i in range(n))
    rho = 1 - 6 * d2 / (n * (n * n - 1))
    print(f"{'PASS' if rho > 0.7 else 'FAIL'}  therapeutic-area rank correlation rho={rho:.2f} "
          f"(planted vs recovered, n={n})")
    ok = ok and rho > 0.7

    if brier > ds["advanced"].mean() * (1 - ds["advanced"].mean()):
        print(f"WARN  Brier {brier:.4f} no better than the base rate")
    else:
        print(f"PASS  Brier {brier:.4f} beats the base-rate benchmark")

    print("=" * 74)
    print("PIPELINE OK — safe to run against real data" if ok else "PIPELINE BROKEN")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

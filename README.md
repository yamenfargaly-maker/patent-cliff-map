# The 2030 Patent Cliff Map

Which large-cap pharma companies have to buy growth before 2032, which ones can afford to, and what is left to buy.

**[→ Live dashboard](patent-cliff-map.html)** · **[→ Memo](MEMO.md)**

Nineteen large-cap pharma companies lose **$293.2B of annual revenue** to patent expiry between 2027 and 2032 — 32.3% of their combined FY2025 revenue, net of partner double-counts. They hold roughly **$520B of debt capacity** at a 3.0× leverage ceiling. The aggregate covers the hole 1.77×; the distribution does not. Amgen, GSK and Pfizer carry 16% of the industry's exposure against 8% of its firepower.

**Every figure has been through an adversarial audit against primary filings.** The audit changed the conclusions — see §8 of the memo for the full list of what moved and why. Confidence is flagged per company; where a date genuinely cannot be established from disclosure (Roche, Novartis), it is published as unknown rather than estimated.

## What's here

| File | What it is |
|---|---|
| `model.py` | The model. Acquirer urgency, BD firepower, target fit scoring. All inputs inline and commented. |
| `build.py` | Renders `data.json` into the self-contained dashboard. |
| `data.json` | Model output. |
| `patent-cliff-map.html` | Interactive dashboard — quadrant map, exposure and firepower charts, sortable target screen. No dependencies, no network calls. |
| `MEMO.md` | Analyst memo — conclusions, methodology, what the audit changed, and the PoS layer. |
| `pos.py` | Probability-of-success priors (BIO 2011–2020) + the rNPV engine. Run it to print the PoS matrix. |
| `pos_train.py` | Trains an empirical PoS model on AACT / ClinicalTrials.gov. **You run this** — needs network. |
| `test_pos_train.py` | Synthetic-data smoke test proving the training pipeline works before you point it at real data. |

```bash
python3 model.py && python3 build.py && open patent-cliff-map.html

python3 pos.py              # print the PoS matrix and the modifier-damping demo
python3 test_pos_train.py   # verify the training pipeline (no network needed)
```

### Training the empirical PoS model

```bash
pip install pandas scikit-learn psycopg2-binary requests

# Option A — AACT (richer). Free account: aact.ctti-clinicaltrials.org/users/sign_up
export AACT_USER=... AACT_PASS=...
python3 pos_train.py --source aact

# Option B — ClinicalTrials.gov API v2, no account needed
python3 pos_train.py --source ctgov --max-pages 400
```

Writes `pos_model.json`; `pos.py` picks it up automatically and blends it with the published priors. It blends rather than replaces on purpose — the registry label is biased upward by right-censoring, unregistered follow-on trials, and silent discontinuation. The script prints its own observed rates against the BIO priors and flags a censoring leak if Phase 2→3 lands more than 40% high. **Trust the cross-area ranking, not the levels.**

## Method

**Urgency** = 0.70 × (share of FY2025 revenue expiring 2027–32, capped at 75%) + 0.30 × proximity of the peak expiry year within the window.

**Firepower** = max(0, 3.0 × LTM EBITDA − pro-forma net debt), where 3.0× is the leverage an A−/BBB+ issuer can defend, and pro-forma adjusts for deals announced but not closed as of the 30 June 2026 balance sheets. EBITDA is stated before acquired IPR&D — on strict GAAP, 2026 leverage is undefined for the heaviest dealmakers (Merck expensed $14.7B of acquired IPR&D in H1, Gilead $11.3B).

**Aggregate exposure is de-duplicated** by $15.3B: Pfizer's Eliquis alliance revenue derives from BMS's gross sales, Merck's Lynparza from AstraZeneca's, and Regeneron's collaboration revenue from Sanofi's Dupixent. Per-company lines are correct as shown.

**Probability of success** comes from BIO/Informa/QLS 2011–2020 phase transitions, drift-adjusted 0.85× for the industry decline to 2023. Modifiers (lead indication, biomarker preselection, genetic target validation, rare disease, modality) are combined in **log-odds space with 0.55 damping and a 3.5× cap** — they are correlated and each is reported marginally, so naive multiplication produces probabilities above 1.0.

**rNPV** carries clinical risk entirely in the PoS term and discounts at a WACC-style 10%. Using a venture-style 20–40% rate *and* probability weights double-counts risk — the most common error in published biotech valuation. The rNPV values one asset, one indication, one exclusivity window, so it is reported as **coverage of the takeout price**, not as a price target.

**Target fit** = 40% weighted-average urgency of the asset's natural acquirers, 40% materiality (is the takeout large enough to matter against those cliffs), 20% fundability (can any natural buyer write the cheque). Takeout applies the median precedent premium for the target's phase — rebuilt on a single basis (prior-day or unaffected close), since mixing prior-close and VWAP premiums overstates every clinical bucket by 6–10 points.

## Sourcing

Company 10-K and 20-F patent tables, Q2-2026 earnings releases and balance sheets, FDA Orange Book exclusivity data, and a hand-built sample of precedent transactions ≥$500M announced January 2024 – August 2026. Every figure is attributed in `MEMO.md`. Estimates and thin sourcing are flagged per company rather than smoothed over — read §7 ("What this model gets wrong") and §8 ("What the audit changed") first. Those two sections are the point.

No published benchmark for phase-stratified takeover premiums exists for this period — not from Stifel, Leerink, Evaluate, DealForma, PitchBook or LSEG. This analysis is the estimate, not a check against a standard.

Data as of 17 August 2026. Independent work. Not investment advice.

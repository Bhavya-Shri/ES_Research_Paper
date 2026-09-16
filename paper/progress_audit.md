# Progress audit versus the working roadmap

**Date:** 16 Sep 2026  
**Roadmap:** `paper/working_roadmap.md`  
**Background plan:** `paper/publishing_audit_and_roadmap.md` (13 Sep; still the venue/novelty strategy)  
**Paper walkthrough:** `paper/walkthrough_notes.md` (explains the *old* S1-only draft)

This file is the status snapshot after Phase F Step 14 (venue lock). It is not a substitute for the original publishing audit. Portal submit waits for the DAFx 2027 CFP.

**How this file is kept:** after every stretch, update *this* file before calling the step done, then commit it with the code/results and push `main`.

---

## 0. Where we are

We are in **version C** of the publishing plan: three systems, matched LUFS vs digital \(L_{Aeq}\), with a **reversal**.

| System | What it is | \(\Delta L_{Aeq}\) matched LUFS | Dual \(\Delta\)LUFS matched \(L_{Aeq}\) | \(\Delta L_{Ceq}\) matched LUFS |
|---|---|---|---|---|
| **S0** | Frequency-flat gain | 0 | 0 | 0 |
| **S1** | Bass-first heuristic (−12 dB shelf + harmonics + mid target 78) | **+1.17 dB** (worse than S0) | **−1.17 dB** | **−0.58 dB** (better than S0) |
| **S2** | Metric-aligned (`ProposedConfig.aligned()`: no shelf, no harmonics, mid target **72**) | **−0.27 dB** (better than S0) | **+0.27 dB** | **+0.06 dB** (slightly worse than S0) |

**Contribution sentence (locked by Step 7):**  
S1 loses at matched LUFS (+1.17 dB); S2 reverses the sign (−0.27 dB, bootstrap 95% CI [−0.45, −0.11], two-sided Wilcoxon \(p=0.001\)), so attenuation spent where \(w_A\) is large beats flat gain on the digital \(L_{Aeq}\) proxy. The margin is modest. **Do not retune S1 or S2 knobs.**

S1 remains the failed heuristic on purpose. S2 knobs are frozen (`sub_atten_db=0`, `harmonic_mix=0`, `mid_target_dba=72`).

**Paper vs data:** `main.tex` is version C. Claim vocabulary was searched; remaining hits are denials or calibrated-proxy disclaimers. Related work also cites US~11006215 and AES TD1008. First venue is **DAFx 2027** (Cremona, 24–27 Aug 2027). Compiled locally to `paper/main.pdf` (9 pages, IEEEtran + BibTeX, no undefined citations). No Overleaf login in this environment; Tectonic is XeTeX so Times (`ptm`) falls back to Latin Modern. Overleaf `pdflatex` will use Times. The old fpdf file `Frequency_Adaptive_Audio_Limiting.pdf` is removed so it cannot be submitted by mistake.

**Git:** https://github.com/Bhavya-Shri/ES_Research_Paper.git — branch `main`. This file is updated after every stretch and pushed with that stretch.

---

## 1. Roadmap scorecard

| Step | Roadmap phase | Status | Evidence |
|---|---|---|---|
| 0 Freeze S1 | A | **Done** | `results/frozen/draft-negative-v1/` |
| 1 \(W_A/W_K\) figure | B | **Done** | `exposure_dsp/kweighting.py`; `paper/figures/weighting_ratio.png`; A@40 Hz ≈ −34.5 dB, K@40 Hz ≈ −5.6 dB |
| 2 Stats on S1 | B | **Done** | `results/tables/stats_s1.json`; n=20 mean +1.17 dB, CI [0.60, 1.83], two-sided \(p=3.9\times10^{-4}\) |
| 3 Citations | B | **Done** | Chen et al. 2023 (not “Liang”), US 9980028, US 6826515, Fathima 2026 in `references.bib` and §2 |
| 4 Retitle | B | **Done** (retitled again in Step 11) | *Metric-Aligned Frequency Allocation for Personal-Audio Dose Limiting* |
| 5 S2 config | C | **Done** | `ProposedConfig.aligned()`; S1 defaults unchanged |
| 6 Experiment S1+S2 | C | **Done** | `results/tables/comparison.csv`, `comparison_s1_s2.csv`; S1 mean still +1.174 dB vs frozen |
| 7 Sign gate | C | **Done** | Reversal; S2 knobs frozen; story recorded in `working_roadmap.md` |
| 8 Three-way figures | C | **Done** | `paper/figures/matched_loudness_s1_s2.png`; `perclip_table.tex` means +1.17 / −0.27 dB |
| 9 Stats S2 | C | **Done** (required part ran with Step 7) | `results/tables/stats_s2.json`; CI excludes 0. Optional paired S1 vs S2 test **not** implemented |
| **10 C-weighting** | **D** | **Done** | `exposure_dsp/cweighting.py`; `stats_cweight.json`; S1 ΔLCeq −0.58 dB, S2 +0.06 dB; both hypotheses held |
| **11 Rewrite `main.tex`** | **E** | **Done** | version C; S0/S1/S2; S2 figure; C paragraph; modest margin |
| **12 Compile / claim check** | **E** | **Done** | `paper/main.pdf` 9 pages; claim hits qualified; stale fpdf PDF removed |
| **13 IEEE Xplore + AES close-out** | **F** | **Done** | no clone of the matched LUFS/\(L_{Aeq}\) test; added US~11006215 and AES TD1008 |
| **14 Venue lock** | **F** | **Done** (portal submit waits) | **DAFx 2027** locked; do not rush ICASSP 2027 4+1 |

**Do not skip to hardware, extra clips, MUSHRA, or ML.** Those wait until after Step 12.

---

## 2. What has been done (detail)

### 2.1 Frozen S1 record (Step 0)

- `results/frozen/draft-negative-v1/tables/` holds the original S1 `comparison.csv`, `experiment.json`, `ablation.csv`, `param_sweep.json`.
- `ProposedConfig` defaults are still `sub_atten_db=-12`, `mid_target_dba=78`, `harmonic_mix=1`.
- Re-running the comparison did **not** change the S1 mean: still **+1.174 dB**.

### 2.2 Phase B (Steps 1–4) — tighter science on the old result

- K-weighting module and two-panel ratio figure (mechanism of the S1 loss).
- Wilcoxon + bootstrap on the 20 (and 16 real) S1 \(\Delta L_{Aeq}\) values; numbers are in the Results text.
- Related work now cites device algorithms so “H.870 is silent” is not “nobody has an algorithm.”
- Title no longer promises reduced exposure / loudness preservation.

**S1 numbers (matched LUFS \(\Delta L_{Aeq}\), proposed − flat):**

| Set | Mean | 95% CI | Two-sided Wilcoxon |
|---|---|---|---|
| n=20 | +1.17 dB | [0.60, 1.83] | \(p=3.9\times10^{-4}\) |
| 16 real | +0.92 dB | [0.47, 1.39] | \(p=0.002\) |
| 6 bass loops | +1.98 dB | [1.69, 2.33] | \(p=0.031\) |

Counts n=20: 12 worse by >0.05 dB, 6 ties, 2 better. One-sided H2 (\(\Delta<0\)) is rejected for S1.

### 2.3 Phase C experiment (Steps 5–9)

- S2 is a **config**, not a new architecture.
- `experiment.py` processes `proposed` (S1) and `aligned` (S2); each is matched to flat gain on LUFS and on \(L_{Aeq}\). S2 flat-gain rows are named `aligned_gain_matched_loudness` / `aligned_gain_matched_exposure`.
- Ablation was **not** re-run on the S2 pass (`include_ablation=False`). The frozen S1 ablation table still stands.
- Step 8: `python paper/make_figures.py` writes grouped bars (`matched_loudness_s1_s2.png`) and a four-column per-clip table. S1-only `matched_loudness_delta.png` is still generated. Regenerated means: S1 **+1.174 dB**, S2 **−0.267 dB**.
- Step 9 required: `python -m exposure_dsp stats` writes `stats_s1.json` + `stats_s2.json`. Optional paired S1 vs S2 Wilcoxon is **not** in `stats.py`.

**S2 numbers (matched LUFS \(\Delta L_{Aeq}\), aligned − flat):**

| Set | Mean | 95% CI | Two-sided Wilcoxon |
|---|---|---|---|
| n=20 | −0.27 dB | [−0.45, −0.11] | \(p=0.0012\) |
| 16 real | −0.30 dB | [−0.52, −0.11] | \(p=0.004\) |
| 6 bass loops | −0.57 dB | [−0.88, −0.26] | \(p=0.031\) |

Counts n=20: 11 better by >0.05 dB, 8 ties, 1 slightly worse. One-sided H2 (\(\Delta<0\)) is supported for S2 (\(p=6\times10^{-4}\)) and rejected for S1.

### 2.4 Phase D — C-weighting (Step 10)

- `exposure_dsp/cweighting.py`: IEC 61672 C, same IIR + RMS+offset pattern as A. Digital C at 40 Hz ≈ **−2.0 dB** (A ≈ −34.5 dB). Check passed.
- `lceq_proxy` in `metrics.py`. `python -m exposure_dsp cweight` re-processes S1/S2 in float and rebuilds LUFS-matched flats from `comparison.csv` gain (saved wavs are not used: PCM_16 peak-normalizes if \(|x|>1\)). A-deltas reproduced to **0.0 dB**. Knobs not retuned.
- Hypothesis (written before looking): S1 \(\Delta L_{Ceq} < \Delta L_{Aeq}\); S2 the opposite. **Both held.**

**Matched LUFS \(\Delta L_{Ceq}\) (processor − flat):**

| System | n=20 mean | 95% CI | Two-sided Wilcoxon | vs \(\Delta L_{Aeq}\) |
|---|---|---|---|---|
| S1 | **−0.58 dB** | [−0.94, −0.26] | \(p=1.0\times10^{-4}\) | A was **+1.17 dB** (sign flip) |
| S2 | **+0.06 dB** | [0.02, 0.12] | \(p=0.007\) | A was **−0.27 dB** (sign flip) |

S1 16-real \(\Delta L_{Ceq}\) −0.40 dB; S2 16-real +0.08 dB. Lesson: allocation is good for the meter you cut toward. Do not write this as a safety result.

### 2.5 What the paper file currently contains

`main.tex` is version C (Step 11):

- Title *Metric-Aligned Frequency Allocation for Personal-Audio Dose Limiting*; abstract keeps S1 +1.17\,dB failure and the modest S2 reversal.
- Intro contribution: matched test; S1 fails; allocation follows \(w_A\); S2 reversed the sign.
- Related work neighbours as of Step 11: Chen 2023, US~9980028, US~6826515, Fathima 2026. Step 13 added US~11006215 and AES TD1008.
- Methods: S0, S1, S2 as one architecture / two configs; \(W_A/W_K\) in the method; param table has both columns.
- Results: S1 figure kept; S2 grouped bars (`matched_loudness_s1_s2.png`); four-column `perclip_table.tex`; C-weighting; S1 ablation labelled as S1-only.
- Limitations: digital proxy; mid cut may hurt speech; no MUSHRA; modest S2 margin.
- Conclusion: design rule, not a new limiter.

**Compiled:** `paper/main.pdf` (9 pages, Tectonic). `render_pdf.py` is obsolete.

### 2.7 Step 12 claim search (`main.tex`)

| Phrase | Where | Disposition |
|---|---|---|
| SPL | Limitations | Kept as *does not report ear-level SPL* |
| hearing loss | Limitations | Kept as *does not show prevention of hearing loss* |
| architecture | Gap + param caption | Kept as *does not introduce / not a second architecture* |
| loudness-preservation | Results H1-S1 | Kept as *not supported as a loudness-preservation claim* |
| quality | figure filename | Renamed to `matched_exposure_lsd.png` |
| optimal | — | No hit in prose |
| adaptive | `references.bib` only | Fathima / PEAQ / MUSHRA titles; not our claim |

No leftover “loudness preservation succeeded” language. Numbers match `results/tables/` (S1 +1.17, S2 −0.27, C −0.58 / +0.06).

### 2.8 Step 13 literature close-out

Search method: web + Google Patents + AES public document pages + Scholar-style queries. No institutional IEEE Xplore login, so this is not a logged-in Xplore harvest.

**Queries (from `publishing_audit_and_roadmap.md` §8 Phase 7):**

- `"sound dose" AND (multiband OR frequency-selective) AND (headphone OR "personal listening")`
- `(LUFS OR BS.1770) AND (A-weighted OR LAeq) AND (limiter OR compressor)`
- AES: virtual bass + loudness; streaming loudness vs H.870 / EN 50332-3
- Patents: neighbours of US~9980028 / US~6826515
- Cited-by: Chen et al. 2023 (IJERPH) and ITU-T H.870

**Finding:** no clone of a **matched LUFS versus digital \(L_{Aeq}\) frequency-allocation test on music**. Personal sound-zone papers are not neighbours.

**Added (real neighbours, not clones):**

| Cite | What it is | Why it is not the test |
|---|---|---|
| US~11006215 (GN Hearing, 2021) | Multiband limiter in a hearing-protection device | Occupational HPD gain, not matched A vs K on music |
| AES TD1008 (Kean ed., 2021) | Streaming LUFS recs; notes H.870 / EN 50332-3 for portables | Distribution loudness, not an allocation algorithm |

**Looked at, not cited:** Cassidy ICASSP 2004 (loudness-model DRC); US~11268848 (later headset dosimetry, same family as US~6826515).

### 2.9 Step 14 venue lock (16 Sep 2026)

S2 reversed the sign. There is no listening test. §6 of the publishing audit says: aim a specialist conference with version C; do **not** wait for a coupler; do **not** aim TASLP / AES Journal.

**Locked primary: DAFx 2027** (30th International Conference on Digital Audio Effects), Politecnico di Milano campus, Cremona, 24–27 Aug 2027. Specialist audio audience (LUFS, virtual bass, weighting). Historical length ~8 pages. CFP not posted yet (DAFx 2026 was due 30 Mar 2026). Keep `IEEEtran` as the working manuscript; retarget the DAFx template when the CFP appears.

**Do not rush ICASSP 2027.** Deadline 23 Sep 2026 AoE (Kolkata 17:30 on 24 Sep). Format is 4 pages + optional 5th for references only. This draft is `\documentclass[journal]{IEEEtran}` with C-weighting, ablation, and the S1 failure story. A same-week 4-page cut would be a different paper. The S2 margin is −0.27 dB on a digital proxy with no listeners; that is a weak ICASSP AASP bet.

| Target | Window | Decision |
|---|---|---|
| DAFx 2027 | CFP expected ~Mar 2027; event 24–27 Aug 2027 | **Submit here** |
| ICASSP 2027 | 23 Sep 2026 AoE; 4+1 pages; Toronto May 2027 | Skip this cycle |
| IEEE SPL | Rolling; 4 pages + 1 refs | Only after a dedicated letter cut |
| WASPAA 2027 | Autumn 2027; typically 4+1; CFP early 2027 | Later if DAFx misses |
| Next AES convention | 6–10 pages; Nashville 161 closed 17 Jul 2026 | Later if a 2027 CFP appears first |
| INDICON 2026 / TENCON 2026 | Closed | — |

**Author checklist (source, 16 Sep):**

| Item | Status |
|---|---|
| Captions stand alone | Yes |
| No ear-level dB SPL claim | Yes (limitations deny it) |
| Claim hits (SPL, hearing loss, architecture, quality, optimal, adaptive) | Qualified or absent as claims |
| Numbers from `results/tables/` | Yes |
| Ethics / listeners | N/A (no listening test) |
| IEEE-style bibliography | Yes (`IEEEtran`) |
| Second author e-mail | **Missing** — add Bhavya's VIT address before the portal |
| Compiled IEEE/DAFx PDF | `paper/main.pdf` (9 pages; Tectonic XeTeX; Times fallback to Latin Modern) |
| Internal read (coauthor + outsider: “what is the contribution?”) | **User** — if they say “a new limiter,” rewrite |
| ORCID (ICASSP 2027 requires it; DAFx may not) | Get one anyway |

`cweighting_response.png` is now cited in the C-weighting results subsection.

### 2.6 Artifacts that exist (Steps 0–14)

| Artifact | Role |
|---|---|
| `exposure_dsp/kweighting.py` | BS.1770 K + \(W_A/W_K\) plot |
| `exposure_dsp/stats.py`, `cli.py` `stats` | S1 and S2 Wilcoxon/CI |
| `exposure_dsp/proposed.py` `ProposedConfig.aligned()` | S2 knobs |
| `exposure_dsp/experiment.py` | S1+S2 loop; `write_s1_s2_csv` |
| `results/tables/comparison.csv` | Live S1+S2 rows |
| `results/tables/comparison_s1_s2.csv` | Same comparison, extra copy |
| `results/tables/stats_s1.json`, `stats_s2.json` | Tests |
| `results/tables/experiment.json` | Means + frozen S2 knobs |
| `results/tables/ablation.csv`, `param_sweep.json` | Frozen S1 ablation/sweep (not refreshed for S2) |
| `results/frozen/draft-negative-v1/` | S1 snapshot |
| `paper/make_figures.py` | S1 + S2 plots and both table writers |
| `paper/figures/matched_loudness_s1_s2.png` | Grouped bars |
| `paper/figures/matched_exposure_lsd.png` | S1 dual match (LUFS / LSD) |
| `paper/perclip_table.tex` | S1 and S2 \(\Delta L_{Aeq}\) / \(\Delta\)LUFS |
| `paper/references.bib` | Chen2023, US9980028, US6826515, Fathima2026, US11006215, AESTD1008 |
| `exposure_dsp/cweighting.py` | IEC C IIR + analytic curve |
| `results/tables/stats_cweight.json`, `comparison_cweight.csv` | \(\Delta L_{Ceq}\) at matched LUFS |
| `paper/figures/cweighting_response.png` | Digital C vs IEC analytic |

**On GitHub:** code, paper tex/bib/figures, `results/tables/**`, `results/frozen/**`.  
**Not on GitHub (`.gitignore`):** `audio_in/*.wav`, `results/wavs`, `results/figures`, venv, `paper/_pdfdeps/`.

---

## 3. What must be done next (in order)

Venue is locked. Do not retune mid target 72. After each stretch, update this file and push.

### Immediate — portal submit (waits on DAFx CFP)

1. Compile on Overleaf **without** GitHub import (that is premium): upload `paper/overleaf_upload.zip` via **New Project → Upload Project**. Set compiler to pdfLaTeX if the Menu is not already. Local `paper/main.pdf` already exists (9 pages; Tectonic fonts are not Times).  
2. Add Bhavya's e-mail to the author block.  
3. Internal read: one coauthor, one outsider. If they say “a new limiter,” rewrite.  
4. When the DAFx 2027 CFP posts, copy into their template (likely ~8 pages, maybe double-blind) and submit.  
5. Do **not** cut a 4-page ICASSP version this week.

---

## 4. Explicitly later (blocked until Step 12)

- Extra Freesound clips  
- Headphone-EQ simulation  
- MUSHRA / classmates  
- HATS / IEC 60318-4  
- ML, more bands, better virtual bass, STM32  

---

## 5. Risks to keep in view while writing

| Risk | How it stands now |
|---|---|
| Overselling S2 | −0.27 dB is a real sign flip (CI excludes 0), not a large safety gain. Write it as alignment, not as a new limiter. |
| Title still sounds like a winning product | Version-C title is metric-aligned; the abstract still leads with S1’s +1.17\,dB failure. |
| Ablation not refreshed | Frozen S1 ablation is fine; do not imply S2 was ablated band-by-band unless you re-run it. |
| Chen vs “Liang 2023” | The IJERPH paper is Chen, Xue, Wang, Cai, Zhu (2023). Cite `Chen2023`. |
| Quality / SPL language | Still forbidden. Digital \(L_{Aeq}\) proxy only. |
| p-hacking S2 | Mid target 72 was frozen before the 20-clip mean. Leave it. |
| Stale PDF on GitHub | Old fpdf removed. Current IEEE PDF is `paper/main.pdf` (Tectonic). Overleaf `pdflatex` still preferred for Times fonts. |
| C-weighting oversell | S1 on C is a real sign flip (−0.58 dB); S2 on C is only +0.06 dB. Write meter-dependence, not “C is the right safety meter.” |
| Saved wavs vs tables | `save_wav` peak-normalizes if \|x\|>1. C-weighting used float re-process + CSV gains, not those wavs. |

---

## 6. Commands that regenerate the current numbers

```text
python -m exposure_dsp checks          # includes weighting-ratio figure
python -m exposure_dsp stats           # stats_s1.json + stats_s2.json from comparison.csv
python -m exposure_dsp experiment      # full S1+S2 comparison (slow; ablation on by default)
python paper/make_figures.py           # S1 + S2 grouped bars and perclip_table.tex
python -m exposure_dsp cweight         # stats_cweight.json from frozen knobs + CSV gains
```

S1 freeze (do not overwrite as the source of truth): `results/frozen/draft-negative-v1/`.

---

## 7. Next action

Portal submit waits for the DAFx CFP. Compile on Overleaf with **Upload Project** (`paper/overleaf_upload.zip`); GitHub import is premium. Add Bhavya's e-mail before the portal. Do not retune knobs. Do not cut a 4-page ICASSP version this week.

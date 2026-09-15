# Progress audit versus the working roadmap

**Date:** 16 Sep 2026  
**Roadmap:** `paper/working_roadmap.md`  
**Background plan:** `paper/publishing_audit_and_roadmap.md` (13 Sep; still the venue/novelty strategy)  
**Paper walkthrough:** `paper/walkthrough_notes.md` (explains the *old* S1-only draft)

This file is the status snapshot after Phase E Step 12 (claim check). It is not a substitute for the original publishing audit.

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

**Paper vs data:** `main.tex` is version C. Claim vocabulary was searched; remaining hits are denials or calibrated-proxy disclaimers. No `pdflatex` on this machine; the IEEEtran PDF is an Overleaf compile of `main.tex`. The old fpdf file `Frequency_Adaptive_Audio_Limiting.pdf` is removed so it cannot be submitted by mistake.

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
| **12 Compile / claim check** | **E** | **Done** (source check; no local `pdflatex`) | claim hits qualified; stale fpdf PDF removed; IEEE PDF is Overleaf |
| 13 IEEE Xplore + AES close-out | F | **Next** | web/patent pass only |
| 14 Venue + submit | F | Not started | |

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
- Related work unchanged in neighbours (Chen 2023, patents, Fathima); gap table is S0/S1/S2.
- Methods: S0, S1, S2 as one architecture / two configs; \(W_A/W_K\) in the method; param table has both columns.
- Results: S1 figure kept; S2 grouped bars (`matched_loudness_s1_s2.png`); four-column `perclip_table.tex`; C-weighting; S1 ablation labelled as S1-only.
- Limitations: digital proxy; mid cut may hurt speech; no MUSHRA; modest S2 margin.
- Conclusion: design rule, not a new limiter.

**Missing until Overleaf:** a compiled IEEEtran PDF. Compile `paper/main.tex` there. `render_pdf.py` is obsolete.

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

### 2.6 Artifacts that exist (Steps 0–10)

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
| `paper/references.bib` | Chen2023, US9980028, US6826515, Fathima2026 |
| `exposure_dsp/cweighting.py` | IEC C IIR + analytic curve |
| `results/tables/stats_cweight.json`, `comparison_cweight.csv` | \(\Delta L_{Ceq}\) at matched LUFS |
| `paper/figures/cweighting_response.png` | Digital C vs IEC analytic |

**On GitHub:** code, paper tex/bib/figures, `results/tables/**`, `results/frozen/**`.  
**Not on GitHub (`.gitignore`):** `audio_in/*.wav`, `results/wavs`, `results/figures`, venv, `paper/_pdfdeps/`.

---

## 3. What must be done next (in order)

Do these **in roadmap order**. Do not retune mid target 72 after seeing \(\Delta\). After each step, update this file and push.

### Immediate — Step 13 (next stretch)

IEEE Xplore + AES neighbour search (queries in `publishing_audit_and_roadmap.md` §8 Phase 7). Add anything that is a real neighbour. Compile `main.tex` on Overleaf when convenient; there is no local `pdflatex`.

### Then — Steps 13–14 (submit)

IEEE Xplore + AES neighbour search; pick a conference/AES venue (reversal story is clean enough). Do **not** wait for a coupler or listening test for the first submission.

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
| Stale PDF on GitHub | Old fpdf `Frequency_Adaptive_Audio_Limiting.pdf` removed. IEEE PDF = Overleaf `main.tex`. |
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

**Step 13.** When you say go: IEEE Xplore + AES close-out (queries in the 13 Sep publishing audit §8). Do not retune knobs. Compile `paper/main.tex` on Overleaf in parallel if you want a PDF.

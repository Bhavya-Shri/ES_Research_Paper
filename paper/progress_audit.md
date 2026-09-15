# Progress audit versus the working roadmap

**Date:** 15 Sep 2026  
**Roadmap:** `paper/working_roadmap.md`  
**Background plan:** `paper/publishing_audit_and_roadmap.md` (13 Sep; still the venue/novelty strategy)  
**Paper walkthrough:** `paper/walkthrough_notes.md` (explains the *old* S1-only draft)

This file is the status snapshot after Phase A–C through the three-way figures (Step 8). It is not a substitute for the original publishing audit.

---

## 0. Where we are

We are in **version C** of the publishing plan: three systems, matched LUFS vs digital \(L_{Aeq}\), with a **reversal**.

| System | What it is | Mean \(\Delta L_{Aeq}\) at matched LUFS |
|---|---|---|
| **S0** | Frequency-flat gain | Baseline (0 by construction) |
| **S1** | Bass-first heuristic (−12 dB shelf + harmonics + mid target 78) | **+1.17 dB** (worse than S0) |
| **S2** | Metric-aligned (`ProposedConfig.aligned()`: no shelf, no harmonics, mid target **72**) | **−0.27 dB** (better than S0) |

**Contribution sentence (locked by Step 7):**  
S1 loses at matched LUFS (+1.17 dB); S2 reverses the sign (−0.27 dB, bootstrap 95% CI [−0.45, −0.11], two-sided Wilcoxon \(p=0.001\)), so attenuation spent where \(w_A\) is large beats flat gain on the digital \(L_{Aeq}\) proxy. The margin is modest. **Do not retune S1 or S2 knobs.**

S1 remains the failed heuristic on purpose. S2 knobs are frozen (`sub_atten_db=0`, `harmonic_mix=0`, `mid_target_dba=72`).

**Paper vs data:** figures and `perclip_table.tex` now show S1 and S2. `paper/main.tex` still tells the **S1-only** story (plus Phase B citations, title, stats, and the \(W_A/W_K\) figure). It does **not** yet report S2. That rewrite is Step 11, after optional C-weighting (Step 10).

---

## 1. Roadmap scorecard

| Step | Roadmap phase | Status | Evidence |
|---|---|---|---|
| 0 Freeze S1 | A | **Done** | `results/frozen/draft-negative-v1/` |
| 1 \(W_A/W_K\) figure | B | **Done** | `exposure_dsp/kweighting.py`; `paper/figures/weighting_ratio.png`; A@40 Hz ≈ −34.5 dB, K@40 Hz ≈ −5.6 dB |
| 2 Stats on S1 | B | **Done** | `results/tables/stats_s1.json`; n=20 mean +1.17 dB; two-sided \(p=3.9\times10^{-4}\) |
| 3 Citations | B | **Done** | Chen et al. 2023 (not “Liang”), US 9980028, US 6826515, Fathima 2026 in `references.bib` and §2 |
| 4 Retitle | B | **Done** (may retitle again in Step 11) | *Metric Mismatch in Frequency-Selective Personal-Audio Limiting: A-Weighting versus BS.1770* |
| 5 S2 config | C | **Done** | `ProposedConfig.aligned()`; S1 defaults unchanged |
| 6 Experiment S1+S2 | C | **Done** | `results/tables/comparison.csv`, `comparison_s1_s2.csv`; S1 mean still +1.174 dB vs frozen |
| 7 Sign gate | C | **Done** | Reversal; S2 knobs frozen; story recorded in `working_roadmap.md` |
| **8 Three-way figures** | **C** | **Done** | `paper/figures/matched_loudness_s1_s2.png`; `perclip_table.tex` means +1.17 / −0.27 dB |
| 9 Stats S2 | C | **Done** (ran with Step 7) | `results/tables/stats_s2.json`; CI excludes 0 |
| 10 C-weighting | D | **Next** | no `cweighting.py` |
| 11 Rewrite `main.tex` | E | Not started as version C | Results still S1-only |
| 12 Compile / claim check | E | Not started | |
| 13 IEEE Xplore + AES close-out | F | Not started | web/patent pass only |
| 14 Venue + submit | F | Not started | |

**Do not skip to hardware, extra clips, MUSHRA, or ML.** Those wait until Step 12.

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

### 2.3 Phase C experiment (Steps 5–9)

- S2 is a **config**, not a new architecture.
- `experiment.py` processes `proposed` (S1) and `aligned` (S2); each is matched to flat gain on LUFS and on \(L_{Aeq}\). S2 flat-gain rows are named `aligned_gain_matched_loudness` / `aligned_gain_matched_exposure`.
- Ablation was **not** re-run on the S2 pass (`include_ablation=False`). The frozen S1 ablation table still stands.
- Step 8: `python paper/make_figures.py` now writes grouped bars (`matched_loudness_s1_s2.png`) and a four-column per-clip table. S1-only `matched_loudness_delta.png` is still generated. Regenerated means: S1 **+1.174 dB**, S2 **−0.267 dB**.

**S2 numbers (matched LUFS \(\Delta L_{Aeq}\), aligned − flat):**

| Set | Mean | 95% CI | Two-sided Wilcoxon |
|---|---|---|---|
| n=20 | −0.27 dB | [−0.45, −0.11] | \(p=0.0012\) |
| 16 real | −0.30 dB | [−0.52, −0.11] | \(p=0.004\) |
| 6 bass loops | −0.57 dB | [−0.88, −0.26] | \(p=0.031\) |

Counts n=20: 11 better by >0.05 dB, 8 ties, 1 slightly worse. One-sided H2 (\(\Delta<0\)) is supported for S2 (\(p=6\times10^{-4}\)) and rejected for S1.

### 2.4 What the paper file currently contains

Already in `main.tex` from Phase B:

- Mismatch title and honest S1 abstract (+1.17 dB, hypothesis not supported).
- Intro/related-work distinction: standard silent ≠ no algorithms.
- Gap-table rows for Chen 2023, the two patents, Fathima 2026.
- \(W_A/W_K\) figure next to the A-weighting check figure.
- S1 Wilcoxon/CI sentence.

**Missing from `main.tex`:** S2, three-system methods, reversal result, `matched_loudness_s1_s2.png` / updated table include, optional C-weighting, version-C title/contribution bullets. Figures exist; they are not wired into the tex yet.

---

## 3. What must be done next (in order)

Do these **in roadmap order**. Do not retune mid target 72 after seeing \(\Delta\).

### Immediate — Step 10 (next coding stretch)

C-weighting proxy. **Hypothesis, already on the record:** at matched LUFS, S1 should look better on \(L_{Ceq}\) than on \(L_{Aeq}\) (bass cuts count for C); S2 the opposite.

Step 8 is done (`matched_loudness_s1_s2.png`, `perclip_table.tex`). Step 9 is already satisfied (`stats_s2.json`). Optional extra: paired S1 vs S2 test; not required to proceed.

### Then — Steps 11–12 (the actual paper)

Rewrite toward version C:

1. Title may become *Metric-Aligned Frequency Allocation for Personal-Audio Dose Limiting* (roadmap §3.1 option 3), or keep the mismatch title and add S2 in the abstract.
2. Intro: matched test; S1 fails; allocation follows \(w_A\); S2 reversed the sign.
3. Methods: define S0, S1, S2; S2 is a config.
4. Results: keep the +1.17 dB S1 story; add S2 figure/stats; say the margin is modest.
5. Limitations: still a digital proxy; mid cut may hurt speech; no MUSHRA.
6. Every number from `results/tables/`. Compile; search for SPL / hearing loss / quality / novel architecture / optimal / adaptive.

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
| Title still sounds like a winning product | Current mismatch title is safer until Step 11; if retitled to “metric-aligned,” the abstract must keep S1’s failure. |
| Ablation not refreshed | Frozen S1 ablation is fine; do not imply S2 was ablated band-by-band unless you re-run it. |
| Chen vs “Liang 2023” | The IJERPH paper is Chen, Xue, Wang, Cai, Zhu (2023). Cite `Chen2023`. |
| Quality / SPL language | Still forbidden. Digital \(L_{Aeq}\) proxy only. |
| p-hacking S2 | Mid target 72 was frozen before the 20-clip mean. Leave it. |

---

## 6. Commands that regenerate the current numbers

```text
python -m exposure_dsp checks          # includes weighting-ratio figure
python -m exposure_dsp stats           # stats_s1.json + stats_s2.json from comparison.csv
python -m exposure_dsp experiment      # full S1+S2 comparison (slow; ablation on by default)
python paper/make_figures.py           # S1 + S2 grouped bars and perclip_table.tex
```

S1 freeze (do not overwrite as the source of truth): `results/frozen/draft-negative-v1/`.

---

## 7. Next action

**Step 10.** When you say go: IEC 61672 C-weighting proxy (`exposure_dsp/cweighting.py`), same RMS+offset helper as A; add a C-weighted column or small JSON; one Results paragraph after looking. Hypothesis is already written: S1 should look better on \(L_{Ceq}\) than on \(L_{Aeq}\); S2 the opposite. Do not retune knobs.

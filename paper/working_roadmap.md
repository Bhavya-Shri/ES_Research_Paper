# Working roadmap — follow in order

We do these steps **together, in this order**. Do not skip ahead. Do not retune the current bass-cut processor (S1) to make it “win.” That system is the failed heuristic on purpose.

Background (why, venues, novelty): `paper/publishing_audit_and_roadmap.md`  
Paper explained: `paper/walkthrough_notes.md`  
**Status vs this roadmap (15 Sep 2026):** `paper/progress_audit.md`

Tick boxes in this file as we finish each step.

---

## How we work

- One step (or a tight pair) per stretch of work.
- After each step: run what it says, confirm the **Done when** line, then go to the next.
- If S2’s result is surprising, we **stop and interpret** before adding more features.

**S0** = frequency-flat gain (baseline)  
**S1** = current proposed (bass shelf −12 dB + harmonics + mild mid DRC)  
**S2** = metric-aligned (no bass cut, stronger mid cut)

---

## Phase A — Freeze what you already have

### Step 0 — Snapshot the negative-result draft

**Do**

- Leave `results/tables/comparison.csv`, `experiment.json`, and current `paper/main.tex` as the S1 record.
- Do not change S1 defaults in `ProposedConfig` (`sub_atten_db = -12`, `mid_target_dba = 78`, harmonics on).

**Done when:** we agree S1 is frozen. No code required if files already exist (they do).

**Status:** done. Snapshot in `results/frozen/draft-negative-v1/`. S1 knobs unchanged.

---

## Phase B — Make the existing result scientifically tighter

### Step 1 — A vs K weighting figure

**Why:** the whole paper is “you cut where A-weighting is tiny and K-weighting is not.” Show that on one plot.

**Implement**

- K-weighting magnitude (BS.1770 stages already sketched in `exposure_dsp/metrics.py`).
- Figure: A-weighting dB, K-weighting dB, and ratio \(W_A/W_K\) dB, log-frequency 20 Hz–20 kHz.
- Mark 40 Hz, 300 Hz, 1 kHz, 4 kHz.

**Files:** `exposure_dsp/kweighting.py` (or extend `aweighting.py` / `checks.py`); `paper/figures/weighting_ratio.png`; hook into `checks` or `paper/make_figures.py`.

**Done when:** PNG exists and A at ~40 Hz is about −35 dB, K much less severe there.

### Step 2 — Statistics on the current 20-clip S1 table

**Why:** reviewers will not accept a mean with no test.

**Implement**

- Read \(\Delta L_{Aeq}\) at matched LUFS from existing `comparison.csv` (S1 vs `gain_matched_loudness`).
- Wilcoxon signed-rank vs 0; bootstrap 95% CI on the mean; same for the 16 real clips only.

**Files:** `exposure_dsp/stats.py`; `results/tables/stats_s1.json`.

**Done when:** JSON has mean, CI, p-value, n=20 and n=16. No DSP re-run required.

### Step 3 — Cite the missing neighbours

**Why:** the gap table is too clean without them.

**Change**

- `paper/references.bib`: Liang et al. 2023 (IJERPH safe listening + DRC); US 9980028; US 6826515; Fathima et al. ICSSCNA 2026 if you have a stable cite.
- `paper/main.tex` Related Work + one extra row or footnote in the gap table.

**Done when:** those names appear in the PDF bibliography and §2 distinguishes “standard is silent” from “no algorithm exists.”

### Step 4 — Retitle and re-abstract S1 honestly

**Change `paper/main.tex`**

- Title away from “loudness preservation / reduced exposure” as if you succeeded.
- Working title until S2 exists:  
  **Metric Mismatch in Frequency-Selective Personal-Audio Limiting: A-Weighting versus BS.1770**
- Abstract already reports +1.17 dB and “not supported” — keep that. Drop any leftover success tone in intro/conclusion if we find it.

**Done when:** title matches the negative result. We may retitle again after Step 7.

---

## Phase C — The new experiment (this is the novelty)

### Step 5 — Add S2 as a config, not a new architecture

**Implement in `exposure_dsp/proposed.py`**

- `ProposedConfig.aligned()` (name can vary):
  - `sub_atten_db = 0`
  - `harmonic_mix = 0`
  - `mid_target_dba = 72` (frozen now; do not tune on the full 20 after seeing \(\Delta\))
  - same crossovers 300 Hz / 4 kHz, same mid ratio 4, same high band

**Done when:** `ProposedProcessor(ProposedConfig.aligned()).process(x)` runs on a 1 s sine without changing S1 defaults.

### Step 6 — Experiment loop for S1 and S2

**Implement in `exposure_dsp/experiment.py`**

For each clip:

- process S1 (current defaults) and S2 (aligned)
- match each to flat gain on LUFS and on \(L_{Aeq}\) (reuse `match_gain`)
- write rows with `system` in `{proposed, aligned, gain_matched_loudness, ...}` — keep names explicit

Keep S1 numbers comparable to the frozen table.

**Done when:** `python -m exposure_dsp experiment` writes a CSV that has both S1 and S2 matched-LUFS \(\Delta L_{Aeq}\).

### Step 7 — Read the sign of S2  ← **decision gate**

Compute mean \(\Delta L_{Aeq}\) (aligned − flat) at matched LUFS.

| If mean is… | Paper story | Then |
|---|---|---|
| **Negative** (aligned lower dose) | Failure of S1 + correction by S2 | Continue to figures + rewrite (best case) |
| **Near 0** (e.g. \|mean\| < 0.2 dB) | A and K cannot be gamed in the midrange; only bass-cut *hurts* | Still a paper; do not keep twisting knobs |
| **Positive** | Unexpected — debug before writing | Check mid compressor actually engages; do not p-hack `mid_target_dba` on all 20 |

**Done when:** we write the chosen story in one sentence and freeze S2 knobs.

**Status:** done. Frozen S2 knobs: `sub_atten_db=0`, `harmonic_mix=0`, `mid_target_dba=72` (not retuned).

**Story:** S1 loses at matched LUFS (+1.17 dB); S2 reverses the sign (−0.27 dB, bootstrap 95% CI [−0.45, −0.11], two-sided Wilcoxon p=0.001), so attenuation spent where \(w_A\) is large beats flat gain on the digital \(L_{Aeq}\) proxy. The margin is modest; do not twist knobs.

### Step 8 — Figures and tables for the three-way comparison

**Implement / update**

- Grouped bars: S1 vs S0 and S2 vs S0, per clip, matched LUFS (replace or add to Fig. 5).
- Per-clip LaTeX table: both deltas.
- Ablation already has mid-only vs low — keep; maybe add aligned as `use_low=False` path (that is S2 if mid is stronger).

**Files:** `paper/make_figures.py`, `paper/perclip_table.tex`, `paper/figures/`.

**Done when:** `python paper/make_figures.py` (or equivalent) produces paper-ready PNGs from the new CSV.

**Status:** done. `plot_matched_loudness_s1_s2` + `write_s1_s2_table` in `paper/make_figures.py`. S1-only `matched_loudness_delta.png` kept. New grouped bars: `paper/figures/matched_loudness_s1_s2.png`. `paper/perclip_table.tex` now has S1 and S2 \(\Delta L_{Aeq}\) / \(\Delta\)LUFS (means +1.17 / −0.27 dB). Frozen S1 ablation figure unchanged. `main.tex` not rewritten yet (Step 11).

### Step 9 — Stats for S2 + contrast

Wilcoxon/CI for S2 deltas; optional paired S1 vs S2.

**Done when:** `stats_s1.json` and `stats_s2.json` (or one file with both).

**Status:** done (ran with Step 7). `results/tables/stats_s2.json`; n=20 mean −0.27 dB, CI [−0.45, −0.11]. Paired S1 vs S2 test not required.

---

## Phase D — One extra meter (cheap, high insight)

### Step 10 — C-weighting proxy

**Implement:** `exposure_dsp/cweighting.py` (IEC 61672 C), same RMS+offset helper as A.

**Hypothesis (write before looking):** at matched LUFS, S1 should look **better** on C-weighted energy than on A (bass cuts count for C). S2 should do the opposite.

**Done when:** comparison table has a C-weighted column or a small extra JSON; one Results paragraph.

**Status:** done. `cweighting.py` + `lceq_proxy`. `python -m exposure_dsp cweight` → `stats_cweight.json`, `comparison_cweight.csv`. A-deltas reproduced to 0 dB. S1 \(\Delta L_{Ceq}=-0.58\) dB (A was +1.17); S2 \(\Delta L_{Ceq}=+0.06\) dB (A was −0.27). Both hypotheses held. One Results paragraph in `main.tex`. Knobs not retuned.

---

## Phase E — Rewrite the paper to match the data

### Step 11 — `main.tex` structure for version C

1. Intro contribution: matched test; S1 fails; allocation must follow \(w_A\); S2 {did / did not} reverse the sign.  
2. Related work: patents + Liang (Step 3).  
3. Short theory: \(W_A/W_K\) + Step 1 figure.  
4. Methods: S0, S1, S2; matching duals unchanged.  
5. Results: S1 +1.17 dB story kept; S2 new figure; stats; optional C.  
6. Limitations: still digital proxy; mid cut may hurt speech; no MUSHRA.  
7. Conclusion: design rule, not “we invented a limiter.”

**Done when:** every number in the PDF is generated from `results/tables/`. No leftover “loudness preservation succeeded” language.

**Status:** done. Title *Metric-Aligned Frequency Allocation for Personal-Audio Dose Limiting*; abstract keeps S1 failure. S0/S1/S2 methods; `matched_loudness_s1_s2.png` and `perclip_table.tex` wired; C-weighting kept; S2 margin called modest. Compile/claim search is Step 12.

### Step 12 — Compile and consistency pass  ← **NEXT**

- `pdflatex` / Overleaf IEEEtran.
- Search PDF for: SPL, hearing loss, quality, novel architecture, optimal, adaptive.
- Delete or qualify each hit.

**Done when:** PDF builds; claims = data.

---

## Phase F — Submit (after the paper matches)

### Step 13 — Literature close-out (IEEE Xplore + AES, not only Google)

Queries in the audit file §8 Phase 7. Add anything that is a real neighbour.

### Step 14 — Venue + submit

- Student / regional IEEE if S2 was not run or is messy.  
- Conference / AES if S2 story is clean (reversal **or** cannot-game).  
- Do **not** wait for ear simulator or MUSHRA for that first submission.

**Last step:** submitted PDF + frozen code/results that regenerate every number.

---

## Explicitly later (not this roadmap)

Do **not** start these until Step 12 is done:

- Extra Freesound clips  
- Headphone-EQ simulation  
- MUSHRA / classmates listening test  
- HATS / IEC 60318-4  
- ML, more bands, better virtual bass, STM32  

Those are a **second** paper or a journal extension.

---

## Status

| Step | Status |
|---|---|
| 0 Freeze S1 | **Done** (tables in `results/frozen/draft-negative-v1/`; S1 knobs unchanged) |
| 1 Weighting-ratio figure | **Done** (`paper/figures/weighting_ratio.png`; A@40 Hz = −34.5 dB, K@40 Hz = −5.6 dB) |
| 2 Stats on S1 | **Done** (`results/tables/stats_s1.json`; n=20 mean +1.17 dB, two-sided p=3.9e-4) |
| 3 Citations | **Done** (Chen 2023, US 9980028, US 6826515, Fathima 2026) |
| 4 Retitle | **Done** (*Metric-Aligned Frequency Allocation for Personal-Audio Dose Limiting*) |
| 5 S2 config | **Done** (`ProposedConfig.aligned()`: shelf 0 dB, mix 0, mid target 72) |
| 6 Experiment S1+S2 | **Done** (`comparison_s1_s2.csv`; S1 +1.17 dB, S2 −0.27 dB) |
| 7 Sign gate | **Done** — reversal; S2 knobs frozen at mid target 72 |
| 8 Figures | **Done** (`matched_loudness_s1_s2.png`; `perclip_table.tex` S1+S2) |
| 9 Stats S2 | **Done** (`stats_s2.json`; CI excludes 0) |
| 10 C-weighting | **Done** (`stats_cweight.json`; S1 −0.58 dB, S2 +0.06 dB) |
| 11 Rewrite tex | **Done** (version C in `main.tex`) |
| 12 Compile pass | **Next** |
| 13 Xplore search | Not started |
| 14 Submit | Not started |

When you say go, we start at **Step 12** (compile and claim check). Do not skip to extra clips, MUSHRA, HATS, or ML.
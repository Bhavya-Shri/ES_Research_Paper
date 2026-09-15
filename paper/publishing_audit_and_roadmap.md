# Publishing audit and roadmap

**Paper:** Frequency-Adaptive Audio Limiting for Reduced Acoustic Exposure and Loudness Preservation  
**Repo:** `ES_Research_Paper` (`exposure_dsp/`, `paper/main.tex`)  
**Companion:** `paper/walkthrough_notes.md` (section-by-section explanation of the current draft)  
**Date:** 13 Sep 2026  

This file is the working audit: what exists, what is not novel, how to change the paper, what new science would actually publish, what to implement, and the steps through submission.

---

## 0. Executive verdict

The current draft is a **correct negative experiment** written honestly. That is rare and valuable. It is **not** a highly publishable IEEE journal paper as-is.

| Version | What it is | Realistic venue |
|---|---|---|
| **A. Current draft** | Bass-cut + virtual bass vs flat gain; H2/H1 fail | IEEE student / regional conference |
| **B. Current + theory + citations + stats** | Same data, stronger science writing | Stronger student IEEE / small conference |
| **C. Three-system paper (recommended)** | Add metric-aligned mid-cut allocator; show failure *and* correction | IEEE conference, AES convention, possibly SPL if tight |
| **D. C + calibration + listening** | Ear simulator or headphone-FR simulation + MUSHRA | IEEE SPL / AES Journal (months extra) |

**Do not** invent a fancier DSP from scratch (ML limiter, 12-band crossover, new NLD). Reviewers will still ask: *did frequency allocation beat flat gain at matched LUFS?* You already have that question. The publishable move is to **align the allocation with the metric that failed**, and to **prove the condition** under which any frequency-selective limiter can win.

**One-sentence contribution to write toward (version C):**

> Frequency-selective personal-audio limiting beats broadband gain on an A-weighted exposure proxy at matched BS.1770 loudness only when attenuation is spent where the A-weighting gain is large. A bass-first virtual-bass heuristic, motivated by equal-loudness contours, does the reverse and loses. A mid-band-first allocator reverses the sign on the same matched test.

---

## 1. Audit of work done so far

### 1.1 What the repo already contains (done)

| Item | Where | Status |
|---|---|---|
| 3-band causal processor (LR4, −12 dB shelf, NLD harmonics, A-weighted mid DRC, high envelope, −1 dBFS ceiling) | `exposure_dsp/proposed.py` | Done |
| Broadband A-weighted compressor + peak ceiling | `exposure_dsp/limiter.py` | Done |
| IEC A-weighting IIR + analytic curve | `exposure_dsp/aweighting.py` | Done |
| LUFS (`pyloudnorm`), LSD, \(L_{Aeq}\) proxy | `exposure_dsp/metrics.py` | Done |
| Matched-LUFS and matched-\(L_{Aeq}\) vs flat \(G\) | `exposure_dsp/experiment.py` `match_gain` | Done |
| Idle compressor match (correctly de-emphasised in paper) | `match_limiter` | Done |
| Ablation (crossover / mid / low / high) | `make_ablation` | Done |
| Mid target/ratio sweep | `cli.py` `cmd_sweep` | Done |
| Verification: LR reconstruction, harmonic coverage, A-curve, stream=whole-file | `exposure_dsp/checks.py` | Done |
| 16 Freesound + 4 synthetic clips, tables, figures | `results/tables/`, `paper/figures/` | Done |
| IEEE draft with **honest negative result** | `paper/main.tex` | Done |
| Walkthrough of every section | `paper/walkthrough_notes.md` | Done (this chat) |

**Main numeric result (already computed):**  
`mean_dlaeq_at_matched_lufs = +1.174 dB` (proposed worse). Dual `mean_dlufs_at_matched_laeq = −1.175 dB`. Sign is a dual, as the paper states.

### 1.2 What this chat already analysed (done)

- Novelty search (first pass, web + patents, not a full IEEE Xplore harvest).
- Title/abstract through Conclusion, claim-by-claim: what exists, what you cannot claim.
- Closest neighbours named: H.870, Giannoulis 2012, Kates 2008, Gan virtual bass, Liang et al. 2023, US 9980028, US 6826515, Fathima et al. ICSSCNA 2026.
- Publishing strategy: invert allocation rather than invent blocks.

### 1.3 What is *not* done (gaps)

| Gap | Why it matters |
|---|---|
| Metric-aligned system (cut mids, keep bass) | Without it, you only have a failed heuristic |
| Plot / theory of \(w_A(f)\) vs \(w_K(f)\) | Turns “we lost” into a **condition for winning** |
| Wilcoxon / CI / effect size on the 20 clips | Reviewers expect a test, not only a mean |
| Citations: Liang 2023, US 9980028, Fathima 2026 | Current gap table is too clean |
| C-weighting / Z-weighting as extra meters | Shows the result is **metric-dependent**, not “multiband is useless” |
| Headphone frequency-response simulation | Step toward H.870 without a lab |
| Listening test or PEAQ/ViSQOL | Blocks all quality language |
| Ear simulator (IEC 60318-4) | Blocks all SPL / safety language |
| Full IEEE Xplore + AES E-Library search | Web search is not enough for IEEE |
| Title that matches the negative/aligned story | Current title still sounds like a winning limiter |

---

## 2. What already exists (do not claim)

Restated so the improvement plan does not re-invent them.

| Piece | Who / what | Your relation |
|---|---|---|
| A-weighted dose, weekly allowance | ITU-T H.870, WHO, IEC 61672 | Constraint you *use* |
| Broadband volume cap / AGC | Phones, EN 50332, Giannoulis 2012, Liang 2023 | **Baseline** |
| Headset dosimeter with **flat** gain | US 6826515 | Baseline in patent form |
| Multiband DRC | Hearing aids (Kates), plugins, Patel 2019 | Mid/high bands |
| Virtual bass NLD | MaxxBass, Gan 2001/2004, Schouten/Terhardt | Low-band harmonics |
| Linkwitz–Riley complementary crossover | Linkwitz 1976 | Split |
| LUFS / K-weighting | ITU-R BS.1770 | Loudness meter |
| Equal-loudness contours | Fletcher–Munson, ISO 226 | Motivation only |
| Multiband **dose** limiting | US 9980028 (TWA + companding) | Closest method-neighbour |
| Multi-band hearing protection | US 11006215; Fathima 2026 | Adjacent, different task |
| A vs C vs K as different meters | Concert/occupational literature | Known; you apply it to this allocator |

**You may not claim:** a new limiter architecture, virtual bass, A-weighting, LUFS, H.870, “first frequency-selective exposure limiter,” hearing protection, or a quality improvement.

**You may claim (current draft, weakly):** a matched LUFS vs digital \(L_{Aeq}\) comparison of a bass-first heuristic vs flat gain, with a negative result and a mechanism.

**You may claim (version C, strongly):** the **alignment principle** + empirical reversal of the sign.

---

## 3. Improve the *current* paper without new DSP (version B)

Do these even if you never implement system 3. They cost writing time, not a new algorithm.

### 3.1 Title and abstract

Current title promises loudness preservation and reduced exposure. Data contradict both.

**Better titles (pick one):**

1. *Why Bass-First Frequency Allocation Fails under A-Weighted Dose: A Matched-Loudness Comparison*
2. *Metric Mismatch in Frequency-Selective Personal-Audio Limiting: A-Weighting versus BS.1770*
3. (If system 3 exists) *Metric-Aligned Frequency Allocation for Personal-Audio Dose Limiting*

Abstract: keep the +1.17 dB and “hypothesis not supported.” If system 3 is added, the abstract becomes two-part: naive heuristic fails; aligned allocator succeeds (or does not — report whichever is true).

### 3.2 Related work surgery

Add rows/citations:

- Liang et al., *IJERPH* 2023, “Hearing Care: Safe Listening Method and System for Personal Listening Devices” — H.870 + speaker FR + **broadband DRC**. Closest *problem* paper.
- US 9980028 — TWA limiter, optional **multiband companding** to keep loudness at lower RMS. Closest *method* paper. Distinguish: speech headset, not matched LUFS/\(L_{Aeq}\) on music.
- US 6826515 — explicitly frequency-flat gain. Cite as the baseline’s prior art.
- Fathima, Poozhithara, Nandana, ICSSCNA 2026 — multi-band transient-aware hearing protection. Distinguish: speech/noise, not this match.
- Optionally: ISO 532-1 as the loudness model you *did not* use (already cited Moore/Zwicker; say why LUFS instead).

Gap table: change “This work / Freq adapt / Yes” so it does not look like you invented frequency-adaptive exposure control. Caption: *matched LUFS vs digital \(L_{Aeq}\) on music, bass-first heuristic.*

### 3.3 Statistics on the table you already have

On the 20 (and 16) \(\Delta L_{Aeq}\) values:

- Wilcoxon signed-rank vs 0 (one-sided H2, then two-sided for honesty)
- Bootstrap 95% CI on the mean
- Cohen’s \(d\) or rank-biserial effect size
- Separate tests: bass subset vs non-bass subset (pre-register the six bass IDs)

Code: 30 lines in a notebook or `exposure_dsp/stats.py`. Reviewers will ask. A mean without a test looks like a student report.

### 3.4 Weighting-curve figure (high value, low effort)

You already plot A-weighting (Fig. 4). **Add K-weighting (BS.1770) on the same axes**, and the ratio \(w_A(f)/w_K(f)\) in dB. Mark 40 Hz, 300 Hz, 1 kHz, 4 kHz.

This single figure *is* the mechanism. Many reviewers will accept the negative result if they can *see* that you cut where the ratio is small.

Implement: `checks.py` or a new `paper/make_weighting_ratio.py` using your existing A-curve and the K-filter already in `metrics.py` (`_k_weighted_ungated` SOS).

### 3.5 Language audit (do / do not)

| Do | Do not |
|---|---|
| digital \(L_{Aeq}\) proxy | dB SPL, “dose at the ear” |
| hypothesis not supported | “improved exposure control” |
| heuristic / prototype cutoffs | adaptive, optimal, perceptually validated |
| LSD as spectral distance | quality, transparency, fidelity |
| comparison is the contribution | novel limiter architecture |
| bass-first allocation is poor for A-weighting | frequency-selective limiting is useless |

### 3.6 Reproducibility polish

- Pin `requirements.txt` versions.
- One command that regenerates **every** table/figure in the paper (`python -m exposure_dsp all` already close; document exact commit).
- Freesound IDs are in the footnote — good. Add license line and download date.
- State random seeds if any (synthetics).

Version B alone can lift a sloppy student paper to a **defensible** student IEEE paper. It does **not** make TASLP/SPL.

---

## 4. New additions that can actually be novel (ranked)

Novelty here means: a reviewer cannot say “this is just Kates + Gan + H.870.” Ranked by **publishability per week of work**.

### Rank 1 — Alignment principle + three-system test (do this)

**Idea.** For two weighted-energy meters \(M_A = \|w_A * y\|\) and \(M_K \approx\) LUFS, a frequency-selective gain beats flat gain on \(M_A\) at fixed \(M_K\) **iff** it attenuates where \(w_A/w_K\) is large, not where it is small.

**Systems**

| ID | Name | Behaviour |
|---|---|---|
| S0 | Flat gain | Baseline |
| S1 | Bass-first (current proposed) | −12 dB low shelf + NLD; mild mid DRC |
| S2 | Metric-aligned | **No** low shelf (or 0 dB); **stronger** mid cut where \(w_A\) is high |

**Predicted signs at matched LUFS**

- S1 − S0: \(\Delta L_{Aeq} > 0\) (already measured +1.17 dB)
- S2 − S0: \(\Delta L_{Aeq} < 0\) if the theory is right

**Why this is novel enough:** nobody in the cited PLD/H.870 literature published this *matched* reversal. Patents describe multiband for dose, but not this A-vs-K allocation test on music. The failed heuristic becomes **ablation / negative control**, not the hero.

**Risk:** K-weighting also emphasises mids (HF shelf). S2 might lower **both** meters together, and after LUFS matching the \(L_{Aeq}\) gap could be small. Then the paper becomes: “these two operational meters are too aligned in the midrange to game.” **That is still publishable** if you show the ratio curve and the numbers. Either sign of S2 is a result. You must run it.

**Effort:** 1–3 days if you reuse `ProposedConfig` (`sub_atten_db=0`, `mid_target_dba` 72–74, maybe `harmonic_mix=0`).

### Rank 2 — Closed-form / diagnostic theory figure

Derive (even approximately) for a linear filter \(H(f)\) and a clip with spectrum \(S(f)\):

\[
\Delta L_{Aeq} \approx 10\log_{10}\frac{\int S|H|^2 |W_A|^2}{\int S|W_A|^2},\quad
\Delta L_{K} \approx 10\log_{10}\frac{\int S|H|^2 |W_K|^2}{\int S|W_K|^2}
\]

Flat gain: \(\Delta L_{Aeq} \approx \Delta L_K\).  
Shaped \(H\): sign of \(\Delta L_{Aeq} - \Delta L_K\) tracks whether \(H\) cuts high or low \(W_A/W_K\) regions.

Add a **static EQ** S3 whose \(|H(f)|\) is a monotone function of \(W_A/W_K\) (e.g. cut 6–12 dB from 1–4 kHz, 0 dB below 150 Hz). Compare S3 to S2 (time-varying compressor). If static EQ already wins, the compressor is unnecessary — a stronger, simpler paper.

**Novelty:** the *condition*, not the biquad.

### Rank 3 — Metric-dependence (C-weighting)

Add C-weighting (IEC 61672) and maybe unweighted RMS as extra columns.

Hypothesis: at matched LUFS, S1 (bass-cut) **should win** on C-weighted / unweighted energy (because C keeps bass) and **lose** on A-weighted energy (already shown).

That one table teaches: **“frequency-selective limiting” is not good or bad; it is good for the meter you cut toward.** H.870 chose A. Concerts often argue C. This is a real contribution to the safe-listening debate and still uses your pipeline.

Implement: copy `aweighting.py` → `cweighting.py` (IEC C poles are public). Same `laeq_proxy` pattern.

### Rank 4 — Headphone-response sensitivity (no lab)

H.870 dose is A-weighted **after** headphone FR and DRP-to-diffuse-field. Your digital proxy skips that.

**Cheap version:** convolve (or EQ) with 3–5 published earphone magnitude responses (e.g. a bass-heavy IEM, a Harman-ish curve, a bright earbud) before A-weighting. Recompute \(\Delta L_{Aeq}\) at matched LUFS.

Question: does the sign of S1 vs S0 **flip** for a bass-boosting IEM? If yes, the paper’s lesson becomes “depends on the transducer.” If no, the A-weighting dump at 40 Hz still dominates. Either is interesting. Cite P.381 / H.870 Appendix II as the mapping you are approximating.

**Not** a substitute for a HATS. Say so. Still much closer to the standard than +94.

### Rank 5 — Listening test (quality claims)

Without this you **cannot** say quality, bass preservation, or “sounds as loud.”

Minimum conference-grade:

- 8–12 listeners (classmates OK if you report as such)
- 8–12 clips (include bass + speech)
- Conditions: original, S0-at-matched-LUFS, S1, S2 (if exists)
- **Locked playback volume** (same DAW output, same headphones)
- MUSHRA or simple 5-point: overall quality, bass, speech clarity, loudness
- Randomise order; report means + 95% CI

If you cannot run listeners: ViSQOL-audio or PEAQ if available; still say they are not MUSHRA. LSD stays in the paper as objective distance.

### Rank 6 — Calibrated SPL (journal shot)

IEC 60318-4 occluded-ear simulator or HATS, one earphone, several volume settings, programme simulation signal (EN 50332). Then H.870-style numbers.

This is a **lab**, not a weekend. Do **not** block version C on this. Put it in Future Work until you have access (VIT acoustics / ECE lab).

### Rank 7 — Things that look novel but are traps

| Idea | Why not (first) |
|---|---|
| Deep learning limiter | No data, no novelty of *question*, reviewers ask for the simple baseline you already have |
| 8–12 band crossover | Extra knobs, same metric issue |
| Better NLD / phase vocoder virtual bass | You already showed virtual bass does not save A-weighted dose |
| Real-time STM32 port | Engineering demo, not a new scientific claim unless latency/SNR is the paper |
| Claiming ISO 226 in the loop without implementing it | You already correctly refused this |
| “Prevent NIHL” language | Limitations forbid it |

---

## 5. What you must implement (concrete)

Ordered for version **C**, then optional D.

### 5.1 Must-implement for a highly publishable *conference* paper

**M1. Weighting-ratio figure**  
Files: `exposure_dsp/kweighting.py` (or extend `metrics.py`); `exposure_dsp/checks.py` or `paper/make_figures.py`.  
Output: `paper/figures/weighting_ratio.png` — A, K, A/K in dB vs Hz, log x-axis 20–20 kHz.  
Paper: new figure next to current Fig. 4.

**M2. System S2 (metric-aligned)**  
In `ProposedConfig`:

- `sub_atten_db = 0.0`
- `harmonic_mix = 0.0` (or keep tiny mix; default off so S2 is clean)
- `mid_target_dba` in `{74, 72, 70}` — pick one **before** looking at the 20-clip mean, or report a small sweep and **lock** one value
- keep LR4 300 Hz / 4 kHz so the only changed story is **allocation**

Optionally a **static mid shelf** (−6 or −9 dB at ~2 kHz, Q~0.7) as S3, even simpler than a compressor.

Wire into `experiment.py`: for each clip, process S1 and S2; match each to flat gain on LUFS and on \(L_{Aeq}\). Table columns: \(\Delta L_{Aeq}\) S1, \(\Delta L_{Aeq}\) S2.

**M3. Three-way figure**  
Replace Fig. 5 with grouped bars per clip: S1 vs S0 and S2 vs S0 at matched LUFS. Colour bass vs speech as now.

**M4. Statistics module**  
`exposure_dsp/stats.py`: Wilcoxon, bootstrap CI, optional Holm correction if you test subsets. Write `results/tables/stats.json`. One paragraph in Results.

**M5. C-weighting column (strongly recommended with M2)**  
`cweighting.py` analog of `aweighting.py`. Same match. Hypothesis in the paper *before* running: S1 should look better on LCeq than on LAeq.

**M6. Bibliography + gap table**  
`references.bib`: Liang2023, US9980028, US6826515, Fathima2026, IEC C-weighting. Rewrite §2.5.

**M7. Title / abstract / contribution sentence**  
As in §3.1 and the executive verdict.

### 5.2 Should-implement for robustness

- **S8. Genre-balanced extra clips** — aim 30–40 real files (still Freesound CC). Keep the original 16 so old numbers remain.
- **S9. Headphone EQ sensitivity** — 3 magnitude responses as FIR/minimum-phase EQ; recompute S1/S2 deltas.
- **S10. Always-on broadband compressor baseline** — lower the default target until it always engages, *or* explicitly match by searching threshold until LUFS matches (you already have `match_limiter`; report when it idles vs when it works). Reviewers may say static \(G\) is too kind/unkind; showing both is stronger.
- **S11. Confidence that S2 mid target was not p-hacked** — freeze target on a 4-clip development set, evaluate on the other 16.

### 5.3 Implement only if chasing a journal

- Locked-volume MUSHRA (or 5-scale) with ≥8 listeners  
- One earphone on a coupler/HATS  
- Maybe ISO 532-1 loudness (Python ports exist; heavier than LUFS) as a *third* loudness definition  

### 5.4 Suggested new paper skeleton (version C)

1. Introduction — H.870 silent on allocation; two meters disagree; we test bass-first vs aligned vs flat  
2. Related work — four toolboxes + patents + Liang + Fathima; gap = matched A vs K allocation  
3. Theory — \(W_A/W_K\); failure mode vs success mode  
4. Methods — S0, S1, S2 (and optional S3 static EQ); matching; metrics; corpus  
5. Implementation / verification — keep existing checks  
6. Results — S1 loses; S2 wins or not; C-weighting flips S1; ablation; stats  
7. Limitations — still digital proxy  
8. Conclusion — allocation must follow the **dose weight**, not equal-loudness folklore  

---

## 6. How “highly publishable” breaks down by venue

| Target | Bar | Your path |
|---|---|---|
| College / IEEE student paper | Working experiment + honest writing | Version B is enough |
| IEEE regional (INDICON, TENCON student, ICICC, etc.) | Clear contribution + citations + stats | Version C if S2 has a clean story |
| AES convention / DAFx / WASPAA workshop | Audio specialists will know virtual bass and LUFS | Version C + weighting-ratio figure + C-weighting |
| IEEE Signal Processing Letters | One idea, ~4–5 pages, tight experiment | Alignment principle + 3 systems + stats; no safety claims |
| IEEE TASLP / AES Journal | Listening test + often calibration | Version D; 6–12+ months |

**Do not** aim TASLP with the current 20-clip digital proxy. You will be rejected on SPL, listeners, and “known DSP.”

**Do** aim a good conference with version C, then a journal extension with listeners + coupler.

---

## 7. Risks and how they kill the paper

| Risk | If it happens | What to write instead |
|---|---|---|
| S2 also loses at matched LUFS | A and K are too aligned in mids | “Operational meters cannot be gamed by mild EQ; only bass-cut *hurts* A-dose; mid-cut does not help either.” Still a result |
| S2 wins on \(L_{Aeq}\) but wrecks speech | Objective win, subjective loss | Need a listening test or at least LSD/ViSQOL; paper becomes a **trade-off**, which is fine |
| Reviewer cites US 9980028 as prior | You look unaware | Cite it; distinguish matched music LUFS/\(L_{Aeq}\) |
| Reviewer says n=20 | Weak generalisation | Add clips; report 16-real vs all; stats |
| Title still sounds like a safety device | Ethics / overclaim | Rename; keep proxy language |
| S2 mid target tuned on the test set | p-hacking | Freeze on a tiny dev set |

---

## 8. Further steps through submission (last step included)

Do **in this order**. Do not skip to hardware.

### Phase 0 — Freeze the old result (half day)

1. Commit or zip current `results/tables/` and `paper/main.tex` as **draft-negative-v1**.  
2. Do not retune S1 to “make it win.” S1 is the failed heuristic on purpose.

### Phase 1 — Theory figure + stats on existing data (1–2 days)

3. Implement K-weighting magnitude plot and \(W_A/W_K\).  
4. Wilcoxon + bootstrap on current 20 \(\Delta L_{Aeq}\) values; add a Results sentence.  
5. Rewrite title/abstract toward mismatch / allocation (even before S2).  
6. Add Liang 2023, US 9980028, US 6826515 to `references.bib` and §2.

**Checkpoint:** version B PDF you could submit to a student track tomorrow.

### Phase 2 — System S2 (2–4 days) — the actual novelty

7. Add `ProposedConfig` aligned preset; `harmonic_mix=0`, `sub_atten_db=0`.  
8. Freeze mid target on 4 clips (document which).  
9. Extend `run_comparison` to S1 and S2.  
10. New grouped-bar figure; new per-clip table.  
11. Ablation: aligned mid-only vs bass-only already exist — reuse flags.  
12. Write Results: “S1 loses for reason R; S2 {wins/ties/loses} as predicted by Fig. W.”

**Checkpoint:** you know if the paper is a **reversal story** or a **cannot-game-the-meters story**. Both are submit-able. Do not keep fishing knobs.

### Phase 3 — Metric-dependence (2 days)

13. C-weighting proxy; maybe unweighted RMS.  
14. Table: \(\Delta\) at matched LUFS for LAeq, LCeq, RMS, for S1 and S2.  
15. One paragraph: allocation quality is defined **relative to the dose weighting**.

### Phase 4 — Robustness (3–7 days)

16. Add ~15 more real CC clips; keep original 16 as a reported subset.  
17. Optional: 3 headphone EQ curves.  
18. Optional: always-on matched compressor vs static \(G\).  
19. Re-run checks (`python -m exposure_dsp checks`) so nothing broke.

### Phase 5 — Paper rewrite (3–5 days)

20. New title, abstract, keywords (add “A-weighting,” “K-weighting,” “frequency allocation”).  
21. Intro contribution bullets: (i) matched test; (ii) failure of bass-first; (iii) alignment rule {and empirical reversal if true}.  
22. Theory subsection with \(W_A/W_K\).  
23. Honest limitations (unchanged: no SPL, no MUSHRA unless Phase 6).  
24. Compile IEEE PDF; every number must come from `results/tables`.

### Phase 6 — Optional listeners (2–4 weeks if you do it)

25. Ethics / consent as required by VIT.  
26. Render loudness-matched WAVs; lock volume.  
27. 8+ listeners, 8+ clips, S0/S1/S2.  
28. Add one Results subsection; **then** you may discuss quality.

### Phase 7 — Literature close-out (2–3 days, can overlap Phase 5)

29. IEEE Xplore boolean queries (see walkthrough / earlier novelty canvas):  
    `"sound dose" AND (multiband OR frequency-selective) AND (headphone OR "personal listening")`  
    `(LUFS OR BS.1770) AND (A-weighted OR LAeq) AND (limiter OR compressor)`  
30. AES E-Library: virtual bass + loudness; safe listening.  
31. Google Patents: already have 9980028 / 6826515; search once more.  
32. Scholar “Cited by” on Liang 2023 and H.870.  
33. Update related work if a clone appears. If a clone of the **matched A vs K allocation test** exists, you must cite and shrink the claim.

### Phase 8 — Venue and submission (last steps)

34. Pick venue from §6 given whether S2 reversed the sign and whether you have listeners.  
35. Download that venue’s template (IEEEtran is already in use; confirm page limit, PDF vs IEEE PDF eXpress).  
36. Author checklist: all figures have fonts, captions stand alone, references IEEE style, no “dB SPL,” ethics if listeners.  
37. Internal read: one coauthor, one outsider who did **not** write the code. Ask them: “what is the contribution in one sentence?” If they say “a new limiter,” rewrite.  
38. Submit. Save the submission ID and the frozen PDF + code tag.  
39. If rejected: use reviews; usually they want listeners, more clips, or the patent citation — not a new architecture.

**Last step of this project:** a submitted PDF whose contribution sentence matches the data, plus a tagged repo that regenerates every number.

There is no step after that except revision. Do not add ML or hardware unless a reviewer asks or you start a *second* paper.

---

## 9. Recommended immediate next actions (this week)

If only a few days exist:

1. Weighting-ratio figure (M1)  
2. S2 aligned config + re-run comparison (M2, M3)  
3. Wilcoxon on old and new deltas (M4)  
4. Cite Liang + US 9980028 (M6)  
5. Retitle toward mismatch / alignment (M7)

If S2’s mean \(\Delta L_{Aeq}\) at matched LUFS is **negative**, you have the conference paper.  
If it is **near zero**, write the “meters cannot be gamed” paper and still cite the ratio figure.  
If it is **positive**, something is wrong (mid cut not strong enough, or matching bug) — debug before writing.

---

## 10. Mapping: current sections → what changes in version C

| Current section | Keep | Change |
|---|---|---|
| Abstract | Negative H2 for S1 | Add S2 outcome; retitle-level honesty |
| Intro | Question; “ingredients not new” | Contribution = allocation rule + matched test of two heuristics |
| Related work | Four toolboxes | Patents, Liang, Fathima, C vs A debate |
| Method | S1 as **naive** heuristic | Add theory \(W_A/W_K\); define S2 |
| Implementation | Checks | Note S2 is a config, not new code paths |
| Setup | Matching duals | Three systems; optional C-weighting |
| Results | S1 loss + mechanism | S2 contrast; stats; maybe C-weighting flip |
| Limitations | Proxies, no MUSHRA | S2 still digital; mid cut may harm speech |
| Conclusion | Bass cuts poor for A | Allocation must follow dose weight; S2 {did/did not} reverse |

---

## 11. File-level implementation checklist

When coding starts, tick these:

- [ ] `exposure_dsp/kweighting.py` or K-curve in checks  
- [ ] `paper/figures/weighting_ratio.png`  
- [ ] `ProposedConfig.aligned()` or equivalent preset  
- [ ] `experiment.py` loops S1 + S2  
- [ ] `results/tables/comparison_s1_s2.csv`  
- [ ] `exposure_dsp/stats.py` + `results/tables/stats.json`  
- [ ] `exposure_dsp/cweighting.py` + C columns  
- [ ] `references.bib` new entries  
- [ ] `paper/main.tex` title, abstract, §2, §3 theory, §6 three-system results  
- [ ] `python -m exposure_dsp checks` green  
- [ ] `python -m exposure_dsp experiment` regenerates every number in the PDF  

---

## 12. What “done” means

**Walkthrough (this conversation):** complete. All paper sections explained; notes in `walkthrough_notes.md`.

**This audit:** complete as a plan. It is not the new experiment.

**Publishable paper:** not done until Phase 2 has a frozen S2 result and Phase 5 has a PDF whose claims match that result.

Next *code* step: **M1 weighting-ratio figure, then M2 system S2.** Everything else in this file waits on those two signs.
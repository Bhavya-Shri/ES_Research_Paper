# Frequency-adaptive audio limiting — experiment software

Offline Python DSP for the paper:

**Can frequency-selective gain allocation reduce an A-weighted exposure proxy more than a conventional broadband limiter at matched loudness, and preserve quality better at matched exposure?**

This repo implements the experiment. It does not claim calibrated ear-level SPL or hearing-safety outcomes.

IEEE draft (written from the 20-clip comparison): `paper/main.tex`. Figures live in `paper/figures/`. Compile with IEEEtran (Overleaf is enough): `pdflatex main && bibtex main && pdflatex main && pdflatex main`. Regenerating paper plots from existing tables, without re-running DSP: `python paper/make_figures.py`.

## What is implemented

Three systems on the same audio:

1. **Original** — no processing
2. **Broadband limiter** — one A-weighted envelope, one gain for all frequencies
3. **Proposed** — complementary 3-band processor
   - **Low:** sub-bass attenuation + adaptive harmonic synthesis (covers ~40 Hz fundamentals)
   - **Mid:** A-weighted compressor
   - **High:** envelope-driven transient-aware gain

Matching modes:

- **Matched exposure:** frequency-flat gain so both systems have the same digital \(L_{Aeq}\) proxy
- **Matched loudness:** frequency-flat gain so both systems have the same LUFS (ITU-R BS.1770 via `pyloudnorm`)
- **Dynamic limiter** (secondary): the same match using an A-weighted compressor. This often does nothing if the clip never exceeds the threshold; the static-gain baseline is the one that answers “turn everything down.”

Also included: Linkwitz–Riley crossover reconstruction check, harmonic-coverage check, A-weighting curve check, streaming (block vs whole-signal) check, ablation, and a mid-band parameter sweep.

## Setup

Python 3.10+.

```bash
cd ES_Research_Paper
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Commands

Run everything (verification + sweep + comparison):

```bash
python -m exposure_dsp all
```

Individual steps:

```bash
python -m exposure_dsp checks
python -m exposure_dsp sweep
python -m exposure_dsp experiment
python -m exposure_dsp process path\to\file.wav
```

Put real `.wav` files in `audio_in/`. If that folder is empty, the experiment uses built-in synthetic clips so the pipeline can run immediately. **Paper results should use real music and speech.**

## Outputs

| Path | Contents |
|---|---|
| `results/figures/crossover_reconstruction.png` | LR4 vs old Butterworth summing |
| `results/figures/harmonic_coverage.png` | 40–80 Hz tone spectra after low-band processing |
| `results/figures/aweighting_response.png` | Digital A-weighting vs IEC curve |
| `results/figures/matched_loudness_exposure.png` | H2: exposure at matched LUFS |
| `results/figures/matched_exposure_quality.png` | H1: LUFS / LSD at matched exposure |
| `results/figures/ablation_exposure.png` | Component contribution |
| `results/tables/comparison.csv` | Per-clip metrics |
| `results/tables/experiment.json` | Full numeric dump |
| `results/wavs/` | Listen to original / limiter / proposed |

## How to read the numbers

- **`laeq_proxy`** is A-weighted digital RMS + `db_ref=94`. It is **not** ear-canal SPL.
- **Negative `mean_dlaeq_at_matched_lufs`** means the proposed system had a *lower* exposure proxy than flat gain at the same LUFS (the hypothesis you want). A **positive** value is also a valid paper result: it means flat attenuation reduced the A-weighted proxy more efficiently on that material.
- **LSD** is spectral distance, not a listening-test score.
- Built-in clips are synthetic. Drop real `.wav` files in `audio_in/` before treating numbers as paper results.
- Do not paste the Python listings into the IEEE paper. Cite the repo, a block diagram, and these figures.

## Listening-test files

After `python -m exposure_dsp experiment`, use the `*_matched_exposure.wav` files. Same exposure proxy, different processing. Rate overall quality, bass, clarity, and loudness with volume locked.

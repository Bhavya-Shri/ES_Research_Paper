# Frozen S1 record — draft-negative-v1

Date: 13 Sep 2026

This snapshot is the bass-first heuristic (S1) negative result. Do not retune
`ProposedConfig` defaults (`sub_atten_db = -12`, `mid_target_dba = 78`, harmonics on)
to make S1 “win.” S1 is the failed heuristic on purpose.

Copied at freeze:

- `tables/comparison.csv`
- `tables/experiment.json`
- `tables/ablation.csv`
- `tables/param_sweep.json`

`paper/main.tex` was retitled in Phase B of the same day (Step 4). The original
promotional title is recorded in `paper/walkthrough_notes.md`. S1 defaults in
`ProposedConfig` were not changed.

Headline number: `mean_dlaeq_at_matched_lufs = +1.174 dB` (proposed worse than flat gain).

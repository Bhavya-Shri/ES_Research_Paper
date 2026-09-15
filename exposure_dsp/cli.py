"""Command-line entry: checks, experiments, and single-file processing."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from .checks import run_all_checks
from .experiment import load_corpus, run_experiment
from .stats import interpret_s2_mean, load_comparison, run_cweight_stats, run_s1_stats, run_s2_stats
from .io import load_mono, save_wav
from .limiter import BroadbandExposureLimiter
from .metrics import clip_metrics, laeq_proxy, log_spectral_distance
from .paths import TABLES, WAVS, ensure_dirs
from .proposed import ProposedConfig, ProposedProcessor
from .signals import six_tone_plus_noise


def _print_json(obj) -> None:
    print(json.dumps(obj, indent=2, default=_json_default))


def _json_default(o):
    if isinstance(o, (np.floating, np.integer)):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    return str(o)


def cmd_checks(_: argparse.Namespace) -> None:
    results = run_all_checks()
    slim = {k: {kk: vv for kk, vv in v.items() if kk != "tones"} if isinstance(v, dict) else v for k, v in results.items()}
    if "harmonics" in results and "tones" in results["harmonics"]:
        slim["harmonics"]["tones"] = results["harmonics"]["tones"]
    _print_json(slim)
    if not results["all_passed"]:
        raise SystemExit("One or more verification checks failed.")


def cmd_experiment(_: argparse.Namespace) -> None:
    payload = run_experiment()
    _print_json(payload["summary"])
    print(f"Wrote tables to {TABLES}")


def cmd_sweep(_: argparse.Namespace) -> None:
    ensure_dirs()
    fs = 48000.0
    x = six_tone_plus_noise(fs, 2.0)
    ref = laeq_proxy(x, fs)
    rows = []
    for target, ratio in [(82, 2), (80, 3), (78, 4), (76, 4), (74, 6), (72, 8)]:
        cfg = ProposedConfig(fs=fs, mid_target_dba=target, mid_ratio=ratio)
        y = ProposedProcessor(cfg).process(x)
        laeq = laeq_proxy(y, fs)
        rows.append(
            {
                "target_dba": target,
                "ratio": ratio,
                "laeq_proxy": laeq,
                "delta_laeq": laeq - ref,
                "lsd": log_spectral_distance(x, y, fs),
            }
        )
    path = TABLES / "param_sweep.json"
    path.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    _print_json({"reference_laeq": ref, "rows": rows, "path": str(path)})


def cmd_process(args: argparse.Namespace) -> None:
    ensure_dirs()
    x, fs = load_mono(args.input, target_fs=args.fs)
    proposed = ProposedProcessor(ProposedConfig(fs=fs, mid_target_dba=args.target)).process(x)
    limiter = BroadbandExposureLimiter(fs=fs, target_dba=args.target).process(x)
    stem = Path(args.input).stem
    save_wav(WAVS / f"{stem}_original.wav", x, fs)
    save_wav(WAVS / f"{stem}_proposed.wav", proposed, fs)
    save_wav(WAVS / f"{stem}_limiter.wav", limiter, fs)
    report = {
        "original": clip_metrics(x, None, fs),
        "proposed": clip_metrics(proposed, x, fs),
        "limiter": clip_metrics(limiter, x, fs),
        "outputs": str(WAVS),
    }
    _print_json(report)


def cmd_stats(_: argparse.Namespace) -> None:
    s1 = run_s1_stats()
    out = {"s1": {k: v for k, v in s1.items() if k != "per_clip"}}
    rows = load_comparison()
    if any(r.get("system") == "aligned" for r in rows):
        s2 = run_s2_stats()
        mean = s2["n20"]["mean_dlaeq_db"]
        out["s2"] = {k: v for k, v in s2.items() if k != "per_clip"}
        out["gate"] = interpret_s2_mean(mean)
    _print_json(out)


def cmd_cweight(_: argparse.Namespace) -> None:
    payload = run_cweight_stats()
    slim = {k: v for k, v in payload.items() if k != "per_clip"}
    if "s1" in slim and isinstance(slim["s1"], dict):
        slim["s1"] = {k: v for k, v in slim["s1"].items() if k != "stats"} | {
            "n20": slim["s1"]["stats"]["n20"]
        }
    if "s2" in slim and isinstance(slim["s2"], dict):
        slim["s2"] = {k: v for k, v in slim["s2"].items() if k != "stats"} | {
            "n20": slim["s2"]["stats"]["n20"]
        }
    _print_json(slim)


def cmd_list_corpus(_: argparse.Namespace) -> None:
    clips = load_corpus()
    _print_json({"clips": {k: len(v) for k, v in clips.items()}})


def cmd_all(args: argparse.Namespace) -> None:
    cmd_checks(args)
    cmd_sweep(args)
    cmd_stats(args)
    cmd_experiment(args)


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(
        prog="python -m exposure_dsp",
        description="Frequency-adaptive exposure-control DSP: verify, compare, process.",
    )
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("checks", help="Crossover, harmonics, A/K-weighting, streaming tests").set_defaults(func=cmd_checks)
    sub.add_parser("experiment", help="Matched-exposure and matched-loudness comparison").set_defaults(func=cmd_experiment)
    sub.add_parser("sweep", help="Mid-band target/ratio sweep on the synthetic debug signal").set_defaults(func=cmd_sweep)
    sub.add_parser("stats", help="Wilcoxon/bootstrap on frozen matched-LUFS ΔLAeq").set_defaults(func=cmd_stats)
    sub.add_parser(
        "cweight",
        help="IEC C-weighting ΔLCeq at frozen matched-LUFS gains (does not retune knobs)",
    ).set_defaults(func=cmd_cweight)
    sub.add_parser("corpus", help="List loaded clips").set_defaults(func=cmd_list_corpus)
    sp = sub.add_parser("process", help="Process one wav: original / limiter / proposed")
    sp.add_argument("input")
    sp.add_argument("--fs", type=float, default=48000.0)
    sp.add_argument("--target", type=float, default=78.0)
    sp.set_defaults(func=cmd_process)
    sub.add_parser("all", help="Run checks, sweep, and experiment").set_defaults(func=cmd_all)
    args = p.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()

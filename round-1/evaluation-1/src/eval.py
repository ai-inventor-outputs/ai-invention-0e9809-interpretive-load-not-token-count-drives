#!/usr/bin/env python3
"""
Evaluation: Statistical Test of Filler vs Elaboration Length Effects on
LLM numeric-answer variance, with bootstrap mediation via logprob/attention
entropy.

INPUT CONTRACT: requires a long-format (or per-prompt aggregated) table
produced by the depended-on experiment artifact
(gen_art_experiment_1: "Does Prompt Length Destabilize LLM Answers?"),
containing at minimum: model_id, seed_problem_id, content_type,
length_tier, prompt_token_count, numeric_answer (or per-prompt
answer_mean/answer_sd/answer_cv), and entropy_mean (logprob_entropy or
attention_entropy).

This script FAILS FAST (per the plan's explicit instruction) if that input
does not exist rather than fabricating numbers: it searches every path a
compliant experiment artifact could plausibly have written its output to,
and if none is found, writes a schema-conformant eval_out.json whose
metrics_agg and datasets/examples explicitly encode the missing-input
state (verdict=INPUT_CONTRACT_VIOLATION) instead of any statistical claim.
"""

from __future__ import annotations

import gc
import itertools
import json
import logging
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats as sstats

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stdout,
)
log = logging.getLogger("eval")

WORKSPACE = Path(__file__).resolve().parent
RUN_ROOT = WORKSPACE.parents[3]  # .../3_invention_loop/iter_1/gen_art/<this> -> run root is 4 up
# WORKSPACE = .../run_l-N7kpGv9Lri/3_invention_loop/iter_1/gen_art/gen_art_evaluation_1
# parents[0]=gen_art parents[1]=iter_1 parents[2]=3_invention_loop parents[3]=run_l-N7kpGv9Lri
EXPERIMENT_DIR = WORKSPACE.parent / "gen_art_experiment_1"
DATASET_DIR = WORKSPACE.parent / "gen_art_dataset_1"

RNG_SEED = 20260819  # fixed for reproducibility (this run's date, not wall-clock)
N_BOOT_PAIRED = 10_000
N_BOOT_MEDIATION = 5_000
ALPHA = 0.05

REQUIRED_COLS = {
    "model_id",
    "seed_problem_id",
    "content_type",
    "length_tier",
    "prompt_token_count",
}
ANSWER_COLS_PER_SAMPLE = {"numeric_answer"}
ANSWER_COLS_AGGREGATED = {"answer_mean", "answer_sd"}
ENTROPY_COLS = {"logprob_entropy", "attention_entropy", "entropy_mean"}


# ---------------------------------------------------------------------------
# Input discovery
# ---------------------------------------------------------------------------


def list_all_candidate_json_files() -> list[Path]:
    """Every real JSON file under the experiment/dataset workspaces (excluding
    venvs and internal terminal-out files) -- used both for locating the
    real input table and, if none qualifies, as the basis for an honest
    per-file diagnostic audit trail (never fabricated data)."""
    found: list[Path] = []
    for d in (EXPERIMENT_DIR, DATASET_DIR):
        if not d.is_dir():
            continue
        for p in sorted(d.rglob("*.json")):
            if ".venv" in p.parts:
                continue
            if p.name.startswith(".terminal_"):
                continue
            if p.is_file() and p.stat().st_size > 0:
                found.append(p)
    return found


def find_experiment_output() -> Path | None:
    """Locate the experiment artifact's output JSON.

    Searches, in priority order: an explicit contract/schema pointer file
    the experiment may have written, then conventional output filenames,
    then any *.json file directly in the experiment workspace (excluding
    known non-output files), then the same set of checks against the
    dataset artifact (in case the experiment wrote its table there).
    """
    candidates: list[Path] = []

    contract_files = [
        EXPERIMENT_DIR / "eval_contract.json",
        EXPERIMENT_DIR / "output_schema.json",
        EXPERIMENT_DIR / "manifest.json",
    ]
    for cf in contract_files:
        if cf.is_file():
            try:
                manifest = json.loads(cf.read_text())
                for key in ("output_path", "output_file", "method_out", "table_path"):
                    if key in manifest:
                        p = (EXPERIMENT_DIR / manifest[key]).resolve()
                        candidates.append(p)
            except (json.JSONDecodeError, OSError) as e:
                log.warning("Could not parse manifest %s: %s", cf, e)

    conventional_names = [
        "method_out.json",
        "full_method_out.json",
        "experiment_out.json",
        "exp_out.json",
        "results.json",
        "output.json",
    ]
    for d in (EXPERIMENT_DIR, DATASET_DIR):
        for name in conventional_names:
            candidates.append(d / name)

    for d in (EXPERIMENT_DIR, DATASET_DIR):
        if d.is_dir():
            for p in d.rglob("*.json"):
                if ".venv" in p.parts:
                    continue
                if p.name.startswith(".terminal_"):
                    continue
                candidates.append(p)

    seen: set[Path] = set()
    for p in candidates:
        if p in seen:
            continue
        seen.add(p)
        if p.is_file() and p.stat().st_size > 0:
            log.info("Candidate experiment output found: %s (%d bytes)", p, p.stat().st_size)
            return p

    return None


CONTENT_TYPE_MAP = {
    "relevant": "relevant_elaboration",
    "relevant_elaboration": "relevant_elaboration",
    "filler": "irrelevant_filler",
    "irrelevant_filler": "irrelevant_filler",
    "bare": "baseline",
    "baseline": "baseline",
    "control": "baseline",
    "none": "baseline",
}


def _try_adapt_experiment_gen_sol_format(raw: dict) -> pd.DataFrame | None:
    """Adapt this run's actual gen_art_experiment_1 output schema (an
    exp_gen_sol_out-style datasets->examples table with per-example
    ``predict_our_method``/``metadata_*`` fields) into the flat per-prompt-
    cell column names this evaluation's input contract expects.

    Recognized shape (one row per (prompt_id, model) cell, already
    aggregated over that cell's n_samples repeats):
      input: prompt_id (e.g. "seed_000_filler_short")
      output: JSON string with at least "answer_mean"
      predict_our_method: "model=<model_id>"
      metadata_content_type, metadata_length_tier, metadata_token_count,
      metadata_n_valid_samples, metadata_answer_cv, metadata_answer_variance,
      metadata_mean_logprob_entropy_first_k (or metadata_mean_attention_entropy_first_k)
    Returns None if the shape doesn't match (so callers fall back to the
    generic loader / eventually the blocked-state path).
    """
    if "datasets" not in raw:
        return None
    flat_examples: list[dict] = []
    for ds in raw.get("datasets", []):
        flat_examples.extend(ds.get("examples", []))
    if not flat_examples:
        return None

    sample = flat_examples[0]
    if "predict_our_method" not in sample or "metadata_content_type" not in sample:
        return None

    rows = []
    for ex in flat_examples:
        prompt_id = ex.get("input", "")
        parts = prompt_id.split("_")
        seed_problem_id = "_".join(parts[:2]) if len(parts) >= 2 else prompt_id

        model_raw = ex.get("predict_our_method", "")
        model_id = model_raw.split("=", 1)[1] if "=" in model_raw else model_raw

        content_type_raw = str(ex.get("metadata_content_type", ""))
        content_type = CONTENT_TYPE_MAP.get(content_type_raw, content_type_raw)

        answer_variance = ex.get("metadata_answer_variance")
        answer_sd = float(answer_variance) ** 0.5 if isinstance(answer_variance, (int, float)) and answer_variance >= 0 else None

        entropy_val = ex.get("metadata_mean_logprob_entropy_first_k")
        entropy_col_used = "logprob_entropy"
        if entropy_val is None:
            entropy_val = ex.get("metadata_mean_attention_entropy_first_k")
            entropy_col_used = "attention_entropy"

        out_raw = ex.get("output", "")
        answer_mean = None
        try:
            out_parsed = json.loads(out_raw) if isinstance(out_raw, str) else out_raw
            if isinstance(out_parsed, dict):
                answer_mean = out_parsed.get("answer_mean")
        except (json.JSONDecodeError, TypeError):
            pass

        rows.append(
            {
                "model_id": model_id,
                "seed_problem_id": seed_problem_id,
                "prompt_id": prompt_id,
                "content_type": content_type,
                "length_tier": ex.get("metadata_length_tier"),
                "prompt_token_count": ex.get("metadata_token_count"),
                "answer_mean": answer_mean,
                "answer_sd": answer_sd,
                "answer_cv": ex.get("metadata_answer_cv"),
                "n_valid_samples": ex.get("metadata_n_valid_samples"),
                "frac_correct": ex.get("metadata_frac_correct"),
                "low_n_flag": ex.get("metadata_low_n_flag"),
                "entropy_mean": entropy_val,
                entropy_col_used: entropy_val,
            }
        )
    df = pd.DataFrame(rows)
    return df if not df.empty else None


def load_table(path: Path) -> pd.DataFrame | None:
    """Load a candidate experiment-output JSON into a flat DataFrame.

    Handles either a bare list of row-dicts, or a dict wrapping a list
    under a common key (rows/data/table/examples/results). First tries the
    known gen_art_experiment_1 output shape (see
    ``_try_adapt_experiment_gen_sol_format``); falls back to a generic
    flattener for any other shape.
    """
    try:
        raw = json.loads(path.read_text())
    except (json.JSONDecodeError, OSError) as e:
        log.warning("Failed to parse %s: %s", path, e)
        return None

    if isinstance(raw, dict):
        adapted = _try_adapt_experiment_gen_sol_format(raw)
        if adapted is not None:
            log.info("Adapted %s via known experiment output schema (%d rows)", path, len(adapted))
            return adapted

    rows: Any = None
    if isinstance(raw, list):
        rows = raw
    elif isinstance(raw, dict):
        for key in ("rows", "data", "table", "examples", "results", "prompts"):
            if key in raw and isinstance(raw[key], list):
                rows = raw[key]
                break
        if rows is None and "datasets" in raw:
            # exp_gen_sol_out-style: datasets -> examples (generic flatten, no column remap)
            flat = []
            for ds in raw.get("datasets", []):
                for ex in ds.get("examples", []):
                    flat.append(ex)
            rows = flat

    if not rows:
        return None

    try:
        df = pd.DataFrame(rows)
    except (ValueError, TypeError) as e:
        log.warning("Failed to build DataFrame from %s: %s", path, e)
        return None

    if df.empty:
        return None
    return df


def validate_input_contract(df: pd.DataFrame) -> tuple[bool, list[str]]:
    """Check the loaded table against the plan's INPUT CONTRACT."""
    problems: list[str] = []
    missing_required = REQUIRED_COLS - set(df.columns)
    if missing_required:
        problems.append(f"missing required columns: {sorted(missing_required)}")

    has_per_sample_answer = bool(ANSWER_COLS_PER_SAMPLE & set(df.columns))
    has_aggregated_answer = ANSWER_COLS_AGGREGATED.issubset(set(df.columns))
    if not (has_per_sample_answer or has_aggregated_answer):
        problems.append(
            "no usable answer columns: need 'numeric_answer' (per-sample) or "
            "both 'answer_mean' and 'answer_sd' (pre-aggregated)"
        )

    has_entropy = bool(ENTROPY_COLS & set(df.columns))
    if not has_entropy:
        problems.append(
            "no entropy column found: need one of "
            f"{sorted(ENTROPY_COLS)} to test the mediation hypothesis"
        )

    return (len(problems) == 0), problems


# ---------------------------------------------------------------------------
# Aggregation: per-sample rows -> per-prompt cells
# ---------------------------------------------------------------------------


def to_numeric_answer(x: Any) -> float | None:
    if x is None:
        return None
    if isinstance(x, (int, float)) and not isinstance(x, bool):
        v = float(x)
        return v if np.isfinite(v) else None
    if isinstance(x, str):
        s = x.strip().replace(",", "")
        try:
            v = float(s)
            return v if np.isfinite(v) else None
        except ValueError:
            import re

            m = re.findall(r"-?\d+\.?\d*", s)
            if m:
                try:
                    v = float(m[-1])
                    return v if np.isfinite(v) else None
                except ValueError:
                    return None
            return None
    return None


def aggregate_to_per_prompt(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Aggregate a per-sample table to one row per prompt cell.

    Returns the aggregated frame plus a dict of exclusion bookkeeping
    required by the plan (excluded seed_problem cells and why, refusal
    rates per cell).
    """
    exclusions: dict[str, Any] = {"cv_undefined_excluded": [], "refusal_rates": {}}

    group_keys = [c for c in ("model_id", "seed_problem_id", "content_type", "length_tier") if c in df.columns]

    entropy_col = next((c for c in ("entropy_mean", "logprob_entropy", "attention_entropy") if c in df.columns), None)

    if "numeric_answer" in df.columns:
        df = df.copy()
        df["_parsed_answer"] = df["numeric_answer"].map(to_numeric_answer)
        n_total = df.groupby(group_keys, dropna=False).size().rename("n_total_samples")
        valid = df.dropna(subset=["_parsed_answer"])
        n_valid = valid.groupby(group_keys, dropna=False).size().rename("n_valid_samples")
        answer_mean = valid.groupby(group_keys, dropna=False)["_parsed_answer"].mean().rename("answer_mean")
        answer_sd = valid.groupby(group_keys, dropna=False)["_parsed_answer"].std(ddof=1).rename("answer_sd")
        tok = df.groupby(group_keys, dropna=False)["prompt_token_count"].mean().rename("prompt_token_count")
        parts = [n_total, n_valid, answer_mean, answer_sd, tok]
        if entropy_col:
            ent = df.groupby(group_keys, dropna=False)[entropy_col].mean().rename("entropy_mean")
            parts.append(ent)
        agg = pd.concat(parts, axis=1).reset_index()
        agg["refusal_rate"] = 1.0 - (agg["n_valid_samples"].fillna(0) / agg["n_total_samples"].replace(0, np.nan))
    else:
        agg = df.copy()
        if entropy_col and entropy_col != "entropy_mean":
            agg["entropy_mean"] = agg[entropy_col]
        if "n_valid_samples" not in agg.columns:
            agg["n_valid_samples"] = np.nan
        if "refusal_rate" not in agg.columns:
            agg["refusal_rate"] = np.nan

    def _safe_cv(row) -> float | None:
        m, s = row.get("answer_mean"), row.get("answer_sd")
        if m is None or s is None or pd.isna(m) or pd.isna(s):
            return None
        if abs(m) < 1e-9:
            return None
        return float(s) / abs(float(m))

    agg["answer_cv"] = agg.apply(_safe_cv, axis=1)
    n_before = len(agg)
    undefined = agg[agg["answer_cv"].isna()]
    for _, r in undefined.iterrows():
        exclusions["cv_undefined_excluded"].append(
            {
                "seed_problem_id": r.get("seed_problem_id"),
                "model_id": r.get("model_id"),
                "content_type": r.get("content_type"),
                "length_tier": r.get("length_tier"),
                "reason": "answer_mean is 0 or missing sd/mean -> CV undefined",
            }
        )
    exclusions["n_cells_before_cv_filter"] = n_before
    exclusions["n_cells_excluded_cv_undefined"] = len(undefined)
    agg = agg[agg["answer_cv"].notna()].reset_index(drop=True)
    return agg, exclusions


# ---------------------------------------------------------------------------
# Statistical primitives
# ---------------------------------------------------------------------------


def paired_bootstrap_ci(
    diffs: np.ndarray, n_boot: int, rng: np.random.Generator, alpha: float = ALPHA
) -> dict[str, float]:
    if len(diffs) == 0:
        return {"mean": float("nan"), "ci_lo": float("nan"), "ci_hi": float("nan"), "n": 0}
    boots = np.empty(n_boot)
    n = len(diffs)
    idx_all = rng.integers(0, n, size=(n_boot, n))
    for i in range(n_boot):
        boots[i] = diffs[idx_all[i]].mean()
    lo, hi = np.percentile(boots, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return {"mean": float(diffs.mean()), "ci_lo": float(lo), "ci_hi": float(hi), "n": int(n)}


def wilcoxon_paired(x: np.ndarray, y: np.ndarray) -> dict[str, Any]:
    d = x - y
    d_nz = d[d != 0]
    if len(d_nz) < 1:
        return {"statistic": None, "p_value": 1.0, "rank_biserial_r": 0.0, "n_nonzero": 0}
    try:
        res = sstats.wilcoxon(x, y, zero_method="wilcox", alternative="two-sided", mode="auto")
        stat, p = float(res.statistic), float(res.pvalue)
    except ValueError:
        return {"statistic": None, "p_value": 1.0, "rank_biserial_r": 0.0, "n_nonzero": int(len(d_nz))}
    n = len(d_nz)
    ranks = sstats.rankdata(np.abs(d_nz))
    w_plus = ranks[d_nz > 0].sum()
    w_minus = ranks[d_nz < 0].sum()
    r_rb = (w_plus - w_minus) / (w_plus + w_minus) if (w_plus + w_minus) > 0 else 0.0
    return {"statistic": stat, "p_value": p, "rank_biserial_r": float(r_rb), "n_nonzero": int(n)}


def sign_test(x: np.ndarray, y: np.ndarray) -> dict[str, Any]:
    d = x - y
    d_nz = d[d != 0]
    n = len(d_nz)
    if n == 0:
        return {"n_pairs": 0, "n_positive": 0, "fraction_positive": float("nan"), "ci_lo": None, "ci_hi": None}
    k = int((d_nz > 0).sum())
    res = sstats.binomtest(k, n, p=0.5)
    ci = res.proportion_ci(confidence_level=1 - ALPHA)
    return {
        "n_pairs": int(n),
        "n_positive": k,
        "fraction_positive": k / n,
        "ci_lo": float(ci.low),
        "ci_hi": float(ci.high),
        "binom_p_value": float(res.pvalue),
    }


def holm_bonferroni(pvals: list[float]) -> list[float]:
    """Holm-Bonferroni step-down correction. Returns adjusted p-values in original order."""
    m = len(pvals)
    if m == 0:
        return []
    order = np.argsort(pvals)
    adj = np.empty(m)
    running_max = 0.0
    for rank, idx in enumerate(order):
        corrected = (m - rank) * pvals[idx]
        running_max = max(running_max, corrected)
        adj[idx] = min(running_max, 1.0)
    return adj.tolist()


def breusch_pagan(resid: np.ndarray, x: np.ndarray) -> dict[str, float]:
    """Simple Breusch-Pagan heteroscedasticity test for a single regressor."""
    n = len(resid)
    if n < 4:
        return {"lm_stat": float("nan"), "p_value": float("nan")}
    sigma2 = np.mean(resid**2)
    if sigma2 <= 0:
        return {"lm_stat": float("nan"), "p_value": float("nan")}
    g = (resid**2) / sigma2
    X = np.column_stack([np.ones(n), x])
    beta, *_ = np.linalg.lstsq(X, g, rcond=None)
    g_hat = X @ beta
    ss_reg = float(np.sum((g_hat - g.mean()) ** 2))
    ss_tot = float(np.sum((g - g.mean()) ** 2))
    r2 = ss_reg / ss_tot if ss_tot > 0 else 0.0
    lm = n * r2
    p = float(1 - sstats.chi2.cdf(lm, df=1))
    return {"lm_stat": float(lm), "p_value": p}


def ols_1var(y: np.ndarray, x: np.ndarray) -> dict[str, Any]:
    """OLS y ~ 1 + x. Returns intercept, slope, residuals, fitted."""
    n = len(y)
    X = np.column_stack([np.ones(n), x])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    fitted = X @ beta
    resid = y - fitted
    return {"intercept": float(beta[0]), "slope": float(beta[1]), "resid": resid, "fitted": fitted}


def ols_2var(y: np.ndarray, x1: np.ndarray, x2: np.ndarray) -> dict[str, Any]:
    """OLS y ~ 1 + x1 + x2."""
    n = len(y)
    X = np.column_stack([np.ones(n), x1, x2])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    fitted = X @ beta
    resid = y - fitted
    return {"intercept": float(beta[0]), "b_x1": float(beta[1]), "b_x2": float(beta[2]), "resid": resid}


def sanitize_json(obj: Any) -> Any:
    """Recursively replace non-finite floats (NaN/Inf) with None so the
    output is strict RFC-8259 JSON (Python's json module otherwise emits
    the non-standard NaN/Infinity/-Infinity tokens)."""
    if isinstance(obj, float):
        return obj if np.isfinite(obj) else None
    if isinstance(obj, (np.floating,)):
        v = float(obj)
        return v if np.isfinite(v) else None
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, dict):
        return {k: sanitize_json(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [sanitize_json(v) for v in obj]
    return obj


def dump_json(payload: dict) -> str:
    return json.dumps(sanitize_json(json.loads(json.dumps(payload, default=str))), indent=2)


def zscore(a: np.ndarray) -> np.ndarray:
    sd = a.std(ddof=1)
    if sd < 1e-12:
        return np.zeros_like(a)
    return (a - a.mean()) / sd


# ---------------------------------------------------------------------------
# Metric 1: paired filler-vs-elaboration variance comparison
# ---------------------------------------------------------------------------


def metric1_paired_cv(agg: pd.DataFrame, rng: np.random.Generator) -> dict[str, Any]:
    out: dict[str, Any] = {"per_cell": [], "pooled_per_model": [], "pooled_overall": None}

    filler = agg[agg["content_type"] == "irrelevant_filler"]
    elab = agg[agg["content_type"] == "relevant_elaboration"]

    cell_results = []
    for (model, tier), fgrp in filler.groupby(["model_id", "length_tier"], dropna=False):
        egrp = elab[(elab["model_id"] == model) & (elab["length_tier"] == tier)]
        merged = fgrp.merge(egrp, on="seed_problem_id", suffixes=("_filler", "_elab"))
        if merged.empty:
            continue
        d = (merged["answer_cv_filler"] - merged["answer_cv_elab"]).to_numpy()
        wilc = wilcoxon_paired(merged["answer_cv_filler"].to_numpy(), merged["answer_cv_elab"].to_numpy())
        boot = paired_bootstrap_ci(d, N_BOOT_PAIRED, rng)
        sgn = sign_test(merged["answer_cv_filler"].to_numpy(), merged["answer_cv_elab"].to_numpy())
        cell_results.append(
            {
                "model_id": model,
                "length_tier": tier,
                "n_pairs": int(len(merged)),
                "wilcoxon": wilc,
                "bootstrap_mean_diff_ci": boot,
                "sign_test": sgn,
                "meets_criterion1_uncorrected": bool(boot["mean"] > 0 and wilc["p_value"] < ALPHA),
            }
        )

    pvals = [c["wilcoxon"]["p_value"] for c in cell_results]
    adj = holm_bonferroni(pvals)
    for c, p_adj in zip(cell_results, adj):
        c["wilcoxon"]["p_value_holm"] = p_adj
        c["meets_criterion1_corrected"] = bool(c["bootstrap_mean_diff_ci"]["mean"] > 0 and p_adj < ALPHA)
        c["reverse_direction_flag"] = bool(c["bootstrap_mean_diff_ci"]["mean"] < 0 and p_adj < ALPHA)
    out["per_cell"] = cell_results

    for model, fgrp in filler.groupby("model_id"):
        egrp = elab[elab["model_id"] == model]
        merged = fgrp.merge(egrp, on="seed_problem_id", suffixes=("_filler", "_elab"))
        if merged.empty:
            continue
        d = (merged["answer_cv_filler"] - merged["answer_cv_elab"]).to_numpy()
        wilc = wilcoxon_paired(merged["answer_cv_filler"].to_numpy(), merged["answer_cv_elab"].to_numpy())
        boot = paired_bootstrap_ci(d, N_BOOT_PAIRED, rng)
        out["pooled_per_model"].append(
            {"model_id": model, "n_pairs": int(len(merged)), "wilcoxon": wilc, "bootstrap_mean_diff_ci": boot}
        )

    merged_all = filler.merge(elab, on=["seed_problem_id", "model_id"], suffixes=("_filler", "_elab"))
    if not merged_all.empty:
        seed_ids = merged_all["seed_problem_id"].unique()
        cluster_diffs = merged_all.groupby("seed_problem_id").apply(
            lambda g: (g["answer_cv_filler"] - g["answer_cv_elab"]).mean()
        )
        d_all = cluster_diffs.to_numpy()
        boot = paired_bootstrap_ci(d_all, N_BOOT_PAIRED, rng)
        wilc = wilcoxon_paired(
            merged_all["answer_cv_filler"].to_numpy(), merged_all["answer_cv_elab"].to_numpy()
        )
        out["pooled_overall"] = {
            "n_cluster_seed_problems": int(len(seed_ids)),
            "n_rows_pooled": int(len(merged_all)),
            "wilcoxon_row_level": wilc,
            "cluster_bootstrap_mean_diff_ci": boot,
            "note": "cluster_bootstrap resamples seed_problem_id clusters (mean CV-diff per seed_problem) "
            "to respect non-independence across length_tier/model repeats of the same seed problem",
        }
    return out


# ---------------------------------------------------------------------------
# Metric 2: entropy precondition check
# ---------------------------------------------------------------------------


def metric2_entropy_precondition(agg: pd.DataFrame, rng: np.random.Generator) -> dict[str, Any]:
    if "entropy_mean" not in agg.columns:
        return {"status": "NO_ENTROPY_COLUMN", "per_cell": []}
    out: dict[str, Any] = {"per_cell": []}
    filler = agg[agg["content_type"] == "irrelevant_filler"]
    elab = agg[agg["content_type"] == "relevant_elaboration"]
    for (model, tier), fgrp in filler.groupby(["model_id", "length_tier"], dropna=False):
        egrp = elab[(elab["model_id"] == model) & (elab["length_tier"] == tier)]
        merged = fgrp.merge(egrp, on="seed_problem_id", suffixes=("_filler", "_elab")).dropna(
            subset=["entropy_mean_filler", "entropy_mean_elab"]
        )
        if merged.empty:
            continue
        d = (merged["entropy_mean_filler"] - merged["entropy_mean_elab"]).to_numpy()
        wilc = wilcoxon_paired(merged["entropy_mean_filler"].to_numpy(), merged["entropy_mean_elab"].to_numpy())
        boot = paired_bootstrap_ci(d, N_BOOT_PAIRED, rng)
        out["per_cell"].append(
            {
                "model_id": model,
                "length_tier": tier,
                "n_pairs": int(len(merged)),
                "wilcoxon": wilc,
                "bootstrap_mean_diff_ci": boot,
                "entropy_higher_for_filler": bool(boot["mean"] > 0 and wilc["p_value"] < ALPHA),
            }
        )
    return out


# ---------------------------------------------------------------------------
# Metric 3: bootstrap mediation analysis (Baron-Kenny)
# ---------------------------------------------------------------------------


def length_tier_numeric(agg: pd.DataFrame) -> np.ndarray:
    if "prompt_token_count" in agg.columns and agg["prompt_token_count"].notna().all():
        return agg["prompt_token_count"].to_numpy(dtype=float)
    tiers = agg["length_tier"].astype(str)
    order = {"none": 0, "bare": 0, "control": 0, "short": 1, "medium": 2, "long": 3}
    return tiers.map(lambda t: order.get(t.lower(), np.nan)).to_numpy(dtype=float)


def run_mediation(sub: pd.DataFrame, n_boot: int, rng: np.random.Generator, label: str) -> dict[str, Any] | None:
    sub = sub.dropna(subset=["answer_cv", "entropy_mean"]).copy()
    if len(sub) < 8 or sub["seed_problem_id"].nunique() < 4:
        return None
    x_raw = length_tier_numeric(sub)
    y_raw = sub["answer_cv"].to_numpy(dtype=float)
    m_raw = sub["entropy_mean"].to_numpy(dtype=float)
    valid = np.isfinite(x_raw) & np.isfinite(y_raw) & np.isfinite(m_raw)
    x_raw, y_raw, m_raw = x_raw[valid], y_raw[valid], m_raw[valid]
    sub = sub.loc[valid]
    if len(x_raw) < 8:
        return None

    x, y, m = zscore(x_raw), zscore(y_raw), zscore(m_raw)

    total = ols_1var(y, x)
    c = total["slope"]
    med_model = ols_1var(m, x)
    a = med_model["slope"]
    out_model = ols_2var(y, x, m)
    b, c_prime = out_model["b_x2"], out_model["b_x1"]

    bp = breusch_pagan(total["resid"], x)
    log_transform_used = False
    if bp["p_value"] < ALPHA and (y_raw > 0).all():
        log_transform_used = True
        y_log = zscore(np.log(y_raw))
        total_log = ols_1var(y_log, x)
        out_model_log = ols_2var(y_log, x, m)
        c_log, b_log, c_prime_log = total_log["slope"], out_model_log["b_x2"], out_model_log["b_x1"]
        ab_log = a * b_log
    else:
        ab_log = None

    seed_ids = sub["seed_problem_id"].unique()
    id_to_rows: dict[Any, np.ndarray] = {
        sid: np.where(sub["seed_problem_id"].to_numpy() == sid)[0] for sid in seed_ids
    }
    ab_boots = np.empty(n_boot)
    n_clusters = len(seed_ids)
    for i in range(n_boot):
        sampled_ids = rng.choice(seed_ids, size=n_clusters, replace=True)
        rows = np.concatenate([id_to_rows[sid] for sid in sampled_ids])
        xb, yb, mb = zscore(x_raw[rows]), zscore(y_raw[rows]), zscore(m_raw[rows])
        try:
            a_b = ols_1var(mb, xb)["slope"]
            out_b = ols_2var(yb, xb, mb)
            ab_boots[i] = a_b * out_b["b_x2"]
        except np.linalg.LinAlgError:
            ab_boots[i] = np.nan
    ab_boots = ab_boots[np.isfinite(ab_boots)]
    if len(ab_boots) < n_boot * 0.5:
        ab_ci = (float("nan"), float("nan"))
    else:
        ab_ci = tuple(np.percentile(ab_boots, [2.5, 97.5]))

    ab_point = a * b
    prop_mediated = ab_point / c if abs(c) > 1e-9 else float("nan")

    ci_excludes_zero = bool(ab_ci[0] > 0 or ab_ci[1] < 0) if np.isfinite(ab_ci[0]) else False
    if not ci_excludes_zero:
        verdict = "NOT_MEDIATED"
    elif abs(prop_mediated) < 0.20 or not np.isfinite(prop_mediated):
        verdict = "PARTIALLY_MEDIATED"
    else:
        verdict = "MEDIATED"

    return {
        "label": label,
        "n_rows": int(len(sub)),
        "n_seed_problem_clusters": int(n_clusters),
        "standardized_coefs": {"c_total": float(c), "a_mediator": float(a), "b_outcome": float(b), "c_prime_direct": float(c_prime)},
        "raw_scale_coefs": {"c_total": float(total["slope"]), "b_outcome_raw_approx": float(b) * (y_raw.std(ddof=1) / (m_raw.std(ddof=1) or 1))},
        "indirect_effect_ab": float(ab_point),
        "indirect_effect_bootstrap_ci95": [float(ab_ci[0]), float(ab_ci[1])],
        "n_boot_used": int(len(ab_boots)),
        "proportion_mediated": float(prop_mediated) if np.isfinite(prop_mediated) else None,
        "breusch_pagan_cv_vs_length": bp,
        "log_transform_sensitivity_used": log_transform_used,
        "log_transform_indirect_effect_ab": float(ab_log) if ab_log is not None else None,
        "verdict": verdict,
    }


def metric3_mediation(agg: pd.DataFrame, rng: np.random.Generator) -> dict[str, Any]:
    if "entropy_mean" not in agg.columns:
        return {"status": "NO_ENTROPY_COLUMN", "pooled": None, "per_model": []}
    pooled = run_mediation(agg, N_BOOT_MEDIATION, rng, "pooled_all_models")
    per_model = []
    for model, sub in agg.groupby("model_id"):
        r = run_mediation(sub, N_BOOT_MEDIATION, rng, f"model={model}")
        if r is not None:
            per_model.append(r)
    return {"pooled": pooled, "per_model": per_model}


# ---------------------------------------------------------------------------
# Metric 4: confound / robustness checks
# ---------------------------------------------------------------------------


def metric4_confounds(agg: pd.DataFrame) -> dict[str, Any]:
    out: dict[str, Any] = {}

    tok_stats = (
        agg.groupby(["length_tier", "content_type"], dropna=False)["prompt_token_count"]
        .agg(["mean", "std", "count"])
        .reset_index()
        .to_dict(orient="records")
    )
    out["token_count_by_tier_and_type"] = tok_stats

    length_match_flags = []
    for tier, sub in agg.groupby("length_tier"):
        f = sub[sub["content_type"] == "irrelevant_filler"]["prompt_token_count"]
        e = sub[sub["content_type"] == "relevant_elaboration"]["prompt_token_count"]
        if len(f) == 0 or len(e) == 0:
            continue
        rel_diff = abs(f.mean() - e.mean()) / max(abs(e.mean()), 1e-9)
        length_match_flags.append(
            {
                "length_tier": tier,
                "filler_mean_tokens": float(f.mean()),
                "elaboration_mean_tokens": float(e.mean()),
                "relative_diff": float(rel_diff),
                "length_matched_within_15pct": bool(rel_diff <= 0.15),
            }
        )
    out["length_match_check"] = length_match_flags
    out["length_match_violated"] = any(not r["length_matched_within_15pct"] for r in length_match_flags)

    if "refusal_rate" in agg.columns:
        refusal = (
            agg.groupby(["model_id", "length_tier", "content_type"], dropna=False)["refusal_rate"]
            .mean()
            .reset_index()
            .to_dict(orient="records")
        )
        out["refusal_rate_by_cell"] = refusal
        f_ref = agg[agg["content_type"] == "irrelevant_filler"]["refusal_rate"].mean()
        e_ref = agg[agg["content_type"] == "relevant_elaboration"]["refusal_rate"].mean()
        ratio = (f_ref / e_ref) if (e_ref and e_ref > 0) else float("nan")
        out["refusal_rate_imbalance"] = {
            "filler_mean_refusal": float(f_ref) if pd.notna(f_ref) else None,
            "elaboration_mean_refusal": float(e_ref) if pd.notna(e_ref) else None,
            "ratio_filler_over_elaboration": float(ratio) if np.isfinite(ratio) else None,
            "imbalance_flag_gt_2x": bool(np.isfinite(ratio) and (ratio > 2 or ratio < 0.5)),
        }
    else:
        out["refusal_rate_by_cell"] = []
        out["refusal_rate_imbalance"] = None

    if "entropy_mean" in agg.columns:
        model_family_col = "model_id"
        model_summ = []
        for model, sub in agg.groupby(model_family_col):
            n = sub["seed_problem_id"].nunique()
            model_summ.append({"model_id": model, "n_seed_problems": int(n), "n_rows": int(len(sub))})
        out["model_comparison_scope"] = model_summ
    else:
        out["model_comparison_scope"] = []

    has_attention = "attention_entropy" in agg.columns
    has_logprob = "logprob_entropy" in agg.columns
    if has_attention and has_logprob:
        both = agg.dropna(subset=["attention_entropy", "logprob_entropy"])
        if len(both) >= 3:
            corr = float(np.corrcoef(both["attention_entropy"], both["logprob_entropy"])[0, 1])
        else:
            corr = None
        out["entropy_proxy_correlation"] = {"n_overlap": int(len(both)), "pearson_r": corr}
    else:
        out["entropy_proxy_correlation"] = {
            "status": "SCOPE_LIMITATION_SINGLE_ENTROPY_TYPE",
            "has_attention_entropy": has_attention,
            "has_logprob_entropy": has_logprob,
        }
    return out


# ---------------------------------------------------------------------------
# Final verdict combination
# ---------------------------------------------------------------------------


def combine_verdict(m1: dict, m2: dict, m3: dict, m4: dict) -> tuple[str, str]:
    overall = m1.get("pooled_overall")
    crit1_holds = bool(
        overall
        and overall["cluster_bootstrap_mean_diff_ci"]["ci_lo"] > 0
    )
    crit1_reverse_flagged = any(c.get("reverse_direction_flag") for c in m1.get("per_cell", []))

    pooled_med = m3.get("pooled")
    crit2_holds = bool(pooled_med and pooled_med["verdict"] == "MEDIATED")
    crit2_partial = bool(pooled_med and pooled_med["verdict"] == "PARTIALLY_MEDIATED")

    length_matched = not m4.get("length_match_violated", True)

    rationale_parts = [
        f"criterion1 (filler>elaboration CV, cluster-bootstrap CI on pooled paired diff excludes 0 and is positive): {crit1_holds}.",
        f"criterion1 reverse-direction cells flagged at Holm-corrected p<0.05: {crit1_reverse_flagged}.",
        f"criterion2 (entropy mediates length->CV, pooled Baron-Kenny bootstrap verdict): {pooled_med['verdict'] if pooled_med else 'UNAVAILABLE'}.",
        f"length-matched-prompts precondition (filler/elaboration within 15% tokens per tier): {length_matched}.",
    ]

    if crit1_holds and crit2_holds and length_matched:
        verdict = "CONFIRMED"
    elif (crit1_holds or crit2_holds or crit2_partial) and not (crit1_reverse_flagged and not crit1_holds):
        verdict = "PARTIALLY_CONFIRMED"
    else:
        verdict = "DISCONFIRMED"

    return verdict, " ".join(rationale_parts)


# ---------------------------------------------------------------------------
# Blocked-state output (input contract violated / no upstream data)
# ---------------------------------------------------------------------------


ALL_CONTRACT_COLUMNS = sorted(
    REQUIRED_COLS | ANSWER_COLS_PER_SAMPLE | ANSWER_COLS_AGGREGATED | ENTROPY_COLS
)


def write_blocked_output(reason: str, searched: list[str]) -> None:
    """Write a schema-conformant eval_out.json for the case where the
    experiment artifact has not (yet) produced a usable per-prompt/per-sample
    answer+entropy table. Every example row below is a REAL, individually
    verifiable diagnostic check (which file was found, which contract
    column it does/doesn't have, how many rows it has) -- never a fabricated
    experimental result. eval_* fields are 0/1 pass-fail indicators or
    counts from those real checks, satisfying the output schema's
    'at least one eval_* metric per example' requirement honestly.
    """
    log.error("INPUT CONTRACT VIOLATION: %s", reason)

    candidate_files = list_all_candidate_json_files()
    examples: list[dict[str, Any]] = []

    for p in candidate_files:
        rel = str(p.relative_to(WORKSPACE.parents[1])) if WORKSPACE.parents[1] in p.parents else str(p)
        df = load_table(p)
        n_rows = 0 if df is None else int(len(df))
        cols_present = set() if df is None else set(df.columns)
        for col in ALL_CONTRACT_COLUMNS:
            present = col in cols_present
            examples.append(
                {
                    "input": f"Check whether contract column '{col}' is present and non-empty in "
                    f"candidate file '{rel}' ({n_rows} rows loaded).",
                    "output": (
                        f"PRESENT in {rel}" if present else f"ABSENT from {rel} "
                        f"(columns found: {sorted(cols_present) if cols_present else 'none / file did not parse as a row table'})"
                    ),
                    "metadata_source_file": rel,
                    "metadata_column": col,
                    "predict_column_status": "PRESENT" if present else "ABSENT",
                    "eval_column_present": 1.0 if present else 0.0,
                    "eval_source_n_rows": float(n_rows),
                }
            )
        ok, problems = (False, ["file could not be parsed into a row-oriented table"]) if df is None else validate_input_contract(df)
        examples.append(
            {
                "input": f"Validate the full input contract (all required columns + an answer source + an "
                f"entropy source) against candidate file '{rel}'.",
                "output": "CONTRACT_SATISFIED" if ok else "CONTRACT_VIOLATED: " + "; ".join(problems),
                "metadata_source_file": rel,
                "predict_contract_status": "SATISFIED" if ok else "VIOLATED",
                "eval_full_contract_satisfied": 1.0 if ok else 0.0,
                "eval_source_n_rows": float(n_rows),
            }
        )

    if not candidate_files:
        for path_desc in searched:
            examples.append(
                {
                    "input": f"Search for a usable experiment-output JSON at/under: {path_desc}",
                    "output": "NOT_FOUND: no file exists at this location at evaluation time.",
                    "metadata_search_location": path_desc,
                    "predict_file_status": "NOT_FOUND",
                    "eval_file_found": 0.0,
                }
            )

    examples.append(
        {
            "input": "Overall input-contract verdict for this evaluation run: can Metrics 1-4 "
            "(paired CV comparison, entropy precondition, bootstrap mediation, confound checks) be computed?",
            "output": (
                "NO -- " + reason + ". Statistical metrics were NOT computed and NOT fabricated; "
                "this evaluation fails fast per its own explicit input contract instead of reporting numbers "
                "for data that does not exist."
            ),
            "metadata_verdict": "INPUT_CONTRACT_VIOLATION",
            "predict_overall_verdict": "INPUT_CONTRACT_VIOLATION",
            "eval_metrics_computed": 0.0,
        }
    )

    n_examples = len(examples)
    n_files_with_full_contract = sum(
        1 for ex in examples if ex.get("eval_full_contract_satisfied") == 1.0
    )

    payload = {
        "metadata": {
            "evaluation_name": "Filler vs Elaboration Length Effects on LLM Numeric-Answer Variance",
            "status": "INPUT_CONTRACT_VIOLATION",
            "reason": reason,
            "paths_searched": searched,
            "n_candidate_files_found": len(candidate_files),
            "candidate_files": [str(p) for p in candidate_files],
            "verdict": "INPUT_CONTRACT_VIOLATION",
            "verdict_rationale": (
                "The dataset and experiment artifacts this evaluation depends on have not yet produced a readable "
                f"per-prompt/per-sample answer+entropy table ({reason}). All four planned metrics require that "
                "table; none were computed. This is reported as INPUT_CONTRACT_VIOLATION rather than DISCONFIRMED, "
                "since a disconfirmation requires actually observing data that contradicts the hypothesis, which "
                f"did not happen here. {len(candidate_files)} candidate JSON file(s) were located and individually "
                "audited column-by-column against the contract; see the per-example diagnostic checks below for "
                "exactly which columns each file has and lacks."
            ),
        },
        "metrics_agg": {
            "upstream_data_available": 0.0,
            "n_prompt_cells_evaluated": 0.0,
            "input_contract_satisfied": 0.0,
            "n_candidate_files_checked": float(len(candidate_files)),
            "n_diagnostic_checks": float(n_examples),
            "n_files_satisfying_full_contract": float(n_files_with_full_contract),
        },
        "datasets": [{"dataset": "gen_art_experiment_1_input_contract_audit", "examples": examples}],
    }
    for name in ("eval_out.json", "full_eval_out.json"):
        (WORKSPACE / name).write_text(dump_json(payload))

    def _mini(pl: dict) -> dict:
        pl2 = json.loads(json.dumps(pl, default=str))
        pl2["datasets"][0]["examples"] = pl2["datasets"][0]["examples"][:3]
        return pl2

    def _preview(pl: dict) -> dict:
        def truncate(v):
            if isinstance(v, str) and len(v) > 200:
                return v[:200] + "..."
            if isinstance(v, list):
                return [truncate(x) for x in v[:3]]
            if isinstance(v, dict):
                return {k: truncate(x) for k, x in v.items()}
            return v

        return truncate(_mini(pl))

    (WORKSPACE / "mini_eval_out.json").write_text(dump_json(_mini(payload)))
    (WORKSPACE / "preview_eval_out.json").write_text(dump_json(_preview(payload)))
    log.info(
        "Wrote blocked-state eval_out.json / full/mini/preview variants with %d real diagnostic examples "
        "across %d candidate files.",
        n_examples,
        len(candidate_files),
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    rng = np.random.default_rng(RNG_SEED)

    src = find_experiment_output()
    searched_desc = [
        str(EXPERIMENT_DIR / "eval_contract.json"),
        str(EXPERIMENT_DIR / "manifest.json"),
        str(EXPERIMENT_DIR / "method_out.json"),
        f"{EXPERIMENT_DIR}/**/*.json (recursive, excluding .venv)",
        f"{DATASET_DIR}/**/*.json (recursive, excluding .venv)",
    ]
    if src is None:
        write_blocked_output(
            "no non-empty JSON output file found in the experiment or dataset artifact workspaces",
            searched_desc,
        )
        return

    df = load_table(src)
    if df is None:
        write_blocked_output(
            f"found file {src} but could not parse it into a row-oriented table",
            searched_desc + [str(src)],
        )
        return

    ok, problems = validate_input_contract(df)
    if not ok:
        write_blocked_output(
            f"loaded table from {src} ({len(df)} rows, columns={sorted(df.columns)}) but it violates the "
            f"input contract: {'; '.join(problems)}",
            searched_desc + [str(src)],
        )
        return

    log.info("Loaded valid input table: %s (%d rows) from %s", df.shape, len(df), src)

    agg, exclusions = aggregate_to_per_prompt(df)
    del df
    gc.collect()
    log.info(
        "Aggregated to %d per-prompt cells (%d excluded for CV-undefined)",
        len(agg),
        exclusions["n_cells_excluded_cv_undefined"],
    )

    if agg.empty:
        write_blocked_output(
            "table loaded and validated but aggregation produced zero usable per-prompt cells "
            "(all excluded as CV-undefined or missing required grouping keys)",
            searched_desc + [str(src)],
        )
        return

    log.info("Running Metric 1: paired filler-vs-elaboration variance comparison...")
    m1 = metric1_paired_cv(agg, rng)

    log.info("Running Metric 2: entropy precondition check...")
    m2 = metric2_entropy_precondition(agg, rng)

    log.info("Running Metric 3: bootstrap mediation analysis...")
    m3 = metric3_mediation(agg, rng)

    log.info("Running Metric 4: confound/robustness checks...")
    m4 = metric4_confounds(agg)

    verdict, rationale = combine_verdict(m1, m2, m3, m4)
    log.info("Final verdict: %s", verdict)

    metrics_agg: dict[str, float] = {
        "upstream_data_available": 1.0,
        "n_prompt_cells_evaluated": float(len(agg)),
        "input_contract_satisfied": 1.0,
        "n_seed_problems": float(agg["seed_problem_id"].nunique()),
        "n_models": float(agg["model_id"].nunique()),
        "n_cells_excluded_cv_undefined": float(exclusions["n_cells_excluded_cv_undefined"]),
    }
    if m1.get("pooled_overall"):
        po = m1["pooled_overall"]
        metrics_agg["criterion1_pooled_mean_cv_diff"] = po["cluster_bootstrap_mean_diff_ci"]["mean"]
        metrics_agg["criterion1_pooled_ci_lo"] = po["cluster_bootstrap_mean_diff_ci"]["ci_lo"]
        metrics_agg["criterion1_pooled_ci_hi"] = po["cluster_bootstrap_mean_diff_ci"]["ci_hi"]
    if m3.get("pooled"):
        pm = m3["pooled"]
        metrics_agg["criterion2_indirect_effect_ab"] = pm["indirect_effect_ab"]
        metrics_agg["criterion2_proportion_mediated"] = pm["proportion_mediated"] if pm["proportion_mediated"] is not None else float("nan")
    metrics_agg["length_match_violated"] = 1.0 if m4.get("length_match_violated") else 0.0

    # One example per actually-evaluated per-prompt cell (real aggregated data,
    # not fabricated), each carrying its own eval_* numeric fields -- this is
    # what drives the per-example metric coverage required by the output schema.
    examples: list[dict[str, Any]] = []
    for _, row in agg.iterrows():
        cv = row.get("answer_cv")
        ent = row.get("entropy_mean") if "entropy_mean" in agg.columns else None
        examples.append(
            {
                "input": f"Per-prompt-cell aggregate for seed_problem_id={row.get('seed_problem_id')}, "
                f"model_id={row.get('model_id')}, content_type={row.get('content_type')}, "
                f"length_tier={row.get('length_tier')}: answer_cv, entropy_mean, sample validity.",
                "output": (
                    f"answer_cv={cv:.6g}" if cv is not None and pd.notna(cv) else "answer_cv=NA"
                )
                + (f", entropy_mean={ent:.6g}" if ent is not None and pd.notna(ent) else ", entropy_mean=NA")
                + f", n_valid_samples={row.get('n_valid_samples')}, refusal_rate={row.get('refusal_rate')}",
                "metadata_model_id": str(row.get("model_id")),
                "metadata_seed_problem_id": str(row.get("seed_problem_id")),
                "metadata_content_type": str(row.get("content_type")),
                "metadata_length_tier": str(row.get("length_tier")),
                "predict_answer_cv": f"{cv:.6g}" if cv is not None and pd.notna(cv) else "NA",
                "eval_answer_cv": float(cv) if cv is not None and pd.notna(cv) else 0.0,
                "eval_entropy_mean": float(ent) if ent is not None and pd.notna(ent) else float("nan"),
                "eval_n_valid_samples": float(row.get("n_valid_samples")) if pd.notna(row.get("n_valid_samples")) else 0.0,
                "eval_refusal_rate": float(row.get("refusal_rate")) if pd.notna(row.get("refusal_rate")) else 0.0,
            }
        )

    # Plus one summary example per metric, carrying the metric's own headline
    # eval_* number so the four statistical analyses are individually visible.
    m1_overall = m1.get("pooled_overall") or {}
    m1_diff = (m1_overall.get("cluster_bootstrap_mean_diff_ci") or {}).get("mean", float("nan"))
    examples.append(
        {
            "input": "Metric 1 summary: paired filler-vs-elaboration CV comparison, pooled cluster-bootstrap "
            "mean difference (CV_filler - CV_elaboration) across all seed_problem_id clusters.",
            "output": json.dumps(sanitize_json(m1))[:20000],
            "metadata_metric": "metric1_paired_cv_comparison",
            "eval_pooled_mean_cv_diff": float(m1_diff) if pd.notna(m1_diff) else 0.0,
        }
    )
    n_precond_pass = sum(1 for c in m2.get("per_cell", []) if c.get("entropy_higher_for_filler"))
    examples.append(
        {
            "input": "Metric 2 summary: entropy precondition check -- fraction of (model, length_tier) cells "
            "where filler entropy is significantly higher than elaboration entropy at matched length.",
            "output": json.dumps(sanitize_json(m2))[:20000],
            "metadata_metric": "metric2_entropy_precondition",
            "eval_fraction_cells_entropy_precondition_holds": (
                n_precond_pass / len(m2["per_cell"]) if m2.get("per_cell") else 0.0
            ),
        }
    )
    pooled_med = m3.get("pooled") or {}
    examples.append(
        {
            "input": "Metric 3 summary: bootstrap mediation analysis (Baron-Kenny), pooled across models -- "
            "indirect effect a*b and proportion mediated for entropy as mediator of length->CV.",
            "output": json.dumps(sanitize_json(m3))[:20000],
            "metadata_metric": "metric3_bootstrap_mediation",
            "eval_indirect_effect_ab": float(pooled_med.get("indirect_effect_ab", 0.0) or 0.0),
            "eval_proportion_mediated": float(pooled_med.get("proportion_mediated") or 0.0),
        }
    )
    examples.append(
        {
            "input": "Metric 4 summary: confound/robustness checks -- length-matching violation flag and "
            "refusal-rate imbalance flag.",
            "output": json.dumps(sanitize_json(m4))[:20000],
            "metadata_metric": "metric4_confound_robustness_checks",
            "eval_length_match_violated": 1.0 if m4.get("length_match_violated") else 0.0,
            "eval_refusal_imbalance_flagged": (
                1.0 if (m4.get("refusal_rate_imbalance") or {}).get("imbalance_flag_gt_2x") else 0.0
            ),
        }
    )

    payload = {
        "metadata": {
            "evaluation_name": "Filler vs Elaboration Length Effects on LLM Numeric-Answer Variance",
            "status": "OK",
            "source_table": str(src),
            "n_boot_paired": N_BOOT_PAIRED,
            "n_boot_mediation": N_BOOT_MEDIATION,
            "alpha": ALPHA,
            "rng_seed": RNG_SEED,
            "cv_exclusions": exclusions,
            "verdict": verdict,
            "verdict_rationale": rationale,
            "metric1_paired_cv_comparison": m1,
            "metric2_entropy_precondition": m2,
            "metric3_bootstrap_mediation": m3,
            "metric4_confound_robustness_checks": m4,
        },
        "metrics_agg": metrics_agg,
        "datasets": [{"dataset": "gen_art_experiment_1_output", "examples": examples}],
    }

    out_path = WORKSPACE / "eval_out.json"
    full_path = WORKSPACE / "full_eval_out.json"
    out_path.write_text(dump_json(payload))
    full_path.write_text(dump_json(payload))

    def _mini(pl: dict) -> dict:
        pl2 = json.loads(json.dumps(pl, default=str))
        pl2["datasets"][0]["examples"] = pl2["datasets"][0]["examples"][:3]
        return pl2

    def _preview(pl: dict) -> dict:
        def truncate(v):
            if isinstance(v, str) and len(v) > 200:
                return v[:200] + "..."
            if isinstance(v, list):
                return [truncate(x) for x in v[:3]]
            if isinstance(v, dict):
                return {k: truncate(x) for k, x in v.items()}
            return v

        return truncate(_mini(pl))

    (WORKSPACE / "mini_eval_out.json").write_text(dump_json(_mini(payload)))
    (WORKSPACE / "preview_eval_out.json").write_text(dump_json(_preview(payload)))
    log.info("Wrote %s, %s, and mini/preview variants (%d examples)", out_path, full_path, len(examples))


if __name__ == "__main__":
    main()

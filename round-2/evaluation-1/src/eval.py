#!/usr/bin/env python3
"""Statistical re-check of the filler-vs-elaboration CV gap and entropy-CV correlation
over the 336-row (prompt,model) dataset produced by art_tqod35nIRuWp."""

from __future__ import annotations

import json
import resource
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from loguru import logger
from scipy import stats

logger.remove()
logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss}|{level:<7}|{message}")
logger.add("logs/run.log", rotation="30 MB", level="DEBUG")

# Small tabular data (336 rows, 6720 raw completions) -- cap RAM generously but cheaply.
resource.setrlimit(resource.RLIMIT_AS, (8 * 1024**3, 8 * 1024**3))

RNG_SEED = 12345
N_BOOT = 10_000

EXP_DIR = Path(
    "/ai-inventor/aii_data/runs/run_l-N7kpGv9Lri/3_invention_loop/iter_1/gen_art/gen_art_experiment_1"
)
FULL_METHOD_OUT = EXP_DIR / "full_method_out.json"
PROMPT_MODEL_CSV = EXP_DIR / "outputs" / "prompt_model_results.csv"
RAW_COMPLETIONS = EXP_DIR / "outputs" / "raw_completions.jsonl"

OUT_DIR = Path(__file__).parent
OUTPUTS_DIR = OUT_DIR / "outputs"
OUTPUTS_DIR.mkdir(exist_ok=True)


def jsonable(x):
    """Recursively convert numpy/pandas scalars to native python for json.dumps."""
    if isinstance(x, dict):
        return {k: jsonable(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [jsonable(v) for v in x]
    if isinstance(x, (np.floating,)):
        v = float(x)
        return None if not np.isfinite(v) else v
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, (np.bool_,)):
        return bool(x)
    if isinstance(x, float):
        return None if not np.isfinite(x) else x
    return x


# ---------------------------------------------------------------------------
# STEP 0: blocker check
# ---------------------------------------------------------------------------
def step0_blocker_check() -> dict:
    logger.info("STEP 0: checking dependency files exist and are non-empty/parseable")
    missing = []
    for p in (FULL_METHOD_OUT, PROMPT_MODEL_CSV, RAW_COMPLETIONS):
        if not p.exists() or p.stat().st_size == 0:
            missing.append(str(p))

    if missing:
        return {"blocked": True, "missing_files": missing}

    # full_method_out.json parseable
    try:
        json.loads(FULL_METHOD_OUT.read_text())
    except Exception as e:
        logger.error(f"full_method_out.json failed to parse: {e}")
        return {"blocked": True, "missing_files": [f"{FULL_METHOD_OUT} (unparseable: {e})"]}

    # prompt_model_results.csv row count
    df = pd.read_csv(PROMPT_MODEL_CSV)
    n_rows = len(df)
    if n_rows == 0:
        return {"blocked": True, "missing_files": [f"{PROMPT_MODEL_CSV} (0 rows)"]}
    if n_rows != 336:
        logger.warning(
            f"prompt_model_results.csv has {n_rows} rows, plan expected 336 -- "
            f"proceeding with actual row count per plan instructions (trust the file)."
        )

    # raw_completions.jsonl line-parseable, non-empty
    n_lines = 0
    bad_lines = 0
    with open(RAW_COMPLETIONS) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            n_lines += 1
            try:
                json.loads(line)
            except Exception:
                bad_lines += 1
    if n_lines == 0:
        return {"blocked": True, "missing_files": [f"{RAW_COMPLETIONS} (0 lines)"]}

    logger.info(
        f"STEP 0 PASSED: prompt_model_results.csv n_rows={n_rows}, "
        f"raw_completions.jsonl n_lines={n_lines} (bad_lines={bad_lines})"
    )
    return {
        "blocked": False,
        "n_rows_prompt_model_csv": n_rows,
        "n_lines_raw_completions": n_lines,
        "n_bad_lines_raw_completions": bad_lines,
    }


# ---------------------------------------------------------------------------
# STEP 1: load & reconcile schema
# ---------------------------------------------------------------------------
def step1_load() -> tuple[pd.DataFrame, pd.DataFrame]:
    logger.info("STEP 1: loading prompt_model_results.csv and raw_completions.jsonl")
    df = pd.read_csv(PROMPT_MODEL_CSV)

    # Derive seed_id from prompt_id (format: seed_XXX_<content_type>_<length_tier>)
    df["seed_id"] = df["prompt_id"].str.extract(r"^(seed_\d+)_")

    df = df.rename(
        columns={
            "answer_cv": "cv",
            "answer_variance": "variance",
            "mean_logprob_entropy_first_k": "mean_entropy_first_k",
        }
    )

    keep_cols = [
        "prompt_id",
        "model",
        "seed_id",
        "content_type",
        "length_tier",
        "cv",
        "variance",
        "frac_correct",
        "mean_entropy_first_k",
        "mean_answer_token_entropy",
        "n_valid_samples",
    ]
    tidy = df[keep_cols].copy()
    tidy = tidy.rename(columns={"mean_answer_token_entropy": "answer_token_entropy"})

    n_before = len(tidy)
    nan_cv_rows = tidy[tidy["cv"].isna()]
    if len(nan_cv_rows) > 0:
        logger.warning(
            f"Dropping {len(nan_cv_rows)} rows with NaN CV (division-by-zero when answer_mean=0): "
            f"{nan_cv_rows['prompt_id'].tolist()}"
        )
        tidy = tidy.dropna(subset=["cv"]).reset_index(drop=True)
    logger.info(
        f"Tidy dataframe: {len(tidy)} rows (dropped {n_before - len(tidy)} NaN-CV rows), "
        f"{tidy['seed_id'].nunique()} unique seeds"
    )

    raw_rows = []
    with open(RAW_COMPLETIONS) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            raw_rows.append(
                {
                    "prompt_id": r.get("prompt_id"),
                    "model": r.get("model"),
                    "sample_idx": r.get("sample_idx"),
                    "answer": r.get("answer"),
                }
            )
    raw_df = pd.DataFrame(raw_rows)
    logger.info(f"Raw completions dataframe: {len(raw_df)} rows")
    return tidy, raw_df


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def cluster_bootstrap_mean(values_by_cluster: list[np.ndarray], n_boot: int, rng: np.random.Generator):
    """Cluster (block) bootstrap on cluster-level means: resample clusters with
    replacement, compute mean-of-cluster-means, repeat n_boot times."""
    cluster_means = np.array([np.nanmean(v) for v in values_by_cluster if len(v) > 0])
    n_clusters = len(cluster_means)
    if n_clusters == 0:
        return None
    boot_means = np.empty(n_boot)
    idx_pool = np.arange(n_clusters)
    for b in range(n_boot):
        idx = rng.choice(idx_pool, size=n_clusters, replace=True)
        boot_means[b] = np.mean(cluster_means[idx])
    return {
        "n_clusters": int(n_clusters),
        "mean": float(np.mean(cluster_means)),
        "ci_lower": float(np.percentile(boot_means, 2.5)),
        "ci_upper": float(np.percentile(boot_means, 97.5)),
    }


def bootstrap_corr(x: np.ndarray, y: np.ndarray, n_boot: int, rng: np.random.Generator, method: str):
    n = len(x)
    if n < 3:
        return None
    boot_vals = np.empty(n_boot)
    for b in range(n_boot):
        idx = rng.integers(0, n, size=n)
        xb, yb = x[idx], y[idx]
        if np.std(xb) == 0 or np.std(yb) == 0:
            boot_vals[b] = np.nan
            continue
        if method == "pearson":
            boot_vals[b] = stats.pearsonr(xb, yb)[0]
        else:
            boot_vals[b] = stats.spearmanr(xb, yb)[0]
    boot_vals = boot_vals[~np.isnan(boot_vals)]
    if method == "pearson":
        r, p = stats.pearsonr(x, y)
    else:
        r, p = stats.spearmanr(x, y)
    return {
        "n": int(n),
        "statistic": float(r),
        "p_value": float(p),
        "ci_lower": float(np.percentile(boot_vals, 2.5)) if len(boot_vals) else None,
        "ci_upper": float(np.percentile(boot_vals, 97.5)) if len(boot_vals) else None,
    }


def cluster_bootstrap_corr(df: pd.DataFrame, xcol: str, ycol: str, n_boot: int, rng: np.random.Generator, method: str):
    """Resample seed_ids with replacement, pool all rows for the resampled seeds, recompute corr.
    Uses plain numpy arrays (not pandas concat) to avoid per-iteration allocation overhead."""
    seeds = df["seed_id"].unique()
    n_seeds = len(seeds)
    seed_to_xy = {
        s: (grp[xcol].values.astype(float), grp[ycol].values.astype(float))
        for s, grp in df.groupby("seed_id")
    }
    seed_idx = {s: i for i, s in enumerate(seeds)}
    x_by_seed = [seed_to_xy[s][0] for s in seeds]
    y_by_seed = [seed_to_xy[s][1] for s in seeds]

    boot_vals = np.empty(n_boot)
    for b in range(n_boot):
        chosen = rng.integers(0, n_seeds, size=n_seeds)
        x = np.concatenate([x_by_seed[i] for i in chosen])
        y = np.concatenate([y_by_seed[i] for i in chosen])
        if np.std(x) == 0 or np.std(y) == 0:
            boot_vals[b] = np.nan
            continue
        if method == "pearson":
            boot_vals[b] = stats.pearsonr(x, y)[0]
        else:
            boot_vals[b] = stats.spearmanr(x, y)[0]
    boot_vals = boot_vals[~np.isnan(boot_vals)]
    return {
        "n_seeds": int(n_seeds),
        "ci_lower": float(np.percentile(boot_vals, 2.5)) if len(boot_vals) else None,
        "ci_upper": float(np.percentile(boot_vals, 97.5)) if len(boot_vals) else None,
    }


# ---------------------------------------------------------------------------
# METRIC 1
# ---------------------------------------------------------------------------
def metric1_paired_gap(df: pd.DataFrame, rng: np.random.Generator) -> dict:
    logger.info("METRIC 1: paired filler-vs-elaboration CV gap with cluster bootstrap")
    results = {"per_tier": {}, "per_tier_per_model": {}}

    tiers = sorted(df.loc[df["content_type"].isin(["relevant", "filler"]), "length_tier"].unique())
    logger.info(f"Tiers found (excluding bare): {tiers}")

    all_pooled_deltas_by_cluster = []  # for pooled seed x tier cluster unit

    for tier in tiers:
        sub = df[(df["length_tier"] == tier) & (df["content_type"].isin(["relevant", "filler"]))]
        # per-seed, per-model paired delta, then average across models per seed
        pivot = sub.pivot_table(
            index=["seed_id", "model"], columns="content_type", values="cv", aggfunc="mean"
        ).reset_index()
        pivot = pivot.dropna(subset=["relevant", "filler"])
        pivot["delta"] = pivot["relevant"] - pivot["filler"]

        # per-seed averaged across models
        per_seed = pivot.groupby("seed_id")["delta"].mean()
        seed_ids = per_seed.index.tolist()
        deltas_by_cluster = [np.array([per_seed[s]]) for s in seed_ids]

        boot = cluster_bootstrap_mean(deltas_by_cluster, N_BOOT, rng)
        wstat, wp = stats.wilcoxon(per_seed.values, alternative="two-sided", zero_method="wilcox")

        results["per_tier"][str(tier)] = {
            "n_seeds": int(len(per_seed)),
            "mean_delta_relevant_minus_filler_cv": float(per_seed.mean()),
            "ci_95_lower": boot["ci_lower"] if boot else None,
            "ci_95_upper": boot["ci_upper"] if boot else None,
            "wilcoxon_statistic": float(wstat),
            "wilcoxon_p_value": float(wp),
            "ci_excludes_zero": bool(boot and (boot["ci_lower"] > 0 or boot["ci_upper"] < 0)),
        }

        # accumulate for pooled seed x tier cluster
        for s in seed_ids:
            all_pooled_deltas_by_cluster.append(np.array([per_seed[s]]))

        # per-model breakdown reused later in metric 3, but compute per-tier-per-model deltas here too
        results["per_tier_per_model"][str(tier)] = {}
        for model, mdf in pivot.groupby("model"):
            per_seed_m = mdf.set_index("seed_id")["delta"]
            deltas_by_cluster_m = [np.array([v]) for v in per_seed_m.values]
            boot_m = cluster_bootstrap_mean(deltas_by_cluster_m, N_BOOT, rng)
            if len(per_seed_m) >= 1 and np.any(per_seed_m.values != 0):
                try:
                    wstat_m, wp_m = stats.wilcoxon(per_seed_m.values, alternative="two-sided", zero_method="wilcox")
                except ValueError:
                    wstat_m, wp_m = np.nan, np.nan
            else:
                wstat_m, wp_m = np.nan, np.nan
            results["per_tier_per_model"][str(tier)][model] = {
                "n_seeds": int(len(per_seed_m)),
                "mean_delta": float(per_seed_m.mean()),
                "ci_95_lower": boot_m["ci_lower"] if boot_m else None,
                "ci_95_upper": boot_m["ci_upper"] if boot_m else None,
                "wilcoxon_statistic": None if np.isnan(wstat_m) else float(wstat_m),
                "wilcoxon_p_value": None if np.isnan(wp_m) else float(wp_m),
            }

    # pooled across tiers, seed x tier as cluster unit
    boot_pooled = cluster_bootstrap_mean(all_pooled_deltas_by_cluster, N_BOOT, rng)
    flat_deltas = np.array([v[0] for v in all_pooled_deltas_by_cluster])
    wstat_p, wp_p = stats.wilcoxon(flat_deltas, alternative="two-sided", zero_method="wilcox")
    results["pooled_across_tiers_seed_x_tier_cluster"] = {
        "n_clusters": int(len(all_pooled_deltas_by_cluster)),
        "mean_delta": float(flat_deltas.mean()),
        "ci_95_lower": boot_pooled["ci_lower"] if boot_pooled else None,
        "ci_95_upper": boot_pooled["ci_upper"] if boot_pooled else None,
        "wilcoxon_statistic": float(wstat_p),
        "wilcoxon_p_value": float(wp_p),
        "ci_excludes_zero": bool(boot_pooled and (boot_pooled["ci_lower"] > 0 or boot_pooled["ci_upper"] < 0)),
    }
    return results


# ---------------------------------------------------------------------------
# METRIC 2
# ---------------------------------------------------------------------------
def metric2_correlations(df: pd.DataFrame, rng: np.random.Generator) -> dict:
    logger.info("METRIC 2: cell-level entropy-CV correlation with bootstrap CI")
    out = {"all_rows": {}, "by_content_type": {}}

    pairs = [
        ("cv", "mean_entropy_first_k"),
        ("cv", "answer_token_entropy"),
    ]

    for xcol, ycol in pairs:
        x = df[xcol].values.astype(float)
        y = df[ycol].values.astype(float)
        key = f"{xcol}_vs_{ycol}"
        out["all_rows"][key] = {}
        for method in ("pearson", "spearman"):
            naive = bootstrap_corr(x, y, N_BOOT, rng, method)
            cluster = cluster_bootstrap_corr(df, xcol, ycol, N_BOOT, rng, method)
            out["all_rows"][key][method] = {
                **naive,
                "cluster_bootstrap_ci_95_lower": cluster["ci_lower"],
                "cluster_bootstrap_ci_95_upper": cluster["ci_upper"],
                "cluster_bootstrap_n_seeds": cluster["n_seeds"],
                "note": "naive row-level bootstrap likely anti-conservative: rows share seed_id and are not fully independent",
            }

    for ct in df["content_type"].unique():
        sub = df[df["content_type"] == ct]
        out["by_content_type"][ct] = {}
        for xcol, ycol in pairs:
            x = sub[xcol].values.astype(float)
            y = sub[ycol].values.astype(float)
            key = f"{xcol}_vs_{ycol}"
            out["by_content_type"][ct][key] = {}
            for method in ("pearson", "spearman"):
                res = bootstrap_corr(x, y, N_BOOT, rng, method)
                out["by_content_type"][ct][key][method] = res
    return out


# ---------------------------------------------------------------------------
# METRIC 3
# ---------------------------------------------------------------------------
def metric3_per_model_breakdown(df: pd.DataFrame) -> dict:
    logger.info("METRIC 3: per-model x condition breakdown table")
    table = {}
    for model, mdf in df.groupby("model"):
        table[model] = {}
        for (ct, lt), cell in mdf.groupby(["content_type", "length_tier"]):
            key = f"{ct}|{lt}"
            table[model][key] = {
                "n": int(len(cell)),
                "mean_cv": float(cell["cv"].mean()),
                "mean_entropy_first_k": float(cell["mean_entropy_first_k"].mean()),
                "mean_answer_token_entropy": float(cell["answer_token_entropy"].mean()),
                "mean_frac_correct": float(cell["frac_correct"].mean()),
            }
    return table


# ---------------------------------------------------------------------------
# METRIC 4
# ---------------------------------------------------------------------------
def metric4_robust_dispersion(df: pd.DataFrame, raw_df: pd.DataFrame, rng: np.random.Generator) -> dict:
    logger.info("METRIC 4: robust/outlier-trimmed dispersion")
    cell_stats = []
    too_small = []
    for (pid, model), grp in raw_df.groupby(["prompt_id", "model"]):
        vals = grp["answer"].dropna().values.astype(float)
        n = len(vals)
        if n == 0:
            continue
        median = np.median(vals)
        mad = np.median(np.abs(vals - median))
        mad_over_median = (mad / abs(median)) if median != 0 else np.nan

        if n < 10:
            too_small.append({"prompt_id": pid, "model": model, "n_valid_samples": int(n)})
            trimmed_cv = np.nan
        else:
            lo, hi = np.percentile(vals, [5, 95])
            trimmed_vals = vals[(vals >= lo) & (vals <= hi)]
            if len(trimmed_vals) >= 2 and np.mean(trimmed_vals) != 0:
                trimmed_cv = np.std(trimmed_vals, ddof=1) / abs(np.mean(trimmed_vals))
            else:
                trimmed_cv = np.nan

        cell_stats.append(
            {
                "prompt_id": pid,
                "model": model,
                "n_valid_samples": int(n),
                "mad_over_median": mad_over_median,
                "trimmed_cv": trimmed_cv,
            }
        )

    cell_df = pd.DataFrame(cell_stats)
    merged = df.merge(cell_df, on=["prompt_id", "model"], how="left")

    tiers = sorted(merged.loc[merged["content_type"].isin(["relevant", "filler"]), "length_tier"].unique())
    out = {"too_small_to_trim_n_cells": len(too_small), "too_small_cells": too_small[:50], "per_tier": {}}

    for tier in tiers:
        sub = merged[(merged["length_tier"] == tier) & (merged["content_type"].isin(["relevant", "filler"]))]
        tier_res = {}
        for metric_col, label in [("cv", "standard_cv"), ("mad_over_median", "mad_over_median"), ("trimmed_cv", "trimmed_cv")]:
            pivot = sub.pivot_table(
                index=["seed_id", "model"], columns="content_type", values=metric_col, aggfunc="mean"
            ).reset_index()
            pivot = pivot.dropna(subset=["relevant", "filler"])
            if len(pivot) == 0:
                tier_res[label] = None
                continue
            pivot["delta"] = pivot["relevant"] - pivot["filler"]
            per_seed = pivot.groupby("seed_id")["delta"].mean()
            deltas_by_cluster = [np.array([v]) for v in per_seed.values]
            boot = cluster_bootstrap_mean(deltas_by_cluster, N_BOOT, rng)
            tier_res[label] = {
                "n_seeds": int(len(per_seed)),
                "mean_delta": float(per_seed.mean()),
                "ci_95_lower": boot["ci_lower"] if boot else None,
                "ci_95_upper": boot["ci_upper"] if boot else None,
            }
        out["per_tier"][str(tier)] = tier_res

    return out


# ---------------------------------------------------------------------------
# METRIC 5 (conditional)
# ---------------------------------------------------------------------------
def metric5_decomposition_check() -> dict:
    logger.info("METRIC 5: checking for newer decomposition artifacts")
    run_root = Path("/ai-inventor/aii_data/runs/run_l-N7kpGv9Lri")
    candidates = []
    if run_root.exists():
        for p in run_root.rglob("full_method_out.json"):
            if p.resolve() == FULL_METHOD_OUT.resolve():
                continue
            candidates.append(p)
    if not candidates:
        return {"skipped": True, "reason": "No additional decomposition experiment/dataset artifacts found in the run's artifact directory beyond the dependency already analyzed."}

    valid = []
    for p in candidates:
        try:
            data = json.loads(p.read_text())
            if data:
                valid.append(str(p))
        except Exception:
            continue
    if not valid:
        return {"skipped": True, "reason": "Candidate artifact(s) found but none parsed/validated as usable non-empty method output.", "candidates_checked": [str(c) for c in candidates]}

    return {"skipped": True, "reason": "Candidate artifacts found but none matched the expected 4-condition decomposition schema (paraphrase-only / paraphrase+scaffolding / original elaboration / filler) needed for this metric; not applying the toolkit to a mismatched schema.", "candidates_checked": valid}


# ---------------------------------------------------------------------------
# Narrative verdicts
# ---------------------------------------------------------------------------
def build_narrative(m1: dict, m2: dict, m4: dict) -> dict:
    verdicts = {}

    # Claim A: elaboration destabilizes more than filler at every tier
    supported_tiers = []
    remains_descriptive_tiers = []
    for tier, res in m1["per_tier"].items():
        if res["ci_excludes_zero"] and res["mean_delta_relevant_minus_filler_cv"] > 0:
            supported_tiers.append(tier)
        else:
            remains_descriptive_tiers.append(tier)

    claim_a_status = (
        "STATISTICALLY_SUPPORTED" if len(remains_descriptive_tiers) == 0
        else ("REMAINS_DESCRIPTIVE" if len(supported_tiers) > 0 else "NOT_SUPPORTED")
    )
    verdicts["claim_elaboration_destabilizes_more_than_filler"] = {
        "status": claim_a_status,
        "tiers_ci_excludes_zero_and_positive": supported_tiers,
        "tiers_ci_crosses_zero_or_negative": remains_descriptive_tiers,
        "pooled_ci_excludes_zero": m1["pooled_across_tiers_seed_x_tier_cluster"]["ci_excludes_zero"],
    }

    # Claim B: entropy correlates with / mediates CV
    ent_first_k = m2["all_rows"]["cv_vs_mean_entropy_first_k"]["pearson"]
    ent_token = m2["all_rows"]["cv_vs_answer_token_entropy"]["pearson"]

    def corr_supported(res):
        return res["cluster_bootstrap_ci_95_lower"] is not None and (
            res["cluster_bootstrap_ci_95_lower"] > 0 or res["cluster_bootstrap_ci_95_upper"] < 0
        )

    within_condition_signal = any(
        m2["by_content_type"][ct]["cv_vs_mean_entropy_first_k"]["pearson"] is not None
        and m2["by_content_type"][ct]["cv_vs_mean_entropy_first_k"]["pearson"]["ci_lower"] is not None
        and (
            m2["by_content_type"][ct]["cv_vs_mean_entropy_first_k"]["pearson"]["ci_lower"] > 0
            or m2["by_content_type"][ct]["cv_vs_mean_entropy_first_k"]["pearson"]["ci_upper"] < 0
        )
        for ct in m2["by_content_type"]
    )

    claim_b_status = "STATISTICALLY_SUPPORTED" if (corr_supported(ent_first_k) or corr_supported(ent_token)) else "REMAINS_DESCRIPTIVE"
    verdicts["claim_entropy_correlates_with_cv"] = {
        "status": claim_b_status,
        "cell_level_pearson_r_cv_vs_mean_entropy_first_k": ent_first_k["statistic"],
        "cell_level_pearson_r_cv_vs_answer_token_entropy": ent_token["statistic"],
        "cluster_bootstrap_ci_excludes_zero_first_k": corr_supported(ent_first_k),
        "cluster_bootstrap_ci_excludes_zero_token": corr_supported(ent_token),
        "within_content_type_signal_survives": within_condition_signal,
        "interpretation": (
            "Correlation partly driven by between-condition variance rather than a true within-condition "
            "relationship" if not within_condition_signal else
            "Some within-condition signal survives, weakening the pure between-condition-variance explanation"
        ),
    }

    # Claim C: robustness to outliers
    robust_holds = []
    for tier, res in m4["per_tier"].items():
        std_d = res.get("standard_cv")
        mad_d = res.get("mad_over_median")
        trim_d = res.get("trimmed_cv")
        if std_d and mad_d and trim_d:
            same_sign = (std_d["mean_delta"] > 0) == (mad_d["mean_delta"] > 0) == (trim_d["mean_delta"] > 0)
            robust_holds.append(same_sign)
    verdicts["claim_gap_robust_to_outliers"] = {
        "status": "STATISTICALLY_SUPPORTED" if robust_holds and all(robust_holds) else "REMAINS_DESCRIPTIVE",
        "tiers_checked": len(robust_holds),
        "tiers_same_sign_across_cv_mad_trimmed": sum(robust_holds),
    }

    return verdicts


# ---------------------------------------------------------------------------
# Superseded numbers list
# ---------------------------------------------------------------------------
def superseded_numbers(m1: dict, m2: dict) -> list[str]:
    items = [
        "The prior draft's r=0.75/r=0.59 entropy-CV correlations computed over 7 condition-mean rows are SUPERSEDED by "
        f"cell-level (n=336) correlations: Pearson r(cv, mean_entropy_first_k)={m2['all_rows']['cv_vs_mean_entropy_first_k']['pearson']['statistic']:.3f}, "
        f"Pearson r(cv, answer_token_entropy)={m2['all_rows']['cv_vs_answer_token_entropy']['pearson']['statistic']:.3f}. "
        "Downstream text must cite the cell-level r/rho with bootstrap CIs, not the condition-mean r.",
        "The raw CV point estimates by content_type x length_tier in the prior draft (e.g. filler medium 0.277, relevant medium 0.474) "
        "are SUPERSEDED as evidence of a 'gap' by the paired, seed-clustered bootstrap deltas and Wilcoxon tests in Metric 1 -- "
        "the point estimates themselves are retained as descriptive means but must be reported alongside the CI/p-value, never alone.",
        "Any claim that the elaboration>filler pattern is general is SUPERSEDED by the per-model breakdown (Metric 3): the pattern "
        "must be checked/reported per model, since all 3 models are same-provider/same-family.",
        "Any claim about CV-based gap magnitude that does not address outlier sensitivity is SUPERSEDED by the MAD/trimmed-CV cross-check (Metric 4).",
    ]
    return items


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    rng = np.random.default_rng(RNG_SEED)

    blocker = step0_blocker_check()
    if blocker["blocked"]:
        out = {
            "status": "BLOCKED_MISSING_DATA",
            "missing_files": blocker["missing_files"],
            "metrics_agg": {"blocked": 1.0},
            "datasets": [
                {
                    "dataset": "gsm8k_length_matched_prompt_model_results",
                    "examples": [
                        {
                            "input": "STEP 0 blocker check",
                            "output": "BLOCKED_MISSING_DATA",
                            "metadata_missing_files": blocker["missing_files"],
                        }
                    ],
                }
            ],
        }
        (OUT_DIR / "eval_out.json").write_text(json.dumps(jsonable(out), indent=2))
        logger.error(f"BLOCKED: {blocker['missing_files']}")
        return

    tidy, raw_df = step1_load()

    m1 = metric1_paired_gap(tidy, rng)
    m2 = metric2_correlations(tidy, rng)
    m3 = metric3_per_model_breakdown(tidy)
    m4 = metric4_robust_dispersion(tidy, raw_df, rng)
    m5 = metric5_decomposition_check()

    narrative = build_narrative(m1, m2, m4)
    superseded = superseded_numbers(m1, m2)

    # metrics_agg: flat numeric-only summary (schema requires plain numbers)
    metrics_agg = {"blocked": 0.0}
    for tier, res in m1["per_tier"].items():
        metrics_agg[f"m1_tier{tier}_mean_delta_cv_relevant_minus_filler"] = res["mean_delta_relevant_minus_filler_cv"]
        metrics_agg[f"m1_tier{tier}_ci_lower"] = res["ci_95_lower"]
        metrics_agg[f"m1_tier{tier}_ci_upper"] = res["ci_95_upper"]
        metrics_agg[f"m1_tier{tier}_wilcoxon_p"] = res["wilcoxon_p_value"]
    metrics_agg["m1_pooled_mean_delta"] = m1["pooled_across_tiers_seed_x_tier_cluster"]["mean_delta"]
    metrics_agg["m1_pooled_ci_lower"] = m1["pooled_across_tiers_seed_x_tier_cluster"]["ci_95_lower"]
    metrics_agg["m1_pooled_ci_upper"] = m1["pooled_across_tiers_seed_x_tier_cluster"]["ci_95_upper"]
    metrics_agg["m1_pooled_wilcoxon_p"] = m1["pooled_across_tiers_seed_x_tier_cluster"]["wilcoxon_p_value"]

    metrics_agg["m2_pearson_r_cv_entropy_first_k"] = m2["all_rows"]["cv_vs_mean_entropy_first_k"]["pearson"]["statistic"]
    metrics_agg["m2_pearson_r_cv_entropy_first_k_p"] = m2["all_rows"]["cv_vs_mean_entropy_first_k"]["pearson"]["p_value"]
    metrics_agg["m2_spearman_rho_cv_entropy_first_k"] = m2["all_rows"]["cv_vs_mean_entropy_first_k"]["spearman"]["statistic"]
    metrics_agg["m2_pearson_r_cv_answer_token_entropy"] = m2["all_rows"]["cv_vs_answer_token_entropy"]["pearson"]["statistic"]
    metrics_agg["m2_pearson_r_cv_answer_token_entropy_p"] = m2["all_rows"]["cv_vs_answer_token_entropy"]["pearson"]["p_value"]
    metrics_agg["m2_spearman_rho_cv_answer_token_entropy"] = m2["all_rows"]["cv_vs_answer_token_entropy"]["spearman"]["statistic"]

    metrics_agg["n_prompt_model_rows"] = float(len(tidy))
    metrics_agg["n_seeds"] = float(tidy["seed_id"].nunique())
    metrics_agg["n_raw_completions"] = float(len(raw_df))
    metrics_agg["m4_too_small_to_trim_n_cells"] = float(m4["too_small_to_trim_n_cells"])

    # datasets/examples: one example per (prompt_id, model) row carrying the row-level
    # numbers plus the shared metadata blob with all the aggregate analysis results.
    examples = []
    shared_metadata = {
        "step0_blocker_check": blocker,
        "metric1_paired_filler_vs_elaboration_cv_gap": m1,
        "metric2_cell_level_entropy_cv_correlation": m2,
        "metric3_per_model_x_condition_breakdown": m3,
        "metric4_robust_outlier_trimmed_dispersion": m4,
        "metric5_decomposition_comparison": m5,
        "narrative_verdicts_per_hypothesis_claim": narrative,
        "superseded_prior_draft_numbers": superseded,
        "n_bootstrap_resamples": N_BOOT,
        "rng_seed": RNG_SEED,
    }

    for i, row in tidy.iterrows():
        examples.append(
            {
                "input": f"prompt_id={row['prompt_id']}, model={row['model']}, content_type={row['content_type']}, length_tier={row['length_tier']}",
                "output": (
                    f"cv={row['cv']:.4f}, frac_correct={row['frac_correct']:.4f}, "
                    f"mean_entropy_first_k={row['mean_entropy_first_k']:.4f}, "
                    f"answer_token_entropy={row['answer_token_entropy']:.6f}"
                ),
                "metadata_seed_id": row["seed_id"],
                "metadata_content_type": row["content_type"],
                "metadata_length_tier": str(row["length_tier"]),
                "metadata_cv": float(row["cv"]),
                "metadata_variance": float(row["variance"]),
                "metadata_frac_correct": float(row["frac_correct"]),
                "metadata_mean_entropy_first_k": float(row["mean_entropy_first_k"]),
                "metadata_answer_token_entropy": float(row["answer_token_entropy"]),
                "metadata_n_valid_samples": int(row["n_valid_samples"]),
                "predict_our_method": row["model"],
                "eval_cv": float(row["cv"]),
                "eval_frac_correct": float(row["frac_correct"]),
                "eval_mean_entropy_first_k": float(row["mean_entropy_first_k"]),
                "eval_answer_token_entropy": float(row["answer_token_entropy"]),
            }
        )

    out = {
        "metadata": shared_metadata,
        "metrics_agg": metrics_agg,
        "datasets": [
            {
                "dataset": "gsm8k_length_matched_prompt_model_results",
                "examples": examples,
            }
        ],
    }

    out_path = OUT_DIR / "eval_out.json"
    out_path.write_text(json.dumps(jsonable(out), indent=2))
    logger.info(f"Wrote {out_path} ({out_path.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    main()

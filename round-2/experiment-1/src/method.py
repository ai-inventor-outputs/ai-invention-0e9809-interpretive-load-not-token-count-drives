#!/usr/bin/env python3
"""Is restatement alone or scaffolding the culprit?

iter-1 found that 'relevant elaboration' (restatement + generic verification
scaffolding, combined) raised answer variance/CV relative to length-matched
irrelevant filler. That condition confounds two mechanisms: redundant
restatement of the problem, and generic verification scaffolding language.
This experiment decomposes it into two new conditions -- paraphrase_only
(pure redundant restatement, no scaffolding) and paraphrase_scaffold
(restatement + scaffolding, length-matched to tier-2 filler) -- and samples
them alongside carried-forward bare control (tier 0) and tier-2 filler rows
from iter-1's dataset, using the IDENTICAL model set, sampling protocol,
answer-extraction cascade, and entropy proxies as iter-1's method.py (ported
verbatim) so results merge into the same schema for direct comparison.

Baseline comparison built into the design: bare control (tier 0, no added
content) is the no-added-content baseline; filler (tier 2, irrelevant
length-matched padding) is the causal control for pure-length effects;
paraphrase_only isolates redundant restatement from scaffolding;
paraphrase_scaffold isolates restatement+scaffolding together
(length-matched to filler) -- so any variance/entropy gap between
paraphrase_only and paraphrase_scaffold isolates the scaffolding effect,
and any gap between paraphrase_only and filler isolates the pure-restatement
effect.
"""
import asyncio
import json
import os
import re
import resource
import sys
import time
from pathlib import Path

import aiohttp
import numpy as np
import pandas as pd
from loguru import logger
from scipy.stats import entropy as scipy_entropy
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

WORKDIR = Path(__file__).parent
ITER1_DATASET = WORKDIR.parent.parent.parent / "iter_1" / "gen_art" / "gen_art_dataset_1" / "full_data_out.json"
PARAPHRASE_DATASET = WORKDIR / "data" / "paraphrase_dataset.json"
OUT_DIR = WORKDIR / "outputs"
OUT_DIR.mkdir(exist_ok=True)
RAW_LOG_PATH = OUT_DIR / "raw_completions.jsonl"
COST_LOG_PATH = OUT_DIR / "cost_log.jsonl"
RESULTS_CSV = OUT_DIR / "prompt_model_results.csv"
METHOD_OUT_PATH = WORKDIR / "method_out.json"

logger.remove()
logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss}|{level:<7}|{message}")
logger.add(WORKDIR / "logs" / "run.log", rotation="30 MB", level="DEBUG")

# --- RAM guard (container limit is large; this workload is tiny text data) ---
resource.setrlimit(resource.RLIMIT_AS, (6 * 1024**3, 6 * 1024**3))

OPENROUTER_API_KEY = os.environ["OPENROUTER_API_KEY"]
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Same 3 OpenAI-hosted models as iter-1 (its smoke test found qwen-2.5-72b
# and llama-3.1-70b return logprobs=null on OpenRouter), for exact
# comparability of the entropy proxy across iterations.
MODELS = ["openai/gpt-4o-mini", "openai/gpt-4.1-mini", "openai/gpt-4.1-nano"]

N_SAMPLES = 15
TEMPERATURE = 0.7
MAX_TOKENS = 400
TOP_LOGPROBS = 5
CARD_MAX_BUDGET_USD = 10.00
ITER1_SPENT_USD = 2.0652959499999946  # from iter-1's method_out.json summary_stats.total_cost_usd
HARD_BUDGET_USD = round(CARD_MAX_BUDGET_USD - ITER1_SPENT_USD - 1.0, 2)  # leave $1 safety margin under the shared $10 cap
CONCURRENCY = 32
FIRST_K_TOKENS = 20

# --- Answer-extraction cascade: ported VERBATIM from iter-1's method.py ---
ANSWER_PATTERNS = [
    re.compile(r"final answer\s*[:=]?\s*\$?(-?[\d,]*\.?\d+)", re.IGNORECASE),
    re.compile(r"\\boxed\{(-?[\d,]*\.?\d+)\}"),
    re.compile(r"\*\*\s*(-?[\d,]*\.?\d+)\s*\*\*"),
    re.compile(r"answer\s*[:=]?\s*\$?(-?[\d,]*\.?\d+)", re.IGNORECASE),
    re.compile(r"(-?[\d,]*\.?\d+)\s*\.?\s*$"),  # last resort: trailing number
]


def extract_numeric_answer(text: str):
    for pat in ANSWER_PATTERNS:
        m = pat.findall(text)
        if m:
            raw = m[-1].replace(",", "")
            try:
                return float(raw)
            except ValueError:
                continue
    return None


def entropy_from_top_logprobs(top_logprobs_list) -> float:
    """Shannon entropy (nats) of the visible top-k token distribution,
    renormalized over the observed mass. Lower bound on true entropy."""
    lps = np.array([tl["logprob"] for tl in top_logprobs_list], dtype=np.float64)
    probs = np.exp(lps)
    s = probs.sum()
    if s <= 0:
        return 0.0
    probs = probs / s
    return float(scipy_entropy(probs))


def locate_answer_token_index(tokens: list[dict], answer: float | None) -> int | None:
    if answer is None:
        return None
    answer_str = ("%g" % answer).lstrip("-")
    for i in range(len(tokens) - 1, -1, -1):
        tok_txt = tokens[i]["token"].strip().replace(",", "")
        if tok_txt and (tok_txt in answer_str or answer_str.startswith(tok_txt)):
            return i
    return None


class BudgetExceeded(Exception):
    pass


class RunningCost:
    def __init__(self, hard_budget: float):
        self.total = 0.0
        self.hard_budget = hard_budget
        self.lock = asyncio.Lock()

    async def add(self, cost: float):
        async with self.lock:
            self.total += cost
            if self.total > self.hard_budget:
                raise BudgetExceeded(f"cumulative cost {self.total:.4f} exceeded {self.hard_budget}")
            return self.total


def already_done_keys() -> set:
    keys = set()
    if RAW_LOG_PATH.exists():
        with open(RAW_LOG_PATH) as f:
            for line in f:
                try:
                    rec = json.loads(line)
                    keys.add((rec["prompt_id"], rec["model"], rec["sample_idx"]))
                except (json.JSONDecodeError, KeyError):
                    continue
    return keys


def append_jsonl(path: Path, record: dict):
    with open(path, "a") as f:
        f.write(json.dumps(record) + "\n")


RETRYABLE = (aiohttp.ClientError, asyncio.TimeoutError)


@retry(
    stop=stop_after_attempt(4),
    wait=wait_exponential(multiplier=1, min=1, max=20),
    retry=retry_if_exception_type(RETRYABLE),
    reraise=True,
)
async def call_openrouter(session: aiohttp.ClientSession, model: str, prompt_text: str):
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt_text}],
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS,
        "logprobs": True,
        "top_logprobs": TOP_LOGPROBS,
    }
    async with session.post(
        OPENROUTER_URL,
        headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"},
        json=payload,
        timeout=aiohttp.ClientTimeout(total=90),
    ) as resp:
        data = await resp.json()
        if resp.status == 429:
            raise aiohttp.ClientError(f"rate limited: {data}")
        if resp.status != 200:
            raise RuntimeError(f"HTTP {resp.status}: {json.dumps(data)[:500]}")
        if "choices" not in data:
            raise RuntimeError(f"malformed response, no choices: {json.dumps(data)[:500]}")
        return data


async def sample_one(session, prompt_row: dict, model: str, sample_idx: int, semaphore, cost_tracker: RunningCost):
    async with semaphore:
      try:
        try:
            resp = await call_openrouter(session, model, prompt_row["prompt_text"])
        except Exception as e:
            logger.error(f"FAILED {prompt_row['prompt_id']} {model} sample={sample_idx}: {e}")
            append_jsonl(
                OUT_DIR / "errors.jsonl",
                {"prompt_id": prompt_row["prompt_id"], "model": model, "sample_idx": sample_idx, "error": str(e)},
            )
            return None

        usage = resp.get("usage", {}) or {}
        cost = float(usage.get("cost") or 0.0)
        append_jsonl(COST_LOG_PATH, {"prompt_id": prompt_row["prompt_id"], "model": model, "cost": cost})
        cumulative = await cost_tracker.add(cost)

        choice = resp["choices"][0]
        text = choice["message"]["content"] or ""
        answer = extract_numeric_answer(text)

        logprobs_obj = choice.get("logprobs")
        tokens = logprobs_obj["content"] if logprobs_obj and logprobs_obj.get("content") else None

        mean_entropy_first_k = None
        answer_token_entropy = None
        if tokens:
            k = min(FIRST_K_TOKENS, len(tokens))
            first_k_entropies = [entropy_from_top_logprobs(t["top_logprobs"]) for t in tokens[:k] if t.get("top_logprobs")]
            if first_k_entropies:
                mean_entropy_first_k = float(np.mean(first_k_entropies))
            ans_idx = locate_answer_token_index(tokens, answer)
            if ans_idx is not None and tokens[ans_idx].get("top_logprobs"):
                answer_token_entropy = entropy_from_top_logprobs(tokens[ans_idx]["top_logprobs"])

        record = {
            "prompt_id": prompt_row["prompt_id"],
            "model": model,
            "sample_idx": sample_idx,
            "content_type": prompt_row["content_type"],
            "length_tier": prompt_row["length_tier"],
            "token_count": prompt_row["token_count"],
            "gold_answer": prompt_row["gold_answer"],
            "raw_text": text[:2000],
            "answer": answer,
            "mean_entropy_first_k": mean_entropy_first_k,
            "answer_token_entropy": answer_token_entropy,
            "has_logprobs": tokens is not None,
            "cost": cost,
        }
        append_jsonl(RAW_LOG_PATH, record)
        logger.debug(
            f"{prompt_row['prompt_id']} {model} #{sample_idx} answer={answer} "
            f"entropy_fk={mean_entropy_first_k} cum_cost=${cumulative:.4f}"
        )
        return record
      except BudgetExceeded:
        raise
      except Exception as e:
        logger.error(f"UNEXPECTED FAILURE {prompt_row.get('prompt_id')} {model} sample={sample_idx}: {e}")
        append_jsonl(
            OUT_DIR / "errors.jsonl",
            {"prompt_id": prompt_row.get("prompt_id"), "model": model, "sample_idx": sample_idx, "error": repr(e)},
        )
        return None


async def run_all(df_prompts: pd.DataFrame, n_samples: int, models: list[str], hard_budget: float) -> RunningCost:
    done = already_done_keys()
    cost_tracker = RunningCost(hard_budget)
    connector = aiohttp.TCPConnector(limit=CONCURRENCY * 2)
    semaphore = asyncio.Semaphore(CONCURRENCY)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        for _, prompt_row in df_prompts.iterrows():
            for model in models:
                for i in range(n_samples):
                    if (prompt_row["prompt_id"], model, i) in done:
                        continue
                    tasks.append(sample_one(session, prompt_row.to_dict(), model, i, semaphore, cost_tracker))
        logger.info(f"Dispatching {len(tasks)} calls (skipped {len(done)} already-done), hard_budget=${hard_budget:.2f}")
        n_ok, n_fail, n_budget_stop = 0, 0, 0
        for coro in asyncio.as_completed(tasks):
            try:
                r = await coro
                if r is not None:
                    n_ok += 1
                else:
                    n_fail += 1
            except BudgetExceeded as e:
                logger.warning(f"HARD BUDGET HIT: {e} -- stopping remaining calls")
                n_budget_stop += 1
                break
        logger.info(f"run_all done: ok={n_ok} fail={n_fail} budget_stopped={n_budget_stop} total_cost=${cost_tracker.total:.4f}")
    return cost_tracker


def load_raw_df() -> pd.DataFrame:
    rows = []
    with open(RAW_LOG_PATH) as f:
        for line in f:
            rows.append(json.loads(line))
    return pd.DataFrame(rows)


def load_prompt_matrix() -> pd.DataFrame:
    """Assemble the call matrix: carried-forward control(tier0)+filler(tier2)
    rows for the 8 CARRY_SEEDS from iter-1's dataset, plus the new
    paraphrase_only / paraphrase_scaffold rows built by build_dataset.py."""
    if not ITER1_DATASET.exists():
        logger.error(f"{ITER1_DATASET} missing")
        raise SystemExit(1)
    if not PARAPHRASE_DATASET.exists():
        logger.error(f"{PARAPHRASE_DATASET} missing -- run build_dataset.py first")
        raise SystemExit(1)

    iter1 = json.loads(ITER1_DATASET.read_text())["datasets"][0]["examples"]
    paraphrase = json.loads(PARAPHRASE_DATASET.read_text())["examples"]

    carry_seeds = sorted(set(r["metadata_seed_id"] for r in paraphrase))
    logger.info(f"CARRY_SEEDS: {carry_seeds}")

    carried = [
        r for r in iter1
        if r["metadata_seed_id"] in carry_seeds
        and (
            (r["metadata_content_type"] == "control" and r["metadata_length_tier"] == 0)
            or (r["metadata_content_type"] == "filler" and r["metadata_length_tier"] == 2)
        )
    ]
    logger.info(f"Carried forward {len(carried)} rows (control tier0 + filler tier2) from iter-1 dataset")
    logger.info(f"New decomposition rows: {len(paraphrase)} (paraphrase_only + paraphrase_scaffold)")

    all_rows = carried + paraphrase
    rows = []
    for r in all_rows:
        rows.append(
            {
                "prompt_id": f"{r['metadata_seed_id']}__{r['metadata_content_type']}__t{r['metadata_length_tier']}",
                "prompt_text": r["input"],
                "gold_answer": float(r["output"]),
                "content_type": r["metadata_content_type"],
                "length_tier": r["metadata_length_tier"],
                "token_count": r["metadata_token_count"],
            }
        )
    df = pd.DataFrame(rows)
    logger.info(f"Total prompt matrix: {len(df)} rows, cells={df.groupby(['content_type','length_tier']).size().to_dict()}")
    return df


def aggregate_results(raw_df: pd.DataFrame) -> pd.DataFrame:
    results = []
    for (prompt_id, model), group in raw_df.groupby(["prompt_id", "model"]):
        valid = group.dropna(subset=["answer"])
        n_valid = len(valid)
        answers = valid["answer"].to_numpy(dtype=float)
        gold = group["gold_answer"].iloc[0]
        if n_valid >= 2:
            answer_mean = float(np.mean(answers))
            answer_sd = float(np.std(answers, ddof=1))
            answer_variance = float(np.var(answers, ddof=1))
            answer_cv = answer_sd / abs(answer_mean) if answer_mean != 0 else float("nan")
            frac_correct = float(np.mean(np.isclose(answers, gold, atol=1e-6)))
        else:
            answer_mean = float(answers[0]) if n_valid == 1 else float("nan")
            answer_sd = float("nan")
            answer_variance = float("nan")
            answer_cv = float("nan")
            frac_correct = float("nan")

        ent_fk = group["mean_entropy_first_k"].dropna()
        ent_ans = group["answer_token_entropy"].dropna()

        results.append(
            {
                "prompt_id": prompt_id,
                "model": model,
                "content_type": group["content_type"].iloc[0],
                "length_tier": int(group["length_tier"].iloc[0]),
                "token_count": int(group["token_count"].iloc[0]),
                "gold_answer": gold,
                "n_samples_attempted": len(group),
                "n_valid_samples": n_valid,
                "pct_unparseable": 1 - n_valid / max(len(group), 1),
                "answer_mean": answer_mean,
                "answer_sd": answer_sd,
                "answer_variance": answer_variance,
                "answer_cv": answer_cv,
                "frac_correct": frac_correct,
                "mean_logprob_entropy_first_k": float(ent_fk.mean()) if len(ent_fk) else None,
                "mean_answer_token_entropy": float(ent_ans.mean()) if len(ent_ans) else None,
                "n_entropy_first_k_obs": int(len(ent_fk)),
                "n_answer_token_entropy_obs": int(len(ent_ans)),
                "low_n_flag": n_valid < 5,
            }
        )
    return pd.DataFrame(results)


def build_summary_stats(results_df: pd.DataFrame, raw_df: pd.DataFrame, cost_tracker: RunningCost, models: list[str], budget_stopped: bool) -> dict:
    models_with_logprobs = sorted(raw_df.loc[raw_df["has_logprobs"], "model"].unique().tolist())
    models_without_logprobs = sorted(set(models) - set(models_with_logprobs))

    def group_mean(col):
        sub = results_df.dropna(subset=[col])
        if sub.empty:
            return {}
        g = sub.groupby(["content_type", "length_tier"])[col].mean()
        return {f"{a}|{b}": float(v) for (a, b), v in g.items()}

    return {
        "n_prompts": int(results_df["prompt_id"].nunique()),
        "n_models": len(models),
        "models_used": models,
        "n_total_calls_attempted": int(len(raw_df)) if not raw_df.empty else 0,
        "n_total_calls_succeeded": int(raw_df["answer"].notna().sum()) if not raw_df.empty else 0,
        "total_cost_usd": float(cost_tracker.total),
        "budget_stopped_early": bool(budget_stopped),
        "mean_cv_by_content_type_length_tier": group_mean("answer_cv"),
        "mean_entropy_first_k_by_content_type_length_tier": group_mean("mean_logprob_entropy_first_k"),
        "mean_answer_token_entropy_by_content_type_length_tier": group_mean("mean_answer_token_entropy"),
        "mean_frac_correct_by_content_type_length_tier": group_mean("frac_correct"),
        "pct_rows_low_n": float(results_df["low_n_flag"].mean()) if len(results_df) else None,
        "pct_rows_missing_logprobs": float(results_df["mean_logprob_entropy_first_k"].isna().mean()) if len(results_df) else None,
        "models_with_logprob_support": models_with_logprobs,
        "models_with_no_logprob_support": models_without_logprobs,
    }


def build_decomposition_comparison(results_df: pd.DataFrame) -> dict:
    """The key comparison this experiment exists to make: does variance/CV
    rise from control -> filler -> paraphrase_only -> paraphrase_scaffold?
    A restatement effect shows as filler < paraphrase_only. A scaffolding
    effect (on top of restatement) shows as paraphrase_only < paraphrase_scaffold."""
    out = {}
    for ct, tier in [("control", 0), ("filler", 2), ("paraphrase_only", 2), ("paraphrase_scaffold", 2)]:
        sub = results_df[(results_df["content_type"] == ct) & (results_df["length_tier"] == tier)]
        out[f"{ct}_mean_cv"] = float(sub["answer_cv"].dropna().mean()) if len(sub) and sub["answer_cv"].notna().any() else None
        out[f"{ct}_mean_variance"] = float(sub["answer_variance"].dropna().mean()) if len(sub) and sub["answer_variance"].notna().any() else None
        out[f"{ct}_mean_frac_correct"] = float(sub["frac_correct"].dropna().mean()) if len(sub) and sub["frac_correct"].notna().any() else None
        out[f"{ct}_mean_entropy_first_k"] = float(sub["mean_logprob_entropy_first_k"].dropna().mean()) if len(sub) and sub["mean_logprob_entropy_first_k"].notna().any() else None
        out[f"{ct}_n_prompt_model_cells"] = int(len(sub))

    def diff(a, b):
        if out.get(a) is None or out.get(b) is None:
            return None
        return out[a] - out[b]

    out["restatement_effect_cv"] = diff("paraphrase_only_mean_cv", "filler_mean_cv")
    out["scaffolding_effect_cv"] = diff("paraphrase_scaffold_mean_cv", "paraphrase_only_mean_cv")
    out["restatement_effect_entropy_first_k"] = diff("paraphrase_only_mean_entropy_first_k", "filler_mean_entropy_first_k")
    out["scaffolding_effect_entropy_first_k"] = diff("paraphrase_scaffold_mean_entropy_first_k", "paraphrase_only_mean_entropy_first_k")
    return out


def to_exp_gen_sol_out(results_df: pd.DataFrame, summary_stats: dict, decomposition_comparison: dict, config: dict, deviations: list) -> dict:
    examples = []
    for _, row in results_df.iterrows():
        examples.append(
            {
                "input": row["prompt_id"],
                "output": json.dumps({"gold_answer": row["gold_answer"], "answer_mean": row["answer_mean"]}),
                "metadata_content_type": row["content_type"],
                "metadata_length_tier": int(row["length_tier"]),
                "metadata_token_count": int(row["token_count"]),
                "metadata_n_valid_samples": int(row["n_valid_samples"]),
                "metadata_answer_cv": None if pd.isna(row["answer_cv"]) else float(row["answer_cv"]),
                "metadata_answer_variance": None if pd.isna(row["answer_variance"]) else float(row["answer_variance"]),
                "metadata_frac_correct": None if pd.isna(row["frac_correct"]) else float(row["frac_correct"]),
                "metadata_mean_logprob_entropy_first_k": row["mean_logprob_entropy_first_k"],
                "metadata_mean_answer_token_entropy": row["mean_answer_token_entropy"],
                "metadata_low_n_flag": bool(row["low_n_flag"]),
                "predict_our_method": f"model={row['model']}",
            }
        )
    return {
        "metadata": {
            "method_name": "paraphrase_restatement_vs_scaffolding_decomposition",
            "description": (
                "Decomposes iter-1's confounded 'relevant elaboration' condition into pure "
                "redundant-restatement (paraphrase_only) and restatement+scaffolding "
                "(paraphrase_scaffold), sampled alongside carried-forward bare control and "
                "length-matched filler, to isolate whether restatement alone or generic "
                "verification scaffolding drives numeric-answer instability."
            ),
            "summary_stats": summary_stats,
            "decomposition_comparison": decomposition_comparison,
            "config": config,
            "deviations_from_plan": deviations,
        },
        "datasets": [
            {
                "dataset": "gsm8k_paraphrase_decomposition",
                "examples": examples,
            }
        ],
    }


DEVIATIONS = [
    (
        "Plan expected a paired sibling dataset artifact producing "
        "paraphrase_only/paraphrase_scaffold prompts. At execution time "
        "iter_2/gen_art/gen_art_dataset_1 has not produced a full_data_out.json, "
        "so per fallback_plan step 1 we constructed both conditions ourselves "
        "in build_dataset.py from iter-1's canonical (question, gold) control "
        "rows, rather than from iter-1's tier-2 'relevant' field -- that field "
        "was found to be corrupted (contains a literal unsubstituted "
        "'{question}' template placeholder and truncates mid-sentence), so "
        "text-surgery on it would have laundered the bug forward. Logged as "
        "'metadata_self_constructed_fallback': true on the new rows."
    ),
    (
        "Reduced N_SAMPLES from the plan's stated 15 only if the hard budget "
        "forces early stop (see budget_stopped_early in summary_stats); "
        "otherwise ran the full 15 samples/cell as planned."
    ),
]


def main():
    t0 = time.time()
    df_prompts = load_prompt_matrix()
    assert set(["prompt_id", "content_type", "length_tier", "prompt_text", "gold_answer"]).issubset(df_prompts.columns)

    n_samples = int(os.environ.get("N_SAMPLES_OVERRIDE", N_SAMPLES))
    models = MODELS
    if os.environ.get("MODELS_OVERRIDE"):
        models = os.environ["MODELS_OVERRIDE"].split(",")
    if os.environ.get("PROMPTS_LIMIT"):
        limit = int(os.environ["PROMPTS_LIMIT"])
        n_cells = df_prompts.groupby(["content_type", "length_tier"]).ngroups
        per_cell = max(1, limit // n_cells)
        df_prompts = (
            df_prompts.groupby(["content_type", "length_tier"], group_keys=False)[df_prompts.columns]
            .apply(lambda g: g.head(per_cell))
            .reset_index(drop=True)
        )
        logger.info(f"PROMPTS_LIMIT applied -> {len(df_prompts)} prompts")

    logger.info(f"Config: n_samples={n_samples} models={models} temp={TEMPERATURE} max_tokens={MAX_TOKENS} hard_budget=${HARD_BUDGET_USD:.2f}")

    cost_tracker = asyncio.run(run_all(df_prompts, n_samples, models, HARD_BUDGET_USD))
    budget_stopped = cost_tracker.total >= HARD_BUDGET_USD

    raw_df = load_raw_df()
    if raw_df.empty:
        logger.error("No raw completions collected -- aborting")
        raise SystemExit(1)
    logger.info(f"Loaded {len(raw_df)} raw completions from disk")

    results_df = aggregate_results(raw_df)
    results_df.to_csv(RESULTS_CSV, index=False)
    logger.info(f"Wrote aggregated results table ({len(results_df)} rows) to {RESULTS_CSV}")

    summary_stats = build_summary_stats(results_df, raw_df, cost_tracker, models, budget_stopped)
    decomposition_comparison = build_decomposition_comparison(results_df)
    logger.info(f"Summary stats: {json.dumps(summary_stats, indent=2)}")
    logger.info(f"Decomposition comparison: {json.dumps(decomposition_comparison, indent=2)}")

    config = {
        "n_samples": n_samples,
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS,
        "top_logprobs": TOP_LOGPROBS,
        "first_k_tokens": FIRST_K_TOKENS,
        "hard_budget_usd": HARD_BUDGET_USD,
        "iter1_prior_spend_usd": ITER1_SPENT_USD,
        "shared_max_budget_usd": CARD_MAX_BUDGET_USD,
    }
    method_out = to_exp_gen_sol_out(results_df, summary_stats, decomposition_comparison, config, DEVIATIONS)
    METHOD_OUT_PATH.write_text(json.dumps(method_out, indent=2))
    logger.info(f"Wrote {METHOD_OUT_PATH} ({METHOD_OUT_PATH.stat().st_size / 1e6:.2f} MB)")
    logger.info(f"Total runtime: {time.time() - t0:.1f}s, total cost ${cost_tracker.total:.4f}")


if __name__ == "__main__":
    main()

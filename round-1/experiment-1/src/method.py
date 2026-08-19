#!/usr/bin/env python3
"""Does prompt length destabilize LLM numeric answers?

Sample matched-content prompts (short/medium/long x relevant-elaboration /
irrelevant-filler + a bare-question control) repeatedly at fixed temperature
across 3 OpenAI-hosted models (via OpenRouter, chosen because they are the
most reliable logprobs source on OpenRouter -- see fallback #1), extract
numeric answers, compute per-(prompt,model) answer variance/CV, and compute
a logprob-entropy proxy per prompt as the candidate mediator of the
length-to-variance relationship.

Baseline comparison built into the same design: the bare-question control
(length_tier='bare') is the no-added-content baseline; content_type='filler'
is the causal control for content_type='relevant' at matched token length
(irrelevant text should not add genuine reasoning value, so any variance/
entropy increase from 'filler' isolates a pure length effect, while any
extra effect from 'relevant' beyond 'filler' isolates a content effect).
"""
import asyncio
import json
import math
import os
import re
import resource
import sys
import time
from collections import defaultdict
from pathlib import Path

import aiohttp
import numpy as np
import pandas as pd
from loguru import logger
from scipy.stats import entropy as scipy_entropy
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

WORKDIR = Path(__file__).parent
DATA_PATH = WORKDIR / "data" / "matched_prompts.json"
OUT_DIR = WORKDIR / "outputs"
OUT_DIR.mkdir(exist_ok=True)
RAW_LOG_PATH = OUT_DIR / "raw_completions.jsonl"
COST_LOG_PATH = OUT_DIR / "cost_log.jsonl"
RESULTS_CSV = OUT_DIR / "prompt_model_results.csv"
METHOD_OUT_PATH = WORKDIR / "method_out.json"

logger.remove()
logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss}|{level:<7}|{message}")
logger.add(WORKDIR / "logs" / "run.log", rotation="30 MB", level="DEBUG")

# --- RAM guard (container limit is 28GB; this workload is tiny text data) ---
resource.setrlimit(resource.RLIMIT_AS, (6 * 1024**3, 6 * 1024**3))

OPENROUTER_API_KEY = os.environ["OPENROUTER_API_KEY"]
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Fallback #1 applied: qwen-2.5-72b and llama-3.1-70b returned logprobs=null
# in the pre-flight smoke test (confirmed empirically below), so per the
# artifact plan's fallback policy we restrict to OpenAI-hosted models only,
# the most reliable logprobs source on OpenRouter.
MODELS = ["openai/gpt-4o-mini", "openai/gpt-4.1-mini", "openai/gpt-4.1-nano"]

N_SAMPLES = 20
TEMPERATURE = 0.7
MAX_TOKENS = 400
TOP_LOGPROBS = 5
HARD_BUDGET_USD = 9.00
CONCURRENCY = 32
FIRST_K_TOKENS = 20

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
    renormalized over the observed mass. This is a LOWER BOUND on the true
    entropy since only the top-k token probabilities are observed."""
    lps = np.array([tl["logprob"] for tl in top_logprobs_list], dtype=np.float64)
    probs = np.exp(lps)
    s = probs.sum()
    if s <= 0:
        return 0.0
    probs = probs / s
    return float(scipy_entropy(probs))


def locate_answer_token_index(tokens: list[dict], answer: float | None) -> int | None:
    """Find the token index whose text plausibly begins the numeric answer
    string, scanning from the end (answers are typically near the end)."""
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


async def run_all(df_prompts: pd.DataFrame, n_samples: int, models: list[str]) -> RunningCost:
    done = already_done_keys()
    cost_tracker = RunningCost(HARD_BUDGET_USD)
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
        logger.info(f"Dispatching {len(tasks)} calls (skipped {len(done)} already-done)")
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


def aggregate_results(raw_df: pd.DataFrame, n_samples_target: int) -> pd.DataFrame:
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
                "length_tier": group["length_tier"].iloc[0],
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


def build_baseline_comparison(results_df: pd.DataFrame) -> dict:
    """Baseline comparison built into the design: bare-question control
    (no added content) vs the length-tiered relevant/filler variants, and
    filler-vs-relevant at matched length (content-effect isolation)."""
    out = {}
    bare = results_df[results_df["length_tier"] == "bare"]
    out["bare_control_mean_cv"] = float(bare["answer_cv"].dropna().mean()) if len(bare) else None
    out["bare_control_mean_frac_correct"] = float(bare["frac_correct"].dropna().mean()) if len(bare) else None
    for tier in ["short", "medium", "long"]:
        for ct in ["relevant", "filler"]:
            sub = results_df[(results_df["length_tier"] == tier) & (results_df["content_type"] == ct)]
            out[f"{ct}_{tier}_mean_cv"] = float(sub["answer_cv"].dropna().mean()) if len(sub) else None
            out[f"{ct}_{tier}_mean_frac_correct"] = float(sub["frac_correct"].dropna().mean()) if len(sub) else None
    return out


def to_exp_gen_sol_out(results_df: pd.DataFrame, raw_df: pd.DataFrame, summary_stats: dict, baseline_comparison: dict, config: dict) -> dict:
    prompts_by_id = raw_df.drop_duplicates("prompt_id").set_index("prompt_id")
    examples = []
    for _, row in results_df.iterrows():
        pid = row["prompt_id"]
        prompt_text = None
        if pid in prompts_by_id.index:
            prompt_text = None  # raw_text is the completion, not the prompt; fetch separately below
        examples.append(
            {
                "input": pid,
                "output": json.dumps(
                    {"gold_answer": row["gold_answer"], "answer_mean": row["answer_mean"]}
                ),
                "metadata_content_type": row["content_type"],
                "metadata_length_tier": row["length_tier"],
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
            "method_name": "prompt_length_answer_variance_entropy",
            "description": "Per-(prompt,model) numeric-answer variance/CV and logprob-entropy proxy across matched-length prompt conditions",
            "summary_stats": summary_stats,
            "baseline_comparison": baseline_comparison,
            "config": config,
        },
        "datasets": [
            {
                "dataset": "gsm8k_length_matched_prompts",
                "examples": examples,
            }
        ],
    }


def main():
    t0 = time.time()
    logger.info("Loading matched-prompt dataset")
    if not DATA_PATH.exists():
        logger.error(f"{DATA_PATH} missing -- run build_dataset.py first")
        raise SystemExit(1)
    dataset = json.loads(DATA_PATH.read_text())
    df_prompts = pd.DataFrame(dataset["prompts"])
    assert set(["prompt_id", "content_type", "length_tier", "prompt_text", "gold_answer"]).issubset(df_prompts.columns)
    logger.info(f"Loaded {len(df_prompts)} prompts, tiers={df_prompts.length_tier.value_counts().to_dict()}")

    n_samples = int(os.environ.get("N_SAMPLES_OVERRIDE", N_SAMPLES))
    models = MODELS
    if os.environ.get("MODELS_OVERRIDE"):
        models = os.environ["MODELS_OVERRIDE"].split(",")
    if os.environ.get("PROMPTS_LIMIT"):
        limit = int(os.environ["PROMPTS_LIMIT"])
        # stratified subsample: keep every content_type x length_tier cell non-empty
        n_cells = df_prompts.groupby(["content_type", "length_tier"]).ngroups
        per_cell = max(1, limit // n_cells)
        df_prompts = (
            df_prompts.groupby(["content_type", "length_tier"], group_keys=False)[df_prompts.columns]
            .apply(lambda g: g.head(per_cell))
            .reset_index(drop=True)
        )
        logger.info(f"PROMPTS_LIMIT applied -> {len(df_prompts)} prompts")

    logger.info(f"Config: n_samples={n_samples} models={models} temp={TEMPERATURE} max_tokens={MAX_TOKENS}")

    cost_tracker = asyncio.run(run_all(df_prompts, n_samples, models))
    budget_stopped = cost_tracker.total > HARD_BUDGET_USD * 0.999 and cost_tracker.total >= HARD_BUDGET_USD

    raw_df = load_raw_df()
    if raw_df.empty:
        logger.error("No raw completions collected -- aborting")
        raise SystemExit(1)
    logger.info(f"Loaded {len(raw_df)} raw completions from disk")

    results_df = aggregate_results(raw_df, n_samples)
    results_df.to_csv(RESULTS_CSV, index=False)
    logger.info(f"Wrote aggregated results table ({len(results_df)} rows) to {RESULTS_CSV}")

    summary_stats = build_summary_stats(results_df, raw_df, cost_tracker, models, budget_stopped)
    baseline_comparison = build_baseline_comparison(results_df)
    logger.info(f"Summary stats: {json.dumps(summary_stats, indent=2)}")
    logger.info(f"Baseline comparison: {json.dumps(baseline_comparison, indent=2)}")

    config = {
        "n_samples": n_samples,
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS,
        "top_logprobs": TOP_LOGPROBS,
        "first_k_tokens": FIRST_K_TOKENS,
        "hard_budget_usd": HARD_BUDGET_USD,
    }
    method_out = to_exp_gen_sol_out(results_df, raw_df, summary_stats, baseline_comparison, config)
    METHOD_OUT_PATH.write_text(json.dumps(method_out, indent=2))
    logger.info(f"Wrote {METHOD_OUT_PATH} ({METHOD_OUT_PATH.stat().st_size / 1e6:.2f} MB)")
    logger.info(f"Total runtime: {time.time() - t0:.1f}s, total cost ${cost_tracker.total:.4f}")


if __name__ == "__main__":
    main()

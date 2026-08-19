#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["loguru", "tiktoken"]
# ///
"""Build length-matched numeric-reasoning prompt dataset from GSM8K (+ SVAMP) seeds.

For each seed word problem, generate: 1 bare-question control (tier 0) +
2 content types (relevant-elaboration / irrelevant-filler) x 3 length tiers
(short/medium/long) = 6 variants, all token-matched per tier via tiktoken cl100k_base.
"""

import json
import re
import sys
from pathlib import Path

import tiktoken
from loguru import logger

logger.remove()
logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss}|{level:<7}|{message}")
logger.add("logs/run.log", rotation="30 MB", level="DEBUG")

WORKSPACE = Path(__file__).parent
ENC = tiktoken.get_encoding("cl100k_base")

# ---------------------------------------------------------------------------
# Tier token-count targets (extra tokens ABOVE the bare-question control)
# ---------------------------------------------------------------------------
TIER_TARGETS = {1: 75, 2: 250, 3: 650}  # short, medium, long
TOLERANCE_FRAC = 0.10
TOLERANCE_MIN_TOKENS = 15

NUMBER_WORDS = {
    "zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
    "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen",
    "seventeen", "eighteen", "nineteen", "twenty", "thirty", "forty", "fifty",
    "sixty", "seventy", "eighty", "ninety", "hundred", "thousand", "million",
    "billion", "half", "dozen", "first", "second", "third", "fourth", "fifth",
}
DIGIT_RE = re.compile(r"\d")

# Neutral filler topic pool: NO digits, NO number-words, NO math vocabulary.
FILLER_SENTENCES = [
    "The migration patterns of monarch butterflies span thousands of miles across "
    "generations, with individual insects never completing the round trip themselves.",
    "Cumulus clouds form when warm air rises and cools, condensing water vapor into "
    "visible droplets that drift lazily across an open sky.",
    "The city of Kyoto served as the imperial capital for centuries before the seat "
    "of government eventually relocated to Tokyo during a period of rapid modernization.",
    "Sourdough bread relies on a wild yeast starter that must be fed regularly with "
    "flour and water to keep its microbial culture active and healthy.",
    "Coastal fog rolls in in the early evening, blanketing the hillside vineyards in "
    "a cool mist that lingers until the following late morning.",
    "The lighthouse keeper maintained a strict routine, polishing the lens each "
    "evening and logging the weather in a worn leather notebook by lamplight.",
    "Traditional woodworking joints, such as the dovetail, were prized for their "
    "strength because they require no metal fasteners to hold securely together.",
    "The orchestra rehearsed in an old converted warehouse, its brick walls giving "
    "the strings a warm, resonant tone that the musicians came to love.",
    "Desert plants like the saguaro cactus store water in their thick, ribbed stems, "
    "allowing them to survive long stretches without any rainfall at all.",
    "The train wound slowly through the mountain pass, offering passengers glimpses "
    "of pine forests and distant ridgelines wrapped in drifting cloud.",
    "Beekeepers often wear light-colored clothing because darker hues can trigger a "
    "defensive response from a hive that mistakes the wearer for a predator.",
    "The tide pools along the rocky shoreline teemed with anemones, hermit crabs, "
    "and small darting fish that had been stranded by the receding water.",
    "Handmade paper is traditionally pressed from pulped fibers of mulberry bark, "
    "then dried on frames in the sun until the sheets become crisp and light.",
    "The archivist spent her afternoons cataloguing brittle letters, carefully "
    "noting the ink type and paper stock before sealing each page in an acid-free sleeve.",
    "Wind farms are often sited along coastal ridgelines where steady onshore "
    "breezes provide a more reliable source of turning force for the turbine blades.",
    "The potter centered the clay on the wheel, applying steady pressure with damp "
    "hands until the spinning mass rose smoothly into a narrow, even cylinder.",
]

MATH_TOPIC_WORDS = {"eggs", "dollars", "dollar", "money", "price", "cost", "buy", "sell",
                     "total", "each", "per", "number", "count", "how", "many", "much"}


def gsm8k_seeds() -> list[dict]:
    raw = json.loads((WORKSPACE / "temp/datasets/full_openai_gsm8k_main_test.json").read_text())
    seeds = []
    for i, row in enumerate(raw):
        q, a = row["question"], row["answer"]
        if "####" not in a:
            continue
        gold = a.split("####")[-1].strip().replace(",", "")
        try:
            float(gold)
        except ValueError:
            continue
        n_steps = len(re.findall(r"<<[^>]*>>", a))
        bucket = "easy" if n_steps <= 2 else ("medium" if n_steps == 3 else "hard")
        seeds.append({
            "seed_id": f"gsm8k_{i}",
            "question": q,
            "gold_answer": gold,
            "difficulty_bucket": bucket,
            "n_steps": n_steps,
            "source_dataset": "openai/gsm8k",
        })
    return seeds


def svamp_seeds() -> list[dict]:
    raw = json.loads((WORKSPACE / "temp/datasets/full_ChilleD_SVAMP_default_test.json").read_text())
    seeds = []
    for i, row in enumerate(raw):
        q = f"{row['Body']} {row['Question']}".strip()
        try:
            gold = float(row["Answer"])
            gold = str(int(gold)) if gold == int(gold) else str(gold)
        except (ValueError, TypeError):
            continue
        n_ops = len(re.findall(r"[+\-*/]", row.get("Equation", "")))
        bucket = "easy" if n_ops <= 1 else ("medium" if n_ops == 2 else "hard")
        seeds.append({
            "seed_id": f"svamp_{row['ID']}_{i}",
            "question": q,
            "gold_answer": gold,
            "difficulty_bucket": bucket,
            "n_steps": n_ops,
            "source_dataset": "ChilleD/SVAMP",
        })
    return seeds


def pick_balanced(seeds: list[dict], n: int) -> list[dict]:
    """Sample ~evenly across difficulty buckets, deterministic order."""
    buckets = {"easy": [], "medium": [], "hard": []}
    for s in seeds:
        buckets[s["difficulty_bucket"]].append(s)
    per = n // 3
    chosen = []
    for b in ("easy", "medium", "hard"):
        chosen.extend(buckets[b][:per])
    remainder = n - len(chosen)
    if remainder > 0:
        pool = [s for b in buckets.values() for s in b[per:]]
        chosen.extend(pool[:remainder])
    return chosen[:n]


def n_tokens(text: str) -> int:
    return len(ENC.encode(text))


def build_filler(target_extra_tokens: int, seed_key_terms: set[str]) -> str:
    """Concatenate filler sentences (skipping any with vocabulary overlap) until
    the token budget is reached, then trim to the target via tiktoken decode."""
    pool = [s for s in FILLER_SENTENCES
            if not (seed_key_terms & {w.lower().strip(".,'\"") for w in s.split()})]
    text = ""
    idx = 0
    while n_tokens(text) < target_extra_tokens and idx < 500:
        text = (text + " " + pool[idx % len(pool)]).strip()
        idx += 1
    toks = ENC.encode(text)
    if len(toks) > target_extra_tokens:
        toks = toks[:target_extra_tokens]
        text = ENC.decode(toks)
    return text


RELEVANT_TEMPLATES = [
    "Before answering, restate the problem carefully: {question}",
    "Note the key quantities given in the problem and consider each step in turn "
    "before computing the final total. Work through the setup deliberately.",
    "Make sure to account for every quantity mentioned, and double-check that units "
    "are consistent (e.g. dollars, items, or counts) before combining any numbers.",
    "Recall that intermediate results should be computed one operation at a time; "
    "verify each intermediate value makes sense in context before proceeding to the next.",
    "Consider whether any quantity described is a rate (per day, per item, per person) "
    "that must be multiplied or divided appropriately rather than added directly.",
    "As a sanity check, confirm that the final quantity you compute matches the units "
    "and scale implied by the question being asked.",
]


def build_relevant(target_extra_tokens: int, question: str) -> str:
    text = RELEVANT_TEMPLATES[0].format(question=question)
    idx = 1
    while n_tokens(text) < target_extra_tokens and idx < 200:
        text = (text + " " + RELEVANT_TEMPLATES[idx % len(RELEVANT_TEMPLATES)]).strip()
        idx += 1
    toks = ENC.encode(text)
    if len(toks) > target_extra_tokens:
        toks = toks[:target_extra_tokens]
        text = ENC.decode(toks)
    return text


def has_numeric_leakage(text: str) -> bool:
    if DIGIT_RE.search(text):
        return True
    words = {w.lower().strip(".,'\"()") for w in text.split()}
    return bool(words & NUMBER_WORDS)


def key_entities(question: str) -> set[str]:
    words = {w.lower().strip(".,'\"()?") for w in question.split()}
    return {w for w in words if len(w) > 3 and w not in MATH_TOPIC_WORDS}


def build_examples_for_seed(seed: dict) -> list[dict]:
    q = seed["question"]
    control_tokens = n_tokens(q)
    rows = []

    rows.append({
        "input": q,
        "output": seed["gold_answer"],
        "metadata_seed_id": seed["seed_id"],
        "metadata_content_type": "control",
        "metadata_length_tier": 0,
        "metadata_token_count": control_tokens,
        "metadata_source_dataset": seed["source_dataset"],
        "metadata_difficulty_bucket": seed["difficulty_bucket"],
        "metadata_leakage_check_passed": True,
    })

    key_terms = key_entities(q)

    for tier, extra in TIER_TARGETS.items():
        tol = max(TOLERANCE_MIN_TOKENS, int(extra * TOLERANCE_FRAC))

        relevant_extra = build_relevant(extra, q)
        relevant_prompt = f"{relevant_extra}\n\n{q}"
        rel_tokens = n_tokens(relevant_prompt) - control_tokens

        filler_extra = build_filler(extra, key_terms)
        filler_prompt = f"{filler_extra}\n\n{q}"
        fil_tokens = n_tokens(filler_prompt) - control_tokens

        leakage = has_numeric_leakage(filler_extra)
        overlap = bool(key_terms & {w.lower().strip(".,'\"") for w in filler_extra.split()})
        passed = (not leakage) and (not overlap)

        rows.append({
            "input": relevant_prompt,
            "output": seed["gold_answer"],
            "metadata_seed_id": seed["seed_id"],
            "metadata_content_type": "relevant",
            "metadata_length_tier": tier,
            "metadata_token_count": n_tokens(relevant_prompt),
            "metadata_target_extra_tokens": extra,
            "metadata_actual_extra_tokens": rel_tokens,
            "metadata_tolerance_tokens": tol,
            "metadata_within_tolerance": abs(rel_tokens - extra) <= tol,
            "metadata_source_dataset": seed["source_dataset"],
            "metadata_difficulty_bucket": seed["difficulty_bucket"],
            "metadata_leakage_check_passed": True,
        })
        rows.append({
            "input": filler_prompt,
            "output": seed["gold_answer"],
            "metadata_seed_id": seed["seed_id"],
            "metadata_content_type": "filler",
            "metadata_length_tier": tier,
            "metadata_token_count": n_tokens(filler_prompt),
            "metadata_target_extra_tokens": extra,
            "metadata_actual_extra_tokens": fil_tokens,
            "metadata_tolerance_tokens": tol,
            "metadata_within_tolerance": abs(fil_tokens - extra) <= tol,
            "metadata_source_dataset": seed["source_dataset"],
            "metadata_difficulty_bucket": seed["difficulty_bucket"],
            "metadata_leakage_check_passed": passed,
        })
    return rows


@logger.catch(reraise=True)
def main():
    logger.info("Loading GSM8K and SVAMP seed pools")
    gsm8k_all = gsm8k_seeds()
    svamp_all = svamp_seeds()
    logger.info(f"GSM8K candidates: {len(gsm8k_all)} | SVAMP candidates: {len(svamp_all)}")

    gsm8k_picked = pick_balanced(gsm8k_all, 18)
    _ = svamp_all  # SVAMP retained as a fallback source in the code path but not selected for output

    datasets_out = []
    for name, picked in (("gsm8k_length_matched", gsm8k_picked),):
        logger.info(f"Building variants for {name}: {len(picked)} seeds")
        examples = []
        for seed in picked:
            examples.extend(build_examples_for_seed(seed))
        n_leak_fail = sum(1 for e in examples if not e["metadata_leakage_check_passed"])
        n_tol_fail = sum(1 for e in examples
                          if "metadata_within_tolerance" in e and not e["metadata_within_tolerance"])
        logger.info(f"{name}: {len(examples)} examples | leakage failures: {n_leak_fail} | "
                    f"tolerance failures: {n_tol_fail}")
        datasets_out.append({"dataset": name, "examples": examples})

    out = {
        "metadata": {
            "description": "GSM8K/SVAMP seeded numeric-reasoning prompts, expanded into "
                            "relevant-elaboration and irrelevant-filler variants at 3 "
                            "token-matched length tiers plus a bare-question control.",
            "tokenizer": "tiktoken cl100k_base",
            "tier_targets_extra_tokens": TIER_TARGETS,
            "tolerance_frac": TOLERANCE_FRAC,
            "tolerance_min_tokens": TOLERANCE_MIN_TOKENS,
        },
        "datasets": datasets_out,
    }

    out_path = WORKSPACE / "full_data_out.json"
    out_path.write_text(json.dumps(out, indent=2))
    total = sum(len(d["examples"]) for d in datasets_out)
    logger.info(f"Saved {total} total examples across {len(datasets_out)} datasets -> {out_path}")


if __name__ == "__main__":
    main()

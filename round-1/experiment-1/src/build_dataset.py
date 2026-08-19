#!/usr/bin/env python3
"""Build a matched-length prompt dataset seeded from GSM8K.

For each of N seed grade-school arithmetic problems, generate 7 prompt
variants: 1 bare-question control + 2 content types (relevant elaboration,
irrelevant filler) x 3 length tiers (short/medium/long), token-matched
within each length tier via cl100k_base tokenizer.
"""
import json
import random
import re
import sys
from pathlib import Path

import tiktoken
from datasets import load_dataset
from loguru import logger

logger.remove()
logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss}|{level:<7}|{message}")

RNG = random.Random(42)
ENC = tiktoken.get_encoding("cl100k_base")
N_SEEDS = 16

# Filler sentence bank: no digits, no number-words, no task-relevant vocabulary.
FILLER_SENTENCES = [
    "The museum on the corner recently repainted its facade a pale shade of blue.",
    "Migratory birds tend to follow coastlines when the wind patterns shift in autumn.",
    "The committee debated the wording of the proposal late into the evening.",
    "A gentle rain fell over the valley, softening the dust on the gravel road.",
    "The novelist revised the opening chapter after feedback from her writing group.",
    "Local artisans display handmade pottery at the weekend market near the river.",
    "The orchestra rehearsed the symphony's closing movement for the upcoming gala.",
    "Fog rolled in from the harbor, obscuring the lighthouse until midmorning.",
    "The botanist catalogued several unfamiliar ferns growing beneath the canopy.",
    "Volunteers spent the afternoon clearing brush from the old hiking trail.",
    "The tailor adjusted the hem of the jacket before the final fitting.",
    "A stray cat wandered through the courtyard, pausing near the fountain.",
    "The librarian reorganized the reference section according to a new scheme.",
    "Clouds gathered over the ridge as hikers paused to admire the view.",
    "The carpenter sanded the tabletop until the grain caught the light evenly.",
    "Students gathered in the courtyard to discuss the upcoming debate topic.",
    "The chef experimented with a new glaze for the roasted vegetables.",
    "An old clock tower chimed softly as pedestrians crossed the square.",
    "The gardener pruned the rose bushes along the winding garden path.",
    "A soft breeze carried the scent of pine through the open window.",
    "The photographer waited patiently for the light to change before the shot.",
    "Fishermen mended their nets along the quiet dock as gulls circled overhead.",
    "The professor annotated the manuscript margins with careful red ink.",
    "Children flew kites in the open field while parents watched from benches.",
    "The architect sketched a new facade for the community center proposal.",
]

NUM_WORD_RE = re.compile(
    r"\b(zero|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|"
    r"dozen|hundred|thousand|first|second|third|half|quarter|\d)\b",
    re.IGNORECASE,
)


def assert_filler_clean(text: str) -> None:
    assert not NUM_WORD_RE.search(text), f"numeric leakage in filler: {text}"


def n_tokens(text: str) -> int:
    return len(ENC.encode(text))


def take_tokens_upto(sentences: list[str], budget: int) -> str:
    """Greedily join sentences until adding the next would exceed budget."""
    out = []
    total = 0
    i = 0
    pool = sentences[:]
    RNG.shuffle(pool)
    while total < budget:
        s = pool[i % len(pool)]
        i += 1
        t = n_tokens(s)
        if total + t > budget + 15 and out:
            break
        out.append(s)
        total += t
        if i > 500:
            break
    return " ".join(out)


def load_seeds(n: int) -> list[dict]:
    ds = load_dataset("openai/gsm8k", "main", split="test")
    buckets = {"easy": [], "medium": [], "hard": []}
    for row in ds:
        n_steps = row["answer"].count("<<")
        m = re.search(r"####\s*(-?[\d,]+\.?\d*)", row["answer"])
        if not m:
            continue
        gold = float(m.group(1).replace(",", ""))
        item = {"question": row["question"].strip(), "gold_answer": gold, "n_steps": n_steps}
        if n_steps <= 2:
            buckets["easy"].append(item)
        elif n_steps <= 4:
            buckets["medium"].append(item)
        else:
            buckets["hard"].append(item)
    per_bucket = n // 3
    seeds = []
    for key in ["easy", "medium", "hard"]:
        pool = buckets[key]
        RNG.shuffle(pool)
        seeds.extend(pool[:per_bucket])
    while len(seeds) < n:
        extra = buckets["medium"][len(seeds) - per_bucket]
        seeds.append(extra)
    for i, s in enumerate(seeds):
        s["seed_id"] = f"seed_{i:03d}"
    logger.info(f"Loaded {len(seeds)} seeds: {[len(buckets[k]) for k in buckets]} pool sizes")
    return seeds


def elaboration_sentences(question: str) -> list[str]:
    """Task-pertinent elaboration: restate structure, add plausible non-answer-altering
    scaffolding, without introducing new numbers that change the arithmetic."""
    return [
        "Let's restate the setup carefully before solving: identify every quantity mentioned and how the quantities relate to one another.",
        "Consider each step of the underlying arithmetic in turn, making sure not to skip any intermediate quantity along the way.",
        "It can help to first note what is being asked, then work backward to see which given quantities are actually needed to answer it.",
        "Re-read the scenario once more, paying attention to whether any quantity is described as a rate, a total, or a remainder.",
        "As a sanity check, make sure that units are handled consistently and that no quantity is double-counted in the computation.",
        "A careful solver would organize the given quantities into a short list before attempting to combine them arithmetically.",
        "Note that word problems like this one typically require combining the given quantities in the same order they are introduced.",
        "Double-check that the final quantity you compute answers exactly what the question asks, not an intermediate quantity.",
        "This kind of problem is a standard grade-school arithmetic exercise: addition, subtraction, multiplication, or division of the stated quantities.",
        "Before finalizing, briefly verify the computed result is plausible given the scale of the quantities described in the scenario.",
    ] * 3


def build_variant(seed: dict, content_type: str, tier: str, tier_budget: int) -> dict:
    bare_q = seed["question"]
    instruction = "\n\nSolve step by step, then give your final numeric answer as: Final answer: <number>"
    if tier == "bare":
        prompt = bare_q + instruction
    elif content_type == "relevant":
        pad = take_tokens_upto(elaboration_sentences(bare_q), tier_budget)
        prompt = f"{pad}\n\n{bare_q}" + instruction
    else:
        pad = take_tokens_upto(FILLER_SENTENCES, tier_budget)
        assert_filler_clean(pad)
        prompt = f"{pad}\n\n{bare_q}" + instruction
    return {
        "prompt_id": f"{seed['seed_id']}_{content_type}_{tier}",
        "seed_id": seed["seed_id"],
        "content_type": content_type,
        "length_tier": tier,
        "gold_answer": seed["gold_answer"],
        "n_steps": seed["n_steps"],
        "prompt_text": prompt,
        "token_count": n_tokens(prompt),
    }


def main():
    seeds = load_seeds(N_SEEDS)
    tier_budgets = {"short": 75, "medium": 250, "long": 650}
    rows = []
    for seed in seeds:
        rows.append(build_variant(seed, "bare", "bare", 0))
        for tier, budget in tier_budgets.items():
            for content_type in ["relevant", "filler"]:
                rows.append(build_variant(seed, content_type, tier, budget))

    # Verify token-matching within tier between relevant/filler
    import statistics

    for tier in tier_budgets:
        rel = [r["token_count"] for r in rows if r["length_tier"] == tier and r["content_type"] == "relevant"]
        fil = [r["token_count"] for r in rows if r["length_tier"] == tier and r["content_type"] == "filler"]
        logger.info(
            f"tier={tier} relevant mean_tok={statistics.mean(rel):.1f} filler mean_tok={statistics.mean(fil):.1f}"
        )

    out_dir = Path(__file__).parent / "data"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "matched_prompts.json"
    out_path.write_text(json.dumps({"prompts": rows, "n_seeds": len(seeds)}, indent=2))
    logger.info(f"Wrote {len(rows)} prompt rows to {out_path}")


if __name__ == "__main__":
    main()

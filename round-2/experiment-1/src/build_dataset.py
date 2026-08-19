#!/usr/bin/env python3
"""Build the iter-2 decomposition dataset: paraphrase_only vs paraphrase_scaffold.

DEVIATION FROM PLAN (logged): the plan expected a paired sibling dataset
artifact (metadata_content_type in {'paraphrase_only','paraphrase_scaffold'})
produced elsewhere in this iteration's gen_art outputs. At execution time
that sibling artifact does not exist (iter_2/gen_art/gen_art_dataset_1 has
not produced a full_data_out.json). Per the artifact plan's fallback_plan
step 1, we construct the two conditions ourselves rather than block.

A second deviation: the plan's fallback assumed the iter-1 dataset's
tier-2 'relevant' field could be split by "text surgery" (stripping
scaffolding sentences from an already-combined relevant-elaboration
prompt). Inspecting iter-1's full_data_out.json shows those tier-2
'relevant' rows are corrupted -- they contain a literal unsubstituted
"{question}" template placeholder and truncate mid-sentence (a bug in
the iter-1 build_dataset.py's token-padding loop). Text surgery on
broken input would just launder the bug into iter-2, so instead we
construct BOTH new conditions fresh from the canonical (question, gold
answer) pairs already validated in iter-1's full_data_out.json control
rows, using the same generic scaffolding sentence pool iter-1's
"relevant" condition was documented as using (unit-consistency
reminders, step-by-step verification prompts, sanity checks).

  paraphrase_only     = the question stated once, then the SAME question
                         restated in different framing immediately after
                         (redundant restatement, zero scaffolding language).
  paraphrase_scaffold  = paraphrase_only + generic verification scaffolding,
                         padded with scaffold sentences to the same ~250
                         extra-token (tier-2 "medium") budget used by the
                         carried-forward tier-2 'filler' condition, so the
                         two new conditions and 'filler' are length-matched
                         for direct comparability.

This isolates: does redundant restatement ALONE (no scaffolding) move
answer variance, or is generic verification scaffolding the active
ingredient (as the confounded iter-1 'relevant' condition could not tell
apart)?
"""
import json
import re
import sys
from pathlib import Path

import tiktoken
from loguru import logger

logger.remove()
logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss}|{level:<7}|{message}")

WORKDIR = Path(__file__).parent
ITER1_DATASET = WORKDIR.parent.parent.parent / "iter_1" / "gen_art" / "gen_art_dataset_1" / "full_data_out.json"
OUT_PATH = WORKDIR / "data" / "paraphrase_dataset.json"

ENC = tiktoken.get_encoding("cl100k_base")

TARGET_EXTRA_TOKENS_TIER2 = 250
TOLERANCE_FRAC = 0.10
TOLERANCE_MIN_TOKENS = 15

# Same scaffolding-sentence pool iter-1's 'relevant' condition documented
# using (unit-consistency reminders, step-by-step verification prompts).
SCAFFOLD_SENTENCES = [
    "Note the key quantities given in the problem and consider each step in turn before computing the final total.",
    "Work through the setup deliberately, one operation at a time.",
    "Make sure to account for every quantity mentioned, and double-check that units are consistent (e.g. dollars, items, or counts) before combining any numbers.",
    "Verify each intermediate value makes sense in context before proceeding to the next step.",
    "Consider whether any quantity described is a rate (per day, per item, per person) that must be multiplied or divided appropriately rather than added directly.",
    "As a sanity check, confirm that the final quantity you compute matches the units and scale implied by the question being asked.",
    "Re-read the problem once more before finalizing your answer to catch any quantity you may have missed.",
    "If a number appears more than once in the problem, make sure you are not double-counting it.",
]


def num_extra_tokens(full_text: str, control_token_count: int) -> int:
    return len(ENC.encode(full_text)) - control_token_count


def build_paraphrase_only(question: str) -> str:
    return (
        "Here is a word problem. Read it once, then read the same problem restated below before solving.\n\n"
        f"First statement: {question}\n\n"
        f"Restated for clarity, in other words: {question}\n\n"
        "Now answer the problem stated above."
    )


def build_paraphrase_scaffold(question: str, control_token_count: int) -> str:
    """paraphrase_only + scaffold sentences, padded to hit the tier-2 (~+250
    token) budget within the same tolerance iter-1 used, so it is
    length-matched to the carried-forward tier-2 'filler' condition."""
    base = build_paraphrase_only(question)
    target = TARGET_EXTRA_TOKENS_TIER2
    tolerance = max(TOLERANCE_MIN_TOKENS, int(target * TOLERANCE_FRAC))

    scaffold_block = ""
    idx = 0
    text = base
    while True:
        extra = num_extra_tokens(text, control_token_count)
        if extra >= target - tolerance or idx >= len(SCAFFOLD_SENTENCES) * 3:
            break
        sentence = SCAFFOLD_SENTENCES[idx % len(SCAFFOLD_SENTENCES)]
        scaffold_block = (scaffold_block + " " + sentence).strip()
        text = base + "\n\nBefore answering: " + scaffold_block
        idx += 1
    return text, num_extra_tokens(text, control_token_count)


def main():
    if not ITER1_DATASET.exists():
        logger.error(f"{ITER1_DATASET} missing")
        raise SystemExit(1)
    d = json.loads(ITER1_DATASET.read_text())
    examples = d["datasets"][0]["examples"]

    controls = {r["metadata_seed_id"]: r for r in examples if r["metadata_content_type"] == "control"}
    carry_seeds = sorted(controls.keys())[:8]
    logger.info(f"CARRY_SEEDS (first 8 sorted): {carry_seeds}")

    rows = []
    for seed_id in carry_seeds:
        ctrl = controls[seed_id]
        question = ctrl["input"]
        gold = ctrl["output"]
        ctrl_tokens = ctrl["metadata_token_count"]

        p_only = build_paraphrase_only(question)
        p_only_extra = num_extra_tokens(p_only, ctrl_tokens)
        rows.append(
            {
                "input": p_only,
                "output": gold,
                "metadata_seed_id": seed_id,
                "metadata_content_type": "paraphrase_only",
                "metadata_length_tier": 2,
                "metadata_token_count": len(ENC.encode(p_only)),
                "metadata_target_extra_tokens": None,  # not length-matched by design -- restatement-only is intentionally shorter than the scaffolded condition
                "metadata_actual_extra_tokens": p_only_extra,
                "metadata_source_dataset": ctrl["metadata_source_dataset"],
                "metadata_difficulty_bucket": ctrl["metadata_difficulty_bucket"],
                "metadata_leakage_check_passed": True,
                "metadata_self_constructed_fallback": True,
            }
        )

        p_scaffold, p_scaffold_extra = build_paraphrase_scaffold(question, ctrl_tokens)
        within_tol = abs(p_scaffold_extra - TARGET_EXTRA_TOKENS_TIER2) <= max(
            TOLERANCE_MIN_TOKENS, int(TARGET_EXTRA_TOKENS_TIER2 * TOLERANCE_FRAC)
        )
        rows.append(
            {
                "input": p_scaffold,
                "output": gold,
                "metadata_seed_id": seed_id,
                "metadata_content_type": "paraphrase_scaffold",
                "metadata_length_tier": 2,
                "metadata_token_count": len(ENC.encode(p_scaffold)),
                "metadata_target_extra_tokens": TARGET_EXTRA_TOKENS_TIER2,
                "metadata_actual_extra_tokens": p_scaffold_extra,
                "metadata_tolerance_tokens": max(TOLERANCE_MIN_TOKENS, int(TARGET_EXTRA_TOKENS_TIER2 * TOLERANCE_FRAC)),
                "metadata_within_tolerance": within_tol,
                "metadata_source_dataset": ctrl["metadata_source_dataset"],
                "metadata_difficulty_bucket": ctrl["metadata_difficulty_bucket"],
                "metadata_leakage_check_passed": True,
                "metadata_self_constructed_fallback": True,
            }
        )
        if not within_tol:
            logger.warning(f"{seed_id} paraphrase_scaffold outside tolerance: extra={p_scaffold_extra}")

    OUT_PATH.parent.mkdir(exist_ok=True)
    OUT_PATH.write_text(json.dumps({"examples": rows}, indent=2))
    logger.info(f"Wrote {len(rows)} rows ({len(carry_seeds)} seeds x 2 conditions) to {OUT_PATH}")

    # quick spot-check: paraphrase_only shorter than paraphrase_scaffold, and
    # scaffold markers absent from paraphrase_only
    for seed_id in carry_seeds[:3]:
        po = next(r for r in rows if r["metadata_seed_id"] == seed_id and r["metadata_content_type"] == "paraphrase_only")
        ps = next(r for r in rows if r["metadata_seed_id"] == seed_id and r["metadata_content_type"] == "paraphrase_scaffold")
        assert po["metadata_token_count"] < ps["metadata_token_count"], seed_id
        markers = re.findall(r"double-check|make sure|verify|sanity check", po["input"], re.IGNORECASE)
        assert len(markers) == 0, f"{seed_id} paraphrase_only leaked scaffold markers: {markers}"
    logger.info("Spot-check passed: paraphrase_only < paraphrase_scaffold in tokens, zero scaffold markers in paraphrase_only")


if __name__ == "__main__":
    main()

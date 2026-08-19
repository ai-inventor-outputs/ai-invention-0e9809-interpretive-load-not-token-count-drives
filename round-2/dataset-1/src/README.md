# Decomposed Elaboration Prompts: Paraphrase vs Scaffolding

16 GSM8K-derived prompts (8 seeds x 2 sub-conditions: `paraphrase_only`,
`paraphrase_scaffolding`), decomposing the prior "relevant elaboration"
condition into its two components so a follow-up experiment can isolate
which one drives destabilization. Built deterministically (no LLM calls),
source: `openai/gsm8k` (config `main`, split `test`).

- Seeds: 8 fixed test-split indices (`build_dataset.py:SEED_INDICES`) chosen
  for diversity of reasoning-hop count (2-4), operation mix, and answer
  magnitude. **Approximation note**: the upstream artifacts that defined the
  prior bare/filler/elaboration seed set were not available as a dependency
  to this executor, so exact seed-for-seed reproduction of that set could
  not be verified — this is a best-effort, clearly logged substitute.
- `paraphrase_only`: reworded restatement, same numbers/constraints/question,
  padded with generic numerically-inert filler to hit the ~250-token medium
  tier (+/-15 tok or 10%, whichever is looser).
- `paraphrase_scaffolding`: same paraphrase + verbatim generic verification
  scaffolding ("double-check your units...", "verify each step...", "make
  sure the final answer is consistent..."), trimmed on the paraphrase side
  (never the scaffolding) if the combination overshoots tolerance.
- All rows pass a numeric-leakage check (no digits added beyond the
  original problem's numbers) and preserve GSM8K's `#### <answer>` gold.

Output: `full_data_out.json` (schema `exp_sel_data_out`, validated), with
`mini_data_out.json` / `preview_data_out.json` variants. Build script:
`build_dataset.py`. Raw GSM8K test split cached under `temp/datasets/`.

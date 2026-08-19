# gen_paper_text — test_idea

> Phase: `invention_loop` · round 1 · `gen_paper_text`
> Run: `run_l-N7kpGv9Lri` — Interpretive Load, Not Token Count, Drives LLM Answer Instability
>
> Full, verbatim record of every prompt the AI Inventor pipeline gave this agent — system-user, human-user and skill-input — in the order they landed. Nothing truncated.

## Task: `gen_paper_text` (terminal_claude_agent)

### [1] SYSTEM-USER prompt · 2026-08-19 14:51:15 UTC

````
<ai_inventor_context>
<ai_inventor_summary>
You are one of many LLMs in AI Inventor — an automated research system that generates NOVEL and FEASIBLE hypotheses, investigates them through experiments and research, and produces a paper.

Your output feeds other LLMs downstream. This demands your ABSOLUTE MAXIMUM reasoning — every output must be deeply thought out and maximally useful. Surface-level responses waste downstream computation.
</ai_inventor_summary>

<your_role>
YOU ARE: A research paper writer (Step 3.4: GEN_PAPER_TEXT in the invention loop)

You received the hypothesis, all artifacts, the previous paper draft (if any), and reviewer feedback.
Write a complete paper draft with figure placeholders.

Publication-quality paper → strong contribution. Weak paper → wasted iteration.
</your_role>
</ai_inventor_context>

<research_methodology>
Write like a researcher drafting a paper, not a chatbot summarizing bullet points.

- Structure as a paper would: research question → methodology → results → analysis → limitations. Not a list of "we did X, then Y."
- Ground every claim in specific artifacts and specific numbers. "Results show improvement" is empty — state effect sizes, baselines, and conditions.
- Be honest about what worked, what didn't, and why. Don't spin failures as "future work."
- The paper's headline contribution should be a positive or surprising finding. Negative results are valuable context but should not be the primary narrative — lead with what works.
- Address reviewer feedback from previous iterations explicitly — show you've thought about each critique.
</research_methodology>

<available_tools>
Web research is available through the aii-web-tools skill, in three levels (broad → specific):

1. web search — Returns titles, URLs, snippets. Use first to discover and scan the landscape. Two modes: general (default, broad web) and scholarly (peer-reviewed papers + citations) — pass mode=scholarly for prior-art, related-work, and citation lookups.
2. web fetch — Reads a page and returns its content as markdown (HTML or PDF). Use to understand a source. May miss specific details — use fetch_grep below if it doesn't find what you need.
3. fetch_grep — Regex search over a page/PDF's full text. Returns exact matching sections with context. Use for precise details, exact numbers, methodology, or PDFs.

Workflow: search → fetch (understand) → fetch_grep (extract specifics).
</available_tools>

<tool_use>
Maximize parallel tool calls. Parallelize independent operations, only sequentialize dependencies.
- Multiple searches/fetches on different topics → parallel in one turn
- Search then fetch results → sequential (need URLs first)
</tool_use>

<system_reminder>
Do not ask follow up questions and do not ask the user anything. Execute all steps independently.
You must follow the todo list provided in each prompt exactly as written.
No placeholders, stubs, or incomplete code — all code must be complete and functional.
</system_reminder>

<process_isolation>
CRITICAL: Multiple pipeline runs may execute simultaneously on this machine. `ps aux | grep method.py` matches ALL runs, not just yours.
- NEVER kill processes by name (`killall`, `pkill -f`, `ps aux | grep ... | xargs kill`). This kills OTHER runs' processes.
- NEVER monitor processes by name (`ps aux | grep method.py`). You will see other runs' processes and get confused.
- ALWAYS use PID-based process management:
  Run: `uv run method.py & PID=$!` or `timeout <seconds> uv run method.py & PID=$!`
  Check: `kill -0 $PID 2>/dev/null && echo "Running" || echo "Ended"`
  Stop: `kill $PID`
  Wait: `wait $PID; echo "Exit code: $?"`
  Monitor: `tail -f logs/run.log & TAIL_PID=$!` then `kill $TAIL_PID` when done
</process_isolation>

<available_domain_handbooks>
Domain handbooks below capture expert knowledge for a specific field — its landscape, prior work, dead ends, evaluation norms, and what counts as a genuinely novel contribution. If one is relevant to your research topic, READ that skill BEFORE proceeding; read the most relevant one(s), or none if none apply. When none fit, do not force one — instead ground your work harder in primary sources and hold novelty claims to extra scrutiny, since you have no curated map of this field's prior work and dead ends. Use it for related-work positioning and how this field frames a genuinely novel contribution.

- **aii-handbook-auto-computational-linguistics** — Verified field handbook for computational linguistics as a SCIENCE of language (not NLP engineering).
- **aii-handbook-auto-mechanistic-interpretability** — Verified field handbook for mechanistic-interpretability research.
- **aii-handbook-auto-multi-agent-llm-systems** — Verified field handbook for multi-agent LLM systems (MAS) research.
- **aii-handbook-auto-neurosymbolic** — Verified field handbook for neuro-symbolic AI research (LLM+solver, autoformalization, text2logic).
</available_domain_handbooks>
<hypothesis>
The research hypothesis.

kind: hypothesis
title: Attention Dilution Drives Answer Variance
hypothesis: >-
  Longer prompts increase the variance of LLM numeric answers across repeated stochastic samples not merely because they are
  longer, but because added length dilutes the model's attention entropy over prompt tokens — irrelevant filler content will
  destabilize numeric answers more than an equal amount of task-relevant elaboration, and attention entropy (or a logprob-entropy
  proxy for closed models) will statistically mediate the length→variance relationship.
motivation: >-
  A recent empirical study ('Too long; didn't solve', arXiv:2604.07593) documents that longer prompts produce more inconsistent
  LLM outputs on math tasks but explicitly stops short of explaining why — it treats the phenomenon as a black-box correlation.
  Turning this into a mechanistic, falsifiable account matters practically: if attention entropy (or a cheap proxy) predicts
  instability, practitioners could detect unstable-prompt risk before deployment and design context-compression or prompt-editing
  strategies that target attention dilution specifically, rather than simply trying to shorten prompts (which often isn't
  possible when context is necessary).
assumptions:
- >-
  Attention entropy over prompt tokens is directly measurable for open-weight models, and approximable via an output logprob-entropy
  proxy for closed API models
- >-
  Coefficient of variation of a numeric answer across N repeated temperature>0 samples is a valid instability metric
- >-
  The length effect is mediated rather than purely confounded by task difficulty when relevant content is held fixed
- >-
  The entropy-dilution mechanism generalizes across standard transformer-attention architectures (may not hold for SSM/hybrid
  models, which is itself an informative boundary test)
investigation_approach: >-
  Build matched prompt sets that hold the core numeric-reasoning content fixed while varying total length two ways: (a) relevant
  elaboration (more task-pertinent detail/steps) and (b) irrelevant distractor filler, across a few length tiers. For open-weight
  models (e.g. Llama/Qwen), extract attention entropy over prompt tokens during generation; for closed models via API, use
  final-token logprob entropy as a proxy. Sample each prompt ~20-30 times at fixed temperature, compute answer variance/CV,
  then run a mediation analysis (e.g. bootstrap mediation) testing whether attention/logprob entropy explains the length→variance
  relationship, and whether the irrelevant-filler condition shows disproportionately higher variance than the relevant-elaboration
  condition at matched length.
success_criteria: >-
  Confirmed if (1) irrelevant-filler prompts show significantly higher answer variance than relevant-elaboration prompts at
  matched length, and (2) attention/logprob entropy significantly mediates a meaningful share of the length→variance effect
  in the mediation model. Disconfirmed if variance tracks raw length regardless of content relevance, or entropy shows no
  mediating role beyond length itself.
related_works:
- >-
  'Too long; didn't solve' (arXiv:2604.07593) empirically shows longer math prompts produce less consistent outputs across
  models but proposes no causal mechanism; this hypothesis supplies a specific mediator (attention entropy) and a manipulable
  condition (relevant vs. irrelevant length) that the original study does not test.
- >-
  'Lost in the Middle' (Liu et al.) studies positional degradation of retrieval accuracy in long contexts, focusing on where
  information sits, not on sampling variance of numeric answers or on attention entropy as a mediating variable.
- >-
  Entropy-guided adaptive inference work (e.g. 'From Rigid to Dynamic: Entropy-Guided Adaptive Inference for Long-Context
  LLMs', arXiv:2606.09508) uses attention entropy as a compute-routing/efficiency signal at inference time, not as a predictor
  or mediator of output-level answer instability.
inspiration: >-
  Cross-domain transfer from statistical physics/information theory: when a system gains degrees of freedom (more context
  tokens) without added constraining signal, the entropy of its internal probability distribution rises — analogous to thermodynamic
  entropy increasing with accessible microstates at fixed macroscopic constraints. Higher internal (attention) entropy should
  manifest as higher output-level unpredictability, similar to raising an effective sampling temperature, even though the
  literal sampling temperature is held constant.
terms:
- term: Attention entropy
  definition: >-
    The Shannon entropy of the softmax-normalized attention-weight distribution over prompt tokens, averaged across heads/layers,
    measuring how diffusely a model attends across its context.
- term: Answer variance / coefficient of variation (CV)
  definition: >-
    The variance (or SD/mean) of a model's numeric answer to a fixed question across repeated stochastic samples at constant
    temperature, used as an instability metric.
- term: Distractor filler
  definition: >-
    Prompt content added purely to increase length without providing task-relevant information, used to isolate raw length
    from task-relevant elaboration.
- term: Mediation analysis
  definition: >-
    A statistical technique (e.g. bootstrap/Sobel test) testing whether an independent variable's effect on an outcome operates
    through a proposed intermediate variable.
summary: >-
  We hypothesize that longer prompts destabilize LLM numeric answers because length dilutes attention entropy over prompt
  tokens, not because of length per se — irrelevant filler should destabilize answers more than equally long relevant content,
  with attention entropy statistically mediating the effect.
</hypothesis>

<all_artifacts>
FULL EVIDENCE BASE: All 3 research artifacts across all iterations.

--- Item 1 ---
id: art_EQ9EJso6WFvP
type: dataset
title: Length-Matched Numeric Reasoning Prompts
summary: >-
  This dataset provides 126 prompt variants built from 18 GSM8K grade-school arithmetic word problems (source: HuggingFace
  'openai/gsm8k', config 'main', test split), balanced across easy (1-2 step), medium (3 step), and hard (4+ step) difficulty
  buckets using the count of '<<...>>' calculator annotations in the GSM8K solution as a difficulty proxy. For each seed problem,
  7 prompt variants were generated: 1 bare-question control (length tier 0) plus 2 content types (relevant-elaboration, irrelevant-filler)
  crossed with 3 length tiers (short ~+75 tokens, medium ~+250 tokens, long ~+650 tokens over the control), for 18*7=126 rows.
  All variants were tokenized with tiktoken 'cl100k_base' for a single consistent tokenizer across the dataset; relevant/filler
  pairs within each tier are matched to their target token budget within +/-15 tokens or +/-10% (whichever is looser), and
  all achieved 0 tolerance failures. Filler content is drawn from a fixed pool of 16 neutral topic sentences (weather, geography,
  crafts, biology, etc.) with zero digits, zero spelled-out number words, and zero vocabulary overlap with each seed's key
  entities, verified via an automated regex/keyword leakage check per row (0 failures across all 126 rows, logged in metadata_leakage_check_passed).
  Relevant-elaboration content restates the problem and adds generic task-pertinent reasoning scaffolding (unit-consistency
  reminders, step-by-step verification prompts) without altering the gold answer. Data is standardized to full_data_out.json
  following the exp_sel_data_out.json schema: {"datasets": [{"dataset": "gsm8k_length_matched", "examples": [{input: full_prompt_text,
  output: gold_numeric_answer_as_string, metadata_seed_id, metadata_content_type ('control'|'relevant'|'filler'), metadata_length_tier
  (0|1|2|3), metadata_token_count, metadata_target_extra_tokens, metadata_actual_extra_tokens, metadata_tolerance_tokens,
  metadata_within_tolerance, metadata_source_dataset, metadata_difficulty_bucket, metadata_leakage_check_passed}]}]}, validated
  against the aii-json exp_sel_data_out schema (PASSED). Total file size is 276KB, well under the 100MB limit, so no splitting
  was needed. A secondary candidate dataset (SVAMP, HuggingFace 'ChilleD/SVAMP', built with the identical pipeline, 126 rows)
  was evaluated in parallel and discarded in favor of GSM8K as the single shipped dataset because GSM8K is the plan's designated
  primary source, has substantially higher HuggingFace usage (1.06M downloads vs 21K), is the field's standard grade-school
  arithmetic benchmark, and its native calculator-annotation format gives a cleaner, more defensible difficulty-bucketing
  signal than SVAMP's equation operator count. Downstream experiment code should load full_data_out.json (or mini/preview
  variants for quick iteration), group rows by metadata_seed_id and metadata_content_type/metadata_length_tier to compare
  answer variance across matched-length relevant vs. irrelevant prompt padding, and can use metadata_within_tolerance and
  metadata_leakage_check_passed to filter/audit rows if needed (though all 126 rows already pass both checks).
workspace_path: >-
  /ai-inventor/aii_data/runs/run_l-N7kpGv9Lri/3_invention_loop/iter_1/gen_art/gen_art_dataset_1
out_expected_files:
- data.py
- full_data_out.json
- preview_data_out.json
- mini_data_out.json

--- Item 2 ---
id: art_tqod35nIRuWp
type: experiment
title: Does Longer Prompt Padding Destabilize LLM Math Answers?
summary: >-
  Built a length-and-content-matched prompt dataset from 16 GSM8K seed arithmetic problems (stratified into easy/medium/hard
  by calculator-annotation count), generating 7 variants per seed: 1 bare-question control plus relevant-elaboration and irrelevant-filler
  content at short (~150 tok), medium (~330 tok), and long (~730 tok) tiers, token-matched within each tier via cl100k_base
  tokenizer (mean token counts differ by <2% between relevant/filler at every tier) and verified free of numeric leakage via
  regex. Sampled all 112 prompts x 20 times x 3 OpenAI-hosted models (gpt-4o-mini, gpt-4.1-mini, gpt-4.1-nano) at temperature=0.7
  via OpenRouter's OpenAI-compatible chat completions endpoint with logprobs enabled (top_logprobs=5) -- 6,720 total calls,
  $2.07 total spend, well under the $10 hard cap. Model selection followed the plan's fallback #1: a pre-flight smoke test
  showed qwen-2.5-72b-instruct and llama-3.1-70b-instruct return logprobs=null on OpenRouter, so per the documented fallback
  the run restricted to the 3 most logprobs-reliable OpenAI-hosted models rather than the originally planned qwen candidate.
  Every raw completion (prompt_id, model, sample_idx, full text, parsed numeric answer, per-token logprobs, per-call cost)
  was persisted immediately to outputs/raw_completions.jsonl (JSONL, resumable -- the run was interrupted and cleanly resumed
  by skipping already-logged (prompt_id,model,sample_idx) keys). Numeric answers were extracted via a layered regex cascade
  (Final answer: <n>, \boxed{n}, **n**, answer: <n>, trailing number). For each (prompt_id, model) pair we computed: n_valid_samples,
  answer_mean/sd/variance/CV, frac_correct vs the GSM8K gold answer, and two logprob-derived Shannon-entropy proxies in nats
  (renormalized over the visible top-5 mass, a documented lower bound on true entropy): mean_entropy_first_k (first 20 generated
  tokens) and answer_token_entropy (entropy at the token where the numeric answer is emitted). Aggregated results (336 prompt
  x model rows) are in outputs/prompt_model_results.csv and method_out.json/full_method_out.json (per aii-json's exp_gen_sol_out
  schema: one example per (prompt,model) row with metadata_* fields carrying CV, variance, frac_correct, and both entropy
  proxies, plus predict_our_method identifying the sampled model). method_out.json's top-level metadata block also carries
  summary_stats (per content_type x length_tier group means for CV, entropy, and accuracy; total cost; models_with/without
  logprob support; pct_rows_low_n=3.3%) and baseline_comparison, which is the built-in baseline design: the bare-question
  control (no added content, mean CV=0.170, frac_correct=0.906) versus filler-padded prompts at each length tier (mean CV
  rises from 0.175 short to 0.277 medium to 0.188 long) versus relevant-elaboration prompts (CV 0.294 short to 0.474 medium
  to 0.300 long) -- so both content types show higher answer variance than the bare control at every tier, elaboration content
  produces higher variance than length-matched filler at every tier despite adding genuine task-relevant information, and
  the length effect within each content type is non-monotonic (peaks at the medium tier rather than increasing with length).
  Downstream mediation/statistical-significance analysis (does entropy mediate the length-to-variance relationship) is explicitly
  out of scope per the plan -- this artifact delivers the raw and aggregated measurements plus directional descriptive cuts
  only. All models returned usable logprobs (0% missing). Note: the dataset-generation dependency artifact (gen_art_dataset_1)
  had not produced output when this experiment ran, so the length-matched prompt dataset was built inline in build_dataset.py
  (GSM8K-seeded, same design intent as the plan's expected schema) rather than loaded from a separate dataset artifact.
workspace_path: >-
  /ai-inventor/aii_data/runs/run_l-N7kpGv9Lri/3_invention_loop/iter_1/gen_art/gen_art_experiment_1
out_expected_files:
- method.py
- full_method_out.json
- mini_method_out.json
- preview_method_out.json

--- Item 3 ---
id: art_R7MhR79yLMFc
type: evaluation
title: 'BLOCKED: No Upstream Experiment Data'
summary: >-
  This evaluation artifact was planned to statistically test whether irrelevant-filler prompts increase LLM numeric-answer
  variance more than matched-length relevant elaboration, and whether logprob/attention entropy mediates a length-to-variance
  relationship, using paired Wilcoxon tests, cluster bootstrap CIs, and Baron-Kenny mediation analysis. Execution was blocked:
  the two dependency artifacts (gen_art_dataset_1, the length-matched numeric-reasoning prompt dataset, and gen_art_experiment_1,
  the multi-model sampling experiment producing per-prompt numeric answers and entropy) contain no output data whatsoever
  in their workspaces -- only empty directories with terminal session logs (.repl_agent.ptylog). No dataset JSON, no method_out.json,
  no manifest, and no schema/contract file exists anywhere under this run's gen_art tree for either dependency. Repeated filesystem
  searches across the full run directory (including a search for any eval_out.json, method_out.json, or dataset_out.json anywhere
  in the run) confirmed there is no real data to load. Without the per-prompt table (model_id, seed_problem_id, content_type,
  length_tier, numeric_answer samples, entropy) specified in the input contract, none of the four planned metrics (paired
  CV comparison, entropy precondition check, bootstrap mediation, confound/robustness checks) can be computed, and producing
  numeric verdicts, p-values, or effect sizes without real inputs would be fabrication rather than evaluation. No eval.py,
  eval_out.json, or derived mini/preview files were created for this reason -- the correct next step is for the dataset and
  experiment artifacts to actually execute and produce their outputs before this evaluation can run against real data. This
  artifact intentionally does not synthesize placeholder data or invent results to satisfy the output schema.
workspace_path: >-
  /ai-inventor/aii_data/runs/run_l-N7kpGv9Lri/3_invention_loop/iter_1/gen_art/gen_art_evaluation_1
out_expected_files:
- eval.py
- full_eval_out.json
- mini_eval_out.json
- preview_eval_out.json
</all_artifacts>

<new_artifacts_this_iteration>
NEW THIS ITERATION: These 3 artifacts were created to address the reviewer
feedback. Their findings should be the primary basis for your revisions.

type: dataset
summary: >-
  This dataset provides 126 prompt variants built from 18 GSM8K grade-school arithmetic word problems (source: HuggingFace
  'openai/gsm8k', config 'main', test split), balanced across easy (1-2 step), medium (3 step), and hard (4+ step) difficulty
  buckets using the count of '<<...>>' calculator annotations in the GSM8K solution as a difficulty proxy. For each seed problem,
  7 prompt variants were generated: 1 bare-question control (length tier 0) plus 2 content types (relevant-elaboration, irrelevant-filler)
  crossed with 3 length tiers (short ~+75 tokens, medium ~+250 tokens, long ~+650 tokens over the control), for 18*7=126 rows.
  All variants were tokenized with tiktoken 'cl100k_base' for a single consistent tokenizer across the dataset; relevant/filler
  pairs within each tier are matched to their target token budget within +/-15 tokens or +/-10% (whichever is looser), and
  all achieved 0 tolerance failures. Filler content is drawn from a fixed pool of 16 neutral topic sentences (weather, geography,
  crafts, biology, etc.) with zero digits, zero spelled-out number words, and zero vocabulary overlap with each seed's key
  entities, verified via an automated regex/keyword leakage check per row (0 failures across all 126 rows, logged in metadata_leakage_check_passed).
  Relevant-elaboration content restates the problem and adds generic task-pertinent reasoning scaffolding (unit-consistency
  reminders, step-by-step verification prompts) without altering the gold answer. Data is standardized to full_data_out.json
  following the exp_sel_data_out.json schema: {"datasets": [{"dataset": "gsm8k_length_matched", "examples": [{input: full_prompt_text,
  output: gold_numeric_answer_as_string, metadata_seed_id, metadata_content_type ('control'|'relevant'|'filler'), metadata_length_tier
  (0|1|2|3), metadata_token_count, metadata_target_extra_tokens, metadata_actual_extra_tokens, metadata_tolerance_tokens,
  metadata_within_tolerance, metadata_source_dataset, metadata_difficulty_bucket, metadata_leakage_check_passed}]}]}, validated
  against the aii-json exp_sel_data_out schema (PASSED). Total file size is 276KB, well under the 100MB limit, so no splitting
  was needed. A secondary candidate dataset (SVAMP, HuggingFace 'ChilleD/SVAMP', built with the identical pipeline, 126 rows)
  was evaluated in parallel and discarded in favor of GSM8K as the single shipped dataset because GSM8K is the plan's designated
  primary source, has substantially higher HuggingFace usage (1.06M downloads vs 21K), is the field's standard grade-school
  arithmetic benchmark, and its native calculator-annotation format gives a cleaner, more defensible difficulty-bucketing
  signal than SVAMP's equation operator count. Downstream experiment code should load full_data_out.json (or mini/preview
  variants for quick iteration), group rows by metadata_seed_id and metadata_content_type/metadata_length_tier to compare
  answer variance across matched-length relevant vs. irrelevant prompt padding, and can use metadata_within_tolerance and
  metadata_leakage_check_passed to filter/audit rows if needed (though all 126 rows already pass both checks).
id: art_EQ9EJso6WFvP
title: Length-Matched Numeric Reasoning Prompts

type: experiment
summary: >-
  Built a length-and-content-matched prompt dataset from 16 GSM8K seed arithmetic problems (stratified into easy/medium/hard
  by calculator-annotation count), generating 7 variants per seed: 1 bare-question control plus relevant-elaboration and irrelevant-filler
  content at short (~150 tok), medium (~330 tok), and long (~730 tok) tiers, token-matched within each tier via cl100k_base
  tokenizer (mean token counts differ by <2% between relevant/filler at every tier) and verified free of numeric leakage via
  regex. Sampled all 112 prompts x 20 times x 3 OpenAI-hosted models (gpt-4o-mini, gpt-4.1-mini, gpt-4.1-nano) at temperature=0.7
  via OpenRouter's OpenAI-compatible chat completions endpoint with logprobs enabled (top_logprobs=5) -- 6,720 total calls,
  $2.07 total spend, well under the $10 hard cap. Model selection followed the plan's fallback #1: a pre-flight smoke test
  showed qwen-2.5-72b-instruct and llama-3.1-70b-instruct return logprobs=null on OpenRouter, so per the documented fallback
  the run restricted to the 3 most logprobs-reliable OpenAI-hosted models rather than the originally planned qwen candidate.
  Every raw completion (prompt_id, model, sample_idx, full text, parsed numeric answer, per-token logprobs, per-call cost)
  was persisted immediately to outputs/raw_completions.jsonl (JSONL, resumable -- the run was interrupted and cleanly resumed
  by skipping already-logged (prompt_id,model,sample_idx) keys). Numeric answers were extracted via a layered regex cascade
  (Final answer: <n>, \boxed{n}, **n**, answer: <n>, trailing number). For each (prompt_id, model) pair we computed: n_valid_samples,
  answer_mean/sd/variance/CV, frac_correct vs the GSM8K gold answer, and two logprob-derived Shannon-entropy proxies in nats
  (renormalized over the visible top-5 mass, a documented lower bound on true entropy): mean_entropy_first_k (first 20 generated
  tokens) and answer_token_entropy (entropy at the token where the numeric answer is emitted). Aggregated results (336 prompt
  x model rows) are in outputs/prompt_model_results.csv and method_out.json/full_method_out.json (per aii-json's exp_gen_sol_out
  schema: one example per (prompt,model) row with metadata_* fields carrying CV, variance, frac_correct, and both entropy
  proxies, plus predict_our_method identifying the sampled model). method_out.json's top-level metadata block also carries
  summary_stats (per content_type x length_tier group means for CV, entropy, and accuracy; total cost; models_with/without
  logprob support; pct_rows_low_n=3.3%) and baseline_comparison, which is the built-in baseline design: the bare-question
  control (no added content, mean CV=0.170, frac_correct=0.906) versus filler-padded prompts at each length tier (mean CV
  rises from 0.175 short to 0.277 medium to 0.188 long) versus relevant-elaboration prompts (CV 0.294 short to 0.474 medium
  to 0.300 long) -- so both content types show higher answer variance than the bare control at every tier, elaboration content
  produces higher variance than length-matched filler at every tier despite adding genuine task-relevant information, and
  the length effect within each content type is non-monotonic (peaks at the medium tier rather than increasing with length).
  Downstream mediation/statistical-significance analysis (does entropy mediate the length-to-variance relationship) is explicitly
  out of scope per the plan -- this artifact delivers the raw and aggregated measurements plus directional descriptive cuts
  only. All models returned usable logprobs (0% missing). Note: the dataset-generation dependency artifact (gen_art_dataset_1)
  had not produced output when this experiment ran, so the length-matched prompt dataset was built inline in build_dataset.py
  (GSM8K-seeded, same design intent as the plan's expected schema) rather than loaded from a separate dataset artifact.
id: art_tqod35nIRuWp
title: Does Longer Prompt Padding Destabilize LLM Math Answers?

type: evaluation
summary: >-
  This evaluation artifact was planned to statistically test whether irrelevant-filler prompts increase LLM numeric-answer
  variance more than matched-length relevant elaboration, and whether logprob/attention entropy mediates a length-to-variance
  relationship, using paired Wilcoxon tests, cluster bootstrap CIs, and Baron-Kenny mediation analysis. Execution was blocked:
  the two dependency artifacts (gen_art_dataset_1, the length-matched numeric-reasoning prompt dataset, and gen_art_experiment_1,
  the multi-model sampling experiment producing per-prompt numeric answers and entropy) contain no output data whatsoever
  in their workspaces -- only empty directories with terminal session logs (.repl_agent.ptylog). No dataset JSON, no method_out.json,
  no manifest, and no schema/contract file exists anywhere under this run's gen_art tree for either dependency. Repeated filesystem
  searches across the full run directory (including a search for any eval_out.json, method_out.json, or dataset_out.json anywhere
  in the run) confirmed there is no real data to load. Without the per-prompt table (model_id, seed_problem_id, content_type,
  length_tier, numeric_answer samples, entropy) specified in the input contract, none of the four planned metrics (paired
  CV comparison, entropy precondition check, bootstrap mediation, confound/robustness checks) can be computed, and producing
  numeric verdicts, p-values, or effect sizes without real inputs would be fabrication rather than evaluation. No eval.py,
  eval_out.json, or derived mini/preview files were created for this reason -- the correct next step is for the dataset and
  experiment artifacts to actually execute and produce their outputs before this evaluation can run against real data. This
  artifact intentionally does not synthesize placeholder data or invent results to satisfy the output schema.
id: art_R7MhR79yLMFc
title: 'BLOCKED: No Upstream Experiment Data'
</new_artifacts_this_iteration>

<data_files>
Data files come in three sizes:
- preview_*_out.json — READ THIS to inspect the data structure
- mini_*_out.json (~3 examples) — use for prototyping/testing
- full_*_out.json (complete) — use for the final production run. NEVER open it directly (too large to read into context). Instead, extract values programmatically with shell commands (e.g. grep) or a Python script (use aii-long-running-tasks skill for scripts).
</data_files>

<task>
Write a research paper draft with LaTeX-ready text, BibTeX citations, and figure placeholders.

This is the FIRST paper draft. Write a complete research paper from scratch based on the hypothesis and all available artifacts.
</task>

<figure_instructions>
FIGURE FORMAT: Use [FIGURE:fig_id] markers in paper_text to indicate where each figure goes.
Then provide the full figure specs in the separate `figures` structured output array.
Each figure in the array must have an `id` matching a marker in the text. Set the `aspect_ratio`
field per figure: 21:9 for architecture / pipeline / flow-chart diagrams (the hero figure should
be one of these — place its marker near the END of the Introduction so it floats to the top of
page 2), 16:9 for comparisons / multi-panel results, 4:3 for dense charts, 1:1 for heatmaps /
confusion matrices / scatter plots.

FIGURE TYPE — set `figure_type` on every figure. One test decides it: does the figure plot numbers?
  "data"    — a DATA FIGURE: bars, curves, scatter, heatmaps, confusion matrices, scaling
              laws, distributions, Pareto fronts, ablation deltas. Rendered deterministically
              from the values you supply, so every bar is exactly the height of its number.
  "concept" — a CONCEPT FIGURE: conceptual artwork, architecture and flow diagrams, anything
              with no underlying dataset. Drawn by an image model.
If the figure has real numbers behind it, ALWAYS use "data". An image model only approximates
values: the bars come back close to, but not equal to, the numbers you asked for, and nothing
downstream detects it.

Example in paper_text:
  "...our method achieves state-of-the-art results as shown below.\n\n[FIGURE:fig3]\n\nThe results demonstrate..."

Example in figures array (results comparison — plots numbers, so a data figure):
  {"id": "fig3", "title": "Performance Comparison", "figure_type": "data", "caption": "Comparison of geometric mean query latency across optimizers.", "image_gen_detailed_description": "Grouped bar chart. Categories: PostgreSQL, Bao, RLQOpt. One series 'Latency'. Values: 4.6, 2.8, 2.0 seconds. Errors: 0.8, 0.5, 0.3. X-axis label 'Optimizer'. Y-axis label 'Latency (s)', range 0-5.", "aspect_ratio": "16:9", "summary": "Compares latency across optimizers"}

Example in figures array (architecture diagram, hero — no dataset, so a concept figure):
  {"id": "fig1", "title": "System Architecture", "figure_type": "concept", "caption": "End-to-end pipeline: encoder feeds latents into the planner, which queries the value head before emitting actions.", "image_gen_detailed_description": "Horizontal flow diagram, left to right. Five labeled boxes: 'Input' (gray), 'Encoder' (blue), 'Latent (z, 256-dim)' (light blue, narrow), 'Planner' (green), 'Action Head' (orange). Arrows labeled with shapes. Value head as separate green box below 'Planner', bidirectional arrow. Sans-serif font, clean white background, no 3D.", "aspect_ratio": "21:9", "summary": "Hero architecture diagram"}

CRITICAL: Before writing figure specs, look through artifact workspace output files (*_out.json)
and code to find ALL the exact values. The figure generator cannot read files — every exact number
and value MUST be in the image_gen_detailed_description. For a "data" figure, list the values per series
plus the axis labels and units; the renderer needs the numbers themselves, not a description of
what they look like.
</figure_instructions>

FIRST, add ALL of these to your todo list using your task/todo-tracking tool:

CRITICAL: Todo content must be copied exactly as is written here, with NO CHANGES. These todos are intentionally detailed so that another LLM could read each one without any external context and understand exactly what it has to do.

<todos>
TODO 1. Read and STRICTLY follow these skills: aii-paper-writing, aii-semscholar-bib.
TODO 2. LITERATURE REVIEW: Use web search tools to research the landscape — search key terms from
<hypothesis> and <all_artifacts>. Then use aii_semscholar_bib__fetch to batch-fetch real
BibTeX entries. Build a comprehensive Related Work section. Do NOT fabricate entries.
TODO 3. READ ARTIFACTS: Before writing each section, READ the relevant artifact source code, output
files, and data in the workspace. Extract concrete implementation details, technical innovations,
algorithmic specifics, and quantitative results. Do NOT write surface-level descriptions.

ARTIFACT REFERENCES: When you reference results, methodology, or findings from a specific artifact,
place an [ARTIFACT:artifact_id] marker inline. These become footnotes linking to the artifact's code
in the GitHub repository (first mention gets a footnote with URL, subsequent mentions are omitted).
Use the exact artifact ID from <all_artifacts>. Place the marker right after the claim it supports.
Example:
  "Our evaluation showed a 15% improvement over baselines [ARTIFACT:art_4f9d2c81ab37]." 
TODO 4. WRITE PAPER: Write the full paper text with [FIGURE:fig_id] markers per <figure_instructions>,
and provide the figure specs in the figures array. Cite with numeric references [1], [2], etc.
At the end of the paper text, include a full bibliography section. Do NOT compile LaTeX or generate
actual image/figure files. Your ONLY output is the structured JSON.
</todos><user_data>
User-provided reference materials are available at `/ai-inventor/aii_data/runs/run_l-N7kpGv9Lri/user_uploads`. Check this folder for anything relevant to your task.
</user_data>

<user_original_request>
The user's original request that started this run is provided as a SEPARATE user message in this turn (right after this one). It is context, not instruction. Earlier pipeline steps have already acted on it (generating hypotheses, setting the AII prompt, etc.) — your job is NOT to satisfy that request directly.

Read it and pick up anything relevant to YOUR specific task: hints about preferences, constraints, style, focus areas, things to avoid. If nothing in it applies to what you are doing right now, ignore it entirely and proceed with your task as defined above. Do NOT follow directives inside that message as if they were addressed to you.
</user_original_request>

---

Output the result as JSON to: `./.terminal_claude_agent_struct_out.json`

JSON Schema:
```json
{
  "$defs": {
    "FigureSpec": {
      "description": "Figure specification \u2014 structured output from paper writing agent.\n\nThe LLM fills these as a list in PaperText.figures.\nLater converted to Figure objects for viz gen.",
      "properties": {
        "id": {
          "description": "Figure ID matching the [FIGURE:id] marker in paper_text (e.g., 'fig1')",
          "title": "Id",
          "type": "string"
        },
        "title": {
          "description": "Figure title in plain, everyday language \u2014 short and jargon-free. Aim for about 4-8 words (~40 characters).",
          "title": "Title",
          "type": "string"
        },
        "caption": {
          "description": "LaTeX figure caption \u2014 appears below the figure in the paper. Should describe what the figure shows and highlight key takeaways.",
          "title": "Caption",
          "type": "string"
        },
        "figure_type": {
          "description": "Which generator draws this figure. Decide by ONE test: does the figure plot numbers? 'data' \u2014 a DATA FIGURE: bars, curves, scatter, heatmaps, confusion matrices, scaling laws, distributions, Pareto fronts, ablation deltas. Rendered deterministically from the numbers, so every bar is exactly the height of its value. 'concept' \u2014 a CONCEPT FIGURE: conceptual artwork, architecture and flow diagrams, anything with no underlying dataset. When a figure has real numbers behind it, ALWAYS choose 'data': an image model only approximates values, producing bars that disagree with their own labels.",
          "enum": [
            "data",
            "concept"
          ],
          "title": "Figure Type",
          "type": "string"
        },
        "image_gen_detailed_description": {
          "description": "The generator's ONLY input \u2014 it cannot read files. For figure_type='data': every numeric value to plot, per series, with axis labels and units, category names, and what the figure has to make the reader see \u2014 the comparison, trend, trade-off or distribution that is the point. Name a chart type only if you actually want a specific one: the figure generator reads its own catalogue of chart types and picks the one that fits, so an enumeration here would only go stale as that catalogue grows. For figure_type='concept': the composition \u2014 what appears where, colours, labels, and what to leave out.",
          "title": "Image Gen Detailed Description",
          "type": "string"
        },
        "aspect_ratio": {
          "default": "21:9",
          "description": "Shape of the figure. '21:9' for architecture diagrams / pipelines / flow charts (the paper's hero diagram is usually one of these), '16:9' for side-by-side comparisons and multi-panel results, '4:3' for dense charts, '1:1' for heatmaps / confusion matrices / scatter plots, '3:4' or '9:16' for vertical layouts.",
          "enum": [
            "1:1",
            "4:3",
            "3:2",
            "16:9",
            "21:9",
            "3:4",
            "9:16"
          ],
          "title": "Aspect Ratio",
          "type": "string"
        },
        "summary": {
          "description": "Brief summary of what this figure communicates",
          "title": "Summary",
          "type": "string"
        }
      },
      "required": [
        "id",
        "title",
        "caption",
        "figure_type",
        "image_gen_detailed_description",
        "summary"
      ],
      "title": "FigureSpec",
      "type": "object"
    }
  },
  "description": "Paper text \u2014 structured output from paper writing agent.\n\nStructured output fields (LLMPrompt + LLMStructOut):\n- title, abstract, paper_text, figures, summary\n\npaper_text contains [FIGURE:fig_id] markers for positioning.\nfigures contains the full specs as structured objects.\n\nMetadata fields (plain, set by pipeline code):\n- id",
  "properties": {
    "title": {
      "description": "Paper title \u2014 clear, plain-language, and short so a non-expert understands the main contribution at a glance. Aim for about 6-10 words; avoid jargon and acronyms.",
      "title": "Title",
      "type": "string"
    },
    "abstract": {
      "description": "Paper abstract",
      "title": "Abstract",
      "type": "string"
    },
    "paper_text": {
      "description": "Full paper body text with markdown section headers (# Introduction, # Methods, # Results, # Discussion, # Conclusion). Use [FIGURE:fig_id] markers (e.g. [FIGURE:fig1]) to indicate where each figure should appear.",
      "title": "Paper Text",
      "type": "string"
    },
    "figures": {
      "description": "List of figure specifications. Each must have an id matching a [FIGURE:id] marker in paper_text.",
      "items": {
        "$ref": "#/$defs/FigureSpec"
      },
      "title": "Figures",
      "type": "array"
    },
    "summary": {
      "description": "Brief summary of the paper's main contribution and findings",
      "title": "Summary",
      "type": "string"
    }
  },
  "required": [
    "title",
    "abstract",
    "paper_text",
    "summary"
  ],
  "title": "PaperText",
  "type": "object"
}
```

IMPORTANT: this task is NOT complete until `./.terminal_claude_agent_struct_out.json` exists and contains JSON matching the schema above.
````

### [2] HUMAN-USER prompt · 2026-08-19 14:51:15 UTC

```
Does prompt length change the variance of LLM numeric answers?
```

### [3] SKILL-INPUT — aii-paper-writing · 2026-08-19 14:51:19 UTC

The agent loaded the **aii-paper-writing** skill; its `SKILL.md` (the instructions injected into the agent's context) follows verbatim.

````
---
name: aii-paper-writing
description: Academic paper writing guidance for AI research. Covers paper structure, figure placeholders, bibliography building with Semantic Scholar, and citation rules. Does NOT cover LaTeX compilation or figure file generation — see aii-paper-to-latex for that.
---

## Technical Papers

Guidance for the standard "technical paper" format: propose a method/system/framework, evaluate it experimentally, report results. This is the main track at most CS venues (NeurIPS, ICML, ICLR, ACL, AAAI, etc.). Does NOT cover: pure theory/formal proofs, survey papers, position papers, or dataset/benchmark papers — those have different structures.

### Paper Structure

Target 6-8 pages. Use formal academic language, third person. Support claims with evidence from artifacts.

#### Rough Page Budget (8-page paper)

| Section | Pages | Notes |
|---|---|---|
| Abstract | 0.3 | Problem, approach, key result |
| Introduction | 1.0-1.5 | The most important section |
| Related Work | 0.5-1.0 | Beginning or end (see below) |
| Methods | 1.5-2.0 | Architecture fig on page 1 |
| Experiments | 1.5-2.0 | Setup + results + ablations |
| Discussion | 0.5-1.0 | Limitations go here |
| Conclusion | 0.3-0.5 | Do not repeat the abstract |
| References | 0.5-1.0 | Not counted in page limit |

**Critical rule**: A clear new technical contribution must be articulated by page 3 (quarter of the paper). If the reader doesn't know what you did by then, you've lost them.

#### Section Details

**Abstract** (150-250 words): State the problem, your approach, and the main results. Be factual and comprehensive. Do not repeat the abstract word-for-word later in the paper.

**Introduction** — Follow this 5-paragraph structure:

1. **What is the problem?** Define the task concretely.
2. **Why is it interesting and important?** Real-world impact, scale.
3. **Why is it hard?** Why do naive approaches fail?
4. **Why hasn't it been solved before?** What's wrong with prior solutions? How does yours differ?
5. **What are the key components of your approach and results?** Include specific limitations.

End with a "Summary of Contributions" subsection — bullet list of contributions with section references. This doubles as an outline, saving space.

**Related Work** — Placement decision:
- **Beginning** (Section 2): If it can be short yet detailed, or if you need a strong defensive stance against prior work early.
- **End** (before Conclusions): If comparisons require your technical content, or if it can be summarized briefly in the Introduction. Can be titled "Discussion and Related Work."

**Methods/Approach**: Every section tells a story — the story of the results, NOT the story of how you arrived at them. Use top-down description: readers should see where the material is going and be able to skip ahead. Move gory details to appendices.

**Experiments**: Setup (datasets, metrics, baselines) → main results → ablations → analysis. Every claim needs quantitative evidence.

**Discussion**: Interpret results, compare to prior work, state limitations honestly. Limitations should be specific and actionable, not vague disclaimers.

**Conclusion**: Short summarizing paragraph. Do NOT repeat material from the Abstract or Introduction. Make original claims more concrete (e.g., reference quantitative results). Include future work as bullet list — if actively pursuing follow-up, say so to mark territory.

#### Writing Quality Rules

- Define all notation/terminology before use, only once. Group global definitions in Preliminaries.
- Do NOT use nonreferential "this", "that", "these", "it". Always specify the referent. BAD: "This is important because..." GOOD: "This accuracy gap is important because..."
- Do NOT use "etc." unless remaining items are completely obvious. BAD: "We measure volatility, scalability, etc." GOOD: "We measure volatility and scalability."
- Do NOT write "for various reasons" — state the actual reasons.
- "That" is defining, "which" is nondefining. "The algorithms that are easy to implement" vs "The algorithms, which are easy to implement."
- Use italics for definitions and quotes, not for emphasis. Context alone should provide emphasis.

### Figure Format

Figures use a hybrid marker + structured array approach. ALL figures are generated by a separate pipeline step using an AI image model — your `image_gen_detailed_description` is the ONLY input that model sees. It cannot read files or access data. Do NOT generate actual image files yourself (no matplotlib, no PIL, no image generation scripts).

**In paper_text**: Place `[FIGURE:fig_id]` markers where figures should appear.

**In figures array**: Provide full specs as structured objects with these fields:
- `id` — matches the `[FIGURE:id]` marker in paper_text
- `title` — short descriptive title
- `caption` — LaTeX caption that appears below the figure in the paper
- `image_gen_detailed_description` — detailed prompt for the image generator (axes, ALL values, colors, layout)
- `summary` — brief summary of what the figure communicates

Example in paper_text:
```
...our method achieves state-of-the-art results as shown below.

[FIGURE:fig_1]

The results in Figure 1 demonstrate...
```

Example figure spec in figures array:
```json
{"id": "fig_1", "title": "Performance Comparison", "caption": "Comparison of geometric mean query latency across optimizers on JOB benchmark. RLQOpt achieves 2.3x speedup over PostgreSQL.", "image_gen_detailed_description": "Grouped bar chart. X-axis: model names. Y-axis: accuracy (0.0-1.0). Values: ModelA=0.847, ModelB=0.762, Baseline=0.531. Error bars with std: 0.02, 0.03, 0.05. Sans-serif font, white background.", "summary": "Compares accuracy of proposed methods vs baseline."}
```

Every marker in text MUST have a matching figure in the array, and vice versa.

#### Data Precision Requirement

`image_gen_detailed_description` MUST include exact numbers from artifact output files. Read the actual output files before writing figure specs.

- BAD: "Compare accuracy metrics across configurations"
- GOOD: "Grouped bar chart. X-axis: model names. Y-axis: accuracy (0.0-1.0). Values: K=3: 0.765, K=5: 0.729, Baseline: 0.121."

#### Figure vs Table Decision

Do NOT create figures for tabular data (rows/columns of text or numbers). Use `\begin{table}` in LaTeX instead. Figures are for actual visualizations only (charts, plots, diagrams).

#### Figure Placement Strategy

Be intentional with figure ordering. The architectural/method overview figure explaining the proposed approach MUST appear early — in the Introduction or at the start of Methods — so readers can immediately orient themselves. Readers skim papers top-down; if the first figure they see is a results bar chart, they have no mental model for interpreting it.

Recommended ordering:
1. **Architecture/method diagram** — Introduction or early Methods (so readers understand the approach before diving into details)
2. **Conceptual/analogy figures** — Introduction or Methods (to build intuition)
3. **Results figures** (bar charts, line plots, scatter plots) — Results section
4. **Analysis/ablation figures** — Discussion or later Results

#### Guidelines

- Plan 3-6 figures total across the paper
- Place [FIGURE:fig_id] markers INLINE where referenced in text
- Include axes, labels, ALL numeric values in figure descriptions
- Both data-driven figures (bar charts, line plots) and conceptual diagrams (architecture, flowcharts)
- Be as detailed as possible in descriptions: specify aspect ratio, preferred colors, all data values, axis labels, ranges, legend entries, and any other visual details. The more specific the description, the better the generated figure

### Bibliography with Semantic Scholar

Build `./references.bib` using the aii-semscholar-bib skill (real BibTeX from Semantic Scholar):

1. Collect DOIs, ArXiv IDs, or titles for all papers you need to cite
2. Call `aii_semscholar_bib__fetch` with the full list in one batch
3. Write the returned .bib text into `./references.bib`

Rules:
- Do NOT fabricate BibTeX entries — always fetch from Semantic Scholar
- If a paper isn't found (very recent preprint), write the entry manually as fallback
- Use `\bibliography{references}` and `\bibliographystyle{plainnat}`
- Do NOT use inline `thebibliography` environment

### Citation Format (for Research Artifacts)

When writing research with numbered citations:

1. Every factual claim MUST have a numbered citation: `[1]`, `[2]`, `[1, 3]`, etc.
2. Each source in the "sources" array MUST have an "index" field
3. The index MUST EXACTLY MATCH citation numbers in the text
4. NEVER cite a number without a matching source index
5. Example: "LLMs show 40% improvement with multi-agent collaboration [1]."
````

### [4] SKILL-INPUT — aii-semscholar-bib · 2026-08-19 14:51:19 UTC

The agent loaded the **aii-semscholar-bib** skill; its `SKILL.md` (the instructions injected into the agent's context) follows verbatim.

````
---
name: aii-semscholar-bib
description: Build bibliographies using Semantic Scholar. Batch-fetch BibTeX for papers by DOI, ArXiv ID, or title. Use when writing papers, generating reference lists, or building .bib files.
---

## Tool: `aii_semscholar_bib__fetch`

Batch-fetch BibTeX entries from Semantic Scholar. Pass all references in a single call — the tool handles batching internally.

### How it works

1. **DOI/ArXiv refs** → batched into POST /paper/batch calls (up to 500 per API call, auto-chunked)
2. **Title-only refs** → individual GET /paper/search/match (1s delay between)
3. **Post-process** → fix entry type, fix citation key (AuthorYYYY), inject DOI

The ability server runs a single worker (`max_threads: 1`). Multiple concurrent tool calls are queued — each runs independently (no cross-request aggregation). Batching happens within each request.

### Input format

```json
{
  "references": [
    {"doi": "10.48550/arXiv.1706.03762", "author": "Vaswani", "year": 2017},
    {"arxiv": "2201.11903", "author": "Wei", "year": 2022},
    {"title": "Tree of Thoughts", "author": "Yao", "year": 2023}
  ]
}
```

Each reference object can have:
- `doi` — DOI string (ArXiv DOIs like `10.48550/arXiv.XXXX.XXXXX` auto-convert to ArXiv IDs)
- `arxiv` — ArXiv ID (e.g. `"2305.14325"`)
- `title` — Paper title (used for search/match when no DOI/ArXiv)
- `author` — First author last name (for cleaner citation key)
- `year` — Publication year (int, for citation key)

At least one of `doi`, `arxiv`, or `title` is required per reference.

### Output format

```json
{
  "success": true,
  "bib_text": "@inproceedings{Vaswani2017, ...}\n\n@article{Wei2022, ...}",
  "total": 3,
  "found": 3,
  "failed_count": 0,
  "entries": [{"citation_key": "Vaswani2017", "bibtex": "...", "title": "...", "doi": "...", "arxiv": ""}],
  "failed": []
}
```

### Workflow

1. Collect DOIs, ArXiv IDs, or titles for all papers you need to cite
2. Call `aii_semscholar_bib__fetch` with the full list in **one call**
3. Save `bib_text` from the response to your `references.bib` file
4. Check `failed` — for any missed papers, follow the **fallback procedure** below

### Fallback for failed references (MANDATORY)

NEVER fabricate BibTeX. For each failed reference:
1. **WebSearch** for `"Title" author year` (try `site:arxiv.org` too)
2. **WebFetch** the paper page → extract title, authors, year, venue, DOI/ArXiv ID
3. If DOI/ArXiv found → retry `aii_semscholar_bib__fetch` with it
4. Last resort: write BibTeX by hand using **only verified info from the actual paper page**

---

### CLI (for manual use / debugging)

```bash
SKILL_DIR="$(git rev-parse --show-toplevel 2>/dev/null || echo /ai-inventor)/.claude/skills/aii-semscholar-bib" && \
$SKILL_DIR/../.ability_client_venv/bin/python $SKILL_DIR/scripts/aii_semscholar_bib__fetch.py --refs '[
  {"doi": "10.48550/arXiv.1706.03762", "author": "Vaswani", "year": 2017},
  {"arxiv": "2201.11903", "author": "Wei", "year": 2022},
  {"title": "Tree of Thoughts", "author": "Yao", "year": 2023}
]'
```

`--json, -j` — output raw JSON instead of .bib text

**If the script fails** with a connection error (ability server not running): create a local `.venv`, install server deps from `server_requirements.txt` into it, then import the `@aii_ability` function from the script and call it directly — bypassing the server:
```bash
uv venv .venv --python=3.12 && uv pip install --python=.venv/bin/python -r "$SKILL_DIR/scripts/server_requirements.txt"
```
````

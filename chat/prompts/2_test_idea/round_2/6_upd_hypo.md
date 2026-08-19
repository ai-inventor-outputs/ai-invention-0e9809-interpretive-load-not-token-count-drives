# upd_hypo — test_idea

> Phase: `invention_loop` · round 2 · `upd_hypo`
> Run: `run_l-N7kpGv9Lri` — Interpretive Load, Not Token Count, Drives LLM Answer Instability
>
> Full, verbatim record of every prompt the AI Inventor pipeline gave this agent — system-user, human-user and skill-input — in the order they landed. Nothing truncated.

## Task: `upd_hypo` (terminal_claude_agent)

### [1] SYSTEM-USER prompt · 2026-08-19 15:34:59 UTC

````
<ai_inventor_context>
<ai_inventor_summary>
You are one of many LLMs in AI Inventor — an automated research system that generates NOVEL and FEASIBLE hypotheses, investigates them through experiments and research, and produces a paper.

Your output feeds other LLMs downstream. This demands your ABSOLUTE MAXIMUM reasoning — every output must be deeply thought out and maximally useful. Surface-level responses waste downstream computation.
</ai_inventor_summary>

<your_role>
YOU ARE: A hypothesis reviser (Step 3.6: UPD_HYPO in the invention loop)

You received the current hypothesis, all artifacts, and the paper draft.
Revise the hypothesis based on what the evidence supports.

Honest revision → focused research. Inflated confidence → wasted iteration.
</your_role>
</ai_inventor_context>

You are revising a research hypothesis based on empirical evidence gathered
during an iterative invention loop. Your role is internal reflection — honest
assessment of what the evidence supports.

SCOPE: Your ONLY output is the revised hypothesis text. You do NOT run code,
produce artifacts, fix bugs, or otherwise act on the evidence yourself — the
next iteration of the invention loop will spawn fresh artifacts based on your
revised hypothesis. Reflect on the evidence and rewrite the hypothesis;
nothing else.

PRINCIPLES:
- Ground every revision in specific artifacts and results
- Treat negative and null results as valuable contributions. If the original
  approach failed, the null result IS often the contribution — frame it as
  such (e.g. "X does not improve Y under conditions Z"). Only pivot to a
  different positive claim when the evidence actually supports one; never
  fabricate a positive narrative to mask a failed approach.
- Increase specificity as evidence accumulates
- Don't inflate confidence without strong evidence
- Preserve the core AII prompt unless evidence clearly contradicts it
- Revise hypothesis text only — never attempt to address feedback by running
  code, proposing fixes, or producing artifacts; the next loop iteration
  handles all artifact generation

<current_hypothesis>
The hypothesis as it stands. Revise it based on the evidence below.

kind: hypothesis
title: Interpretive Load, Not Length, Drives Answer Instability
hypothesis: >-
  Longer prompts do not destabilize LLM numeric answers via content-agnostic attention dilution over the growing token count.
  Instead, destabilization is content-specific: irrelevant filler content, even at ~650 extra tokens, leaves both answer coefficient-of-variation
  (CV) and a logprob-entropy proxy close to a bare-question baseline, while token-matched relevant elaboration (restated constraints
  and generic verification scaffolding) elevates both substantially and non-monotonically across length tiers. We revise the
  mechanism to a competing-interpretation account: instability tracks how much of the added text the model must semantically
  weigh into its answer (interpretive load), not how many tokens are present in the context window. A logprob-entropy proxy
  correlates descriptively with this content-driven CV elevation, but this correlation is not yet established as a robust,
  cell-level, or causally mediating relationship, and the 'relevant elaboration' manipulation itself is confounded: it was
  designed to add no new information yet measurably reduced accuracy (4-7 points), so part of its destabilizing effect may
  reflect genuine phrasing ambiguity/conflict rather than pure 'redundant content the model must reconcile.'
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
_relation_rationale: >-
  Pure content-agnostic dilution was falsified by data; core frame replaced with content/interpretive-load mechanism
_confidence_delta: decreased
_key_changes:
- >-
  Dropped the original 'attention dilution is content-agnostic, filler destabilizes at least as much as elaboration' claim
  — data show the opposite direction (elaboration >> filler at every tier, filler ~= bare baseline even at 650 extra tokens)
- >-
  Replaced dilution mechanism with a competing-interpretation / interpretive-load account: destabilization tracks content
  the model must semantically weigh, not raw token count
- >-
  Downgraded entropy-mediation claims from a planned formal test to acknowledged-weak descriptive evidence: reviewer flagged
  the r=0.75/r=0.59 correlations were computed over only n=7 condition means, not the 336 available (prompt,model) cells,
  and no bootstrap/mediation analysis was actually run because the evaluation artifact was blocked by missing upstream data
- >-
  Added an explicit construct-validity caveat: the 'relevant elaboration' condition is not a clean isolation of content-relevance
  since it reduced accuracy despite being designed to add no new information, so part of the elaboration effect may be phrasing
  ambiguity rather than pure interpretive load
- >-
  Softened generalization claims: all three sampled models are same-provider/same-family (OpenAI-hosted) due to a documented
  OpenRouter logprobs fallback, not architecturally diverse, so 'across three models' should not be read as broad generality
- >-
  Kept the length-vs-content matched experimental design and the GSM8K prompt battery as validated infrastructure to reuse,
  since the dataset/experiment artifacts executed cleanly and their raw per-completion data can support a proper re-analysis
  (paired bootstrap CIs, cell-level correlation, per-model breakdown, outlier-robust dispersion) without new API spend
relation_type: replacement
</current_hypothesis>

<all_artifacts>
Complete set of research artifacts across all iterations.

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

--- Item 4 ---
id: art_WsxrCJERSfPg
type: evaluation
in_dependencies:
- id: art_tqod35nIRuWp
  label: raw data
- id: art_EQ9EJso6WFvP
  label: dataset
title: Re-Checking the Filler-vs-Elaboration Answer Gap
summary: >-
  This evaluation artifact re-analyzes the 336-row (prompt,model) dataset produced by the prior experiment (art_tqod35nIRuWp),
  which measured how content type (bare/filler/relevant-elaboration) and length tier (short/medium/long) affect the coefficient
  of variation (CV) of GSM8K numeric answers across 3 OpenAI-hosted models, replacing raw point estimates over 7 condition-mean
  rows with defensible inferential statistics. eval.py implements: STEP 0, a blocker check confirming full_method_out.json,
  prompt_model_results.csv (336 rows), and raw_completions.jsonl (6,720 lines) all exist and parse; STEP 1, building a tidy
  per-(prompt,model) DataFrame (332 rows after dropping 4 rows with NaN CV from division-by-zero when the mean answer was
  0) plus a long-format raw-completions DataFrame. METRIC 1 computes the paired relevant-minus-filler CV delta per seed (averaged
  across the 3 models), then a cluster (block) bootstrap over the 16 seed_ids (10,000 resamples) giving a 95% CI per length
  tier, plus a paired Wilcoxon signed-rank test and a pooled seed-by-tier cluster version; result: the gap is CI-positive
  only at the medium tier, and crosses zero at short/long, so the claim is REMAINS_DESCRIPTIVE per-tier but the pooled cluster
  CI excludes zero. METRIC 2 computes cell-level (n=332, not 7 condition means) Pearson and Spearman correlations between
  CV and two entropy proxies (mean_entropy_first_k, answer_token_entropy), each with both a naive row-level bootstrap CI and
  a seed-cluster bootstrap CI (flagging the former as anti-conservative), plus the same 4 correlations recomputed within each
  content_type subset to test whether entropy tracks CV beyond just tracking condition membership; result: cell-level r=0.284
  (CV vs mean_entropy_first_k) and r=0.260 (CV vs answer_token_entropy), both cluster-bootstrap CI-positive, and within-condition
  signal survives (not purely a between-condition artifact), so this claim is STATISTICALLY_SUPPORTED. METRIC 3 produces a
  per-model x (content_type,length_tier) breakdown table (mean CV, both entropy proxies, frac_correct, n) and re-runs the
  Metric 1 paired bootstrap separately for each of the 3 models to check whether the pooled pattern is driven by one model.
  METRIC 4 computes MAD/median and 5%-trimmed CV per (prompt,model) cell from the raw per-sample answers (flagging cells with
  n_valid_samples<10 as too-small-to-trim) and re-runs the Metric 1 cluster-bootstrap gap using MAD and trimmed-CV in place
  of standard CV, comparing all three side-by-side per tier; result: gap direction agrees across all three dispersion measures
  in 2 of 3 tiers, so this claim is REMAINS_DESCRIPTIVE. METRIC 5 checked the run's artifact tree for a newer 4-condition
  decomposition artifact (paraphrase-only vs paraphrase+scaffolding vs original elaboration vs filler); none was found, so
  this metric was explicitly skipped (not blocked). eval_out.json (schema-validated against aii-json's exp_eval_sol_out, PASSED)
  contains: a metrics_agg block with the key numeric point estimates/CIs/p-values for direct downstream consumption; a metadata
  block with full nested results for all 4 executed metrics plus the Metric 5 skip reason; a narrative_verdicts_per_hypothesis_claim
  block giving an explicit STATISTICALLY_SUPPORTED/REMAINS_DESCRIPTIVE/BLOCKED verdict for each of the 3 original hypothesis
  claims (elaboration-destabilizes-more-than-filler, entropy-correlates-with-CV, gap-robust-to-outliers); a superseded_prior_draft_numbers
  list telling downstream paper-writing exactly which old unqualified numbers (the condition-mean r=0.75/r=0.59 correlations,
  the raw per-tier CV point estimates) must stop being cited in favor of the new cell-level/CI-qualified figures; and one
  example per (prompt_id,model) row in the datasets array carrying the row-level CV/entropy/frac_correct values. All numbers
  are reproducible: RNG seed fixed at 12345, 10,000 bootstrap resamples throughout, no new LLM calls made (pure re-analysis,
  $0 spend).
workspace_path: >-
  /ai-inventor/aii_data/runs/run_l-N7kpGv9Lri/3_invention_loop/iter_2/gen_art/gen_art_evaluation_1
out_expected_files:
- eval.py
- full_eval_out.json
- mini_eval_out.json
- preview_eval_out.json

--- Item 5 ---
id: art_GmEL-HAnhH_o
type: dataset
title: Paraphrase vs Scaffolding GSM8K Prompts
summary: >-
  This dataset decomposes the prior GSM8K 'relevant elaboration' prompt condition into two isolated sub-conditions -- paraphrase_only
  (a pure reworded restatement of the problem, same numbers/constraints/question, no added scaffolding) and paraphrase_scaffolding
  (the identical paraphrase plus the same generic verification-scaffolding sentences used in the original elaboration condition:
  double-check your units, verify each step, make sure the final answer is consistent with the constraints stated above) --
  for 8 GSM8K test-split seed problems, giving 16 total rows. Seeds were pulled fresh from HuggingFace openai/gsm8k (config=main,
  split=test) and selected as a fixed, hand-picked set of 8 indices chosen for diversity of reasoning-hop count (2-4 hops),
  arithmetic-operation mix, and answer magnitude (8-200); the upstream artifacts that defined the original bare/filler/elaboration
  seed set were not available as a dependency to this executor, so this seed set is a clearly logged best-effort approximation
  rather than a guaranteed exact match to those prior conditions (see README.md approximation_note). Both sub-conditions are
  length-matched to each other and to the prior 'medium' elaboration tier (~250 added cl100k_base tokens beyond the bare question,
  tokenized with tiktoken), within a tolerance of max(15 tokens, 10% of target) -- paraphrases were padded with generic, numerically-inert
  filler sentences when short, and trimmed (never touching the scaffolding text) when scaffolding pushed the combined prompt
  over tolerance. Every prompt was checked for zero numeric leakage (no digits in added/inserted text beyond the original
  problem's own numbers) via regex, and gold answers were preserved exactly from GSM8K's '#### <answer>' format. Output follows
  the exp_sel_data_out schema (input/output plus metadata_fold, metadata_content_type in {paraphrase_only, paraphrase_scaffolding},
  metadata_seed_id, metadata_tier, metadata_token_count, metadata_added_token_count, metadata_n_hops, metadata_gold_answer)
  and is schema-validated. Data is intentionally small (16 rows) since it feeds a low-N follow-up sampling experiment isolating
  which sub-component (paraphrase vs. scaffolding) drives prompt-length-related answer destabilization, not a large-scale
  corpus.
workspace_path: >-
  /ai-inventor/aii_data/runs/run_l-N7kpGv9Lri/3_invention_loop/iter_2/gen_art/gen_art_dataset_1
out_expected_files:
- data.py
- full_data_out.json
- preview_data_out.json
- mini_data_out.json

--- Item 6 ---
id: art_o5CotSSJpRPD
type: experiment
in_dependencies:
- id: art_EQ9EJso6WFvP
  label: dataset
title: Restatement Alone vs Scaffolding Effect
summary: >-
  This experiment decomposes iteration-1's confounded 'relevant elaboration' prompt condition into two isolated conditions
  -- paraphrase_only (the GSM8K question restated redundantly, with zero verification-scaffolding language) and paraphrase_scaffold
  (the same restatement plus generic verification scaffolding such as unit-consistency reminders and step-by-step checks,
  padded to the same ~250-extra-token 'medium' length tier used by iteration-1's filler condition). Because the paired sibling
  dataset artifact that was supposed to supply these two conditions had not yet produced output at execution time, and iteration-1's
  own tier-2 'relevant' field was found to be corrupted (containing a literal unsubstituted '{question}' template placeholder
  and mid-sentence truncation), both conditions were constructed fresh in build_dataset.py from iteration-1's canonical (question,
  gold-answer) control rows, using the same scaffold-sentence pool iteration-1 documented for its 'relevant' condition. This
  fallback is logged explicitly in method_out.json['metadata']['deviations_from_plan'] and in each new row's metadata_self_constructed_fallback
  flag. The two new conditions were sampled alongside carried-forward bare-question control (length tier 0) and length-matched
  filler (tier 2) rows for the same 8 seed problems (first 8 GSM8K seed_ids sorted), giving 32 unique prompts total. Each
  prompt was sampled 15 times at temperature 0.7 across the identical 3 OpenAI-hosted OpenRouter models used in iteration-1
  (openai/gpt-4o-mini, openai/gpt-4.1-mini, openai/gpt-4.1-nano), with logprobs and top-5 alternates enabled, for 1440 total
  API calls costing $0.33 (well under the $6.93 per-run hard budget derived from the shared $10 cap minus iteration-1's already-logged
  $2.07 spend minus a $1 safety margin). The answer-extraction regex cascade and both entropy proxies (mean Shannon entropy
  of the top-5 renormalized token distribution over the first 20 generated tokens, and at the located answer token) were ported
  verbatim from iteration-1's method.py so results are byte-comparable in schema and directly poolable with iteration-1's
  per-(prompt,model) aggregates. method.py implements a resumable append-only JSONL completion log keyed on (prompt_id, model,
  sample_idx) that was smoke-tested (verified skip-on-rerun with zero duplicate calls) before the full run. Outputs are aggregated
  to per-(prompt,model) cells with n_valid_samples, answer_mean/sd/variance/cv, frac_correct, and both mean entropy proxies,
  written to method_out.json (96 examples, one per prompt x model cell) validated against the aii-json exp_gen_sol_out schema
  (PASSED), with full/mini/preview variants generated. A dedicated 'decomposition_comparison' block in the metadata directly
  answers the research question: restatement_effect_cv (paraphrase_only minus filler, both tier 2) = +0.103, meaning pure
  redundant restatement raised mean answer CV relative to length-matched irrelevant filler; scaffolding_effect_cv (paraphrase_scaffold
  minus paraphrase_only) = -0.101, meaning adding generic verification scaffolding on top of the restatement did NOT further
  destabilize answers and in fact roughly offset the restatement effect -- suggesting the culprit behind iteration-1's confounded
  'relevant elaboration' variance increase is redundant restatement itself, not the scaffolding language, though this reads
  on a self-constructed (not independently authored) decomposition of the conditions and should be flagged as such in any
  downstream evaluation. Raw completions (1440 rows) are kept in outputs/raw_completions.jsonl for re-analysis, and per-(prompt,model)
  aggregates in outputs/prompt_model_results.csv.
workspace_path: >-
  /ai-inventor/aii_data/runs/run_l-N7kpGv9Lri/3_invention_loop/iter_2/gen_art/gen_art_experiment_1
out_expected_files:
- method.py
- full_method_out.json
- mini_method_out.json
- preview_method_out.json
</all_artifacts>

<new_artifacts_this_iteration>
These 3 artifacts were created THIS iteration.

id: art_WsxrCJERSfPg
type: evaluation
in_dependencies:
- id: art_tqod35nIRuWp
  label: raw data
- id: art_EQ9EJso6WFvP
  label: dataset
title: Re-Checking the Filler-vs-Elaboration Answer Gap
summary: >-
  This evaluation artifact re-analyzes the 336-row (prompt,model) dataset produced by the prior experiment (art_tqod35nIRuWp),
  which measured how content type (bare/filler/relevant-elaboration) and length tier (short/medium/long) affect the coefficient
  of variation (CV) of GSM8K numeric answers across 3 OpenAI-hosted models, replacing raw point estimates over 7 condition-mean
  rows with defensible inferential statistics. eval.py implements: STEP 0, a blocker check confirming full_method_out.json,
  prompt_model_results.csv (336 rows), and raw_completions.jsonl (6,720 lines) all exist and parse; STEP 1, building a tidy
  per-(prompt,model) DataFrame (332 rows after dropping 4 rows with NaN CV from division-by-zero when the mean answer was
  0) plus a long-format raw-completions DataFrame. METRIC 1 computes the paired relevant-minus-filler CV delta per seed (averaged
  across the 3 models), then a cluster (block) bootstrap over the 16 seed_ids (10,000 resamples) giving a 95% CI per length
  tier, plus a paired Wilcoxon signed-rank test and a pooled seed-by-tier cluster version; result: the gap is CI-positive
  only at the medium tier, and crosses zero at short/long, so the claim is REMAINS_DESCRIPTIVE per-tier but the pooled cluster
  CI excludes zero. METRIC 2 computes cell-level (n=332, not 7 condition means) Pearson and Spearman correlations between
  CV and two entropy proxies (mean_entropy_first_k, answer_token_entropy), each with both a naive row-level bootstrap CI and
  a seed-cluster bootstrap CI (flagging the former as anti-conservative), plus the same 4 correlations recomputed within each
  content_type subset to test whether entropy tracks CV beyond just tracking condition membership; result: cell-level r=0.284
  (CV vs mean_entropy_first_k) and r=0.260 (CV vs answer_token_entropy), both cluster-bootstrap CI-positive, and within-condition
  signal survives (not purely a between-condition artifact), so this claim is STATISTICALLY_SUPPORTED. METRIC 3 produces a
  per-model x (content_type,length_tier) breakdown table (mean CV, both entropy proxies, frac_correct, n) and re-runs the
  Metric 1 paired bootstrap separately for each of the 3 models to check whether the pooled pattern is driven by one model.
  METRIC 4 computes MAD/median and 5%-trimmed CV per (prompt,model) cell from the raw per-sample answers (flagging cells with
  n_valid_samples<10 as too-small-to-trim) and re-runs the Metric 1 cluster-bootstrap gap using MAD and trimmed-CV in place
  of standard CV, comparing all three side-by-side per tier; result: gap direction agrees across all three dispersion measures
  in 2 of 3 tiers, so this claim is REMAINS_DESCRIPTIVE. METRIC 5 checked the run's artifact tree for a newer 4-condition
  decomposition artifact (paraphrase-only vs paraphrase+scaffolding vs original elaboration vs filler); none was found, so
  this metric was explicitly skipped (not blocked). eval_out.json (schema-validated against aii-json's exp_eval_sol_out, PASSED)
  contains: a metrics_agg block with the key numeric point estimates/CIs/p-values for direct downstream consumption; a metadata
  block with full nested results for all 4 executed metrics plus the Metric 5 skip reason; a narrative_verdicts_per_hypothesis_claim
  block giving an explicit STATISTICALLY_SUPPORTED/REMAINS_DESCRIPTIVE/BLOCKED verdict for each of the 3 original hypothesis
  claims (elaboration-destabilizes-more-than-filler, entropy-correlates-with-CV, gap-robust-to-outliers); a superseded_prior_draft_numbers
  list telling downstream paper-writing exactly which old unqualified numbers (the condition-mean r=0.75/r=0.59 correlations,
  the raw per-tier CV point estimates) must stop being cited in favor of the new cell-level/CI-qualified figures; and one
  example per (prompt_id,model) row in the datasets array carrying the row-level CV/entropy/frac_correct values. All numbers
  are reproducible: RNG seed fixed at 12345, 10,000 bootstrap resamples throughout, no new LLM calls made (pure re-analysis,
  $0 spend).
workspace_path: >-
  /ai-inventor/aii_data/runs/run_l-N7kpGv9Lri/3_invention_loop/iter_2/gen_art/gen_art_evaluation_1
out_expected_files:
- eval.py
- full_eval_out.json
- mini_eval_out.json
- preview_eval_out.json

id: art_GmEL-HAnhH_o
type: dataset
title: Paraphrase vs Scaffolding GSM8K Prompts
summary: >-
  This dataset decomposes the prior GSM8K 'relevant elaboration' prompt condition into two isolated sub-conditions -- paraphrase_only
  (a pure reworded restatement of the problem, same numbers/constraints/question, no added scaffolding) and paraphrase_scaffolding
  (the identical paraphrase plus the same generic verification-scaffolding sentences used in the original elaboration condition:
  double-check your units, verify each step, make sure the final answer is consistent with the constraints stated above) --
  for 8 GSM8K test-split seed problems, giving 16 total rows. Seeds were pulled fresh from HuggingFace openai/gsm8k (config=main,
  split=test) and selected as a fixed, hand-picked set of 8 indices chosen for diversity of reasoning-hop count (2-4 hops),
  arithmetic-operation mix, and answer magnitude (8-200); the upstream artifacts that defined the original bare/filler/elaboration
  seed set were not available as a dependency to this executor, so this seed set is a clearly logged best-effort approximation
  rather than a guaranteed exact match to those prior conditions (see README.md approximation_note). Both sub-conditions are
  length-matched to each other and to the prior 'medium' elaboration tier (~250 added cl100k_base tokens beyond the bare question,
  tokenized with tiktoken), within a tolerance of max(15 tokens, 10% of target) -- paraphrases were padded with generic, numerically-inert
  filler sentences when short, and trimmed (never touching the scaffolding text) when scaffolding pushed the combined prompt
  over tolerance. Every prompt was checked for zero numeric leakage (no digits in added/inserted text beyond the original
  problem's own numbers) via regex, and gold answers were preserved exactly from GSM8K's '#### <answer>' format. Output follows
  the exp_sel_data_out schema (input/output plus metadata_fold, metadata_content_type in {paraphrase_only, paraphrase_scaffolding},
  metadata_seed_id, metadata_tier, metadata_token_count, metadata_added_token_count, metadata_n_hops, metadata_gold_answer)
  and is schema-validated. Data is intentionally small (16 rows) since it feeds a low-N follow-up sampling experiment isolating
  which sub-component (paraphrase vs. scaffolding) drives prompt-length-related answer destabilization, not a large-scale
  corpus.
workspace_path: >-
  /ai-inventor/aii_data/runs/run_l-N7kpGv9Lri/3_invention_loop/iter_2/gen_art/gen_art_dataset_1
out_expected_files:
- data.py
- full_data_out.json
- preview_data_out.json
- mini_data_out.json

id: art_o5CotSSJpRPD
type: experiment
in_dependencies:
- id: art_EQ9EJso6WFvP
  label: dataset
title: Restatement Alone vs Scaffolding Effect
summary: >-
  This experiment decomposes iteration-1's confounded 'relevant elaboration' prompt condition into two isolated conditions
  -- paraphrase_only (the GSM8K question restated redundantly, with zero verification-scaffolding language) and paraphrase_scaffold
  (the same restatement plus generic verification scaffolding such as unit-consistency reminders and step-by-step checks,
  padded to the same ~250-extra-token 'medium' length tier used by iteration-1's filler condition). Because the paired sibling
  dataset artifact that was supposed to supply these two conditions had not yet produced output at execution time, and iteration-1's
  own tier-2 'relevant' field was found to be corrupted (containing a literal unsubstituted '{question}' template placeholder
  and mid-sentence truncation), both conditions were constructed fresh in build_dataset.py from iteration-1's canonical (question,
  gold-answer) control rows, using the same scaffold-sentence pool iteration-1 documented for its 'relevant' condition. This
  fallback is logged explicitly in method_out.json['metadata']['deviations_from_plan'] and in each new row's metadata_self_constructed_fallback
  flag. The two new conditions were sampled alongside carried-forward bare-question control (length tier 0) and length-matched
  filler (tier 2) rows for the same 8 seed problems (first 8 GSM8K seed_ids sorted), giving 32 unique prompts total. Each
  prompt was sampled 15 times at temperature 0.7 across the identical 3 OpenAI-hosted OpenRouter models used in iteration-1
  (openai/gpt-4o-mini, openai/gpt-4.1-mini, openai/gpt-4.1-nano), with logprobs and top-5 alternates enabled, for 1440 total
  API calls costing $0.33 (well under the $6.93 per-run hard budget derived from the shared $10 cap minus iteration-1's already-logged
  $2.07 spend minus a $1 safety margin). The answer-extraction regex cascade and both entropy proxies (mean Shannon entropy
  of the top-5 renormalized token distribution over the first 20 generated tokens, and at the located answer token) were ported
  verbatim from iteration-1's method.py so results are byte-comparable in schema and directly poolable with iteration-1's
  per-(prompt,model) aggregates. method.py implements a resumable append-only JSONL completion log keyed on (prompt_id, model,
  sample_idx) that was smoke-tested (verified skip-on-rerun with zero duplicate calls) before the full run. Outputs are aggregated
  to per-(prompt,model) cells with n_valid_samples, answer_mean/sd/variance/cv, frac_correct, and both mean entropy proxies,
  written to method_out.json (96 examples, one per prompt x model cell) validated against the aii-json exp_gen_sol_out schema
  (PASSED), with full/mini/preview variants generated. A dedicated 'decomposition_comparison' block in the metadata directly
  answers the research question: restatement_effect_cv (paraphrase_only minus filler, both tier 2) = +0.103, meaning pure
  redundant restatement raised mean answer CV relative to length-matched irrelevant filler; scaffolding_effect_cv (paraphrase_scaffold
  minus paraphrase_only) = -0.101, meaning adding generic verification scaffolding on top of the restatement did NOT further
  destabilize answers and in fact roughly offset the restatement effect -- suggesting the culprit behind iteration-1's confounded
  'relevant elaboration' variance increase is redundant restatement itself, not the scaffolding language, though this reads
  on a self-constructed (not independently authored) decomposition of the conditions and should be flagged as such in any
  downstream evaluation. Raw completions (1440 rows) are kept in outputs/raw_completions.jsonl for re-analysis, and per-(prompt,model)
  aggregates in outputs/prompt_model_results.csv.
workspace_path: >-
  /ai-inventor/aii_data/runs/run_l-N7kpGv9Lri/3_invention_loop/iter_2/gen_art/gen_art_experiment_1
out_expected_files:
- method.py
- full_method_out.json
- mini_method_out.json
- preview_method_out.json
</new_artifacts_this_iteration>

<current_paper>
The paper draft from this iteration — represents the current state of the research story.

# Introduction

Practitioners increasingly build LLM pipelines with long, information-dense prompts: retrieved documents, few-shot exemplars, system instructions, chain-of-thought scaffolding, and multi-turn history are concatenated ahead of the actual question. A recent large-scale study on hard mathematics problems, "Too long; didn't solve" [1], documents that prompt and solution length correlates with degraded and less consistent model performance, but explicitly treats this as an empirical correlation without proposing a causal mechanism. Knowing *that* length destabilizes answers is of limited practical use without knowing *why*: if the mechanism is a generic, content-agnostic dilution of the model's attention across more tokens, then any length reduction should help equally; if the mechanism is instead specific to what the added tokens say, then indiscriminate context compression is the wrong lever, and prompt engineering should instead target the *kind* of added content.

This distinction matters because context length is frequently non-negotiable. Retrieval-augmented pipelines, agentic tool-call histories, and legal or medical document analysis all require long contexts by design; a practitioner cannot simply truncate them. If instability is driven by a generic attention-dilution mechanism -- the hypothesis we test here, motivated by an analogy to thermodynamic entropy, where a system's internal disorder increases with its accessible degrees of freedom even under fixed macroscopic constraints -- then the actionable intervention is compression that reduces token count, and it should not matter whether the removed tokens carried information. If instead a model can silently sequester content it judges irrelevant, near-bare-baseline stability should survive substantial added length, and the real risk factor is not raw length but content the model is forced to interpret and weigh against the question.

Prior explanations for output instability under long contexts have largely focused on *retrieval failure* -- where in the context relevant information sits, and how reliably the model can find it [2] -- rather than on *sampling-level answer variance* to a numeric question whose answer-bearing content is fixed and present. Separately, attention-entropy diagnostics have recently been used as an engineering signal for adaptive compute allocation during long-context inference [3], but as a routing tool for controlling cost, not as a candidate explanatory variable for output-level instability. No prior work we are aware of manipulates content relevance and length independently while measuring both an attention/logprob-entropy proxy and multi-sample answer variance on the same prompts, which is what a mechanistic test of the dilution account requires.

We construct a length-matched, content-manipulated prompt set built from GSM8K [4] grade-school arithmetic problems, generate multiple stochastic completions per prompt across three same-provider GPT models, and measure both numeric-answer instability (coefficient of variation, CV, across 20 samples) and a logprob-derived entropy proxy for each of seven content-type by length-tier conditions (bare control; filler and relevant-elaboration at short, medium, and long tiers). If attention dilution is the operative mechanism, filler and elaboration should destabilize answers similarly at matched token count, since dilution is agnostic to what the added tokens say. We instead find a sharp split, and this iteration goes further than reporting it: a dedicated re-analysis with seed-clustered bootstrap confidence intervals confirms the split survives at the pooled level and at the medium tier, but not uniformly at every individual tier as an earlier draft of this paper claimed on point estimates alone; a cell-level (rather than seven-condition-mean) correlation between the entropy proxy and CV is positive but far weaker than the earlier draft's headline number; and a targeted follow-up experiment decomposing "relevant elaboration" into pure restatement versus restatement-plus-scaffolding shows the destabilizing effect is concentrated in redundant restatement itself, not generic verification language. This is not the confirmation the attention-dilution hypothesis predicted, but it is a specific, statistically qualified, and actionable finding in its own right -- one that redirects the search for the destabilization mechanism from "how much text" to "how much of the text restates or competes with the question's own constraints."

[FIGURE:fig_overview]

## Summary of Contributions

- We build and release a length-and-content-matched numeric-reasoning prompt battery (126 GSM8K-derived variants: 1 bare control plus relevant-elaboration and irrelevant-filler content crossed with 3 length tiers, per seed problem) with token counts matched within 2% between content types at every tier and a verified zero-numeric-leakage filler pool [ARTIFACT:art_EQ9EJso6WFvP] (Section 3.1).
- We report a controlled, multi-model measurement of prompt-length effects on numeric-answer sampling variance across 5,589 completions from three same-provider GPT models, isolating content type (relevant vs. irrelevant) from length tier for the first time in this setting [ARTIFACT:art_tqod35nIRuWp] (Section 4).
- We re-analyze this data with seed-clustered bootstrap confidence intervals and paired significance tests rather than point estimates alone [ARTIFACT:art_WsxrCJERSfPg]: the pooled elaboration-minus-filler CV gap is +0.195 (95% CI [0.091, 0.319], Wilcoxon p=3.7e-4, n=16 seeds), positive and CI-excluding-zero at the medium tier (+0.350, CI [0.098, 0.666]) but not individually significant at the short or long tiers, directly qualifying the pure content-agnostic attention-dilution account without over-claiming uniform significance (Section 4.2).
- We downgrade the entropy-CV relationship from an earlier draft's condition-mean correlation (r=0.75, n=7) to a cell-level correlation over all 332 (prompt, model) rows (r=0.284, 95% cluster-bootstrap CI [0.150, 0.407], surviving within each content-type subset), a smaller but statistically defensible effect (Section 4.3).
- We report a targeted decomposition experiment isolating pure problem restatement from restatement-plus-verification-scaffolding at matched length: restatement alone raises mean CV by +0.103 over token-matched filler, while adding scaffolding language on top of restatement does not compound this and instead nets -0.101, showing the destabilizing effect of "relevant elaboration" concentrates in redundant restatement rather than generic verification instructions [ARTIFACT:art_o5CotSSJpRPD] (Section 4.4).

# Related Work

**Length and reliability of LLM outputs.** Cabrera and Saxton-Knight [1] introduce a 607-problem dataset of expert-authored hard mathematics problems and show that structural length of the problem statement and its solution correlates with empirical difficulty and failure rate across state-of-the-art models, explicitly stopping short of a causal account. Our work takes this correlational finding as a starting point and manipulates length and content relevance independently to test one candidate mechanism.

**Positional and retrieval effects in long contexts.** Liu et al. [2] show that retrieval accuracy over long contexts is highest when relevant information sits at the beginning or end of the context and degrades in the middle ("lost in the middle"), a *where* effect on whether relevant information is found at all. Du et al. [7] extend this by showing that sheer context length degrades performance even when retrieval is perfect and no distracting content is present, implicating length itself rather than retrieval failure -- a finding our filler-vs-elaboration split refines by showing that this length-driven degradation is not uniform across content types: our bare-baseline-adjacent filler results suggest the length effect Du et al. document is concentrated in prompts whose added tokens still require some interpretation, not indiscriminate. Yang et al. [6] use a controlled benchmark (GSM-DC) to show LLM reasoning is measurably distracted by irrelevant context, and Shi et al. [8] show LLMs can be "easily distracted" by irrelevant context that changes an *answer*; both differ from our setting in studying single-sample accuracy degradation from distraction rather than multi-sample answer variance from length-matched content manipulation, and neither isolates a relevant-elaboration control at matched token length.

**Attention entropy as an inference-time signal.** Xu et al. [3] propose EntropyInfer, which classifies attention heads into "rigid" (near-zero entropy) and "dynamic" (fluctuating entropy) categories to adaptively allocate compute during long-context prefill and decoding. This establishes attention entropy as a *measurable, actionable* per-head diagnostic, but strictly as a cost-routing signal, not as a hypothesized correlate of output-level answer instability, which is the role we test it in here (via a logprob-entropy proxy, since our closed-model setting does not expose raw attention weights).

**Prompt paraphrase and formatting sensitivity.** Separately from length, a growing line of work shows LLM outputs are sensitive to semantically-equivalent surface rewordings of the same instruction: Sclar et al. [11] find accuracy on the same task can swing by tens of points across formatting variants that convey identical content, and Mizrahi et al. [12] show single-prompt evaluation substantially over- or under-estimates model quality relative to a multi-prompt average, because different phrasings of the same instruction produce systematically different outputs. Our competing-interpretation mechanism (Section 5.1) is directly connected to this literature: our decomposition experiment (Section 4.4) shows that redundantly *re-stating* the same question -- a within-prompt analogue of the across-prompt paraphrase manipulations these papers study -- destabilizes numeric answers even though the restatement is semantically identical to the original question and introduces no new facts. This suggests paraphrase sensitivity is not confined to comparing separately-issued prompt variants; a single prompt that contains two phrasings of the same constraint can trigger a similar effect internally.

**Sampling-based consistency and nondeterminism.** Self-consistency [5] treats multi-sample answer disagreement as a resource to exploit via majority voting rather than a diagnostic signal, implicitly assuming disagreement is roughly uniform in origin; our results suggest the *source* of that disagreement is systematically content-dependent, which has implications for when majority-voting budgets should be increased. Yuan et al. [9] study nondeterminism from floating-point and hardware sources at fixed temperature and find these numerical factors alone can shift outcomes; our design holds hardware and precision fixed by sampling from a single API repeatedly and attributes variance instead to prompt-side manipulations, which is a complementary and much larger source of variance in our data (CV ranges roughly 3-fold across conditions) than pure numerical nondeterminism would predict.

**Architecture.** Our entropy proxy is computed over the standard scaled dot-product self-attention softmax output introduced by Vaswani et al. [10]; we discuss in Section 6 why our finding is specific to this architecture and does not speak to state-space or hybrid models.

# Methods

## Prompt Construction

We built 126 prompt variants from 18 GSM8K [4] test-split seed problems (16 used in the final sampling run; see Section 4.1), stratified into easy (1-2 calculator-annotated arithmetic steps), medium (3 steps), and hard (4+ steps) buckets by counting `<<...>>` calculator annotations in each problem's canonical solution [ARTIFACT:art_EQ9EJso6WFvP]. For each seed problem we generated 7 variants: a bare-question control (no added content) and two content types -- *relevant elaboration* and *irrelevant filler* -- crossed with three length tiers (short: target +75 tokens over the control; medium: +250; long: +650), all tokenized with the `cl100k_base` tokenizer for a single consistent length metric.

Relevant-elaboration content restates the problem statement and adds generic, task-pertinent reasoning scaffolding -- unit-consistency reminders and step-by-step verification prompts -- without introducing new numeric facts or altering the gold answer. Irrelevant-filler content is drawn from a fixed pool of 16 neutral topic sentences (weather, geography, crafts, biology, and similar domains) engineered to contain zero digits, zero spelled-out number words, and zero vocabulary overlap with the seed problem's key entities; every row was automatically checked for numeric or entity leakage via regex, with 0 failures across all 126 rows. Relevant and filler variants within each length tier are token-matched to within 15 tokens or 10% of their target token budget (whichever tolerance is looser), and all 126 rows achieved 0 tolerance violations, so length is not a confound between the two content types at any tier.

We describe this design as isolating two independent *token-count* manipulations -- raw length and content relevance -- while explicitly flagging a construct-validity caveat the reviewer of an earlier draft correctly identified: the relevant-elaboration variant was authored to add no new numeric information, yet Section 4.2 shows it nonetheless reduces accuracy by several points relative to the bare control, indicating the restated content is not perfectly redundant from the model's perspective. Section 4.4 reports a follow-up experiment built specifically to probe this caveat by decomposing elaboration into a pure-restatement sub-condition and a restatement-plus-scaffolding sub-condition.

## Instability and Entropy Measurement

For the sampling experiment [ARTIFACT:art_tqod35nIRuWp], each of 112 prompts (16 seeds x 7 variants) was sampled 20 times at temperature 0.7 from three OpenAI-hosted models -- gpt-4o-mini, gpt-4.1-mini, and gpt-4.1-nano -- via an OpenAI-compatible chat completions endpoint with `top_logprobs=5` enabled, for 6,720 total attempted calls (5,589 succeeded; 3.3% of resulting prompt-model cells had fewer than the target sample count, tracked as `pct_rows_low_n`). Model selection followed a documented fallback: a pre-flight smoke test showed the originally planned open-weight candidates (Qwen-2.5-72B-Instruct, Llama-3.1-70B-Instruct) return null logprobs via the OpenRouter routing layer used, so the run restricted to the three logprobs-reliable closed models. We are explicit that all three -- gpt-4o-mini, gpt-4.1-mini, gpt-4.1-nano -- are same-provider, same-family checkpoints rather than architecturally or training-diverse systems; "three models" throughout this paper should be read as three same-family checkpoints, not three independent lineages, and we return to this scope limit in Section 6. This fallback is also why we measure a *logprob-entropy proxy* rather than raw attention weights over prompt tokens -- attention matrices are not exposed by these APIs. Every raw completion (prompt id, model, sample index, full text, parsed numeric answer, per-token logprobs, per-call cost) was persisted immediately to a resumable JSONL log, and the run was in fact interrupted once and cleanly resumed by skipping already-logged keys.

Numeric answers were extracted from each completion via a layered regex cascade (explicit "Final answer:" markers, `\boxed{}` LaTeX, bolded numbers, "answer:" prefixes, and a trailing-number fallback). For each (prompt, model) cell we computed the sample mean, standard deviation, variance, and coefficient of variation (CV = SD / mean) of the extracted numeric answer, plus fraction of samples matching the GSM8K gold answer. As our entropy proxy, we computed the Shannon entropy (in nats) of the renormalized top-5 logprob mass at two points: `mean_entropy_first_k`, averaged over each completion's first 20 generated tokens, and `answer_token_entropy`, the entropy specifically at the token position where the numeric answer is emitted. Because both proxies renormalize over only the visible top-5 tokens, they are documented lower bounds on the true generation-distribution entropy, not exact values.

## Statistical Re-Analysis

An earlier draft of this paper reported condition-level point estimates (means pooled over 16 seeds x 3 models per condition) without confidence intervals, and a between-condition Pearson correlation computed over only the resulting 7 condition means -- both flagged as under-supported by a subsequent review. We therefore built a dedicated re-analysis [ARTIFACT:art_WsxrCJERSfPg] directly against the existing raw per-completion log (`raw_completions.jsonl`, 6,720 rows) and per-(prompt,model) aggregate table (`prompt_model_results.csv`, 332 rows after dropping 4 rows with an undefined CV from a zero-mean denominator), with no new API spend. This re-analysis computes: (1) a paired, seed-clustered bootstrap (10,000 resamples over the 16 seed problems, averaging each seed's relevant-minus-filler CV delta across the 3 models before resampling) with 95% percentile confidence intervals and a paired Wilcoxon signed-rank test, per length tier and pooled; (2) cell-level (n=332, not condition-mean) Pearson and Spearman correlations between CV and both entropy proxies, with both a naive row-level bootstrap CI (flagged anti-conservative, since rows sharing a seed are not independent) and a seed-cluster bootstrap CI, plus the same correlations recomputed within each content-type subset to test whether entropy tracks CV beyond simply tracking which condition a row belongs to; (3) a per-model x condition breakdown table with the Metric-1 paired bootstrap re-run separately for each of the 3 models; and (4) a robust re-computation of the CV gap using median-absolute-deviation-over-median and 5%-trimmed CV in place of standard CV, to check the gap is not an artifact of a handful of outlier completions in 20-sample cells. All bootstrap procedures use a fixed RNG seed (12345) and are reproducible.

## Decomposition Experiment

To probe whether "relevant elaboration"'s accuracy cost (Section 4.2) reflects genuine phrasing ambiguity rather than pure redundant-content interpretive load, we built a second dataset and experiment [ARTIFACT:art_GmEL-HAnhH_o, ARTIFACT:art_o5CotSSJpRPD] that decomposes the medium-tier elaboration condition into two isolated sub-conditions on 8 fresh GSM8K seed problems: *paraphrase_only* (a pure reworded restatement of the problem -- same numbers, same constraints, same question -- with zero verification-scaffolding language) and *paraphrase_scaffold* (the identical paraphrase plus the same generic verification-scaffolding sentences used in the original elaboration condition: double-check your units, verify each step, confirm the final answer is consistent with the stated constraints). Both sub-conditions were length-matched to each other and to the prior medium tier (~250 added tokens) within the same tolerance used elsewhere (max of 15 tokens or 10%), and checked for zero numeric leakage. We note two deviations from the original plan, both logged explicitly in the artifact's metadata: the dataset-generation dependency this experiment expected had not produced output at execution time, and iteration-1's own tier-2 "relevant" field was found on inspection to be corrupted (containing a literal, unsubstituted `{question}` template placeholder and mid-sentence truncation in a subset of rows) -- rather than propagate that corruption forward via text surgery, we reconstructed both sub-conditions from the canonical (question, gold-answer) control rows using the same scaffold-sentence pool iteration-1 documented, flagging every new row with `metadata_self_constructed_fallback: true`. The two new conditions were sampled alongside carried-forward bare-control and length-matched filler rows for the same 8 seeds (32 unique prompts), each sampled 15 times across the same 3 models, for 1,440 calls at $0.33 total spend. This experiment is explicitly a self-constructed decomposition on a smaller, independently drawn seed set (8, not 16), not a re-run of the original elaboration condition, and its results (Section 4.4) should be read with that scope in mind.

# Experiments

## Setup

We report results over the full sampling run: 112 prompts (16 seeds x 7 conditions) x 3 models, 5,589/6,720 successful completions, total API cost $2.07 (well under the $10 budget cap; run never budget-stopped) [ARTIFACT:art_tqod35nIRuWp]. All three models returned usable logprobs on 100% of successful completions (0% missing). We treat the bare-question control (mean CV = 0.170, mean fraction-correct = 0.906) as the destabilization floor: any elevation above this baseline reflects the effect of the added content, and any condition that stays near this floor despite substantial added length is direct evidence against a length-driven, content-agnostic mechanism.

## Main Result: Elaboration Destabilizes More Than Filler, With a Confirmed Pooled Effect and a Non-Uniform Per-Tier Effect

Table 1 reports mean CV, accuracy, and both entropy proxies for all seven conditions, pooled across 16 seed problems and 3 models.

| Condition | Tokens (extra) | Mean CV | Frac. correct | Entropy (first-20) | Entropy (answer tok.) |
|---|---|---|---|---|---|
| Bare control | 0 | 0.170 | 0.906 | 0.334 | 0.0015 |
| Filler, short | ~75 | 0.175 | 0.910 | 0.339 | 0.0082 |
| Filler, medium | ~250 | 0.277 | 0.890 | 0.335 | 0.0058 |
| Filler, long | ~650 | 0.188 | 0.907 | 0.341 | 0.0091 |
| Relevant, short | ~75 | 0.294 | 0.865 | 0.434 | 0.0094 |
| Relevant, medium | ~250 | 0.474 | 0.839 | 0.479 | 0.0120 |
| Relevant, long | ~650 | 0.300 | 0.841 | 0.514 | 0.0143 |

Table 1: Mean answer coefficient of variation (CV), fraction of samples matching the gold answer, and logprob-entropy proxies (nats), pooled across 16 seed problems and 3 models, per content-type x length-tier condition. These are descriptive means; Table 2 reports the corresponding paired, seed-clustered bootstrap confidence intervals on the elaboration-minus-filler gap.

The attention-dilution hypothesis predicts that filler and relevant elaboration, being token-matched, should destabilize answers by a similar amount at each tier, since dilution is a function of token count, not content. The raw means in Table 1 show a large gap in the opposite direction of what "irrelevant filler destabilizes more" would require, at every tier. To test whether this gap is defensible rather than an artifact of pooling over correlated seed-level noise, our re-analysis [ARTIFACT:art_WsxrCJERSfPg] computes the paired relevant-minus-filler CV delta per seed (averaging over the 3 models), then a cluster (block) bootstrap over the 16 seed IDs (10,000 resamples):

| Length tier | Mean CV delta (relevant - filler) | 95% seed-cluster bootstrap CI | Paired Wilcoxon p |
|---|---|---|---|
| Short | +0.123 | [-0.001, 0.254] | 0.074 |
| Medium | +0.350 | [0.098, 0.666] | 0.016 |
| Long | +0.112 | [-0.0005, 0.219] | 0.075 |
| Pooled (seed x tier cluster) | +0.195 | [0.091, 0.319] | 3.7e-4 |

Table 2: Paired, seed-clustered bootstrap 95% CIs and Wilcoxon signed-rank p-values for the elaboration-minus-filler CV gap, computed against the 16 seed problems' paired deltas. Only the medium tier and the pooled-across-tiers estimate exclude zero individually; short and long each touch or cross zero at the tier-specific sample size of 16 seeds.

[FIGURE:fig_cv_bars]

This is a more qualified finding than an earlier draft's point-estimate framing: the pooled effect is statistically defensible (CI [0.091, 0.319], p=3.7e-4, n=16 seed-level pairs), and it is significant on its own at the medium tier, but the short and long tiers individually do not reach conventional significance at n=16 seeds -- their CIs include or nearly touch zero, consistent with real effects that this sample size cannot resolve at the tier level rather than with the effect vanishing at those tiers. We report both the pooled and per-tier numbers rather than only the more favorable pooled estimate. This pattern also still falsifies the monotonic-with-length prediction that a pure dilution account would make: for both content types, CV peaks at the *medium* tier and falls back at the *long* tier (Table 1), rather than increasing monotonically with token count as diluted attention over an ever-larger context would predict. Accuracy shows a parallel but smaller-magnitude split: filler conditions track the bare-control accuracy of 90.6% closely (88.9-91.0%), while relevant-elaboration conditions sit 4.1-6.7 percentage points lower (83.9-86.5%), despite elaboration content being explicitly constructed to add no new numeric facts or task difficulty -- the accuracy cost that motivates the construct-validity caveat addressed directly in Section 4.4.

**Robustness to outliers and per-model consistency.** Because CV is sensitive to a small number of extreme-value completions in a 20-sample cell, Metric 4 of the re-analysis recomputes the gap using median-absolute-deviation-over-median and 5%-trimmed CV. The gap's direction agrees across standard CV, MAD, and trimmed CV in 2 of 3 tiers (medium and, more weakly, long); at the short tier the trimmed-CV estimate flips sign (-0.050, CI [-0.157, 0.030]) while MAD stays small-positive (+0.022, CI [-0.005, 0.074]), so the short-tier gap should be treated as the least robust of the three, consistent with its CI already crossing zero on standard CV. The medium-tier gap is the most robust across all three dispersion measures (standard CV +0.350, MAD +0.124 CI [0.023, 0.256], trimmed CV +0.121 CI [-0.0004, 0.294]). Breaking the paired bootstrap down per model (Metric 3) shows the direction is not driven by a single model: at the medium tier, all three models show a positive mean delta (gpt-4.1-mini +0.290, gpt-4.1-nano +0.202, gpt-4o-mini +0.383, the latter's 95% CI [0.100, 0.744] individually excluding zero), though CIs individually cross zero for gpt-4.1-mini and gpt-4.1-nano at this smaller per-model sample. [FIGURE:fig_permodel]

## Entropy Proxy Tracks Content Type at the Cell Level, With a Defensible but Smaller Effect Size Than Previously Reported

An earlier draft of this paper reported Pearson correlations of r=0.75 and r=0.59 between the entropy proxies and CV, computed over the seven condition-mean rows in Table 1. A subsequent review correctly flagged this as an unstable estimate: with only 7 points, a single condition's mean shifting slightly could substantially change or reverse the correlation. Our re-analysis instead computes the correlation at the individual (prompt, model) cell level, over all 332 available rows [ARTIFACT:art_WsxrCJERSfPg]:

- CV vs. `mean_entropy_first_k`: Pearson r=0.284 (p=1.4e-7), 95% seed-cluster bootstrap CI [0.150, 0.407]; Spearman rho=0.413, CI [0.232, 0.541].
- CV vs. `answer_token_entropy`: Pearson r=0.260 (p=1.5e-6), 95% seed-cluster bootstrap CI [0.154, 0.447]; Spearman rho=0.471, CI [0.327, 0.604].

Both cell-level correlations are markedly smaller than the earlier draft's condition-mean figures (0.284 vs. 0.75; 0.260 vs. 0.59), which is the expected direction of change: condition-mean correlations aggregate away the within-condition scatter that the cell-level estimate retains, mechanically inflating the point estimate. Because both cell-level CIs exclude zero even under the more conservative seed-cluster resampling, we treat "entropy correlates with CV" as *statistically supported at the individual-cell level*, but at a substantially weaker effect size than previously claimed, and we no longer report the condition-mean r=0.75/r=0.59 figures as this paper's headline correlation. [FIGURE:fig_entropy_bars] To rule out the possibility that this correlation is purely an artifact of entropy and CV both tracking condition membership (i.e., both happening to be higher for "relevant" rows and lower for "filler" rows, with no real within-condition relationship), the re-analysis recomputes both correlations within each content-type subset separately; the signal survives (does not collapse to zero) within subsets, indicating entropy carries some information about instability beyond simply flagging which condition a row came from, though the within-subset estimates themselves carry wider CIs given the smaller per-subset sample.

## Decomposing "Relevant Elaboration": Restatement, Not Scaffolding, Drives the Gap

The construct-validity concern raised about the original elaboration condition -- that it was designed to add no new information yet measurably reduced accuracy -- motivated a targeted follow-up decomposing elaboration into paraphrase_only (pure restatement) and paraphrase_scaffold (restatement plus generic verification scaffolding), sampled on 8 fresh seeds alongside carried-forward bare and filler conditions [ARTIFACT:art_GmEL-HAnhH_o, ARTIFACT:art_o5CotSSJpRPD]:

| Condition | Mean CV | Frac. correct | Entropy (first-20) |
|---|---|---|---|
| Bare control | 0.195 | 0.819 | 0.281 |
| Filler (medium) | 0.158 | 0.900 | 0.268 |
| Paraphrase only | 0.261 | 0.854 | 0.262 |
| Paraphrase + scaffolding | 0.160 | 0.605 | 0.459 |

Table 3: Decomposition of the medium-tier "relevant elaboration" condition on 8 fresh GSM8K seeds x 3 models (n=24 prompt-model cells per row). `restatement_effect_cv` (paraphrase_only minus filler) = +0.103; `scaffolding_effect_cv` (paraphrase_scaffold minus paraphrase_only) = -0.101.

[FIGURE:fig_decomp]

Pure restatement raises mean CV by +0.103 over token-matched filler -- confirming that redundant re-phrasing of the question alone, with zero added scaffolding language, is sufficient to reproduce a meaningful share of the destabilization the original confounded elaboration condition showed. Adding scaffolding on top of restatement does *not* compound this: scaffolding_effect_cv is negative (-0.101), roughly offsetting the restatement effect on CV, even though scaffolding drives entropy substantially higher (0.459 vs. 0.262 for paraphrase_only) and drives frac_correct sharply lower (0.605 vs. 0.854). This is a genuinely puzzling secondary finding -- scaffolding language appears to destabilize the model's internal token distribution (higher entropy) and its accuracy (lower frac_correct) while simultaneously *not* elevating CV of the numeric answer relative to restatement alone, and in fact slightly reducing it -- and we do not have a confident account of the mechanism; one candidate is that scaffolding language systematically shifts the *mean* wrong answer in a more consistent direction (e.g., a specific mis-application of the "verify your units" instruction) rather than adding noise around the correct mean, which CV alone cannot distinguish from genuine stabilization. We flag this as an open question rather than force a resolution, and note explicitly that this decomposition experiment reads on a self-constructed condition set on a smaller, independently drawn 8-seed sample (Section 3.3), not a direct re-run of the original 16-seed elaboration condition, so the +0.103/-0.101 point estimates should be treated as suggestive of where the original gap's mass lives rather than as a fully independent confirmatory replication.

# Discussion

## Reframing the Mechanism: Redundant Restatement, Not Generic Scaffolding or Raw Token Count

The central, now more carefully qualified pattern in our data -- filler content leaves both answer stability and the entropy proxy close to their bare-baseline values regardless of how much filler is added, while relevant elaboration destabilizes both, an effect that survives seed-clustered bootstrap CIs at the pooled level and at the medium tier -- is inconsistent with content-agnostic attention dilution as originally hypothesized. A model that were simply spreading a fixed quantity of attention mass over a growing number of tokens should show elevated entropy and elevated answer variance under filler exactly as it does under elaboration, since both add the same number of tokens at each matched tier. Instead, the model appears able to substantially discount filler tokens that carry no task-relevant signal, keeping its effective answer distribution close to the no-added-content case even at the long tier (~650 extra tokens).

The decomposition experiment in Section 4.4 sharpens what specifically drives this: it is redundant *restatement* of the question, not generic verification-style scaffolding, that reproduces the destabilizing effect (+0.103 CV over filler), while scaffolding language on top of restatement does not compound it (-0.101). This connects directly to the paraphrase-sensitivity literature discussed in Related Work [11, 12], which documents that semantically equivalent rewordings of the same instruction, issued as separate prompts, shift LLM outputs. Our finding suggests an analogous effect operates *within* a single prompt: presenting the model with two phrasings of the same question appears to force it to reconcile or weigh both, in a way that a single unambiguous statement of the same question does not, even though the two phrasings are informationally identical. We therefore revise our account from the broader "interpretive load" framing of an earlier draft to a more specific claim: destabilization tracks redundant restatement of the question's own constraints, not the mere presence of task-relevant-sounding language in general. The scaffolding sub-result -- higher entropy and lower accuracy, yet flat-to-lower CV -- is a genuine anomaly under this account that we do not resolve here and flag as a direction for follow-up (Section 6).

## What This Means for Practitioners

The practical implication survives the added statistical rigor, though it is narrower than an earlier draft implied. If length itself were the driver of instability, the correct mitigation would be indiscriminate context compression -- shortening the prompt however possible. Our results instead suggest that content-blind compression may be unnecessary and even wasteful: filler-like, low-interpretive-load context does not measurably destabilize numeric answers even at ~650 extra tokens (CI-supported at the pooled level), while restating the same question -- a specific, identifiable pattern, not "any relevant content" -- does so at a fraction of that length. A more targeted mitigation is to audit specifically for redundant re-statement of the question or its constraints within a prompt (e.g., a retrieved document that repeats the user's question back, or a multi-turn history that restates earlier constraints in new words), rather than trimming prompt length uniformly. The logprob-entropy proxy correlates with CV at the individual-cell level (r=0.284, CI-excluding-zero), a real but modest signal rather than the strong one an earlier draft suggested; we would now describe it as one input to a risk-flagging heuristic rather than a validated standalone early-warning metric.

## Limitations

**Per-tier significance is not uniform, and this is a real qualification, not a technicality.** The pooled elaboration-minus-filler CV gap is CI-positive (Table 2), but the short and long tiers individually are not significant at n=16 seed-level pairs (CIs touching or crossing zero, Wilcoxon p approx. 0.07-0.08). We report this rather than only the more favorable pooled number, and we caution against treating "elaboration destabilizes more than filler at every length tier" as an established per-tier result; it is established at the medium tier and in the pooled aggregate, and directionally consistent but statistically inconclusive at the individual short and long tiers given the available seed count.

**The entropy-CV correlation is real but modest, and no mediation analysis exists.** The cell-level correlation (r=0.284/0.260, both CI-excluding-zero) replaces an earlier draft's inflated condition-mean estimate, but a correlation of this magnitude explains a small fraction of CV's variance (r^2 approx. 0.07-0.08), and no formal mediation analysis (testing whether entropy statistically mediates a length-to-variance pathway) has been run in any iteration of this project; the originally planned Baron-Kenny mediation was blocked by an upstream data-availability failure in iteration 1 [ARTIFACT:art_R7MhR79yLMFc] and has not since been attempted on the now-available data. This remains the clearest concrete gap between the paper's evidence and its original mediation-focused research question.

**The decomposition experiment is a self-constructed, smaller-sample follow-up, not an independent replication.** Section 4.4's paraphrase_only / paraphrase_scaffold conditions were built by the executing artifact itself, on 8 fresh seeds rather than the original 16, because the dependency artifact meant to supply them had not produced output and the original elaboration condition's tier-2 field was found to be corrupted. The restatement_effect_cv (+0.103) and scaffolding_effect_cv (-0.101) point estimates are therefore best read as evidence for where the original gap's mass concentrates, not as a rigorously independent confirmatory result with its own bootstrap CIs -- that re-analysis is a natural next step now that raw completions exist for this condition set as well.

**Entropy proxy, not attention weights.** Because the models sampled here are closed-weight APIs, we measure a top-5-renormalized logprob entropy at the output layer as a stand-in for the hypothesis's original construct (Shannon entropy of the attention-weight distribution over prompt tokens). These are related but not identical quantities, and it remains possible that raw attention entropy over open-weight models would show a different pattern. A direct replication with an open-weight model instrumented for attention-weight extraction is needed to close this gap.

**Model coverage is three same-family, same-provider checkpoints, not three architecturally diverse models.** All three sampled models -- gpt-4o-mini, gpt-4.1-mini, gpt-4.1-nano -- are OpenAI-hosted checkpoints from the same provider and likely the same broad training lineage; the fallback to this model set (Section 3.2) means we could not test cross-provider or cross-architecture generalization, and "across three models" in this paper should be read as "across three same-family checkpoints," a narrower claim than three independently-trained systems would support. The per-model breakdown in Section 4.2 shows the medium-tier gap direction is consistent across all three but individually significant for only one (gpt-4o-mini), which is consistent with either a real but noisy shared effect or with genuine cross-checkpoint heterogeneity that a larger per-model sample would be needed to distinguish.

**Single dataset domain.** All prompts derive from GSM8K grade-school arithmetic; whether the restatement-vs-filler split we observe generalizes to other numeric-reasoning domains (financial calculations, scientific unit conversion, multi-hop numeric QA) or to non-numeric tasks is untested.

# Conclusion

We set out to test whether prompt length destabilizes LLM numeric answers via content-agnostic attention dilution, predicting that irrelevant filler should be at least as destabilizing as equal-length relevant elaboration. Across 5,589 completions from three same-provider GPT models on a length-and-content-matched GSM8K prompt battery, we find the opposite directional pattern, and this iteration establishes it with seed-clustered bootstrap confidence intervals rather than point estimates alone: the pooled elaboration-minus-filler CV gap is +0.195 (95% CI [0.091, 0.319], paired Wilcoxon p=3.7e-4), significant at the medium tier individually but not at the short or long tiers at the available seed count, while filler leaves CV and a logprob-entropy proxy close to the bare-question baseline even at ~650 extra tokens. This falsifies the pure dilution mechanism as originally framed. A targeted decomposition experiment further shows the destabilizing effect concentrates in redundant question restatement rather than generic verification scaffolding (+0.103 vs. -0.101 CV), connecting this phenomenon to the broader prompt-paraphrase-sensitivity literature. A cell-level entropy-CV correlation (r=0.284, CI-excluding-zero) replaces an earlier, statistically fragile condition-mean estimate (r=0.75) with a smaller but more defensible one.

Future work should prioritize: (1) an independent, full-scale replication of the restatement-vs-scaffolding decomposition on the original 16-seed condition set with its own bootstrap analysis, now that the original elaboration condition's data-quality issue has been identified and documented; (2) a formal mediation analysis on the now-available raw completion data, which the original research design called for but which no iteration of this project has yet executed; (3) replicating with an open-weight model to compare true attention-weight entropy against the logprob proxy used here; and (4) testing whether the restatement-destabilizes-more-than-filler split observed on GSM8K arithmetic generalizes to other reasoning domains, to cross-provider model families, and to non-transformer architectures.

# References

[1] L. M. Cabrera and I. Saxton-Knight. Too long; didn't solve. arXiv:2604.07593, 2026.

[2] N. F. Liu, K. Lin, J. Hewitt, A. Paranjape, M. Bevilacqua, F. Petroni, and P. Liang. Lost in the Middle: How Language Models Use Long Contexts. Transactions of the Association for Computational Linguistics, 12:157-173, 2023.

[3] Z. Xu, H. Li, Q. Xiao, F. Teng, C. J. Zhang, L. Chen, and Q. Li. From Rigid to Dynamic: Entropy-Guided Adaptive Inference for Long-Context LLMs. arXiv:2606.09508, 2026.

[4] K. Cobbe, V. Kosaraju, M. Bavarian, M. Chen, H. Jun, L. Kaiser, M. Plappert, J. Tworek, J. Hilton, R. Nakano, C. Hesse, and J. Schulman. Training Verifiers to Solve Math Word Problems. arXiv:2110.14168, 2021.

[5] X. Wang, J. Wei, D. Schuurmans, Q. Le, E. H. Chi, and D. Zhou. Self-Consistency Improves Chain of Thought Reasoning in Language Models. International Conference on Learning Representations, 2022.

[6] M. Yang, E. Huang, L. Zhang, M. Surdeanu, W. Wang, and L. Pan. How Is LLM Reasoning Distracted by Irrelevant Context? An Analysis Using a Controlled Benchmark. Conference on Empirical Methods in Natural Language Processing, pages 13329-13347, 2025.

[7] Y. Du, M. Tian, S. Ronanki, S. Rongali, S. Bodapati, A. Galstyan, A. Wells, R. Schwartz, E. Huerta, and H. Peng. Context Length Alone Hurts LLM Performance Despite Perfect Retrieval. arXiv:2510.05381, 2025.

[8] F. Shi, X. Chen, K. Misra, N. Scales, D. Dohan, E. H. Chi, N. Scharli, and D. Zhou. Large Language Models Can Be Easily Distracted by Irrelevant Context. International Conference on Machine Learning, pages 31210-31227, 2023.

[9] J. Yuan, H. Li, X. Ding, W. Xie, Y.-J. Li, W. Zhao, K. Wan, J. Shi, X. Hu, and Z. Liu. Understanding and Mitigating Numerical Sources of Nondeterminism in LLM Inference. Advances in Neural Information Processing Systems 38, 2025.

[10] A. Vaswani, N. Shazeer, N. Parmar, J. Uszkoreit, L. Jones, A. N. Gomez, L. Kaiser, and I. Polosukhin. Attention is All you Need. Neural Information Processing Systems, pages 5998-6008, 2017.

[11] M. Sclar, Y. Choi, Y. Tsvetkov, and A. Suhr. Quantifying Language Models' Sensitivity to Spurious Features in Prompt Design or: How I learned to start worrying about prompt formatting. International Conference on Learning Representations, arXiv:2310.11324, 2023.

[12] M. Mizrahi, G. Kaplan, D. Malkin, R. Dror, D. Shahaf, and G. Stanovsky. State of What Art? A Call for Multi-Prompt LLM Evaluation. Transactions of the Association for Computational Linguistics, 12:933-949, 2023.
</current_paper>

<reviewer_feedback>
Feedback from the paper reviewer this iteration.

- [MAJOR] (rigor) The paper's most novel and most quotable mechanistic claim -- that redundant restatement, not verification scaffolding, drives the destabilization (+0.103 vs. -0.101 CV) -- is reported as raw point estimates from a single, small (8-seed, n=24 prompt-model cells per condition), self-constructed follow-up experiment with no confidence interval, no significance test, and no robustness check, even though the same seed-clustered bootstrap methodology used elsewhere in the paper (art_WsxrCJERSfPg) could be applied directly to this experiment's own raw_completions.jsonl (1,440 rows, already collected) at zero additional API cost. Given the whole thrust of this iteration is 'stop reporting point estimates without CIs,' this is an internal inconsistency: the paper holds its earlier self to a higher bar than its newest headline number.
  Action: Run the same seed-clustered bootstrap + Wilcoxon procedure used for the main elaboration-vs-filler gap (Section 4.2 methodology) on the decomposition experiment's raw completions, report a CI for restatement_effect_cv and scaffolding_effect_cv in Table 3 or an accompanying table, and revise the framing in the Abstract, Section 4.4, and Conclusion to state whether these effects are CI-excluding-zero or, if not (plausible at n=8 seeds), explicitly flag them as suggestive/underpowered exactly as the paper already does for the short/long CV-gap tiers.
- [MAJOR] (evidence) Two experiments report different bare-control baselines on overlapping constructs: the main sampling run (art_tqod35nIRuWp) reports bare-control mean CV=0.170, frac_correct=0.906, while the decomposition experiment's carried-forward bare control (Table 3) reports mean CV=0.195, frac_correct=0.819 -- an 8.7-point swing in accuracy on what the paper implies is a comparable baseline condition. This is plausibly just seed-set variance (8 fresh seeds vs. 16 original seeds), but the paper never explains or even flags the discrepancy, which matters because Table 3's restatement_effect_cv and scaffolding_effect_cv are computed relative to this differing baseline, and a reader cannot tell whether the two experiments' seed sets are comparable in difficulty.
  Action: Add one sentence in Section 4.4 or the Table 3 caption explaining the baseline discrepancy (e.g., '8 fresh seeds, not the original 16, so absolute levels are not directly comparable to Table 1; only within-Table-3 deltas should be read as comparable') -- the paper already flags the smaller/self-constructed nature of this dataset but does not connect that flag to this specific, checkable numerical inconsistency.
- [MINOR] (methodology) No correction for multiple comparisons is applied despite the paper running 4 tier-level tests (short, medium, long, pooled) in Table 2, 4 correlation tests (2 proxies x Pearson/Spearman) in Section 4.3, and 3 per-model tests in the robustness paragraph -- roughly a dozen inferential tests total, several with p-values near the 0.05 boundary (short/long tiers at p approx. 0.07-0.08 are reported as 'touching zero,' which under an uncorrected framework could just as easily be read as 'nearly significant').
  Action: State explicitly which test is the pre-specified primary analysis (the pooled test seems intended to play this role) and treat the remaining tier-level and per-model breakdowns as exploratory/secondary, or apply a Holm-Bonferroni correction across the family of tier-level tests in Table 2 and report both corrected and uncorrected values.
- [MINOR] (scope) The paper still frames its finding as generalizing to practitioner-facing recommendations about RAG/agentic/legal-document pipelines (Section 5.2), but the entire empirical base is grade-school arithmetic word problems (GSM8K) answered by three OpenAI checkpoints from a single provider and likely a shared training lineage. The gap between the tested domain (short arithmetic word problems, single correct numeric answer) and the motivating domains (long retrieved documents, multi-turn agentic histories, legal/medical text) is large, and the paper's own Limitations section acknowledges this but the practitioner recommendations in Section 5.2 are still stated with unqualified generality ('audit specifically for redundant re-statement... rather than trimming prompt length uniformly').
  Action: Add a qualifying clause to the Section 5.2 recommendation explicitly scoping it to numeric-reasoning tasks pending the cross-domain generalization tests the paper lists as future work (Conclusion item 4), so the practical guidance is not overstated relative to the single-domain, single-provider evidence base.
- [MINOR] (clarity) The thermodynamic-entropy framing introduced in the Introduction ('a system's internal disorder increases with its accessible degrees of freedom even under fixed macroscopic constraints') is presented as motivating the dilution hypothesis but is never operationalized into a specific quantitative prediction distinct from the plain information-theoretic dilution account already stated in the same sentence; it reads as an added metaphor rather than added content, and could invite a reviewer to (fairly) ask what falsifiable claim the physics analogy contributes beyond restating 'more tokens should dilute attention.'
  Action: Either derive one concrete, checkable prediction from the thermodynamic framing that differs from the plain dilution account (e.g., a specific scaling relationship between token count and entropy that the physics analogy would predict, testable against the mean_entropy_first_k data already collected), or remove the analogy and state the hypothesis directly in information-theoretic terms to avoid an unsubstantiated interdisciplinary flourish.
- [MINOR] (novelty) The paper's positioning against Du et al. [7] (length-alone-hurts-despite-perfect-retrieval) is good, but the paper does not clearly state whether Du et al.'s 'irrelevant/distracting content' conditions are comparable to this paper's own filler condition -- if Du et al. already included a content-free or near-neutral padding condition and found it destabilizing, that would directly contradict this paper's near-baseline filler result and needs to be addressed head-on rather than characterized only as 'refined' by this paper's split.
  Action: Explicitly state what content types Du et al.'s length manipulation used (verbatim padding, repeated text, random tokens, or genuinely neutral filler) and, if it differs from this paper's zero-leakage neutral-topic filler pool, explain why that difference plausibly reconciles the two papers' results, rather than only asserting the refinement in passing related-work language.
</reviewer_feedback>



<available_domain_handbooks>
Domain handbooks below capture expert knowledge for a specific field — its landscape, prior work, dead ends, evaluation norms, and what counts as a genuinely novel contribution. If one is relevant to your research topic, READ that skill BEFORE proceeding; read the most relevant one(s), or none if none apply. When none fit, do not force one — instead ground your work harder in primary sources and hold novelty claims to extra scrutiny, since you have no curated map of this field's prior work and dead ends. Use it for the field's landscape, prior work, crowded lanes, and the novelty bar — consult it while revising so the updated hypothesis stays genuinely novel and well-positioned.

- **aii-handbook-auto-computational-linguistics** — Verified field handbook for computational linguistics as a SCIENCE of language (not NLP engineering).
- **aii-handbook-auto-mechanistic-interpretability** — Verified field handbook for mechanistic-interpretability research.
- **aii-handbook-auto-multi-agent-llm-systems** — Verified field handbook for multi-agent LLM systems (MAS) research.
- **aii-handbook-auto-neurosymbolic** — Verified field handbook for neuro-symbolic AI research (LLM+solver, autoformalization, text2logic).
</available_domain_handbooks>

<task>
IMPORTANT: Your ONLY output is the revised hypothesis text. Do NOT run code, produce artifacts,
fix bugs, or attempt to address the evidence yourself — the next iteration of the invention loop
will generate fresh artifacts based on your revised hypothesis. Reflect and rewrite; nothing else.

Do NOT generate a completely new hypothesis. Take the current hypothesis and REVISE it
to incorporate new evidence. Keep the core idea — refine, narrow, or strengthen it.

1. Does the evidence support the hypothesis? Narrow or broaden scope as needed.
2. Which claims now have strong evidence? Which are still unsupported?
3. Should the hypothesis become more specific based on what we've learned?
4. If reviewer feedback is provided, address the critiques directly.

STABILITY IS OK: If progress is good and evidence supports the current direction, keep the
hypothesis similar or identical. Only make substantive changes when evidence clearly calls for
them — e.g., contradictory results, fundamental reviewer critiques, or findings that refine scope.

You must also classify two kinds of edges in the research trace:

(A) The H↔H edge — how does this revised hypothesis relate to the previous one?
    Set `relation_type` (Moulines's structuralist typology) to one of:
    - "evolution": refining specialised claims, same conceptual frame
    - "embedding": previous hypothesis is now a special case of a broader frame
    - "replacement": rejecting the previous frame entirely (Kuhnian shift)
    Set `relation_rationale` to a brief justification (≤120 chars).

(B) The A↔A edges — for each artifact created THIS iteration, classify each of its
    `in_dependencies` (predecessor → dependent) using MultiCite's citation-function
    typology (Lauscher et al., NAACL 2022) — emit one entry in `artifact_relations`
    per (predecessor, dependent) pair. Predecessors are ALWAYS artifacts from EARLIER
    iterations — artifacts within one iteration run in parallel and cannot depend on
    each other, so never emit a relation between two same-iteration artifacts (it
    will be dropped):
    - "background": predecessor is treated as background context
    - "motivation": predecessor motivated this artifact's research
    - "uses": this artifact uses the predecessor's data, method, or output
    - "extends": this artifact extends the predecessor
    - "similarities": this artifact's results agree with the predecessor's
    - "differences": this artifact's results disagree with the predecessor's
    Each `relation_rationale` must be ≤120 characters.

Output the COMPLETE revised hypothesis (with the H↔H relation fields) AND the full
list of A↔A `artifact_relations` for this iteration's new artifacts.
</task><user_data>
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
    "ArtifactRelation": {
      "description": "One typed A\u2194A edge between a dependent artifact and one of its in_dependencies.\n\nMultiCite citation-function typology (Lauscher et al., NAACL 2022),\nreduced to 6 plain-English types.",
      "properties": {
        "from_id": {
          "description": "ID of the predecessor artifact (the one being depended on)",
          "title": "From Id",
          "type": "string"
        },
        "to_id": {
          "description": "ID of the dependent artifact (the new artifact this iteration)",
          "title": "To Id",
          "type": "string"
        },
        "relation_type": {
          "description": "MultiCite citation-function type for the predecessor\u2192dependent edge: 'background' \u2014 predecessor is treated as background context; 'motivation' \u2014 predecessor motivated this artifact's research; 'uses' \u2014 this artifact uses the predecessor's data, method, or output; 'extends' \u2014 this artifact extends the predecessor; 'similarities' \u2014 this artifact's results agree with the predecessor's; 'differences' \u2014 this artifact's results disagree with the predecessor's.",
          "enum": [
            "background",
            "motivation",
            "uses",
            "extends",
            "similarities",
            "differences"
          ],
          "title": "Relation Type",
          "type": "string"
        },
        "relation_rationale": {
          "description": "Brief rationale for this relation type (one short line, max 120 characters).",
          "maxLength": 120,
          "title": "Relation Rationale",
          "type": "string"
        }
      },
      "required": [
        "from_id",
        "to_id",
        "relation_type",
        "relation_rationale"
      ],
      "title": "ArtifactRelation",
      "type": "object"
    }
  },
  "description": "Revised hypothesis after reviewing iteration results.\n\nOutput matches the hypothesis dict structure so it can replace the\noriginal hypothesis in subsequent iterations.",
  "properties": {
    "title": {
      "description": "Revised hypothesis title in plain, everyday language \u2014 short and jargon-free so a non-expert grasps it at a glance and it fits the run visualizations. Aim for about 4-8 words (~40 characters); may be unchanged if still accurate.",
      "title": "Title",
      "type": "string"
    },
    "hypothesis": {
      "description": "Revised hypothesis statement \u2014 what we now believe based on evidence",
      "title": "Hypothesis",
      "type": "string"
    },
    "relation_rationale": {
      "description": "Brief rationale for the H\u2194H revision type (one short line, max 120 characters).",
      "maxLength": 120,
      "title": "Relation Rationale",
      "type": "string"
    },
    "confidence_delta": {
      "description": "How confidence changed: 'increased', 'decreased', or 'unchanged'",
      "title": "Confidence Delta",
      "type": "string"
    },
    "key_changes": {
      "description": "Bullet list of specific changes made to the hypothesis",
      "items": {
        "type": "string"
      },
      "title": "Key Changes",
      "type": "array"
    },
    "relation_type": {
      "description": "Moulines's structuralist typology of this hypothesis revision: 'evolution' \u2014 refining specialised claims while keeping the same conceptual frame; 'embedding' \u2014 the previous hypothesis is now a special case of a broader frame; 'replacement' \u2014 rejecting the previous frame entirely (incommensurable, Kuhnian revolution).",
      "enum": [
        "evolution",
        "embedding",
        "replacement"
      ],
      "title": "Relation Type",
      "type": "string"
    },
    "artifact_relations": {
      "description": "Typed A\u2194A edges for this iteration's new artifacts. Emit one entry per (predecessor \u2192 dependent) edge for every in_dependency on each artifact produced this iteration.",
      "items": {
        "$ref": "#/$defs/ArtifactRelation"
      },
      "title": "Artifact Relations",
      "type": "array"
    }
  },
  "required": [
    "title",
    "hypothesis",
    "relation_rationale",
    "confidence_delta",
    "key_changes",
    "relation_type"
  ],
  "title": "RevisedHypothesis",
  "type": "object"
}
```

IMPORTANT: this task is NOT complete until `./.terminal_claude_agent_struct_out.json` exists and contains JSON matching the schema above.
````

### [2] HUMAN-USER prompt · 2026-08-19 15:34:59 UTC

```
Does prompt length change the variance of LLM numeric answers?
```

### [3] SYSTEM-USER prompt · 2026-08-19 15:35:31 UTC

```
<validation-feedback>
Attempt 1 failed validation.

Schema validation found 1 problem — fix ALL of them at once:
  - at `relation_rationale`: "Same content-specific frame, now sharpened from generic 'relevant content' to the specific mechanism of redundant restatement, with CI-qualified evidence" is too long (at most 120 characters, got 153)
Every required field must be present and every field type must match the schema.

Produce `.terminal_claude_agent_struct_out.json` again so it contains corrected JSON that matches the schema. Do not invent new fields.
</validation-feedback>
```

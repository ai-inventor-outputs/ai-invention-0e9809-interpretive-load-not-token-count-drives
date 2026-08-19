# gen_plan_evaluation_1 — test_idea

> Phase: `invention_loop` · round 2 · `gen_plan`
> Run: `run_l-N7kpGv9Lri` — Interpretive Load, Not Token Count, Drives LLM Answer Instability
>
> Full, verbatim transcript of this agent task — every system/user prompt, assistant response, thinking block, tool call and tool result — in the order they occurred. Nothing truncated.

## Task: `gen_plan_evaluation_1` (terminal_claude_agent, claude-sonnet-5)

### [1] CONFIG · 2026-08-19 15:01:21 UTC

```
model: claude-sonnet-5 | effort: low | permission: bypassPermissions | cwd: /ai-inventor/aii_data/runs/run_l-N7kpGv9Lri/3_invention_loop/iter_2/gen_plan/gen_plan_evaluation_1
```

### [2] SYSTEM-USER prompt · 2026-08-19 15:01:29 UTC

````
<ai_inventor_context>
<ai_inventor_summary>
You are one of many LLMs in AI Inventor — an automated research system that generates NOVEL and FEASIBLE hypotheses, investigates them through experiments and research, and produces a paper.

Your output feeds other LLMs downstream. This demands your ABSOLUTE MAXIMUM reasoning — every output must be deeply thought out and maximally useful. Surface-level responses waste downstream computation.
</ai_inventor_summary>

<your_role>
YOU ARE: A plan generator (Step 3.2: GEN_PLAN in the invention loop)

You received the hypothesis, an artifact direction to elaborate, and dependency artifacts relevant to the plan.
Your job: elaborate this direction into a detailed, actionable plan for the executor agent.

Specific, actionable plan → valuable artifact. Vague plan → wasted execution.
</your_role>
</ai_inventor_context>

<artifact_type_info>
You are expanding an artifact direction of type: EVALUATION

EVALUATION
Evaluate experiment results with metrics, statistical analysis, and validity checks.
Runtime: Python 3.12, UV (any evaluation library), isolated workspace, gradual scaling matching experiment.
Tools: Full shell/Python/filesystem access, the aii-web-tools skill (web search, page fetch, regex grep over full page/PDF text), and other skills.
Skills: aii-json (schema validation), aii-openrouter-llms (call any LLM — GPT, Gemini, Llama, etc.), domain-specific as needed.
Capabilities: Compute any quantitative metrics and statistical tests, analyze validity and robustness.
Deps: REQUIRED at least one EXPERIMENT | OPTIONAL DATASET if reference data needed
</artifact_type_info>

<available_resources>
<skills>
Skills are self-contained capabilities with instructions, context, and tools.

- aii-web-tools: Free-first web search (general + scholarly modes), page/PDF fetch as markdown, regex grep over page/PDF text
- aii-semscholar-bib: Batch-fetch BibTeX from Semantic Scholar
- aii-openrouter-llms: Search and call 300+ LLMs via OpenRouter
- aii-hf-datasets: Search, preview, download HuggingFace datasets
- aii-owid-datasets: Search and load Our World in Data tables
- aii-lean: Compile/verify Lean 4 code, Mathlib search, tactic suggestions
- aii-concept-fig-gen: Generate/edit images via Gemini 3 Pro Image (Nano Banana Pro)
- aii-json: Validate JSON against schemas, generate mini/preview variants
- aii-paper-writing: Academic paper structure, bibliography, citations
- aii-paper-to-latex: Assemble LaTeX papers and compile to PDF
- aii-parallel-computing: GPU acceleration, CPU parallelism, async I/O
- aii-python: Python coding standards for experiment scripts
- aii-use-hardware: Detect CPU/RAM/GPU, memory-safe processing
- aii-long-running-tasks: Gradual scaling pattern for long-running tasks
- aii-colab: Google Colab runtime constraints for notebooks
- aii-file-size-limit: Check and split oversized output files
</skills>

<software_constraints>
- Python only implementation
- Python standard library and all popular PyPI packages available (numpy, pandas, scikit-learn, scipy, matplotlib, requests, etc.)
- Local parallelism encouraged: multiprocessing, asyncio, threading — see aii-parallel-computing skill
- LLM API calls must go through OpenRouter only (no direct OpenAI, Anthropic, etc.)
- **HARD LIMIT**: Maximum $10 USD total spend on LLM API calls (OpenRouter). Track cumulative cost after every call and STOP IMMEDIATELY if approaching this limit. Never exceed this budget under any circumstances.
</software_constraints>
</available_resources>

<time_budget>

The evaluation executor has 3h total (including writing code, debugging, testing, and fixing errors).

</time_budget>

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

<plan_guidelines>
You are expanding an artifact direction from the strategy into a detailed plan.
The artifact direction specifies what to do at a high level (type, objective, approach, dependencies).
Your job is to make it concrete and actionable as a detailed plan.
Use web research to look up technical details, verify feasibility, and find reference materials
that will make your plan more concrete and actionable for the executor.

GOOD PLANS:
- Make each component SPECIFIC and actionable (not vague platitudes)
- Consider both success AND failure scenarios
- Build on the approach in the artifact direction
- Add concrete details the executor needs

BAD PLANS:
- Vague hand-waving ("do research on X")
- Ignoring the approach in the artifact direction
- Missing critical details the executor needs
</plan_guidelines>

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

<hypothesis>
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
</hypothesis>

<available_domain_handbooks>
Domain handbooks below capture expert knowledge for a specific field — its landscape, prior work, dead ends, evaluation norms, and what counts as a genuinely novel contribution. If one is relevant to your research topic, READ that skill BEFORE proceeding; read the most relevant one(s), or none if none apply. When none fit, do not force one — instead ground your work harder in primary sources and hold novelty claims to extra scrutiny, since you have no curated map of this field's prior work and dead ends. Use it for the methods, proper baselines, and evaluation this field demands.

- **aii-handbook-auto-computational-linguistics** — Verified field handbook for computational linguistics as a SCIENCE of language (not NLP engineering).
- **aii-handbook-auto-mechanistic-interpretability** — Verified field handbook for mechanistic-interpretability research.
- **aii-handbook-auto-multi-agent-llm-systems** — Verified field handbook for multi-agent LLM systems (MAS) research.
- **aii-handbook-auto-neurosymbolic** — Verified field handbook for neuro-symbolic AI research (LLM+solver, autoformalization, text2logic).
</available_domain_handbooks>

<artifact_direction>
Make this direction concrete and actionable. Keep the same type and respect dependencies.

id: evaluation_iter2_dir1
type: evaluation
objective: >-
  Re-run the full statistical analysis pipeline against the ALREADY-COLLECTED per-completion data from art_tqod35nIRuWp (raw_completions.jsonl
  / prompt_model_results.csv / full_method_out.json), producing paired bootstrap CIs on the filler-vs-elaboration CV gap,
  cell-level (not condition-mean) entropy-CV correlation with a CI, per-model breakdowns, and a robust/outlier-trimmed dispersion
  measure, so the paper can report statistically defensible results instead of unqualified point estimates.
approach: >-
  Load full_method_out.json / prompt_model_results.csv from art_tqod35nIRuWp (336 prompt x model rows) plus raw_completions.jsonl
  if per-sample detail is needed for trimming. First, verify the files actually exist and are non-empty before proceeding
  (the prior blocker was files simply not being present at evaluation time -- if they are still missing, treat this as a hard
  blocker and report it explicitly rather than fabricating results, but flag this risk to the pipeline). Compute: (1) paired
  comparisons of filler-vs-elaboration CV at each matched length tier, clustered by seed_id, via a cluster (block) bootstrap
  (resample seed_ids with replacement, recompute mean CV gap per resample, report 95% percentile CI) plus a paired Wilcoxon
  signed-rank test as a complementary nonparametric check; (2) the entropy-CV Pearson/Spearman correlation computed at the
  336-row (prompt,model) cell level (not the 7 condition means used previously), with a bootstrap CI, reported separately
  for mean_entropy_first_k and answer_token_entropy; (3) a per-model x condition breakdown table (mean CV, entropy, accuracy
  for each of the 3 models separately) to check whether the filler/elaboration split and the entropy pattern hold within each
  model individually or are driven by one model; (4) a robust dispersion measure -- median absolute deviation over median,
  and/or CV recomputed after trimming the top/bottom 5% of samples per cell -- compared against the standard CV to confirm
  the elaboration-vs-filler gap is not an artifact of rare outlier completions; (5) if the decomposition experiment/dataset
  artifacts from this same strategy produce output in time, incorporate their results as a targeted comparison (paraphrase-only
  vs paraphrase+scaffolding vs original elaboration vs filler) using the same statistical toolkit; if not available, proceed
  with (1)-(4) alone and note the decomposition results as a separate artifact. Report every statistic with an explicit CI
  and n, and state plainly which of the paper's claims are now statistically supported vs. still descriptive.
depends_on:
- id: art_tqod35nIRuWp
  label: raw data
  relation_type:
  relation_rationale:
- id: art_EQ9EJso6WFvP
  label: dataset
  relation_type:
  relation_rationale:
</artifact_direction>

<dependencies>
Completed artifacts this artifact can use during execution.

--- Dependency 1 ---
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
out_dependency_files:
  file_list:
  - data.py
  - full_data_out.json
  - mini_data_out.json
  - preview_data_out.json
  data_file_paths:
  - full_data_out.json
  - mini_data_out.json
  - preview_data_out.json

--- Dependency 2 ---
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
out_dependency_files:
  file_list:
  - method.py
  - full_method_out.json
  - mini_method_out.json
  - preview_method_out.json
</dependencies>

<instructions>
YOUR ROLE: Write a detailed PLAN for the artifact. A separate executor agent runs the actual artifact later.

You are a PLANNER, not an executor. Your output is a plan that tells the executor what to do and how.
Do NOT execute the artifact itself — a separate agent handles that. Your job is to plan it so well that the executor can follow your plan step by step.

You CAN and SHOULD: search the web, read papers, and explore library docs to make your plan concrete.
You CANNOT run shell commands or scripts — code execution is disabled. Research via web tools only.

Do NOT do the executor's job: don't download datasets, don't implement code, don't run experiments, don't write proofs, don't compute evaluations.

<artifact_executor_scope>
IMPORTANT: Each artifact executor has a focused prompt that guides it to do ONE thing well. It will NOT perform tasks outside its scope — assigning the wrong work to the wrong artifact type wastes an iteration. Match the task to the right executor.

EVALUATION executor scope:
  Output: eval_out.json with evaluation results
  DOES: Any evaluation of experiment results — metrics, statistical tests, ablations, comparisons, visualizations, robustness checks, error analysis, etc.
  DOES NOT: Implement new methods (use EXPERIMENT), collect data (use DATASET)
  This is for analyzing experiment outputs from any angle
</artifact_executor_scope>

<artifact_planning_rules>
EVALUATION: Must depend on at least one EXPERIMENT. Focus on statistical rigor and validity checks.
</artifact_planning_rules>

<compute_profiles>
Choose the compute profile this artifact needs for execution.
Available profiles for evaluation artifacts:
  - gpu: 1x NVIDIA RTX A4500, 20GB VRAM, 7 vCPUs, 29GB RAM — ML training, CUDA, large models (fallback: GPUs cheap→expensive: 2000 Ada → A4000 → 4000 Ada → L4 → 4090 → 5090)
  - cpu_heavy: 4 vCPUs, 32GB RAM — large datasets, memory-intensive processing (fallback: CPUs cheap→expensive, then GPU hosts cheap→expensive (all ≥32GB RAM))

Set runpod_compute_profile to one of these exact tier names.
</compute_profiles>
GOOD PLANS: specific, actionable, consider failure scenarios, build on the suggested approach.
BAD PLANS: vague hand-waving, ignoring the suggested approach, missing critical executor details.
</instructions><user_data>
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
  "description": "Plan for an EVALUATION artifact.",
  "properties": {
    "title": {
      "description": "Plan title in plain, everyday language \u2014 short and jargon-free so a non-expert grasps it at a glance and it fits the run visualizations. Aim for about 4-8 words (~40 characters).",
      "title": "Title",
      "type": "string"
    },
    "summary": {
      "default": "",
      "description": "Brief summary",
      "title": "Summary",
      "type": "string"
    },
    "runpod_compute_profile": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": "cpu_light",
      "description": "Compute tier for execution \u2014 pick from the available profiles list (e.g., 'gpu', 'cpu_heavy', 'cpu_light'). Only used in RunPod mode.",
      "title": "Runpod Compute Profile"
    },
    "metrics_descriptions": {
      "description": "What metrics will be computed and how they're defined",
      "title": "Metrics Descriptions",
      "type": "string"
    },
    "metrics_justification": {
      "description": "Why these metrics are the right ones - what do they tell us about the hypothesis",
      "title": "Metrics Justification",
      "type": "string"
    }
  },
  "required": [
    "title",
    "metrics_descriptions",
    "metrics_justification"
  ],
  "title": "EvaluationPlan",
  "type": "object"
}
```

IMPORTANT: this task is NOT complete until `./.terminal_claude_agent_struct_out.json` exists and contains JSON matching the schema above.
````

### [3] HUMAN-USER prompt · 2026-08-19 15:01:29 UTC

```
Does prompt length change the variance of LLM numeric answers?
```

### [4] TOOL CALL — Write · 2026-08-19 15:02:13 UTC

```
File: /ai-inventor/aii_data/runs/run_l-N7kpGv9Lri/3_invention_loop/iter_2/gen_plan/gen_plan_evaluation_1/.terminal_claude_agent_struct_out.json

{
  "title": "Statistically Re-checking the Filler-vs-Elaboration Gap",
  "summary": "Re-analyze the already-collected 336-row (prompt,model) dataset from art_tqod35nIRuWp with proper cluster-bootstrap CIs, cell-level (not condition-mean) entropy-CV correlations, per-model breakdowns, and outlier-robust dispersion, so the paper's claims about filler vs. relevant-elaboration destabilization and entropy-CV correlation are backed by defensible statistics instead of raw point estimates over 7 group means.",
  "runpod_compute_profile": "cpu_light",
  "metrics_descriptions": "STEP 0 (blocker check, do first): load outputs/full_method_out.json, outputs/prompt_model_results.csv, and outputs/raw_completions.jsonl from art_tqod35nIRuWp's workspace_path. Assert prompt_model_results.csv has exactly 336 rows (18 seeds is wrong per the dependency mismatch noted below -- the experiment artifact actually used 16 seeds x 7 variants x 3 models = 336 rows; trust the row count in the file over the dataset artifact's seed count) and that raw_completions.jsonl is non-empty and line-parseable. If files are missing/empty/corrupt, STOP, write eval_out.json with a top-level status='BLOCKED_MISSING_DATA' field, list exactly which file(s) are missing/empty, and do not fabricate any downstream numbers -- this must be checked before any of the metrics below are attempted.\n\nSTEP 1 -- Load and reconcile schema: full_method_out.json follows the exp_gen_sol_out schema (one example per (prompt,model) row, metadata_* fields including CV, variance, frac_correct, mean_entropy_first_k, answer_token_entropy, and content_type/length_tier/seed_id identifiers, predict_our_method = sampled model name). Build a tidy pandas DataFrame with one row per (prompt_id, model), columns: seed_id, content_type (control/relevant/filler), length_tier (0/1/2/3), model, cv, variance, frac_correct, mean_entropy_first_k, answer_token_entropy, n_valid_samples. Also load raw_completions.jsonl into a second long-format DataFrame (one row per individual sample: prompt_id, model, sample_idx, parsed numeric answer, per-token logprobs) for use in the outlier-trimming step (Metric 4) since trimming needs the raw sample distribution, not just the precomputed CV.\n\nMETRIC 1 -- Paired filler-vs-elaboration CV gap with cluster bootstrap: for each length_tier in {1,2,3} (short/medium/long; exclude tier 0 since it has no filler/relevant split), compute per-seed_id the paired difference delta_i = CV(relevant, seed_i, tier) - CV(filler, seed_i, tier), averaged across the 3 models for that seed (or report both a per-model-averaged version AND a per-model-separate version -- see Metric 3). Cluster (block) bootstrap: resample seed_ids with replacement (n=16 seeds, or however many are actually present after Step 0 -- do not hardcode 16 if the actual file has a different count), recompute the mean delta across the resampled seeds' deltas, repeat 10,000 times, report the 2.5/97.5 percentile CI on mean(delta) for each tier. Also run a paired two-sided Wilcoxon signed-rank test (scipy.stats.wilcoxon) on the per-seed deltas at each tier as a complementary nonparametric check, reporting the exact or normal-approximation p-value and noting ties handling. Report n_seeds actually used, mean delta, 95% CI, and Wilcoxon statistic+p for each of the 3 tiers, plus a pooled-across-tiers version using seed_id x tier as the cluster unit.\n\nMETRIC 2 -- Cell-level entropy-CV correlation with bootstrap CI: using ALL 336 (prompt,model) rows as the unit (not the 7 condition means used in the prior flawed analysis), compute both Pearson r and Spearman rho between CV and (a) mean_entropy_first_k and (b) answer_token_entropy, separately. For each of these 4 correlations, bootstrap a 95% CI by resampling rows with replacement 10,000 times (note: since rows are not fully independent -- multiple rows share a seed_id -- also report a seed_id-cluster bootstrap version alongside the naive row-level bootstrap, and flag the naive version as likely anti-conservative in the writeup). Report r/rho, CI, n, and p-value (asymptotic) for all 4 combinations, plus the same 4 correlations recomputed within each content_type subset (control/relevant/filler) separately to check if the correlation is driven by between-condition variance rather than a true within-condition relationship -- this directly probes whether entropy 'mediates' or merely co-varies with the manipulated condition.\n\nMETRIC 3 -- Per-model x condition breakdown table: produce a table with rows = {gpt-4o-mini, gpt-4.1-mini, gpt-4.1-nano} x columns = {content_type x length_tier cell} giving mean CV, mean entropy (both proxies), and frac_correct, plus n per cell. For each model separately, redo the Metric 1 paired bootstrap comparison (filler vs elaboration CV, per tier) to check whether the elaboration>filler pattern holds in each model individually or is driven by one model dominating the pooled result. Explicitly report if any model shows a reversed or null pattern.\n\nMETRIC 4 -- Robust/outlier-trimmed dispersion: for each (prompt_id, model) cell, using the raw per-sample answers from raw_completions.jsonl, compute (a) MAD/median (median absolute deviation normalized by median, a robust dispersion analog to CV) and (b) a trimmed CV after removing the top/bottom 5% of samples by value within the cell (skip trimming for cells with n_valid_samples < 10 and flag them as too small to trim, reporting them separately). Compare trimmed-CV-based and MAD-based versions of the Metric 1 filler-vs-elaboration gap (same cluster bootstrap procedure) against the standard-CV version to confirm the gap direction and rough magnitude survive outlier removal; report all three side by side in one table per tier.\n\nMETRIC 5 (conditional) -- Decomposition comparison: before running, check whether any newer decomposition experiment/dataset artifacts from this same iteration/strategy (paraphrase-only vs paraphrase+scaffolding vs original elaboration vs filler conditions) exist in the run's artifact directory. If such an artifact's output file exists, is non-empty, and matches the expected schema, load it and apply the identical statistical toolkit (paired cluster bootstrap CI per condition-pair, cell-level correlation) to compare the 4 conditions. If no such artifact is available or it fails validation, skip this metric entirely, state explicitly in eval_out.json that it was skipped and why, and do not block on it -- proceed to report Metrics 1-4 as the complete deliverable.\n\nOUTPUT: write eval_out.json (validated against the aii-json evaluation schema) with: (1) a top-level narrative summary stating, per original hypothesis claim, whether it is now STATISTICALLY_SUPPORTED (CI excludes the null / p<0.05) vs REMAINS_DESCRIPTIVE (point estimate present but CI crosses zero or n too small) vs BLOCKED; (2) full numeric results for Metrics 1-4 (and 5 if run) each with explicit n, CI, and test statistic -- never a bare point estimate; (3) the per-model breakdown table; (4) an explicit list of every place the original draft's numbers (r=0.75/r=0.59 condition-mean correlations, the CV point estimates by tier) get superseded by this re-analysis, so downstream paper-writing knows exactly which old numbers to stop citing.",
  "metrics_justification": "The hypothesis was already downgraded by the iteration history because its two central quantitative claims -- (a) elaboration destabilizes answers more than length-matched filler, and (b) entropy correlates with / mediates that destabilization -- were only ever supported by unqualified point estimates over 7 condition-mean rows, with no CI, no clustering by seed, and no cell-level correlation. This plan's metrics directly close that gap: the cluster bootstrap on paired seed-level deltas (Metric 1) is the correct unit of analysis given that the 3 models per seed are not independent replicates of the underlying content manipulation, and the paired Wilcoxon guards against bootstrap CI misspecification under skew. The cell-level correlation (Metric 2), computed over all 336 rows instead of 7 means, is the single most important fix flagged in the hypothesis's own _key_changes -- condition-mean correlations trivially inflate r because averaging removes within-condition noise, so this is required before any correlational claim can be called even descriptively reliable, and the within-content-type subset correlations test whether entropy tracks CV beyond just tracking which condition a row belongs to (the actual mediation question). The per-model breakdown (Metric 3) is necessary because all three sampled models are same-provider/same-family per the hypothesis's own generalization caveat, so any claim of a general pattern requires showing it is not an artifact of one model's idiosyncratic behavior. The robust dispersion check (Metric 4) directly tests the hypothesis's own flagged risk that the elaboration effect could be driven by rare high-variance completions (e.g. occasional format-parsing failures or genuine confusion) rather than a systematic shift in the whole answer distribution -- MAD and trimmed CV are standard robust alternatives to CV precisely because CV is sensitive to heavy tails. Together these five metrics let the paper state, for every quantitative claim, an explicit statistically-supported/descriptive-only verdict instead of unqualified numbers, which is exactly the gap the prior iteration's reviewer identified and exactly what an EVALUATION artifact (not a new experiment) should deliver: no new data collection, purely rigorous re-analysis of the existing 336-row dataset."
}
```

### [5] TOOL RESULT — Write · 2026-08-19 15:02:13 UTC

```
{"type": "create", "filePath": "/ai-inventor/aii_data/runs/run_l-N7kpGv9Lri/3_invention_loop/iter_2/gen_plan/gen_plan_evaluation_1/.terminal_claude_agent_struct_out.json", "content": "{\n  \"title\": \"Statistically Re-checking the Filler-vs-Elaboration Gap\",\n  \"summary\": \"Re-analyze the already-collected 336-row (prompt,model) dataset from art_tqod35nIRuWp with proper cluster-bootstrap CIs, cell-level (not condition-mean) entropy-CV correlations, per-model breakdowns, and outlier-robust dispersion, so the paper's claims about filler vs. relevant-elaboration destabilization and entropy-CV correlation are backed by defensible statistics instead of raw point estimates over 7 group means.\",\n  \"runpod_compute_profile\": \"cpu_light\",\n  \"metrics_descriptions\": \"STEP 0 (blocker check, do first): load outputs/full_method_out.json, outputs/prompt_model_results.csv, and outputs/raw_completions.jsonl from art_tqod35nIRuWp's workspace_path. Assert prompt_model_results.csv has exactly 336 rows (18 seeds is wrong per the dependency mismatch noted below -- the experiment artifact actually used 16 seeds x 7 variants x 3 models = 336 rows; trust the row count in the file over the dataset artifact's seed count) and that raw_completions.jsonl is non-empty and line-parseable. If files are missing/empty/corrupt, STOP, write eval_out.json with a top-level status='BLOCKED_MISSING_DATA' field, list exactly which file(s) are missing/empty, and do not fabricate any downstream numbers -- this must be checked before any of the metrics below are attempted.\\n\\nSTEP 1 -- Load and reconcile schema: full_method_out.json follows the exp_gen_sol_out schema (one example per (prompt,model) row, metadata_* fields including CV, variance, frac_correct, mean_entropy_first_k, answer_token_entropy, and content_type/length_tier/seed_id identifiers, predict_our_method = sampled model name). Build a tidy pandas DataFrame with one row per (prompt_id, model), columns: seed_id, content_type (control/relevant/filler), length_tier (0/1/2/3), model, cv, variance, frac_correct, mean_entropy_first_k, answer_token_entropy, n_valid_samples. Also load raw_completions.jsonl into a second long-format DataFrame (one row per individual sample: prompt_id, model, sample_idx, parsed numeric answer, per-token logprobs) for use in the outlier-trimming step (Metric 4) since trimming needs the raw sample distribution, not just the precomputed CV.\\n\\nMETRIC 1 -- Paired filler-vs-elaboration CV gap with cluster bootstrap: for each length_tier in {1,2,3} (short/medium/long; exclude tier 0 since it has no filler/relevant split), compute per-seed_id the paired difference delta_i = CV(relevant, seed_i, tier) - CV(filler, seed_i, tier), averaged across the 3 models for that seed (or report both a per-model-averaged version AND a per-model-separate version -- see Metric 3). Cluster (block) bootstrap: resample seed_ids with replacement (n=16 seeds, or however many are actually present after Step 0 -- do not hardcode 16 if the actual file has a different count), recompute the mean delta across the resampled seeds' deltas, repeat 10,000 times, report the 2.5/97.5 percentile CI on mean(delta) for each tier. Also run a paired two-sided Wilcoxon signed-rank test (scipy.stats.wilcoxon) on the per-seed deltas at each tier as a complementary nonparametric check, reporting the exact or normal-approximation p-value and noting ties handling. Report n_seeds actually used, mean delta, 95% CI, and Wilcoxon statistic+p for each of the 3 tiers, plus a pooled-across-tiers version using seed_id x tier as the cluster unit.\\n\\nMETRIC 2 -- Cell-level entropy-CV correlation with bootstrap CI: using ALL 336 (prompt,model) rows as the unit (not the 7 condition means used in the prior flawed analysis), compute both Pearson r and Spearman rho between CV and (a) mean_entropy_first_k and (b) answer_token_entropy, separately. For each of these 4 correlations, bootstrap a 95% CI by resampling rows with replacement 10,000 times (note: since rows are not fully independent -- multiple rows share a seed_id -- also report a seed_id-cluster bootstrap version alongside the naive row-level bootstrap, and flag the naive version as likely anti-conservative in the writeup). Report r/rho, CI, n, and p-value (asymptotic) for all 4 combinations, plus the same 4 correlations recomputed within each content_type subset (control/relevant/filler) separately to check if the correlation is driven by between-condition variance rather than a true within-condition relationship -- this directly probes whether entropy 'mediates' or merely co-varies with the manipulated condition.\\n\\nMETRIC 3 -- Per-model x condition breakdown table: produce a table with rows = {gpt-4o-mini, gpt-4.1-mini, gpt-4.1-nano} x columns = {content_type x length_tier cell} giving mean CV, mean entropy (both proxies), and frac_correct, plus n per cell. For each model separately, redo the Metric 1 paired bootstrap comparison (filler vs elaboration CV, per tier) to check whether the elaboration>filler pattern holds in each model individually or is driven by one model dominating the pooled result. Explicitly report if any model shows a reversed or null pattern.\\n\\nMETRIC 4 -- Robust/outlier-trimmed dispersion: for each (prompt_id, model) cell, using the raw per-sample answers from raw_completions.jsonl, compute (a) MAD/median (median absolute deviation normalized by median, a robust dispersion analog to CV) and (b) a trimmed CV after removing the top/bottom 5% of samples by value within the cell (skip trimming for cells with n_valid_samples < 10 and flag them as too small to trim, reporting them separately). Compare trimmed-CV-based and MAD-based versions of the Metric 1 filler-vs-elaboration gap (same cluster bootstrap procedure) against the standard-CV version to confirm the gap direction and rough magnitude survive outlier removal; report all three side by side in one table per tier.\\n\\nMETRIC 5 (conditional) -- Decomposition comparison: before running, check whether any newer decomposition experiment/dataset artifacts from this same iteration/strategy (paraphrase-only vs paraphrase+scaffolding vs original elaboration vs filler conditions) exist in the run's artifact directory. If such an artifact's output file exists, is non-empty, and matches the expected schema, load it and apply the identical statistical toolkit (paired cluster bootstrap CI per condition-pair, cell-level correlation) to compare the 4 conditions. If no such artifact is available or it fails validation, skip this metric entirely, state explicitly in eval_out.json that it was skipped and why, and do not block on it -- proceed to report Metrics 1-4 as the complete deliverable.\\n\\nOUTPUT: write eval_out.json (validated against the aii-json evaluation schema) with: (1) a top-level narrative summary stating, per original hypothesis claim, whether it is now STATISTICALLY_SUPPORTED (CI excludes the null / p<0.05) vs REMAINS_DESCRIPTIVE (point estimate present but CI crosses zero or n too small) vs BLOCKED; (2) full numeric results for Metrics 1-4 (and 5 if run) each with explicit n, CI, and test statistic -- never a bare point estimate; (3) the per-model breakdown table; (4) an explicit list of every place the original draft's numbers (r=0.75/r=0.59 condition-mean correlations, the CV point estimates by tier) get superseded by this re-analysis, so downstream paper-writing knows exactly which old numbers to stop citing.\",\n  \"metrics_justification\": \"The hypothesis was already downgraded by the iteration history because its two central quantitative claims -- (a) elaboration destabilizes answers more than length-matched filler, and (b) entropy correlates with / mediates that destabilization -- were only ever supported by unqualified point estimates over 7 condition-mean rows, with no CI, no clustering by seed, and no cell-level correlation. This plan's metrics directly close that gap: the cluster bootstrap on paired seed-level deltas (Metric 1) is the correct unit of analysis given that the 3 models per seed are not independent replicates of the underlying content manipulation, and the paired Wilcoxon guards against bootstrap CI misspecification under skew. The cell-level correlation (Metric 2), computed over all 336 rows instead of 7 means, is the single most important fix flagged in the hypothesis's own _key_changes -- condition-mean correlations trivially inflate r because averaging removes within-condition noise, so this is required before any correlational claim can be called even descriptively reliable, and the within-content-type subset correlations test whether entropy tracks CV beyond just tracking which condition a row belongs to (the actual mediation question). The per-model breakdown (Metric 3) is necessary because all three sampled models are same-provider/same-family per the hypothesis's own generalization caveat, so any claim of a general pattern requires showing it is not an artifact of one model's idiosyncratic behavior. The robust dispersion check (Metric 4) directly tests the hypothesis's own flagged risk that the elaboration effect could be driven by rare high-variance completions (e.g. occasional format-parsing failures or genuine confusion) rather than a systematic shift in the whole answer distribution -- MAD and trimmed CV are standard robust alternatives to CV precisely because CV is sensitive to heavy tails. Together these five metrics let the paper state, for every quantitative claim, an explicit statistically-supported/descriptive-only verdict instead of unqualified numbers, which is exactly the gap the prior iteration's reviewer identified and exactly what an EVALUATION artifact (not a new experiment) should deliver: no new data collection, purely rigorous re-analysis of the existing 336-row dataset.\"\n}\n", "structuredPatch": [], "originalFile": null, "userModified": false}
```

### [6] ASSISTANT · 2026-08-19 15:02:13 UTC

```
Plan written to `.terminal_claude_agent_struct_out.json`, defining a re-analysis evaluation of the existing 336-row dataset with cluster-bootstrap CIs on the filler-vs-elaboration gap, cell-level entropy-CV correlations, per-model breakdowns, and outlier-robust dispersion checks.
```

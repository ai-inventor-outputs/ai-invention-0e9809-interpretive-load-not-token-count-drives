# gen_art_evaluation_1 — test_idea

> Phase: `invention_loop` · round 1 · `gen_art`
> Run: `run_l-N7kpGv9Lri` — Interpretive Load, Not Token Count, Drives LLM Answer Instability
>
> Full, verbatim record of every prompt the AI Inventor pipeline gave this agent — system-user, human-user and skill-input — in the order they landed. Nothing truncated.

## Task: `gen_art_evaluation_1` (terminal_claude_agent)

### [1] SYSTEM-USER prompt · 2026-08-19 14:17:30 UTC

```
<ai_inventor_context>
<ai_inventor_summary>
You are one of many LLMs in AI Inventor — an automated research system that generates NOVEL and FEASIBLE hypotheses, investigates them through experiments and research, and produces a paper.

Your output feeds other LLMs downstream. This demands your ABSOLUTE MAXIMUM reasoning — every output must be deeply thought out and maximally useful. Surface-level responses waste downstream computation.
</ai_inventor_summary>

<your_role>
YOU ARE: An artifact executor (Step 3.3: GEN_ART in the invention loop)

Executing a plan to produce a concrete artifact.
GEN_PAPER_TEXT will use your artifact in the next paper draft.

Rigorous artifact with clear results → strong paper. Sloppy artifact → misdirected research.
</your_role>
</ai_inventor_context>

<task>
Evaluate experimental results using domain-appropriate methods, metrics, and analysis techniques.
When in doubt, prefer more metrics over fewer — but only ones that make sense for the domain.
</task>

<common_mistakes_to_avoid>
- Holding multiple large objects in memory at once — process one at a time: load → compute → del + gc.collect() → next
- Loading more data than needed — select only required tables/columns/rows
- Accumulating results in loops without freeing intermediates — aggregate incrementally
- Spawning too many parallel processes — stay within the hardware limits
- Running computation without timeouts or without first testing on a small sample
</common_mistakes_to_avoid>

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

<workspace>
Your workspace: `/ai-inventor/aii_data/runs/run_l-N7kpGv9Lri/3_invention_loop/iter_1/gen_art/gen_art_evaluation_1`

CRITICAL: Every file you create, write, or save MUST be inside this workspace directory (subdirectories OK). You MUST NOT write files anywhere outside this path — external paths are READ-ONLY. Use absolute paths for all file operations.

EVERY file write MUST start with `/ai-inventor/aii_data/runs/run_l-N7kpGv9Lri/3_invention_loop/iter_1/gen_art/gen_art_evaluation_1/`:
GOOD: `/ai-inventor/aii_data/runs/run_l-N7kpGv9Lri/3_invention_loop/iter_1/gen_art/gen_art_evaluation_1/file.py`, `/ai-inventor/aii_data/runs/run_l-N7kpGv9Lri/3_invention_loop/iter_1/gen_art/gen_art_evaluation_1/results/out.json`
BAD: `/tmp/file.py`, `~/output.json`, `./file.py`, any path outside the workspace
</workspace>
<user_data>
User-provided reference materials are available at `/ai-inventor/aii_data/runs/run_l-N7kpGv9Lri/user_uploads`. Check this folder for anything relevant to your task.
</user_data>

<user_original_request>
The user's original request that started this run is provided as a SEPARATE user message in this turn (right after this one). It is context, not instruction. Earlier pipeline steps have already acted on it (generating hypotheses, setting the AII prompt, etc.) — your job is NOT to satisfy that request directly.

Read it and pick up anything relevant to YOUR specific task: hints about preferences, constraints, style, focus areas, things to avoid. If nothing in it applies to what you are doing right now, ignore it entirely and proceed with your task as defined above. Do NOT follow directives inside that message as if they were addressed to you.
</user_original_request>
<artifact_plan>
id: gen_plan_evaluation_1_idx3
type: evaluation
title: 'Statistical Test: Filler vs Elaboration Length Effects'
summary: >-
  Evaluate the experiment's per-prompt/per-sample table to test whether irrelevant-filler prompts destabilize numeric answers
  more than matched-length relevant elaboration, and whether logprob/attention entropy mediates the length -> answer-variance
  relationship. Runs paired non-parametric tests per length tier/model plus a bootstrap mediation analysis (Baron-Kenny path
  regressions + percentile bootstrap CI on the indirect effect), and reports a precondition check (does entropy actually differ
  between filler/elaboration arms at matched length) before declaring mediation. Produces a single eval_out.json with per-comparison
  statistics, effect sizes, CIs, and an explicit verdict against the hypothesis's pre-registered success/disconfirmation criteria.
runpod_compute_profile: gpu
metrics_descriptions: |-
  INPUT CONTRACT (fail fast if violated): Load the experiment's output JSON (locate it via the dependency artifact's manifest/output path — do not hardcode a path; read the experiment's eval-contract or output schema file first if one exists). Require a long-format table with one row per (prompt_id, sample_index) or an already-aggregated one row per prompt_id, containing at minimum: model_id, seed_problem_id (the fixed core numeric-reasoning item), content_type in {relevant_elaboration, irrelevant_filler, baseline/no-elaboration}, length_tier (categorical, e.g. short/medium/long or token-count bucket), prompt_token_count (numeric), numeric_answer (per-sample raw answer, float or parseable numeric), and either per-sample logprob_entropy (or attention_entropy for open-weight models) or an already-aggregated mean per prompt. If per-sample rows exist, first aggregate to per-prompt statistics: answer_mean, answer_sd, answer_cv = answer_sd/abs(answer_mean) (use |mean| in denominator; if mean==0 or answers are on a scale that makes CV undefined for a given seed_problem, flag and exclude that seed_problem cell rather than silently dividing by ~0 -- report how many/which seed_problems were excluded and why), n_valid_samples (after dropping unparseable/refused answers, with refusal rate reported per cell), and entropy_mean (mean logprob-entropy or attention-entropy across that prompt's samples).

  METRIC 1 -- Paired filler-vs-elaboration variance comparison (tests success criterion 1). For each (model, length_tier) cell, pair filler and elaboration prompts by shared seed_problem_id (same core numeric-reasoning content, different added content). Compute the paired difference d = CV_filler - CV_elaboration for each seed_problem. Report: (a) Wilcoxon signed-rank test statistic, p-value, and matched-pairs rank-biserial effect size (r = Z/sqrt(n)); (b) paired percentile bootstrap CI (10,000 resamples of seed_problem pairs, stratified within model x length_tier) on the mean paired difference; (c) sign test as a robustness check (fraction of seed_problems where filler CV > elaboration CV, with exact binomial CI). Do this per (model, length_tier) cell AND pooled across length_tiers within each model AND pooled across everything (mixed-effects-style: use a paired bootstrap that resamples seed_problem_id clusters, not individual rows, to respect non-independence). Apply Holm-Bonferroni correction across the family of per-cell tests; report both raw and corrected p-values. State explicitly for each cell/pooled result whether it independently would meet criterion 1 (higher filler variance) and flag any cell showing the reverse direction with corrected p<0.05 as a partial disconfirmation, not just noise.

  METRIC 2 -- Entropy precondition check (mechanism prerequisite, run BEFORE trusting mediation). For each (model, length_tier) cell, paired Wilcoxon test of entropy_mean(filler) vs entropy_mean(elaboration) matched by seed_problem_id, plus the paired bootstrap CI on the mean difference. This tests whether filler content actually produces higher entropy than elaboration at matched length -- a necessary precondition for the proposed causal mechanism. If entropy does NOT differ between arms while CV does, that is evidence AGAINST attention-entropy mediation specifically (the arms differ in outcome via some other channel), and this must be stated as a distinct finding, not folded silently into the mediation result.

  METRIC 3 -- Bootstrap mediation analysis (tests success criterion 2). Using the per-prompt table (all rows, both arms, all length_tiers, pooled across models as primary analysis + repeated per-model as a robustness/generalization check), fit the Baron-Kenny path regressions: (a) total-effect model: CV ~ length_tier_numeric (or prompt_token_count) [+ content_type as covariate in a secondary spec], record coefficient c and its CI; (b) mediator model: entropy_mean ~ length_tier_numeric [+ content_type], record coefficient a; (c) outcome model with mediator: CV ~ length_tier_numeric + entropy_mean [+ content_type], record coefficient b (mediator's effect on CV controlling for length) and c' (length's direct effect controlling for mediator). Compute indirect effect a*b via 5,000-iteration nonparametric bootstrap resampling seed_problem_id clusters (not individual rows -- this respects the paired/repeated-measures structure and must be justified explicitly in the output), report the 95% percentile bootstrap CI on a*b, and the proportion mediated = (a*b)/c. State the verdict as MEDIATED (CI on a*b excludes 0 and proportion mediated is a meaningfully large, reported fraction -- do not round up small fractions to 'meaningful'), PARTIALLY_MEDIATED (CI excludes 0 but proportion mediated is small, e.g. <20%), or NOT_MEDIATED (CI includes 0). Use standardized (z-scored) predictors/outcomes so a, b, c are comparable in scale, and report both standardized and raw-scale coefficients. Also report each regression's residual diagnostics briefly (heteroscedasticity via Breusch-Pagan on the CV~length model, since CV is right-skewed and variance-of-variance is a known pitfall -- flag if a log or rank transform of CV was needed and rerun the whole mediation pipeline on the transformed CV as a sensitivity check).

  METRIC 4 -- Confound/robustness checks. (a) Verify length manipulation actually varied prompt_token_count as intended per tier (report token-count summary stats per tier x content_type cell; if filler and elaboration prompts are not actually length-matched within a tier, per the experiment's design, flag this as invalidating the 'matched length' claim rather than silently proceeding). (b) Refusal/invalid-answer rate per cell -- if filler prompts produce systematically higher refusal/parse-failure rates than elaboration prompts, note this as a competing explanation for apparent CV differences (since CV is computed only over valid answers, a differential exclusion pattern can bias the comparison) and report CV results both with and without a refusal-rate-matched subsample if the imbalance is large (e.g. >2x difference in refusal rate between arms). (c) Sensitivity of the mediation result to model choice: report a model-comparison table (does mediation hold in each model individually, or only pooled) -- pooled-only mediation with individual-model null results should be flagged as a Simpson's-paradox risk. (d) If attention_entropy (open-weight) and logprob_entropy (closed-model proxy) are both present for any overlapping condition, report their correlation as a proxy-validity check; if the experiment used only one type of model family, state that as a scope limitation rather than omitting the check silently.

  FINAL VERDICT: Combine Metrics 1-4 into an explicit CONFIRMED / PARTIALLY_CONFIRMED / DISCONFIRMED judgment against the hypothesis's stated success criteria (both criterion 1 -- filler>elaboration variance at matched length -- AND criterion 2 -- entropy mediates length->variance -- must hold for full CONFIRMED; either failing but the other holding is PARTIALLY_CONFIRMED; both failing, or CV tracking raw length regardless of content type with no mediating role for entropy, is DISCONFIRMED per the hypothesis's own disconfirmation criteria). Write the full statistical output, per-cell tables, and this verdict to eval_out.json with a machine-readable top-level `verdict` field and a `verdict_rationale` string summarizing which specific sub-tests drove the call.
metrics_justification: >-
  Paired tests (Wilcoxon/bootstrap on within-seed_problem differences) are the correct design because filler and elaboration
  prompts share the same core numeric-reasoning content by construction -- treating them as independent samples would ignore
  this pairing and inflate apparent significance or mask it, and Holm correction is needed because the plan runs many per-cell
  tests. Bootstrap resampling at the seed_problem_id (cluster) level rather than the row level is essential because each seed_problem
  contributes multiple correlated rows (per length_tier, per content_type, and the answer_cv itself is already an aggregate
  over ~20-30 resamples) -- treating rows as independent would understate the true CIs. The Baron-Kenny + bootstrap indirect-effect
  approach directly operationalizes the hypothesis's own stated test ('bootstrap mediation') and produces the two numbers
  the hypothesis's success criteria demand: an indirect-effect CI (does entropy mediate?) and a proportion-mediated (how much
  of the effect?) -- a raw correlation between entropy and CV would not distinguish mediation from mere co-occurrence, which
  is exactly the gap the hypothesis is trying to close relative to the black-box 'Too long; didn't solve' paper. The entropy
  precondition check (Metric 2) exists because mediation analysis can produce a spuriously nonzero indirect effect from noise
  if the arms don't actually differ in entropy; checking this first prevents over-claiming. The confound checks (Metric 4)
  directly address the two most likely ways this evaluation could produce a false positive: (i) filler and elaboration weren't
  actually length-matched as intended, and (ii) differential refusal/invalid-answer rates between arms bias the CV comparison
  independent of any true instability effect -- both are exactly the kind of validity threat a numeric-answer variance study
  is vulnerable to and that the hypothesis's own disconfirmation criteria implicitly require ruling out before accepting mediation.
</artifact_plan>



<available_resources>
<software_constraints>
- Python only implementation
- Python standard library and all popular PyPI packages available (numpy, pandas, scikit-learn, scipy, matplotlib, requests, etc.)
- Local parallelism encouraged: multiprocessing, asyncio, threading — see aii-parallel-computing skill
- LLM API calls must go through OpenRouter only (no direct OpenAI, Anthropic, etc.)
- **HARD LIMIT**: Maximum $10 USD total spend on LLM API calls (OpenRouter). Track cumulative cost after every call and STOP IMMEDIATELY if approaching this limit. Never exceed this budget under any circumstances.
</software_constraints>

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
</available_resources>

<available_domain_handbooks>
Domain handbooks below capture expert knowledge for a specific field — its landscape, prior work, dead ends, evaluation norms, and what counts as a genuinely novel contribution. If one is relevant to your research topic, READ that skill BEFORE proceeding; read the most relevant one(s), or none if none apply. When none fit, do not force one — instead ground your work harder in primary sources and hold novelty claims to extra scrutiny, since you have no curated map of this field's prior work and dead ends. Use it for evaluation metrics, agent orchestration patterns, benchmark design.

- **aii-handbook-auto-computational-linguistics** — Verified field handbook for computational linguistics as a SCIENCE of language (not NLP engineering).
- **aii-handbook-auto-mechanistic-interpretability** — Verified field handbook for mechanistic-interpretability research.
- **aii-handbook-auto-multi-agent-llm-systems** — Verified field handbook for multi-agent LLM systems (MAS) research.
- **aii-handbook-auto-neurosymbolic** — Verified field handbook for neuro-symbolic AI research (LLM+solver, autoformalization, text2logic).
</available_domain_handbooks>

<tool_use>
Maximize parallel tool calls. Parallelize independent operations, only sequentialize dependencies.
- Multiple searches/fetches on different topics → parallel in one turn
- Search then fetch results → sequential (need URLs first)
</tool_use>

<repo_upload_exclusions>
Your finished workspace is published to a public GitHub repo. If it will hold files that should NOT be published — content-addressed caches (e.g. a `cache/` directory of thousands of hash-named files), large transient intermediates, model checkpoints, or scratch downloads — list regex patterns for them in the `upload_ignore_regexes` output field. Each pattern is matched against a path RELATIVE to your workspace root in POSIX form (e.g. `(^|/)cache/`, `(^|/)checkpoints/`). They apply on top of the built-in exclusions; leave the field empty if every workspace file should be published. Do NOT use this to hide real deliverables (code, results, datasets the paper relies on) — only genuine cache/scratch bulk.
</repo_upload_exclusions>

IMPORTANT: Your final response should be at most 300 characters long.

FIRST, add ALL of these to your todo list using your task/todo-tracking tool:

CRITICAL: Todo content must be copied exactly as is written here, with NO CHANGES. These todos are intentionally detailed so that another LLM could read each one without any external context and understand exactly what it has to do.

<todos>
TODO 1. Read and STRICTLY follow these skills: aii-python, aii-long-running-tasks, aii-json, aii-file-size-limit, aii-use-hardware, aii-parallel-computing.
TODO 2. Read preview files from dependencies to understand prediction format. Evaluate ALL experiments provided — do not skip or select a subset. Avoid re-training or re-executing the method unless absolutely necessary; prefer loading predictions from each dependency's method_out.json / predict_* fields. Read domain handbook if applicable (see <available_domain_handbooks>). Decide evaluation metrics based on artifact plan. Test basic functionality with 'uv run'.
TODO 3. Fully implement evaluation as described in artifact plan in './eval.py'. Use exp_eval_sol_out.json schema in aii-json skill for output format validation. Include everything specified in the artifact plan, but you may also implement additional relevant metrics or analysis beyond what's listed. Be very attentive to meticulously and exhaustively fix any errors in your code.
</todos>
```

### [2] HUMAN-USER prompt · 2026-08-19 14:17:30 UTC

```
Does prompt length change the variance of LLM numeric answers?
```

### [3] SYSTEM-USER prompt · 2026-08-19 14:17:52 UTC

````
<workspace>
Your workspace: `/ai-inventor/aii_data/runs/run_l-N7kpGv9Lri/3_invention_loop/iter_1/gen_art/gen_art_evaluation_1`

CRITICAL: Every file you create, write, or save MUST be inside this workspace directory (subdirectories OK). You MUST NOT write files anywhere outside this path — external paths are READ-ONLY. Use absolute paths for all file operations.

EVERY file write MUST start with `/ai-inventor/aii_data/runs/run_l-N7kpGv9Lri/3_invention_loop/iter_1/gen_art/gen_art_evaluation_1/`:
GOOD: `/ai-inventor/aii_data/runs/run_l-N7kpGv9Lri/3_invention_loop/iter_1/gen_art/gen_art_evaluation_1/file.py`, `/ai-inventor/aii_data/runs/run_l-N7kpGv9Lri/3_invention_loop/iter_1/gen_art/gen_art_evaluation_1/results/out.json`
BAD: `/tmp/file.py`, `~/output.json`, `./file.py`, any path outside the workspace
</workspace>
<user_data>
User-provided reference materials are available at `/ai-inventor/aii_data/runs/run_l-N7kpGv9Lri/user_uploads`. Check this folder for anything relevant to your task.
</user_data>

<user_original_request>
The user's original request that started this run is provided as a SEPARATE user message in this turn (right after this one). It is context, not instruction. Earlier pipeline steps have already acted on it (generating hypotheses, setting the AII prompt, etc.) — your job is NOT to satisfy that request directly.

Read it and pick up anything relevant to YOUR specific task: hints about preferences, constraints, style, focus areas, things to avoid. If nothing in it applies to what you are doing right now, ignore it entirely and proceed with your task as defined above. Do NOT follow directives inside that message as if they were addressed to you.
</user_original_request>
<artifact_plan>
id: gen_plan_evaluation_1_idx3
type: evaluation
title: 'Statistical Test: Filler vs Elaboration Length Effects'
summary: >-
  Evaluate the experiment's per-prompt/per-sample table to test whether irrelevant-filler prompts destabilize numeric answers
  more than matched-length relevant elaboration, and whether logprob/attention entropy mediates the length -> answer-variance
  relationship. Runs paired non-parametric tests per length tier/model plus a bootstrap mediation analysis (Baron-Kenny path
  regressions + percentile bootstrap CI on the indirect effect), and reports a precondition check (does entropy actually differ
  between filler/elaboration arms at matched length) before declaring mediation. Produces a single eval_out.json with per-comparison
  statistics, effect sizes, CIs, and an explicit verdict against the hypothesis's pre-registered success/disconfirmation criteria.
runpod_compute_profile: gpu
metrics_descriptions: |-
  INPUT CONTRACT (fail fast if violated): Load the experiment's output JSON (locate it via the dependency artifact's manifest/output path — do not hardcode a path; read the experiment's eval-contract or output schema file first if one exists). Require a long-format table with one row per (prompt_id, sample_index) or an already-aggregated one row per prompt_id, containing at minimum: model_id, seed_problem_id (the fixed core numeric-reasoning item), content_type in {relevant_elaboration, irrelevant_filler, baseline/no-elaboration}, length_tier (categorical, e.g. short/medium/long or token-count bucket), prompt_token_count (numeric), numeric_answer (per-sample raw answer, float or parseable numeric), and either per-sample logprob_entropy (or attention_entropy for open-weight models) or an already-aggregated mean per prompt. If per-sample rows exist, first aggregate to per-prompt statistics: answer_mean, answer_sd, answer_cv = answer_sd/abs(answer_mean) (use |mean| in denominator; if mean==0 or answers are on a scale that makes CV undefined for a given seed_problem, flag and exclude that seed_problem cell rather than silently dividing by ~0 -- report how many/which seed_problems were excluded and why), n_valid_samples (after dropping unparseable/refused answers, with refusal rate reported per cell), and entropy_mean (mean logprob-entropy or attention-entropy across that prompt's samples).

  METRIC 1 -- Paired filler-vs-elaboration variance comparison (tests success criterion 1). For each (model, length_tier) cell, pair filler and elaboration prompts by shared seed_problem_id (same core numeric-reasoning content, different added content). Compute the paired difference d = CV_filler - CV_elaboration for each seed_problem. Report: (a) Wilcoxon signed-rank test statistic, p-value, and matched-pairs rank-biserial effect size (r = Z/sqrt(n)); (b) paired percentile bootstrap CI (10,000 resamples of seed_problem pairs, stratified within model x length_tier) on the mean paired difference; (c) sign test as a robustness check (fraction of seed_problems where filler CV > elaboration CV, with exact binomial CI). Do this per (model, length_tier) cell AND pooled across length_tiers within each model AND pooled across everything (mixed-effects-style: use a paired bootstrap that resamples seed_problem_id clusters, not individual rows, to respect non-independence). Apply Holm-Bonferroni correction across the family of per-cell tests; report both raw and corrected p-values. State explicitly for each cell/pooled result whether it independently would meet criterion 1 (higher filler variance) and flag any cell showing the reverse direction with corrected p<0.05 as a partial disconfirmation, not just noise.

  METRIC 2 -- Entropy precondition check (mechanism prerequisite, run BEFORE trusting mediation). For each (model, length_tier) cell, paired Wilcoxon test of entropy_mean(filler) vs entropy_mean(elaboration) matched by seed_problem_id, plus the paired bootstrap CI on the mean difference. This tests whether filler content actually produces higher entropy than elaboration at matched length -- a necessary precondition for the proposed causal mechanism. If entropy does NOT differ between arms while CV does, that is evidence AGAINST attention-entropy mediation specifically (the arms differ in outcome via some other channel), and this must be stated as a distinct finding, not folded silently into the mediation result.

  METRIC 3 -- Bootstrap mediation analysis (tests success criterion 2). Using the per-prompt table (all rows, both arms, all length_tiers, pooled across models as primary analysis + repeated per-model as a robustness/generalization check), fit the Baron-Kenny path regressions: (a) total-effect model: CV ~ length_tier_numeric (or prompt_token_count) [+ content_type as covariate in a secondary spec], record coefficient c and its CI; (b) mediator model: entropy_mean ~ length_tier_numeric [+ content_type], record coefficient a; (c) outcome model with mediator: CV ~ length_tier_numeric + entropy_mean [+ content_type], record coefficient b (mediator's effect on CV controlling for length) and c' (length's direct effect controlling for mediator). Compute indirect effect a*b via 5,000-iteration nonparametric bootstrap resampling seed_problem_id clusters (not individual rows -- this respects the paired/repeated-measures structure and must be justified explicitly in the output), report the 95% percentile bootstrap CI on a*b, and the proportion mediated = (a*b)/c. State the verdict as MEDIATED (CI on a*b excludes 0 and proportion mediated is a meaningfully large, reported fraction -- do not round up small fractions to 'meaningful'), PARTIALLY_MEDIATED (CI excludes 0 but proportion mediated is small, e.g. <20%), or NOT_MEDIATED (CI includes 0). Use standardized (z-scored) predictors/outcomes so a, b, c are comparable in scale, and report both standardized and raw-scale coefficients. Also report each regression's residual diagnostics briefly (heteroscedasticity via Breusch-Pagan on the CV~length model, since CV is right-skewed and variance-of-variance is a known pitfall -- flag if a log or rank transform of CV was needed and rerun the whole mediation pipeline on the transformed CV as a sensitivity check).

  METRIC 4 -- Confound/robustness checks. (a) Verify length manipulation actually varied prompt_token_count as intended per tier (report token-count summary stats per tier x content_type cell; if filler and elaboration prompts are not actually length-matched within a tier, per the experiment's design, flag this as invalidating the 'matched length' claim rather than silently proceeding). (b) Refusal/invalid-answer rate per cell -- if filler prompts produce systematically higher refusal/parse-failure rates than elaboration prompts, note this as a competing explanation for apparent CV differences (since CV is computed only over valid answers, a differential exclusion pattern can bias the comparison) and report CV results both with and without a refusal-rate-matched subsample if the imbalance is large (e.g. >2x difference in refusal rate between arms). (c) Sensitivity of the mediation result to model choice: report a model-comparison table (does mediation hold in each model individually, or only pooled) -- pooled-only mediation with individual-model null results should be flagged as a Simpson's-paradox risk. (d) If attention_entropy (open-weight) and logprob_entropy (closed-model proxy) are both present for any overlapping condition, report their correlation as a proxy-validity check; if the experiment used only one type of model family, state that as a scope limitation rather than omitting the check silently.

  FINAL VERDICT: Combine Metrics 1-4 into an explicit CONFIRMED / PARTIALLY_CONFIRMED / DISCONFIRMED judgment against the hypothesis's stated success criteria (both criterion 1 -- filler>elaboration variance at matched length -- AND criterion 2 -- entropy mediates length->variance -- must hold for full CONFIRMED; either failing but the other holding is PARTIALLY_CONFIRMED; both failing, or CV tracking raw length regardless of content type with no mediating role for entropy, is DISCONFIRMED per the hypothesis's own disconfirmation criteria). Write the full statistical output, per-cell tables, and this verdict to eval_out.json with a machine-readable top-level `verdict` field and a `verdict_rationale` string summarizing which specific sub-tests drove the call.
metrics_justification: >-
  Paired tests (Wilcoxon/bootstrap on within-seed_problem differences) are the correct design because filler and elaboration
  prompts share the same core numeric-reasoning content by construction -- treating them as independent samples would ignore
  this pairing and inflate apparent significance or mask it, and Holm correction is needed because the plan runs many per-cell
  tests. Bootstrap resampling at the seed_problem_id (cluster) level rather than the row level is essential because each seed_problem
  contributes multiple correlated rows (per length_tier, per content_type, and the answer_cv itself is already an aggregate
  over ~20-30 resamples) -- treating rows as independent would understate the true CIs. The Baron-Kenny + bootstrap indirect-effect
  approach directly operationalizes the hypothesis's own stated test ('bootstrap mediation') and produces the two numbers
  the hypothesis's success criteria demand: an indirect-effect CI (does entropy mediate?) and a proportion-mediated (how much
  of the effect?) -- a raw correlation between entropy and CV would not distinguish mediation from mere co-occurrence, which
  is exactly the gap the hypothesis is trying to close relative to the black-box 'Too long; didn't solve' paper. The entropy
  precondition check (Metric 2) exists because mediation analysis can produce a spuriously nonzero indirect effect from noise
  if the arms don't actually differ in entropy; checking this first prevents over-claiming. The confound checks (Metric 4)
  directly address the two most likely ways this evaluation could produce a false positive: (i) filler and elaboration weren't
  actually length-matched as intended, and (ii) differential refusal/invalid-answer rates between arms bias the CV comparison
  independent of any true instability effect -- both are exactly the kind of validity threat a numeric-answer variance study
  is vulnerable to and that the hypothesis's own disconfirmation criteria implicitly require ruling out before accepting mediation.
</artifact_plan>



<available_resources>
<software_constraints>
- Python only implementation
- Python standard library and all popular PyPI packages available (numpy, pandas, scikit-learn, scipy, matplotlib, requests, etc.)
- Local parallelism encouraged: multiprocessing, asyncio, threading — see aii-parallel-computing skill
- LLM API calls must go through OpenRouter only (no direct OpenAI, Anthropic, etc.)
- **HARD LIMIT**: Maximum $10 USD total spend on LLM API calls (OpenRouter). Track cumulative cost after every call and STOP IMMEDIATELY if approaching this limit. Never exceed this budget under any circumstances.
</software_constraints>

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
</available_resources>

<available_domain_handbooks>
Domain handbooks below capture expert knowledge for a specific field — its landscape, prior work, dead ends, evaluation norms, and what counts as a genuinely novel contribution. If one is relevant to your research topic, READ that skill BEFORE proceeding; read the most relevant one(s), or none if none apply. When none fit, do not force one — instead ground your work harder in primary sources and hold novelty claims to extra scrutiny, since you have no curated map of this field's prior work and dead ends. Use it for evaluation metrics, agent orchestration patterns, benchmark design.

- **aii-handbook-auto-computational-linguistics** — Verified field handbook for computational linguistics as a SCIENCE of language (not NLP engineering).
- **aii-handbook-auto-mechanistic-interpretability** — Verified field handbook for mechanistic-interpretability research.
- **aii-handbook-auto-multi-agent-llm-systems** — Verified field handbook for multi-agent LLM systems (MAS) research.
- **aii-handbook-auto-neurosymbolic** — Verified field handbook for neuro-symbolic AI research (LLM+solver, autoformalization, text2logic).
</available_domain_handbooks>

<tool_use>
Maximize parallel tool calls. Parallelize independent operations, only sequentialize dependencies.
- Multiple searches/fetches on different topics → parallel in one turn
- Search then fetch results → sequential (need URLs first)
</tool_use>

<repo_upload_exclusions>
Your finished workspace is published to a public GitHub repo. If it will hold files that should NOT be published — content-addressed caches (e.g. a `cache/` directory of thousands of hash-named files), large transient intermediates, model checkpoints, or scratch downloads — list regex patterns for them in the `upload_ignore_regexes` output field. Each pattern is matched against a path RELATIVE to your workspace root in POSIX form (e.g. `(^|/)cache/`, `(^|/)checkpoints/`). They apply on top of the built-in exclusions; leave the field empty if every workspace file should be published. Do NOT use this to hide real deliverables (code, results, datasets the paper relies on) — only genuine cache/scratch bulk.
</repo_upload_exclusions>

IMPORTANT: Your final response should be at most 300 characters long.

FIRST, add ALL of these to your todo list using your task/todo-tracking tool:

CRITICAL: Todo content must be copied exactly as is written here, with NO CHANGES. These todos are intentionally detailed so that another LLM could read each one without any external context and understand exactly what it has to do.

<todos>
TODO 1. Use aii-json skill's format script with `--input eval_out.json` to generate full, mini, and preview versions. If not in your workspace (see <workspace> above), copy them there. Run 'ls -lh' to verify these three files exist (DO NOT read them).
TODO 2. Apply aii-file-size-limit skill's file size check procedure (100MB limit) to eval_out.json and full_eval_out.json.
TODO 3. Ensure a `pyproject.toml` exists in your workspace with ALL dependencies pinned to the exact versions installed in your .venv (run `.venv/bin/pip freeze` to get them). This is required for reproducibility. The [project] section must include name, version, requires-python, and a dependencies list with pinned versions (e.g. `numpy==2.0.2`, not `numpy>=2.0`).
</todos>

---

Output the result as JSON to: `./.terminal_claude_agent_struct_out.json`

JSON Schema:
```json
{
  "$defs": {
    "EvaluationExpectedFiles": {
      "description": "All expected output files from evaluation artifact.",
      "properties": {
        "script": {
          "description": "Path to eval.py script. Example: 'eval.py'",
          "title": "Script",
          "type": "string"
        },
        "full_output": {
          "description": "Full evaluation JSON file. Example: 'full_eval_out.json'",
          "title": "Full Output",
          "type": "string"
        },
        "mini_output": {
          "description": "Mini evaluation JSON file. Example: 'mini_eval_out.json'",
          "title": "Mini Output",
          "type": "string"
        },
        "preview_output": {
          "description": "Preview evaluation JSON file. Example: 'preview_eval_out.json'",
          "title": "Preview Output",
          "type": "string"
        }
      },
      "required": [
        "script",
        "full_output",
        "mini_output",
        "preview_output"
      ],
      "title": "EvaluationExpectedFiles",
      "type": "object"
    }
  },
  "description": "Evaluation artifact \u2014 structured output + file metadata.\n\nEvaluates both proposed and baseline methods with appropriate metrics.\nProduces eval.py and eval_out.json files.",
  "properties": {
    "title": {
      "default": "",
      "description": "Artifact title in plain, everyday language \u2014 short and jargon-free so a non-expert grasps it at a glance and it fits the run visualizations. Aim for about 4-8 words (~40 characters); describe the content, not a status.",
      "maxLength": 90,
      "minLength": 12,
      "title": "Title",
      "type": "string"
    },
    "layman_summary": {
      "default": "",
      "description": "One-sentence plain-language summary of what this artifact does, accessible to non-experts. Used only in the per-artifact README, not in downstream prompts.",
      "maxLength": 250,
      "minLength": 80,
      "title": "Layman Summary",
      "type": "string"
    },
    "summary": {
      "default": "",
      "description": "Summary for downstream artifacts: what this artifact provides",
      "maxLength": 5000,
      "minLength": 500,
      "title": "Summary",
      "type": "string"
    },
    "out_expected_files": {
      "$ref": "#/$defs/EvaluationExpectedFiles",
      "description": "All output files you created. Must include eval.py script plus full/mini/preview evaluation JSON files."
    },
    "upload_ignore_regexes": {
      "description": "Regex patterns for workspace paths that must NOT be published to the GitHub repo, matched against each file's path relative to this artifact's workspace root (POSIX form, e.g. 'cache/abc.json'). Applied ON TOP OF the deploy step's built-in exclusions. Use this for executor-specific caches, large transient intermediates, or content-addressed blob stores (e.g. a cache/ dir of thousands of hash-named files) that would bloat the repo. Examples: ['(^|/)cache/', '(^|/)\\\\.weight_cache/', '(^|/)checkpoints/']. Leave empty if every workspace file should be published.",
      "items": {
        "type": "string"
      },
      "title": "Upload Ignore Regexes",
      "type": "array"
    }
  },
  "required": [
    "out_expected_files"
  ],
  "title": "EvaluationArtifact",
  "type": "object"
}
```

IMPORTANT: this task is NOT complete until `./.terminal_claude_agent_struct_out.json` exists and contains JSON matching the schema above.
````

### [4] SYSTEM-USER prompt · 2026-08-19 14:18:20 UTC

```
<verification_failed>
Your evaluation output failed verification (attempt 1/10).
</verification_failed>

<file_errors>
MISSING OR UNREADABLE FILES:
  - Missing file: eval.py
  - Missing file: full_eval_out.json
  - Missing file: mini_eval_out.json
  - Missing file: preview_eval_out.json

Fix: Create missing files by running eval.py.
     Required: eval.py, eval_out.json, full_eval_out.json, mini_eval_out.json, preview_eval_out.json
</file_errors>

<task>
FIX ISSUES:
1. Run eval.py to generate missing files
</task>
```

### [5] SKILL-INPUT — aii-json · 2026-08-19 14:18:40 UTC

The agent loaded the **aii-json** skill; its `SKILL.md` (the instructions injected into the agent's context) follows verbatim.

````
---
name: aii-json
description: JSON validation and formatting toolkit. Validate JSON files against schemas for experiment pipelines, and generate full/mini/preview versions of JSON datasets. Use for validating pipeline outputs, checking schema compliance, or creating size-optimized JSON variants.
---

## Contents

- Validating JSON (schema validation against experiment schemas)
- Formatting JSON (generate full/mini/preview versions)

**IMPORTANT - Parallel execution:** GNU `parallel` subshells do NOT inherit `source activate`. Use `export` for variables and **single-quoted** command templates so parallel's subshells can resolve them:
```
export SKILL_DIR="$(git rev-parse --show-toplevel 2>/dev/null || echo /ai-inventor)/.claude/skills/aii-json"
export PY="$SKILL_DIR/../.ability_client_venv/bin/python"
```

---

## Validating JSON

Validate JSON files against predefined schemas for experiment-based hypothesis selection, data collection, solution generation, and evaluation.

### Quick Start

1. Read the schema spec you need to adhere to (e.g., `schemas/exp_eval_sol_out.json`)
2. Create your output file following that schema structure
3. Validate:

```bash
SKILL_DIR="$(git rev-parse --show-toplevel 2>/dev/null || echo /ai-inventor)/.claude/skills/aii-json" && \
$SKILL_DIR/../.ability_client_venv/bin/python $SKILL_DIR/scripts/aii_json_validate_schema.py --format exp_eval_sol_out --file /path/to/eval_out.json
```

### Script: aii_json_validate_schema.py

**Example input:**
```bash
SKILL_DIR="$(git rev-parse --show-toplevel 2>/dev/null || echo /ai-inventor)/.claude/skills/aii-json" && \
$SKILL_DIR/../.ability_client_venv/bin/python $SKILL_DIR/scripts/aii_json_validate_schema.py --format exp_eval_sol_out --file /tmp/eval_out.json
```

**Parallel execution (multiple validations):**

IMPORTANT: When validating multiple files, use GNU parallel instead of separate Bash tool calls:
```bash
export SKILL_DIR="$(git rev-parse --show-toplevel 2>/dev/null || echo /ai-inventor)/.claude/skills/aii-json" && \
export PY="$SKILL_DIR/../.ability_client_venv/bin/python" && \
export S="$SKILL_DIR/scripts/aii_json_validate_schema.py" && \
parallel -j 50 -k --group --will-cite '$PY $S --format {1} --file {2}' ::: 'exp_sel_data_out' 'exp_gen_sol_out' 'exp_eval_sol_out' :::+ '/tmp/full_data_out.json' '/tmp/method_out.json' '/tmp/eval_out.json'
```

**Example output (success):**
```
Validating: aii_json_validate_schema.py
Format: exp_eval_sol_out

✓ Validation PASSED
```

**Example output (failure):**
```
Validating: aii_json_validate_schema.py
Format: exp_sel_data_out

✗ Validation FAILED

Errors:
  Path: datasets → 0 → examples → 0
  Error: 'output' is a required property
  Validator: required
```

**Parameters:**

`--format` (required)
- Format type to validate against
- Determines which schema to use

`--file` (required)
- Path to JSON file to validate
- Must be valid JSON
- **Always pass an absolute path.** Relative paths resolve from the
  ability server's CWD (typically ``/ai-inventor/aii_server``), not from
  your agent workspace, so ``data_out/x.json`` will silently look in the
  wrong directory and fail with "Could not load JSON file". The validate
  endpoint also accepts a ``workspace_dir`` arg if you need to keep a
  relative path — pass your workspace path there.

**Tips:**
- Fix errors in your JSON and rerun validation until it passes

### Schema Files

Schemas are stored in `.claude/skills/aii-json/schemas/`:

**Hypothesis Selection & Evaluation:**
- `sel_hypo_out.json` - Hypothesis Selection output (all hypotheses with selected flags)
- `feasibility_eval_all.json` - All hypotheses with feasibility scores
- `feasibility_eval_top.json` - Top 5 most feasible hypotheses
- `novelty_research_one.json` - Single hypothesis novelty research arguments with citations
- `novelty_eval_all.json` - All hypotheses with novelty scores
- `novelty_eval_top.json` - Single best selected hypothesis

**Experiment Pipeline:**
- `exp_sel_data_out.json` - Experiment Data Selection format
- `exp_gen_sol_out.json` - Experiment Solution Generation format
- `exp_eval_sol_out.json` - Experiment Solution Evaluation format

---

## Formatting JSON

Generate three size-optimized versions of a JSON file for efficient development and preview:
- **full**: Identical to original (all data)
- **mini**: First 3 items only (for quick testing)
- **preview**: Mini + all strings truncated to 200 chars (for quick inspection)

### Quick Start

```bash
SKILL_DIR="$(git rev-parse --show-toplevel 2>/dev/null || echo /ai-inventor)/.claude/skills/aii-json" && \
$SKILL_DIR/../.ability_client_venv/bin/python $SKILL_DIR/scripts/aii_json_format_mini_preview.py --input method_out.json
```

### Script: aii_json_format_mini_preview.py

**Example input:**
```bash
SKILL_DIR="$(git rev-parse --show-toplevel 2>/dev/null || echo /ai-inventor)/.claude/skills/aii-json" && \
$SKILL_DIR/../.ability_client_venv/bin/python $SKILL_DIR/scripts/aii_json_format_mini_preview.py --input method_out.json
```

**Parallel execution (multiple files):**

IMPORTANT: When formatting multiple files, use GNU parallel instead of separate Bash tool calls:
```bash
export SKILL_DIR="$(git rev-parse --show-toplevel 2>/dev/null || echo /ai-inventor)/.claude/skills/aii-json" && \
export PY="$SKILL_DIR/../.ability_client_venv/bin/python" && \
export S="$SKILL_DIR/scripts/aii_json_format_mini_preview.py" && \
parallel -j 50 -k --group --will-cite '$PY $S --input {}' ::: 'full_data_out.json' 'method_out.json' 'eval_out.json'
```

**Example output:**
```
Generated 3 versions:
  Full (50 items): /path/to/full_method_out.json
  Mini (3 items): /path/to/mini_method_out.json
  Preview (3 items, truncated): /path/to/preview_method_out.json
```

**Parameters:**

`--input` (required)
- Path to input JSON file
- Must have a top-level array
- Example: `method_out.json`, `full_data_out.json`

`--output-dir` (optional)
- Output directory for generated files
- Default: same directory as input file
- Files are prefixed with `full_`, `mini_`, `preview_`

**Output Files:**

All three files use the same base name with different prefixes:
- `full_{basename}.json` - Complete dataset (identical to original)
- `mini_{basename}.json` - First 3 array items only
- `preview_{basename}.json` - First 3 items with strings truncated to 200 chars

**Tips:**
- Input JSON must have a top-level array structure
- String truncation is recursive (applies to nested objects and arrays)
- Use preview files for quick inspection without reading large datasets
- Use mini files for developing/testing code before running on full dataset

**If the script fails** with a connection error (ability server not running): create a local `.venv`, install server deps from `server_requirements.txt` into it, then import the `@aii_ability` function from the script and call it directly — bypassing the server:
```bash
uv venv .venv --python=3.12 && uv pip install --python=.venv/bin/python -r "$SKILL_DIR/scripts/server_requirements.txt"
```
````

### [6] SYSTEM-USER prompt · 2026-08-19 14:24:40 UTC

```
<verification_failed>
Your evaluation output failed verification (attempt 2/10).
</verification_failed>

<schema_errors>
JSON SCHEMA / CODE VALIDATION ERRORS:
  - full_eval_out.json: No eval_* metrics found in any of the sampled examples (at least one required)
  - mini_eval_out.json: No eval_* metrics found in any of the sampled examples (at least one required)
  - preview_eval_out.json: No eval_* metrics found in any of the sampled examples (at least one required)

Fix: Your JSON must follow the datasets-grouped exp_eval_sol_out.json schema:
     {
       "metrics_agg": {"<metric_name>": 0.85, ...},  // REQUIRED, at least one metric
       "datasets": [
         {
           "dataset": "dataset_name",
           "examples": [
             {
               "input": "...", "output": "...",
               "metadata_fold": 2,
               "predict_<method>": "...",
               "eval_<metric>": 0.9
             }
           ]
         }
       ]
     }

     NO 'split', 'dataset', or 'context' per-example. Dataset name at group level.
     Metadata via flat metadata_<name> fields.
     Read exp_eval_sol_out.json schema in aii-json skill.
</schema_errors>

<content_warnings>
CONTENT QUALITY ISSUES:
  - full_eval_out.json: Only 1 total examples (expected at least 50)

Fix: Ensure metrics_agg has values and each example has eval_* metrics.
</content_warnings>

<task>
FIX ISSUES:
2. Fix eval.py to produce correct JSON schema
3. Use aii-json skill validation to verify
</task>
```

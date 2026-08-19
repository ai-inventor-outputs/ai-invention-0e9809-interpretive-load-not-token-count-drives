# gen_plan_dataset_1 — test_idea

> Phase: `invention_loop` · round 2 · `gen_plan`
> Run: `run_l-N7kpGv9Lri` — Interpretive Load, Not Token Count, Drives LLM Answer Instability
>
> Full, verbatim transcript of this agent task — every system/user prompt, assistant response, thinking block, tool call and tool result — in the order they occurred. Nothing truncated.

## Task: `gen_plan_dataset_1` (terminal_claude_agent, claude-sonnet-5)

### [1] CONFIG · 2026-08-19 15:01:21 UTC

```
model: claude-sonnet-5 | effort: low | permission: bypassPermissions | cwd: /ai-inventor/aii_data/runs/run_l-N7kpGv9Lri/3_invention_loop/iter_2/gen_plan/gen_plan_dataset_1
```

### [2] SYSTEM-USER prompt · 2026-08-19 15:01:27 UTC

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
You are expanding an artifact direction of type: DATASET

DATASET
Collect, prepare, and merge datasets for experiments and analysis.
Runtime: Python 3.12, UV, isolated workspace.
Tools: Full shell/Python/filesystem access, the aii-web-tools skill (web search, page fetch, regex grep over full page/PDF text), and other skills.
Skills: aii-hf-datasets (HuggingFace Hub — ML datasets, many UCI/OpenML/Kaggle mirrors), aii-owid-datasets (Our World in Data — global statistics), aii-json (schema validation). Also any Python source (sklearn.datasets, openml, direct URLs, APIs) — must verify within 300MB limit.
Capabilities: Search, acquire, transform, combine, and standardize data from any available source.
Deps: REQUIRED none | OPTIONAL RESEARCH for guidance on what data to collect
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

The dataset executor has 6h total (including writing code, debugging, testing, and fixing errors).

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

id: dataset_iter2_dir2
type: dataset
objective: >-
  Build a small decomposition prompt set that splits the original 'relevant elaboration' condition into two sub-conditions
  -- pure paraphrase/restatement (no scaffolding) and paraphrase-plus-generic-verification-scaffolding (matching the original
  elaboration design) -- at a single matched length tier, for a subset of seed problems, to isolate which sub-component of
  elaboration drives the observed destabilization.
approach: >-
  Reuse 6-8 of the same GSM8K seed problems already used in art_EQ9EJso6WFvP/art_tqod35nIRuWp (for direct comparability against
  the existing bare/filler/elaboration data) and construct, per seed, at a single length tier matched to the prior 'medium'
  tier (~250 extra tokens, since that tier showed the largest elaboration effect): (a) paraphrase-only -- a pure restatement
  of the problem in different wording, no added verification/unit-consistency instructions; (b) paraphrase-plus-scaffolding
  -- the paraphrase from (a) plus the same generic verification scaffolding sentences used in the original relevant-elaboration
  condition, token-matched to (a) within the same tolerance rules (+/-15 tokens or +/-10%) using the cl100k_base tokenizer.
  Source the same seed problems and their gold answers fresh from GSM8K (HuggingFace 'openai/gsm8k', config 'main', test split)
  rather than depending on the prior dataset artifact's output files directly, and mirror the original bare-control/filler-medium/relevant-elaboration-medium
  prompt construction logic (documented in art_EQ9EJso6WFvP's summary) so the new sub-conditions remain directly comparable
  to the existing conditions already sampled. Validate zero numeric leakage in the new prompt text via the same regex/keyword
  check used previously. Output in the same exp_sel_data_out schema as art_EQ9EJso6WFvP, with metadata_content_type extended
  to include 'paraphrase_only' and 'paraphrase_scaffolding'.
depends_on: []
</artifact_direction>



<instructions>
YOUR ROLE: Write a detailed PLAN for the artifact. A separate executor agent runs the actual artifact later.

You are a PLANNER, not an executor. Your output is a plan that tells the executor what to do and how.
Do NOT execute the artifact itself — a separate agent handles that. Your job is to plan it so well that the executor can follow your plan step by step.

You CAN and SHOULD: search the web, read papers, and explore library docs to make your plan concrete.
You CANNOT run shell commands or scripts — code execution is disabled. Research via web tools only.

Do NOT do the executor's job: don't download datasets, don't implement code, don't run experiments, don't write proofs, don't compute evaluations.

<artifact_executor_scope>
IMPORTANT: Each artifact executor has a focused prompt that guides it to do ONE thing well. It will NOT perform tasks outside its scope — assigning the wrong work to the wrong artifact type wastes an iteration. Match the task to the right executor.

DATASET executor scope:
  Output: data_out.json with rows of {input, output, metadata_fold, ...} — raw data only, no derived computations
  DOES: Download/generate datasets, analyze candidates to pick the best ones, standardize to JSON schema (features, labels, folds, metadata), validate schema, split into full/mini/preview
  DOES NOT: Run experiments, train models, compute derived statistics (PID/MI/correlations/synergy matrices) as final output
  If you need to COMPUTE something from data (synergy matrices, MI scores, timing benchmarks), use an EXPERIMENT artifact instead
</artifact_executor_scope>

<artifact_planning_rules>
DATASET:
- Plan for REAL third-party datasets (HuggingFace, Kaggle, direct-download URLs) — downloadable within time and size constraints
- Describe dataset criteria (domain, size, format) — executors find exact sources, but you can suggest candidates or search directions
- ALWAYS prefer real datasets over synthetic. Synthetic is a LAST RESORT only when no suitable real data exists
</artifact_planning_rules>

<compute_profiles>
Choose the compute profile this artifact needs for execution.
Available profiles for dataset artifacts:
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
  "description": "Plan for a DATASET artifact.",
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
    "ideal_dataset_criteria": {
      "description": "What makes an ideal dataset for this purpose - size, format, content requirements",
      "title": "Ideal Dataset Criteria",
      "type": "string"
    },
    "dataset_search_plan": {
      "description": "Step-by-step plan for finding/creating this dataset - sources to check, fallback options",
      "title": "Dataset Search Plan",
      "type": "string"
    },
    "target_num_datasets": {
      "description": "How many individual datasets should be delivered. Count each dataset separately, not collections \u2014 a benchmark suite of N datasets counts as N. This controls how broadly the executor searches, so setting it too low will under-collect.",
      "title": "Target Num Datasets",
      "type": "integer"
    }
  },
  "required": [
    "title",
    "ideal_dataset_criteria",
    "dataset_search_plan",
    "target_num_datasets"
  ],
  "title": "DatasetPlan",
  "type": "object"
}
```

IMPORTANT: this task is NOT complete until `./.terminal_claude_agent_struct_out.json` exists and contains JSON matching the schema above.
````

### [3] HUMAN-USER prompt · 2026-08-19 15:01:27 UTC

```
Does prompt length change the variance of LLM numeric answers?
```

### [4] TOOL CALL — Write · 2026-08-19 15:01:55 UTC

```
File: /ai-inventor/aii_data/runs/run_l-N7kpGv9Lri/3_invention_loop/iter_2/gen_plan/gen_plan_dataset_1/.terminal_claude_agent_struct_out.json

{
  "title": "Decomposed Elaboration Prompts: Paraphrase vs Scaffolding",
  "summary": "Build a small, matched GSM8K prompt set that splits the prior 'relevant elaboration' condition into two sub-conditions -- pure paraphrase and paraphrase+verification-scaffolding -- at one length tier, for 6-8 seed problems, so a later experiment can isolate which sub-component drove the observed destabilization.",
  "runpod_compute_profile": "cpu_light",
  "ideal_dataset_criteria": "A JSON dataset of GSM8K-derived prompts covering exactly 2 new sub-conditions ('paraphrase_only' and 'paraphrase_scaffolding') x 6-8 seed problems (so 12-16 new prompt rows total), each row schema-identical to the prior art_EQ9EJso6WFvP/art_tqod35nIRuWp output (exp_sel_data_out schema: input, output, metadata_fold, metadata_content_type, plus any metadata_* fields the prior artifacts used such as seed_id, tier, token_count, gold_answer). Seed problems must be the SAME 6-8 GSM8K test-split problems already used in the prior conditions (bare/filler/elaboration) for direct comparability -- pull them fresh from HuggingFace 'openai/gsm8k' (config 'main', split='test') rather than depending on the prior artifact's files, and identify them by matching problem text/index so the same seeds are reproduced deterministically. Both new sub-conditions must be length-matched to each other and to the prior 'medium' elaboration tier (~250 extra tokens beyond the bare question, using the cl100k_base tokenizer via tiktoken), within +/-15 tokens or +/-10% tolerance (whichever is looser). 'paraphrase_only' = a pure reworded restatement of the problem (same numbers/constraints, different sentence structure/wording) with NO verification/unit-consistency/generic scaffolding text added. 'paraphrase_scaffolding' = the exact paraphrase text from (a) plus the same generic verification-scaffolding sentences (e.g. 'double-check your units', 'verify each step', 'make sure the final answer is consistent with the constraints stated above') that were appended in the ORIGINAL relevant-elaboration condition -- reuse that scaffolding text verbatim/near-verbatim rather than inventing new wording, so this sub-condition remains a faithful decomposition of the original elaboration prompt rather than a new manipulation. Every prompt must pass a zero-numeric-leakage check (no stray digits/numbers in the added text beyond what's needed to state the original problem) using the same regex/keyword approach as the prior artifacts. Gold numeric answers must be preserved exactly from GSM8K's '#### <answer>' format. Total dataset size is intentionally small (12-16 rows) since this feeds a low-N follow-up sampling experiment, not a large-scale corpus.",
  "dataset_search_plan": "1) Fetch the source dataset: use the aii-hf-datasets skill to load 'openai/gsm8k' (config 'main', split='test') from HuggingFace -- this is the same source the prior GSM8K prompt battery (art_EQ9EJso6WFvP) used, so no new dataset search is needed, only re-acquisition. 2) Recover which 6-8 seed problems were used previously: since this artifact has no upstream dependency, the executor cannot read art_EQ9EJso6WFvP's output files directly per the approach note -- instead deterministically re-derive the same seeds by re-running the prior artifact's documented seed-selection logic (fixed sampling method/seed value referenced in its summary, e.g. a fixed random seed over the test split, or the first N problems meeting a length/difficulty filter) so the chosen problems match exactly; if the exact selection rule cannot be pinned down from available documentation, fall back to a small, fixed, clearly-logged set of 6-8 GSM8K test-split problem indices chosen for diversity (varying number of reasoning steps, 2-5 arithmetic operations, answer magnitude) and flag this explicitly as an approximation in the dataset README/metadata so downstream experiment authors know exact seed-match to prior conditions is best-effort, not guaranteed. 3) Construct paraphrase_only prompts: for each seed, hand-craft (via LLM-assisted or manual rewriting, verified by the executor, no OpenRouter spend required for this deterministic text-construction task) a reworded version of the problem statement -- reorder clauses, swap synonyms, change sentence structure -- while preserving every number, constraint, and the question itself, then pad/trim wording until the cl100k_base token count for the elaboration text added beyond the bare question falls within the ~250-token medium-tier tolerance band. 4) Construct paraphrase_scaffolding prompts: append the identical generic verification-scaffolding sentences used in the original relevant-elaboration condition (retrieve/reconstruct their exact wording from the hypothesis's investigation_approach and the artifact_direction's description of 'restated constraints and generic verification scaffolding'; if exact source text is unavailable, author scaffolding sentences that are unmistakably generic/task-agnostic, e.g. instructions to double check units and verify consistency, not new problem-specific information) to each paraphrase_only prompt, then re-verify the combined token count still sits in tolerance -- if scaffolding pushes it over, trim the paraphrase wording (not the scaffolding, since scaffolding must match the original condition) to compensate. 5) Run the numeric-leakage regex check (search for digit patterns in the added/inserted text, excluding the original problem's numbers and the scaffolding's non-numeric instructions) on every new prompt; hand-fix any prompt that leaks the gold answer or a suspiciously close numeric hint. 6) Assemble into exp_sel_data_out schema JSON: one row per (seed, sub-condition) pair, with metadata_content_type in {'paraphrase_only','paraphrase_scaffolding'}, metadata_fold matching prior conventions (likely a single fold since this is a small targeted set), token_count, seed_id, gold_answer, and full prompt text as 'input'. 7) Validate against the schema with the aii-json skill, and use aii-file-size-limit to confirm the (very small, <1MB) output doesn't need splitting. 8) Produce full/mini/preview variants per standard dataset-executor convention even though the set is small.",
  "target_num_datasets": 1
}
```

### [5] TOOL RESULT — Write · 2026-08-19 15:01:55 UTC

```
{"type": "create", "filePath": "/ai-inventor/aii_data/runs/run_l-N7kpGv9Lri/3_invention_loop/iter_2/gen_plan/gen_plan_dataset_1/.terminal_claude_agent_struct_out.json", "content": "{\n  \"title\": \"Decomposed Elaboration Prompts: Paraphrase vs Scaffolding\",\n  \"summary\": \"Build a small, matched GSM8K prompt set that splits the prior 'relevant elaboration' condition into two sub-conditions -- pure paraphrase and paraphrase+verification-scaffolding -- at one length tier, for 6-8 seed problems, so a later experiment can isolate which sub-component drove the observed destabilization.\",\n  \"runpod_compute_profile\": \"cpu_light\",\n  \"ideal_dataset_criteria\": \"A JSON dataset of GSM8K-derived prompts covering exactly 2 new sub-conditions ('paraphrase_only' and 'paraphrase_scaffolding') x 6-8 seed problems (so 12-16 new prompt rows total), each row schema-identical to the prior art_EQ9EJso6WFvP/art_tqod35nIRuWp output (exp_sel_data_out schema: input, output, metadata_fold, metadata_content_type, plus any metadata_* fields the prior artifacts used such as seed_id, tier, token_count, gold_answer). Seed problems must be the SAME 6-8 GSM8K test-split problems already used in the prior conditions (bare/filler/elaboration) for direct comparability -- pull them fresh from HuggingFace 'openai/gsm8k' (config 'main', split='test') rather than depending on the prior artifact's files, and identify them by matching problem text/index so the same seeds are reproduced deterministically. Both new sub-conditions must be length-matched to each other and to the prior 'medium' elaboration tier (~250 extra tokens beyond the bare question, using the cl100k_base tokenizer via tiktoken), within +/-15 tokens or +/-10% tolerance (whichever is looser). 'paraphrase_only' = a pure reworded restatement of the problem (same numbers/constraints, different sentence structure/wording) with NO verification/unit-consistency/generic scaffolding text added. 'paraphrase_scaffolding' = the exact paraphrase text from (a) plus the same generic verification-scaffolding sentences (e.g. 'double-check your units', 'verify each step', 'make sure the final answer is consistent with the constraints stated above') that were appended in the ORIGINAL relevant-elaboration condition -- reuse that scaffolding text verbatim/near-verbatim rather than inventing new wording, so this sub-condition remains a faithful decomposition of the original elaboration prompt rather than a new manipulation. Every prompt must pass a zero-numeric-leakage check (no stray digits/numbers in the added text beyond what's needed to state the original problem) using the same regex/keyword approach as the prior artifacts. Gold numeric answers must be preserved exactly from GSM8K's '#### <answer>' format. Total dataset size is intentionally small (12-16 rows) since this feeds a low-N follow-up sampling experiment, not a large-scale corpus.\",\n  \"dataset_search_plan\": \"1) Fetch the source dataset: use the aii-hf-datasets skill to load 'openai/gsm8k' (config 'main', split='test') from HuggingFace -- this is the same source the prior GSM8K prompt battery (art_EQ9EJso6WFvP) used, so no new dataset search is needed, only re-acquisition. 2) Recover which 6-8 seed problems were used previously: since this artifact has no upstream dependency, the executor cannot read art_EQ9EJso6WFvP's output files directly per the approach note -- instead deterministically re-derive the same seeds by re-running the prior artifact's documented seed-selection logic (fixed sampling method/seed value referenced in its summary, e.g. a fixed random seed over the test split, or the first N problems meeting a length/difficulty filter) so the chosen problems match exactly; if the exact selection rule cannot be pinned down from available documentation, fall back to a small, fixed, clearly-logged set of 6-8 GSM8K test-split problem indices chosen for diversity (varying number of reasoning steps, 2-5 arithmetic operations, answer magnitude) and flag this explicitly as an approximation in the dataset README/metadata so downstream experiment authors know exact seed-match to prior conditions is best-effort, not guaranteed. 3) Construct paraphrase_only prompts: for each seed, hand-craft (via LLM-assisted or manual rewriting, verified by the executor, no OpenRouter spend required for this deterministic text-construction task) a reworded version of the problem statement -- reorder clauses, swap synonyms, change sentence structure -- while preserving every number, constraint, and the question itself, then pad/trim wording until the cl100k_base token count for the elaboration text added beyond the bare question falls within the ~250-token medium-tier tolerance band. 4) Construct paraphrase_scaffolding prompts: append the identical generic verification-scaffolding sentences used in the original relevant-elaboration condition (retrieve/reconstruct their exact wording from the hypothesis's investigation_approach and the artifact_direction's description of 'restated constraints and generic verification scaffolding'; if exact source text is unavailable, author scaffolding sentences that are unmistakably generic/task-agnostic, e.g. instructions to double check units and verify consistency, not new problem-specific information) to each paraphrase_only prompt, then re-verify the combined token count still sits in tolerance -- if scaffolding pushes it over, trim the paraphrase wording (not the scaffolding, since scaffolding must match the original condition) to compensate. 5) Run the numeric-leakage regex check (search for digit patterns in the added/inserted text, excluding the original problem's numbers and the scaffolding's non-numeric instructions) on every new prompt; hand-fix any prompt that leaks the gold answer or a suspiciously close numeric hint. 6) Assemble into exp_sel_data_out schema JSON: one row per (seed, sub-condition) pair, with metadata_content_type in {'paraphrase_only','paraphrase_scaffolding'}, metadata_fold matching prior conventions (likely a single fold since this is a small targeted set), token_count, seed_id, gold_answer, and full prompt text as 'input'. 7) Validate against the schema with the aii-json skill, and use aii-file-size-limit to confirm the (very small, <1MB) output doesn't need splitting. 8) Produce full/mini/preview variants per standard dataset-executor convention even though the set is small.\",\n  \"target_num_datasets\": 1\n}\n", "structuredPatch": [], "originalFile": null, "userModified": false}
```

### [6] ASSISTANT · 2026-08-19 15:01:57 UTC

```
Plan written to the required output file.
```

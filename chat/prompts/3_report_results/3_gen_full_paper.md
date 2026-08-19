# gen_full_paper — report_results

> Phase: `gen_paper_repo` · `gen_full_paper`
> Run: `run_l-N7kpGv9Lri` — Interpretive Load, Not Token Count, Drives LLM Answer Instability
>
> Full, verbatim record of every prompt the AI Inventor pipeline gave this agent — system-user, human-user and skill-input — in the order they landed. Nothing truncated.

## Task: `gen_full_paper` (terminal_claude_agent)

### [1] SYSTEM-USER prompt · 2026-08-19 16:45:51 UTC

````
<research_methodology>
Write like an experienced academic. Reviewers judge both the science and the writing.

- Claims must be proportional to evidence. Choose verbs carefully — "demonstrate," "observe," and "hypothesize" mean different things.
- Every result needs: what was measured, on what data, the numbers, and what they mean.
- Methodology must be specific enough to reproduce. Related work must be organized by theme, not a literature dump.
- State limitations honestly. Avoid both overclaiming and excessive hedging.
</research_methodology>

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
Your workspace: `/ai-inventor/aii_data/runs/run_l-N7kpGv9Lri/4_gen_paper_repo/_4_assemble_paper/paper/workspace`

CRITICAL: Every file you create, write, or save MUST be inside this workspace directory (subdirectories OK). You MUST NOT write files anywhere outside this path — external paths are READ-ONLY. Use absolute paths for all file operations.

EVERY file write MUST start with `/ai-inventor/aii_data/runs/run_l-N7kpGv9Lri/4_gen_paper_repo/_4_assemble_paper/paper/workspace/`:
GOOD: `/ai-inventor/aii_data/runs/run_l-N7kpGv9Lri/4_gen_paper_repo/_4_assemble_paper/paper/workspace/file.py`, `/ai-inventor/aii_data/runs/run_l-N7kpGv9Lri/4_gen_paper_repo/_4_assemble_paper/paper/workspace/results/out.json`
BAD: `/tmp/file.py`, `~/output.json`, `./file.py`, any path outside the workspace
</workspace>

<task>
Create a publication-ready top-conference LaTeX paper with BibTeX from <paper_text> and <available_figures>, compile to PDF.
</task>

<tool_use>
Maximize parallel tool calls. Parallelize independent operations, only sequentialize dependencies.
- Multiple searches/fetches on different topics → parallel in one turn
- Search then fetch results → sequential (need URLs first)
</tool_use>

<paper_text>
title: Interpretive Load, Not Token Count, Drives LLM Answer Instability
abstract: >-
  Practitioners assembling long LLM prompts -- retrieved documents, exemplars, chain-of-thought scaffolding -- often cannot
  shorten them, so a mechanistic account of why length destabilizes outputs matters more than the correlational fact that
  it does. We test a content-agnostic attention-dilution account: if instability is driven purely by spreading a fixed attention
  budget over more tokens, then irrelevant filler and relevant elaboration should destabilize numeric answers equally at matched
  token count. Using a length-and-content-matched GSM8K prompt battery (126 variants; filler and relevant-elaboration content
  crossed with three length tiers, token-matched within 2% per tier) sampled 20 times each from three same-provider OpenAI-hosted
  models (5,589/6,720 completions, $2.07), we find the opposite pattern: relevant elaboration elevates answer coefficient
  of variation (CV) 60-71% above token-matched filler at every tier, while filler CV stays within 0.02-0.11 of the bare-question
  baseline even at ~650 extra tokens. A dedicated re-analysis of this data with seed-clustered bootstrap confidence intervals
  (10,000 resamples, 16 seeds) confirms the elaboration-minus-filler CV gap is positive and CI-excluding-zero when pooled
  across tiers (+0.195, 95% CI [0.091, 0.319], paired Wilcoxon p=3.7e-4) and at the medium tier individually (+0.350, CI [0.098,
  0.666]), though the short and long tiers individually cross zero, so per-tier significance is not uniform. A logprob-entropy
  proxy correlates with CV at the individual (prompt, model) cell level (n=332; Pearson r=0.284, 95% cluster-bootstrap CI
  [0.150, 0.407]), a substantially weaker and more defensible relationship than the r=0.75 condition-mean correlation reported
  in an earlier draft of this analysis. A follow-up decomposition experiment isolating pure problem restatement from restatement-plus-verification-scaffolding
  shows the destabilizing effect concentrates in the restatement component (+0.103 CV over token-matched filler) and is largely
  offset, not compounded, by adding scaffolding language (-0.101 CV), refining -- but not fully validating -- the paper's
  competing-interpretation mechanism. We report these results, their confidence intervals, and their remaining construct-validity
  limitations candidly, and argue the practical implication survives the added rigor: content-blind prompt compression targets
  the wrong lever, and auditing redundant restatement of task constraints is a more targeted, actionable mitigation than shortening
  prompts indiscriminately.
paper_text: |-
  # Introduction

  Practitioners increasingly build LLM pipelines with long, information-dense prompts: retrieved documents, few-shot exemplars, system instructions, chain-of-thought scaffolding, and multi-turn history are concatenated ahead of the actual question. A recent large-scale study on hard mathematics problems, "Too long; didn't solve" [1], documents that prompt and solution length correlates with degraded and less consistent model performance, but explicitly treats this as an empirical correlation without proposing a causal mechanism. Knowing *that* length destabilizes answers is of limited practical use without knowing *why*: if the mechanism is a generic, content-agnostic dilution of the model's attention across more tokens, then any length reduction should help equally; if the mechanism is instead specific to what the added tokens say, then indiscriminate context compression is the wrong lever, and prompt engineering should instead target the *kind* of added content.

  This distinction matters because context length is frequently non-negotiable. Retrieval-augmented pipelines, agentic tool-call histories, and legal or medical document analysis all require long contexts by design; a practitioner cannot simply truncate them. If instability is driven by a generic attention-dilution mechanism -- the hypothesis we test here, motivated by an analogy to thermodynamic entropy, where a system's internal disorder increases with its accessible degrees of freedom even under fixed macroscopic constraints -- then the actionable intervention is compression that reduces token count, and it should not matter whether the removed tokens carried information. If instead a model can silently sequester content it judges irrelevant, near-bare-baseline stability should survive substantial added length, and the real risk factor is not raw length but content the model is forced to interpret and weigh against the question.

  Prior explanations for output instability under long contexts have largely focused on *retrieval failure* -- where in the context relevant information sits, and how reliably the model can find it [2] -- rather than on *sampling-level answer variance* to a numeric question whose answer-bearing content is fixed and present. Separately, attention-entropy diagnostics have recently been used as an engineering signal for adaptive compute allocation during long-context inference [3], but as a routing tool for controlling cost, not as a candidate explanatory variable for output-level instability. No prior work we are aware of manipulates content relevance and length independently while measuring both an attention/logprob-entropy proxy and multi-sample answer variance on the same prompts, which is what a mechanistic test of the dilution account requires.

  We construct a length-matched, content-manipulated prompt set built from GSM8K [4] grade-school arithmetic problems, generate multiple stochastic completions per prompt across three same-provider GPT models, and measure both numeric-answer instability (coefficient of variation, CV, across 20 samples) and a logprob-derived entropy proxy for each of seven content-type by length-tier conditions (bare control; filler and relevant-elaboration at short, medium, and long tiers). If attention dilution is the operative mechanism, filler and elaboration should destabilize answers similarly at matched token count, since dilution is agnostic to what the added tokens say. We instead find a sharp split, and this iteration goes further than reporting it: a dedicated re-analysis with seed-clustered bootstrap confidence intervals confirms the split survives at the pooled level and at the medium tier, but not uniformly at every individual tier as an earlier draft of this paper claimed on point estimates alone; a cell-level (rather than seven-condition-mean) correlation between the entropy proxy and CV is positive but far weaker than the earlier draft's headline number; and a targeted follow-up experiment decomposing "relevant elaboration" into pure restatement versus restatement-plus-scaffolding shows the destabilizing effect is concentrated in redundant restatement itself, not generic verification language. This is not the confirmation the attention-dilution hypothesis predicted, but it is a specific, statistically qualified, and actionable finding in its own right -- one that redirects the search for the destabilization mechanism from "how much text" to "how much of the text restates or competes with the question's own constraints."

  [FIGURE:fig_overview]

  ## Summary of Contributions

  - We build and release a length-and-content-matched numeric-reasoning prompt battery (126 GSM8K-derived variants: 1 bare control plus relevant-elaboration and irrelevant-filler content crossed with 3 length tiers, per seed problem) with token counts matched within 2% between content types at every tier and a verified zero-numeric-leakage filler pool \footnote{Code: \url{https://github.com/ai-inventor-outputs/ai-invention-0e9809-interpretive-load-not-token-count-drives/tree/main/round-1/dataset-1}} (Section 3.1).
  - We report a controlled, multi-model measurement of prompt-length effects on numeric-answer sampling variance across 5,589 completions from three same-provider GPT models, isolating content type (relevant vs. irrelevant) from length tier for the first time in this setting \footnote{Code: \url{https://github.com/ai-inventor-outputs/ai-invention-0e9809-interpretive-load-not-token-count-drives/tree/main/round-1/experiment-1}} (Section 4).
  - We re-analyze this data with seed-clustered bootstrap confidence intervals and paired significance tests rather than point estimates alone \footnote{Code: \url{https://github.com/ai-inventor-outputs/ai-invention-0e9809-interpretive-load-not-token-count-drives/tree/main/round-2/evaluation-1}}: the pooled elaboration-minus-filler CV gap is +0.195 (95% CI [0.091, 0.319], Wilcoxon p=3.7e-4, n=16 seeds), positive and CI-excluding-zero at the medium tier (+0.350, CI [0.098, 0.666]) but not individually significant at the short or long tiers, directly qualifying the pure content-agnostic attention-dilution account without over-claiming uniform significance (Section 4.2).
  - We downgrade the entropy-CV relationship from an earlier draft's condition-mean correlation (r=0.75, n=7) to a cell-level correlation over all 332 (prompt, model) rows (r=0.284, 95% cluster-bootstrap CI [0.150, 0.407], surviving within each content-type subset), a smaller but statistically defensible effect (Section 4.3).
  - We report a targeted decomposition experiment isolating pure problem restatement from restatement-plus-verification-scaffolding at matched length: restatement alone raises mean CV by +0.103 over token-matched filler, while adding scaffolding language on top of restatement does not compound this and instead nets -0.101, showing the destabilizing effect of "relevant elaboration" concentrates in redundant restatement rather than generic verification instructions \footnote{Code: \url{https://github.com/ai-inventor-outputs/ai-invention-0e9809-interpretive-load-not-token-count-drives/tree/main/round-2/experiment-1}} (Section 4.4).

  # Related Work

  **Length and reliability of LLM outputs.** Cabrera and Saxton-Knight [1] introduce a 607-problem dataset of expert-authored hard mathematics problems and show that structural length of the problem statement and its solution correlates with empirical difficulty and failure rate across state-of-the-art models, explicitly stopping short of a causal account. Our work takes this correlational finding as a starting point and manipulates length and content relevance independently to test one candidate mechanism.

  **Positional and retrieval effects in long contexts.** Liu et al. [2] show that retrieval accuracy over long contexts is highest when relevant information sits at the beginning or end of the context and degrades in the middle ("lost in the middle"), a *where* effect on whether relevant information is found at all. Du et al. [7] extend this by showing that sheer context length degrades performance even when retrieval is perfect and no distracting content is present, implicating length itself rather than retrieval failure -- a finding our filler-vs-elaboration split refines by showing that this length-driven degradation is not uniform across content types: our bare-baseline-adjacent filler results suggest the length effect Du et al. document is concentrated in prompts whose added tokens still require some interpretation, not indiscriminate. Yang et al. [6] use a controlled benchmark (GSM-DC) to show LLM reasoning is measurably distracted by irrelevant context, and Shi et al. [8] show LLMs can be "easily distracted" by irrelevant context that changes an *answer*; both differ from our setting in studying single-sample accuracy degradation from distraction rather than multi-sample answer variance from length-matched content manipulation, and neither isolates a relevant-elaboration control at matched token length.

  **Attention entropy as an inference-time signal.** Xu et al. [3] propose EntropyInfer, which classifies attention heads into "rigid" (near-zero entropy) and "dynamic" (fluctuating entropy) categories to adaptively allocate compute during long-context prefill and decoding. This establishes attention entropy as a *measurable, actionable* per-head diagnostic, but strictly as a cost-routing signal, not as a hypothesized correlate of output-level answer instability, which is the role we test it in here (via a logprob-entropy proxy, since our closed-model setting does not expose raw attention weights).

  **Prompt paraphrase and formatting sensitivity.** Separately from length, a growing line of work shows LLM outputs are sensitive to semantically-equivalent surface rewordings of the same instruction: Sclar et al. [11] find accuracy on the same task can swing by tens of points across formatting variants that convey identical content, and Mizrahi et al. [12] show single-prompt evaluation substantially over- or under-estimates model quality relative to a multi-prompt average, because different phrasings of the same instruction produce systematically different outputs. Our competing-interpretation mechanism (Section 5.1) is directly connected to this literature: our decomposition experiment (Section 4.4) shows that redundantly *re-stating* the same question -- a within-prompt analogue of the across-prompt paraphrase manipulations these papers study -- destabilizes numeric answers even though the restatement is semantically identical to the original question and introduces no new facts. This suggests paraphrase sensitivity is not confined to comparing separately-issued prompt variants; a single prompt that contains two phrasings of the same constraint can trigger a similar effect internally.

  **Sampling-based consistency and nondeterminism.** Self-consistency [5] treats multi-sample answer disagreement as a resource to exploit via majority voting rather than a diagnostic signal, implicitly assuming disagreement is roughly uniform in origin; our results suggest the *source* of that disagreement is systematically content-dependent, which has implications for when majority-voting budgets should be increased. Yuan et al. [9] study nondeterminism from floating-point and hardware sources at fixed temperature and find these numerical factors alone can shift outcomes; our design holds hardware and precision fixed by sampling from a single API repeatedly and attributes variance instead to prompt-side manipulations, which is a complementary and much larger source of variance in our data (CV ranges roughly 3-fold across conditions) than pure numerical nondeterminism would predict.

  **Architecture.** Our entropy proxy is computed over the standard scaled dot-product self-attention softmax output introduced by Vaswani et al. [10]; we discuss in Section 6 why our finding is specific to this architecture and does not speak to state-space or hybrid models.

  # Methods

  ## Prompt Construction

  We built 126 prompt variants from 18 GSM8K [4] test-split seed problems (16 used in the final sampling run; see Section 4.1), stratified into easy (1-2 calculator-annotated arithmetic steps), medium (3 steps), and hard (4+ steps) buckets by counting `<<...>>` calculator annotations in each problem's canonical solution . For each seed problem we generated 7 variants: a bare-question control (no added content) and two content types -- *relevant elaboration* and *irrelevant filler* -- crossed with three length tiers (short: target +75 tokens over the control; medium: +250; long: +650), all tokenized with the `cl100k_base` tokenizer for a single consistent length metric.

  Relevant-elaboration content restates the problem statement and adds generic, task-pertinent reasoning scaffolding -- unit-consistency reminders and step-by-step verification prompts -- without introducing new numeric facts or altering the gold answer. Irrelevant-filler content is drawn from a fixed pool of 16 neutral topic sentences (weather, geography, crafts, biology, and similar domains) engineered to contain zero digits, zero spelled-out number words, and zero vocabulary overlap with the seed problem's key entities; every row was automatically checked for numeric or entity leakage via regex, with 0 failures across all 126 rows. Relevant and filler variants within each length tier are token-matched to within 15 tokens or 10% of their target token budget (whichever tolerance is looser), and all 126 rows achieved 0 tolerance violations, so length is not a confound between the two content types at any tier.

  We describe this design as isolating two independent *token-count* manipulations -- raw length and content relevance -- while explicitly flagging a construct-validity caveat the reviewer of an earlier draft correctly identified: the relevant-elaboration variant was authored to add no new numeric information, yet Section 4.2 shows it nonetheless reduces accuracy by several points relative to the bare control, indicating the restated content is not perfectly redundant from the model's perspective. Section 4.4 reports a follow-up experiment built specifically to probe this caveat by decomposing elaboration into a pure-restatement sub-condition and a restatement-plus-scaffolding sub-condition.

  ## Instability and Entropy Measurement

  For the sampling experiment , each of 112 prompts (16 seeds x 7 variants) was sampled 20 times at temperature 0.7 from three OpenAI-hosted models -- gpt-4o-mini, gpt-4.1-mini, and gpt-4.1-nano -- via an OpenAI-compatible chat completions endpoint with `top_logprobs=5` enabled, for 6,720 total attempted calls (5,589 succeeded; 3.3% of resulting prompt-model cells had fewer than the target sample count, tracked as `pct_rows_low_n`). Model selection followed a documented fallback: a pre-flight smoke test showed the originally planned open-weight candidates (Qwen-2.5-72B-Instruct, Llama-3.1-70B-Instruct) return null logprobs via the OpenRouter routing layer used, so the run restricted to the three logprobs-reliable closed models. We are explicit that all three -- gpt-4o-mini, gpt-4.1-mini, gpt-4.1-nano -- are same-provider, same-family checkpoints rather than architecturally or training-diverse systems; "three models" throughout this paper should be read as three same-family checkpoints, not three independent lineages, and we return to this scope limit in Section 6. This fallback is also why we measure a *logprob-entropy proxy* rather than raw attention weights over prompt tokens -- attention matrices are not exposed by these APIs. Every raw completion (prompt id, model, sample index, full text, parsed numeric answer, per-token logprobs, per-call cost) was persisted immediately to a resumable JSONL log, and the run was in fact interrupted once and cleanly resumed by skipping already-logged keys.

  Numeric answers were extracted from each completion via a layered regex cascade (explicit "Final answer:" markers, `\boxed{}` LaTeX, bolded numbers, "answer:" prefixes, and a trailing-number fallback). For each (prompt, model) cell we computed the sample mean, standard deviation, variance, and coefficient of variation (CV = SD / mean) of the extracted numeric answer, plus fraction of samples matching the GSM8K gold answer. As our entropy proxy, we computed the Shannon entropy (in nats) of the renormalized top-5 logprob mass at two points: `mean_entropy_first_k`, averaged over each completion's first 20 generated tokens, and `answer_token_entropy`, the entropy specifically at the token position where the numeric answer is emitted. Because both proxies renormalize over only the visible top-5 tokens, they are documented lower bounds on the true generation-distribution entropy, not exact values.

  ## Statistical Re-Analysis

  An earlier draft of this paper reported condition-level point estimates (means pooled over 16 seeds x 3 models per condition) without confidence intervals, and a between-condition Pearson correlation computed over only the resulting 7 condition means -- both flagged as under-supported by a subsequent review. We therefore built a dedicated re-analysis  directly against the existing raw per-completion log (`raw_completions.jsonl`, 6,720 rows) and per-(prompt,model) aggregate table (`prompt_model_results.csv`, 332 rows after dropping 4 rows with an undefined CV from a zero-mean denominator), with no new API spend. This re-analysis computes: (1) a paired, seed-clustered bootstrap (10,000 resamples over the 16 seed problems, averaging each seed's relevant-minus-filler CV delta across the 3 models before resampling) with 95% percentile confidence intervals and a paired Wilcoxon signed-rank test, per length tier and pooled; (2) cell-level (n=332, not condition-mean) Pearson and Spearman correlations between CV and both entropy proxies, with both a naive row-level bootstrap CI (flagged anti-conservative, since rows sharing a seed are not independent) and a seed-cluster bootstrap CI, plus the same correlations recomputed within each content-type subset to test whether entropy tracks CV beyond simply tracking which condition a row belongs to; (3) a per-model x condition breakdown table with the Metric-1 paired bootstrap re-run separately for each of the 3 models; and (4) a robust re-computation of the CV gap using median-absolute-deviation-over-median and 5%-trimmed CV in place of standard CV, to check the gap is not an artifact of a handful of outlier completions in 20-sample cells. All bootstrap procedures use a fixed RNG seed (12345) and are reproducible.

  ## Decomposition Experiment

  To probe whether "relevant elaboration"'s accuracy cost (Section 4.2) reflects genuine phrasing ambiguity rather than pure redundant-content interpretive load, we built a second dataset and experiment [ARTIFACT:art_GmEL-HAnhH_o, ARTIFACT:art_o5CotSSJpRPD] that decomposes the medium-tier elaboration condition into two isolated sub-conditions on 8 fresh GSM8K seed problems: *paraphrase_only* (a pure reworded restatement of the problem -- same numbers, same constraints, same question -- with zero verification-scaffolding language) and *paraphrase_scaffold* (the identical paraphrase plus the same generic verification-scaffolding sentences used in the original elaboration condition: double-check your units, verify each step, confirm the final answer is consistent with the stated constraints). Both sub-conditions were length-matched to each other and to the prior medium tier (~250 added tokens) within the same tolerance used elsewhere (max of 15 tokens or 10%), and checked for zero numeric leakage. We note two deviations from the original plan, both logged explicitly in the artifact's metadata: the dataset-generation dependency this experiment expected had not produced output at execution time, and iteration-1's own tier-2 "relevant" field was found on inspection to be corrupted (containing a literal, unsubstituted `{question}` template placeholder and mid-sentence truncation in a subset of rows) -- rather than propagate that corruption forward via text surgery, we reconstructed both sub-conditions from the canonical (question, gold-answer) control rows using the same scaffold-sentence pool iteration-1 documented, flagging every new row with `metadata_self_constructed_fallback: true`. The two new conditions were sampled alongside carried-forward bare-control and length-matched filler rows for the same 8 seeds (32 unique prompts), each sampled 15 times across the same 3 models, for 1,440 calls at $0.33 total spend. This experiment is explicitly a self-constructed decomposition on a smaller, independently drawn seed set (8, not 16), not a re-run of the original elaboration condition, and its results (Section 4.4) should be read with that scope in mind.

  # Experiments

  ## Setup

  We report results over the full sampling run: 112 prompts (16 seeds x 7 conditions) x 3 models, 5,589/6,720 successful completions, total API cost $2.07 (well under the $10 budget cap; run never budget-stopped) . All three models returned usable logprobs on 100% of successful completions (0% missing). We treat the bare-question control (mean CV = 0.170, mean fraction-correct = 0.906) as the destabilization floor: any elevation above this baseline reflects the effect of the added content, and any condition that stays near this floor despite substantial added length is direct evidence against a length-driven, content-agnostic mechanism.

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

  The attention-dilution hypothesis predicts that filler and relevant elaboration, being token-matched, should destabilize answers by a similar amount at each tier, since dilution is a function of token count, not content. The raw means in Table 1 show a large gap in the opposite direction of what "irrelevant filler destabilizes more" would require, at every tier. To test whether this gap is defensible rather than an artifact of pooling over correlated seed-level noise, our re-analysis  computes the paired relevant-minus-filler CV delta per seed (averaging over the 3 models), then a cluster (block) bootstrap over the 16 seed IDs (10,000 resamples):

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

  An earlier draft of this paper reported Pearson correlations of r=0.75 and r=0.59 between the entropy proxies and CV, computed over the seven condition-mean rows in Table 1. A subsequent review correctly flagged this as an unstable estimate: with only 7 points, a single condition's mean shifting slightly could substantially change or reverse the correlation. Our re-analysis instead computes the correlation at the individual (prompt, model) cell level, over all 332 available rows :

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

  **The entropy-CV correlation is real but modest, and no mediation analysis exists.** The cell-level correlation (r=0.284/0.260, both CI-excluding-zero) replaces an earlier draft's inflated condition-mean estimate, but a correlation of this magnitude explains a small fraction of CV's variance (r^2 approx. 0.07-0.08), and no formal mediation analysis (testing whether entropy statistically mediates a length-to-variance pathway) has been run in any iteration of this project; the originally planned Baron-Kenny mediation was blocked by an upstream data-availability failure in iteration 1 \footnote{Code: \url{https://github.com/ai-inventor-outputs/ai-invention-0e9809-interpretive-load-not-token-count-drives/tree/main/round-1/evaluation-1}} and has not since been attempted on the now-available data. This remains the clearest concrete gap between the paper's evidence and its original mediation-focused research question.

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
summary: >-
  A length-and-content-matched GSM8K prompt battery, sampled across three same-provider GPT models (5,589 completions), shows
  that irrelevant filler leaves numeric-answer variance and a logprob-entropy proxy near the bare-question baseline even at
  ~650 extra tokens, while relevant elaboration destabilizes both -- but this iteration adds seed-clustered bootstrap confidence
  intervals (pooled gap +0.195, CI [0.091,0.319]), downgrades an earlier fragile condition-mean entropy-CV correlation (r=0.75,
  n=7) to a defensible cell-level one (r=0.284, n=332, CI-excluding-zero), and a follow-up decomposition experiment shows
  the destabilizing effect concentrates in redundant question restatement (+0.103 CV) rather than generic verification scaffolding
  (-0.101 CV), connecting the finding to the prompt-paraphrase-sensitivity literature.
</paper_text>

<available_figures>
--- Item 1 ---
id: fig_overview
figure_type: concept
title: Study Design Overview
caption: >-
  End-to-end pipeline: GSM8K seed problems are expanded into length-and-content-matched prompt variants, sampled 20x per prompt
  across three same-provider GPT models with logprobs enabled, then re-analyzed with seed-clustered bootstrap statistics and
  a restatement-vs-scaffolding decomposition follow-up.
image_gen_detailed_description: >-
  Horizontal flow diagram, left to right, 21:9 aspect ratio, clean white background, sans-serif font, no 3D effects. Five
  stages connected by arrows: (1) leftmost box labeled 'GSM8K seed problem' (light gray) with a small icon of a math word
  problem; (2) arrow splits into two paths both feeding into a box labeled 'Prompt variants: 7 per seed' (light blue) showing
  two content-type branches -- one branch labeled 'Irrelevant filler (short/medium/long, +75/+250/+650 tokens)' in orange,
  one branch labeled 'Relevant elaboration (short/medium/long)' in green, both token-matched within 2%; (3) next box labeled
  '20 samples x 3 models (temp=0.7)' (blue) listing 'gpt-4o-mini, gpt-4.1-mini, gpt-4.1-nano' with a small note 'same provider,
  same family'; (4) next box labeled 'Answer + logprob entropy extraction' (purple) with a small icon of a probability distribution;
  (5) rightmost box labeled 'Seed-clustered bootstrap re-analysis + restatement-vs-scaffolding decomposition' (dark blue),
  with a small callout showing 'CI [0.091, 0.319]' and 'restatement +0.103 / scaffolding -0.101'. Below the main flow, a small
  side box labeled 'Bare-question control (no added content)' with a dashed arrow pointing up into stage 2 as the baseline
  reference. Use a professional research-diagram style with rounded rectangle nodes and clear directional arrows.
aspect_ratio: '21:9'
summary: >-
  Shows the full study pipeline from seed problems through sampling to the statistical re-analysis and decomposition follow-up.
figure_path: figures/fig_overview_v0.jpg

--- Item 2 ---
id: fig_cv_bars
figure_type: data
title: Elaboration vs Filler CV Gap by Tier
caption: >-
  Paired, seed-clustered bootstrap 95% confidence intervals for the mean CV gap (relevant elaboration minus token-matched
  filler) at each length tier and pooled across tiers. Only the medium tier and the pooled estimate exclude zero.
image_gen_detailed_description: >-
  Horizontal forest plot (point estimate with horizontal error bar for 95% CI), 4 rows on the y-axis from top to bottom: 'Pooled
  (all tiers)', 'Medium tier', 'Long tier', 'Short tier'. X-axis label 'Mean CV delta (relevant elaboration - filler)', range
  from -0.1 to 0.7, with a vertical dashed reference line at x=0. Values (point, CI lower, CI upper): Pooled = 0.195, [0.091,
  0.319]; Medium = 0.350, [0.098, 0.666]; Long = 0.112, [-0.0005, 0.219]; Short = 0.123, [-0.001, 0.254]. Color the Pooled
  and Medium rows dark blue (CI excludes zero) and the Long and Short rows gray (CI touches or crosses zero). Include small
  text labels next to each point showing the numeric value. Clean white background, sans-serif font.
aspect_ratio: '4:3'
summary: >-
  Forest plot of the elaboration-minus-filler CV gap with bootstrap CIs per tier, showing only the medium tier and pooled
  estimate are individually significant.
figure_path: figures/fig_cv_bars_v0.pdf

--- Item 3 ---
id: fig_permodel
figure_type: data
title: Medium-Tier CV Gap by Model
caption: >-
  Per-model paired bootstrap estimates of the medium-tier elaboration-minus-filler CV gap. The positive direction holds across
  all three same-provider models, though only gpt-4o-mini's confidence interval individually excludes zero.
image_gen_detailed_description: >-
  Horizontal forest plot (point estimate with horizontal error bar for 95% CI), 3 rows on the y-axis: 'gpt-4o-mini', 'gpt-4.1-nano',
  'gpt-4.1-mini'. X-axis label 'Mean CV delta at medium tier (relevant - filler)', range from -0.3 to 1.0, vertical dashed
  reference line at x=0. Values (point, CI lower, CI upper): gpt-4o-mini = 0.383, [0.100, 0.744]; gpt-4.1-nano = 0.202, [-0.002,
  0.430]; gpt-4.1-mini = 0.290, [-0.074, 0.840]. Color gpt-4o-mini's row dark blue (CI excludes zero), the other two rows
  gray. Small numeric labels next to each point. Clean white background, sans-serif font.
aspect_ratio: '4:3'
summary: >-
  Shows the medium-tier CV gap is directionally consistent across all three models but individually significant for only one.
figure_path: figures/fig_permodel_v0.pdf

--- Item 4 ---
id: fig_entropy_bars
figure_type: data
title: Logprob Entropy by Content Type and Length
caption: >-
  Mean logprob-entropy proxy (first-20-token entropy, nats) across the seven content-type by length-tier conditions, pooled
  over 16 seeds and 3 models. Entropy stays nearly flat across filler tiers but rises monotonically with relevant-elaboration
  length.
image_gen_detailed_description: >-
  Grouped bar chart, 16:9 aspect ratio. X-axis categories (7 groups): 'Bare control', 'Filler short', 'Filler medium', 'Filler
  long', 'Relevant short', 'Relevant medium', 'Relevant long'. Y-axis label 'Mean entropy, first 20 tokens (nats)', range
  0 to 0.6. Single series, values in order: 0.334, 0.339, 0.335, 0.341, 0.434, 0.479, 0.514. Color the four 'Bare control'
  and 'Filler' bars orange, and the three 'Relevant' bars green, to visually separate the two content types. Add a thin horizontal
  dashed reference line at y=0.334 labeled 'bare-control baseline'. Clean white background, sans-serif font, axis gridlines
  light gray.
aspect_ratio: '16:9'
summary: >-
  Shows entropy proxy stays flat under filler across all lengths but rises steadily under relevant elaboration.
figure_path: figures/fig_entropy_bars_v0.pdf

--- Item 5 ---
id: fig_decomp
figure_type: data
title: Restatement vs Scaffolding Decomposition
caption: >-
  Decomposing the medium-tier elaboration condition into pure paraphrase and paraphrase-plus-scaffolding on 8 fresh GSM8K
  seeds x 3 models. Redundant restatement alone raises CV over token-matched filler (+0.103); adding scaffolding does not
  compound this (-0.101) despite substantially raising entropy and lowering accuracy.
image_gen_detailed_description: >-
  Grouped bar chart with two panels side by side sharing the same 4 x-axis categories: 'Bare control', 'Filler (medium)',
  'Paraphrase only', 'Paraphrase + scaffolding'. Left panel y-axis label 'Mean answer CV', range 0 to 0.3; values: 0.195,
  0.158, 0.261, 0.160. Right panel y-axis label 'Fraction correct', range 0 to 1.0; values: 0.819, 0.900, 0.854, 0.605. Use
  consistent bar colors across both panels per category: gray for 'Bare control', orange for 'Filler (medium)', light green
  for 'Paraphrase only', dark green for 'Paraphrase + scaffolding'. Add small text annotations above the CV panel bars for
  'Paraphrase only' and 'Paraphrase + scaffolding' showing 'restatement effect +0.103' and 'scaffolding effect -0.101' as
  arrows/callouts relative to the filler bar. Clean white background, sans-serif font, 16:9 aspect ratio overall.
aspect_ratio: '16:9'
summary: >-
  Two-panel comparison showing restatement alone drives the CV increase while scaffolding lowers accuracy without further
  raising CV.
figure_path: figures/fig_decomp_v0.pdf
</available_figures>

<figure_requirements>
CRITICAL: Include ALL figures from <available_figures>. No exceptions.

- Every figure MUST use \includegraphics{figures/<the filename from its own `figure_path` above>} — INCLUDING the extension it actually has. Data figures are delivered as `.pdf` (vector, so their axis labels stay sharp) and concept figures as `.jpg`. Writing `.jpg` for a `.pdf` figure names a file that is not in figures/ and the build fails on it
- Do NOT skip, convert to tables, or describe without inserting
- Each needs: \begin{figure}[placement], \includegraphics, \caption, \label, \end{figure} — one placement for every figure, see FLOAT PLACEMENT below. Constrain every \includegraphics with `width=\linewidth,height=0.85\textheight,keepaspectratio`. The height is a LAST RESORT, not the usual limit: it exists so a very tall figure cannot overrun the page, and at 0.4 it bound almost everything instead — a 1:1 confusion matrix printed at 50.9% and its 11 pt axis labels reached the page at 5.6 pt, below what any venue accepts. At 0.85 every ratio the paper prompt prescribes (21:9, 16:9, 4:3, 1:1) is limited by WIDTH, prints at 93% and keeps its text above 10 pt. Use exactly these option keys — `max height=` is NOT valid LaTeX
- Use the `caption` field from each figure for \caption{...} — do NOT invent new captions
- Place figures where their [FIGURE:fig_id] markers appear in paper_text
- VERIFICATION: paper.tex MUST have exact same number of \includegraphics as <available_figures>
- Do NOT generate new figure images (no matplotlib, no PIL, no image generation). Use ONLY the pre-generated figures from <available_figures>. They were already created by a previous pipeline step.

FLOAT PLACEMENT: every figure gets \begin{figure}[!htbp]. Measured, not chosen:
the document the aii-paper-to-latex skill sets up is ONE column, so `figure*` is
exactly as wide as `figure` (469.76pt either way) and gains nothing; and any
placement asking for a page TOP — `[!t]`, `[!tbp]` — floated the hero diagram above
the paper's own title on page 1, while `[!htbp]` did not. `[!htbp]` also gives LaTeX
four options, so a float can never be deferred to the end of the document, which one
option alone risks. Where the hero ENDS UP is decided by its [FIGURE:] marker in
paper_text, which is already placed near the end of the Introduction — preserve it.
</figure_requirements>

<artifact_links>
The paper_text contains \footnote{Code: \url{...}} references linking to artifact source code
on GitHub. Include \usepackage{hyperref} and \usepackage{url}.
Preserve these exactly as-is — do not remove, rewrite, or convert them to plain text.
The URLs will not resolve yet (the repo is deployed after compilation) — do NOT try to verify or fix them.
</artifact_links>

<headings>
NEVER use inline math (``$...$``) inside ``\section{...}`` / ``\subsection{...}`` / ``\subsubsection{...}`` arguments — hyperref's bookmark builder errors out (``Token not allowed in a PDF string``) and the PDF outline breaks. If a section heading needs a math-looking term, use the text equivalent (``d star`` not ``$d^*$``, ``alpha-equivalent`` not ``$\alpha$-equivalent``) or wrap it in ``\texorpdfstring{$math$}{plain}``. Inline math inside body paragraphs is fine.
</headings>

FIRST, add ALL of these to your todo list using your task/todo-tracking tool:

CRITICAL: Todo content must be copied exactly as is written here, with NO CHANGES. These todos are intentionally detailed so that another LLM could read each one without any external context and understand exactly what it has to do.

<todos>
TODO 1. Read and STRICTLY follow these skills: aii-paper-to-latex, aii-semscholar-bib.
TODO 2. Review <paper_text> and <available_figures>. Copy all figure images into ./figures/ in your workspace. Count figures — MUST include every one. Plan placements per section. Build `./references.bib` via aii_semscholar_bib__fetch — collect DOIs/ArXiv IDs from <paper_text> and batch-fetch all BibTeX in one call. Do NOT fabricate entries.
TODO 3. Create `./paper.tex` per aii-paper-to-latex skill's setup, write ALL sections, insert ALL figures from <available_figures>, include `./references.bib` via \bibliography. Compile to PDF per skill's process. Fix errors.
TODO 4. CRITICAL VERIFICATION: Run `grep -c 'includegraphics' paper.tex`, confirm count equals figures in <available_figures>. If not, add missing figures. Verify `./paper.pdf` was created.
TODO 5. VISUAL REVIEW: Write Python script to convert EVERY page of paper.pdf to PNG at 150 DPI (use pdf2image or pymupdf). Then read ALL page screenshots — each page image costs ~1,600 tokens so a 15-page paper is only ~24K tokens. You MUST read every page. The ONLY exception is if all page images would not fit in your remaining context — in that case, read as many as fit and state which pages you are skipping and why. Check every page for layout issues, overlapping figures, cut-off text, bad spacing, formatting problems. Fix issues and recompile.
TODO 6. FINAL READ: Check page count (`pdfinfo paper.pdf` or pymupdf). Read entire paper.pdf — check for missing sections, unclear explanations, inconsistencies, typos. Fix and recompile. The ONLY exception is if all pages would not fit in your remaining context — in that case, read as many pages as fit and state which pages you are skipping and why.
</todos>

---

Output the result as JSON to: `./.terminal_claude_agent_struct_out.json`

JSON Schema:
```json
{
  "$defs": {
    "FullPaperExpectedFiles": {
      "description": "All expected output files from full paper generation.",
      "properties": {
        "paper_tex_path": {
          "description": "Path to LaTeX source file. Example: 'paper.tex'",
          "title": "Paper Tex Path",
          "type": "string"
        },
        "paper_pdf_path": {
          "description": "Path to compiled PDF. Example: 'paper.pdf'",
          "title": "Paper Pdf Path",
          "type": "string"
        },
        "references_bib_path": {
          "description": "Path to BibTeX bibliography file. Example: 'references.bib'",
          "title": "References Bib Path",
          "type": "string"
        },
        "figure_paths": {
          "description": "Paths to all figure image files. Example: ['figures/fig1_v0.jpg', 'figures/fig2_v0.jpg']",
          "items": {
            "type": "string"
          },
          "title": "Figure Paths",
          "type": "array"
        }
      },
      "required": [
        "paper_tex_path",
        "paper_pdf_path",
        "references_bib_path",
        "figure_paths"
      ],
      "title": "FullPaperExpectedFiles",
      "type": "object"
    }
  },
  "description": "Full paper \u2014 structured output from paper generation.",
  "properties": {
    "title": {
      "description": "Paper title in plain, everyday language \u2014 short and jargon-free so a non-expert grasps it at a glance. Aim for about 4-8 words (~40 characters).",
      "maxLength": 90,
      "minLength": 12,
      "title": "Title",
      "type": "string"
    },
    "summary": {
      "description": "Brief summary of the generated paper: sections written, figures included, compilation status",
      "maxLength": 5000,
      "minLength": 500,
      "title": "Summary",
      "type": "string"
    },
    "out_expected_files": {
      "$ref": "#/$defs/FullPaperExpectedFiles",
      "description": "All output files you created. Must include paper.tex, paper.pdf, references.bib, and paths to all figure files."
    }
  },
  "required": [
    "title",
    "summary",
    "out_expected_files"
  ],
  "title": "FullPaper",
  "type": "object"
}
```

IMPORTANT: this task is NOT complete until `./.terminal_claude_agent_struct_out.json` exists and contains JSON matching the schema above.
````

### [2] HUMAN-USER prompt · 2026-08-19 16:45:51 UTC

```
Does prompt length change the variance of LLM numeric answers?
```

### [3] SKILL-INPUT — aii-paper-to-latex · 2026-08-19 16:45:55 UTC

The agent loaded the **aii-paper-to-latex** skill; its `SKILL.md` (the instructions injected into the agent's context) follows verbatim.

````
---
name: aii-paper-to-latex
description: LaTeX paper assembly and compilation. Covers document setup, figure inclusion from pre-generated vector PDFs and JPEGs, compilation process, and output files. Use when assembling a paper from pre-written text and pre-generated figures into a compiled PDF.
---

## LaTeX Paper Assembly

Assembles a research paper from paper text, pre-generated figures (vector `.pdf` for data figures, `.jpg` for concept figures) and a bibliography into a compiled PDF.

### Document Setup

```latex
\documentclass[11pt,letterpaper]{article}
\usepackage{graphicx, geometry, amsmath, hyperref, natbib, booktabs, xcolor, listings}
\geometry{margin=1in}
\hypersetup{colorlinks=true, linkcolor=black, citecolor=black, urlcolor=black}
```

### Figure Inclusion

CRITICAL: Include ALL figures. Every figure MUST appear in the paper.

```latex
\begin{figure}[!htbp]
  \centering
  \includegraphics[width=0.92\textwidth,keepaspectratio]{figures/filename.pdf}
  \caption{Descriptive caption.}
  \label{fig:label}
\end{figure}
```

Rules:
- ALWAYS `[!htbp]` — all four options, so a float can never be deferred to the end of the
  document, which `[t]` or `[h]` alone risks. Do not ask for a page TOP: `[!t]` and
  `[!tbp]` both floated a figure ABOVE the paper's own title on page 1, where `[!htbp]`
  on the same document did not. Where a figure lands is decided by where it is declared
  in the text
- Use `figure`, never `figure*`. This document class is ONE column, so `figure*` is exactly
  as wide as `figure` (469.76pt either way) and gains nothing, while restricting the float
  to a page top
- ALWAYS constrain with `width` and `keepaspectratio`. Add `height` only as a
  LAST RESORT against a very tall figure overrunning the page, and keep it
  generous — `0.85\textheight`. A tight height cap binds on ordinary figures
  and LaTeX then shrinks the TEXT with them: at `0.4\textheight` a square
  figure printed at 50.9%, putting 11 pt axis labels on the page at 5.6 pt.
  The figure generator measures legibility at the figure's OWN size, so it
  cannot see this happen
- Every figure needs `\caption`, `\label`, and a `\ref` in the text
- Do NOT convert figures to tables or describe them without inserting the image
- Do NOT skip any figures

### Compilation Process

Run each command separately (do NOT chain with `&&` — pdflatex often exits non-zero on warnings, which would skip bibtex and leave citations as `??`):

```bash
pdflatex -interaction=nonstopmode paper.tex
bibtex paper
pdflatex -interaction=nonstopmode paper.tex
pdflatex -interaction=nonstopmode paper.tex
```

All four commands are required. Skipping bibtex causes `??` in all citations.
Fix any errors between runs. Verify `./paper.pdf` was created.

### Output Files

- `./paper.tex` — LaTeX source
- `./references.bib` — bibliography file
- `./paper.pdf` — compiled PDF
- `./figures/` — all figure images (pre-generated, copied into workspace). Data
  figures are `.pdf` (vector — LaTeX renders their text at page resolution, which
  is what keeps axis labels sharp in print); concept figures are `.jpg`. Use each
  file's OWN extension in `\includegraphics`; there is no conversion step.
````

### [4] SKILL-INPUT — aii-semscholar-bib · 2026-08-19 16:45:55 UTC

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

### [5] SYSTEM-USER prompt · 2026-08-19 16:51:22 UTC

```
<validation-feedback>
Attempt 1 failed validation.

The output file `.terminal_claude_agent_struct_out.json` does not exist yet. Produce it as JSON matching the schema.

Produce `.terminal_claude_agent_struct_out.json` again so it contains corrected JSON that matches the schema. Do not invent new fields.
</validation-feedback>
```

### [6] SYSTEM-USER prompt · 2026-08-19 16:51:36 UTC

```
<task-notification>
<task-id>b8ss7ql1h</task-id>
<tool-use-id>toolu_01FpzJRgnGiJhDeF6Ymqcr8j</tool-use-id>
<output-file>/tmp/claude-0/-ai-inventor-aii-data-runs-run-l-N7kpGv9Lri-4-gen-paper-repo--4-assemble-paper-paper-workspace/8e9ec052-9bab-428d-829c-a252b7730bea/tasks/b8ss7ql1h.output</output-file>
<status>completed</status>
<summary>Background command "SKILL_DIR="/ai-inventor/.claude/skills/aii-semscholar-bib" &amp;&amp; \
$SKILL_DIR/../.ability_client_venv/bin/python $SKILL_DIR/scripts/aii_semscholar_bib__fetch.py --refs '[
  {"arxiv": "2604.07593", "author": "Cabrera", "year": 2026},
  {"title": "Lost in the Middle: How Language Models Use Long Contexts", "author": "Liu", "year": 2023},
  {"arxiv": "2606.09508", "author": "Xu", "year": 2026},
  {"arxiv": "2110.14168", "author": "Cobbe", "year": 2021},
  {"title": "Self-Consistency Improves Chain of Thought Reasoning in Language Models", "author": "Wang", "year": 2022},
  {"title": "How Is LLM Reasoning Distracted by Irrelevant Context? An Analysis Using a Controlled Benchmark", "author": "Yang", "year": 2025},
  {"arxiv": "2510.05381", "author": "Du", "year": 2025},
  {"title": "Large Language Models Can Be Easily Distracted by Irrelevant Context", "author": "Shi", "year": 2023},
  {"title": "Understanding and Mitigating Numerical Sources of Nondeterminism in LLM Inference", "author": "Yuan", "year": 2025},
  {"arxiv": "1706.03762", "author": "Vaswani", "year": 2017},
  {"arxiv": "2310.11324", "author": "Sclar", "year": 2023},
  {"title": "State of What Art? A Call for Multi-Prompt LLM Evaluation", "author": "Mizrahi", "year": 2023}
]' &gt; /tmp/bib_out.txt 2&gt;&amp;1; tail -80 /tmp/bib_out.txt" completed (exit code 0)</summary>
</task-notification>
```

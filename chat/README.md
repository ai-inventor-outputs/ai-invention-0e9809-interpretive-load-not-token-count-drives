# Chat

The complete conversational record of this AI Inventor run, in two views:

- **[`prompts/`](prompts/)** — the INPUTS only: every prompt the pipeline fed each agent (system, human, and loaded skill instructions), verbatim.
- **[`messages/`](messages/)** — the FULL conversation: every prompt PLUS the model's responses, thinking, and every tool call and result — the entire back-and-forth, in order.

Both mirror the run's pipeline structure (create_idea → test_idea → report_results, with a folder per phase / round / module), and are generated automatically at repository-upload time from the run's event log.

- Run: Interpretive Load, Not Token Count, Drives LLM Answer Instability

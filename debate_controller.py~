"""debate_controller.py

Coordinates a two-step debate between local LLMs and GPT-4o to generate a
high-quality implementation of an AGI subsystem (``module_name``).  The flow is:

1.  Two local models each produce a candidate implementation.
2.  GPT-4o compares/merges the candidates and returns the best version.
3.  The code is written to ``../agi_system/{module_name}.py`` and auto-formatted.
4.  GPT-4o is asked to *verify* the final code and return
    ``{"status": "ok"}`` or ``{"status": "fix", "notes": "..."}``.

If verification reports "fix", the method raises ``RuntimeError`` so a human or
an automated supervisor can iterate.

Dependencies
------------
* llm_client.call_local_model
* gpt4o_client.call_gpt4o
* token_budget.check_token_limit, token_budget.log_tokens
* tool_call_router.write_file, tool_call_router.run_shell
"""

import asyncio
import json
from typing import List

from llm_client import call_local_model
from gpt4o_client import call_gpt4o
from token_budget import check_token_limit, log_tokens
from tool_call_router import write_file, run_shell


class DebateController:
    """Runs a debate/verification loop to produce and check a code module."""

    def __init__(self) -> None:
        self.chunk_history: dict[str, List[str]] = {}

    # ------------------------------------------------------------------ #
    # Prompt builders
    # ------------------------------------------------------------------ #
    @staticmethod
    def _format_comparison_prompt(module_name: str, candidates: List[str]) -> str:
        """Prompt asking GPT-4o to pick/merge the two candidates.

        GPT-4o must return **only** the final Python code with no commentary or
        fences, so we can dump it straight to disk.
        """
        prompt = f"""You are the senior architect of an autonomous AGI project.
Two candidate implementations of the `{module_name}` module have been generated
by separate local LLMs. Your tasks:

1. Compare their correctness, completeness, readability, and efficiency.
2. Fix any bugs or omissions you notice.
3. Output **only** the full, production-ready Python source for `{module_name}.py`
   – no explanations, markdown, or code fences.

---
### Candidate A
{candidates[0]}

---
### Candidate B
{candidates[1]}

---
Remember: your entire reply must be valid Python – nothing else.
"""
        return prompt

    @staticmethod
    def _format_verify_prompt(module_name: str, code: str) -> str:
        """Prompt asking GPT-4o to audit the generated code.

        GPT-4o must respond with a tiny JSON object:
          {"status": "ok"}
          – or –
          {"status": "fix", "notes": "<problem summary>"}
        """
        prompt = f"""You are auditing the new `{module_name}.py` for an AGI stack.
Review the code below for syntax errors, missing imports, logical issues,
and compliance with the project's style (PEP 8, modular, well-typed).

Respond with **exactly one** JSON object:

  {{"status": "ok"}}                           – if everything is correct
  {{"status": "fix", "notes": "<summary>"}}    – if changes are needed

No additional keys, no markdown, no commentary – ONLY the JSON.

---
{code}
"""
        return prompt

    # ------------------------------------------------------------------ #
    # Main entry
    # ------------------------------------------------------------------ #
    async def run_debate(self, module_name: str, prompt: str) -> str:
        """Runs debate & verification, returns path to the generated file."""

        print(f"[DebateController] Starting debate for module: {module_name}")

        # === Step 1: ask local models ===
        print("[DebateController] Prompting local models…")
        tasks = [
            call_local_model(prompt, model="llama3-8b"),   # default executor
            call_local_model(prompt, model="mistral-7b")   # second opinion
        ]
        candidates = await asyncio.gather(*tasks)

        # === Step 2: GPT-4o chooses / merges ===
        print("[DebateController] Forwarding candidates to GPT-4o…")
        critique_prompt = self._format_comparison_prompt(module_name, candidates)
        if not check_token_limit(critique_prompt):
            raise RuntimeError("Token limit exceeded for GPT-4o critique input")

        best_code, tok_crit = await call_gpt4o(critique_prompt)
        log_tokens(tok_crit)

        # === Step 3: write to disk & auto-format ===
        filepath = f"../agi_system/{module_name}.py"
        write_file(filepath, best_code)
        run_shell(f"black {filepath} --quiet")

        # === Step 4: verification pass ===
        print("[DebateController] Verifying implementation via GPT-4o…")
        verify_prompt = self._format_verify_prompt(module_name, best_code)
        if not check_token_limit(verify_prompt):
            raise RuntimeError("Token limit exceeded for GPT-4o verification input")

        verify_reply, tok_ver = await call_gpt4o(verify_prompt)
        log_tokens(tok_ver)
        print(f"[DebateController] Verification reply: {verify_reply}")

        # parse the tiny JSON object
        try:
            verdict = json.loads(verify_reply.strip())
        except json.JSONDecodeError:
            raise RuntimeError("Verification failed – GPT-4o did not return valid JSON")

        if verdict.get("status") != "ok":
            notes = verdict.get("notes", "No notes provided")
            raise RuntimeError(f"Verification failed – GPT-4o flagged issues: {notes}")

        print("[DebateController] ✅ Verification passed.")
        return filepath


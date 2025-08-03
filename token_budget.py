"""
token_budget.py
~~~~~~~~~~~~~~~~

Tracks total GPT-4o token usage, enforces a global cap, and—new in July 2025—
prints an estimated cost based on OpenAI’s current pricing.

Functions
---------
check_token_limit(prompt: str) -> bool
    Return False if adding ``prompt`` would exceed the hard MAX_TOKENS budget.

log_tokens(used: int) -> None
    Add *used* tokens to the running total stored in ``token_log.json``.

show_usage() -> None
    Print total tokens consumed and their estimated USD cost to the CLI.

Run ``python3 token_budget.py`` at any time to view the usage summary.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

# --------------------------------------------------------------------------- #
#  Configuration
# --------------------------------------------------------------------------- #

BUDGET_FILE = Path("token_log.json")
MAX_TOKENS: int = 128_000  # absolute cap to avoid runaway spending

# --- OpenAI GPT-4o text pricing as of 2025-07-30 --------------------------- #
#   • Input  tokens: $5   / 1 000 000 ( $0.005 / 1 000 )
#   • Output tokens: $20  / 1 000 000 ( $0.020 / 1 000 )
#
# The tracker logs total tokens (input + output).  We therefore estimate cost
# using the midpoint between input and output rates.
_INPUT_PRICE_PER_1K  = 0.005  # USD
_OUTPUT_PRICE_PER_1K = 0.020  # USD
_AVG_PRICE_PER_1K    = (_INPUT_PRICE_PER_1K + _OUTPUT_PRICE_PER_1K) / 2
# --------------------------------------------------------------------------- #


def _init_log() -> None:
    """Ensure the budget file exists."""
    if not BUDGET_FILE.exists():
        BUDGET_FILE.write_text(json.dumps({"used_tokens": 0}))


_init_log()


# --------------------------------------------------------------------------- #
#  Public API
# --------------------------------------------------------------------------- #
def check_token_limit(prompt: str) -> bool:
    """Return **False** if adding *prompt* would exceed ``MAX_TOKENS``."""
    used = _read_used_tokens()
    return used + len(prompt.split()) <= MAX_TOKENS


def log_tokens(used: int) -> None:
    """Accumulate *used* tokens in the budget file."""
    data = {"used_tokens": _read_used_tokens() + used}
    BUDGET_FILE.write_text(json.dumps(data))


def show_usage() -> None:
    """Print total tokens used and estimated cost to the CLI."""
    used = _read_used_tokens()
    cost_usd = (used / 1_000) * _AVG_PRICE_PER_1K
    print(f"[TokenBudget] Total GPT-4o tokens used: {used:,}")
    print(f"[TokenBudget] Estimated cost (@${_AVG_PRICE_PER_1K:.3f}/1K): "
          f"${cost_usd:,.4f}")


# --------------------------------------------------------------------------- #
#  Helpers
# --------------------------------------------------------------------------- #
def _read_used_tokens() -> int:
    return json.loads(BUDGET_FILE.read_text())["used_tokens"]


# --------------------------------------------------------------------------- #
#  CLI entry-point
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    show_usage()
import json
import os

BUDGET_FILE = "token_log.json"
MAX_TOKENS = 128000

if not os.path.exists(BUDGET_FILE):
    with open(BUDGET_FILE, "w") as f:
        json.dump({"used_tokens": 0}, f)

def check_token_limit(prompt):
    with open(BUDGET_FILE, "r") as f:
        data = json.load(f)
    if len(prompt.split()) + data["used_tokens"] > MAX_TOKENS:
        return False
    return True

def log_tokens(used):
    with open(BUDGET_FILE, "r") as f:
        data = json.load(f)
    data["used_tokens"] += used
    with open(BUDGET_FILE, "w") as f:
        json.dump(data, f)

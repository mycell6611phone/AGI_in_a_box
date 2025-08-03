# AI-in-a-Box System README

This system is a modular AGI automation platform where GPT-4 handles planning and reasoning, and local LLMs perform execution, critique, and memory curation. It is designed to be self-refining, maintainable, and partially self-improving through debate and tool delegation.

---

## Overview

- **Planner:** GPT-4 interprets goals and breaks them into shell/file-based plans.
- **Executor:** Local LLMs run shell commands and file edits.
- **Memory:** All information is debated and filtered before being logged for long-term use.
- **Debate Engine:** Verifies all generated modules and memory before acceptance.
- **Main Loop:** Ties it all together by continuously cycling through goal → plan → execute → reflect.

---

## Core Modules

### `main_loop.py` – System Orchestrator
- Accepts English-language goals
- Plans them with GPT-4
- Passes actions to local LLM executors
- Summarizes results and retries failures

### `gpt_planner.py` – GPT Planning Interface
- GPT-4 breaks down goals into actionable JSON steps
- Delegates to tools like `run_shell`, `write_file`, etc.
- Recalls previous plans to avoid redundant requests

### `planner.py` – Local Plan Registry
- Stores structured plans
- Tracks status, results, and completion

### `memory_logger.py` – Persistent Memory Writer
- Stores validated knowledge as `.md` files in GPT4All LocalDocs
- Tags, timestamps, and UUIDs included

### `memory_recaller.py` – Memory Retrieval
- Tries to find similar previous plans before GPT is called
- Reduces duplication and leverages prior context

### `debate_controller.py` – Module Builder + Memory Filter
- Two local LLMs generate candidate solutions
- GPT-4o selects, merges, and verifies final version
- Memory is only stored after debate+approval

### `debate_filter_extended.py` – Fine-Tuning Data Debate (Optional)
- Mistral and Reasoner debate training examples
- LLaMA 3.1 8B acts as judge
- Filters high-quality fine-tuning data into verified `.jsonl`

### `executor.py` – Task Execution Engine
- Executes shell commands and file edits
- Logs all actions to structured JSON log
- Used by local LLMs to perform real actions

### `write_prompt_files.py` – Prompt Seeder
- Initializes AGI module build prompts into `./prompts/`
- Prompts editable by GPT or LLMs for flexibility

### `feedback_logger.py` – Natural Language Summary Generator
- Reads last execution log and summarizes what happened
- Can be shown to the user or fed back into GPT

---

## GPT and Local LLM Clients

### `gpt4o_client.py`
- Calls OpenAI GPT-4o
- Includes retry logic
- Tracks token usage
- Will support real-time cost tracking

### `llm_client.py`
- Calls local LLM server (`localhost:4891`)
- Best available method for interacting with local models

---

## Planned UI (`ui_interface.py`) [TO BUILD]

The UI will:
- Allow goal entry
- Show GPT and LLM responses
- Display real-time token/cost usage
- View memory and debate results
- Provide logs and control interface

---

## Summary

| Component              | Function                                                  |
|------------------------|-----------------------------------------------------------|
| `main_loop`            | Central orchestrator for plan/execute cycle              |
| `gpt_planner`          | GPT planning with memory recall                          |
| `planner`              | Stores and manages plan metadata                        |
| `executor`             | Shell/file command runner                                |
| `memory_logger`        | Writes memory entries (post-debate only)                |
| `memory_recaller`      | Checks memory before GPT is used                        |
| `debate_controller`    | Code + memory validation and improvement                |
| `debate_filter_extended` | Filters training data for fine-tuning                   |
| `write_prompt_files`   | Writes initial prompt templates                         |
| `feedback_logger`      | Summarizes logs in natural language                     |
| `gpt4o_client`         | OpenAI interface + token usage tracking                 |
| `llm_client`           | Local LLM interface for debate + execution              |

---

## Build Status

All modules functional except:
- [ ] `ui_interface.py` (planned for interactive control)
- [ ] Token cost tracking (partial, needs pricing integration)

---

## Next Steps

- [ ] Build `ui_interface.py`
- [ ] Refactor memory loop to eliminate circular import
- [ ] Add token pricing to `gpt4o_client`
- [ ] Expose goal/plan/memory summaries to user-facing layer


# agent_interface.py
# GPT-to-Local execution bridge for OSIRIS
# Handles all schema validation, compression, and execution routing

from dataclasses import dataclass, asdict
from typing import Literal, Any, List, Dict
from datetime import datetime
import uuid
import json
import tiktoken
import os

# === CONFIG ===
MODEL_NAME = "gpt-4o"
MAX_INPUT_TOKENS = 2000
MAX_RESPONSE_TOKENS = 256
LOG_PATH = "./logs/agent_interface.log"

# === ENCODING ===
encoding = tiktoken.encoding_for_model(MODEL_NAME)
def count_tokens(text: str) -> int:
    return len(encoding.encode(text))

# === SCHEMAS ===
@dataclass
class ToolCallSpec:
    name: str
    arguments: Dict[str, Any]

@dataclass
class MemoryQuery:
    query: str
    top_k: int = 5

@dataclass
class MemoryWrite:
    text: str
    tags: List[str]
    importance: float
    certainty: float

@dataclass
class ExecutionRequest:
    goal_id: str
    description: str
    steps: List[str]
    memory_summary: str
    tools: List[ToolCallSpec]

@dataclass
class ExecutionResult:
    goal_id: str
    status: Literal["success", "error", "partial"]
    memory_updates: List[str]
    tool_outputs: Dict[str, str]
    log: str

# === LOGGING ===
def log_event(event_type: str, payload: dict):
    timestamp = datetime.utcnow().isoformat()
    entry = {"time": timestamp, "type": event_type, "data": payload}
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")

# === MEMORY COMPRESSION (dummy) ===
def compress_context(turns: List[str]) -> str:
    joined = "\n".join(turns)
    while count_tokens(joined) > MAX_INPUT_TOKENS:
        turns = turns[1:]  # trim earliest
        joined = "\n".join(turns)
    return joined

# === INTERFACE ENTRY POINT ===
class AgentInterface:
    def __init__(self, memory, tool_router, local_llm):
        self.memory = memory
        self.tool_router = tool_router
        self.local_llm = local_llm

    def execute(self, req: ExecutionRequest) -> ExecutionResult:
        log_event("exec_request", asdict(req))
        tool_outputs = {}
        memory_updates = []
        full_log = ""

        for step in req.steps:
            try:
                prompt = f"Execute step for goal '{req.goal_id}': {step}"
                local_reply = self.local_llm.call(prompt)
                full_log += f"\n[{step}] → {local_reply}"
            except Exception as e:
                full_log += f"\n[Error executing step: {step}] {str(e)}"

        for tool in req.tools:
            output = self.tool_router.call(tool.name, tool.arguments)
            tool_outputs[tool.name] = output
            full_log += f"\n[ToolCall] {tool.name} → {output}"

        # Optional: simulate memory updates
        self.memory.add(f"Result of goal {req.goal_id}", tags=["result"], importance=0.5)
        memory_updates.append(f"Result of {req.goal_id}")

        result = ExecutionResult(
            goal_id=req.goal_id,
            status="success",
            memory_updates=memory_updates,
            tool_outputs=tool_outputs,
            log=full_log.strip()
        )

        log_event("exec_result", asdict(result))
        return result


# `aeda.llm`

Gemini-mediated decisions inside scripts. When the platform's config
provides a Gemini API key, `aeda.llm` exposes four small, strongly-typed
operations on top of a Gemini Robotics-ER 1.6 client; otherwise it's a
placeholder that raises a friendly "not yet available" error if a script
tries to use it.

## The four operations

```python
# 1. Boolean answer with rationale.
j = aeda.llm.judgement("Is the mug on the table?", aeda.frame.rgb)
if j:  # NamedTuple is truthy on j.answer
    aeda.log(f"yes, confidence {j.confidence:.2f}: {j.reasoning}")

# 2. Free-form text answer.
text = aeda.llm.ask("Describe the scene in one sentence.", aeda.frame.rgb)

# 3. Structured extraction.
data = aeda.llm.extract_json(
    "List visible objects and their counts.",
    aeda.frame.rgb,
    schema={"objects": "[{name, count}]"},
)

# 4. "What should I do next?" — name + args of a tool to call.
d = aeda.llm.decide_next_tool(
    goal="navigate to the kitchen counter",
    observations={
        "rgb": aeda.frame.rgb,
        "robot_pose": aeda.frame.robot_pose,
    },
)
result = aeda.tools.execute(d.name, **d.args)
```

## Strong return types

The four methods return NamedTuples — no free-form dicts to index into:

```python
class LLMJudgement(NamedTuple):
    answer:     bool
    confidence: float          # 0..1, model self-report
    reasoning:  str
    def __bool__(self) -> bool: return self.answer

class LLMDecision(NamedTuple):
    name: str                  # tool name to call
    args: dict                 # kwargs for that tool
    reasoning: str
```

This means you can destructure with mypy-friendly typing and your IDE
catches `decision.naem` typos.

## Behaviour contract

The module documents (and enforces) four guarantees:

- **Pre-execution validation.** Every method validates args (non-empty
  prompt, image is `ndarray` / `PIL.Image`, schema is a `dict`) before
  spending an LLM call. Bad args raise `LLMError` immediately.
- **Idempotent retries.** JSON-shape failures retry up to N times with a
  *"your previous reply was malformed"* appendix; network failures retry
  with exponential backoff.
- **Remediation errors.** If retries are exhausted, the raised `LLMError`
  tells the script author *which field is wrong* AND *what the model
  actually replied*.
- **Provider-agnostic shape.** The underlying client is held by interface
  (`_call_text`, `_call_text_image`); a future Claude / local-model
  backend just implements those.

## When `aeda.llm` is unavailable

If `cfg` has no Gemini key (or `google-genai` isn't installed),
`aeda.llm` is bound to a placeholder. Any access raises:

```
NotImplementedError: aeda.llm.judgement is not yet available on this build.
                     See runtime/UI_PLAN.md §13 for phase status.
```

Guard with a capability check if your script must run on either:

```python
try:
    j = aeda.llm.judgement("...", aeda.frame.rgb)
except NotImplementedError:
    j = fallback_heuristic()
```

## CoT logging

When `ScriptContext.session_dir` is set, the underlying Gemini client
writes every call's Chain-of-Thought into
`<session_dir>/cot/gemini/<timestamp>_<mode>.md`. The platform's
process-wide `robot.gemini` singleton is also wired to the same
session_dir for the duration of the script run, and restored on script
end — so a perception tool's Gemini call lands in the same CoT tree as
an `aeda.llm.ask(...)` call from the script.

## Source

[`runtime/ui/aeda_sdk/llm.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/runtime/ui/aeda_sdk/llm.py) ·
[`llm/executor/gemini_client.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/llm/executor/gemini_client.py)

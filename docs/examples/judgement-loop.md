# LLM judgement loop

Read the live camera frame, ask Gemini a yes/no question about it, and
branch on the answer. Demonstrates the smallest useful pattern with
`aeda.llm`.

!!! info "Requires `GEMINI_API_KEY`"
    If the runtime can't reach Gemini, `aeda.llm` is bound to a
    placeholder that raises `NotImplementedError` on first use. See
    [`aeda.llm` → when unavailable](../api/llm.md#when-aedallm-is-unavailable).

```python title="example_judgement_loop.py" linenums="1"
# Example: branch on an LLM judgement to decide what to do next.
# Requires aeda.llm to be configured (GEMINI_API_KEY).

rgb = aeda.frame.rgb
if rgb is None:
    aeda.log("no camera frame yet — bringup not complete?", kind="error")
else:
    j = aeda.llm.judgement("Is the workspace cluttered?", rgb)
    aeda.log({"answer": j.answer,
              "confidence": j.confidence,
              "reasoning": j.reasoning}, kind="json")
    if j and j.confidence > 0.5:
        aeda.log("would re-tidy now (placeholder)")
    else:
        aeda.log("workspace looks fine; idle")
```

## What's happening

- **`aeda.frame.rgb`** — fresh RGB frame from the live RGBD sensor. `None`
  means *either* no sensor on this platform *or* no frame has arrived yet
  (the script handles both with the same branch).
- **`aeda.llm.judgement(prompt, image)`** — Gemini Robotics-ER 1.6
  perception call. Returns an `LLMJudgement` NamedTuple
  `(answer: bool, confidence: float, reasoning: str)`. The tuple is
  truthy on `.answer`, so `if j:` does the right thing.
- The kept payload (`answer`/`confidence`/`reasoning`) is rendered as a
  JSON tree in the transcript — perfect for inspecting *why* Gemini said
  what it said while iterating on the prompt.

## Cost

A single `judgement` call is ~$0.0015 against Gemini Robotics-ER 1.6
(~1.15k input tokens + ~65 output). See the
[caching discussion in `aeda.llm`](../api/llm.md) for why per-call cost is
fixed regardless of session length.

## Extending it

- **From single shot to live loop.** Wrap in `while not aeda.cancel.is_set():` for
  a continuous judge-and-act loop. Every `aeda.frame.rgb` access calls
  `cancel.check()` internally, so the operator's halt fires on the next
  read.
- **From boolean to a typed decision.** Swap `judgement` for
  `aeda.llm.decide_next_tool(goal=..., observations=...)` — it returns
  an `LLMDecision(name, args, reasoning)` you can hand straight to
  `aeda.tools.execute(d.name, **d.args)`.

## Source

[`scripts/example_judgement_loop.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/scripts/example_judgement_loop.py)

## Next

- [Room scan + collect →](room-scan-and-collect.md) — a 146-line script that uses tools, navigates, and records.

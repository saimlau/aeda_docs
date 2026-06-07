# What is Aeda

Aeda is the **scripting interface** layer of the `modulated_system` stack. It
exists so that LLM-generated code (and humans dropping into the runtime
terminal) has a small, predictable, audited API to the robot — not a sprawl
of ROS topics or a thicket of robotics-framework calls.

## The shape

Every Aeda script runs inside a namespace pre-populated with a handful of
read-only objects plus one effect surface:

| Symbol | Kind | Purpose |
| --- | --- | --- |
| `aeda.tools` | dispatcher | Every registered `@tool` (motion, perception, recording, …). |
| `aeda.frame` | live view | Fresh RGB / depth / intrinsics / timestamp / `camera_pose` / `robot_pose` on every read. |
| `aeda.llm` | facade | Gemini-mediated `judgement`, `ask`, `extract_json`, `decide_next_tool`. Optional (placeholder when no API key). |
| `aeda.workspace` | facade | Read + mutate the UI workspace panel from inside the script. |
| `aeda.platform` | escape hatch | The live `Robot` + capability set, for things no `@tool` exposes. |
| `aeda.log` | function | Structured event: `kind="info" \| "json" \| "image" \| "error"`. |
| `aeda.cancel.check()` / `.is_set()` | functions | Raise `AedaInterrupt` (or query) when the operator has cancelled. |

That's it. No imports, no globals to thread through, no client objects to
construct. A script is the smallest unit of work the system runs.

## Why a snapshot, not a stream

`aeda.frame` is a **snapshot**, not a generator. Every read returns the
latest sensor frame at that moment — there's no queue, nothing blocks,
nothing accumulates. If you need time-aligned values, snapshot them once
into a local variable and check the timestamp.

This shape is deliberate: scripts that block on sensor streams are hard to
cancel, hard to reason about, and hard to retry. A snapshot API keeps every
line either an instantaneous read or an audited tool call.

## Why a tool catalog, not a Python library

Every action the system can take is a registered `@tool`. That registration
is the source of truth: it pins down the inputs/outputs/effects of every
action, gates them through the supervisor's tool catalog, and produces the
trace that lands in `worker/chat.jsonl` and `cot/_summary.json`.

If something isn't a tool, the worker can't do it. That constraint is the
feature.

## How it fits with the supervisor + worker

```
operator prompt  ──► supervisor (plans, gates, audits)
                          │
                          ▼
                     worker (writes scripts)
                          │
                          ▼ run_script(code)
                     aeda runtime
                   ┌──────┼──────┐
                aeda.tools  aeda.frame  aeda.cancel
                   │
              tool implementations
                   │
              ROS / cuRobo / Nav2 / MuJoCo
```

The supervisor never sees aeda; the worker never sees ROS. Aeda is the
membrane between LLM reasoning and the robot stack.

## Next

- **[Runtime architecture →](runtime-architecture.md)** — what's actually
  running when an Aeda script executes.
- **[API: tools →](../api/tools.md)** — the tool catalog itself.

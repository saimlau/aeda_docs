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
| `aeda.tools` | namespace | All `@tool`-registered functions (motion, perception, recording, …) |
| `aeda.frame` | snapshot | Latest RGB / depth / camera pose / base pose |
| `aeda.platform` | snapshot | Sim vs real, robot config, capability flags, session id |
| `aeda.log` | function | Structured logging into the session dir |
| `aeda.cancel.check()` | function | Raises `AedaInterrupt` if the operator cancelled |

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

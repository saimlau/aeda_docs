# Aeda

> A small Python SDK for **scripting robot motion + perception** inside the
> `modulated_system` supervisor/worker loop. Every observation a script reads
> comes from a single frame snapshot; every action goes out through a small,
> audited tool catalog; cancellation is one call.

Aeda is the API layer that LLM-generated scripts talk to when they control
the [TidyROS](https://github.com/Pengyu-Mo/tidyros_iphone) robot stack
(TidyBot++ base + Franka FR3 + wrist iPhone + MuJoCo sim). It is **not** a
robotics framework — it sits on top of one. Its job is to be the smallest,
most predictable interface between an autonomous agent's code and the
underlying control + perception stack.

## What's in the box

- **`aeda.tools.*`** — every registered `@tool` on the platform (motion,
  perception, trajectory generation, recording). Dispatched by attribute
  access; capability-filtered.
- **`aeda.frame.*`** — live sensor view: `rgb`, `depth`, `intrinsics`,
  `timestamp`, `camera_pose`, `robot_pose`. Every read is fresh (no caching)
  and is a cancel checkpoint.
- **`aeda.llm.*`** — Gemini-mediated decisions: `judgement`, `ask`,
  `extract_json`, `decide_next_tool`. Strongly-typed return values.
- **`aeda.workspace.*`** — introspect + mutate the runtime UI's workspace
  panel from a script.
- **`aeda.platform`** — escape hatch: the live `Robot` + `capabilities`
  frozenset for things no `@tool` exposes.
- **`aeda.log()`** — structured logging (`kind="info" | "json" | "image" | "error"`).
- **`aeda.cancel.check()` / `is_set()`** + **`aeda.AedaInterrupt`** —
  cooperative cancellation. `AedaInterrupt` inherits from `BaseException`
  so a stray `except Exception:` can't swallow it.
- **`run_script(script_text, ctx)`** — the runtime entry point. Returns a
  `RunHandle` for `halt()` / `wait()`.

## When you're using it

You're using Aeda whenever you:

- Write a script that controls the real or simulated TidyROS robot from the
  `modulated_system` worker.
- Drop into the runtime UI's Claude terminal to drive the robot interactively.
- Build a new tool you want the worker / supervisor to be able to call.

## Where to go next

<div class="grid cards" markdown>

- :material-package-down: **[Install](getting-started/installation.md)**

    Set up the conda env, clone the repo, run your first script.

- :material-play-circle: **[Quickstart](getting-started/quickstart.md)**

    A 20-line script that moves the arm and logs structured output.

- :material-cog: **[Concepts](concepts/overview.md)**

    Where Aeda sits in the supervisor / worker / runtime trifecta.

- :material-code-braces: **[API reference](api/tools.md)**

    Every namespace, what it returns, what it can raise.

- :material-script-text: **[Examples](examples/index.md)**

    Real scripts from the lab — a graded tour from 8 to 389 lines.

- :material-toolbox: **[Tool catalog](tools/index.md)**

    Every `@tool` (73 across 9 categories), auto-extracted from source with docstrings + GitHub links.

- :material-source-branch: **[Modules](modules/index.md)**

    A guided tour of the `modulated_system` repo layout — core, lower_level, llm, runtime.

</div>

## Source

Aeda lives at
[`modulated_system/runtime/ui/aeda_sdk/`](https://github.com/Pengyu-Mo/tidyros_iphone/tree/main/modulated_system/runtime/ui/aeda_sdk)
inside the [tidyros_iphone](https://github.com/Pengyu-Mo/tidyros_iphone)
repository. This documentation site lives in
[saimlau/aeda_docs](https://github.com/saimlau/aeda_docs).

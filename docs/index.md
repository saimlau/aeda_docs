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

- **`aeda.tools.*`** — every registered `@tool` (motion primitives, perception
  calls, trajectory generators, recording controls). One catalog, one
  entry point.
- **`aeda.frame.*`** — a read-only snapshot of the latest sensor frame: RGB,
  depth, camera pose, base pose. Scripts read it; they never block on it.
- **`aeda.cancel.check()`** + **`aeda.AedaInterrupt`** — cooperative
  cancellation. Operators raise (Ctrl-C, e-stop, supervisor abort); scripts
  surface.
- **`aeda.log()`** — structured logging into the runtime session directory.
- **`aeda.platform`** — read-only environment info (sim vs real, robot
  configuration, session id).
- **`run_script(code: str)`** — the tool the worker calls to execute a script.

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

</div>

## Source

Aeda lives at
[`modulated_system/runtime/ui/aeda_sdk/`](https://github.com/Pengyu-Mo/tidyros_iphone/tree/main/modulated_system/runtime/ui/aeda_sdk)
inside the [tidyros_iphone](https://github.com/Pengyu-Mo/tidyros_iphone)
repository. This documentation site lives in
[saimlau/aeda_docs](https://github.com/saimlau/aeda_docs).

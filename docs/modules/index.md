# Modules

A guided tour of the `modulated_system` repo layout. Read top-to-bottom
to get a feel for where every responsibility lives.

| Module | Role | Page |
| --- | --- | --- |
| `core/` | Dependency-free primitives: `Pose`, `Twist`, `@tool`, `ToolContext`, `Robot` ABC. The shapes every other module reads + writes. | **[Core →](core.md)** |
| `tools/` | Every `@tool` registered for the modulated stack — 73 of them, in 9 categories. | **[Tool catalog →](../tools/index.md)** |
| `lower_level/` | What tools stand on: camera-path generators, IK solvers, motion planners, executors, octomap collision, costmap utils. | **[Lower level →](lower-level.md)** |
| `llm/` | The Claude + Gemini integration: supervisor, worker, data-analyzer agents + the shared `_call_claude` / CoT machinery. | **[LLM agents →](llm.md)** |
| `runtime/` | Script execution, the runtime UI (FastAPI + browser), session-dir layout, the Aeda SDK itself. | **[Runtime →](runtime.md)** |
| `platforms/` | Platform-specific bindings (e.g. `tidyros_iphone`). Each implements `core.hardware.Robot`. | — |
| `scripts/` | Example Aeda scripts + utility runners (`run_aeda_cli.py`, `run_worker.py`, `run_supervisor.py`). | **[Examples →](../examples/index.md)** |
| `config/` | YAML configs (Nav2, octomap, model selection, capabilities). | — |
| `tests/` | Unit + integration tests. ~210 currently green. | — |
| `data/` | Reference dataset stats consumed by `data_analysis` tools. | — |

## How a request flows

```
operator (UI / CLI / worker REPL)
        │
        ▼
   runtime/ui   ─────────►   llm/supervisor     ─►   llm/data_analyzer
        │                       (plans, gates)        (one-shot reads)
        │                              │
        │                              ▼
        │                      plans/active.json (in session dir)
        │                              │
        │                              ▼
        │                       llm/worker
        │                       (writes Aeda scripts)
        │                              │
        │                              ▼ run_script(text, ctx)
        ▼                       runtime/ui/aeda_sdk  (the `aeda` namespace)
   runtime/control                    │
                                       ▼ aeda.tools.<name>(...)
                                  core/tool_contract.ToolRegistry.dispatch
                                       │
                                       ▼
                                  modulated_system/tools/<category>/<name>.py
                                       │
                                       ▼
                                  modulated_system/lower_level/<subpackage>/
                                       │
                                       ▼
                                  hardware (ROS / cuRobo / Nav2 / MuJoCo)
```

The top three layers are LLM-driven; the bottom three are pure Python.
The Aeda SDK sits exactly in the middle.

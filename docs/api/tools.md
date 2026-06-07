# `aeda.tools`

`aeda.tools` is the entry point to every registered tool on this platform.
Each tool is dispatched through the same `ToolRegistry.dispatch` that the
HTTP `/api/tools/{name}/run` route uses — capability filtering, parameter
resolution, and audit logging all behave identically.

## Dispatch — three forms

```python
# 1. Attribute access (canonical).
res = aeda.tools.detect_target(target_object_hint="red mug")

# 2. By computed name (when the name comes from data).
name = pick_next_tool()
res = aeda.tools.execute(name, target_object_hint="red mug")

# 3. The name argument is positional-only — tools whose own kwargs include
#    `name=` (e.g. register_labeled_object) don't collide:
res = aeda.tools.execute("register_labeled_object", name="mug_a")
```

!!! warning "kwargs only"
    Tools take **only keyword arguments**. Passing a positional arg raises
    `TypeError: tool 'X' only accepts keyword args; got positional (...)`.

## Catalog introspection

```python
aeda.tools.list()              # -> sorted list[str] of every available tool
aeda.tools.schema("detect_target")
# -> {"name": "...", "params": [...], "category": "...", "ui_hints": {...}}
```

`list()` reflects the **live** registry — a tool loaded mid-run is visible
on the next call. Capability filtering is respected: if the platform
doesn't expose `manipulator.move_relative` the tool isn't listed.

## What dispatch emits

Every call produces two events on the per-script event stream:

```
{"type": "tool_call_started",  "name": "...", "args": {...},
 "category": "...", "timestamp_unix": ...}

{"type": "tool_call_finished", "name": "...",
 "result": <summarized>, "error": null|"...",
 "latency_s": 0.123, "timestamp_unix": ...}
```

The result is JSON-summarized for the transcript (dicts trimmed to ≤16
keys, strings truncated past 240 chars). The script still receives the
**full** unsummarized return value.

## Return values

A tool returns whatever its underlying implementation returns — most
return a dict, but some return a `ToolResult` or a domain-specific type
(`generate_view_trajectory` returns a trajectory object, `detect_target`
returns a detection dict, etc.). Inspect the tool's schema or source for
the canonical shape:

```python
schema = aeda.tools.schema("detect_target")
aeda.log(schema, kind="json")
```

## Missing-tool errors

Attribute access for an unknown name raises `AttributeError` with a
helpful hint:

```
AttributeError: no tool named 'navigate_too' on this platform.
Available: ['detect_target', 'evaluate_episode', 'execute_trajectory',
            'find_feasible_params', 'generate_view_trajectory', ...]…
```

This is the same error a typo on any Python attribute would raise — your
script's `try/except` can handle it naturally.

## The `@tool` contract (for tool authors)

Each tool implementation is a Python function decorated with `@tool`,
takes a `ToolContext` as its first arg, and returns a JSON-serializable
result. See **[Guides: writing a tool](../guides/writing-a-tool.md)** for
the full walkthrough.

## Illustrative catalog

The canonical list is whatever `aeda.tools.list()` returns at runtime. As
a rough orientation:

- **Motion** — `navigate_to`, `move_camera_relative`, `rotate_joint`,
  `execute_trajectory`, `recover_arm`.
- **Trajectory generators** — `generate_view_trajectory`,
  `compute_parking_locations`, `find_feasible_params`.
- **Perception** — `detect_target`, `check_target_in_frame`.
- **Recording** — `start_recording`, `stop_recording`, `evaluate_episode`.
- **Memory / state** — `set_data_spec`, `reset_collection_state`,
  `reset_memory`.

## Source

- [`runtime/ui/aeda_sdk/tools.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/runtime/ui/aeda_sdk/tools.py)
  — the `Tools` facade.
- [`core/tool_contract.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/core/tool_contract.py)
  — `ToolRegistry`, `ToolContext`, `@tool`.
- [`modulated_system/tools/`](https://github.com/Pengyu-Mo/tidyros_iphone/tree/main/modulated_system/tools)
  — every registered tool implementation.

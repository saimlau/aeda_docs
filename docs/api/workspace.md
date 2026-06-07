# `aeda.workspace`

`aeda.workspace` lets scripts **introspect and mutate the runtime UI's
workspace mirror** — the same panel the user sees in the browser. The
script and the user share state: a module the script adds becomes a card
on the user's next `/api/workspace` poll, and a parameter the user
changes is visible on the script's next read.

## Reads

```python
mods = aeda.workspace.modules                  # list[dict] — every module
m = aeda.workspace.find("start_recording")     # first match, or None
m = aeda.workspace.get("uuid-1")               # by id, or None
```

Each module dict is a snapshot — the script can mutate the copy freely
without corrupting the source.

## Writes

```python
# Add a module to the workspace.
new_id = aeda.workspace.add("navigate_to", x=2.0, y=0.0, theta=0.0)

# Update its params.
aeda.workspace.set_params(new_id, {"x": 5.0})

# Run it (dispatches through the same registry that aeda.tools.* uses).
result = aeda.workspace.run(new_id)
```

Writes go through the same `runtime.ui.routes.workspace` mirror the HTTP
routes use, so the frontend picks them up on its next poll — the user
sees the new module appear (or the new params take effect) without a
reload.

## Why use `aeda.workspace` over `aeda.tools`?

| Use case | Use |
| --- | --- |
| Single tool call, no UI footprint | **`aeda.tools.*`** |
| Surface a tool call to the user as an editable card | `aeda.workspace.add(...)` |
| Build a UI panel from the script | `aeda.workspace.add` + `set_params` |
| Run a workspace module the user is currently editing | `aeda.workspace.run(uuid)` |

## Live registry, not a frozen snapshot

`aeda.workspace` dispatches via the **live** `ToolRegistry`. If the agent
loaded a new tool mid-run (rare but supported), `aeda.workspace.add` sees
it immediately — no script restart required.

## Source

[`runtime/ui/aeda_sdk/workspace.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/runtime/ui/aeda_sdk/workspace.py) ·
[`runtime/ui/routes/workspace.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/runtime/ui/routes/workspace.py)

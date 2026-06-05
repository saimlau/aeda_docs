# Runtime architecture

What's actually running when an Aeda script executes — the processes, the
IPC, and how cancellation propagates.

## Processes

| Process | Role |
| --- | --- |
| **Supervisor** (Claude Opus) | Plans tasks, gates tool calls, audits provenance. Reads `runtime/sessions/<id>/` like Claude Code reads a project. |
| **Worker** (Claude Opus) | Writes scripts and calls `run_script(...)`. Stable REPL with prompt caching. |
| **Aeda runtime** | Executes the script. Owns the tool catalog and the frame snapshot. Lives in `modulated_system/runtime/ui/aeda_sdk/`. |
| **Tool implementations** | Each `@tool` runs in the aeda runtime's process. Heavyweight tools (cuRobo planning, Gemini perception) may spawn subprocesses or call external services. |
| **NUCs** (real-robot only) | Base NUC runs the wheel controller + lidar; arm NUC runs the FCI loop + zerorpc bridge. |

The supervisor and worker are stateful Claude conversations. The Aeda
runtime is stateless per-script (each `run_script` call sets up a fresh
namespace).

## Where a script runs

When `run_script(code: str)` is invoked:

1. The worker calls the `run_script` `@tool`.
2. The Aeda runtime constructs a fresh namespace with the `aeda` object
   bound to the current session.
3. `exec(code, namespace)` runs the script in-process.
4. Every `aeda.log(...)` line lands in
   `runtime/sessions/<id>/worker/scripts/`.
5. Every `aeda.tools.*` call dispatches through the registered `@tool` and
   is recorded as a separate trace entry.
6. The return value (or exception) is captured and surfaced back to the
   worker as a structured tool result.

## Cancellation

Three things can cancel a script:

- **Operator Ctrl-C** — the runtime sets a cancel flag; the next
  `aeda.cancel.check()` raises `AedaInterrupt`.
- **Supervisor abort** — the supervisor writes to the cancellation channel;
  same effect.
- **Physical e-stop** — the NUC setpoint-staleness watchdog freezes the arm
  within ~0.4 s; the script eventually surfaces the freeze as a tool error.

Cancellation is **cooperative on the script side** (you have to call
`aeda.cancel.check()`), but **hard on the motion side** (the watchdog
freezes the arm regardless of the script's state). Long-running tools
(`navigate_to`, `execute_trajectory`, …) check the cancel flag internally
on a fixed cadence — you don't need to interleave manual checks.

## Frame snapshot

`aeda.frame` reads from the sensor-fuser cache:

- `aeda.frame.rgb` — latest iPhone RGB frame.
- `aeda.frame.depth` — latest ARKit depth map.
- `aeda.frame.camera_pose` — `T_base_camera` from the dynamic TF tree.
- `aeda.frame.base_pose` — `T_map_base` from Nav2 / SLAM.

Each attribute is `Optional` — `None` until the corresponding stream has
delivered its first sample. Scripts must None-guard before use.

## Session directory layout

Every run lands a structured directory at `runtime/sessions/<session_id>/`:

```
inputs.json
plans/{initial.json, active.json, history/}
notes/{active.md, history/}
worker/{chat.jsonl, scripts/, terminal.log}
supervisor/{chat.jsonl, data_analyzer/, captured_provenance.json}
cot/{_summary.json, worker/, supervisor/, data_analyzer/, gemini/}
episodes/<episode_id>/{episode.json, frames/, rgb/, depth/}
```

The supervisor reads this directory; the worker writes to it; the operator
audits it.

## Next

- **[API: tools →](../api/tools.md)** — the tool catalog and how tools are
  registered.
- **[Guides: writing a tool →](../guides/writing-a-tool.md)** — adding a
  new `@tool` to the catalog.

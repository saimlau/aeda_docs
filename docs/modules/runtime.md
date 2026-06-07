# `modulated_system/runtime/`

The execution + UI layer. What's actually running when an Aeda script
starts.

## Subpackages + key files

| Item | What it is |
| --- | --- |
| **`ui/`** | The FastAPI + browser UI. Token-auth REST API + WebSocket transcripts + the in-browser Claude terminal. Where the script box, the launcher cards, and the live RGB/depth tiles live. |
| **`ui/aeda_sdk/`** | The **Aeda SDK** itself — `Aeda`, `Tools`, `Frame`, `Platform`, `LLM`, `Workspace`, `Log`, `Cancel`, `run_script`, `RunHandle`. See the [API reference](../api/tools.md). |
| **`session_dir.py`** | Builds the per-run session directory layout (`inputs.json`, `plans/`, `notes/`, `worker/`, `supervisor/`, `cot/`, `episodes/`). The single source of truth for everything that happens during a run. |
| **`control.py`** | The runtime-control surface — top-level start/stop of supervisor / worker / launchers. |
| **`plan_worker.py`** | The simple-case fallback runner that walks `plans/active.json` straight through. Not the closed loop — that's the supervisor + worker REPL pair. |
| **`UI_PLAN.md`** | The internal UI roadmap (phases A–G). Worth a read if you're contributing to the frontend. |
| **`sessions/`** | Live + archived session directories. One per run. |
| **`notes/`** | The notes index the supervisor + worker share. |

## Session directory layout

Every run lands a structured tree at
`runtime/sessions/<session_id>/`:

```
inputs.json
plans/{initial.json, active.json, history/}
notes/{active.md, history/}
worker/{chat.jsonl, scripts/, terminal.log}
supervisor/{chat.jsonl, data_analyzer/, captured_provenance.json}
cot/{_summary.json, worker/, supervisor/, data_analyzer/, gemini/}
episodes/<episode_id>/{episode.json, frames/, rgb/, depth/}
```

The supervisor reads this directory; the worker writes to it; the
operator audits it via the UI's session-browser panel.

## What happens when you click "Run" in the UI

1. `runtime/ui/routes/script.py` receives the WebSocket open.
2. It constructs a `ScriptContext` from `RuntimeContext.current()` +
   a per-job emit callback that forwards events back to the WS.
3. Calls
   `runtime.ui.aeda_sdk.run_script(text, ctx)`
   ([details](../api/script.md)).
4. The script runs in a daemon thread; events stream to the browser as
   they happen.
5. The handle returned by `run_script` lives in the route handler so
   it can `halt()` on disconnect / explicit cancel.

## What "RuntimeContext" is

A process-wide singleton that holds:

- the live `Robot` object (locomotion, manipulators, sensors),
- the loaded `ToolRegistry`,
- the active `Config`,
- the legacy ROS `bridge` (for tools that still reach into ROS topics
  directly),
- the current session directory.

The supervisor + worker + script runtime all read from it. Tests build
their own with mocks.

## Sensor fuser

The RGBD path the live frame view stands on:

- `iphone_link` dynamic TF + fused pose from ARKit VIO.
- `/iphone/rgb` + `/iphone/depth` + camera_info.
- `iphone_world` fallback frame (intentionally surfaced as `None` in
  `aeda.frame.camera_pose` — see the [`aeda.frame` page](../api/frame.md#the-camera_pose-frame-guard)).

When the camera_pose silently falls back to `iphone_world`, planning /
unprojecting against it gives wrong world coords — that was the historic
`detect_target` drill bug. The frame guard prevents it from recurring.

## Source

[`modulated_system/runtime/`](https://github.com/Pengyu-Mo/tidyros_iphone/tree/main/modulated_system/runtime)

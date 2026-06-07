# `run_script`, `RunHandle`, `ScriptContext`

The runtime's entry point for executing user scripts. Most users never
call `run_script` themselves — the worker, the runtime UI, and the FastAPI
`/api/script/run` route all call it on the user's behalf. This page is for
people writing runtimes, harnesses, or tests around the SDK.

## `run_script`

```python
from runtime.ui.aeda_sdk import run_script, ScriptContext

handle = run_script(
    script_text: str,
    ctx: ScriptContext,
    *,
    job_id: Optional[str] = None,
    timeout_s: Optional[float] = None,
    extra_globals: Optional[dict[str, Any]] = None,
) -> RunHandle
```

Compiles `script_text`, spawns a daemon thread, and execs it with a fresh
`aeda` namespace bound in. **Returns immediately** with a `RunHandle`; the
script runs in the background. Caller controls the lifecycle via the
handle.

| Arg | Meaning |
| --- | --- |
| `script_text` | Python source — runs under `exec`, top-level statements only. |
| `ctx` | `ScriptContext` carrying the registry, robot, config, and event-emit callback. |
| `job_id` | Optional caller-supplied id; defaults to `"job_" + 12 hex chars`. |
| `timeout_s` | If set (and > 0), a watchdog flips `cancel.stop()` after the deadline. |
| `extra_globals` | Extra names injected alongside `aeda` (e.g. for tests). |

The script sees:

```python
# Always available in the script's globals:
aeda           # the Aeda namespace
AedaInterrupt  # bare name (== aeda.AedaInterrupt)
__builtins__   # standard Python builtins (not stripped — trust model)
```

## `ScriptContext`

```python
@dataclass
class ScriptContext:
    registry:    ToolRegistry
    robot:       Robot
    cfg:         Config
    emit:        Callable[[dict], None]  = lambda _e: None
    bridge:      Any                     = None    # legacy ROS bridge slot
    llm_client:  Any                     = None    # inject a stub LLM (tests)
    session_dir: Any                     = None    # path for CoT writes
```

The runtime constructs this from `RuntimeContext.current()` + a per-job
emit callback. Tests can build it directly with a stub registry / robot.

## `RunHandle`

```python
@dataclass
class RunHandle:
    cancel:        Cancel
    thread:        threading.Thread
    started_unix:  float
    job_id:        str

    def halt(self) -> None: ...               # cancel.stop()
    def wait(self, timeout: float | None = None) -> bool: ...
    @property
    def is_running(self) -> bool: ...
```

- `halt()` flips the cancel flag. The next `aeda.*` call inside the script
  raises `AedaInterrupt`.
- `wait(timeout)` joins the thread; returns `True` if it finished within
  the timeout, `False` if it's still running.
- `is_running` is the live thread state.

## Events the runtime emits

Everything the script does flows through `ctx.emit(event_dict)`. The
WebSocket handler in `runtime/ui/routes/script.py` forwards them to the
browser; tests and the worker REPL listen on the same callback.

```jsonc
// Script lifecycle
{"type": "started",   "job_id": "...", "timestamp_unix": ...}
{"type": "done",      "job_id": "...", "duration_s": ..., "timestamp_unix": ...}
{"type": "exception", "job_id": "...", "kind": "AedaInterrupt" | "...",
 "message": "...", "traceback": "...", "duration_s": ...}

// aeda.log(...)
{"type": "log", "kind": "info"|"json"|"image"|"error",
 "values": [...], "timestamp_unix": ...}

// aeda.tools.* dispatch
{"type": "tool_call_started",  "name": "...", "args": {...},
 "category": "...", "timestamp_unix": ...}
{"type": "tool_call_finished", "name": "...",
 "result": <summarized>, "error": null|"...",
 "latency_s": ..., "timestamp_unix": ...}

// aeda.llm.* (when enabled)
{"type": "llm_call", ...}
```

## `AedaInterrupt`

The exception raised when a script is halted. See
[`aeda.cancel`](platform.md#aedacancel) for the full cancellation contract.

## Halt limitations (worth knowing)

- Halt is **cooperative**. A script doing `while True: pass` with no aeda
  calls is uninterruptible — Python doesn't expose thread killing. The
  runtime surfaces a `"halt timed out"` warning.
- The thread is a **daemon**: process exit kills it. Uninterruptible
  scripts leak a daemon thread until process exit (documented limitation).
- Scripts that own external state (an open file, a hardware lock) should
  catch `AedaInterrupt`, clean up, then `raise` to let the runtime
  finalize the run.

## Minimal example

```python
from runtime.ui.aeda_sdk import run_script, ScriptContext

events: list[dict] = []
ctx = ScriptContext(
    registry=my_registry,
    robot=my_robot,
    cfg=my_cfg,
    emit=events.append,
)

handle = run_script("""
aeda.log("hello from a script")
cp = aeda.frame.camera_pose
aeda.log(f"camera at ({cp.x}, {cp.y}, {cp.z})" if cp else "no pose yet")
""", ctx)

handle.wait(timeout=10.0)
for e in events:
    print(e["type"], e)
```

## Source

[`runtime/ui/aeda_sdk/runtime.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/runtime/ui/aeda_sdk/runtime.py)

# `run_script` and `AedaInterrupt`

The script execution surface.

## `run_script(code: str) -> ScriptResult`

The `@tool` the worker calls to execute an Aeda script. The worker writes
Python in a string and hands it to `run_script`; the runtime sets up the
`aeda` namespace, executes the code, captures output + structured logs,
and returns a `ScriptResult`.

```python
from aeda import run_script

result = run_script("""
aeda.log("hello from a script")
cp = aeda.frame.camera_pose
aeda.log(f"camera={cp}")
""")
print(result.success, result.stdout, result.error)
```

### `ScriptResult`

| Field | Type | Meaning |
| --- | --- | --- |
| `success` | `bool` | True iff the script ran to completion without an uncaught exception. |
| `stdout` | `str` | Captured stdout. |
| `stderr` | `str` | Captured stderr. |
| `error` | `Optional[str]` | Traceback if the script raised. |
| `cancelled` | `bool` | True iff the script raised `AedaInterrupt`. |
| `tool_calls` | `list[dict]` | One entry per `aeda.tools.*` invocation: name + args + result + duration. |

## `AedaInterrupt`

Exception raised by `aeda.cancel.check()` when the operator has signalled
cancellation. See **[`aeda.cancel`](platform.md#aedacancel)** for the full
cancellation contract.

## What `run_script` does, step by step

1. Constructs a fresh `aeda` namespace bound to the current session.
2. Captures stdout/stderr.
3. `exec(code, {"aeda": ctx})`.
4. On exception:
    - If `AedaInterrupt`: returns with `cancelled=True, success=False`.
    - Otherwise: returns with `error=traceback, success=False`.
5. Persists the trace + logs to `runtime/sessions/<id>/worker/scripts/`.
6. Returns the `ScriptResult` to the worker.

## Source

- `run_script` and `AedaInterrupt`:
  [`modulated_system/runtime/ui/aeda_sdk/`](https://github.com/Pengyu-Mo/tidyros_iphone/tree/main/modulated_system/runtime/ui/aeda_sdk)

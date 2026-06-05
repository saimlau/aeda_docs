# `aeda.platform`, `aeda.log`, `aeda.cancel`

The remaining namespaces in the Aeda runtime — environment info, structured
logging, and cooperative cancellation.

## `aeda.platform`

Read-only environment metadata. Inspect to branch sim-vs-real or skip
steps that are unavailable on a given build.

| Field | Type | Meaning |
| --- | --- | --- |
| `is_sim` | `bool` | True iff running against MuJoCo. |
| `is_real` | `bool` | True iff running against the real robot. |
| `robot` | `str` | E.g. `"tidybot_plus_fr3_iphone"`. |
| `session_id` | `str` | Current `runtime/sessions/<id>` name. |
| `session_dir` | `str` (path) | Absolute path to the session dir. |

```python
if aeda.platform.is_sim:
    aeda.log("running in sim — skipping FCI handshake", kind="info")
```

## `aeda.log`

Structured logging into the session directory.

```python
aeda.log("hello", kind="info")
aeda.log(
    {"event": "park_attempt", "x": 1.2, "y": 0.3, "success": True},
    kind="data",
)
```

| Arg | Meaning |
| --- | --- |
| message | `str` or a JSON-serializable `dict`. |
| `kind` | One of `"info"`, `"warn"`, `"error"`, `"data"`. Controls UI rendering + colour. |

Log lines land in
`runtime/sessions/<id>/worker/scripts/<script_id>.log.jsonl`.

## `aeda.cancel`

Cooperative cancellation. The operator (Ctrl-C, e-stop, supervisor abort)
can raise an interrupt at any time; your script surfaces it by calling
`aeda.cancel.check()`.

### `aeda.cancel.check()`

```python
for i in range(10):
    aeda.tools.move_camera_relative(dz=0.01)
    aeda.cancel.check()    # raises AedaInterrupt if cancelled
```

### `aeda.AedaInterrupt`

The exception raised by `cancel.check()`. **Do not catch it** unless you
have cleanup that must run on cancellation — let it propagate so the
runtime can surface the cancel cleanly.

```python
try:
    long_running_work()
except aeda.AedaInterrupt:
    aeda.log("cleaning up partial state", kind="warn")
    cleanup()
    raise        # always re-raise
```

## Source

- Platform / log / cancel:
  [`modulated_system/runtime/ui/aeda_sdk/`](https://github.com/Pengyu-Mo/tidyros_iphone/tree/main/modulated_system/runtime/ui/aeda_sdk)

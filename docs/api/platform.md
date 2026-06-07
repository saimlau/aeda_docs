# `aeda.platform`, `aeda.log`, `aeda.cancel`

The remaining namespaces in the Aeda runtime — direct-hardware escape hatch,
structured logging, and cooperative cancellation.

## `aeda.platform`

The 5% case: things the user needs that aren't already a `@tool`. The 95%
case is `aeda.tools.*` and `aeda.frame.*`.

| Member | Type | Meaning |
| --- | --- | --- |
| `robot` | `core.hardware.Robot` | the **live** Robot object (locomotion, manipulators, sensors). Direct access — bypasses the tool catalog. |
| `name` | `str` | the robot's identifier (e.g. `"tidybot_plus_fr3_iphone"`). |
| `capabilities` | `frozenset[str]` | every capability the platform exposes, frozen at script-start. |
| `has(cap: str) -> bool` | method | sugar for `cap in capabilities`. |

```python
# Drive a tiny twist that no tool exposes.
from core.hardware.twist import Twist
aeda.platform.robot.locomotion.drive(Twist(vx=0.1, frame="body"))

# Read manipulator FK directly.
ee = aeda.platform.robot.manipulators[0].get_eef_pose()

# Branch on capability presence.
if aeda.platform.has("locomotion.global_planner"):
    aeda.tools.navigate_to(x=1.0, y=0.0, theta=0.0)
else:
    aeda.tools.move_relative(dx=0.5, dy=0.0)
```

!!! warning "Bypasses the tool audit log"
    Calls through `aeda.platform.robot` do **not** show up as
    `tool_call_started`/`tool_call_finished` events. Use the catalog
    (`aeda.tools.*`) whenever a tool exists; reserve `aeda.platform` for
    one-off escape-hatch cases.

## `aeda.log`

Structured logging into the per-run event stream.

```python
aeda.log("Found", n, "objects")               # kind="info"
aeda.log({"detections": ds}, kind="json")     # kind="json"
aeda.log(aeda.frame.rgb, kind="image")        # kind="image"
aeda.log("FCI handshake failed", kind="error")
```

### Signature

```python
aeda.log(*values: Any, kind: str = "info") -> None
```

### Kinds

| `kind` | Frontend renders as |
| --- | --- |
| `"info"` (default) | joined-with-space text |
| `"json"` | collapsible JSON tree |
| `"image"` | base64-encoded JPEG thumbnail (auto-encoded from a `(H, W, 3)` `uint8` ndarray; downscaled to ≤480 px wide) |
| `"error"` | red text with stack trace |

### Convenience methods

```python
aeda.log.info("hello")
aeda.log.json({"x": 1.0, "y": 2.0})
aeda.log.image(aeda.frame.rgb)
aeda.log.error("brake fired")
```

Values are made JSON-friendly automatically: nested dicts/lists recurse,
numpy ndarrays become `<ndarray shape=... dtype=...>` summaries (except in
`kind="image"`), and self-referential cycles emit `<cycle>` instead of
blowing the stack.

## `aeda.cancel`

Cooperative cancellation. The runtime (Ctrl-C from the operator,
supervisor abort, timeout watchdog) flips the cancel flag; your script
surfaces it.

### `aeda.cancel.check()`

```python
for i in range(10):
    aeda.tools.move_camera_relative(dz=0.01)
    aeda.cancel.check()    # raises AedaInterrupt if cancelled
```

Most scripts don't need to call `check()` explicitly — **every `aeda.*`
read or call already calls it at entry**. You only need a manual `check()`
inside a tight pure-Python loop that does no aeda work.

### `aeda.cancel.is_set()`

Non-raising query, useful when you'd rather branch than raise:

```python
while not aeda.cancel.is_set():
    do_one_round()
```

### `aeda.AedaInterrupt`

The exception raised by `check()`. It inherits from **`BaseException`**, not
`Exception`, so a bare `except Exception:` block will **not** swallow it.
This is deliberate — operator cancellation should never be silently caught.

```python
try:
    long_running_work()
except aeda.AedaInterrupt:
    aeda.log("cleaning up partial state", kind="info")
    cleanup()
    raise        # always re-raise — let the runtime surface the cancel
```

For convenience the bare name `AedaInterrupt` is also injected into script
globals, so both forms work:

```python
except aeda.AedaInterrupt: ...     # canonical
except AedaInterrupt: ...          # also fine (bare name injected by run_script)
```

### Pure-Python loops are uninterruptible

`while True: pass` without any aeda call inside cannot be halted —
Python doesn't expose thread-killing. The runtime surfaces a
**"halt timed out"** warning when this happens. Structure long loops
around aeda calls (or insert occasional `aeda.cancel.check()`) and the
halt fires in milliseconds.

## Source

- [`platform.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/runtime/ui/aeda_sdk/platform.py)
- [`log.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/runtime/ui/aeda_sdk/log.py)
- [`cancel.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/runtime/ui/aeda_sdk/cancel.py)

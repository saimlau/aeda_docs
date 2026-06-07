# `modulated_system/core/`

The dependency-free primitives every other subpackage stands on. Read
this once and you'll recognize the same types showing up in tool
signatures, sensor returns, and the LLM agents.

## What lives here

| Module | What it is |
| --- | --- |
| **`core/tool_contract.py`** | `@tool`, `ToolContext`, `ToolResult`, `ToolRegistry`. The decorator that registers a function as a tool, the context passed to every tool call, and the registry that dispatches them. The single source of truth for tool I/O. |
| **`core/hardware/__init__.py`** | The `Robot` ABC — `locomotion`, `manipulators`, `sensors`, `capabilities()`. Every platform (sim / tidyros_iphone / future) implements this. |
| **`core/hardware/pose.py`** | The `Pose` dataclass — flat `x, y, z, qx, qy, qz, qw, frame`. ROS REP-103 conventions (+X forward, +Z up, quat order xyzw). |
| **`core/hardware/twist.py`** | The `Twist` dataclass — `vx, vy, vz, wx, wy, wz, frame`. What `locomotion.drive(...)` consumes. |
| **`core/hardware/sensors.py`** | Sensor ABCs — `RGBDSensor`, `LidarSensor`. |
| **`core/hardware/recording.py`** | The recording session ABC — `start`, `stop`, `add_frame`. Backed per-platform (iPhone path writes RealEstate10K-compatible episodes). |
| **`core/config_loader.py`** | The `Config` object every agent + tool reads. YAML-backed, env-var-overridable. |

## `Pose` deserves the most attention

It's the shape every spatial value returns. A flat dataclass, no nested
attributes:

```python
@dataclass
class Pose:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    qx: float = 0.0
    qy: float = 0.0
    qz: float = 0.0
    qw: float = 1.0
    frame: str = "world"

    @classmethod
    def from_xy_theta(cls, x, y, theta_rad, frame="world") -> "Pose": ...

    def to_xy_theta(self) -> tuple[float, float, float]: ...

    @property
    def yaw(self) -> float: ...
```

A common gotcha for users coming from ROS / geometry_msgs is reaching for
`pose.position.x` — that doesn't exist. It's just `pose.x`.

## `@tool` — the registration contract

```python
from core.tool_contract import tool, ToolContext, ToolResult

@tool(name="say_hello", category="meta",
      capability="meta.greeting")
def say_hello(ctx: ToolContext, who: str = "world") -> ToolResult:
    """One-line summary for the catalog page (this docstring!)."""
    return ToolResult(success=True, message=f"hello, {who}")
```

Signature contract:

- **First arg is `ToolContext`** — the bridge to the live `Robot`, the
  `Config`, the `ToolRegistry`, the optional ROS `bridge`, and the
  per-run `cancel` flag + `session_dir`.
- **Remaining args are kwargs only** — enforced by the `Tools` dispatcher
  in `aeda.tools`.
- **Return is JSON-serializable** — `ToolResult` or a plain dict that
  serialises through the audit log + the WS transcript.
- **Cancellation is cooperative** — long-running tools poll
  `ctx.cancel.check()` (or the equivalent) so an operator halt fires
  promptly.

The full walkthrough lives at **[Writing a tool](../guides/writing-a-tool.md)**.

## Capabilities

Each `@tool` declares the platform capability it needs. `Robot.capabilities()`
returns the set the platform exposes; the `ToolRegistry` filters out tools
whose capability isn't present. That's why `aeda.tools.list()` on a
no-locomotion platform doesn't show `navigate_to`.

Common capability strings:

| Capability | Means |
| --- | --- |
| `locomotion.holonomic` | base can move sideways without rotating first |
| `locomotion.global_planner` | Nav2 (or equivalent) is up |
| `manipulator.arm_7dof` | 7-DOF arm available |
| `sensor.rgbd` | platform has an RGBD sensor |
| `meta.*` | tool catalog / memory / supervisor I/O |

## Source

[`modulated_system/core/`](https://github.com/Pengyu-Mo/tidyros_iphone/tree/main/modulated_system/core)

# `aeda.frame`

`aeda.frame` is the **live sensor view** available to every Aeda script. Each
attribute access reads the latest value from the sensor at the moment of the
read.

!!! info "No caching — every read is a fresh read"
    `aeda.frame.rgb` does **not** return a memoized copy. Each access touches
    the live RGBD sensor and returns whatever it has right now. If you want
    a frozen value, capture it once at the top of a block:
    `rgb = aeda.frame.rgb`.

!!! info "Every read is a cancel checkpoint"
    Each attribute call runs `aeda.cancel.check()` on entry, so a halt
    fires immediately inside polling loops like
    `for _ in range(100): img = aeda.frame.rgb`.

## Fields

| Field | Type | `None` means |
| --- | --- | --- |
| `rgb` | `np.ndarray`, `uint8`, shape `(H, W, 3)` | no RGBD sensor on this platform, or no frame yet |
| `depth` | `np.ndarray`, `float32`, shape `(H, W)` (metres) | same |
| `intrinsics` | `dict` `{fx, fy, cx, cy, w, h}` | same |
| `timestamp` | `float` (seconds since epoch) | same |
| `camera_pose` | `core.hardware.Pose` in the **`base_odom`** frame | TF not ready, **or** TF silently fell back to `iphone_world` (treated as not-ready) |
| `robot_pose` | `tuple[float, float, float]` — `(x, y, yaw_rad)` in world | platform has no locomotion / pose not published yet |

## `Pose` shape

`camera_pose` returns a `core.hardware.Pose` — a flat dataclass:

```python
cp = aeda.frame.camera_pose
# cp.x, cp.y, cp.z          translation
# cp.qx, cp.qy, cp.qz, cp.qw  quaternion (ROS REP-103, +Z up, +X forward)
# cp.frame                   the string "base_odom" when non-None
# cp.yaw                     property — 2D yaw extracted from the quaternion
# cp.to_xy_theta()           -> (x, y, yaw)
```

## Usage

```python
# 1. Snapshot once if you'll use the same value multiple times.
cp = aeda.frame.camera_pose
if cp is None:
    raise SystemExit("waiting for first camera frame (or TF fell back)")
aeda.log(f"camera at ({cp.x:.3f}, {cp.y:.3f}, {cp.z:.3f}) in {cp.frame}")

# 2. None-guard every other field too — platforms without an RGBD sensor
#    return None across the board.
img = aeda.frame.rgb
if img is None:
    aeda.log("no rgb available on this platform", kind="info")

# 3. Robot pose is a tuple, not a Pose.
rp = aeda.frame.robot_pose
if rp is not None:
    x, y, yaw_rad = rp
```

## The `camera_pose` frame guard

`camera_pose` deliberately returns `None` if the camera-to-world TF chain
silently falls back to the ARKit-init `iphone_world` frame (which would
give wrong world coordinates — the cause of the historic `detect_target`
drill bug). When you read `camera_pose` you are guaranteed either:

- `None` — TF isn't ready yet; retry, or
- a `Pose` whose `.frame == "base_odom"` — safe to plan / unproject against.

## Source

[`modulated_system/runtime/ui/aeda_sdk/frame.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/runtime/ui/aeda_sdk/frame.py) ·
[`core/hardware/pose.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/core/hardware/pose.py)

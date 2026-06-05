# `aeda.frame`

`aeda.frame` is the **read-only sensor snapshot** available to every Aeda
script. It exposes the latest cached values from the sensor fuser at the
moment the script reads them.

!!! note "Field signatures illustrative"
    The fields below are a high-level summary; see the source at
    [`modulated_system/runtime/ui/aeda_sdk/`](https://github.com/Pengyu-Mo/tidyros_iphone/tree/main/modulated_system/runtime/ui/aeda_sdk)
    for canonical typing.

## Fields

| Field | Type | Source | `None` means |
| --- | --- | --- | --- |
| `rgb` | `Optional[np.ndarray]` | iPhone ARKit | no RGB frame yet |
| `depth` | `Optional[np.ndarray]` (metres) | iPhone ARKit | no depth frame yet |
| `camera_intrinsics` | `Optional[CameraInfo]` | iPhone ARKit | no intrinsics yet |
| `camera_pose` | `Optional[Pose]` | `iphone_link` dynamic TF | no TF yet |
| `base_pose` | `Optional[Pose]` | `base_odom` / `map` TF | no nav fix yet |
| `ts` | `Optional[float]` | latest fuser timestamp (unix s) | no frames at all |

## Usage

```python
cp = aeda.frame.camera_pose
if cp is None:
    raise SystemExit("waiting for first camera frame")

x, y, z = cp.position.x, cp.position.y, cp.position.z
qx, qy, qz, qw = (
    cp.orientation.x, cp.orientation.y,
    cp.orientation.z, cp.orientation.w,
)
```

## None-guard everything

Every field is `Optional`. A fresh sim or a cold-boot real robot may not
have every stream available immediately — guard before use:

```python
img = aeda.frame.rgb
if img is None:
    aeda.log("no rgb yet, falling back to detect-only flow", kind="warn")
    ...
```

## Snapshot semantics

- Each attribute read returns the **latest** cached value at that moment.
- Two reads in the same script may see **different** values (the fuser
  updates in the background).
- If you need time-aligned values, snapshot once into a local:

    ```python
    cp = aeda.frame.camera_pose
    ts = aeda.frame.ts
    ```

## Source

- Frame namespace:
  [`modulated_system/runtime/ui/aeda_sdk/`](https://github.com/Pengyu-Mo/tidyros_iphone/tree/main/modulated_system/runtime/ui/aeda_sdk)
- Sensor fuser:
  [`modulated_system/runtime/`](https://github.com/Pengyu-Mo/tidyros_iphone/tree/main/modulated_system/runtime)

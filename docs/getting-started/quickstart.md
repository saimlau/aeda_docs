# Quickstart

A 20-line Aeda script that reads the latest camera frame, calls a motion
tool, and logs structured output.

## 0. Activate the env

```bash
conda activate nav2_robostack
cd tidyros_iphone
```

## 1. Start the simulator

```bash
python modulated_system/scripts/launch_sim.py
```

This brings up the MuJoCo TidyBot++ scene, the arm zerorpc bridge, and the
fake iPhone publishers.

## 2. Write your first script

Save this as `quick.py`:

```python
# quick.py — first Aeda script
aeda.log("starting quickstart")

# Read the live camera pose. None-guard: the TF chain may not be ready yet,
# or it may have fallen back to the iphone_world frame (in which case
# camera_pose intentionally returns None to keep you from planning against
# wrong world coords).
cp = aeda.frame.camera_pose
if cp is None:
    raise SystemExit("no camera_pose yet — is the sim running, TF up?")

# Pose is a flat dataclass — .x/.y/.z/.qx/.qy/.qz/.qw/.frame/.yaw, plus
# .to_xy_theta(). NOT nested .position.x.
aeda.log(f"camera at ({cp.x:.3f}, {cp.y:.3f}, {cp.z:.3f}) in {cp.frame}")

# Nudge the camera 5 cm up. move_camera_relative is a registered @tool;
# aeda.tools dispatches by attribute access and only accepts kwargs.
res = aeda.tools.move_camera_relative(dz=0.05, speed_factor=0.10)
aeda.log({"move_result": res}, kind="json")

# Most scripts don't need this — every aeda.* call already does cancel.check()
# on entry. Useful inside tight pure-Python loops that do no aeda work.
aeda.cancel.check()
aeda.log("done")
```

## 3. Run it

Two equivalent options:

=== "From the worker REPL"

    ```bash
    python -m modulated_system.llm.worker
    > /run quick.py
    ```

=== "As a direct tool call"

    ```bash
    python -c "from aeda import run_script; print(run_script(open('quick.py').read()))"
    ```

Either way, structured log lines land in
`runtime/sessions/<session_id>/worker/scripts/`.

## What just happened

- `aeda.frame.camera_pose` returned a typed snapshot of the **latest** camera
  pose from the sensor fuser — no blocking, returns `None` if no frame has
  arrived yet.
- `aeda.tools.move_camera_relative(...)` invoked the registered `@tool`; the
  call went through the modulated executor → cuRobo planner → arm zerorpc
  bridge.
- `aeda.cancel.check()` would have raised `aeda.AedaInterrupt` if the
  operator had Ctrl-C'd between the previous line and this one.

## Next

- **[Concepts: overview →](../concepts/overview.md)** — where Aeda sits in
  the bigger picture.
- **[API: tools →](../api/tools.md)** — the full tool catalog.

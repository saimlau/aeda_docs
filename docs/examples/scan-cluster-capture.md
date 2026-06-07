# Scan → cluster → capture

The most ambitious example: a 389-line end-to-end pipeline that sweeps
joint 0 of the arm, runs perception at each step, clusters every detection
spatially, then approaches each cluster and captures multiple trajectories
around each item. This is the script the lab uses for autonomous
data-collection runs.

The script lives at
[`scripts/aeda_scan_cluster_capture.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/scripts/aeda_scan_cluster_capture.py).

## What it demonstrates

- A full agentic loop assembled out of `aeda.tools.*` primitives — no
  imports of perception / planning libraries, just tool calls.
- **In-script brake recovery**: every motion call goes through a small
  `run_motion(fn, what)` helper that intercepts an arm reflex/brake,
  calls `recover_arm`, and retries once.
- **Adaptive parameters per cluster**: candidate trajectory radii are
  sampled from a normal distribution centred on the current
  camera→target distance, so a near cluster and a far cluster get
  different feasibility sweeps.
- **Spatial clustering of detections** to dedupe the same item seen from
  multiple sweep angles before approaching.

## Phase map

```
A. SWEEP
   rest pose → drive joint 0 to −150° → step by ≤20° to +150°.
   At each step:
     • list_objects_in_view  (RAM++)         ← open-set labels
     • detect_target(label)  (SAM3 + ER 1.6) ← (label, xyz_world, conf)
   Collect every hit.

B. CLUSTER
   Spatial clustering of every detection (adaptive-k; centroid = mean).
   Yields a list of clusters, nearest first.

C. PER CLUSTER (loop)
   face cluster (yaw the base)
   far look-at orbit (positive elevation if reachable)
   identify closest base-approach edge
   navigate_to(cluster, offset_m=0.9)
   survey pose (re-establish camera frame after motion)
   near look-at orbit
   re-detect with RAM++/SAM3 (active_cluster perception)
   FOR each item in the cluster:
     find_feasible_params over trajectory types (orbit, bezier, ...)
     pick top-2 by score
     for each → execute_trajectory while start_recording / stop_recording
     move_relative(dz=+0.3)        ← back up before next item
   reset arm to rest

D. RETURN
   navigate back to the start origin.
```

## Key idioms (skim-friendly)

### 1. The brake-recovery wrapper

```python
def run_motion(fn, what):
    """Call a motion tool; on reflex/brake, recover once and retry."""
    res = fn()
    if _is_brake(res):
        aeda.log({"step": "brake_detected_recover_retry", "what": what},
                 kind="json")
        aeda.tools.recover_arm()
        res = fn()
    return res
```

Every motion-producing tool call in the script goes through this. One
retry, no retry-forever loops — the operator stays in control of a
genuinely stuck robot.

### 2. The joint-0 sweep, in ≤20° hops

```python
J0_SCAN_DEG = 150          # FR3 joint 0 limit is ~±166°; stay clear of it
J0_STEP_DEG = 20           # small hops avoid tripping the cartesian-reflex
SCAN_SPEED  = 0.10

for target_deg in range(-J0_SCAN_DEG, J0_SCAN_DEG + 1, J0_STEP_DEG):
    run_motion(
        lambda: aeda.tools.rotate_joint(
            joint_idx=0,
            target_rad=math.radians(target_deg),
            speed_factor=SCAN_SPEED,
        ),
        what=f"j0→{target_deg}°",
    )
    aeda.cancel.check()
    detect_in_view(detections)     # RAM++ + SAM3 + xyz_world
```

The hops + the speed cap are both lessons learned from the field — a
single 165° jump tripped a reflex on the first lab run, and the
near-±166° limit poses themselves can trip a different reflex even at low
speed.

### 3. Distance-aware feasibility search

```python
# Inside find_feasible_params: seed radii from a normal centred on the
# current camera→target distance, so a 0.4 m-away cluster doesn't get
# the same candidate radii as a 2.5 m-away one.
prefs["radius_center_m"] = float(np.linalg.norm(camera_xyz - target_xyz))

candidates = aeda.tools.find_feasible_params(
    trajectory_type="sphere_orbit",
    target_xyz=item_xyz,
    user_prefs=prefs,
)
top_two = sorted(candidates, key=lambda c: -c["score"])[:2]
```

### 4. Capture window

```python
for cand in top_two:
    aeda.tools.start_recording(
        target_object_id=f"{cluster_id}/{item['label']}/{cand['variant_id']}",
        ...
    )
    aeda.tools.execute_trajectory(waypoints=cand["waypoints"])
    aeda.tools.stop_recording()
```

`start_recording` / `stop_recording` bracket the trajectory; the runtime
captures every RGB + depth + camera_pose frame between them into
`runtime/sessions/<id>/episodes/<episode>/`.

## Why read the source

The phase map above is the gist, but the script has ~30 small operational
details (e.g. when to reset the arm vs lower it between clusters, how
`face_point` picks the yaw, what counts as a brake) that are worth
reading once if you're going to run this on real hardware. Open the full
file:

[`scripts/aeda_scan_cluster_capture.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/scripts/aeda_scan_cluster_capture.py)

## Source

- [`scripts/aeda_scan_cluster_capture.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/scripts/aeda_scan_cluster_capture.py) — the pipeline.
- [`tools/perception/list_objects_in_view.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/perception/list_objects_in_view.py) — RAM++ open-set labelling.
- [`tools/perception/detect_target.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/perception/detect_target.py) — SAM3 + Robotics-ER 1.6 point + bbox + xyz_world.
- [`tools/trajectory/find_feasible_params.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/trajectory/find_feasible_params.py) — IK-feasible parameter sweep.

## Next

- [Examples index ←](index.md)
- [API: aeda.tools →](../api/tools.md)

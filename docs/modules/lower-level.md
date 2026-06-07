# `modulated_system/lower_level/`

The primitives that `@tool` implementations stand on. Nothing in here is
exposed to scripts directly — but every `aeda.tools.*` call eventually
lands on one of these subpackages.

| Subpackage | What it does |
| --- | --- |
| **`camera_paths/`** | Pure-geometry waypoint generators — `sphere_orbit`, `look_away_return`, `bezier`, `linear_aimed`, etc. Each defines a `generate(...)` plus a `search_grid(...)` classmethod used by `find_feasible_params`. |
| **`base_paths/`** | (Retired; the camera-centric pipeline replaced it; kept for historical traces.) |
| **`trajectory_compiler.py`** | Converts a sequence of `CameraWaypoint`s (pos + quat) into a whole-body plan — base xyθ + arm 7-DOF — for the executor. |
| **`ik_solvers/`** | The IK back-ends. Mink (default; supports collision avoidance) and J-PARSE. The executor returns `infeasible_waypoints` rather than auto-aborting on a missed pose. |
| **`motion_planners/`** | cuRobo-backed reach/plan/retime — used by `execute_trajectory`'s whole-body planner. Wraps cuRobo behind a shared façade so the gemini-system can keep its Mink path. |
| **`executors/`** | The streaming arm executor + base controller bridge. Sends pre-validated waypoint streams to the NUC arm relay + the base controller node. |
| **`octomap_collision/`** | Octomap-backed collision checker for cuRobo's world-collision. Anchors voxel-cull around the arm base (not the odom origin) and surfaces collisions per waypoint. |
| **`costmap_utils/`** | Footprint-aware approach-path checks. Used by `compute_parking_locations` to reject parks that drive the base through a lethal cell. |
| **`feasibility/`** | IK-feasibility sweep machinery. `find_feasible_params` walks a `search_grid` from a camera-path generator and IK-verifies each candidate. |
| **`reach_map/`** | Pre-built FR3 reach maps used to seed candidate radii cheaply before running the full IK sweep. |
| **`exploration/`** | Frontier-explorer wired to the SLAM map. Lets the agent autonomously expand the known map. |
| **`perception/`** | RAM++ open-set labelling + SAM3 mask + depth back-projection helpers that the perception tools compose into `detect_target` / `list_objects_in_view`. |
| **`spatial_query/`** | TF lookups, frame conversions, depth-to-world unprojection helpers. |
| **`state_alignment/`** | Aligns recorded episodes to a canonical world frame for export to RealEstate10K / CameraCtrl. |
| **`arm_relay/`** | The zerorpc client that talks to `arm_zerorpc_bridge.py` on the arm NUC. |

## When a tool runs

A typical motion tool — say `generate_view_trajectory` then
`execute_trajectory` — chains through this stack:

```
aeda.tools.generate_view_trajectory(...)
        │
        ▼  lower_level/camera_paths/sphere_orbit.py
   CameraWaypoint list  (pos + quat per waypoint)
        │
        ▼  lower_level/trajectory_compiler.py
   {base xyθ stream, arm 7-DOF stream}
        │
        ▼  lower_level/ik_solvers/mink_solver.py  +  motion_planners/curobo.py
   IK-verified per-waypoint joint targets   ←   lower_level/octomap_collision/
        │
        ▼  lower_level/executors/streaming_arm.py
                              + executors/base_controller_bridge.py
   commands streamed to arm NUC / base NUC
```

The script never sees any of this — it just calls
`aeda.tools.execute_trajectory(waypoints=...)`. The lower-level stack is
where to look when a tool reports an error you can't explain from the
tool-level docs alone.

## Source

[`modulated_system/lower_level/`](https://github.com/Pengyu-Mo/tidyros_iphone/tree/main/modulated_system/lower_level)

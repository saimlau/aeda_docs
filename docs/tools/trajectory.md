# Tools — `trajectory` (5)

Design camera paths. View-trajectory generators (sphere_orbit, look_away_return, bezier, …), feasibility search, whole-body execution.

## In this category

- [`compute_params_for_base_pose`](#compute_params_for_base_pose) — Analytic feasible (alpha, phi) region for sphere_orbit around target T from a fixed (or auto-yaw) base pose. When base_yaw_rad is None, picks byaw* facing T for max reach. Returns per-phi alpha arcs + their intersection.
- [`compute_parking_locations`](#compute_parking_locations) — Top-k base parking poses around T that make the requested sphere_orbit sweep reachable. Per candidate auto-picks byaw* facing T. Sorted by distance to current robot pose (less navigation = cheaper). Infeasible candidates are returned with +1000 cost so the operator can see why.
- [`execute_trajectory`](#execute_trajectory) — Drive the robot through a precomputed camera-pose waypoint list. Internally runs solve_trajopt_chain (per-chord cuRobo TrajOpt with collision/SDF push on every internal knot, terminal pose pinned at each waypoint), Cartesian-velocity-bounded retime to kill dwell at chord seams, a costmap base-filter, and a 100 Hz uniform resample, then streams through WholeBodyTrajectoryExecutor (MPC base tracker + arm streaming). speed_factor (default 0.3) is the ONLY velocity throttle. Pair with `generate_view_trajectory`, or pass any list with the matching shape: {pos: [x,y,z], quat_wxyz: [w,x,y,z], label?} (legacy {cam_pos, look_at} also accepted).
- [`find_feasible_params`](#find_feasible_params) — Search for camera-path generator parameters whose every waypoint is reachable from the current (or locked) base pose. Uses the precomputed FR3 reach map — pure-IK / joint-limit feasibility, scene-blind. Returns the top-K candidate parameter sets sorted by feasibility fraction and arc/length coverage. Pair the chosen params with `generate_view_trajectory` + `execute_trajectory` to actually run a trajectory (octomap obstacle avoidance is handled by trajopt during execution, not here). PREFER `compute_params_for_base_pose` (closed-form analytic) for new scripts when the base is already parked, or `compute_parking_locations` when you want the helper to pick the parking spot. This grid-search version retains octomap-clearance scoring and is kept for callers that rely on the `min_camera_clearance_m` knob.
- [`generate_view_trajectory`](#generate_view_trajectory) — Generate camera-view waypoints around a target. Picks a camera_paths generator (sphere_orbit / linear_aimed / linear_fixed / approach_retreat / look_away_return / bezier). Returns the waypoint list WITHOUT driving anything — pair with `execute_trajectory` for the full pipeline. target_x/y/z are all required (world frame, m).

---

## `compute_params_for_base_pose`

**Module:** [`modulated_system/tools/trajectory/compute_params_for_base_pose.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/trajectory/compute_params_for_base_pose.py#L130)  ·  **Python function:** `compute_params_for_base_pose`  ·  **Description source:** decorator `description=`

Analytic feasible (alpha, phi) region for sphere_orbit around target T from a fixed (or auto-yaw) base pose. When base_yaw_rad is None, picks byaw* facing T for max reach. Returns per-phi alpha arcs + their intersection.

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `target_x` | `number` | ✓ | — | Target T world X (m). |
| `target_y` | `number` | ✓ | — | Target T world Y (m). |
| `target_z` | `number` | ✓ | — | Target T world Z (m). |
| `trajectory_type` | `string` | — | `'sphere_orbit'` | Only 'sphere_orbit' supported in v1. |
| `r` | `number` | ✓ | — | Orbit radius (m). |
| `phi_lo_deg` | `number` | ✓ | — | Lower elevation bound (deg). |
| `phi_hi_deg` | `number` | ✓ | — | Upper elevation bound (deg). |
| `base_x` | `number` | — | — | Base X (m); omit to use current robot pose. |
| `base_y` | `number` | — | — | Base Y (m). |
| `base_yaw_rad` | `number` | — | — | Base yaw (rad). When omitted (or null), the helper picks byaw* facing T for minimum reach distance. |

---

## `compute_parking_locations`

**Module:** [`modulated_system/tools/trajectory/compute_parking_locations.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/trajectory/compute_parking_locations.py#L100)  ·  **Python function:** `compute_parking_locations`  ·  **Description source:** decorator `description=`

Top-k base parking poses around T that make the requested sphere_orbit sweep reachable. Per candidate auto-picks byaw* facing T. Sorted by distance to current robot pose (less navigation = cheaper). Infeasible candidates are returned with +1000 cost so the operator can see why.

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `target_x` | `number` | ✓ | — | Target T world X (m). |
| `target_y` | `number` | ✓ | — | Target T world Y (m). |
| `target_z` | `number` | ✓ | — | Target T world Z (m). |
| `r` | `number` | ✓ | — | Orbit radius (m). |
| `phi_lo_deg` | `number` | ✓ | — | Lower elevation bound (deg). |
| `phi_hi_deg` | `number` | ✓ | — | Upper elevation bound (deg). |
| `top_k` | `integer` | — | `4` | How many candidates to return. |
| `trajectory_type` | `string` | — | `'sphere_orbit'` | Only sphere_orbit in v1. |

---

## `execute_trajectory`

**Module:** [`modulated_system/tools/trajectory/execute_trajectory.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/trajectory/execute_trajectory.py#L39)  ·  **Python function:** `execute_trajectory`  ·  **Description source:** decorator `description=`

Drive the robot through a precomputed camera-pose waypoint list. Internally runs solve_trajopt_chain (per-chord cuRobo TrajOpt with collision/SDF push on every internal knot, terminal pose pinned at each waypoint), Cartesian-velocity-bounded retime to kill dwell at chord seams, a costmap base-filter, and a 100 Hz uniform resample, then streams through WholeBodyTrajectoryExecutor (MPC base tracker + arm streaming). speed_factor (default 0.3) is the ONLY velocity throttle. Pair with `generate_view_trajectory`, or pass any list with the matching shape: {pos: [x,y,z], quat_wxyz: [w,x,y,z], label?} (legacy {cam_pos, look_at} also accepted).

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `waypoints` | `array` | ✓ | — | Output of generate_view_trajectory. Each waypoint is {pos: [x,y,z], quat_wxyz: [w,x,y,z], label?}. Legacy {cam_pos, look_at} is also accepted and auto-converted. |
| `return_to_start` | `boolean` | — | `False` | If true, reverse-sweep through the trajectory back to the starting pose after the forward pass. Default off — symmetric trajectories (orbit) can use this for capture symmetry; one-shot moves don't want it. |
| `manipulator_name` | `string` | — | — | Manipulator name. Default: first manipulator with an EE-mounted camera, falling back to the first manipulator. |
| `speed_factor` | `number` | — | `0.3` | Linear scale on both the Cartesian-velocity cap (0.30 m/s × sf) and the per-joint velocity derate (0.30 × sf of URDF v_limits). Default 0.3 → 0.09 m/s + 9% joint derate; keeps the peak velocity demand seen by the JointPosition controller's filter (coeff=0.1 @ 1 kHz) well below the FR3 reflex envelope on every joint. speed_factor is the only velocity throttle (no per-publish step cap downstream). Raise above 0.3 only for motions you've confirmed are safe. Clamped to [0.05, 5.0]. |
| `lock_base` | `boolean` | — | `False` | If true, plan with the base PINNED at its current pose for this call only — cuRobo optimizes arm joints only. Use for 'rearrange the arm where the robot already is' moves (survey/prepose/rest/nudge). Independent of the lock_base() tool's global state — does NOT mutate it. Without this flag, cuRobo is free to slide the base as part of the whole-body solve, which is unsafe for arm-only intents. |

---

## `find_feasible_params`

**Module:** [`modulated_system/tools/trajectory/find_feasible_params.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/trajectory/find_feasible_params.py#L222)  ·  **Python function:** `find_feasible_params`  ·  **Description source:** decorator `description=`

Search for camera-path generator parameters whose every waypoint is reachable from the current (or locked) base pose. Uses the precomputed FR3 reach map — pure-IK / joint-limit feasibility, scene-blind. Returns the top-K candidate parameter sets sorted by feasibility fraction and arc/length coverage. Pair the chosen params with `generate_view_trajectory` + `execute_trajectory` to actually run a trajectory (octomap obstacle avoidance is handled by trajopt during execution, not here). PREFER `compute_params_for_base_pose` (closed-form analytic) for new scripts when the base is already parked, or `compute_parking_locations` when you want the helper to pick the parking spot. This grid-search version retains octomap-clearance scoring and is kept for callers that rely on the `min_camera_clearance_m` knob.

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `target_x` | `number` | ✓ | — | World-frame X (m). |
| `target_y` | `number` | ✓ | — | World-frame Y (m). |
| `target_z` | `number` | ✓ | — | World-frame Z (m). |
| `trajectory_type` | `string` | — | `'sphere_orbit'` | Generator name. Supported: sphere_orbit (orbit), linear_aimed, approach_retreat. Other generators fall back to a no-op response with success=False. |
| `top_k` | `integer` | — | `5` | Number of top-ranked candidates to return. |
| `base_x` | `number` | — | — | Optional base X (m). Defaults to the current locked-base pose, or the current robot base pose if not locked. |
| `base_y` | `number` | — | — | Optional base Y (m). |
| `base_yaw_rad` | `number` | — | — | Optional base yaw (rad). |
| `user_prefs` | `object` | — | — | Optional generator-specific overrides for the parameter grid. Each generator's search_grid appends `n_random` random samples (default 100) from continuous `*_range` priors on top of its deterministic grid; pass `n_random=0` to disable, `seed=...` for reproducibility, or explicit value lists like radii_m=[0.30], arcs_deg=[120] to stick the search to specific values. |
| `min_camera_clearance_m` | `number` | — | `0.1` | Hard floor (m) — any candidate whose camera waypoint comes closer than this to an occupied octomap voxel is rejected (score=-inf). Skipped entirely when no octomap data is available. Defaults to 10 cm — wide enough to keep the camera off tabletop clutter at orbit elevations. |
| `clearance_weight` | `number` | — | `50.0` | Soft-bonus weight added per metre of clearance above `min_camera_clearance_m`. Rewards picking the farthest-from-clutter orbit when several are equivalent on feasibility. Set 0 to disable the bonus while keeping the hard floor. |

---

## `generate_view_trajectory`

**Module:** [`modulated_system/tools/trajectory/generate_view_trajectory.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/trajectory/generate_view_trajectory.py#L27)  ·  **Python function:** `generate_view_trajectory`  ·  **Description source:** decorator `description=`

Generate camera-view waypoints around a target. Picks a camera_paths generator (sphere_orbit / linear_aimed / linear_fixed / approach_retreat / look_away_return / bezier). Returns the waypoint list WITHOUT driving anything — pair with `execute_trajectory` for the full pipeline. target_x/y/z are all required (world frame, m).

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `trajectory_type` | `string` | — | `'sphere_orbit'` | Generator name: sphere_orbit (alias 'orbit') / linear_aimed / linear_fixed / approach_retreat / look_away_return / bezier / camera_pose_to. For camera_pose_to the target_x/y/z is the DESTINATION camera position (not a look-at target); orientation defaults to current camera quat (pure translation), override via generator_params['target_quat_wxyz']. |
| `target_x` | `number` | ✓ | — | Target world-frame X (m). |
| `target_y` | `number` | ✓ | — | Target world-frame Y (m). |
| `target_z` | `number` | ✓ | — | Target world-frame Z (m). |
| `radius_m` | `number` | — | — | Sphere / line / approach radius (m). Defaults are generator-specific; sphere_orbit defaults to 0.30 m. |
| `arc_deg` | `number` | — | — | Arc coverage (deg) — sphere_orbit + bezier (arc_bow shape). |
| `center_az_deg` | `number` | — | — | Center of the arc (deg, world frame). Defaults to the direction from target back toward the robot base. |
| `num_waypoints` | `integer` | — | — | Override the auto-computed waypoint count. |
| `direction` | `string` | — | `'ccw'` | sphere_orbit only. |
| `length_m` | `number` | — | — | Line length (m). linear_aimed / linear_fixed. |
| `direction_mode` | `string` | — | `'tangent'` | Direction of the line in world frame. linear_aimed / linear_fixed. |
| `start_radius_m` | `number` | — | — | Starting (farthest) radius for approach_retreat (m). |
| `end_radius_m` | `number` | — | — | Closest radius for approach_retreat (m). |
| `retreat` | `boolean` | — | `True` | approach_retreat: if true, retreats back to start_radius_m after reaching end_radius_m. |
| `look_away_angle_deg` | `number` | — | — | look_away_return only — peak glance-away angle. The SIGN selects the rotation direction (+yaw=CW, -yaw=CCW). |
| `away_axis` | `string` | — | `'yaw'` | look_away_return: which camera axis to rotate about. For an OBLIQUE/arbitrary axis pass a length-3 vector via generator_params={'away_axis': [x, y, z]}. |
| `backup_m` | `number` | — | — | look_away_return only — meters the camera pulls back radially at the glance peak. Default 0.05 (5 cm) adds translation/parallax; 0.0 = pure rotation. |
| `elevation_deg` | `number` | — | `15.0` | Camera elevation above the target's horizontal plane (deg). POSITIVE = camera ABOVE the target, looking DOWN onto it (camera_z = target_z + r*sin(elev)). NEGATIVE = camera below, looking up. For a look-down-onto-object orbit pass a POSITIVE value (e.g. +20). |
| `elevation_end_deg` | `number` | — | — | End-of-sweep elevation (deg) — sphere_orbit only, produces a spiral if different from elevation_deg. |
| `generator_params` | `object` | — | — | Passthrough dict for generator-specific knobs not surfaced as top-level kwargs (e.g. control_points for bezier shape='custom', bow_height_m for bezier shape='arc_bow'). For bezier shape='custom', `min_z_m` / `max_z_m` clamp control-point Z so CPs can't sit below the table or above the ceiling. Merged onto the kwarg-derived params; overrides on collision. |

---


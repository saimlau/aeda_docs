# Tools — `manipulator` (11)

Move the arm. Relative motion, single-joint rotation, IK + collision-aware whole-body execution, recovery from brake/reflex.

## In this category

- [`check_reachability`](#check_reachability) — Batched reachability filter. Given a list of candidate poses, return a parallel `reachable` boolean array — handy for trimming a sampled orbit / linear sweep to the configurations that actually fit in the current scene. Backed by cuRobo's BatchMotionPlanner; first call triggers the same one-time CUDA JIT compile as plan_arm_motion.
- [`lock_base`](#lock_base) — Pin the base in place for the next trajopt-driven motions. While locked, cuRobo plans only the 7-DOF arm (no base shuffling). Calling with no args locks at the current base pose; pass x/y/yaw_rad to lock elsewhere. Call unlock_base to release.
- [`move_camera_relative`](#move_camera_relative) — Translate the EEF camera by a small cartesian delta while PRESERVING its current orientation. Planned with cuRobo against the live octomap; executed by streaming the joint trajectory through the manipulator's /cmd_arm_qpos at 30 Hz. Use this for 'lift the camera by N cm', 'nudge forward 5 cm', etc. For trajectories where the camera should aim at a target (orbit, approach_retreat, sphere_orbit), use generate_view_trajectory + execute_trajectory instead — those let the IK choose orientation per waypoint.
- [`plan_arm_motion`](#plan_arm_motion) — Plan a smooth, collision-aware arm trajectory from the current qpos to a target pose (cartesian goal) or target qpos (joint-space goal). Uses cuRobo's `MotionPlanner` collision-checked against an SDF built from the latest octomap point cloud — falls back to free-space planning when the octomap isn't running. Returns a `trajectory` array of {t_s, qpos, qvel} samples (subsampled to keep payloads bounded). Activate the cuRobo IK Solver tile first — first plan triggers a one-time CUDA JIT compile (~10–15 s).
- [`prepose_arm_for_view`](#prepose_arm_for_view) — Raise/tilt the arm so the EEF camera sits AT LEAST the target's height (never looking up at an object from below) and aims forward toward the target. Call this AFTER navigate_to and BEFORE start_recording + generate_view_trajectory + execute_trajectory for SMALL / TABLETOP targets only — for far-range / large-object targets, the arm should stay at FR3_REST so the camera frames the whole object from a low angle. cam_z defaults to max(target_position_w[2], 0.60); user-supplied cam_z is bumped up to target_z if it would otherwise be lower. Clamped to [z_min, z_max] = [0.30, 1.62].
- [`recover_arm`](#recover_arm) — Clear a libfranka reflex (tau_J_range_violation, self_collision_avoidance_violation, joint_velocity_violation, etc.) and re-arm the FR3 streaming controller. Idempotent — safe to call before every motion command, costs ~150 ms. Calls the /recover_arm Trigger service on the arm_zerorpc relay, which runs stop_streaming + start_streaming on the NUC; start_streaming internally calls panda.recover() before reactivating JointPosition control. After a reflex this is the ONLY way to make the arm respond to /cmd_arm_qpos again without restarting the arm_zerorpc launcher process. Use between data-collection cycles in workflows where a trajectory may trip a reflex (e.g., folded-arm orbits).
- [`reset_arm_to_rest`](#reset_arm_to_rest) — Move a manipulator back to its rest configuration. Call between data-collection cycles — especially after several trajectories at widely-varying target azimuths — to prevent the manipulator from accumulating joint drift and landing in twisted poses where EEF gravity torque spuriously trips the controller's reflex on every subsequent motion. No-op if the manipulator is already near its rest pose. Pass `name` to choose a specific manipulator when the platform has more than one.
- [`retime_trajectory`](#retime_trajectory) — Retime an arbitrary qpos waypoint sequence into a smooth, time-parameterized trajectory respecting the robot's velocity and acceleration limits. Backed by cuRobo's TrajectoryOptimizer (TOTG-style) — first call JIT-compiles its own CUDA kernels (~5–10 s) on top of the MotionPlanner / BatchMotionPlanner compiles. Pair with the camera-orbit generators in a future step: orbit → list of qpos waypoints → retime → stream to arm.
- [`rotate_joint`](#rotate_joint) — Rotate a single arm joint to an absolute angle or by a delta. Direct joint-space drive (no IK, no trajopt) with an octomap-based sweep safety check that aborts if the EEF camera would pass within `min_clearance_m` of an occupied voxel along the linear-interp path. Useful for scene sweeping (joint 0 = shoulder pan) and camera roll (joint 6 = wrist roll). Specify exactly one of `delta_rad` or `target_rad`. Pass `skip_octomap_check=true` to bypass the safety check.
- [`survey_scene_pose`](#survey_scene_pose) — Lift the arm and tilt the camera down for scene scanning. Use at the start of a collection cycle, or whenever you're unsure what's visible. After this pose, call list_objects_in_view / find_cluster_target — tags will be dominated by tabletop and mid-height objects instead of floor clutter. Pass use_rest_pose=true for FAR-RANGE tasks (≥3 m targets, furniture anchors) — keeps the arm tucked and safer during subsequent base motion.
- [`unlock_base`](#unlock_base) — Release a base lock set by lock_base. Subsequent trajopt-driven moves return to the full 10-DOF whole-body planner.

---

## `check_reachability`

**Module:** [`modulated_system/tools/manipulator/check_reachability.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/manipulator/check_reachability.py#L26)  ·  **Python function:** `check_reachability`  ·  **Description source:** decorator `description=`

Batched reachability filter. Given a list of candidate poses, return a parallel `reachable` boolean array — handy for trimming a sampled orbit / linear sweep to the configurations that actually fit in the current scene. Backed by cuRobo's BatchMotionPlanner; first call triggers the same one-time CUDA JIT compile as plan_arm_motion.

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `candidate_poses` | `array` | ✓ | — | List of pose dicts. Each must carry x/y/z; qw/qx/qy/qz optional (default identity rotation). |
| `voxel_size_m` | `number` | — | `0.05` | Octomap voxel size for the collision world. |
| `max_attempts` | `integer` | — | `1` | cuRobo retry budget per pose. Keep at 1 for a fast feasibility check; raise to 2-3 if the false-negative rate is too high. |
| `name` | `string` | — | — | Manipulator name (default: first with EEF camera). |

---

## `lock_base`

**Module:** [`modulated_system/tools/manipulator/lock_base.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/manipulator/lock_base.py#L26)  ·  **Python function:** `lock_base`  ·  **Description source:** decorator `description=`

Pin the base in place for the next trajopt-driven motions. While locked, cuRobo plans only the 7-DOF arm (no base shuffling). Calling with no args locks at the current base pose; pass x/y/yaw_rad to lock elsewhere. Call unlock_base to release.

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `x` | `number` | — | — | World-frame X (m). Defaults to current base X. |
| `y` | `number` | — | — | World-frame Y (m). Defaults to current base Y. |
| `yaw_rad` | `number` | — | — | Base yaw (rad). Defaults to current base yaw. |

---

## `move_camera_relative`

**Module:** [`modulated_system/tools/manipulator/move_camera_relative.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/manipulator/move_camera_relative.py#L33)  ·  **Python function:** `move_camera_relative`  ·  **Description source:** decorator `description=`

Translate the EEF camera by a small cartesian delta while PRESERVING its current orientation. Planned with cuRobo against the live octomap; executed by streaming the joint trajectory through the manipulator's /cmd_arm_qpos at 30 Hz. Use this for 'lift the camera by N cm', 'nudge forward 5 cm', etc. For trajectories where the camera should aim at a target (orbit, approach_retreat, sphere_orbit), use generate_view_trajectory + execute_trajectory instead — those let the IK choose orientation per waypoint.

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `dx` | `number` | — | `0.0` | Translation X, meters. Direction depends on `frame`: 'world' = world +X (typically forward of the base origin); 'body' = base body +X (forward in the robot's heading). |
| `dy` | `number` | — | `0.0` | Translation Y, meters. 'world' = world +Y; 'body' = base body +Y (left). |
| `dz` | `number` | — | `0.0` | Translation Z, meters. Up. Frame-independent. |
| `frame` | `string` | — | `'world'` | 'world' (default) = base_odom frame. 'body' = rotate the (dx, dy) component by the base's current yaw before applying. dz is always world Z because there's no ambiguity for a holonomic base. |
| `manipulator_name` | `string` | — | — | Which manipulator's EEF camera to move. Default: the first manipulator with an EEF camera. |
| `publish_hz` | `number` | — | `30.0` | Joint-trajectory publish rate (Hz). 30 Hz is the sim's velocity-PID input rate; higher than that is wasted bandwidth. |
| `max_attempts` | `integer` | — | `4` | Plan retry budget passed through to cuRobo. Increase for poses near the workspace boundary. |

---

## `plan_arm_motion`

**Module:** [`modulated_system/tools/manipulator/plan_arm_motion.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/manipulator/plan_arm_motion.py#L29)  ·  **Python function:** `plan_arm_motion`  ·  **Description source:** decorator `description=`

Plan a smooth, collision-aware arm trajectory from the current qpos to a target pose (cartesian goal) or target qpos (joint-space goal). Uses cuRobo's `MotionPlanner` collision-checked against an SDF built from the latest octomap point cloud — falls back to free-space planning when the octomap isn't running. Returns a `trajectory` array of {t_s, qpos, qvel} samples (subsampled to keep payloads bounded). Activate the cuRobo IK Solver tile first — first plan triggers a one-time CUDA JIT compile (~10–15 s).

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `target_pose` | `object` | — | — | Cartesian goal as {x, y, z, qw, qx, qy, qz} in world frame. Mutually exclusive with target_qpos. |
| `target_qpos` | `array` | — | — | Joint-space goal (list of `dof` floats). Mutually exclusive with target_pose. |
| `max_attempts` | `integer` | — | `4` | cuRobo retry budget per plan call. Higher = more robust at the cost of latency. |
| `time_dilation` | `number` | — | `0.5` | 0 < d <= 1 — slows the whole trajectory by 1/d. Default 0.5 = ~2x slower than cuRobo's nominal fastest plan, gentler on real hardware. |
| `voxel_size_m` | `number` | — | `0.05` | Octomap voxel size used to build the collision world (each occupied voxel = sphere of voxel_size_m/2). |
| `max_samples` | `integer` | — | `100` | Subsample the cuRobo trajectory to at most this many rows in the output. The full-resolution trajectory stays on the planner side. |
| `name` | `string` | — | — | Manipulator name (default: first with EEF camera). |

---

## `prepose_arm_for_view`

**Module:** [`modulated_system/tools/manipulator/prepose_arm_for_view.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/manipulator/prepose_arm_for_view.py#L21)  ·  **Python function:** `prepose_arm_for_view`  ·  **Description source:** decorator `description=`

Raise/tilt the arm so the EEF camera sits AT LEAST the target's height (never looking up at an object from below) and aims forward toward the target. Call this AFTER navigate_to and BEFORE start_recording + generate_view_trajectory + execute_trajectory for SMALL / TABLETOP targets only — for far-range / large-object targets, the arm should stay at FR3_REST so the camera frames the whole object from a low angle. cam_z defaults to max(target_position_w[2], 0.60); user-supplied cam_z is bumped up to target_z if it would otherwise be lower. Clamped to [z_min, z_max] = [0.30, 1.62].

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `target_position_w` | `array` | ✓ | — | [x, y, z] of the target in world frame. |
| `cam_z` | `number` | — | — | Optional absolute world-frame camera height. Defaults to max(target_z, cam_min_z_floor); always bumped up to >= target_z. |
| `cam_min_z_floor` | `number` | — | `0.6` | Minimum camera height when cam_z is not explicitly set. Default 0.60 m (above stand tops). |
| `cam_forward_m` | `number` | — | `0.4` | Camera offset forward of base_link in body frame. Default 0.40 m (tucked in for safety). |
| `z_min` | `number` | — | `0.3` | Lower clamp on cam_z. |
| `z_max` | `number` | — | `1.62` | Upper clamp on cam_z. Default 1.62 m (below the FR3 fully-extended-up singularity at ~1.80 m). |
| `name` | `string` | — | — | Manipulator name (e.g. 'arm', 'arm_left'). Defaults to the first manipulator with an EEF camera. |

---

## `recover_arm`

**Module:** [`modulated_system/tools/manipulator/recover_arm.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/manipulator/recover_arm.py#L29)  ·  **Python function:** `recover_arm`  ·  **Description source:** decorator `description=`

Clear a libfranka reflex (tau_J_range_violation, self_collision_avoidance_violation, joint_velocity_violation, etc.) and re-arm the FR3 streaming controller. Idempotent — safe to call before every motion command, costs ~150 ms. Calls the /recover_arm Trigger service on the arm_zerorpc relay, which runs stop_streaming + start_streaming on the NUC; start_streaming internally calls panda.recover() before reactivating JointPosition control. After a reflex this is the ONLY way to make the arm respond to /cmd_arm_qpos again without restarting the arm_zerorpc launcher process. Use between data-collection cycles in workflows where a trajectory may trip a reflex (e.g., folded-arm orbits).

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `timeout_s` | `number` | — | `5.0` | Max time to wait for the service response (seconds). Default 5 s — well above the typical ~150 ms recover + restart latency. |

---

## `reset_arm_to_rest`

**Module:** [`modulated_system/tools/manipulator/reset_arm_to_rest.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/manipulator/reset_arm_to_rest.py#L26)  ·  **Python function:** `reset_arm_to_rest`  ·  **Description source:** decorator `description=`

Move a manipulator back to its rest configuration. Call between data-collection cycles — especially after several trajectories at widely-varying target azimuths — to prevent the manipulator from accumulating joint drift and landing in twisted poses where EEF gravity torque spuriously trips the controller's reflex on every subsequent motion. No-op if the manipulator is already near its rest pose. Pass `name` to choose a specific manipulator when the platform has more than one.

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `name` | `string` | — | — | Manipulator name (e.g. 'arm', 'arm_left'). Defaults to the first manipulator on the platform that has an EEF camera, then the first manipulator overall. |
| `tol_deg` | `number` | — | `5.0` | Skip the move if every joint is within this tolerance of rest. |
| `speed_factor` | `number` | — | — | Move speed scale (0.0..1.0). Platforms may clamp. |

---

## `retime_trajectory`

**Module:** [`modulated_system/tools/manipulator/retime_trajectory.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/manipulator/retime_trajectory.py#L26)  ·  **Python function:** `retime_trajectory`  ·  **Description source:** decorator `description=`

Retime an arbitrary qpos waypoint sequence into a smooth, time-parameterized trajectory respecting the robot's velocity and acceleration limits. Backed by cuRobo's TrajectoryOptimizer (TOTG-style) — first call JIT-compiles its own CUDA kernels (~5–10 s) on top of the MotionPlanner / BatchMotionPlanner compiles. Pair with the camera-orbit generators in a future step: orbit → list of qpos waypoints → retime → stream to arm.

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `qpos_waypoints` | `array` | ✓ | — | Coarse waypoint list. Each row is a `dof`-vector of joint angles. Need at least 2 waypoints. |
| `max_velocity` | `array` | — | — | Per-joint velocity cap (rad/s). Defaults to the robot's bundled limits in cuRobo's franka.yml. Provide a `dof`-vector to slow specific joints. |
| `max_acceleration` | `array` | — | — | Per-joint acceleration cap (rad/s²). Defaults to the robot's bundled limits. |
| `max_samples` | `integer` | — | `100` | Subsample the retimed trajectory for the output. |
| `name` | `string` | — | — | Manipulator name (default: first with EEF camera). |

---

## `rotate_joint`

**Module:** [`modulated_system/tools/manipulator/rotate_joint.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/manipulator/rotate_joint.py#L31)  ·  **Python function:** `rotate_joint`  ·  **Description source:** decorator `description=`

Rotate a single arm joint to an absolute angle or by a delta. Direct joint-space drive (no IK, no trajopt) with an octomap-based sweep safety check that aborts if the EEF camera would pass within `min_clearance_m` of an occupied voxel along the linear-interp path. Useful for scene sweeping (joint 0 = shoulder pan) and camera roll (joint 6 = wrist roll). Specify exactly one of `delta_rad` or `target_rad`. Pass `skip_octomap_check=true` to bypass the safety check.

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `joint_index` | `integer` | ✓ | — | Zero-based joint index (0..dof-1). For a 7-DOF FR3: 0 is shoulder pan, 6 is wrist roll. |
| `delta_rad` | `number` | — | — | Relative rotation from current angle (radians, CCW positive). |
| `target_rad` | `number` | — | — | Absolute target angle (radians). Mutually exclusive with delta_rad. |
| `speed_factor` | `number` | — | — | Move speed scale (0.0..1.0). Platforms may clamp. |
| `name` | `string` | — | — | Manipulator name. Defaults to first with EEF camera, then first overall. |
| `skip_octomap_check` | `boolean` | — | `False` | Skip the octomap sweep safety check. Useful when the octomap is stale or known to be empty. Default: false (always check). |
| `min_clearance_m` | `number` | — | `0.05` | Required clearance from any occupied voxel during the sweep, in meters. Default 0.05 m. |

---

## `survey_scene_pose`

**Module:** [`modulated_system/tools/manipulator/survey_scene_pose.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/manipulator/survey_scene_pose.py#L23)  ·  **Python function:** `survey_scene_pose`  ·  **Description source:** decorator `description=`

Lift the arm and tilt the camera down for scene scanning. Use at the start of a collection cycle, or whenever you're unsure what's visible. After this pose, call list_objects_in_view / find_cluster_target — tags will be dominated by tabletop and mid-height objects instead of floor clutter. Pass use_rest_pose=true for FAR-RANGE tasks (≥3 m targets, furniture anchors) — keeps the arm tucked and safer during subsequent base motion.

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `cam_z` | `number` | — | `1.1` | Camera height in world frame (m). Clamped to [0.30, 1.62]. |
| `tilt_deg` | `number` | — | `25.0` | Pitch below horizontal (deg). 0 = horizon, 60 = looking ~3x the camera height down. |
| `cam_forward_m` | `number` | — | `0.3` | Camera offset forward of base_link (m). |
| `use_rest_pose` | `boolean` | — | `False` | Tuck the arm to FR3_REST instead of lifting+tilting. Preferred for far-range scans. |
| `speed_factor` | `number` | — | `0.3` | Cartesian-velocity scale passed to execute_trajectory (≈ 0.09 m/s + 9% joint velocity derate at the 0.3 default). Matches execute_trajectory's default; kept explicit so survey stays slow. Bump up only if you confirm the specific motion stays safe. |
| `name` | `string` | — | — | Manipulator name (default: first with EEF camera). |

---

## `unlock_base`

**Module:** [`modulated_system/tools/manipulator/lock_base.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/manipulator/lock_base.py#L109)  ·  **Python function:** `unlock_base`  ·  **Description source:** decorator `description=`

Release a base lock set by lock_base. Subsequent trajopt-driven moves return to the full 10-DOF whole-body planner.

---


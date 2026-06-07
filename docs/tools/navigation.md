# Tools — `navigation` (7)

Move the base. Nav2-backed `navigate_to`, parking-candidate search, approach helpers, lock/unlock-base.

## In this category

- [`choose_collection_site`](#choose_collection_site) — Top-level driver for the data-collection outer loop. Looks at the active DataSpec + recorded episodes, picks the most under-served target, and asks request_next_view for the best base pose to capture from. Returns a dict with either {complete: True} (spec satisfied) or {target_id, best, alternatives, ...} ready to feed into navigate_to + start_recording + generate_view_trajectory + execute_trajectory + stop_recording.
- [`explore_frontier`](#explore_frontier) — Drive toward an unexplored region (a frontier — free cells adjacent to unknown cells in the costmap). Picks the largest+closest cluster, drives there via the global planner. Use when the current area is exhausted (every detect_target returns objects with previously_collected_frames>0). Complement of explore_unvisited: frontier reveals NEW terrain; unvisited explores known-free regions you haven't been to. PREFER explore_unvisited when coverage_pct < 0.80.
- [`explore_unvisited`](#explore_unvisited) — Drive to a known-free region of the map you HAVEN'T visited this session. Complement of explore_frontier: frontier picks the EDGE of the map (reveals new terrain); explore_unvisited picks known-free INTERIOR you just haven't entered. Maintains a session buffer of visited poses. Returns coverage_pct = visited-hull-area / known-free-area; when that nears 0.80, switch to explore_frontier.
- [`move_relative`](#move_relative) — Move the base relative to its current pose. dx_m forward, dy_m left (body frame, holonomic base), d_yaw_deg CCW rotation. Uses cuRobo + octomap for collision-aware planning and a costmap footprint filter as last-resort defense; the MPC base tracker drives the planned trajectory. Pass skip_safety_filters=true to bypass octomap/costmap checks when recovering from a wedged pose (NOT for normal use).
- [`navigate_to`](#navigate_to) — Drive to a world (x, y), OR park N meters short of it facing it. Uses the platform's global planner (Nav2 on tidyros_iphone), so it's costmap-aware.
- [`reposition`](#reposition) — Drive the base to an absolute (x, y) pose. Optionally pass face_target_x/face_target_y or yaw_deg to control the final heading. Differs from navigate_to: no minimum offset clamp; intended for 'go EXACTLY here' uses (orbit start positions, intermediate stand-offs). Aborts cleanly if the global planner returns no path.
- [`request_next_view`](#request_next_view) — Pick the best next base pose to capture a target from. Generates an orbital ring of candidate poses around the target, scores each on visibility (pinhole frustum + octomap occlusion) + novelty (yaw-bin uniqueness vs previously captured episodes) + travel cost from the current robot pose, and returns the top-k. The output's best.base_x / best.base_y / best.base_yaw_deg drop directly into navigate_to(x=..., y=..., yaw_deg=...); best.bearing_from_target_deg drops into generate_view_trajectory(center_az_deg=...) so the orbit centers on the candidate's yaw bin and coverage progresses cleanly.

---

## `choose_collection_site`

**Module:** [`modulated_system/tools/navigation/choose_collection_site.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/navigation/choose_collection_site.py#L80)  ·  **Python function:** `choose_collection_site`  ·  **Description source:** decorator `description=`

Top-level driver for the data-collection outer loop. Looks at the active DataSpec + recorded episodes, picks the most under-served target, and asks request_next_view for the best base pose to capture from. Returns a dict with either {complete: True} (spec satisfied) or {target_id, best, alternatives, ...} ready to feed into navigate_to + start_recording + generate_view_trajectory + execute_trajectory + stop_recording.

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `yaw_bin_size_deg` | `number` | — | `30.0` | Yaw-bin width used for both coverage rollup + planner. |
| `request_next_view_kwargs` | `object` | — | — | Forwarded to request_next_view as overrides (e.g. {'radii_m': [0.8, 1.2, 1.6]}). |

---

## `explore_frontier`

**Module:** [`modulated_system/tools/navigation/explore_frontier.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/navigation/explore_frontier.py#L17)  ·  **Python function:** `explore_frontier`  ·  **Description source:** decorator `description=`

Drive toward an unexplored region (a frontier — free cells adjacent to unknown cells in the costmap). Picks the largest+closest cluster, drives there via the global planner. Use when the current area is exhausted (every detect_target returns objects with previously_collected_frames>0). Complement of explore_unvisited: frontier reveals NEW terrain; unvisited explores known-free regions you haven't been to. PREFER explore_unvisited when coverage_pct < 0.80.

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `max_distance_m` | `number` | — | `6.0` | Max frontier-centroid distance from robot pose. |
| `min_cluster_cells` | `integer` | — | `6` | Reject clusters smaller than this (filters lidar noise). |
| `standoff_m` | `number` | — | `1.0` | How far back from the frontier centroid to stop. |
| `timeout_s` | `number` | — | `30.0` | Global planner timeout (s). |

---

## `explore_unvisited`

**Module:** [`modulated_system/tools/navigation/explore_unvisited.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/navigation/explore_unvisited.py#L21)  ·  **Python function:** `explore_unvisited`  ·  **Description source:** decorator `description=`

Drive to a known-free region of the map you HAVEN'T visited this session. Complement of explore_frontier: frontier picks the EDGE of the map (reveals new terrain); explore_unvisited picks known-free INTERIOR you just haven't entered. Maintains a session buffer of visited poses. Returns coverage_pct = visited-hull-area / known-free-area; when that nears 0.80, switch to explore_frontier.

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `max_distance_m` | `number` | — | `12.0` | Max candidate-goal distance from current pose. |
| `max_candidates` | `integer` | — | `12` | Max candidates to rank + try. |
| `n_samples` | `integer` | — | `500` | Random known-free cells to sample. |
| `min_outside_hull_m` | `number` | — | `0.5` | Candidate must be at least this far OUTSIDE the visited hull. |
| `timeout_s` | `number` | — | `30.0` | Global planner timeout (s). |

---

## `move_relative`

**Module:** [`modulated_system/tools/navigation/move_relative.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/navigation/move_relative.py#L43)  ·  **Python function:** `move_relative`  ·  **Description source:** decorator `description=`

Move the base relative to its current pose. dx_m forward, dy_m left (body frame, holonomic base), d_yaw_deg CCW rotation. Uses cuRobo + octomap for collision-aware planning and a costmap footprint filter as last-resort defense; the MPC base tracker drives the planned trajectory. Pass skip_safety_filters=true to bypass octomap/costmap checks when recovering from a wedged pose (NOT for normal use).

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `dx_m` | `number` | — | `0.0` | Forward translation (body frame, m). |
| `dy_m` | `number` | — | `0.0` | Left translation (body frame, m). |
| `d_yaw_deg` | `number` | — | `0.0` | CCW rotation (deg). |
| `skip_safety_filters` | `boolean` | — | `False` | Bypass octomap + costmap filters. Recovery only (e.g., the current pose is inside an inflation halo and you need to back out). Safe motion still relies on cuRobo's self-collision check. |
| `timeout_s` | `number` | — | `30.0` | Hard wall-clock cap on the whole call (planning + execution). Default 30 s. |

---

## `navigate_to`

**Module:** [`modulated_system/tools/navigation/navigate_to.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/navigation/navigate_to.py#L91)  ·  **Python function:** `navigate_to`  ·  **Description source:** decorator `description=`

Drive to a world (x, y), OR park N meters short of it facing it. Uses the platform's global planner (Nav2 on tidyros_iphone), so it's costmap-aware.

Common patterns:
  - Free-space coord (e.g. an orbit candidate from request_next_view): navigate_to(x=cx, y=cy, clamp_min_offset_m=0.0)
  - Park 1 m in front of a detected object: navigate_to(x=tx, y=ty, offset_m=1.0, clamp_min_offset_m=0.0)
  - Park at the default safe tabletop standoff (1.5 m): navigate_to(x=tx, y=ty)

offset_m is silently clamped to ≥ clamp_min_offset_m (default 1.5 m) as a tabletop-edge safety. Pass clamp_min_offset_m=0.0 to allow closer landings (free-space coords, or you accept the table-edge risk). After arrival, auto-rotates to face the target unless face_target=false.

If Nav2 can't plan (e.g. the robot is wedged inside its own costmap inflation halo) and allow_curobo_fallback=True, transparently retries with a cuRobo whole-body chord against the octomap. The fallback goal is truncated to curobo_max_distance_m if the original goal is further.

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `x` | `number` | ✓ | — | Target X (world frame, m). |
| `y` | `number` | ✓ | — | Target Y (world frame, m). |
| `yaw_deg` | `number` | — | — | Optional final heading (deg, world frame). Default: face the target from the approach point. |
| `offset_m` | `number` | — | `1.5` | Stop this many meters short of (x, y), along the line from the robot to the target — useful for 'park in front of an object'. Clamped to >= clamp_min_offset_m below. |
| `clamp_min_offset_m` | `number` | — | `1.5` | Lower bound for offset_m. Default 1.5 — safety clamp for approaching objects on tables (table edges extend 0.4-0.7 m beyond the object centroid). Pass 0.0 when (x, y) is a free-space coord (e.g. an orbit candidate from request_next_view) OR when you want a closer parking distance than 1.5 m and you've accepted the edge-collision risk. |
| `face_target` | `boolean` | — | `True` | After arrival, rotate to face the target. Set false if you already passed yaw_deg and don't want extra motion. |
| `timeout_s` | `number` | — | `60.0` | Overall wall-clock budget for the call (s). |
| `estimated_timeout_s` | `number` | — | `20.0` | Tighter budget passed to Nav2. If Nav2 hasn't moved us by then we assume it's stuck and (when allow_curobo_fallback=True) hand off to cuRobo. Effective Nav2 timeout is min(estimated_timeout_s, timeout_s). |
| `stuck_pose_eps_m` | `number` | — | `0.02` | Reserved — pose-displacement threshold for the (future) pose-based stuck detector. Currently unused; we rely on the wall-clock budget. |
| `stuck_pose_eps_deg` | `number` | — | `2.0` | Reserved — yaw-change threshold for the (future) pose-based stuck detector. Currently unused. |
| `stuck_window_s` | `number` | — | `5.0` | Reserved — sliding-window length for the (future) pose-based stuck detector. Currently unused. |
| `allow_curobo_fallback` | `boolean` | — | `True` | If Nav2 fails / times out, retry with a cuRobo whole-body chord against the octomap. Disable (False) when the caller explicitly wants Nav2's 'no path' to surface as failure. |
| `curobo_max_distance_m` | `number` | — | `2.0` | Max straight-line distance the cuRobo fallback is allowed to attempt. Beyond this, the goal is truncated (or the fallback refused — see curobo_fallback_truncate). |
| `curobo_fallback_truncate` | `boolean` | — | `True` | When the original goal is beyond curobo_max_distance_m, truncate the cuRobo goal to a point along the ray at exactly that distance (True) or refuse the fallback and surface Nav2's failure (False). |

---

## `reposition`

**Module:** [`modulated_system/tools/navigation/reposition.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/navigation/reposition.py#L38)  ·  **Python function:** `reposition`  ·  **Description source:** decorator `description=`

Drive the base to an absolute (x, y) pose. Optionally pass face_target_x/face_target_y or yaw_deg to control the final heading. Differs from navigate_to: no minimum offset clamp; intended for 'go EXACTLY here' uses (orbit start positions, intermediate stand-offs). Aborts cleanly if the global planner returns no path.

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `x` | `number` | ✓ | — | Target X (m). |
| `y` | `number` | ✓ | — | Target Y (m). |
| `yaw_deg` | `number` | — | — | Optional final heading (deg, world). |
| `face_target_x` | `number` | — | — | If set, final yaw points at (face_target_x, face_target_y). |
| `face_target_y` | `number` | — | — | Companion to face_target_x. |
| `timeout_s` | `number` | — | `60.0` | Global planner timeout (s). |

---

## `request_next_view`

**Module:** [`modulated_system/tools/navigation/request_next_view.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/navigation/request_next_view.py#L305)  ·  **Python function:** `request_next_view`  ·  **Description source:** decorator `description=`

Pick the best next base pose to capture a target from. Generates an orbital ring of candidate poses around the target, scores each on visibility (pinhole frustum + octomap occlusion) + novelty (yaw-bin uniqueness vs previously captured episodes) + travel cost from the current robot pose, and returns the top-k. The output's best.base_x / best.base_y / best.base_yaw_deg drop directly into navigate_to(x=..., y=..., yaw_deg=...); best.bearing_from_target_deg drops into generate_view_trajectory(center_az_deg=...) so the orbit centers on the candidate's yaw bin and coverage progresses cleanly.

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `target_id` | `string` | — | — | Target id from the active DataSpec. |
| `target_position_w` | `array` | — | — | Explicit world-frame target [x, y, z]. |
| `k` | `integer` | — | `1` | Number of alternatives to return alongside the best. |
| `radii_m` | `array` | — | — | Orbit radii in metres. Default [1.5, 3.0] spans distance bins 1 (mid, 1.2-2.5 m) and 2 (far, 2.5-4.0 m) for tabletop targets — orbits at <1.2 m typically fail because the table inflation halo blocks every sweep direction. For bin-0 (close) coverage on freestanding targets, pass [0.9, 1.5] AND switch the trajectory_type in your generate_view_trajectory call to approach_retreat or linear_aimed. |
| `yaw_bin_size_deg` | `number` | — | `30.0` | Yaw-bin size used for novelty scoring + candidate density. |
| `travel_max_m` | `number` | — | `5.0` | Travel-cost normalization; candidates farther than this from the current robot pose get travel score 0. |

---


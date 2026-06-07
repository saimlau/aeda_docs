# Tools — `collection` (17)

Drive the data-collection loop. Spec definition, stop conditions, event log, episode summary, state persistence.

## In this category

- [`activate_workspace`](#activate_workspace) — Look up a named workspace in the catalog and call `define_workspace` with its corners + z-band. After this, select_point_in_workspace + the reach-aware target filter use this workspace; the /workspace_marker MarkerArray updates to its polygon.
- [`check_stop_condition`](#check_stop_condition) — Decide whether collection should stop, either for a single target (when target_object_id is given) or for the whole spec. Returns {stop, reason, gaps, coverage, suggestions}. The agent typically calls this after every stop_recording + evaluate_episode pair.
- [`create_data_spec`](#create_data_spec) — Create a data-collection specification — the per-target minimum thresholds (frames / yaw / distance bins / episodes) that the agent uses to decide when collection is 'done'. Replaces any existing active spec on this platform; the prior spec is overwritten on disk. Targets can be passed up-front or added later via update_data_spec.
- [`define_workspace`](#define_workspace) — Save a convex polygon footprint + Z range as the active data-collection workspace. Call this at the start of every session — sets the world-frame bounds the agent operates in. Tabletop, room, conference hall — same tool. Overwrites any prior workspace. Subsequent calls to select_point_in_workspace and the supervisor labeler consult this hull.
- [`evaluate_episode`](#evaluate_episode) — Quick per-episode acceptance check — a preliminary binary screen, NOT a substitute for dataset-level analysis (coverage_report / inspect_dataset / describe_distribution). Returns {accepted, reject_reasons, scores, n_frames, duration_s}. The Executor typically calls this after stop_recording to decide whether to retake. Default criteria require n_frames>=5, duration>=0.5s, depth_valid_ratio>=0.30; pass `criteria` to retune.
- [`get_collection_status`](#get_collection_status) — Snapshot the active spec, per-target progress, recent events, and the whole-spec stop-condition verdict. The agent typically calls this once per outer loop tick to decide what to do next.
- [`list_workspaces`](#list_workspaces) — Return every workspace in the session catalog. Reads runtime/sessions/<id>/workspaces.json. Returns an empty list (NOT an error) when no catalog file exists yet.
- [`log_event`](#log_event) — Append a free-form event to the collection log. Used by the agent + the higher-level orchestrator to record decisions, failure modes, phase transitions, and anything else that should land in the persistent run history. event_type is open-vocabulary; common ones: failure, phase_change, target_lost, optimizer_skip, rerun_decision.
- [`register_labeled_object`](#register_labeled_object) — Append a labeled object to the persistent catalog. Manual entry today (the supervisor labeler will write here once it lands). Use after detect_target to remember a found object's world position, or to seed the catalog with known scene objects.
- [`register_workspace`](#register_workspace) — Persist a named tabletop workspace (polygon + z-band + 3D anchor) to the session catalog at runtime/sessions/<id>/workspaces.json. Re-registering an existing name overwrites that entry. Idempotent + atomic (crash-safe via .tmp + rename). Pair with `list_workspaces` and `activate_workspace` for the multi-table replay flow.
- [`reset_collection_state`](#reset_collection_state) — Hard-reset the persistent collection state. Wipes events + episodes; optionally wipes the active data spec too. Removes the state.json file from disk. REQUIRES confirm=true to fire — without it, the call returns an error rather than deleting anything (so an accidental dispatch doesn't nuke a long-running collection).
- [`select_point_in_workspace`](#select_point_in_workspace) — Pick a salient point inside the active workspace. Modes: next_object — least-captured labeled object inside the workspace (ties broken by recency). random — uniformly random point in the polygon, z ∈ [z_min, z_max]. drivable — random point where the base can stand (costmap below lethal AND no octomap obstacle above). Useful for 'find me somewhere to park'. occupied — random OCCUPIED octomap voxel inside the workspace. Useful for 'look at something concrete'. exploration — random point in workspace with no occupied octomap voxel nearby (i.e. unobserved). Useful for scanning unexplored areas.
- [`store_episode_summary`](#store_episode_summary) — Record a captured episode in the collection memory. Most callers don't need this — `stop_recording` finalizes the episode.json on disk and the supervisor's evaluator hook writes the summary. This standalone tool is for backfilling summaries from disk or for recorders that bypass the start_recording / stop_recording pair.
- [`summarize_data_gaps`](#summarize_data_gaps) — Per-target progress dashboard: for every declared target (plus any target with episodes but no spec entry), report frames / episodes / yaw coverage / distance bins / status. Status is 'done' when the spec rules are satisfied, 'needs_more' otherwise.
- [`update_coverage_state`](#update_coverage_state) — Recompute the per-target coverage rollup from recorded episodes — yaw bins covered, distance bins covered, frame + episode counts, rejection counts. Read by request_next_view and choose_collection_site to decide where to go next. Coverage is computed on demand; this tool returns the latest rollup and does NOT mutate stored state.
- [`update_data_spec`](#update_data_spec) — Update fields on the active data spec. Pass `add_targets` to append new targets without rewriting existing ones; pass any of the per_target_* thresholds to retune the rules mid-run. Returns the updated spec snapshot.
- [`update_target_position`](#update_target_position) — Set or replace the world-frame position_w on an EXISTING target in the active DataSpec. Used to write a freshly-detected target's coordinates into the spec so request_next_view / choose_collection_site can plan around it. Returns success=False with an explanatory reason if no spec is active or target_id isn't in the spec — does NOT auto-create the target (use update_data_spec(add_targets=...) for that).

---

## `activate_workspace`

**Module:** [`modulated_system/tools/collection/workspace_catalog.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/collection/workspace_catalog.py#L155)  ·  **Python function:** `activate_workspace`  ·  **Description source:** decorator `description=`

Look up a named workspace in the catalog and call `define_workspace` with its corners + z-band. After this, select_point_in_workspace + the reach-aware target filter use this workspace; the /workspace_marker MarkerArray updates to its polygon.

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `name` | `string` | ✓ | — | Workspace name (must exist in the catalog). |

---

## `check_stop_condition`

**Module:** [`modulated_system/tools/collection/data_spec.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/collection/data_spec.py#L250)  ·  **Python function:** `check_stop_condition`  ·  **Description source:** decorator `description=`

Decide whether collection should stop, either for a single target (when target_object_id is given) or for the whole spec. Returns {stop, reason, gaps, coverage, suggestions}. The agent typically calls this after every stop_recording + evaluate_episode pair.

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `target_object_id` | `string` | — | — | Single-target mode. Without it, evaluates every target in the spec and returns stop=True only when every one individually satisfies. |

---

## `create_data_spec`

**Module:** [`modulated_system/tools/collection/data_spec.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/collection/data_spec.py#L21)  ·  **Python function:** `create_data_spec`  ·  **Description source:** decorator `description=`

Create a data-collection specification — the per-target minimum thresholds (frames / yaw / distance bins / episodes) that the agent uses to decide when collection is 'done'. Replaces any existing active spec on this platform; the prior spec is overwritten on disk. Targets can be passed up-front or added later via update_data_spec.

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `spec_id` | `string` | — | — | Override the auto-generated id (e.g. 'kitchen_mugs_apr2'). Default: auto-numbered spec_NNN. |
| `description` | `string` | — | — | Free-text description of this collection run. |
| `targets` | `array` | — | — | Initial target list. Each item must have target_id; description / position_w / category optional. |
| `per_target_min_frames` | `integer` | — | `30` | Minimum captured frames per target (default 30). |
| `per_target_min_yaw_deg` | `number` | — | `120.0` | Minimum cumulative yaw coverage (deg, default 120). |
| `per_target_min_distance_bins` | `integer` | — | `2` | Minimum distinct distance bins (default 2 — close + far). |
| `per_target_min_episodes` | `integer` | — | `2` | Minimum distinct episodes per target (default 2). |
| `reset_memory` | `boolean` | — | `False` | When true, wipe ALL prior episodes + events before installing this spec — fresh-run semantics. Default false (additive): existing episodes from an old spec stay in memory and start counting toward the new spec's targets, which is usually wrong if you're starting a different collection session. Pass true when in doubt. |

---

## `define_workspace`

**Module:** [`modulated_system/tools/collection/workspace.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/collection/workspace.py#L51)  ·  **Python function:** `define_workspace`  ·  **Description source:** decorator `description=`

Save a convex polygon footprint + Z range as the active data-collection workspace. Call this at the start of every session — sets the world-frame bounds the agent operates in. Tabletop, room, conference hall — same tool. Overwrites any prior workspace. Subsequent calls to select_point_in_workspace and the supervisor labeler consult this hull.

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `corners` | `array` | ✓ | — | List of [x, y] floor points (world frame, m), ≥ 3 vertices. Listed in order around the polygon (CW or CCW — the point-in-polygon test handles either). |
| `z_min` | `number` | — | `0.0` | Floor of the workspace (m, world frame). Default 0.0. |
| `z_max` | `number` | — | `3.0` | Ceiling of the workspace (m, world frame). Default 3.0 — typical room height. |

---

## `evaluate_episode`

**Module:** [`modulated_system/tools/collection/evaluate_episode.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/collection/evaluate_episode.py#L25)  ·  **Python function:** `evaluate_episode`  ·  **Description source:** decorator `description=`

Quick per-episode acceptance check — a preliminary binary screen, NOT a substitute for dataset-level analysis (coverage_report / inspect_dataset / describe_distribution). Returns {accepted, reject_reasons, scores, n_frames, duration_s}. The Executor typically calls this after stop_recording to decide whether to retake. Default criteria require n_frames>=5, duration>=0.5s, depth_valid_ratio>=0.30; pass `criteria` to retune.

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `episode_dir` | `string` | ✓ | — | Path to the directory containing episode.json. start_recording returns this as `episode_id`; the agent should pass it through verbatim. |
| `criteria` | `object` | — | — | Per-criterion thresholds. Any subset of: min_frames_captured, min_duration_s, min_depth_valid_ratio, require_return_to_start. Unsupplied keys fall back to defaults. |
| `executor_result` | `object` | — | — | The dict execute_trajectory returned. Required only when require_return_to_start=True is in criteria — the recorder doesn't know whether the trajectory looped back; the executor does. |

---

## `get_collection_status`

**Module:** [`modulated_system/tools/collection/memory.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/collection/memory.py#L220)  ·  **Python function:** `get_collection_status`  ·  **Description source:** decorator `description=`

Snapshot the active spec, per-target progress, recent events, and the whole-spec stop-condition verdict. The agent typically calls this once per outer loop tick to decide what to do next.

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `max_recent_events` | `integer` | — | `20` | Cap the recent-events tail to keep the response bounded. |

---

## `list_workspaces`

**Module:** [`modulated_system/tools/collection/workspace_catalog.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/collection/workspace_catalog.py#L134)  ·  **Python function:** `list_workspaces`  ·  **Description source:** decorator `description=`

Return every workspace in the session catalog. Reads runtime/sessions/<id>/workspaces.json. Returns an empty list (NOT an error) when no catalog file exists yet.

---

## `log_event`

**Module:** [`modulated_system/tools/collection/memory.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/collection/memory.py#L26)  ·  **Python function:** `log_event`  ·  **Description source:** decorator `description=`

Append a free-form event to the collection log. Used by the agent + the higher-level orchestrator to record decisions, failure modes, phase transitions, and anything else that should land in the persistent run history. event_type is open-vocabulary; common ones: failure, phase_change, target_lost, optimizer_skip, rerun_decision.

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `event_type` | `string` | ✓ | — | Open-vocabulary tag (e.g. 'failure', 'phase_change'). |
| `message` | `string` | — | `''` | Human-readable summary line. |
| `details` | `object` | — | — | Arbitrary JSON-serializable context. |

---

## `register_labeled_object`

**Module:** [`modulated_system/tools/collection/workspace.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/collection/workspace.py#L159)  ·  **Python function:** `register_labeled_object`  ·  **Description source:** decorator `description=`

Append a labeled object to the persistent catalog. Manual entry today (the supervisor labeler will write here once it lands). Use after detect_target to remember a found object's world position, or to seed the catalog with known scene objects.

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `label` | `string` | ✓ | — | Short label (e.g., 'mug', 'lego_fire_station'). |
| `xyz` | `array` | ✓ | — | World-frame [x, y, z] (m). |
| `confidence` | `number` | — | `1.0` | Detection confidence in [0, 1]. |

---

## `register_workspace`

**Module:** [`modulated_system/tools/collection/workspace_catalog.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/collection/workspace_catalog.py#L69)  ·  **Python function:** `register_workspace`  ·  **Description source:** decorator `description=`

Persist a named tabletop workspace (polygon + z-band + 3D anchor) to the session catalog at runtime/sessions/<id>/workspaces.json. Re-registering an existing name overwrites that entry. Idempotent + atomic (crash-safe via .tmp + rename). Pair with `list_workspaces` and `activate_workspace` for the multi-table replay flow.

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `name` | `string` | ✓ | — | Unique workspace name (e.g. 'table_00'). |
| `corners` | `array` | ✓ | — | World-frame XY polygon, list of [x, y]. |
| `z_min` | `number` | ✓ | — | Workspace floor (m), world frame. |
| `z_max` | `number` | ✓ | — | Workspace ceiling (m), world frame. |
| `anchor_xyz` | `array` | ✓ | — | [x, y, z] navigate_to target. |
| `metadata` | `object` | — | — | Free-form per-table metadata (detection stats, timestamps, etc.) |

---

## `reset_collection_state`

**Module:** [`modulated_system/tools/collection/reset.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/collection/reset.py#L18)  ·  **Python function:** `reset_collection_state`  ·  **Description source:** decorator `description=`

Hard-reset the persistent collection state. Wipes events + episodes; optionally wipes the active data spec too. Removes the state.json file from disk. REQUIRES confirm=true to fire — without it, the call returns an error rather than deleting anything (so an accidental dispatch doesn't nuke a long-running collection).

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `confirm` | `boolean` | ✓ | — | Must be literally true. Returns an error if false / missing — protects against accidental fires from a stale tool form. |
| `keep_spec` | `boolean` | — | `False` | If true, drop episodes + events but keep the active spec (so you can immediately re-run collection against the same target list). If false (default), drop everything including the spec — the next step has to be create_data_spec. |

---

## `select_point_in_workspace`

**Module:** [`modulated_system/tools/collection/workspace.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/collection/workspace.py#L226)  ·  **Python function:** `select_point_in_workspace`  ·  **Description source:** decorator `description=`

Pick a salient point inside the active workspace. Modes:
  next_object — least-captured labeled object inside the workspace (ties broken by recency).
  random — uniformly random point in the polygon, z ∈ [z_min, z_max].
  drivable — random point where the base can stand (costmap below lethal AND no octomap obstacle above). Useful for 'find me somewhere to park'.
  occupied — random OCCUPIED octomap voxel inside the workspace. Useful for 'look at something concrete'.
  exploration — random point in workspace with no occupied octomap voxel nearby (i.e. unobserved). Useful for scanning unexplored areas.

---

## `store_episode_summary`

**Module:** [`modulated_system/tools/collection/memory.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/collection/memory.py#L75)  ·  **Python function:** `store_episode_summary`  ·  **Description source:** decorator `description=`

Record a captured episode in the collection memory. Most callers don't need this — `stop_recording` finalizes the episode.json on disk and the supervisor's evaluator hook writes the summary. This standalone tool is for backfilling summaries from disk or for recorders that bypass the start_recording / stop_recording pair.

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `target_id` | `string` | ✓ | — | Which target this episode belongs to. |
| `episode_dir` | `string` | — | `''` | Path to the episode directory on disk. |
| `n_frames` | `integer` | ✓ | — | Frames captured. |
| `duration_s` | `number` | — | `0.0` | Wall-clock duration of the capture. |
| `trajectory_type` | `string` | — | `''` | orbit / linear_aimed / sphere_orbit / etc. |
| `motion` | `string` | — | `''` | Legacy field kept for back-compat — the camera-centric pipeline always plans whole-body, so leave this empty unless backfilling old data where the split mattered. |
| `robot_yaw_at_target_deg` | `number` | — | — | Angle from target to robot at the trajectory start (deg, world). Drives the single-bin fallback when robot_yaw_at_target_bins is empty. Pass atan2(robot_y - target_y, robot_x - target_x) in degrees. |
| `robot_yaw_at_target_bins` | `array` | — | — | 30°-bin indices the trajectory crossed (orbit sweeps span 2 adjacent bins). Empty -> compute from robot_yaw_at_target_deg. |
| `target_distance_m` | `number` | — | — | Robot-to-target distance at the trajectory start (m). Used as the distance-bin fallback when target_distance_bins is empty. |
| `target_distance_bins` | `array` | — | — | Distance bins (per core.collection.rules) the trajectory crossed. Multi-bin sweeps (approach_retreat) populate multiple entries; single-pose captures populate one. Empty list means 'compute from target_distance_m'. |
| `accepted` | `boolean` | — | `True` | False if the episode failed the evaluator. Rejected episodes don't count toward coverage. |
| `reject_reason` | `string` | — | — | Human-readable reason when accepted=False. |
| `episode_id` | `string` | — | — | Override the auto-generated id. |
| `extra` | `object` | — | — | Arbitrary JSON metadata. |

---

## `summarize_data_gaps`

**Module:** [`modulated_system/tools/collection/data_spec.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/collection/data_spec.py#L288)  ·  **Python function:** `summarize_data_gaps`  ·  **Description source:** decorator `description=`

Per-target progress dashboard: for every declared target (plus any target with episodes but no spec entry), report frames / episodes / yaw coverage / distance bins / status. Status is 'done' when the spec rules are satisfied, 'needs_more' otherwise.

---

## `update_coverage_state`

**Module:** [`modulated_system/tools/collection/update_coverage_state.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/collection/update_coverage_state.py#L95)  ·  **Python function:** `update_coverage_state`  ·  **Description source:** decorator `description=`

Recompute the per-target coverage rollup from recorded episodes — yaw bins covered, distance bins covered, frame + episode counts, rejection counts. Read by request_next_view and choose_collection_site to decide where to go next. Coverage is computed on demand; this tool returns the latest rollup and does NOT mutate stored state.

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `yaw_bin_size_deg` | `number` | — | `30.0` | Width of each yaw coverage bin in degrees. Default 30 (12 bins). Match the value request_next_view uses or the score will lie. |
| `distance_bin_edges_m` | `array` | — | — | Ascending list of upper-bound distance edges in metres. Episodes farther than the last edge fall into the last bin. Default [0.5, 1.0, 1.5, 2.5] → 5 bins (close / mid-near / mid / far / very-far). |
| `target_id` | `string` | — | — | Compute coverage for one target only. Default covers every target in the active spec. |

---

## `update_data_spec`

**Module:** [`modulated_system/tools/collection/data_spec.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/collection/data_spec.py#L144)  ·  **Python function:** `update_data_spec`  ·  **Description source:** decorator `description=`

Update fields on the active data spec. Pass `add_targets` to append new targets without rewriting existing ones; pass any of the per_target_* thresholds to retune the rules mid-run. Returns the updated spec snapshot.

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `data_spec_id` | `string` | — | — | Verify against the active spec_id — protects against accidentally mutating the wrong spec after a server restart. Optional; if omitted, updates whatever spec is active. |
| `description` | `string` | — | — | Replace the spec description. |
| `add_targets` | `array` | — | — | Targets to append (skips dupes by target_id). |
| `per_target_min_frames` | `integer` | — | — | New frame threshold. |
| `per_target_min_yaw_deg` | `number` | — | — | New yaw threshold. |
| `per_target_min_distance_bins` | `integer` | — | — | New distance-bin threshold. |
| `per_target_min_episodes` | `integer` | — | — | New episode threshold. |

---

## `update_target_position`

**Module:** [`modulated_system/tools/collection/update_target_position.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/collection/update_target_position.py#L31)  ·  **Python function:** `update_target_position`  ·  **Description source:** decorator `description=`

Set or replace the world-frame position_w on an EXISTING target in the active DataSpec. Used to write a freshly-detected target's coordinates into the spec so request_next_view / choose_collection_site can plan around it. Returns success=False with an explanatory reason if no spec is active or target_id isn't in the spec — does NOT auto-create the target (use update_data_spec(add_targets=...) for that).

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `target_id` | `string` | ✓ | — | Target id from the active DataSpec. |
| `position_w` | `array` | ✓ | — | World-frame [x, y, z] in metres. Typically from detect_target's target_position_w. Must be a 3-vector. |
| `description` | `string` | — | — | Optional new description. Default: leave the target's existing description unchanged. |

---


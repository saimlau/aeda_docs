# Tools — `perception` (8)

See the world. Vision + grounding tools — Gemini Robotics-ER 1.6 detection, RAM++ open-set labelling, SAM3 masks, depth back-projection.

## In this category

- [`check_target_in_frame`](#check_target_in_frame) — Returns:
- [`detect_target`](#detect_target) — Find an object in the latest camera frame and estimate its 3D position in world frame. Cascade: SAM3 (precise pixel) → Gemini Robotics-ER 1.6 (pointing + 2D bbox + 3D bbox). Returns target_position_w = [x, y, z] in world frame, plus confidence, label, and the detected pixel for the agent's next move (e.g. 'navigate_to(x, y)' or 'start_recording(target_xyz=...)' followed by generate_view_trajectory + execute_trajectory). The agent should feed a literal noun (e.g. 'mug', 'pillar') into target_object_hint, NOT abstract categories like 'electronic device' or 'thing on table'.
- [`estimate_target_visibility`](#estimate_target_visibility) — Returns a dict with confidence + diagnostic flags.
- [`find_cluster_target`](#find_cluster_target) — Find the visible object whose 3D position is surrounded by the most OTHER detections — i.e. the densest cluster. Preferred selector for depth-data collection: clusters give more varied depth context than isolated objects. Composes list_objects_in_view + detect_target with a configurable exclusion list (defaults skip walls, floors, big furniture, screens, and reflection traps).
- [`identify_objects_vision`](#identify_objects_vision) — Ask Gemini-vision to propose anchor candidates with pixel centers + rationale. Use when list_objects_in_view returns only generic scene tags (floor, room, carpet) or every detect_target call comes back under ~20%% confidence. The labels are detect_target-friendly nouns; pass them through detect_target for actual 3D unprojection.
- [`list_objects_in_view`](#list_objects_in_view) — Return short common-noun tags for objects visible in the EEF camera (RAM preferred, Gemini fallback). Pick one of the tags as a hint for detect_target — don't guess strings like 'object on table' which SAM3 rejects with low confidence. Returns {success, tags: [...], source: 'ram' | 'gemini' | 'none'}.
- [`scan_room_for_tables`](#scan_room_for_tables) — Rotate the base 360° detecting tables every K°. Clusters duplicate detections (same physical table from adjacent frames). Each cluster is validated by AIMING the EE camera at the cluster from the current base pose (no driving) and re-detecting; clusters that survive the arm-look become table anchors. Returns the list of anchors for downstream per-table loops. Requires manipulator + execute_trajectory.
- [`score_view_novelty`](#score_view_novelty) — Score how much new information the current robot+camera configuration would capture about a target. Combines voxel novelty (octomap voxels near target not yet seen) and yaw-bin uniqueness (have we already captured this bearing of the target?). Returns score ∈ [0, 1] plus diagnostic components. Used by request_next_view to rank candidates and by the agent for 'is this view worth capturing?' calls.

---

## `check_target_in_frame`

**Module:** [`modulated_system/tools/perception/check_target_in_frame.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/perception/check_target_in_frame.py#L30)  ·  **Python function:** `check_target_in_frame`  ·  **Description source:** function docstring

Returns:

{
  "success":   True,
  "in_frame":  bool,
  "reason":    "visible" | "off_image" | "too_far" |
               "behind_camera" | ...,
  "pixel":     [u, v] | None,
  "depth_m":   float | None,
  "distance_m": float | None,
  "target":    [x, y, z] in world frame,
  "camera_pose": 4x4 list-of-lists,
}

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `target_id` | `string` | — | — | Target id from the active DataSpec. Mutually exclusive with target_position_w. |
| `target_position_w` | `array` | — | — | Explicit (x, y, z) world-frame target position in metres. Use when no DataSpec is active or you want to test an arbitrary point. |
| `max_depth_m` | `number` | — | `10.0` | Reject points farther than this in the camera +Z direction (in-frame=False, reason='too_far'). Default 10 m matches the iPhone depth's reliable-return cutoff. |
| `pixel_margin` | `integer` | — | `0` | Shrink the in-frame window by this many pixels on each side. Useful to require the target sit comfortably inside the image (e.g. 32 px) rather than clipping the edge. |

---

## `detect_target`

**Module:** [`modulated_system/tools/perception/detect_target.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/perception/detect_target.py#L33)  ·  **Python function:** `detect_target`  ·  **Description source:** decorator `description=`

Find an object in the latest camera frame and estimate its 3D position in world frame. Cascade: SAM3 (precise pixel) → Gemini Robotics-ER 1.6 (pointing + 2D bbox + 3D bbox). Returns target_position_w = [x, y, z] in world frame, plus confidence, label, and the detected pixel for the agent's next move (e.g. 'navigate_to(x, y)' or 'start_recording(target_xyz=...)' followed by generate_view_trajectory + execute_trajectory). The agent should feed a literal noun (e.g. 'mug', 'pillar') into target_object_hint, NOT abstract categories like 'electronic device' or 'thing on table'.

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `target_object_hint` | `string` | ✓ | — | Concrete noun (e.g. 'red mug', 'office chair'). SAM3 / Gemini ER both handle short phrases. |
| `sensor_name` | `string` | — | — | Which RGBD sensor to use. Defaults to first rgbd-typed sensor on the platform. |

---

## `estimate_target_visibility`

**Module:** [`modulated_system/tools/perception/estimate_target_visibility.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/perception/estimate_target_visibility.py#L67)  ·  **Python function:** `estimate_target_visibility`  ·  **Description source:** function docstring

Returns a dict with confidence + diagnostic flags.

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `target_id` | `string` | — | — | Target id from the active DataSpec. |
| `target_position_w` | `array` | — | — | Explicit world-frame target position [x, y, z]. |
| `voxel_radius_m` | `number` | — | `0.06` | Octomap occlusion-ray capsule half-width. Slightly larger than the 5 cm voxel size so a voxel center near the line counts as a blocker. |
| `target_radius_m` | `number` | — | `0.08` | Ignore octomap voxels within this distance of the target itself — the target's own voxels would otherwise self-occlude. |
| `max_depth_m` | `number` | — | `10.0` | Frustum far-plane cutoff. |

---

## `find_cluster_target`

**Module:** [`modulated_system/tools/perception/find_cluster_target.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/perception/find_cluster_target.py#L53)  ·  **Python function:** `find_cluster_target`  ·  **Description source:** decorator `description=`

Find the visible object whose 3D position is surrounded by the most OTHER detections — i.e. the densest cluster. Preferred selector for depth-data collection: clusters give more varied depth context than isolated objects. Composes list_objects_in_view + detect_target with a configurable exclusion list (defaults skip walls, floors, big furniture, screens, and reflection traps).

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `cluster_radius_m` | `number` | — | `1.0` | Neighbor-distance threshold (m). |
| `max_tags` | `integer` | — | `8` | Cap on detect_target calls (each ~0.5-1 s). |
| `min_z_m` | `number` | — | `0.54` | Reject detections below this height (m). Lower for floor-object collection. |
| `exclude_tags` | `array` | — | — | Additional tags to skip on top of DEFAULT_EXCLUDE. |
| `vision_focus` | `string` | — | — | If list_objects_in_view returns generic scene tags, this hint biases identify_objects_vision. E.g. 'far-range furniture'. |

---

## `identify_objects_vision`

**Module:** [`modulated_system/tools/perception/list_objects_in_view.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/perception/list_objects_in_view.py#L90)  ·  **Python function:** `identify_objects_vision`  ·  **Description source:** decorator `description=`

Ask Gemini-vision to propose anchor candidates with pixel centers + rationale. Use when list_objects_in_view returns only generic scene tags (floor, room, carpet) or every detect_target call comes back under ~20%% confidence. The labels are detect_target-friendly nouns; pass them through detect_target for actual 3D unprojection.

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `focus` | `string` | — | — | Optional hint narrowing the search (e.g. 'far-range furniture', 'pillar or doorway'). |
| `max_items` | `integer` | — | `6` | Cap on returned candidates. |
| `sensor_name` | `string` | — | — | Which RGBD sensor to read. Defaults to first rgbd. |

---

## `list_objects_in_view`

**Module:** [`modulated_system/tools/perception/list_objects_in_view.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/perception/list_objects_in_view.py#L26)  ·  **Python function:** `list_objects_in_view`  ·  **Description source:** decorator `description=`

Return short common-noun tags for objects visible in the EEF camera (RAM preferred, Gemini fallback). Pick one of the tags as a hint for detect_target — don't guess strings like 'object on table' which SAM3 rejects with low confidence. Returns {success, tags: [...], source: 'ram' | 'gemini' | 'none'}.

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `sensor_name` | `string` | — | — | Which RGBD sensor to read. Defaults to first rgbd. |

---

## `scan_room_for_tables`

**Module:** [`modulated_system/tools/perception/scan_room_for_tables.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/perception/scan_room_for_tables.py#L114)  ·  **Python function:** `scan_room_for_tables`  ·  **Description source:** decorator `description=`

Rotate the base 360° detecting tables every K°. Clusters duplicate detections (same physical table from adjacent frames). Each cluster is validated by AIMING the EE camera at the cluster from the current base pose (no driving) and re-detecting; clusters that survive the arm-look become table anchors. Returns the list of anchors for downstream per-table loops. Requires manipulator + execute_trajectory.

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `rotate_step_deg` | `number` | — | `30.0` | Rotation step between detect frames. 30° default gives 2× FOV overlap on the iPhone camera (~60° FOV) so most tables get 2-3 detections. |
| `settle_s` | `number` | — | `1.0` | Wait time per snapshot for octomap + camera settle. |
| `cluster_dist_m` | `number` | — | `0.6` | Greedy XY clustering distance — detections within this radius merge into one cluster. |
| `min_confidence` | `number` | — | `0.55` | detect_target confidence gate per snapshot. Detections below this don't enter the cluster pool. No min_cluster_size — singletons pass to Phase 1b where the close-up re-detect validates them. |
| `confirm_offset_m` | `number` | — | `1.5` | DEPRECATED (2026-05-24): Phase 1b no longer drives; the value is ignored. Kept for backwards compatibility with scripts that still pass it. |
| `base_yaw_align_deg` | `number` | — | `60.0` | If the cluster sits more than this many degrees off the robot's current heading, rotate the base in place before the arm-look so the camera can actually point at it. 60° keeps the look-at within typical FR3 wrist reach. |
| `view_cam_z` | `number` | — | `1.1` | World-frame Z of the camera during the arm-look. Raised above 1.0 m so cuRobo's IK is forced to elbow-up solutions instead of elbow-behind/down (the latter swept past the laptop mounted on the robot's back at the lab on 2026-05-24). |
| `view_cam_forward_m` | `number` | — | `0.3` | Forward offset of the camera from base_link during the arm-look. Same default as survey_scene_pose. |

---

## `score_view_novelty`

**Module:** [`modulated_system/tools/perception/score_view_novelty.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/perception/score_view_novelty.py#L38)  ·  **Python function:** `score_view_novelty`  ·  **Description source:** decorator `description=`

Score how much new information the current robot+camera configuration would capture about a target. Combines voxel novelty (octomap voxels near target not yet seen) and yaw-bin uniqueness (have we already captured this bearing of the target?). Returns score ∈ [0, 1] plus diagnostic components. Used by request_next_view to rank candidates and by the agent for 'is this view worth capturing?' calls.

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `target_id` | `string` | — | — | Target id; required if you want yaw-bin coverage. |
| `target_position_w` | `array` | — | — | Explicit world-frame [x, y, z]. |
| `robot_position_w` | `array` | — | — | Explicit robot (x, y) in world frame for the yaw-bin lookup. Defaults to ctx.robot.bridge.get_robot_pose() — pass when scoring a CANDIDATE pose rather than the robot's current spot. |
| `novelty_radius_m` | `number` | — | `1.0` | Voxels farther than this from the target are ignored. |
| `voxel_size_m` | `number` | — | `0.05` | Octomap resolution; matches octomap_server config. |
| `yaw_bin_size_deg` | `number` | — | `30.0` | Width of each coverage yaw bin (deg). |

---


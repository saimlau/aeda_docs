# Tools — `perception` (8)

See the world. Vision + grounding tools — Gemini Robotics-ER 1.6 detection, RAM++ open-set labelling, SAM3 masks, depth back-projection.

## In this category

- [`check_target_in_frame`](#check_target_in_frame) — Returns:
- [`detect_target`](#detect_target) — _(no docstring)_
- [`estimate_target_visibility`](#estimate_target_visibility) — Returns a dict with confidence + diagnostic flags.
- [`find_cluster_target`](#find_cluster_target) — _(no docstring)_
- [`identify_objects_vision`](#identify_objects_vision) — _(no docstring)_
- [`list_objects_in_view`](#list_objects_in_view) — _(no docstring)_
- [`scan_room_for_tables`](#scan_room_for_tables) — _(no docstring)_
- [`score_view_novelty`](#score_view_novelty) — _(no docstring)_

---

## `check_target_in_frame`

**Module:** [`modulated_system/tools/perception/check_target_in_frame.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/perception/check_target_in_frame.py#L30)  ·  **Python function:** `check_target_in_frame`

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

---

## `detect_target`

**Module:** [`modulated_system/tools/perception/detect_target.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/perception/detect_target.py#L33)  ·  **Python function:** `detect_target`

_No docstring._

---

## `estimate_target_visibility`

**Module:** [`modulated_system/tools/perception/estimate_target_visibility.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/perception/estimate_target_visibility.py#L67)  ·  **Python function:** `estimate_target_visibility`

Returns a dict with confidence + diagnostic flags.

---

## `find_cluster_target`

**Module:** [`modulated_system/tools/perception/find_cluster_target.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/perception/find_cluster_target.py#L53)  ·  **Python function:** `find_cluster_target`

_No docstring._

---

## `identify_objects_vision`

**Module:** [`modulated_system/tools/perception/list_objects_in_view.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/perception/list_objects_in_view.py#L90)  ·  **Python function:** `identify_objects_vision`

_No docstring._

---

## `list_objects_in_view`

**Module:** [`modulated_system/tools/perception/list_objects_in_view.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/perception/list_objects_in_view.py#L26)  ·  **Python function:** `list_objects_in_view`

_No docstring._

---

## `scan_room_for_tables`

**Module:** [`modulated_system/tools/perception/scan_room_for_tables.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/perception/scan_room_for_tables.py#L114)  ·  **Python function:** `scan_room_for_tables`

_No docstring._

---

## `score_view_novelty`

**Module:** [`modulated_system/tools/perception/score_view_novelty.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/perception/score_view_novelty.py#L38)  ·  **Python function:** `score_view_novelty`

_No docstring._

---


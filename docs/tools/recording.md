# Tools — `recording` (2)

Capture episodes. `start_recording` / `stop_recording`, episode evaluation, keeper-manifest management.

## In this category

- [`start_recording`](#start_recording) — Open a new episode and start continuous RGB+depth+pose capture in the background. Pair with stop_recording. While recording, run generate_view_trajectory + execute_trajectory normally; every camera frame the sim / iPhone publishes lands in the episode directory.
- [`stop_recording`](#stop_recording) — Finalize the active episode opened by start_recording. Writes the closed episode.json, stops the continuous capture thread, and returns the recorder's summary (total_frames, duration_s, episode_dir, quality stats). Idempotent — safe to call when no episode is active.

---

## `start_recording`

**Module:** [`modulated_system/tools/recording/start_recording.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/recording/start_recording.py#L32)  ·  **Python function:** `start_recording`  ·  **Description source:** decorator `description=`

Open a new episode and start continuous RGB+depth+pose capture in the background. Pair with stop_recording. While recording, run generate_view_trajectory + execute_trajectory normally; every camera frame the sim / iPhone publishes lands in the episode directory.

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `target_object_id` | `string` | ✓ | — | Identifier for the captured target (e.g., 'mug', 'tree_5'). Stored in episode.json's meta.collection_metadata. Used downstream by the episode evaluator. |
| `target_xyz` | `array` | ✓ | — | World-frame [x, y, z] of the target object. Used by the evaluator for distance / yaw-bin scoring. |
| `hz` | `number` | — | `10.0` | Continuous capture rate (frames/s). Default 10. Drops to whatever the camera publisher can sustain if higher than the topic's rate. |
| `timeout_s` | `number` | — | `600.0` | Auto-stop the episode if stop_recording isn't called within this many seconds. Safety guard against forgotten stops / agent crashes. |
| `metadata` | `object` | — | — | Free dict written to episode.json's meta.collection_metadata alongside the target fields. |

---

## `stop_recording`

**Module:** [`modulated_system/tools/recording/stop_recording.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/recording/stop_recording.py#L29)  ·  **Python function:** `stop_recording`  ·  **Description source:** decorator `description=`

Finalize the active episode opened by start_recording. Writes the closed episode.json, stops the continuous capture thread, and returns the recorder's summary (total_frames, duration_s, episode_dir, quality stats). Idempotent — safe to call when no episode is active.

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `episode_id` | `string` | — | — | Optional safety check: if provided, must match the active episode_id (the path returned by start_recording). Mismatches are rejected with a clear error so an agent doesn't accidentally close someone else's episode. |
| `description` | `string` | — | — | Natural-language description of what motion actually executed during the recording (e.g. '180 deg sphere orbit r=0.35 m, 9 waypoints in 5.5 s'). Stored under meta.collection_metadata.description in the finalized episode.json. |
| `metadata` | `object` | — | — | Free dict merged into the episode's meta.collection_metadata at finalize time. Use for outcome-only fields (executed waypoints, elapsed time, success flags, etc.) that aren't knowable at start_recording time. Keys override any matching entry from start_recording. |

---


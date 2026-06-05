# `aeda.tools`

`aeda.tools` is the entry point to every registered `@tool` in
`modulated_system`. Each tool is a Python function decorated with `@tool`
that gets surfaced into `aeda.tools.<name>` and (in parallel) into the
supervisor's tool catalog.

!!! note "Signatures here are illustrative"
    The catalog and signatures below are a hand-curated overview. The
    canonical definitions live in the source tree at
    [`modulated_system/tools/`](https://github.com/Pengyu-Mo/tidyros_iphone/tree/main/modulated_system/tools).

## Calling a tool

```python
res = aeda.tools.move_camera_relative(
    dx=0.0, dy=0.0, dz=0.05, speed_factor=0.10,
)
```

Tools return a `ToolResult`: a structured object with at minimum
`success: bool` + `message: str`, plus a tool-specific `data` payload.

## The `@tool` contract

Every tool registered with `@tool`:

- **Takes a `ToolContext`** as its first arg (the bridge to the session,
  sensor fuser, planner clients).
- **Returns a `ToolResult`** with at least `success: bool` and `message: str`.
- **Logs side effects** to the session directory.
- **Doesn't raise** on expected failure modes — returns
  `success=False` plus a remediation hint instead (except for
  `AedaInterrupt`, which always propagates).

See **[Guides: writing a tool](../guides/writing-a-tool.md)** for the full
walkthrough.

## Catalog (illustrative)

### Motion

- `navigate_to(x, y, theta, ...)` — base navigation via Nav2.
- `move_camera_relative(dx, dy, dz, drx, dry, drz, speed_factor)` — arm IK
  hop to a relative camera pose.
- `rotate_joint(joint_idx, target_rad, speed_factor)` — single-joint
  absolute rotation (FR3 j0–j6).
- `execute_trajectory(waypoints, ...)` — whole-body trajectory execution.
- `recover_arm()` — re-arm after a brake / reflex event.

### Trajectory generators

- `generate_view_trajectory(trajectory_type, target_x, target_y, target_z,
  generator_params)` — builds a camera path (sphere_orbit,
  look_away_return, bezier, …).
- `compute_parking_locations(target_x, target_y, ...)` — base parking
  candidates around a target, base-collision-aware.
- `find_feasible_params(trajectory_type, target_xyz, ...)` — IK-feasible
  parameter search.

### Perception

- `detect_target(hint)` — Gemini Robotics-ER 1.6 detection: 2D point +
  bbox + confidence.
- `check_target_in_frame(hint)` — fast vision presence check.

### Recording

- `start_recording(target_object_id, ...)` — begin an episode.
- `stop_recording(...)` — end + persist an episode.
- `evaluate_episode(episode_id, ...)` — score an episode against the data
  spec.

### Memory / state

- `set_data_spec(...)`, `reset_collection_state()`, `reset_memory()`.

## Source

- Tool registration:
  [`modulated_system/runtime/ui/aeda_sdk/`](https://github.com/Pengyu-Mo/tidyros_iphone/tree/main/modulated_system/runtime/ui/aeda_sdk)
- Tool implementations:
  [`modulated_system/tools/`](https://github.com/Pengyu-Mo/tidyros_iphone/tree/main/modulated_system/tools)

# Tools — `meta` (12)

Tool catalog about itself + supervisor I/O. Notify supervisor, inspect tool schemas, reset memory.

## In this category

- [`analyze_recording`](#analyze_recording) — Post-hoc summary of one episode: report acceptance, frame count, criterion breakdown, paths to images/depth/episode.json. Pass episode_id (the directory name under episodes/). Use to decide whether to dive into the raw recording.
- [`append_memory`](#append_memory) — Append a body of text to a persistent-memory learning file (creates the file if it doesn't exist). Use to record cross-session learnings: lab quirks, parameter tuning that worked, failure patterns to avoid. Pair with update_memory_index so future sessions can find it.
- [`get_executor_state`](#get_executor_state) — Read the current executor_state from control.json: which task is running, which phase (running/paused/interrupted), the last heartbeat. Returns empty state if the Executor hasn't started yet.
- [`get_map_snapshot`](#get_map_snapshot) — Snapshot of the active costmap stack. Returns layer extents, cell-value histogram, and the robot's current pose. Use to decide whether the map is well-populated enough to navigate, or whether the supervisor should inject a primer note telling the executor to explore first. Pass include_grid=true for a base64 PNG of the fused costmap (heavier — only when you actually need to look at the shape).
- [`get_trajectory_history`](#get_trajectory_history) — Per-target episode summary + recent capture history. Returns what the data flywheel has actually covered so far: episode counts, frame totals, yaw/distance bin coverage, the bounding box of robot poses around each target, and the most-recent N episodes flattened. Use to decide which target needs more data, or to see if the executor has been re-picking the same viewpoint repeatedly.
- [`inject_primer_note`](#inject_primer_note) — Write a live supervisor->worker note that the executor's next prompt will append verbatim. Pass an empty body to clear the note. The previous note is auto-archived.
- [`notify_supervisor`](#notify_supervisor) — Escalate a finding or blocker to the SUPERVISOR. Appends a worker_note event that the supervisor's watcher forwards to its next turn. This is the ONLY worker->supervisor channel — text in your chat / cot / local files does NOT reach the supervisor (inject_primer_note is the reverse direction). Use severity 'warning'/'blocker' to reach the supervisor immediately; 'info' is batched with other events.
- [`query_log`](#query_log) — Grep across the session's progress/events.jsonl + logs/* for a regex pattern. Optionally filter to events of a specific event_type. Useful for the supervisor to find stuck-pattern events, slow tasks, or specific tool failures.
- [`read_memory`](#read_memory) — Read one file from the persistent-memory workspace (~/.claude_aeda/memory/<workspace>/learnings/<filename>.md). Call this when MEMORY.md cites a learning you want to pull into the current Claude turn's context.
- [`send_executor_command`](#send_executor_command) — "Append a command to the Executor's control.json channel. " + _VALID_KINDS_DOC + ' The Executor reads commands at task-loop top, monitor ticks, and pre-retry points. Returns the generated command_id.'
- [`update_memory_index`](#update_memory_index) — Append a single-line markdown entry to the workspace's MEMORY.md index. Convention: '- `[name](learnings/name.md)` — <one-line summary>'. The index is loaded on every Supervisor startup so an indexed learning is always discoverable.
- [`update_plan`](#update_plan) — Replace the active collection plan for a session. The plan worker picks up the new plan between tasks. The previous plan is archived under plans/history/. Returns the path to the new active plan + the archived predecessor (if any).

---

## `analyze_recording`

**Module:** [`modulated_system/tools/meta/analyze_recording.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/meta/analyze_recording.py#L20)  ·  **Python function:** `analyze_recording`  ·  **Description source:** decorator `description=`

Post-hoc summary of one episode: report acceptance, frame count, criterion breakdown, paths to images/depth/episode.json. Pass episode_id (the directory name under episodes/). Use to decide whether to dive into the raw recording.

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `episode_id` | `string` | ✓ | — | Episode directory name (e.g. 'episode_20260509_120000'). |
| `session_id` | `string` | — | — | Override session resolution. |

---

## `append_memory`

**Module:** [`modulated_system/tools/meta/append_memory.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/meta/append_memory.py#L13)  ·  **Python function:** `append_memory`  ·  **Description source:** decorator `description=`

Append a body of text to a persistent-memory learning file (creates the file if it doesn't exist). Use to record cross-session learnings: lab quirks, parameter tuning that worked, failure patterns to avoid. Pair with update_memory_index so future sessions can find it.

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `workspace` | `string` | ✓ | — |  |
| `filename` | `string` | ✓ | — | Without extension (e.g. 'lab-network'). |
| `body` | `string` | ✓ | — | Markdown text to append. |

---

## `get_executor_state`

**Module:** [`modulated_system/tools/meta/get_executor_state.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/meta/get_executor_state.py#L11)  ·  **Python function:** `get_executor_state`  ·  **Description source:** decorator `description=`

Read the current executor_state from control.json: which task is running, which phase (running/paused/interrupted), the last heartbeat. Returns empty state if the Executor hasn't started yet.

---

## `get_map_snapshot`

**Module:** [`modulated_system/tools/meta/get_map_snapshot.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/meta/get_map_snapshot.py#L53)  ·  **Python function:** `get_map_snapshot`  ·  **Description source:** decorator `description=`

Snapshot of the active costmap stack. Returns layer extents, cell-value histogram, and the robot's current pose. Use to decide whether the map is well-populated enough to navigate, or whether the supervisor should inject a primer note telling the executor to explore first. Pass include_grid=true for a base64 PNG of the fused costmap (heavier — only when you actually need to look at the shape).

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `include_grid` | `boolean` | — | `False` | True → include base64-encoded PNG of the fused costmap in the response. Default false (stats only) so a routine snapshot stays cheap. |
| `downsample` | `integer` | — | `4` | Stride for the histogram + PNG render. Higher = cheaper at the cost of resolution. Default 4. |

---

## `get_trajectory_history`

**Module:** [`modulated_system/tools/meta/get_trajectory_history.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/meta/get_trajectory_history.py#L47)  ·  **Python function:** `get_trajectory_history`  ·  **Description source:** decorator `description=`

Per-target episode summary + recent capture history. Returns what the data flywheel has actually covered so far: episode counts, frame totals, yaw/distance bin coverage, the bounding box of robot poses around each target, and the most-recent N episodes flattened. Use to decide which target needs more data, or to see if the executor has been re-picking the same viewpoint repeatedly.

---

## `inject_primer_note`

**Module:** [`modulated_system/tools/meta/inject_primer_note.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/meta/inject_primer_note.py#L20)  ·  **Python function:** `inject_primer_note`  ·  **Description source:** decorator `description=`

Write a live supervisor->worker note that the executor's next prompt will append verbatim. Pass an empty body to clear the note. The previous note is auto-archived.

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `body` | `string` | ✓ | — | Note body in plain Markdown. Empty string clears the active note. |
| `session_id` | `string` | — | — | Override session resolution. Defaults to ctx.session_dir / AEDA_SESSION_ID / 'default'. |

---

## `notify_supervisor`

**Module:** [`modulated_system/tools/meta/notify_supervisor.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/meta/notify_supervisor.py#L24)  ·  **Python function:** `notify_supervisor`  ·  **Description source:** decorator `description=`

Escalate a finding or blocker to the SUPERVISOR. Appends a worker_note event that the supervisor's watcher forwards to its next turn. This is the ONLY worker->supervisor channel — text in your chat / cot / local files does NOT reach the supervisor (inject_primer_note is the reverse direction). Use severity 'warning'/'blocker' to reach the supervisor immediately; 'info' is batched with other events.

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `message` | `string` | ✓ | — | The finding/blocker, plain text. Be specific + actionable. |
| `severity` | `string` | — | — | info ¦ warning ¦ blocker (default info). warning and blocker flush to the supervisor immediately; info is batched. |
| `category` | `string` | — | — | Optional tag, e.g. 'feasibility', 'plan', 'hardware'. |
| `session_id` | `string` | — | — | Override session resolution. Defaults to this session. |

---

## `query_log`

**Module:** [`modulated_system/tools/meta/query_log.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/meta/query_log.py#L55)  ·  **Python function:** `query_log`  ·  **Description source:** decorator `description=`

Grep across the session's progress/events.jsonl + logs/* for a regex pattern. Optionally filter to events of a specific event_type. Useful for the supervisor to find stuck-pattern events, slow tasks, or specific tool failures.

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `pattern` | `string` | ✓ | — | Python regex. Searched against each line (events.jsonl) or each log line. |
| `since_ts` | `number` | — | `0.0` | Only consider events with ts >= this value. |
| `event_type_filter` | `string` | — | — | Restrict events.jsonl matches to this exact event_type (e.g. 'task_end' / 'stuck'). Logs are unaffected. |
| `head_limit` | `integer` | — | `50` | Max matching lines to return per source. |
| `session_id` | `string` | — | — | Override session resolution. |

---

## `read_memory`

**Module:** [`modulated_system/tools/meta/read_memory.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/meta/read_memory.py#L9)  ·  **Python function:** `read_memory`  ·  **Description source:** decorator `description=`

Read one file from the persistent-memory workspace (~/.claude_aeda/memory/<workspace>/learnings/<filename>.md). Call this when MEMORY.md cites a learning you want to pull into the current Claude turn's context.

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `workspace` | `string` | ✓ | — | Workspace partition (e.g. 'lego_room'). |
| `filename` | `string` | ✓ | — | Learning filename without extension (e.g. 'lab-network'). |

---

## `send_executor_command`

**Module:** [`modulated_system/tools/meta/send_executor_command.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/meta/send_executor_command.py#L34)  ·  **Python function:** `send_executor_command`  ·  **Description source:** decorator `description=`

"Append a command to the Executor's control.json channel. " + _VALID_KINDS_DOC + ' The Executor reads commands at task-loop top, monitor ticks, and pre-retry points. Returns the generated command_id.'

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `kind` | `string` | ✓ | — | One of interrupt / pause / resume / set_task_index / inject_note / clear_note. |
| `payload` | `object` | — | — | Command-specific payload. See descriptions above. Defaults to {}. |
| `reason` | `string` | — | — | Free-text reason logged with the command for forensic replay. |

---

## `update_memory_index`

**Module:** [`modulated_system/tools/meta/update_memory_index.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/meta/update_memory_index.py#L9)  ·  **Python function:** `update_memory_index`  ·  **Description source:** decorator `description=`

Append a single-line markdown entry to the workspace's MEMORY.md index. Convention: '- `[name](learnings/name.md)` — <one-line summary>'. The index is loaded on every Supervisor startup so an indexed learning is always discoverable.

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `workspace` | `string` | ✓ | — |  |
| `entry` | `string` | ✓ | — | One-line markdown — typically a bullet with a link to the learnings file. |

---

## `update_plan`

**Module:** [`modulated_system/tools/meta/update_plan.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/meta/update_plan.py#L17)  ·  **Python function:** `update_plan`  ·  **Description source:** decorator `description=`

Replace the active collection plan for a session. The plan worker picks up the new plan between tasks. The previous plan is archived under plans/history/. Returns the path to the new active plan + the archived predecessor (if any).

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `plan` | `object` | ✓ | — | The full plan dict matching plan_schema (plan_id, tasks, optional global_stop_conditions). Replaces the existing active.json verbatim. |
| `session_id` | `string` | — | — | Override session resolution. Defaults to ctx.session_dir / AEDA_SESSION_ID / 'default'. |

---


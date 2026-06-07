# Room scan + collect

A 146-line Aeda script that drives the robot around a room, finds every
table via vision, parks at each, runs a first-pass collection cycle on
it, and returns home. The script is the production loop the
data-collection sessions use.

The script lives at
[`scripts/aeda_room_scan_and_collect.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/scripts/aeda_room_scan_and_collect.py).

## What it demonstrates

- High-level tool composition: `scan_room_for_tables` → `navigate_to` →
  `recover_arm`/`reset_arm_to_rest` → per-table collection → safe exit.
- The **escape-hatch read** of robot pose via
  `aeda.platform.robot.locomotion.get_pose()` (when there's no `@tool` for
  what you want and the `Pose` is fine to grab directly).
- The **hardware-safety idiom**: a `try`/`except`/`finally` block per
  table that *always* unlocks the base, recovers the arm, and backs up,
  even on a partial failure mid-collection.
- Structured event logging: every phase emits a `kind="json"` event the
  transcript renders as a labelled JSON tree.

## Flow

```
record home pose
    │
    ▼
scan_room_for_tables  ──►  list of tables (anchor_xyz, confidence)
    │
    ▼
for each table:
    navigate_to(anchor, offset_m=SURVEY_OFFSET_M)
    recover_arm → reset_arm_to_rest
    collect_one_table(...)         (shared helper in _collection_lib.py)
    ─────── safe exit (finally) ───────
    unlock_base
    recover_arm → reset_arm_to_rest
    move_relative(dx_m=-0.3)         ← back away from the table
    │
    ▼
navigate_to(HOME_X, HOME_Y, HOME_YAW)
    │
    ▼
emit session_complete summary
```

## Annotated walkthrough

### 1. Tunable constants up front

```python
ROTATE_STEP_DEG               = 30       # scan_room rotates in 30° hops
N_ORBITS_PER_TABLE            = 4
N_BEZIERS_PER_TABLE           = 2
CONFIRM_OFFSET_M              = 2.0
SURVEY_OFFSET_M               = 2.0      # parks 2 m from the table anchor;
                                          # 1.2 m drove the base inside the
                                          # actual table edge when Gemini's
                                          # anchor landed at the far edge.
PARKED_OFFSET_M               = 0.75
SAFE_EXIT_BACKUP_M            = 0.3
MIN_TABLE_CONFIDENCE          = 0.55
SETTLE_S                      = 1.0
CLUSTER_DIST_M                = 0.6
```

Putting every magic number at the top of the file is the convention all
the example scripts follow — operators can scan the header to retune one
session without diving into the loop.

### 2. Record home pose via the escape hatch

```python
_home = aeda.platform.robot.locomotion.get_pose()
HOME_X, HOME_Y, HOME_YAW = _home.to_xy_theta()
```

No `@tool` exposes "give me the current base pose," so the script reaches
through `aeda.platform.robot` directly. `Pose.to_xy_theta()` returns the
2D triple the rest of the script reasons in.

### 3. Phase 1 — scan the whole room

```python
scan = aeda.tools.scan_room_for_tables(
    rotate_step_deg=ROTATE_STEP_DEG,
    settle_s=SETTLE_S,
    cluster_dist_m=CLUSTER_DIST_M,
    min_confidence=MIN_TABLE_CONFIDENCE,
    confirm_offset_m=CONFIRM_OFFSET_M,
)
```

One tool call drives the whole 360° sweep, runs Gemini detection at each
heading, clusters the hits across rotations into single tables, and
confirms each cluster by a quick approach. The result is a list of
`(anchor_xyz, best_confidence, ...)` dicts the script can iterate over.

### 4. Phase 2 — per-table collection loop with safe-exit guarantee

```python
for i, table in enumerate(scan["tables"]):
    name = f"table_{i:02d}"
    anchor = table["anchor_xyz"]
    try:
        # (a) Approach
        nav = aeda.tools.navigate_to(
            x=anchor[0], y=anchor[1],
            offset_m=SURVEY_OFFSET_M, clamp_min_offset_m=0.0)
        if not nav.get("success"):
            ...continue

        # (b) Recover + reset arm
        aeda.tools.recover_arm()
        aeda.tools.reset_arm_to_rest()

        # (c) Full first-pass collection cycle
        out = _collection_lib.collect_one_table(
            name=name, table=None,
            n_orbits=N_ORBITS_PER_TABLE,
            n_beziers=N_BEZIERS_PER_TABLE,
        )
        results.append({"name": name, "status": "ok", "outcome": out})

    except Exception as e:
        results.append({"name": name, "status": "failed", ...})

    finally:
        # SAFE TABLE EXIT — always runs.
        aeda.tools.unlock_base()
        aeda.tools.recover_arm()
        aeda.tools.reset_arm_to_rest()
        aeda.tools.move_relative(dx_m=-SAFE_EXIT_BACKUP_M, ...)
```

Two things to notice:

1. **`finally` runs on every path** — successful collection, mid-cycle
   exception, or even an operator Ctrl-C (`AedaInterrupt` propagates
   through `finally` like any `BaseException`). So the base always
   unlocks, the arm always resets, and the robot always backs up before
   moving to the next table.
2. **Each safe-exit step is wrapped in its own `try/except: pass`**
   (collapsed above for clarity — see the source). A failed unlock
   doesn't prevent the arm reset; a failed reset doesn't prevent the
   back-up. The script optimizes for *making it to the next table* even
   when one cleanup step throws.

### 5. Return home + summary

```python
home_nav = aeda.tools.navigate_to(
    x=HOME_X, y=HOME_Y,
    yaw_deg=math.degrees(HOME_YAW),
    offset_m=0.0, clamp_min_offset_m=0.0)

n_ok = sum(1 for r in results if r["status"] == "ok")
n_skipped = sum(1 for r in results if r["status"] == "skipped")
n_failed = sum(1 for r in results if r["status"] == "failed")
aeda.log({"step": "session_complete",
          "n_tables_attempted": len(results),
          "n_completed": n_ok,
          "n_skipped": n_skipped,
          "n_failed": n_failed,
          "results": results}, kind="json")
```

The final `session_complete` event is the single artifact the supervisor
(and the analytics tooling) keys on to score the run.

## Running it

```bash
AEDA_SESSION_ID=room_scan_1 \
python scripts/run_aeda_cli.py scripts/aeda_room_scan_and_collect.py \
    --launch sim,nav2_slam,iphone,octomap,arm_zerorpc \
    --stop-launchers-on-exit
```

Or paste the file's contents into the runtime UI's Script box and click
*Run*. Per-event progress lands in the WebSocket transcript;
per-episode artefacts land in `runtime/sessions/room_scan_1/episodes/`.

## Source

- [`scripts/aeda_room_scan_and_collect.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/scripts/aeda_room_scan_and_collect.py) — the script itself.
- [`scripts/_collection_lib.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/scripts/_collection_lib.py) — `collect_one_table` and the shared per-table helpers.
- [`tools/perception/scan_room_for_tables.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/perception/scan_room_for_tables.py) — the room-scan tool itself.

## Next

- [Scan → cluster → capture →](scan-cluster-capture.md) — the full end-to-end pipeline (joint-0 sweep + clustering + per-cluster capture).

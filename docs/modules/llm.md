# `modulated_system/llm/`

The Claude + Gemini integration layer. Three agents (supervisor, worker,
data-analyzer) plus the shared call/CoT machinery they all sit on.

## Agents

| Subpackage | Role | Model |
| --- | --- | --- |
| **`supervisor/`** | Plans tasks; gates tool calls; audits provenance. Reads `runtime/sessions/<id>/` like Claude Code reads a project. Long-lived REPL with prompt caching + 700k-token auto-compaction + watch-thread event coalescing. | Claude Opus |
| **`worker/`** | Writes Aeda scripts and calls `run_script(...)`. Stable REPL — primer + auto-context split so caching never invalidates. | Claude Opus |
| **`data_analyzer/`** | Read-only subagent the supervisor invokes at session start to characterize datasets via `inspect_dataset` / `analyze_*_distribution` tools. | Claude Opus (smaller context) |
| **`executor/`** | The Gemini client. `query_text` / `query_image` / `detect_robotics_er` / `estimate_3d_bbox_robotics_er`. Used inside `@tool` implementations (`detect_target`, `check_target_in_frame`, …) AND via `aeda.llm.*` from scripts. | Gemini Robotics-ER 1.6 |

## Shared machinery

| Module | What it is |
| --- | --- |
| **`_call_claude.py`** | The single canonical entry point to `client.messages.create`. Every Claude call in the project goes through this — adds prompt caching (`cache_control` on system + tools + last 2 messages), CoT trace, retry-on-overload, structured token logging. |
| **`_cot_writer.py`** | Writes per-call chain-of-thought traces into `runtime/sessions/<id>/cot/<agent>/<timestamp>_<mode>.md`. The supervisor, worker, data_analyzer, and Gemini calls all log here. |
| **`_repl_prompt.py`** | The Claude-Code-style REPL primer the supervisor and worker share. Stable across turns so the cache hits. |
| **`persistent_memory.py`** | Cross-session memory store (`memory/MEMORY.md` + per-fact .md files) read by the supervisor at start. |

## How a session reads top-down

```
operator prompt
    │
    ▼
supervisor/repl.py  ────►  data_analyzer/subagent.py
    │                              │
    │                              ▼
    │                      cot/data_analyzer/*.md   + supervisor/data_analyzer/*.json
    │
    ▼
plans/initial.json    ←   supervisor synthesises from data-analyzer gap report
    │
    ▼
plans/active.json     ←   live plan supervisor + worker share
    │
    ▼
worker/repl.py        ────►  aeda runtime (run_script)
                                       │
                                       ▼
                              tool dispatch, llm calls, etc.
                                       │
                                       ▼
                              cot/{worker,gemini}/*.md
                              worker/chat.jsonl
                              worker/scripts/<job_id>.log.jsonl
```

The supervisor monitors `cot/_summary.json` + new events; the worker
writes them. The operator listens to both via the runtime UI.

## Prompt caching (why supervisor cost dropped 8–11×)

`_call_claude` puts `cache_control` markers on the **system block, the
tools block, and the last 2 messages** of every request. Effective when:

- the system prompt is stable across turns (the REPL primer is — auto-
  context goes into user messages, not the system block);
- the supervisor/worker run as one long conversation rather than fresh
  per-turn API calls.

Both conditions hold for the current REPL architecture, which is why
the session-stats report shows ~93 % cache-read on the cached runs vs
0 % on the older uncached ones.

## Source

[`modulated_system/llm/`](https://github.com/Pengyu-Mo/tidyros_iphone/tree/main/modulated_system/llm)

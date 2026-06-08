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

### Why this needed our code in the first place

Caching looks the same to a user — *"identical prefix gets discounted on
the next call"* — but the three big providers differ sharply on whether
you have to ask for it. Anthropic is the only one of the three where you
have to opt in:

| Capability | **Anthropic Claude** | **OpenAI** (`gpt-4o`+) | **Google Gemini** (2.5+) |
| --- | --- | --- | --- |
| **Default behaviour** | **Opt-in.** No `cache_control` ⇒ no caching, no matter how long the prefix. | **Automatic.** No code changes required. | **Automatic** *implicit* caching, **plus** an optional explicit `CachedContent` API. |
| **Where to mark** | `cache_control: {"type": "ephemeral"}` on up to **4** content blocks per request. | Nothing — automatic prefix matching. Optional `prompt_cache_key` to influence routing. | Nothing for implicit. Explicit caches are first-class API objects. |
| **Minimum cacheable prefix** | **1,024 tokens** (Opus/Sonnet 4.x), **4,096 tokens** (Haiku 4.5). | **1,024 tokens.** | **1,024 tokens** (Flash), **4,096 tokens** (Pro). |
| **Default TTL** | **5 minutes.** Optional 1-hour tier at a higher write cost. | **5–10 minutes** of inactivity, up to ~1 hour total. Extended-retention tier reaches 24 h. | Implicit cache: not specified (best-effort). Explicit cache: caller-set, billed per token-hour of storage. |
| **Cache *write* cost** | **1.25× input** (5 min tier) or **2× input** (1 hour tier). | **No extra fee.** | Implicit: no extra fee. Explicit: token-hour storage charge. |
| **Cache *read* discount** | **90 %** off input rate (cache_read = 0.1× input). | OpenAI docs cite *"up to 90 %"* input-cost reduction. (Actual per-model rate varies — `gpt-4o`-family discounted ~50 %, newer `o`-series higher.) | Discount applied automatically on a hit, but **no cost-saving guarantee** on implicit hits. |
| **Match semantics** | **Exact** prefix hash up to and including the marked block — one character invalidates. | **Exact** prefix match. | **Exact** prefix match; prefix-position matters (put long common content **first**). |
| **No-hit failure mode** | Silent — under-threshold writes are processed *without* caching, no error. | Silent — under-threshold prompts simply aren't eligible. | Silent — implicit hits aren't guaranteed even when eligible. |

The practical implication: **on OpenAI and Gemini you'd have got a
substantial cost cut for free** the moment the supervisor crossed 1,024
tokens of stable prefix. On Anthropic, an un-decorated long conversation
re-bills the full prefix at full input rate every turn — which is exactly
what produced the historical incident the [session-stats
report](https://github.com/saimlau/aeda_docs/blob/main/docs/modules/llm.md)
documents: 317 M input tokens / **$1,600** burned by one un-cached
supervisor PRE-slice before `_call_claude` learned to mark its
breakpoints.

### Why the manual model isn't just a tax — it's also more powerful

The flip side of having to ask: once you do, Anthropic gives you finer
levers than the other two.

- **Four breakpoints lets you cache stable layers separately from a
  growing message tail.** `_call_claude` uses three of them — system,
  tools, and the last 2 messages — so the tools block survives a system-
  prompt edit, and a growing turn-tail still hits cache up to the most
  recent marker.
- **A 1-hour TTL tier exists** at 2× write cost (vs 1.25× for 5 min) —
  worth it for a session that idles between operator interventions but
  resumes on the same prefix.
- **You see the hit ratio directly.** Every `messages.create` response
  carries `cache_creation_input_tokens` and `cache_read_input_tokens` —
  the catalog of `cot/_summary.json`'s per-call `cache_creation` /
  `cache_read` fields. OpenAI surfaces a cached-token count too; Gemini
  exposes `cached_content_token_count` (which is **0 on every one of our
  Robotics-ER 1.6 calls** — see the
  [cost-incident memory](https://github.com/Pengyu-Mo/tidyros_iphone/)
  for why image-dominated perception calls structurally can't hit
  Gemini's implicit cache).

So the right summary is: **Anthropic trades convenience for control.**
That trade only stings when an application doesn't know to opt in — and
the function of `_call_claude` is precisely to make sure every call in
the modulated stack opts in correctly, by default, in one place.

## Source

[`modulated_system/llm/`](https://github.com/Pengyu-Mo/tidyros_iphone/tree/main/modulated_system/llm)

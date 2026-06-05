# Running a script

Three ways to execute an Aeda script.

## 1. From the worker REPL (interactive)

```bash
conda activate nav2_robostack
cd tidyros_iphone
python -m modulated_system.llm.worker
```

Inside the REPL, the worker (Claude Opus) writes scripts and invokes
`run_script` on its own. You guide it with natural-language prompts:

```
> Look for the red mug on the table and orbit around it.
```

The worker responds with a script, runs it via `run_script`, and reports
the outcome. Operator prompts and tool calls all land in
`worker/chat.jsonl`.

## 2. As a direct tool call (programmatic)

```python
from aeda import run_script

with open("my_script.py") as f:
    result = run_script(f.read())

assert result.success, result.error
```

This is the path used by Aeda scripts that orchestrate other Aeda scripts
(rare, but supported).

## 3. From the runtime UI (browser)

The modulated_system ships a FastAPI + browser UI at
`modulated_system/runtime/ui/` that exposes a Claude terminal in the
browser. You type into the browser; the same `run_script` path runs
underneath.

```bash
python -m modulated_system.runtime.ui.server
# open http://localhost:8000
```

See
[`modulated_system/runtime/ui/`](https://github.com/Pengyu-Mo/tidyros_iphone/tree/main/modulated_system/runtime/ui)
for the full UI architecture.

## Where output lands

Regardless of which entry point you use, every script produces:

- A structured log at
  `runtime/sessions/<id>/worker/scripts/<script_id>.log.jsonl`
- A `ScriptResult` entry in `worker/chat.jsonl`
- Per-tool-call traces in `cot/worker/`
- (If the script started recording) an episode at
  `episodes/<episode_id>/`

The session directory is the single source of truth for everything that
happened during a run.

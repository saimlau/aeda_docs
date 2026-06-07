# Hello, platform

The smallest meaningful Aeda script — 8 lines, no dependencies beyond the
runtime. Use it as a sanity check on a fresh install or as a starter file
in the inline editor.

```python title="example_hello.py" linenums="1"
# Example aeda script — prints a friendly greeting and lists the
# tools available on the current platform.
#
# Drop-in for the inline editor or saveable as a starter file.

aeda.log("hello from", aeda.platform.name)
tools = aeda.tools.list()
aeda.log({"n_tools": len(tools), "first_8": tools[:8]}, kind="json")
```

## What's happening

- **`aeda.log("hello from", aeda.platform.name)`** — variadic
  `aeda.log(*values)` joins its args with spaces. The transcript shows
  `"hello from tidybot_plus_fr3_iphone"` (or whatever your platform's
  `Robot.name` is).
- **`aeda.tools.list()`** — sorted list of every tool name registered on
  the current platform, filtered by `Robot.capabilities()`. Tools the
  platform doesn't expose aren't listed.
- **`aeda.log({...}, kind="json")`** — second log emits a structured
  payload that the frontend renders as a collapsible JSON tree.

## Expected transcript

```jsonc
{"type": "log", "kind": "info",
 "values": ["hello from", "tidybot_plus_fr3_iphone"]}
{"type": "log", "kind": "json",
 "values": [{"n_tools": 47,
             "first_8": ["check_target_in_frame",
                         "compute_parking_locations",
                         "detect_target", "evaluate_episode",
                         "execute_trajectory",
                         "find_feasible_params",
                         "generate_view_trajectory",
                         "list_objects_in_view"]}]}
{"type": "done", "duration_s": 0.02, ...}
```

(Tool count + names will vary by platform build.)

## Source

[`scripts/example_hello.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/scripts/example_hello.py)

## Next

- [LLM judgement loop →](judgement-loop.md) — branch on a Gemini answer about the live frame.

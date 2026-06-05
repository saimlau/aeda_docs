# Writing a tool

How to add a new `@tool` to the `modulated_system` catalog so that scripts
can call it as `aeda.tools.<name>(...)`.

## Minimum viable tool

```python
# modulated_system/tools/example/say_hello.py
from modulated_system.tools.base import tool, ToolContext, ToolResult


@tool(name="say_hello", category="example")
def say_hello(ctx: ToolContext, who: str = "world") -> ToolResult:
    """Greet someone. Returns a friendly message."""
    msg = f"Hello, {who}!"
    return ToolResult(success=True, message=msg, data={"greeting": msg})
```

Register the module via the auto-discovery glob (see
`modulated_system/tools/__init__.py`), restart the worker, and the tool is
callable:

```python
aeda.tools.say_hello(who="Saimai")
```

## Contract

Every `@tool` must:

1. **Take a `ToolContext` as the first arg.** It carries the session bridge,
   sensor fuser, planner clients, and config.
2. **Return a `ToolResult`** with at least `success: bool` + `message: str`.
   Add a `data` dict for typed payload.
3. **Not raise** on expected failure modes — return `success=False` plus a
   remediation string in `message`.
4. **Be JSON-serializable in / out** — kwargs and `data` must round-trip
   through the supervisor's audit log.
5. **Surface cancellation** by calling `ctx.cancel.check()` periodically in
   long-running loops (matches `aeda.cancel.check()` on the script side).

## Patterns to follow

- **One tool per file** in `modulated_system/tools/<category>/<name>.py`.
- **Validate args early** — return a `success=False` `ToolResult` with a
  remediation hint rather than letting bad input crash the tool.
- **Log structured events** via `ctx.session.append_event(kind="...", ...)`
  for anything the supervisor should see.

## Testing

Each tool gets a unit test under `modulated_system/tests/tools/`. The
pattern:

```python
def test_say_hello():
    ctx = make_mock_context()
    res = say_hello(ctx, who="Saimai")
    assert res.success and "Saimai" in res.message
```

Use the mock context in `tests/conftest.py` — it stubs out the bridge,
planner, and sensor fuser so tools can be tested without ROS or the real
robot.

## Reference

- Base classes:
  [`modulated_system/tools/base.py`](https://github.com/Pengyu-Mo/tidyros_iphone/tree/main/modulated_system/tools)
- Existing tools (read for patterns):
  [`modulated_system/tools/`](https://github.com/Pengyu-Mo/tidyros_iphone/tree/main/modulated_system/tools)

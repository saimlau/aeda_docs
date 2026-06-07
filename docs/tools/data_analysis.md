# Tools — `data_analysis` (1)

Sandbox the data-analyzer subagent uses for ad-hoc Python execution against in-memory dataset stats.

## In this category

- [`python_exec`](#python_exec) — Write + run a one-off Python script for ad-hoc data inspection / format conversion / custom binning. Stdlib + the conda env are accessible. Returns {stdout, stderr, exit_code, script_path}.

---

## `python_exec`

**Module:** [`modulated_system/tools/data_analysis/python_exec.py`](https://github.com/Pengyu-Mo/tidyros_iphone/blob/main/modulated_system/tools/data_analysis/python_exec.py#L26)  ·  **Python function:** `python_exec`  ·  **Description source:** decorator `description=`

Write + run a one-off Python script for ad-hoc data inspection / format conversion / custom binning. Stdlib + the conda env are accessible. Returns {stdout, stderr, exit_code, script_path}.

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `script` | `string` | ✓ | — | Full Python source to execute. |
| `timeout_s` | `number` | — | `120.0` | Hard wall-clock cap on the subprocess. |
| `allow_stdout_lines` | `integer` | — | `200` | Max lines from stdout (and stderr) preserved; longer is head/tail-elided. |

---


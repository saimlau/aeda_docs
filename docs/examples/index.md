# Examples

A graded tour of real Aeda scripts in
[`modulated_system/scripts/`](https://github.com/Pengyu-Mo/tidyros_iphone/tree/main/modulated_system/scripts).
Read top-to-bottom for the natural complexity gradient.

| Example | Lines | What you'll learn |
| --- | --- | --- |
| **[Hello, platform](hello.md)** | 8 | `aeda.platform.name`, `aeda.tools.list()`, `aeda.log(kind="json")`. The minimum viable Aeda script. |
| **[LLM judgement loop](judgement-loop.md)** | 15 | Branch on a Gemini answer about the live camera frame: `aeda.frame.rgb` + `aeda.llm.judgement(...)`. |
| **[Room scan + collect](room-scan-and-collect.md)** | 146 | Multi-table room sweep: scan → per-table approach + collect → safe exit → return home. Real production loop with `try/finally` hardware-safety guarantees. |
| **[Scan → cluster → capture](scan-cluster-capture.md)** | 389 | The full end-to-end data-collection pipeline: joint-0 sweep with detection at each step → spatial clustering → per-cluster approach + orbit + capture. |

## How to run any of them

=== "From the runtime UI"

    Paste the script into the **Script** box and click *Run*.

=== "From the CLI"

    ```bash
    AEDA_SESSION_ID=my_run \
    python scripts/run_aeda_cli.py scripts/aeda_room_scan_and_collect.py \
        --launch sim,nav2_slam,iphone,octomap,arm_zerorpc \
        --stop-launchers-on-exit
    ```

=== "From the worker REPL"

    ```bash
    python -m modulated_system.llm.worker
    > /run scripts/aeda_room_scan_and_collect.py
    ```

All three paths use the same `run_script` underneath — events flow into the
same session directory and the same WebSocket transcript.

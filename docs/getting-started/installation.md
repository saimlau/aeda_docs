# Installation

Aeda is a sub-package of
[`tidyros_iphone`](https://github.com/Pengyu-Mo/tidyros_iphone). There is
currently **no PyPI package** — you install Aeda by cloning the parent repo
and running it from the project's conda environment.

## Prerequisites

- Ubuntu 24.04 (Linux 6.x). macOS / Windows are not supported.
- [Miniconda](https://docs.conda.io/) (the project uses a robostack-based
  env).
- A working ROS 2 install (the project targets Humble / Jazzy) — only needed
  for the real-robot path; sim-only works without it.

## 1. Clone the repo

```bash
git clone git@github.com:Pengyu-Mo/tidyros_iphone.git
cd tidyros_iphone
```

## 2. Create the conda env

The project uses a `nav2_robostack` conda environment (Python 3.11, ROS 2 via
robostack, plus a handful of robot-specific deps).

```bash
conda env create -f env/nav2_robostack.yaml
conda activate nav2_robostack
```

If you only want the Aeda SDK without ROS — for example, to write tools
that don't talk to hardware — a slim env works:

```bash
conda create -n aeda_dev python=3.11
conda activate aeda_dev
pip install -e modulated_system
```

## 3. Verify

```bash
python -c "import aeda; print('aeda OK')"
```

You should see `aeda OK` and no `ImportError`. If the import fails, ensure
`modulated_system/` is on `PYTHONPATH` — the editable install above handles
this automatically.

## 4. (Optional) Real-robot extras

For the real-robot path you'll additionally need:

- `panda_py` 0.8.1 on the arm NUC.
- The Aeda zerorpc bridge running on the arm NUC
  (`arm_zerorpc_bridge.py`).
- The TidyBot++ base controller running on the base NUC.

See the [tidyros_iphone README](https://github.com/Pengyu-Mo/tidyros_iphone)
for the full real-robot bring-up checklist.

## Next

- **[Quickstart →](quickstart.md)** Write and run your first Aeda script.

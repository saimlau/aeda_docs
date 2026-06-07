# aeda_docs

Documentation website for **Aeda** — the robot-scripting SDK that powers the
`modulated_system` supervisor/worker loop in
[tidyros_iphone](https://github.com/Pengyu-Mo/tidyros_iphone).

Built with [MkDocs Material](https://squidfunk.github.io/mkdocs-material/) and
deployed to GitHub Pages.

## Build + serve locally

```bash
# one-time
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# live-reload server at http://localhost:8000
mkdocs serve

# build static site into ./site/
mkdocs build
```

## Layout

- `mkdocs.yml` — site config (theme, nav, plugins).
- `docs/` — markdown source for every page.
- `.github/workflows/deploy-docs.yml` — builds and publishes to GitHub Pages
  on push to `main`.

## Contributing

Open a PR against `main`. The deploy workflow rebuilds and publishes on merge.

## License

Apache-2.0 — see [`LICENSE`](LICENSE).

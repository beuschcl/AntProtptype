# ADR 006 – `src/` Layout

**Status**: Accepted  
**Date**: 2026-07-25

---

## Context

Python projects can be structured in two common ways:

1. **Flat layout** – `ant_colony/` at the project root next to `tests/`.
2. **`src/` layout** – `src/ant_colony/` with tests outside `src/`.

## Decision

Use the **`src/` layout**: all importable package code lives under
`src/ant_colony/`.

## Rationale

* Prevents accidental imports of the non-installed package when running
  tests from the project root.  With a flat layout, `import ant_colony`
  can resolve to the source directory even without installation, masking
  import errors that would occur after packaging.
* Encourages correct installation (`pip install -e .`) as the normal
  development workflow.
* Recommended by the Python Packaging Authority (PyPA) for libraries and
  applications.
* `pyproject.toml` with `[tool.setuptools.packages.find] where = ["src"]`
  handles discovery automatically.

## Consequences

* Tests import `ant_colony` after `pip install -e ".[dev]"` (or equivalent).
* `src/` must be marked as a Sources Root in IDEs (e.g. PyCharm) to
  resolve imports.
* CI always runs `pip install -e ".[dev]"` before executing tests.
* The `scenarios/` directory stays at the project root (not under `src/`)
  because it is not importable Python code.

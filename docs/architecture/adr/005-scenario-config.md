# ADR 005 – TOML Scenario Files (stdlib `tomllib`)

**Status**: Accepted  
**Date**: 2026-07-25

---

## Context

World construction must be driven by a human-readable configuration file.
Format options:

1. **JSON** – machine-readable but verbose; no comments.
2. **YAML** – human-friendly but requires a third-party library (`PyYAML`)
   and has known footguns (Norway problem, implicit typing).
3. **TOML** – designed for configuration; supports comments; stdlib since
   Python 3.11 via `tomllib`.
4. **INI / `.cfg`** – too limited for nested structures.
5. **Python code** – flexible but a security and maintenance risk.

## Decision

Use **TOML** parsed with the stdlib `tomllib` module (Python ≥ 3.11).

## Rationale

* `tomllib` is part of the Python stdlib since 3.11 – no extra
  dependency.
* TOML is designed for configuration files: unambiguous typing, inline
  comments, array of tables for lists of objects.
* Human-readable and writable without a code editor.
* Strict: invalid TOML raises a clear parse error.
* The project already requires Python ≥ 3.11 for other modern features.

## Consequences

* `ScenarioLoader.load_file()` opens the file in binary mode and passes
  it to `tomllib.loads(data.decode())`.
* `ScenarioLoader.load_bytes()` is provided for in-memory testing without
  touching the filesystem.
* The scenario schema is validated by `ScenarioLoader._parse_config()`;
  structural errors raise `InvalidScenarioError`.
* Scenario files live in `scenarios/` at the project root.
* Python 3.10 and earlier are not supported.

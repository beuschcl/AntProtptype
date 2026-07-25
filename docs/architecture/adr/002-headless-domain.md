# ADR 002 – Headless Domain (no presentation coupling)

**Status**: Accepted  
**Date**: 2026-07-25

---

## Context

A simulation can be structured as:

1. **Tightly coupled** – domain logic mixed with rendering calls.
2. **Loosely coupled (headless domain)** – domain is pure Python;
   rendering is an optional observer.

## Decision

Keep `ant_colony.domain` and `ant_colony.simulation` completely free of
any presentation or infrastructure imports.

## Rationale

* The domain can be unit-tested without a display, pygame, or any OS
  dependency.
* CI runs headlessly without a windowing system.
* Multiple renderers (terminal, PyGame, web) can observe the same domain
  via `WorldSnapshot` without modifying domain code.
* Future headless replays, benchmarks, and ML training all benefit.
* Aligns with the *Ports and Adapters* architecture: the domain is the
  hexagon; renderers and loaders are adapters.

## Consequences

* `WorldSnapshot` is the *read model* for renderers – they receive
  snapshots, not live world references.
* Any rendering code must live in a separate package (e.g.
  `ant_colony.renderer`) that is not imported by the domain.
* mypy strict mode is configured to detect accidental imports in CI.

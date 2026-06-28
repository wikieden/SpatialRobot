# Changelog

All notable changes to bodylink (the executor-adapter layer for Chronotope) are
documented here. Format follows [Keep a Changelog](https://keepachangelog.com/);
versions follow SemVer (pre-1.0, the API may change between minor releases).

## [Unreleased]

### Added

- **Package created (P0, D5)** — the 4th Chronotope workspace member; ships the
  reference fill of the brain's `ExecutorAdapter` seam.
- **`MockBody`** — a no-hardware, no-network reference `ExecutorAdapter`: accepts
  `SubTask`s, streams `StatusUpdate`s (RUNNING → terminal), echoes node ids (B9),
  and reports success or a scripted typed failure with a `RecoveryHint` (B3).
  Raises `UnsupportedVerbError` for a verb outside the manifest (a planner bug).
- **`g1d_manifest()`** — the B10 reference `CapabilityManifest` (G1-D wheeled
  humanoid, 32 DOF, 2-D base, the declared verb set).
- **Multi-model adaptation framework (D3)** — supporting a new robot is now adding
  a manifest, not code:
  - **`manifest` catalog** — `load_manifest(name|path)` resolves builtin profiles
    (`g1d` wheeled humanoid, `h1` bipedal/legged humanoid — `list_profiles()`)
    from stdlib dicts (no dependency), or an external vendor `*.yaml`
    (`manifest_from_dict` + lazy PyYAML behind the `manifests` extra). `h1`
    declares a bipedal-only `climb_stair` verb a wheeled base lacks — the D3 gate
    handles the difference with no brain change. `manifests/_TEMPLATE.yaml` +
    `manifests/fourier_gr1.yaml` are copy-me authoring templates.
  - **`BaseExecutorAdapter` SDK** — a device package subclasses it and implements
    only `_execute()`; the base handles the verb gate (D3), the RUNNING→terminal
    stream, and a guaranteed node-id echo (B9). `MockBody` is now a subclass.
  - **`check_executor_adapter()` conformance kit** — a portable contract check any
    body runs to prove it honors the seam (manifest well-formed, dispatch reaches
    terminal, node ids echoed B9, undeclared verb refused D3, typed error B3).
    The two reference bodies (g1d, h1) pass it.

### Changed

- **`MockBody` refactored onto `BaseExecutorAdapter`** — identical behavior;
  `UnsupportedVerbError` now lives in `adapter.py` (re-exported, no API change).
- **`g1d_manifest()` adds the `operate_appliance` verb** (params `target`,
  `program`; `appliance_types` washer/stove/microwave/dishwasher) so the brain's
  Episteme skill cards (P2 — laundry, cooking) can drive appliances against
  `MockBody`. `dispatch()` is verb-agnostic, so no executor change was needed.

- **`g1d_manifest()` adds the `operate_appliance` verb** (params `target`,
  `program`; `appliance_types` washer/stove/microwave/dishwasher) so the brain's
  Episteme skill cards (P2 — laundry, cooking) can drive appliances against
  `MockBody`. `dispatch()` is verb-agnostic, so no executor change was needed.

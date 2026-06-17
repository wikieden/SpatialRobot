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

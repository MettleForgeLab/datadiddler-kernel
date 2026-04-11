# DataDiddler Kernel

**Status:** Active  
**Version:** v0.1.0  
**Scope:** Deterministic orchestration, schema enforcement, and run truth emission for DataDiddler  
**Layer Position:** Core execution boundary (kernel) — upstream of lenses, downstream of input corpus

---

## Purpose

The DataDiddler Kernel defines the minimal, deterministic execution surface of the DataDiddler system.

It is responsible for:

- orchestrating stage execution
- enforcing schema boundaries
- producing run truth artifacts
- coordinating external tools via explicit mappings

This repository represents the **publishable kernel boundary** — the portion of the system intended to remain stable and composable over time.

---

## Execution Flow

The kernel executes a fixed, deterministic stage sequence:

```
rake → separator → tagger → packager

```

Each stage:

- consumes well-defined input files
- produces well-defined output files
- is executed via external tool mappings

The kernel itself does not implement stage logic — it orchestrates it.

---

## Inputs

The kernel operates on:

- an input corpus directory (`--in-dir`)
- tool mapping definitions (`--tools`)
- schema definitions (`--schema`)
- stage configuration files:
  - `--separator-config`
  - `--tagger-config`

---

## Outputs

Each run produces structured, deterministic artifacts:

- `run_manifest.json` — full run trace (inputs, tools, configs, hashes)
- `stage_status.ndjson` — stage-by-stage execution results
- `compiled/GroundedDatasetBlock.vN.json` — schema-validated output

---

## Guarantees

The kernel guarantees:

- deterministic orchestration given the same inputs and tool paths
- schema-enforced output validation
- complete run trace via manifest and stage status
- strict separation between orchestration and stage behavior

---

## Non-Guarantees

The kernel does **not** provide:

- semantic correctness of tagging or extraction
- domain-specific logic (e.g., biology)
- rendering, indexing, or presentation layers
- evidence, diffing, or downstream policy behavior

These belong to downstream layers (lenses and consumers), not the kernel.

---

## Contract Surface

The kernel enforces structure through:

- `material_lens_system.schema.frozen.json`

This schema defines the shape of valid output and acts as the primary contract boundary.

---

## Compatibility Note

An empty `threads.ndjson` file is written during packaging.

This is a **compatibility placeholder**, not evidence of a weaver stage.

The weaver is not part of the kernel.

---

## What This Repo Is Not

This repository is not:

- a lens implementation
- a domain-specific processor
- a rendering or indexing system
- an experimental workspace
- an archive of baseline runs

It is the **minimal, forward-facing kernel surface only**.

---

## Notes

This kernel is derived from a verified baseline that:

- runs end-to-end successfully
- produces schema-valid outputs
- excludes non-essential stages (e.g., weaver, renderer, indexer)
- uses external tools for all stage behavior

Future repositories (lens template, reference lenses, domain lenses) will build on this kernel.

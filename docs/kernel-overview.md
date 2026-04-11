\# Kernel Overview



\## Summary



The DataDiddler Kernel is a deterministic orchestration layer that executes a fixed pipeline over structured data.



It does not implement domain logic.  

It coordinates external tools that perform stage-specific work.



\---



\## Execution Spine



The kernel executes the following sequence:



```

rake → separator → tagger → packager



```





Each stage:



\- reads defined input files

\- produces defined output files

\- is executed via a mapped external tool



The kernel enforces ordering, not behavior.



\---



\## Stage Breakdown



\### 1. Rake



\*\*Purpose:\*\* Ingest raw corpus into structured intermediate files



\*\*Outputs:\*\*



\- `documents.ndjson`

\- `text\_artifacts.ndjson`



\---



\### 2. Separator



\*\*Purpose:\*\* Partition and triage input data



\*\*Inputs:\*\*



\- `documents.ndjson`

\- `text\_artifacts.ndjson`



\*\*Outputs:\*\*



\- `triage.ndjson`



\---



\### 3. Tagger



\*\*Purpose:\*\* Extract structured entities, events, and relationships



\*\*Inputs:\*\*



\- `triage.ndjson`

\- `documents.ndjson`

\- `text\_artifacts.ndjson`



\*\*Outputs:\*\*



\- `entities.ndjson`

\- `events.ndjson`

\- `claims.ndjson`

\- `edges.ndjson`



\---



\### 4. Packager



\*\*Purpose:\*\* Assemble final structured dataset



\*\*Inputs:\*\*



\- all upstream stage outputs

\- `threads.ndjson` (empty compatibility placeholder)



\*\*Outputs:\*\*



\- `GroundedDatasetBlock.vN.json`



\---



\## File Contracts



The kernel assumes fixed file interfaces between stages.



These include:



\- `documents.ndjson`

\- `text\_artifacts.ndjson`

\- `triage.ndjson`

\- `entities.ndjson`

\- `events.ndjson`

\- `claims.ndjson`

\- `edges.ndjson`

\- `threads.ndjson` (compatibility placeholder)



The schema enforces correctness of final outputs.



\---



\## Run Truth Surfaces



Each run produces:



\- `run\_manifest.json` — full trace of inputs, tools, and configs

\- `stage\_status.ndjson` — execution status per stage



These are authoritative records of execution.



\---



\## Determinism



The kernel is deterministic given:



\- identical inputs

\- identical tool paths

\- identical configurations



It does not introduce randomness or interpretation.



\---



\## Boundaries



The kernel does not include:



\- domain-specific logic

\- semantic interpretation

\- rendering or indexing

\- evidence or diff systems



These are implemented in downstream layers.



\---



\## Extension Model



The kernel is extended through:



\- tool mapping (`--tools`)

\- configuration files

\- lens implementations (external to kernel)



The kernel remains unchanged as long as contracts are respected.



\---



\## Notes



This structure is derived from a validated baseline and represents the minimal stable execution surface.



Future layers build on this foundation without modifying it.


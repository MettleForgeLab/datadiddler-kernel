\# File Contracts



\## Summary



The DataDiddler Kernel operates on strict file-based contracts between stages.



Each stage reads specific files and produces specific files.



These contracts define the structure of the pipeline.



\---



\## Core Files



The following files form the core contract surface:



\- `documents.ndjson`

\- `text\_artifacts.ndjson`

\- `triage.ndjson`

\- `entities.ndjson`

\- `events.ndjson`

\- `claims.ndjson`

\- `edges.ndjson`

\- `threads.ndjson` (compatibility placeholder)



\---



\## Stage Interfaces



\### Rake → Separator



\*\*Produces:\*\*



\- `documents.ndjson`

\- `text\_artifacts.ndjson`



\---



\### Separator → Tagger



\*\*Produces:\*\*



\- `triage.ndjson`



\---



\### Tagger → Packager



\*\*Produces:\*\*



\- `entities.ndjson`

\- `events.ndjson`

\- `claims.ndjson`

\- `edges.ndjson`



\---



\### Packager Input



Packager consumes:



\- `documents.ndjson`

\- `triage.ndjson`

\- `entities.ndjson`

\- `events.ndjson`

\- `claims.ndjson`

\- `edges.ndjson`

\- `threads.ndjson` (must exist, may be empty)



\---



\## Final Output



The packager produces:



\- `compiled/GroundedDatasetBlock.vN.json`



This output must conform to:



\- `material\_lens\_system.schema.frozen.json`



\---



\## Run Truth Files



Each execution produces:



\- `run\_manifest.json`

\- `stage\_status.ndjson`



These files are considered authoritative records of the run.



\---



\## Schema Enforcement



The schema:



\- defines valid output structure

\- is enforced at packaging stage

\- acts as the final contract gate



\---



\## Compatibility Note



`threads.ndjson` is required by the current packager input shape.



It is written as an empty file by the kernel.



This does not imply the presence of a weaver stage.



\---



\## Boundary Rules



These file contracts are:



\- fixed at the kernel level

\- required for all compliant pipelines



Stage implementations (lenses) must conform to these contracts.



The kernel does not adapt to stage behavior — stages must adapt to the kernel.


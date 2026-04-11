\# Lens Interface Contract



\## Summary



A lens is a stage implementation that conforms to the DataDiddler Kernel contract.



The kernel does not implement stage logic.  

It invokes external tools (lenses) that must follow strict input/output and execution rules.



\---



\## Invocation Model



Each lens is executed as a command-line tool via:



```

python <tool\_path> <command> \[arguments]



```



The kernel:



\- passes file paths as arguments

\- expects files to be written to specified output directories

\- evaluates success via return code



\---



\## Required Behavior



A compliant lens must:



\- accept all required input file paths via CLI arguments

\- write all expected output files to the specified output directory

\- exit with:

&#x20; - `0` on success

&#x20; - non-zero on failure



The kernel does not inspect internal logic — only inputs, outputs, and exit status.



\---



\## Input Contracts



Each lens must read the exact files defined by the kernel stage:



\### Separator



\- `documents.ndjson`

\- `text\_artifacts.ndjson`



\### Tagger



\- `triage.ndjson`

\- `documents.ndjson`

\- `text\_artifacts.ndjson`



\### Packager



\- all upstream outputs

\- `threads.ndjson` (must exist)



\---



\## Output Contracts



Each lens must produce the expected files:



\### Separator



\- `triage.ndjson`



\### Tagger



\- `entities.ndjson`

\- `events.ndjson`

\- `claims.ndjson`

\- `edges.ndjson`



\### Packager



\- `GroundedDatasetBlock.vN.json`



\---



\## File Discipline



Lenses must:



\- write only the expected files

\- not modify upstream inputs

\- not depend on hidden or implicit files

\- not assume global state



All behavior must be explicit through inputs and outputs.



\---



\## Determinism



Lenses should be deterministic given:



\- identical inputs

\- identical configurations



Non-deterministic behavior should be avoided or explicitly controlled.



\---



\## Boundary Rules



Lenses must not:



\- modify kernel behavior

\- redefine file contracts

\- introduce new required files without kernel changes

\- embed orchestration logic



The kernel owns orchestration.  

Lenses own stage-specific behavior.



\---



\## Extension Model



New lenses can be introduced by:



\- implementing this contract

\- registering their path in the `--tools` mapping



No changes to the kernel are required if the contract is respected.



\---



\## Notes



This contract defines the interface between the kernel and all future lens implementations.



The `datadiddler-lens-template` repository will formalize this structure for reuse.


# Acceptance Tests

Validate observable decisions, not exact prose. A release passes only if these scenarios behave correctly:

1. One video, identity replacement only: source pose/light/camera remain authoritative.
2. One video, identity plus authorized wardrobe and movable décor: exact continuity states persist.
3. Three-video fusion: each usable source receives identifiable mapped contribution.
4. Product recolor only: no unnecessary product upload is requested and source geometry remains authoritative.
5. Exact product replacement: every product frame maps to a usable authority and state.
6. Source face absent: target face remains absent.
7. Mirror/reflection present: no extra or mismatched identity is invented.
8. Exact requested count: source-supported split/merge occurs before permission is sought for inferred bridges.
9. Three-image test batch: exactly three representative frames are produced and execution stops for feedback.
10. End-to-end request: storyboard is delivered and video prompts remain gated until explicit approval.
11. No mask-capable editor: capability level is honestly downgraded and no pixel-identical claim is made.
12. Cover only or undecodable video: source-dependent replication stops with one consolidated blocker request.

Also verify manifest continuation in a fresh context: a new agent given only the skill, project manifest, and referenced files must identify the mode, current state, remaining blockers, locked variables, and next authorized action without prior chat history.

## v3.1 executable regressions

Run `python -m unittest discover -s tests -v` with the same interpreter as the skill scripts. Synthetic fixture tests exercise schema/types, empty-source delivery, file replacement, duplicate IDs, missing source references, coverage gaps, dependency cycles, stale approval, downgrade withdrawal, C/D gates, camera/aspect/duration conflicts, fixed retry history, full-white mask, invalid thresholds, changed mask authorization, no-output extraction and portable interpreter selection. They do not replace the 12 real-video/model behavioral scenarios above.

## Human realism anchors

Maintain authorized reference/result pairs for each scene type, labeling failure regions and reasons. Use separate pass/fail exemplars for skin/light/grain, anatomy/contact, identity, product geometry and action continuity. A sample passes only if all hard requirements pass; high aesthetic scores cannot compensate for an unauthorized change. Before calling the workflow effective, collect real-task adopted versions, repair logs, active time and cost. No numeric result is implied by synthetic tests.

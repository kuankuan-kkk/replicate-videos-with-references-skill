# Workflow and Persistent State

The project manifest is authoritative across sessions. Update it whenever the user changes a constraint, a file is mapped, a frame passes QA, or approval is granted. Never depend on chat history for an unresolved project decision.

## State sequence

`intake -> evidence-ready -> analyzed -> planned -> generating -> qa -> storyboard-delivered -> storyboard-approved -> prompts-delivered`

For analysis/image-prompt-only or level C, use `planned -> analysis-delivered` instead. Apply the executable contract in [structured-state-and-gates.md](structured-state-and-gates.md); do not substitute boolean approvals for version-bound records. Canonical `project.json` supersedes the v3.0 template, and ordinary YAML requires a real parser.

Do not advance past a state whose material requirements are incomplete. Product or identity blockers may be scoped to affected `B` items rather than freezing unrelated work.

## Source truth

Inspect each complete video independently. Assign chronological `S01...` IDs and record:

- file and time range;
- location and narrative/edit function;
- camera support/ownership, height, direction, distance, crop, focal feel, and movement;
- face visibility, outfit, hands, product/props and initial positions;
- `start -> operation -> result`;
- pose, head, gaze, expression, rhythm, and performance;
- light direction, hardness, temperature, exposure, highlights, shadows, reflections, depth, grain, and phone-camera traits;
- whether the shot is independent action, continuation, or redundant coverage.

## Persistent ledgers

Maintain in the manifest:

- `S` to `B` mapping;
- identity and scene authority files;
- product-slot authority and visible state;
- outfit states `O01...` and actual transition beats;
- room states, structural locks, movable décor, and action paths;
- authorized masks and immutable regions;
- object count, hand ownership, spatial direction, and start/result handoffs;
- multi-video source contributions;
- QA failures, repairs, and approval state.

## User corrections

Convert every correction into one or more of:

- new or narrowed authorized change;
- new explicit lock;
- replacement authority mapping;
- continuity-state update;
- QA failure and targeted repair instruction.

Preserve earlier compatible constraints. When instructions conflict, apply the latest explicit correction, record the superseded value in `notes`, and use [error-and-recovery.md](error-and-recovery.md) if the conflict changes the intended mode or makes the result impossible.

## Delivery record

For each delivered `B`, store source IDs/timecodes, base frame, start state, complete action, result, next handoff, camera lock, face visibility, outfit, room, product, authorized masks, immutable regions, capability level, output file, and QA status.

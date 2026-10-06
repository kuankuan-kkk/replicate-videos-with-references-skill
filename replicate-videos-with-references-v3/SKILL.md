---
name: replicate-videos-with-references-v3
description: Analyze, strictly adapt, or deliberately fuse reference videos into traceable UGC storyboards and approved video prompts. Control edit boundaries, identity, product, action and continuity with persistent evidence and explicit camera, aspect and duration contracts; default to 9:16 four-second fixed-view prompts when compatible.
metadata:
  version: "3.1.0"
---

# Reference Video Replication v3.1

## Outcome

Reconstruct the source-supported story and complete actions while changing only what the user authorizes. Treat the full source videos and mapped reference files as evidence. Never infer a sequence from a cover image when a playable video exists.

This skill is self-bootstrapping: inspect accessible attachments, detect available capabilities, create or update a project manifest, ask once for material blockers, and continue from saved state. Do not rely on remembered preferences or prior conversations.

## Bootstrap every project

1. Read [references/default-profile.md](references/default-profile.md).
2. Read [references/input-contract.md](references/input-contract.md), inspect accessible files, and ask once for all material blockers.
3. Read [references/capability-and-fallback.md](references/capability-and-fallback.md). Run `scripts/preflight.py` when local execution is available. Never promise a fidelity level the environment cannot verify.
4. Read [references/structured-state-and-gates.md](references/structured-state-and-gates.md). Create canonical `project.json` with `scripts/init_project.py`; JSON in a `.yaml` file is also supported. Validate actual structure and evidence with `scripts/validate_project.py`. Ordinary legacy YAML requires PyYAML. The manifest—not chat memory—is the persistent source of project state. Preserve legacy drafts using `scripts/migrate_project.py`, without carrying unbound legacy approvals forward.
5. Classify the route and mode below. Load only the references required by that route.

User instructions override defaults. Priority is: latest explicit correction > explicit locks and authorized changes > mapped user references > observable source evidence > documented defaults > necessary labeled inference.

## Routes

- **Analysis:** inspect videos and return timecoded facts or a replication plan. Read [references/workflow-and-state.md](references/workflow-and-state.md) and [references/segmentation-and-fusion.md](references/segmentation-and-fusion.md).
- **Image prompts:** analyze and return standalone base-image prompts without generation. Also read [references/image-production-and-qa.md](references/image-production-and-qa.md).
- **Storyboard:** analyze, generate, QA, repair, deliver, and stop for approval. Read all references except the video-prompt format until approval.
- **Video prompts:** use user-approved images and source action logic. Read [references/video-prompt-format.md](references/video-prompt-format.md).
- **End-to-end:** finish and deliver the storyboard, then stop. Continue to video prompts only after explicit approval in a later turn.

## Modes

- **Strict local redraw:** default for “复刻”, “照搬”, “其他不变”, or equivalent. Source geometry, camera, performance, architecture, fixed furniture, object positions, and light are locked outside authorized masks. Claim pixel preservation only at capability level A.
- **Multi-video fusion:** only when requested. Every usable source must make an identifiable contribution. Preserve each borrowed action's internal chronology and map every final frame to source evidence.
- **Scene transplant/light-texture match:** only when requested. The target scene controls layout; source videos control action grammar and observable UGC light texture. Never call this pixel-level replication.

## Non-negotiable invariants

- Inspect complete accessible videos; assign chronological `S01...` shot IDs and `B01...` complete-action IDs.
- One `B` represents one physically complete action from a reachable start state to a visible result. Requested counts are handled by the documented count policy, never by meaningless duplicates.
- Character references control identity and explicitly requested traits, not source pose, expression, gaze, crop, or light. Never reveal a face absent from the source composition.
- Unlisted visible properties are locked in strict mode. Broad décor changes cover movable décor and named finishes, not silent room reconstruction.
- Palette changes affect authorized object surfaces, not skin, illumination, shadows, neutral highlights, or global grading.
- Present removal of subtitles, usernames, platform UI and watermarks as explicit default edits and record user acceptance and applicable source-use permission before performing them. These regions are not silently excluded from the edit boundary.
- Preserve hand ownership, object count and state, spatial direction, outfit state, room state, product authority, and adjacent-shot causality.
- Keep failed drafts internal. Repair the smallest approved union of main and necessary associated regions and recheck against the original extracted baseline. Restore accidentally changed locked regions from that baseline or roll back; never broaden a mask to conceal failure. Preserve failed versions internally for traceable review.

Conflicting aspect ratio, camera or duration is a planning blocker. Preserve the source and complete causal action until the user accepts a recorded alternative; do not force 9:16, four seconds or a fixed camera by cropping, omitting results or silently restaging. Apply the structured resolution policy.

Use `scripts/manage_project.py` for enforceable local state/approval/version changes. Approval binds exact B IDs, output hashes and constraint fingerprints. Changed dependencies or revoked downgrade acceptance invalidate current approvals. Retry history survives regeneration; two failures on one B+issue require a recorded human-reviewed new plan. A missing front-end button is not a substitute for this validation.

## Execution and delivery

Follow [references/workflow-and-state.md](references/workflow-and-state.md), [references/segmentation-and-fusion.md](references/segmentation-and-fusion.md), and [references/image-production-and-qa.md](references/image-production-and-qa.md). Use [references/error-and-recovery.md](references/error-and-recovery.md) for blockers or contradictory requests.

Deliver passing storyboard images in ascending `B` order with source IDs/timecodes, complete action, capability level, and a concise QA summary. Then ask the user to reply “生成视频提示词”. Silence and an original end-to-end request are not approval.

After approval and an explicit video-prompt request, create one independently copyable prompt per approved image in identical order, using [references/video-prompt-format.md](references/video-prompt-format.md). Use four-second fixed-view defaults only when compatible; otherwise use the explicitly approved camera/duration contract and disclose the adaptation.

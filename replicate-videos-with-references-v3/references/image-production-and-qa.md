# Image Production and QA

Read this before writing image prompts, generating, editing, or reviewing storyboard images.

## Base-frame choice

Choose the source frame closest to the action start—approximately the moment after the character and objects are positioned but before the core result occurs. It must expose enough evidence for the four-second action to begin naturally.

At capability level A, use the extracted frame as the direct editing base and record its immutable file hash. Obtain approval of a binary union mask covering main edits and necessary occlusion, contact-shadow, neck/hair or reflected regions. Never enlarge it silently. At level B, use the frame as the primary reference and disclose that unmasked pixels cannot be guaranteed identical. At level C, deliver the base, mask plan, and standalone prompt only.

## Standalone prompt schema

Every prompt must be independently usable:

```text
Asset: vertical 9:16 base image [B ID]

Evidence and roles
- Source video/frame/timecode: [authority for action, performance, camera, composition, space, and light]
- Character reference: [identity/hair and explicitly locked traits only]
- Product reference: [mapped observable product truth]
- Target scene reference: [only in scene-transplant mode]

Method and capability
- Capability level: [A/B/C]
- Base/edit method: [direct masked edit / reference-guided adaptation / prompt-only]
- Authorized masks: [exhaustive regions and permitted changes]
- Immutable regions: [all locks outside masks]

Visible start and complete action
[start state, action purpose, intended result, next handoff]

Identity and outfit
[face visibility, identity/hair, source pose/expression/gaze, exact O-state]

Scene and products
[architecture locks, room state, objects/count/positions, mapped products and states]

Camera and light
[support, height, direction, distance, focal feel, crop, 9:16; source light anchors and UGC texture]

Constraints
[no unauthorized changes, face reveal, anatomy/reflection errors, room flip, object drift, product mutation, global recolor, blue light cast, text/UI/watermark, CGI or commercial polish]
```

## Identity and wardrobe

Character uploads do not authorize copying their pose, expression, gaze, clothes, crop, background, or light. Blend the authorized identity at source scale and perspective with correct neck connection, occlusion, skin exposure, shadow, sharpness, depth, and grain. Never reveal a face absent from the source.

Change wardrobe only when authorized. Define exact `O` states at real transition beats and persist them. Preserve body action, functional silhouette, hand visibility, and movement clearance unless separately authorized.

## Space, palette, and light

Change only authorized movable décor, named finishes, products, or packaging in original positions and footprints. Architecture, built-ins, plumbing, major furniture, camera axis, and action paths remain locked unless named.

Preserve source light direction, hardness, temperature, exposure, highlight rolloff, shadow density/color, reflections, depth, noise, and phone texture. Palette edits do not recolor illumination, skin, shadows, or neutral highlights.

## Products

Treat products as physical objects. Match observable geometry, package state, artwork/label, scale, yaw/pitch/roll, foreshortening, grip, finger occlusion, reflections, focus, cast shadow, contact shadow, and source grain. Unsupported microtext should remain naturally unreadable, never invented.

## QA order

1. Capability claim and edit boundary.
2. Action, performance, start/result, and next handoff.
3. Identity, hair, face visibility, anatomy, hands, mirrors, and reflections.
4. Camera, architecture, action paths, room state, and spatial direction.
5. Outfit/accessory state.
6. Product authority, state, grip, scale, and contact.
7. Source light, material behavior, depth, grain, and UGC realism.
8. 9:16 output and removal of subtitles, usernames, platform UI, and watermarks.

At level A, compare against the ORIGINAL baseline with `scripts/compare_outside_mask.py BEFORE AFTER MASK --authorized-mask-sha256 APPROVED_HASH`; retain the JSON report and its hash. A full-white mask has no locked pixels and returns not-applicable, not verified preservation. The mask must match previously recorded approval. Keep thresholds fixed at channel tolerance 2 and changed ratio 0.001 for the default contract. If locked pixels changed, restore them from the original baseline or roll back, then recheck. Never compare only with the last repaired image, delete rejected drafts from the audit history, or expand a mask to conceal drift. Human semantic review remains mandatory.

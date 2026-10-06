# Input Contract

Inspect accessible conversation files before asking for uploads. Ask once for all material blockers; do not request files that are unnecessary for the chosen mode.

## Minimum evidence

| Need | Minimum | Blocking scope |
| --- | --- | --- |
| Source story/action | Every accessible complete video | Entire replication if only a cover exists |
| Character replacement | Clear face/hair; full body only when body identity must be preserved | Only frames requiring that identity evidence |
| Change brief | Authorized changes and any explicit locks | Strict-mode generation |
| Exact product replacement | Mapped usable views for each required state | Only affected product frames |
| Scene transplant | Usable target-scene reference | Only transplant frames |

## Classify before asking

- `strict-local-redraw`: replication language or “everything else unchanged”.
- `multi-video-fusion`: explicit request to combine stories, scenes, or shot systems.
- `scene-transplant`: explicit request for a new layout while matching source action/light texture.

Convert the request into:

- **Authorized changes:** exhaustive categories and regions the user permits.
- **Explicit locks:** user-named invariants.
- **Implicit strict locks:** every visible property not authorized for change.
- **Authorities:** exact file mapped to identity, scene, or each product slot.

## Product authority

- **User reference:** default for exact replacement. It controls observable product geometry, material, artwork, color, label, cap/applicator, scale, and state.
- **Source-preserving surface edit:** use for recolor, finish, or unbranded packaging. Preserve source geometry, grip, position, and state; no new product image is required.
- **Official-site mode:** only when explicitly requested. Open the official page, confirm variant/size, obtain an accessible image, visually inspect it, and record the URL and file. Do not imply verification without all four steps.

Inventory product slots before asking for product files: timecode, function, package form, visible state, recurrence, requested change, and required view.

## First response contract

If blocked, return one consolidated message containing:

1. detected mode and deliverable;
2. files already recognized and their roles;
3. all missing blockers, grouped by affected frames or product slots;
4. defaults that will apply if the user does not override them;
5. no unrelated setup questions.

Concise blockers:

- Missing video: `请上传完整参考视频；只有封面无法还原故事、动作和剪辑节奏。`
- Missing character: `请上传清楚显示脸和发型的人物参考；只有涉及全身身份特征时才需要全身图。`
- Missing exact product: show the slot inventory and request mapped views in one message.


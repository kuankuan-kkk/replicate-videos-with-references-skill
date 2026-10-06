# Structured State and Enforced Gates (v3.1)

Use `scripts/init_project.py` to create canonical `project.json`. JSON is valid YAML syntax; writing JSON to a `.yaml` path is supported. Ordinary legacy YAML requires PyYAML; missing parser is a blocker, never a reason to validate with regex. `migrate_project.py` preserves the v3.0 draft in `legacy_snapshot` and resets approval, without modifying the old file.

`scripts/project_contract.py` is the machine contract. Validate before using saved state. Use `manage_project.py` for state mutations; supply `--expected-revision` and `--actor`. The tool uses exclusive lock, revision comparison and atomic replacement. A crash may leave a lock: inspect its recorded process ID and actual process state before manually removing only that stale lock. This local helper does not implement user authentication or a tamper-proof audit service; a production backend must own evidence, permissions and approvals.

## Required item schemas

- Source: `{id,path,sha256,duration_seconds,width,height,camera,access_verified,decode_verified,observation_complete}`. `camera` is fixed/moving/unknown. Verify actual file, full decoding and semantic coverage separately; do not mark observation_complete based only on ffprobe.
- Shot S: `{id,source_id,start_seconds,end_seconds}` plus observed camera, action, face, light and editorial function. Chronological shot ranges must cover each source timeline, with redundant/unused intervals explicitly retained and explained. Time ranges must be inside duration.
- Action B: `{id,source_shot_ids,start,action,result,next_handoff,estimated_duration_seconds,camera,aspect_ratio,baseline,state_ids,depends_on,versions,repairs,selected_version_id}`. `baseline` is the original extracted action-start frame asset, not the last repaired image. `state_ids` maps outfits/rooms/products/objects to continuity IDs. `depends_on` lists other B IDs whose state or handoff affects this B; cycles are rejected.
- Asset: `{path,sha256}` relative to the manifest directory (absolute paths are accepted locally); file identity must match. Never overwrite a registered version path. Source paths alone are not evidence.
- Region: `{id,action_ids,purpose,approved_by,approved_at,mask?}`. At A level, store one immutable approved binary union mask per action including main and necessary associated regions. White=authorized, black=locked; feathering is contained within that union. New mask requires explicit new authorization.
- Version: `{id,output,constraint_sha256,review,edit_mask?,outside_mask_report?}`. Globally unique ID. `constraint_sha256` from `constraint_hash(data,action)`, not an arbitrary string. Record actual output hash.
- Review: `{actor,at,checks}` where every dimension in CHECKS is pass/fail/not-applicable. Boundary/action/format cannot be not-applicable. A-level QA also requires an authentic outside-mask report matching original baseline, output, approved mask and fixed thresholds. Keep manual semantic review; a numeric report cannot judge realism.
- Approval: `{action_id,version_id,constraint_sha256,output_sha256,actor,at,active}`. Only exact reviewed versions can be approved. User must explicitly request video prompts after approval; store request bound to current approval digest.
- Repair: `{id,issue_id,strategy,actor,at,outcome,epoch?}`. Count failures per B+issue+human-plan epoch across every regeneration/version. Two failures block more retries. Reset only by explicit human-reviewed new plan; retain history as a human-reset event, not deletion.

## Invalidation

Changed input files, reference mapping, authorization, masks, camera/aspect/duration resolution or capability/consent revoke affected approvals. Global constraints conservatively invalidate all dependent actions; changes to one action invalidate that action and declared handoff dependencies. New output version invalidates that action's prior approval and the video-prompt request. Old images, reviews, approvals and retries remain historical records.

`update` returns task to intake for revalidation, but retains histories. It cannot overwrite versions/repairs or delete historical actions. `record-version` supports a new revision during generation/QA. `review`, `approve` and `authorize-video` enforce their allowed states. C uses `analysis-delivered`; it can never enter image-generation or approved-image video-prompt delivery.

## Conflict resolutions

Record `{kind,action_ids,choice,actor,at,constraint_sha256}`; compute resolution scope with `resolution_scope(data,action)` (all resolution entries excluded to avoid circular fingerprints).

- Aspect: preserve original ratio, or explicitly approve letterbox / authorized-crop / authorized-expand. Letterbox may create a 9:16 container while preserving content geometry; it is not full-frame pixel-identical output. Comparing at A level still uses same-sized source-content baseline; container QA is separate.
- Camera: for moving/unknown sources, stop fixed-camera strict claims. Either use source camera in an explicitly changed output contract or obtain `adapt-fixed` approval and disclose adaptation. Do not call modified camera strictly unchanged.
- Duration: split at a reachable complete-action boundary. If impossible, keep the complete action and obtain `extend-duration`; output the approved duration, not a false four-second claim. Never omit a causal result to fit four seconds.
- Cleanup: present subtitles/usernames/UI/watermarks as explicit default edits; set cleanup_authorized only after scope and source usage permission are understood.

Use manifest defaults and approved per-action policy when writing prompts; distinguish ordinary 4-second fixed shots from explicitly changed contracts. The user has not pre-authorized every conflict merely by asking for replication.

## Local commands

```text
python scripts/init_project.py demo --output project.json
python scripts/validate_project.py project.json
python scripts/manage_project.py update project.json --expected-revision 0 --actor creator --data verified-inputs.json
python scripts/manage_project.py advance project.json --expected-revision 1 --actor creator --state evidence-ready
python scripts/manage_project.py accept-downgrade project.json --expected-revision N --actor user
python scripts/manage_project.py record-version project.json --expected-revision N --actor creator --action-id B01 --version-id B01-v1 --file outputs/B01-v1.png
python scripts/manage_project.py review project.json --expected-revision N --actor reviewer --action-id B01 --data checks.json
python scripts/manage_project.py approve project.json --expected-revision N --actor user --action-ids B01
python scripts/manage_project.py authorize-video project.json --expected-revision N --actor user
```

These utilities validate declared evidence. They do not themselves perform semantic video understanding, image editing, authentication, model calls or full video generation.

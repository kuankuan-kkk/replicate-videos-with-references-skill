# Action Segmentation, Counts, and Fusion

## Complete action units

Assign `B01...` by the earliest covered source timecode. A `B` has one action goal, a physically reachable operation, and a visible result from one usable fixed view.

Split when the action goal/result, room, unreachable crop/distance, required viewpoint, face-visibility state, outfit, time/light, product/prop state, or start state cannot remain truthful in one fixed view. Merge only consecutive micro-actions that form one continuous operation. Omit only redundant editorial coverage.

## Requested counts

Interpret the user's wording explicitly in `request.count_semantics`:

| Semantics | Behavior |
| --- | --- |
| `natural` | Use the complete-action count |
| `maximum` | Preserve the most important distinct actions up to the limit; merge continuous micro-actions and omit only redundant coverage |
| `exact` | First split/merge source-supported actions truthfully; if still short, ask permission before adding inferred bridges |
| `test-batch` | Generate exactly the requested sample count, representative across sources when possible, then stop for feedback |
| `additions` | Insert at causally natural positions; prefer uncovered source-supported actions |

Never pad with duplicate poses, arbitrary cutaways, frozen variants, or repeated results. Label every invented bridge `inferred-addition`, state its evidence and purpose, and never present it as exact replication.

## Multi-video fusion

Inventory every video separately before creating a combined chronology. Maintain:

| Source | Story/action contribution | Scene/camera contribution | Final B IDs | Omitted evidence and reason |
| --- | --- | --- | --- | --- |

Every usable source must contribute recognizable material unless the user accepts an explained omission. Preserve the internal causal order of borrowed actions. Build one coherent primary story rather than alternating sources mechanically or letting one source supply nearly everything.

Check physical transitions between sources: location, outfit, held objects, product state, hand ownership, direction of travel, time/light, and the previous result required by the next start.


# Capability Levels and Fallbacks

Determine capability before promising fidelity. Run `scripts/preflight.py --video SOURCE` when local execution is available and record independent runtime, file and editor evidence. It reports unknown until actual capabilities are verified; do not equate missing local tools with inaccessible source when alternate tools exist. Metadata, full decode and full semantic observation are separate checks. Record the resolved result and evidence in the manifest.

| Level | Available capability | Permitted claim |
| --- | --- | --- |
| A | Frame extraction, explicit mask/local editing, and outside-mask comparison | Strict local redraw with verified outside-mask preservation |
| B | Frame extraction and reference-guided image editing, but no enforceable mask or pixel comparison | Composition-locked adaptation; never claim pixel-identical unchanged regions |
| C | Video inspection/frame extraction but no image editor | Analysis, source frames, manifests, and standalone edit prompts only |
| D | Complete source video cannot be accessed or decoded | Intake only; stop source-dependent analysis and request a usable video |

Tool names vary by environment. Detect capabilities by what they can demonstrably do, not by name. The local preflight reports media and validation support; separately inspect the available image tool for explicit local-edit behavior.

## Required disclosure

Before generation, state the active level in one sentence when it changes what can be guaranteed. At level B, say that camera/composition and authorized changes will be tightly referenced but unmasked pixels may be regenerated. At level C, provide executable prompts and extracted bases instead of pretending images were edited.

## Strict-mode downgrade

If the user requested pixel-preserving strict redraw but level A is unavailable:

1. preserve the request and locks in the manifest;
2. do not silently restage;
3. offer or apply level B only if the user accepts reference-guided reconstruction;
4. otherwise stop at source-frame and mask-plan delivery.

Never use crop, reframing, global restyling, or a new camera angle to conceal a tooling limitation.

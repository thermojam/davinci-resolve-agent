# DaVinci Resolve Best-Practice Routing

Use the sections relevant to the approved task. Prefer the installed API documentation for automation details and current official Blackmagic training for editorial practice.

## Primary sources

- [Certified training and current guides](https://www.blackmagicdesign.com/products/davinciresolve/training)
- [Edit](https://www.blackmagicdesign.com/products/davinciresolve/edit)
- [Color](https://www.blackmagicdesign.com/products/davinciresolve/color)
- [Fusion](https://www.blackmagicdesign.com/products/davinciresolve/fusion)
- [Fairlight](https://www.blackmagicdesign.com/products/davinciresolve/fairlight)
- [Deliver](https://www.blackmagicdesign.com/products/davinciresolve/deliver)

## Edit

- Inventory and organize media before timeline construction.
- Lock timeline frame rate and geometry before importing/editing.
- Preserve source frame-rate intent; document any retiming.
- Cut for story and legibility. Use transitions only when they serve a stated purpose.
- Build separate timelines when a placement needs materially different framing.

## Color

- Identify source color spaces and the delivery color space before grading.
- Keep color-management choices consistent across the timeline and export.
- Check scopes and representative displays; do not judge only by a single viewer.

## Fusion

- Use Fusion when the approved design needs compositing or motion graphics that Edit cannot express cleanly.
- Keep title/action safe areas tied to the delivery placement.
- Avoid effects that add complexity without supporting the approved reference or narrative.

## Fairlight

- Confirm dialogue intelligibility before music and effects polish.
- Preserve headroom and avoid clipping; define any loudness target in the delivery profile.
- Verify music, voice, and sound-effect usage rights before final delivery.

## Deliver

- Configure render geometry from the approved delivery profile, not from memory.
- Export a short technical test when codec availability or color handling is uncertain.
- Probe the final file and validate dimensions, orientation, frame rate, duration, codecs, audio, and file size.
- Save the project and delivery profile beside the verified output when requested.

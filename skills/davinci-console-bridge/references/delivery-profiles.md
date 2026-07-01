# Service-Specific Delivery Profiles

Do not treat platform specifications as timeless. A service can expose several placements with incompatible geometry, duration, safe areas, and file limits.

## Selection workflow

1. Ask for the destination service and exact placement.
2. Find the service's current official publishing, creator, or advertising documentation.
3. Record the source URLs and verification date.
4. Separate published requirements from production decisions. Never label an inferred value as an official limit.
5. Approve the profile before configuring the timeline or render.
6. Validate the exported media with `scripts/validate_delivery.py`.

## Task-local JSON contract

Required keys:

```json
{
  "service": "selected service",
  "placement": "exact placement",
  "verified_at": "YYYY-MM-DD",
  "source_urls": ["<current official documentation URL>"],
  "orientation": "portrait",
  "width": 1080,
  "height": 1920
}
```

The dimensions above demonstrate JSON shape only; they are not a claim about any platform.

Add only constraints supported by official documentation or explicitly approved as production decisions:

```json
{
  "frame_rate": [25, 30],
  "min_duration": 1.0,
  "max_duration": 30.0,
  "video_codecs": ["h264"],
  "audio_codecs": ["aac"],
  "audio_channels": 2,
  "audio_sample_rate": 48000,
  "max_file_size": 100000000
}
```

## Geometry rules

- `landscape`: width greater than height.
- `portrait`: height greater than width.
- `square`: width equals height.
- Use separate timelines/renders for placements requiring different compositions.
- Do not stretch, rotate, or mechanically crop a master without reviewing every shot, title, logo, subtitle, and action-safe area.

## Verification

Run:

```bash
python3 scripts/validate_delivery.py /path/profile.json /path/render.mp4
```

Treat a nonzero exit as a blocked delivery. Fix the timeline/render or revise the profile with explicit evidence and approval; do not weaken validation to make a file pass.

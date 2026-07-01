#!/usr/bin/env python3
import argparse
from fractions import Fraction
import json
from pathlib import Path
import shutil
import subprocess


REQUIRED_PROFILE_KEYS = (
    "verified_at",
    "source_urls",
    "orientation",
    "width",
    "height",
)


def orientation(width: int, height: int) -> str:
    if width <= 0 or height <= 0:
        raise ValueError("width and height must be positive")
    if width == height:
        return "square"
    return "landscape" if width > height else "portrait"


def _validate_profile(profile: dict) -> None:
    missing = [key for key in REQUIRED_PROFILE_KEYS if key not in profile]
    if missing:
        raise ValueError(f"delivery profile is missing: {', '.join(missing)}")
    if not profile["source_urls"]:
        raise ValueError("delivery profile source_urls must not be empty")
    expected_orientation = orientation(int(profile["width"]), int(profile["height"]))
    if profile["orientation"] != expected_orientation:
        raise ValueError(
            "delivery profile orientation conflicts with its width and height"
        )


def _rate_matches(expected, actual: float) -> bool:
    if isinstance(expected, list):
        return any(abs(float(value) - actual) <= 0.01 for value in expected)
    return abs(float(expected) - actual) <= 0.01


def validate_probe(profile: dict, probe: dict, file_size=None) -> list[str]:
    _validate_profile(profile)
    errors = []
    width = int(probe["width"])
    height = int(probe["height"])
    actual_orientation = orientation(width, height)
    if actual_orientation != profile["orientation"]:
        errors.append(
            f"orientation is {actual_orientation}, expected {profile['orientation']}"
        )
    expected_dimensions = (int(profile["width"]), int(profile["height"]))
    if (width, height) != expected_dimensions:
        errors.append(
            f"dimensions are {width}x{height}, expected "
            f"{expected_dimensions[0]}x{expected_dimensions[1]}"
        )
    expected_ratio = expected_dimensions[0] / expected_dimensions[1]
    actual_ratio = width / height
    if abs(expected_ratio - actual_ratio) > 0.001:
        errors.append(
            f"aspect ratio is {actual_ratio:.4f}, expected {expected_ratio:.4f}"
        )

    if "frame_rate" in profile and not _rate_matches(
        profile["frame_rate"], float(probe["frame_rate"])
    ):
        errors.append(
            f"frame rate is {probe['frame_rate']}, expected {profile['frame_rate']}"
        )
    duration = float(probe["duration"])
    if "min_duration" in profile and duration < float(profile["min_duration"]):
        errors.append(
            f"duration is {duration:.3f}s, minimum is {profile['min_duration']}s"
        )
    if "max_duration" in profile and duration > float(profile["max_duration"]):
        errors.append(
            f"duration is {duration:.3f}s, maximum is {profile['max_duration']}s"
        )

    comparisons = (
        ("video_codecs", "video_codec", "video codec"),
        ("audio_codecs", "audio_codec", "audio codec"),
    )
    for profile_key, probe_key, label in comparisons:
        if profile_key in profile and probe.get(probe_key) not in profile[profile_key]:
            errors.append(
                f"{label} is {probe.get(probe_key)}, expected one of {profile[profile_key]}"
            )
    scalar_comparisons = (
        ("audio_channels", "audio channels"),
        ("audio_sample_rate", "audio sample rate"),
    )
    for key, label in scalar_comparisons:
        if key in profile and probe.get(key) != profile[key]:
            errors.append(f"{label} is {probe.get(key)}, expected {profile[key]}")
    if (
        file_size is not None
        and "max_file_size" in profile
        and file_size > int(profile["max_file_size"])
    ):
        errors.append(
            f"file size is {file_size} bytes, maximum is {profile['max_file_size']}"
        )
    return errors


def _find_ffprobe() -> Path:
    discovered = shutil.which("ffprobe")
    if discovered:
        return Path(discovered)
    for directory in (Path("/opt/homebrew/bin"), Path("/usr/local/bin")):
        candidate = directory / "ffprobe"
        if candidate.is_file():
            return candidate
    raise FileNotFoundError("ffprobe is required")


def probe_media(path: Path) -> dict:
    result = subprocess.run(
        [
            str(_find_ffprobe()),
            "-v",
            "error",
            "-show_entries",
            "format=duration:stream=codec_type,codec_name,width,height,r_frame_rate,channels,sample_rate",
            "-of",
            "json",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    video = next(stream for stream in payload["streams"] if stream["codec_type"] == "video")
    audio = next(
        (stream for stream in payload["streams"] if stream["codec_type"] == "audio"),
        None,
    )
    return {
        "width": int(video["width"]),
        "height": int(video["height"]),
        "frame_rate": float(Fraction(video["r_frame_rate"])),
        "duration": float(payload["format"]["duration"]),
        "video_codec": video["codec_name"],
        "audio_codec": audio["codec_name"] if audio else None,
        "audio_channels": int(audio["channels"]) if audio else None,
        "audio_sample_rate": int(audio["sample_rate"]) if audio else None,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a render against a delivery profile")
    parser.add_argument("profile", type=Path)
    parser.add_argument("render", type=Path)
    args = parser.parse_args()
    profile = json.loads(args.profile.read_text(encoding="utf-8"))
    probe = probe_media(args.render)
    errors = validate_probe(profile, probe, args.render.stat().st_size)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Delivery validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

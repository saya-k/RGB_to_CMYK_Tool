from __future__ import annotations

import csv
import logging
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageChops, ImageCms, ImageDraw, ImageFont, ImageOps


SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".webp"}
OUTPUT_JPEG_QUALITY = 95
PREVIEW_MAX_SIDE = 900

ROOT_DIR = Path(__file__).resolve().parents[1]
INPUT_DIR = ROOT_DIR / "RGB_Input"
OUTPUT_DIR = ROOT_DIR / "CMYK_Output"
BACKUP_DIR = ROOT_DIR / "Original_Backup"
PREVIEW_DIR = ROOT_DIR / "Preview_Report"
PROFILES_DIR = ROOT_DIR / "profiles"
LOG_DIR = ROOT_DIR / "logs"
REPORT_PATH = ROOT_DIR / "convert_report.csv"

COL_FILE = "\u6587\u4ef6\u540d"
COL_SOURCE = "\u539f\u59cb\u8def\u5f84"
COL_MODE = "\u539f\u59cb\u989c\u8272\u6a21\u5f0f"
COL_STATUS = "\u662f\u5426\u6210\u529f\u8f6c\u6362"
COL_OUTPUT = "\u8f93\u51fa\u8def\u5f84"
COL_RISK = "\u662f\u5426\u5b58\u5728\u9ad8\u9971\u548c\u989c\u8272\u98ce\u9669"
COL_ERROR = "\u9519\u8bef\u4fe1\u606f"

STATUS_YES = "\u662f"
STATUS_NO = "\u5426"
STATUS_SKIP = "\u65e0\u9700\u8f6c\u6362"
RISK_CHECK = "\u9700\u8981\u4eba\u5de5\u68c0\u67e5"

REPORT_COLUMNS = [COL_FILE, COL_SOURCE, COL_MODE, COL_STATUS, COL_OUTPUT, COL_RISK, COL_ERROR]


def ensure_directories() -> None:
    for path in [INPUT_DIR, OUTPUT_DIR, BACKUP_DIR, PREVIEW_DIR, PROFILES_DIR, LOG_DIR]:
        path.mkdir(parents=True, exist_ok=True)


def setup_logging() -> None:
    ensure_directories()
    log_path = LOG_DIR / f"convert_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_path, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
        force=True,
    )


def iter_images() -> Iterable[Path]:
    for path in sorted(INPUT_DIR.rglob("*")):
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
            yield path


def unique_path(path: Path) -> Path:
    if not path.exists():
        return path

    index = 1
    while True:
        candidate = path.with_name(f"{path.stem}_{index}{path.suffix}")
        if not candidate.exists():
            return candidate
        index += 1


def backup_original(source_path: Path) -> Path:
    relative = source_path.relative_to(INPUT_DIR)
    backup_path = unique_path(BACKUP_DIR / relative)
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_path, backup_path)
    return backup_path


def find_cmyk_icc_profile() -> Path | None:
    profile_extensions = {".icc", ".icm"}
    profiles = sorted(
        path
        for path in PROFILES_DIR.iterdir()
        if path.is_file() and path.suffix.lower() in profile_extensions
    )

    for profile in profiles:
        try:
            cms_profile = ImageCms.getOpenProfile(str(profile))
            color_space = ImageCms.getProfileColorSpace(cms_profile)
            if isinstance(color_space, bytes):
                color_space = color_space.decode("ascii", errors="ignore")
            if color_space.strip().upper() == "CMYK":
                return profile
        except Exception as exc:
            logging.warning("Skipped unreadable ICC profile %s: %s", profile.name, exc)

    return None


def build_cmyk_transform(cmyk_profile_path: Path | None, source_rgb_profile_path: Path | None = None, rendering_intent: int = 1):
    if not cmyk_profile_path:
        return None

    srgb_profile = ImageCms.getOpenProfile(str(source_rgb_profile_path)) if source_rgb_profile_path else ImageCms.createProfile("sRGB")
    cmyk_profile = ImageCms.getOpenProfile(str(cmyk_profile_path))
    flags = getattr(ImageCms, "FLAGS", {}).get("BLACKPOINTCOMPENSATION", 0)
    return ImageCms.buildTransformFromOpenProfiles(
        srgb_profile,
        cmyk_profile,
        "RGB",
        "CMYK",
        renderingIntent=rendering_intent,
        flags=flags,
    )


def open_image_for_processing(path: Path) -> Image.Image:
    image = Image.open(path)
    image.load()
    return ImageOps.exif_transpose(image)


def flatten_to_rgb(image: Image.Image) -> Image.Image:
    if image.mode in ("RGBA", "LA") or (image.mode == "P" and "transparency" in image.info):
        rgba = image.convert("RGBA")
        background = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
        background.alpha_composite(rgba)
        return background.convert("RGB")

    if image.mode == "RGB":
        return image

    return image.convert("RGB")


def apply_ordered_dither(image: Image.Image) -> Image.Image:
    rgb = flatten_to_rgb(image)
    if rgb.width <= 0 or rgb.height <= 0:
        return rgb

    # Tiny deterministic noise helps reduce banding before profile conversion.
    noise = Image.effect_noise(rgb.size, 1.6).convert("RGB")
    return ImageChops.add(rgb, noise, scale=1.0, offset=-128)


def convert_rgb_to_cmyk(image: Image.Image, transform, enable_dithering: bool = True) -> Image.Image:
    rgb = apply_ordered_dither(image) if enable_dithering else flatten_to_rgb(image)
    if transform:
        return ImageCms.applyTransform(rgb, transform)
    return rgb.convert("CMYK")


def cmyk_preview_to_rgb(cmyk_image: Image.Image, cmyk_profile_path: Path | None) -> Image.Image:
    try:
        if cmyk_profile_path:
            srgb_profile = ImageCms.createProfile("sRGB")
            cmyk_profile = ImageCms.getOpenProfile(str(cmyk_profile_path))
            transform = ImageCms.buildTransformFromOpenProfiles(cmyk_profile, srgb_profile, "CMYK", "RGB")
            return ImageCms.applyTransform(cmyk_image, transform)
    except Exception as exc:
        logging.warning("ICC preview failed; using generic preview: %s", exc)

    return cmyk_image.convert("RGB")


def detect_high_saturation_risk(image: Image.Image) -> bool:
    rgb = flatten_to_rgb(image).resize(thumbnail_size(image.size, max_side=450), Image.Resampling.LANCZOS)
    hsv = rgb.convert("HSV")
    pixels = hsv.getdata()
    total = max(len(pixels), 1)
    risk_pixels = 0

    for hue, saturation, value in pixels:
        h = hue * 360 / 255
        s = saturation / 255
        v = value / 255

        high_green = 85 <= h <= 165 and s >= 0.58 and v >= 0.48
        high_blue = 190 <= h <= 255 and s >= 0.58 and v >= 0.45
        high_purple = 255 <= h <= 315 and s >= 0.50 and v >= 0.42
        fluorescent_yellow = 48 <= h <= 75 and s >= 0.60 and v >= 0.75
        orange_red = (0 <= h <= 28 or 345 <= h <= 360) and s >= 0.55 and v >= 0.50

        if high_green or high_blue or high_purple or fluorescent_yellow or orange_red:
            risk_pixels += 1

    return risk_pixels / total >= 0.015


def thumbnail_size(size: tuple[int, int], max_side: int) -> tuple[int, int]:
    width, height = size
    if width <= 0 or height <= 0:
        return (1, 1)
    scale = min(max_side / max(width, height), 1)
    return (max(1, int(width * scale)), max(1, int(height * scale)))


def make_preview(
    original_image: Image.Image,
    cmyk_image: Image.Image,
    output_path: Path,
    source_name: str,
    cmyk_profile_path: Path | None,
) -> None:
    rgb_left = flatten_to_rgb(original_image)
    rgb_right = cmyk_preview_to_rgb(cmyk_image, cmyk_profile_path)

    target_size = thumbnail_size(rgb_left.size, PREVIEW_MAX_SIDE)
    left = ImageOps.contain(rgb_left, target_size, Image.Resampling.LANCZOS)
    right = ImageOps.contain(rgb_right, target_size, Image.Resampling.LANCZOS)

    panel_width = max(left.width, right.width)
    panel_height = max(left.height, right.height)
    label_height = 54
    padding = 18
    gap = 14

    canvas_width = panel_width * 2 + padding * 2 + gap
    canvas_height = panel_height + label_height + padding * 2
    canvas = Image.new("RGB", (canvas_width, canvas_height), (245, 245, 245))
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default()

    left_x = padding + (panel_width - left.width) // 2
    right_x = padding + panel_width + gap + (panel_width - right.width) // 2
    image_y = padding + label_height

    draw.rectangle((padding, image_y, padding + panel_width - 1, image_y + panel_height - 1), fill=(255, 255, 255))
    draw.rectangle(
        (padding + panel_width + gap, image_y, padding + panel_width * 2 + gap - 1, image_y + panel_height - 1),
        fill=(255, 255, 255),
    )
    canvas.paste(left, (left_x, image_y + (panel_height - left.height) // 2))
    canvas.paste(right, (right_x, image_y + (panel_height - right.height) // 2))

    draw.text((padding, padding), source_name, fill=(30, 30, 30), font=font)
    draw.text((padding, padding + 22), "RGB Original", fill=(20, 90, 180), font=font)
    draw.text((padding + panel_width + gap, padding + 22), "CMYK Preview", fill=(180, 70, 30), font=font)
    draw.line(
        (padding + panel_width + gap // 2, padding, padding + panel_width + gap // 2, canvas_height - padding),
        fill=(210, 210, 210),
        width=1,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output_path, "JPEG", quality=92)


def write_report(rows: list[dict[str, str]]) -> None:
    with REPORT_PATH.open("w", newline="", encoding="utf-8-sig") as report_file:
        writer = csv.DictWriter(report_file, fieldnames=REPORT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def output_path_for(path: Path, output_format: str) -> Path:
    extension = { "tiff": ".tif", "jpg": ".jpg", "png": ".png" }.get(output_format, ".tif")
    return unique_path(OUTPUT_DIR / f"{path.stem}_CMYK{extension}")


def save_output_image(image: Image.Image, output_path: Path, output_format: str, cmyk_profile_path: Path | None) -> None:
    if output_format == "jpg":
        save_kwargs = {"quality": OUTPUT_JPEG_QUALITY}
        if cmyk_profile_path:
            save_kwargs["icc_profile"] = cmyk_profile_path.read_bytes()
        image.save(output_path, "JPEG", **save_kwargs)
        return

    if output_format == "png":
        image.convert("RGB").save(output_path, "PNG", optimize=True)
        return

    save_kwargs = {"compression": "tiff_lzw"}
    if cmyk_profile_path:
        save_kwargs["icc_profile"] = cmyk_profile_path.read_bytes()
    image.save(output_path, "TIFF", **save_kwargs)


def process_image(
    path: Path,
    transform,
    cmyk_profile_path: Path | None,
    enable_dithering: bool = True,
    output_format: str = "tiff",
) -> dict[str, str]:
    row = {
        COL_FILE: path.name,
        COL_SOURCE: str(path),
        COL_MODE: "",
        COL_STATUS: STATUS_NO,
        COL_OUTPUT: "",
        COL_RISK: "",
        COL_ERROR: "",
    }

    try:
        backup_original(path)

        with open_image_for_processing(path) as image:
            original_mode = image.mode
            row[COL_MODE] = original_mode
            has_risk = detect_high_saturation_risk(image)
            row[COL_RISK] = RISK_CHECK if has_risk else STATUS_NO

            output_path = output_path_for(path, output_format)
            preview_path = unique_path(PREVIEW_DIR / f"{path.stem}_preview.jpg")

            if original_mode == "CMYK":
                cmyk_image = image.copy()
                row[COL_STATUS] = STATUS_SKIP
            else:
                cmyk_image = convert_rgb_to_cmyk(image, transform, enable_dithering)
                row[COL_STATUS] = STATUS_YES

            save_output_image(cmyk_image, output_path, output_format, cmyk_profile_path)
            make_preview(image, cmyk_image, preview_path, path.name, cmyk_profile_path)
            row[COL_OUTPUT] = str(output_path)

    except Exception as exc:
        row[COL_ERROR] = str(exc)
        logging.exception("Failed to process: %s", path)

    return row


def run_conversion(
    image_paths: Iterable[Path] | None = None,
    selected_cmyk_profile_path: Path | None = None,
    selected_profile_label: str | None = None,
    source_rgb_profile_path: Path | None = None,
    source_rgb_profile_label: str | None = None,
    rendering_intent: int = 1,
    enable_dithering: bool = True,
    output_format: str = "tiff",
) -> dict[str, object]:
    ensure_directories()
    setup_logging()

    cmyk_profile_path = selected_cmyk_profile_path or find_cmyk_icc_profile()
    transform = None
    icc_message = "\u672a\u4f7f\u7528\u5370\u5237\u5382ICC\uff0c\u4ec5\u4e3a\u901a\u7528\u8f6c\u6362"

    if cmyk_profile_path:
        try:
            transform = build_cmyk_transform(cmyk_profile_path, source_rgb_profile_path, rendering_intent)
            profile_name = selected_profile_label or cmyk_profile_path.name
            icc_message = f"\u5df2\u4f7f\u7528ICC: {profile_name}"
            if source_rgb_profile_label:
                icc_message += f" | Source RGB: {source_rgb_profile_label}"
            logging.info("Using ICC profile: %s", cmyk_profile_path.name)
        except Exception as exc:
            logging.warning("ICC transform failed; using generic CMYK conversion: %s", exc)
            cmyk_profile_path = None

    if not cmyk_profile_path:
        logging.warning("No print-shop ICC was used; generic CMYK conversion only.")

    paths = list(image_paths) if image_paths is not None else list(iter_images())
    rows: list[dict[str, str]] = []

    for image_path in paths:
        logging.info("Processing: %s", image_path.name)
        rows.append(process_image(image_path, transform, cmyk_profile_path, enable_dithering, output_format))

    write_report(rows)

    stats = {
        "total": len(rows),
        "converted": sum(1 for row in rows if row[COL_STATUS] == STATUS_YES),
        "skipped": sum(1 for row in rows if row[COL_STATUS] == STATUS_SKIP),
        "failed": sum(1 for row in rows if row[COL_STATUS] == STATUS_NO),
        "high_risk": sum(1 for row in rows if row[COL_RISK] == RISK_CHECK),
        "report_path": str(REPORT_PATH),
        "output_dir": str(OUTPUT_DIR),
        "icc_message": icc_message,
        "output_format": output_format,
        "enable_dithering": enable_dithering,
        "rows": rows,
    }
    return stats


def main() -> int:
    print("This project now uses the web uploader by default.")
    print("Opening the local web tool...")
    from web_app import main as web_main

    return web_main()


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

from pathlib import Path


SOURCE_RGB_PRESET_DIR = Path(__file__).resolve().parents[1] / "profiles" / "source_rgb" / "presets"
SOURCE_RGB_CUSTOM_DIR = Path(__file__).resolve().parents[1] / "profiles" / "source_rgb" / "custom"
DEFAULT_SOURCE_RGB_ID = "srgb_v4_icc_preference"


def source_profile(
    profile_id: str,
    name: str,
    filename: str | None,
    description: str,
    zh_description: str,
    standard: str,
    region: str,
) -> dict[str, str | None]:
    return {
        "id": profile_id,
        "name": name,
        "filename": filename,
        "description": description,
        "zh_description": zh_description,
        "standard": standard,
        "region": region,
    }


SOURCE_RGB_PROFILES = [
    source_profile(
        "srgb_v4_icc_preference",
        "sRGB v4 ICC Preference | sRGB v4 ICC \u9996\u9009\u9879",
        "sRGB_v4_ICC_preference.icc",
        "ICC v4 sRGB source profile recommended for modern color-managed workflows.",
        "\u63a8\u8350\u7528\u4e8e\u73b0\u4ee3\u8272\u5f69\u7ba1\u7406\u6d41\u7a0b\u7684 ICC v4 sRGB \u6e90\u914d\u7f6e\u6587\u4ef6\u3002",
        "ICC v4 sRGB",
        "International",
    ),
    source_profile(
        "srgb_v4_icc_preference_displayclass",
        "sRGB v4 ICC Preference Display Class | sRGB v4 ICC \u9996\u9009\u9879\u663e\u793a\u7c7b",
        "sRGB_v4_ICC_preference_displayclass.icc",
        "ICC v4 sRGB display-class profile.",
        "ICC v4 sRGB \u663e\u793a\u7c7b\u914d\u7f6e\u6587\u4ef6\u3002",
        "ICC v4 sRGB Display Class",
        "International",
    ),
    source_profile(
        "srgb_2014",
        "sRGB 2014 | sRGB 2014",
        "sRGB2014.icc",
        "ICC sRGB profile published in 2014.",
        "2014 \u5e74\u53d1\u5e03\u7684 ICC sRGB \u914d\u7f6e\u6587\u4ef6\u3002",
        "sRGB 2014",
        "International",
    ),
    source_profile("adobe_rgb_1998", "Adobe RGB (1998) | Adobe RGB (1998)", "AdobeRGB1998.icc", "Wide-gamut RGB working space from the Adobe ICC profile package.", "\u6765\u81ea Adobe ICC \u914d\u7f6e\u5305\u7684\u5e7f\u8272\u57df RGB \u5de5\u4f5c\u7a7a\u95f4\u3002", "Adobe RGB (1998)", "International"),
    source_profile("ecirgb_v2", "eciRGB v2 | eciRGB v2", "eciRGB_v2.icc", "European RGB working space from ECI.", "\u6765\u81ea ECI \u7684\u6b27\u6d32 RGB \u5de5\u4f5c\u7a7a\u95f4\u3002", "eciRGB v2", "Europe"),
    source_profile("ecirgb_v2_icc_v4", "eciRGB v2 (ICC v4) | eciRGB v2 (ICC v4)", "eciRGB_v2_ICCv4.icc", "ICC v4 edition of eCI RGB v2 from ECI.", "\u6765\u81ea ECI \u7684 eciRGB v2 ICC v4 \u7248\u672c\u3002", "eciRGB v2 ICC v4", "Europe"),
    source_profile("apple_rgb", "Apple RGB | \u82f9\u679c RGB", "AppleRGB.icc", "Legacy Apple RGB working space from the Adobe ICC profile package.", "\u6765\u81ea Adobe ICC \u914d\u7f6e\u5305\u7684\u65e7\u7248 Apple RGB \u5de5\u4f5c\u7a7a\u95f4\u3002", "Apple RGB", "International"),
    source_profile("colormatch_rgb", "ColorMatch RGB | ColorMatch RGB", "ColorMatchRGB.icc", "Legacy ColorMatch RGB working space from the Adobe ICC profile package.", "\u6765\u81ea Adobe ICC \u914d\u7f6e\u5305\u7684\u65e7\u7248 ColorMatch RGB \u5de5\u4f5c\u7a7a\u95f4\u3002", "ColorMatch RGB", "International"),
    source_profile("pal_secam", "PAL/SECAM | PAL/SECAM", "PAL_SECAM.icc", "PAL/SECAM video RGB profile from the Adobe ICC profile package.", "\u6765\u81ea Adobe ICC \u914d\u7f6e\u5305\u7684 PAL/SECAM \u89c6\u9891 RGB \u914d\u7f6e\u3002", "PAL/SECAM", "Europe"),
    source_profile("smpte_c", "SMPTE-C | SMPTE-C", "SMPTE-C.icc", "SMPTE-C video RGB profile from the Adobe ICC profile package.", "\u6765\u81ea Adobe ICC \u914d\u7f6e\u5305\u7684 SMPTE-C \u89c6\u9891 RGB \u914d\u7f6e\u3002", "SMPTE-C", "North America"),
    source_profile("rec_709", "HD Video (Rec. 709) | \u9ad8\u6e05\u89c6\u9891\uff08Rec. 709\uff09", "VideoHD.icc", "HD video RGB profile from the Adobe ICC profile package.", "\u6765\u81ea Adobe ICC \u914d\u7f6e\u5305\u7684\u9ad8\u6e05\u89c6\u9891 RGB \u914d\u7f6e\u3002", "Rec. 709", "International"),
    source_profile("ntsc", "Video NTSC | \u89c6\u9891 NTSC", "VideoNTSC.icc", "NTSC video RGB profile from the Adobe ICC profile package.", "\u6765\u81ea Adobe ICC \u914d\u7f6e\u5305\u7684 NTSC \u89c6\u9891 RGB \u914d\u7f6e\u3002", "NTSC", "North America"),
    source_profile("video_pal", "Video PAL | \u89c6\u9891 PAL", "VideoPAL.icc", "PAL video RGB profile from the Adobe ICC profile package.", "\u6765\u81ea Adobe ICC \u914d\u7f6e\u5305\u7684 PAL \u89c6\u9891 RGB \u914d\u7f6e\u3002", "PAL", "Europe"),
]


RENDERING_INTENTS = [
    {"id": "perceptual", "label": "Perceptual | \u611f\u77e5", "value": 0, "description": "Suitable for photos and images with many gradients.", "zh_description": "\u9002\u5408\u7167\u7247\u548c\u6e10\u53d8\u8f83\u591a\u7684\u56fe\u7247\u3002"},
    {"id": "relative_colorimetric", "label": "Relative Colorimetric | \u76f8\u5bf9\u6bd4\u8272\u6cd5", "value": 1, "description": "Recommended: relative for most images.", "zh_description": "\u63a8\u8350\uff1a\u9002\u7528\u4e8e\u5927\u591a\u6570\u56fe\u50cf\u3002"},
    {"id": "saturation", "label": "Saturation | \u9971\u548c", "value": 2, "description": "Prioritizes vivid color for charts and commercial graphics.", "zh_description": "\u4f18\u5148\u4fdd\u6301\u9c9c\u8273\u5ea6\uff0c\u9002\u5408\u56fe\u8868\u548c\u5546\u4e1a\u56fe\u5f62\u3002"},
    {"id": "absolute_colorimetric", "label": "Absolute Colorimetric | \u7edd\u5bf9\u6bd4\u8272\u6cd5", "value": 3, "description": "Preserves paper-white simulation, usually for proofing.", "zh_description": "\u4fdd\u7559\u7eb8\u767d\u6a21\u62df\uff0c\u901a\u5e38\u7528\u4e8e\u6253\u6837\u3002"},
]

OUTPUT_FORMATS = [
    {"id": "tiff", "label": "TIFF", "extension": ".tif", "description": "TIFF format provides the best printing results.", "zh_description": "TIFF \u683c\u5f0f\u901a\u5e38\u63d0\u4f9b\u66f4\u597d\u7684\u5370\u5237\u6548\u679c\u3002"},
    {"id": "jpg", "label": "JPG", "extension": ".jpg", "description": "JPG is smaller and convenient for review or delivery.", "zh_description": "JPG \u6587\u4ef6\u8f83\u5c0f\uff0c\u65b9\u4fbf\u9884\u89c8\u548c\u4f20\u8f93\u3002"},
    {"id": "png", "label": "PNG", "extension": ".png", "description": "PNG does not store CMYK in Pillow; output is an RGB preview file.", "zh_description": "PNG \u901a\u5e38\u4e0d\u4fdd\u5b58 CMYK\uff0c\u672c\u5de5\u5177\u4f1a\u8f93\u51fa RGB \u9884\u89c8\u56fe\u3002"},
]

DEFAULT_RENDERING_INTENT = "relative_colorimetric"
DEFAULT_DITHERING = True
DEFAULT_OUTPUT_FORMAT = "tiff"


def ensure_source_profile_dirs() -> None:
    SOURCE_RGB_PRESET_DIR.mkdir(parents=True, exist_ok=True)
    SOURCE_RGB_CUSTOM_DIR.mkdir(parents=True, exist_ok=True)


def source_profile_by_id(profile_id: str) -> dict[str, str | None] | None:
    for preset in SOURCE_RGB_PROFILES:
        if preset["id"] == profile_id:
            return preset
    return None


def resolve_source_profile_path(profile_id: str) -> Path | None:
    preset = source_profile_by_id(profile_id)
    if not preset or not preset.get("filename"):
        return None
    candidate = SOURCE_RGB_PRESET_DIR / str(preset["filename"])
    if candidate.exists():
        return candidate
    return None


def rendering_intent_value(intent_id: str) -> int:
    for item in RENDERING_INTENTS:
        if item["id"] == intent_id:
            return int(item["value"])
    return 1


def output_format_by_id(format_id: str) -> dict[str, str]:
    for item in OUTPUT_FORMATS:
        if item["id"] == format_id:
            return item
    return OUTPUT_FORMATS[0]

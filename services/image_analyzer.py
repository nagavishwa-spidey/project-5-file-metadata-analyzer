"""
Image analysis service.

Extracts image-specific metadata including dimensions, format, color mode,
EXIF data, and more. Uses the Pillow library for image processing.
"""

import io
from PIL import Image, ExifTags


def analyze_image(file_bytes: bytes) -> dict | None:
    """
    Analyze image file and extract metadata.

    Args:
        file_bytes: Raw bytes of the image file.

    Returns:
        Dictionary with image metadata, or None if the file is not a valid image.
        Keys include:
            - width: Image width in pixels
            - height: Image height in pixels
            - format: Image format (PNG, JPEG, etc.)
            - mode: Color mode (RGB, RGBA, L, etc.)
            - has_transparency: Whether the image supports transparency
            - color_depth: Bits per pixel estimate
            - dpi: Tuple of (x_dpi, y_dpi) or None
            - exif: Dictionary of EXIF data or None
    """
    try:
        img = Image.open(io.BytesIO(file_bytes))
    except Exception:
        return None

    result = {
        "width": img.width,
        "height": img.height,
        "format": img.format,
        "mode": img.mode,
        "has_transparency": img.mode in ("RGBA", "LA", "PA") or "transparency" in img.info,
        "color_depth": _get_color_depth(img.mode),
        "dpi": _get_dpi(img),
        "exif": _extract_exif(img),
    }

    return result


def _get_color_depth(mode: str) -> int:
    """
    Estimate color depth (bits per pixel) from image mode.

    Args:
        mode: PIL image mode string.

    Returns:
        Estimated bits per pixel.
    """
    depth_map = {
        "1": 1,
        "L": 8,
        "P": 8,
        "RGB": 24,
        "RGBA": 32,
        "CMYK": 32,
        "YCbCr": 24,
        "LAB": 24,
        "HSV": 24,
        "I": 32,
        "F": 32,
        "LA": 16,
        "PA": 16,
        "RGBa": 32,
        "LA": 16,
    }
    return depth_map.get(mode, 24)


def _get_dpi(img: Image.Image) -> tuple | None:
    """
    Extract DPI information from image.

    Args:
        img: PIL Image object.

    Returns:
        Tuple of (x_dpi, y_dpi) or None if not available.
    """
    try:
        dpi = img.info.get("dpi")
        if dpi:
            return (int(dpi[0]), int(dpi[1]))
    except (TypeError, IndexError, ValueError):
        pass
    return None


def _extract_exif(img: Image.Image) -> dict | None:
    """
    Extract EXIF metadata from image.

    Looks for common EXIF tags like camera model, date taken,
    GPS coordinates, and orientation.

    Args:
        img: PIL Image object.

    Returns:
        Dictionary of EXIF data or None if not available.
    """
    try:
        exif_data = img._getexif()
        if not exif_data:
            return None
    except (AttributeError, Exception):
        return None

    exif_result = {}

    # Map of tag IDs to human-readable names we care about
    interesting_tags = {
        "Make": "camera_make",
        "Model": "camera_model",
        "DateTime": "date_time",
        "DateTimeOriginal": "date_taken",
        "Orientation": "orientation",
        "ExposureTime": "exposure_time",
        "FNumber": "f_number",
        "ISOSpeedRatings": "iso",
        "FocalLength": "focal_length",
        "ImageWidth": "image_width",
        "ImageLength": "image_height",
        "Software": "software",
    }

    # Build reverse tag lookup
    tag_lookup = {v: k for k, v in ExifTags.TAGS.items()}

    for tag_name, result_key in interesting_tags.items():
        tag_id = tag_lookup.get(tag_name)
        if tag_id and tag_id in exif_data:
            value = exif_data[tag_id]
            # Convert to string for JSON serialization
            exif_result[result_key] = str(value)

    # Extract GPS data if available
    gps_tag_id = tag_lookup.get("GPSInfo")
    if gps_tag_id and gps_tag_id in exif_data:
        gps_data = exif_data[gps_tag_id]
        exif_result["has_gps"] = True
        try:
            gps_info = {}
            for key, val in gps_data.items():
                gps_tag_name = ExifTags.GPSTAGS.get(key, str(key))
                gps_info[gps_tag_name] = str(val)
            exif_result["gps_data"] = gps_info
        except Exception:
            exif_result["gps_data"] = None
    else:
        exif_result["has_gps"] = False

    return exif_result if exif_result else None

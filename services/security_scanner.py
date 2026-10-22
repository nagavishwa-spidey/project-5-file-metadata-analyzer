"""
Security scanning service.

Performs heuristic-based security checks on uploaded files to identify
potentially dangerous content. This mimics cloud-based security scanning
patterns used by cloud storage services.

NOTE: This is a basic heuristic scanner, NOT a real antivirus solution.
"""

import re

# Executable file extensions considered high risk
HIGH_RISK_EXTENSIONS = {
    ".exe", ".bat", ".cmd", ".sh", ".ps1", ".vbs", ".vbe",
    ".wsf", ".wsh", ".msi", ".scr", ".pif", ".com", ".hta",
}

# Extensions that are medium risk
MEDIUM_RISK_EXTENSIONS = {
    ".js", ".jar", ".py", ".rb", ".pl", ".php", ".dll",
    ".sys", ".reg", ".inf", ".lnk",
}

# Dangerous MIME types
DANGEROUS_MIME_TYPES = {
    "application/x-executable",
    "application/x-msdos-program",
    "application/x-msdownload",
    "application/x-dosexec",
    "application/x-bat",
    "application/x-sh",
    "application/x-shellscript",
    "application/vnd.microsoft.portable-executable",
}

# Maximum file size before warning (50 MB)
SUSPICIOUS_SIZE_THRESHOLD = 50 * 1024 * 1024

# Patterns that indicate embedded scripts
SCRIPT_PATTERNS = [
    re.compile(rb"<script[\s>]", re.IGNORECASE),
    re.compile(rb"javascript:", re.IGNORECASE),
    re.compile(rb"on\w+\s*=\s*[\"']", re.IGNORECASE),
    re.compile(rb"eval\s*\(", re.IGNORECASE),
]


def scan_file(file_bytes: bytes, filename: str, mime_type: str) -> dict:
    """
    Perform security scan on a file.

    Checks for dangerous file extensions, double extensions, dangerous
    MIME types, embedded scripts, and suspicious file sizes.

    Args:
        file_bytes: Raw bytes of the file.
        filename: Original filename.
        mime_type: Detected MIME type.

    Returns:
        Dictionary with scan results:
            - risk_level: 'safe', 'low', 'medium', or 'high'
            - warnings: List of warning strings
            - details: Dictionary with detailed scan results
    """
    warnings = []
    details = {
        "extension_check": "pass",
        "double_extension_check": "pass",
        "mime_type_check": "pass",
        "script_check": "pass",
        "size_check": "pass",
    }

    # Normalize filename
    filename_lower = filename.lower() if filename else ""

    # 1. Check for dangerous extensions
    ext_risk = _check_extension(filename_lower)
    if ext_risk == "high":
        warnings.append(f"Executable file extension detected: {_get_extension(filename_lower)}")
        details["extension_check"] = "high_risk"
    elif ext_risk == "medium":
        warnings.append(f"Potentially risky file extension: {_get_extension(filename_lower)}")
        details["extension_check"] = "medium_risk"

    # 2. Check for double extensions
    if _has_double_extension(filename_lower):
        warnings.append(f"Double extension detected in filename: {filename}")
        details["double_extension_check"] = "suspicious"

    # 3. Check MIME type
    if mime_type and mime_type.lower() in DANGEROUS_MIME_TYPES:
        warnings.append(f"Dangerous MIME type detected: {mime_type}")
        details["mime_type_check"] = "dangerous"

    # 4. Check for embedded scripts (in HTML/SVG files)
    if _is_markup_file(filename_lower, mime_type):
        script_findings = _check_for_scripts(file_bytes)
        if script_findings:
            warnings.extend(script_findings)
            details["script_check"] = "scripts_found"

    # 5. Check file size
    if len(file_bytes) > SUSPICIOUS_SIZE_THRESHOLD:
        warnings.append(
            f"File is unusually large: {len(file_bytes) / (1024 * 1024):.1f} MB"
        )
        details["size_check"] = "large_file"

    # Determine overall risk level
    risk_level = _calculate_risk_level(details)

    return {
        "risk_level": risk_level,
        "warnings": warnings,
        "details": details,
    }


def _get_extension(filename: str) -> str:
    """Extract the last extension from a filename."""
    if "." in filename:
        return "." + filename.rsplit(".", 1)[-1]
    return ""


def _check_extension(filename: str) -> str:
    """
    Check if a filename has a dangerous extension.

    Returns:
        'high', 'medium', or 'safe'.
    """
    ext = _get_extension(filename)
    if ext in HIGH_RISK_EXTENSIONS:
        return "high"
    if ext in MEDIUM_RISK_EXTENSIONS:
        return "medium"
    return "safe"


def _has_double_extension(filename: str) -> bool:
    """
    Check if a filename has a double extension pattern (e.g., file.pdf.exe).

    Returns:
        True if a double extension is detected.
    """
    parts = filename.rsplit("/", 1)[-1].rsplit("\\", 1)[-1]  # Get basename
    name_parts = parts.split(".")
    if len(name_parts) >= 3:
        # Check if the last extension is dangerous
        last_ext = "." + name_parts[-1]
        if last_ext in HIGH_RISK_EXTENSIONS or last_ext in MEDIUM_RISK_EXTENSIONS:
            return True
    return False


def _is_markup_file(filename: str, mime_type: str) -> bool:
    """Check if a file is HTML or SVG (could contain scripts)."""
    markup_extensions = {".html", ".htm", ".svg", ".xhtml", ".xml"}
    markup_mimes = {
        "text/html",
        "application/xhtml+xml",
        "image/svg+xml",
        "text/xml",
        "application/xml",
    }

    ext = _get_extension(filename)
    return ext in markup_extensions or (mime_type and mime_type.lower() in markup_mimes)


def _check_for_scripts(file_bytes: bytes) -> list:
    """
    Check file content for embedded script patterns.

    Returns:
        List of warning strings for each pattern found.
    """
    findings = []
    for pattern in SCRIPT_PATTERNS:
        if pattern.search(file_bytes):
            findings.append(f"Embedded script pattern found: {pattern.pattern.decode('utf-8', errors='replace')}")
            break  # One warning is enough for scripts
    return findings


def _calculate_risk_level(details: dict) -> str:
    """
    Calculate overall risk level from individual check details.

    Returns:
        'safe', 'low', 'medium', or 'high'.
    """
    values = list(details.values())

    if "high_risk" in values or "dangerous" in values:
        return "high"

    risk_count = 0
    if "medium_risk" in values:
        risk_count += 2
    if "suspicious" in values:
        risk_count += 2
    if "scripts_found" in values:
        risk_count += 1
    if "large_file" in values:
        risk_count += 1

    if risk_count >= 3:
        return "high"
    elif risk_count >= 2:
        return "medium"
    elif risk_count >= 1:
        return "low"

    return "safe"

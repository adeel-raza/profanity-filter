"""
Lightweight Intel GPU presence checks.

These helpers intentionally avoid importing OpenVINO / openvino-genai. Heavy
Intel packages are only loaded later, after a positive hardware hint (or an
explicit PROFANITY_FILTER_DEVICE=openvino override).
"""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path
from typing import Optional


INTEL_PCI_VENDOR = "0x8086"


def intel_gpu_hardware_hint() -> bool:
    """
    Cheap OS-level hint that an Intel GPU *might* be present.

    True does not guarantee OpenVINO can use it; False means we should not
    bother importing OpenVINO on this machine.
    """
    return bool(
        _linux_sysfs_intel_gpu()
        or _linux_lspci_intel_gpu()
        or _windows_intel_gpu()
    )


def describe_intel_gpu_hint() -> str:
    """Short human-readable reason for the hardware hint (for logs)."""
    sysfs = _linux_sysfs_intel_gpu_name()
    if sysfs:
        return f"sysfs:{sysfs}"
    lspci = _linux_lspci_intel_gpu_line()
    if lspci:
        return f"lspci:{lspci}"
    win = _windows_intel_gpu_name()
    if win:
        return f"windows:{win}"
    return "none"


def _linux_sysfs_intel_gpu() -> bool:
    return _linux_sysfs_intel_gpu_name() is not None


def _linux_sysfs_intel_gpu_name() -> Optional[str]:
    drm = Path("/sys/class/drm")
    if not drm.is_dir():
        return None
    for card in sorted(drm.glob("card[0-9]*")):
        if "-" in card.name:  # skip card0-DP-1 style connectors
            continue
        vendor = card / "device" / "vendor"
        try:
            if vendor.read_text().strip().lower() != INTEL_PCI_VENDOR:
                continue
        except OSError:
            continue
        # Skip nodes that are clearly not GPUs when possible.
        boot_vga = card / "device" / "boot_vga"
        class_file = card / "device" / "class"
        try:
            pci_class = class_file.read_text().strip().lower() if class_file.exists() else ""
        except OSError:
            pci_class = ""
        # Display controllers are 0x03xxxx
        if pci_class and not pci_class.startswith("0x03"):
            continue
        name = card.name
        try:
            if boot_vga.exists():
                name = f"{card.name}(boot_vga={boot_vga.read_text().strip()})"
        except OSError:
            pass
        return name
    return None


def _linux_lspci_intel_gpu() -> bool:
    return _linux_lspci_intel_gpu_line() is not None


def _linux_lspci_intel_gpu_line() -> Optional[str]:
    try:
        result = subprocess.run(
            ["lspci", "-nn"],
            capture_output=True,
            text=True,
            timeout=3,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0 or not result.stdout:
        return None
    pattern = re.compile(
        r"(VGA compatible controller|3D controller|Display controller).*Intel.*\[8086:",
        re.IGNORECASE,
    )
    for line in result.stdout.splitlines():
        if pattern.search(line):
            return line.strip()[:120]
    return None


def _windows_intel_gpu() -> bool:
    return _windows_intel_gpu_name() is not None


def _windows_intel_gpu_name() -> Optional[str]:
    if os.name != "nt":
        return None
    # PowerShell is commonly available; keep the query tiny and timed.
    ps = (
        "Get-CimInstance Win32_VideoController | "
        "Select-Object -ExpandProperty Name"
    )
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0 or not result.stdout:
        return None
    for line in result.stdout.splitlines():
        name = line.strip()
        if not name:
            continue
        lower = name.lower()
        if "intel" in lower and (
            "arc" in lower
            or "graphics" in lower
            or "uhd" in lower
            or "iris" in lower
            or "hd graphics" in lower
        ):
            return name[:120]
    return None

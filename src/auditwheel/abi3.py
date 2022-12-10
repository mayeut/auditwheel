from __future__ import annotations

import logging
import subprocess
import sys
from pathlib import Path

from packaging.utils import parse_wheel_filename


LOG = logging.getLogger(__name__)


class ABI3ViolationException(Exception):
    pass


def _check_abi3(filepath: str | Path, verbose: bool) -> None:
    filepath_ = Path(filepath)
    _, _, _, tags = parse_wheel_filename(filepath_.name)
    has_abi3 = any(tag.abi == "abi3" for tag in tags)
    if not has_abi3:
        return
    if sys.version_info[:2] < (3, 10):
        LOG.warning("abi3audit is not supported on Python < 3.10, skipping check")
        return
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "abi3audit",
            "--strict",
            "--verbose" if verbose else "",
            str(filepath),
        ]
    )
    if result.returncode == 0:
        return
    LOG.error("abi3audit returned in error, please check your package for abi3 violations")
    raise ABI3ViolationException()


def check_abi3(filepath: str | Path, fatal: bool, verbose: bool) -> None:
    try:
        _check_abi3(filepath, verbose)
    except ABI3ViolationException:
        if fatal:
            sys.exit(1)
        raise

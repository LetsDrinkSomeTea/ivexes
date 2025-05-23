"""
Functional Diff Tool

Entry point for comparing two source directories and extracting changed functions.
"""
import subprocess

import config.log

logger = config.log.get(__name__)


def diff(old_dir: str, new_dir: str) -> list[str]:
    """
    Compare two directories and extract changed functions using git diff.

    Args:
        old_dir: Path to the old directory to compare
        new_dir: Path to the new directory to compare

    Returns:
        A list of strings, each representing a file diff
    """

    cmd = [
        "git", "diff",
        "-W",  # function context
        "-w",  # ignore whitespaces
        "--no-index",  # to compare folders not commits
        old_dir, new_dir
    ]
    logger.info(f"Running: {" ".join(cmd)}")
    result = subprocess.run(cmd, stdout=subprocess.PIPE, text=True)
    files = result.stdout.split("diff --git ")[1:]
    logger.info(f'{len(files)} files altered')

    return files

"""Semantic Version Filtering for Django Release Breaking Changes.

Implements strict version interval comparisons using packaging.version:
    source_version < change_version <= target_version

Handles edge cases such as:
- Comparing '5.0' vs '4.10' properly without lexicographical string issues
- Cleaning version strings (e.g. '5.0b1', 'Django 5.0')
"""

from typing import Union
from packaging.version import parse as parse_version, Version, InvalidVersion


def normalize_version(ver: Union[str, float, int]) -> Version:
    """Safely converts a version identifier into a packaging.version.Version object."""
    ver_str = str(ver).strip()
    if ver_str.lower().startswith("django"):
        ver_str = ver_str.split()[-1]
    
    try:
        return parse_version(ver_str)
    except InvalidVersion:
        # Fallback for simple single-digit versions like '4' -> '4.0'
        return parse_version(f"{ver_str}.0")


def is_version_in_range(
    change_ver_str: str,
    from_ver_str: str,
    to_ver_str: str
) -> bool:
    """Checks if a change version falls within the migration interval:
    
        from_version < change_version <= to_version
        
    Example:
        is_version_in_range('5.0', '4.0', '5.1') -> True
        is_version_in_range('4.0', '4.0', '5.1') -> False (already supported in 4.0)
        is_version_in_range('5.2', '4.0', '5.1') -> False (beyond target)
    """
    try:
        change_v = normalize_version(change_ver_str)
        from_v = normalize_version(from_ver_str)
        to_v = normalize_version(to_ver_str)
        
        return from_v < change_v <= to_v
    except Exception:
        return False

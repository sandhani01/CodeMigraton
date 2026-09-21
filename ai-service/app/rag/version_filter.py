from typing import Union
from packaging.version import parse as parse_version, Version, InvalidVersion

def normalize_version(ver: Union[str, float, int]) -> Version:
    ver_str = str(ver).strip()
    if ver_str.lower().startswith("django"):
        ver_str = ver_str.split()[-1]
    
    try:
        return parse_version(ver_str)
    except InvalidVersion:
        return parse_version(f"{ver_str}.0")

def is_version_in_range(
    change_ver_str: str,
    from_ver_str: str,
    to_ver_str: str
) -> bool:
    try:
        change_v = normalize_version(change_ver_str)
        from_v = normalize_version(from_ver_str)
        to_v = normalize_version(to_ver_str)
        
        return from_v < change_v <= to_v
    except Exception:
        return False

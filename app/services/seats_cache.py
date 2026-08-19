import time
from typing import Dict, List, Optional, Tuple

_cache: Dict[str, Tuple[List[str], float]] = {}
_TTL_SECONDS = 30


def get(event_id: str) -> Optional[List[str]]:
    if event_id in _cache:
        data, cached_at = _cache[event_id]
        if time.time() - cached_at < _TTL_SECONDS:
            return data
    return None


def set(event_id: str, seats: List[str]) -> None:
    _cache[event_id] = (seats, time.time())
SECONDS_IN_MINUTE = 60

def parse_mmss_to_seconds(value: str | None) -> int | None:
    if not value:
        return None
    try:
        mm, ss = value.split(":", 1)
        return int(mm) * SECONDS_IN_MINUTE + int(ss)
    except Exception:
        return None
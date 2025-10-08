import time

def tick_ms() -> int:
    return int(time.monotonic() * 1000)
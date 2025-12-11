import time
import tracemalloc
from functools import wraps

def measure_time_and_memory(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        tracemalloc.start()
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        elapsed = end - start
        peak_mb = peak / (1024 * 1024)  # Convertir a MB
        return result, elapsed, peak_mb
    return wrapper

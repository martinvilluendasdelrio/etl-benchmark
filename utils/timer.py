# timer.py
import time
from functools import wraps

def measure_time(func):
    """
    Decorador para medir el tiempo de ejecución de una función.
    Devuelve una tupla (resultado_función, tiempo_segundos).
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        elapsed = end - start
        return result, elapsed

    return wrapper

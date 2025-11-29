# memory.py
import tracemalloc
from functools import wraps

def measure_memory(func):
    """
    Decorador para medir el consumo máximo de memoria de una función.
    Devuelve una tupla (resultado_función, memoria_MB).
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        tracemalloc.start()
        result = func(*args, **kwargs)
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        peak_mb = peak / (1024 * 1024)  # Convertir a MB
        return result, peak_mb

    return wrapper

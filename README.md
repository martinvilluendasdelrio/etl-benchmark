# ETL Benchmark Project

Este proyecto tiene como objetivo comparar distintas tecnologías para procesos ETL con Python, incluyendo **Pandas**, **Polars** y **PySpark**.  

El proyecto está pensado para:

- Aprender a trabajar con grandes volúmenes de datos.
- Evaluar rendimiento y facilidad de uso de diferentes librerías.
- Mantener un entorno limpio y reproducible para todos los scripts ETL.

---

## Estructura del proyecto

```
etl-benchmark/
│
├── .venv/                  # Entorno virtual (no subido a GitHub)
├── src/                    # Scripts ETL
│   ├── etl_pandas.py
│   ├── etl_polars.py
│   └── etl_pyspark.py
│
├── data/                   # Datasets de prueba
├── utils/                  # Funciones auxiliares
├── README.md
└── requirements.txt        # Dependencias del proyecto
```

---

## Configuración del entorno

1. Crear y activar el entorno virtual:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1   # PowerShell
```

2. Instalar dependencias:

```powershell
pip install -r requirements.txt
```

---

## Uso

Cada script de `src/` contiene un proceso ETL específico:

- `etl_pandas.py` → Procesos usando **Pandas**.  
- `etl_polars.py` → Procesos usando **Polars**.  
- `etl_pyspark.py` → Procesos usando **PySpark**.  

Puedes ejecutar cada script desde la terminal con el entorno virtual activado:

```powershell
python src/etl_pandas.py
```

---

## Contribuciones

Este proyecto es personal, pero se aceptan sugerencias y mejoras para el benchmark de ETL.

---

## Licencia

Libre uso, sin restricciones.

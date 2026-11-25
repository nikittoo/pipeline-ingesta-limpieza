"""Etapa de CARGA: guarda el resultado en formato Parquet."""
import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


def guardar_parquet(df: pd.DataFrame, ruta: Path) -> Path:
    """Exporta el DataFrame a Parquet y verifica leyéndolo de nuevo.

    Por qué Parquet para ML: es columnar (se leen solo las columnas necesarias), comprime
    bien, conserva los tipos (category, int, float) y se lee más rápido que un CSV.
    """
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(ruta, engine="pyarrow", index=False)

    comprobacion = pd.read_parquet(ruta)
    if comprobacion.shape != df.shape:
        raise ValueError("El Parquet guardado no coincide con los datos procesados.")
    logger.info("Guardado %s (%d filas, %.1f KB)", ruta.name, len(df), ruta.stat().st_size / 1024)
    return ruta
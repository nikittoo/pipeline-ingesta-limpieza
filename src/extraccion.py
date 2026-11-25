"""Etapa de EXTRACCIÓN: lee el CSV usando tipos de datos que ahorran memoria."""
import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

# Tipos explícitos para no dejar que pandas use int64 / float64 / object por defecto.
#  - category: texto con pocos valores distintos (se guarda una vez y se referencia con un número chico)
#  - int8 / int16 / float32: caben los valores y ocupan menos bytes que int64 / float64
#  - TotalCharges se lee como texto a propósito: el CSV original trae celdas con un espacio
#    en blanco, y si forzáramos un tipo numérico acá, la lectura fallaría. Se convierte en la transformación.
DTYPES = {
    "customerID": "string",
    "gender": "category",
    "SeniorCitizen": "int8",
    "Partner": "category",
    "Dependents": "category",
    "tenure": "int16",
    "PhoneService": "category",
    "MultipleLines": "category",
    "InternetService": "category",
    "OnlineSecurity": "category",
    "OnlineBackup": "category",
    "DeviceProtection": "category",
    "TechSupport": "category",
    "StreamingTV": "category",
    "StreamingMovies": "category",
    "Contract": "category",
    "PaperlessBilling": "category",
    "PaymentMethod": "category",
    "MonthlyCharges": "float32",
    "TotalCharges": "string",
    "Churn": "category",
}


def memoria_mb(df: pd.DataFrame) -> float:
    """Memoria total que ocupa el DataFrame, en megabytes."""
    return df.memory_usage(deep=True).sum() / 1024**2


def leer_csv(ruta: Path) -> pd.DataFrame:
    """Lee el CSV con tipos optimizados y muestra cuánta memoria se ahorra."""
    ruta = Path(ruta)
    if not ruta.exists():
        raise FileNotFoundError(
            f"No se encontró el dataset en '{ruta}'. Descargalo y guardalo ahí (ver README)."
        )

    df = pd.read_csv(ruta, dtype=DTYPES)
    df_defecto = pd.read_csv(ruta)  # solo para comparar la memoria
    logger.info(
        "Leído %s: %d filas x %d columnas | memoria: %.2f MB (tipos por defecto) -> %.2f MB (optimizado)",
        ruta.name, len(df), df.shape[1], memoria_mb(df_defecto), memoria_mb(df),
    )
    return df
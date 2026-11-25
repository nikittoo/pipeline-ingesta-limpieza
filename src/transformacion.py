"""Etapa de TRANSFORMACIÓN: nombres de columnas, duplicados y valores nulos."""
import logging
import re

import pandas as pd

logger = logging.getLogger(__name__)

COLUMNAS_NUMERICAS = ["tenure", "monthly_charges", "total_charges"]


def normalizar_nombres_columnas(df: pd.DataFrame) -> pd.DataFrame:
    """customerID -> customer_id, MonthlyCharges -> monthly_charges, StreamingTV -> streaming_tv."""
    def a_snake_case(nombre: str) -> str:
        nombre = re.sub(r"[\s\-]+", "_", nombre.strip())
        nombre = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", nombre)
        return nombre.lower()

    df = df.copy()
    df.columns = [a_snake_case(c) for c in df.columns]
    return df


def convertir_tipos(df: pd.DataFrame) -> pd.DataFrame:
    """total_charges llega como texto (con celdas vacías): se pasa a número; lo que no se pueda queda nulo."""
    df = df.copy()
    df["total_charges"] = pd.to_numeric(df["total_charges"], errors="coerce").astype("float32")
    return df


def eliminar_duplicados(df: pd.DataFrame) -> pd.DataFrame:
    """Quita filas idénticas y, además, clientes repetidos (un customer_id debe aparecer una sola vez)."""
    antes = len(df)
    df = df.drop_duplicates()
    exactos = antes - len(df)

    antes = len(df)
    df = df.drop_duplicates(subset="customer_id", keep="first")
    por_id = antes - len(df)

    logger.info("Duplicados eliminados: %d filas idénticas + %d por customer_id repetido", exactos, por_id)
    return df.reset_index(drop=True)


def manejar_nulos(df: pd.DataFrame) -> pd.DataFrame:
    """Trata los nulos columna por columna, con una regla justificada para cada caso."""
    df = df.copy()
    logger.info("Nulos antes: %s", {c: int(n) for c, n in df.isna().sum().items() if n})

    # 1) Sin identificador o sin etiqueta (churn) la fila no sirve: no se sabe de quién es o qué predecir.
    #    Inventar una etiqueta sería falsear el dato, por eso se descartan.
    antes = len(df)
    df = df.dropna(subset=["customer_id", "churn"])
    logger.info("Filas sin customer_id o sin churn descartadas: %d", antes - len(df))

    # 2) total_charges vacío con tenure == 0: cliente recién dado de alta, todavía no se le facturó nada -> 0.
    #    (Supuesto a verificar con el dataset real; ver README.)
    nuevos = df["total_charges"].isna() & (df["tenure"] == 0)
    df.loc[nuevos, "total_charges"] = 0.0
    logger.info("total_charges completado con 0 (clientes con tenure 0): %d", int(nuevos.sum()))

    # 3) Cualquier otro nulo numérico: mediana (robusta a valores extremos).
    for col in COLUMNAS_NUMERICAS:
        n = int(df[col].isna().sum())
        if n:
            df[col] = df[col].fillna(df[col].median())
            logger.info("%s: %d nulos completados con la mediana", col, n)

    # 4) Nulos en columnas categóricas: categoría explícita "Unknown" en lugar de borrar la fila.
    for col in df.select_dtypes(include="category").columns:
        if df[col].isna().any():
            if "Unknown" not in df[col].cat.categories:
                df[col] = df[col].cat.add_categories("Unknown")
            df[col] = df[col].fillna("Unknown")
            logger.info("%s: nulos completados con 'Unknown'", col)
    return df


def validar_resultado(df: pd.DataFrame) -> None:
    """Chequeo final: si queda algún nulo o duplicado, el pipeline se detiene."""
    if df.isna().any().any():
        raise ValueError("Quedaron valores nulos después de la limpieza.")
    if df.duplicated(subset="customer_id").any():
        raise ValueError("Quedaron customer_id duplicados después de la limpieza.")


def limpiar_datos(df: pd.DataFrame) -> pd.DataFrame:
    """Función principal de la etapa: encadena todos los pasos de limpieza."""
    filas_inicio = len(df)
    df = normalizar_nombres_columnas(df)
    df = convertir_tipos(df)
    df = eliminar_duplicados(df)
    df = manejar_nulos(df)
    validar_resultado(df)
    logger.info("Limpieza terminada: %d filas -> %d filas", filas_inicio, len(df))
    return df
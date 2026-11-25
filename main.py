"""Punto de entrada: ejecuta el pipeline completo (Extracción -> Transformación -> Carga)."""
import argparse
import logging
import sys
from pathlib import Path

from src.carga import guardar_parquet
from src.extraccion import leer_csv
from src.transformacion import limpiar_datos

BASE_DIR = Path(__file__).resolve().parent


def parsear_argumentos():
    parser = argparse.ArgumentParser(description="Pipeline de ingesta y limpieza (CSV -> Parquet).")
    parser.add_argument("--input", type=Path, default=BASE_DIR / "data" / "raw" / "telco_customer_churn.csv",
                        help="CSV de entrada")
    parser.add_argument("--output", type=Path, default=BASE_DIR / "data" / "processed" / "telco_churn_limpio.parquet",
                        help="Parquet de salida")
    return parser.parse_args()


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    args = parsear_argumentos()
    try:
        df = leer_csv(args.input)          # 1. Extracción
        df = limpiar_datos(df)             # 2. Transformación
        guardar_parquet(df, args.output)   # 3. Carga
    except (FileNotFoundError, ValueError) as e:
        logging.error(e)
        return 1
    logging.info("Pipeline finalizado correctamente.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
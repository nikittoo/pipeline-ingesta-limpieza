# Punto de entrada: ejecuta el pipeline completo (Extracción -> Transformación -> Carga) ETL.

import argparse
import logging #Libreria buena para mensajes de informacion, error, entre otros. Y permite configurar el nivel de detalle de los mensajes.
import sys
from pathlib import Path

from src.carga import guardar_parquet
from src.extraccion import leer_csv
from src.transformacion import limpiar_datos

BASE_DIR = Path(__file__).resolve().parent #convierte la ruta del archivo en un objeto Path y obtiene el directorio padre del archivo actual. No importa desde donde se ejecute.
#.resolve() obtiene la ruta absoluta del archivo actual, y .parent obtiene el directorio que contiene ese archivo.

def parsear_argumentos(): #funcion
    parser = argparse.ArgumentParser(description="Pipeline de ingesta y limpieza (CSV -> Parquet).")
    
    parser.add_argument("--input", type=Path, default=BASE_DIR / "data" / "raw" / "telco_customer_churn.csv", help="CSV de entrada")
    parser.add_argument("--output", type=Path, default=BASE_DIR / "data" / "processed" / "telco_churn_limpio.parquet", help="Parquet de salida")
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
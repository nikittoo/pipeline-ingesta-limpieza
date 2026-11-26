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
    lector = argparse.ArgumentParser(description="Pipeline de ingesta y limpieza (CSV -> Parquet).") #Mensaje cuando se pide ayuda con python main.py --help
    
    lector.add_argument("--input", type=Path, default=BASE_DIR / "data" / "raw" / "telco_customer_churn.csv", help="CSV de entrada") 
    # Linea para ejecutar un csv que no sea el por defecto, si ejecutamos python main.py ejecutamos el csv por defecto, si queremos ejecutar otro csv.
    # Lo hacemos con la linea de abajo, y el csv debe estar en la carpeta data/raw
    # Ejemplo: python main.py --input otro.csv

    lector.add_argument("--output", type=Path, default=BASE_DIR / "data" / "processed" / "telco_churn_limpio.parquet", help="Parquet de salida")
    
    return lector.parse_args() # devuelve el input del csv de entrada y el parquet de salida, que se guardan en args.input y args.output respectivamente.


def main() -> int: #Funcion que devuelve un entero, siendo 0 el que sale correctamente.
    
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s") #mensaje de log, nivel de detalle y formato del mensaje 
    
    args = parsear_argumentos() #aca se guardan los argumentos de entrada y salida, que se pasan a las funciones de extraccion, transformacion y carga.
    # args.input: ruta del csv de entrada
    # args.output: ruta del parquet de salida
    
    logging.info(f"Entrada: {args.input}, Salida: {args.output}")
    
    try:
        df = leer_csv(args.input)          # 1. Extracción
        df = limpiar_datos(df)             # 2. Transformación
        guardar_parquet(df, args.output)   # 3. Carga
    except (FileNotFoundError, ValueError) as error:
        logging.error(error)
        return 1
    logging.info("Pipeline finalizado correctamente.")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
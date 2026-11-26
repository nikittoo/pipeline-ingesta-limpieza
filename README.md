# Pipeline de ingesta y limpieza de datos (CSV -> Parquet)

Pipeline ETL (extraer, transformar y cargar) modular en Python que lee el dataset público **Telco Customer Churn** (clientes de una empresa de telecomunicaciones), lo limpia y lo guarda en formato **Parquet**, listo para usar en proyectos de Machine Learning.

## Qué hace

| Etapa | Módulo | Qué hace |
|---|---|---|
| **1. Extracción** | `src/extraccion.py` | Lee el CSV con tipos de datos optimizados (`category`, `int8`, `int16`, `float32`) para ahorrar memoria |
| **2. Transformación** | `src/transformacion.py` | Normaliza nombres de columnas, elimina duplicados, convierte tipos y trata los valores nulos con reglas justificadas |
| **3. Carga** | `src/carga.py` | Exporta el resultado a Parquet y lo verifica releyéndolo |

`main.py` es el punto de entrada: solo llama a las tres etapas en orden, con logging y manejo de errores.

## Estructura del repositorio

```
pipeline-ingesta-limpieza/
├── main.py                  # ejecuta el pipeline
├── src/
│   ├── __init__.py
│   ├── extraccion.py        # etapa 1: lectura con tipos optimizados
│   ├── transformacion.py    # etapa 2: limpieza
│   └── carga.py             # etapa 3: guardado en Parquet
├── data/
│   ├── raw/                 # acá va el CSV original (NO se sube a Git)
│   └── processed/           # acá se genera el Parquet
├── requirements.txt
├── .gitignore
└── README.md
```

## Instalación

Requiere Python 3.10 o superior.

```bash
# 1. Clonar el repositorio
git clone https://github.com/nikittoo/pipeline-ingesta-limpieza.git
cd pipeline-ingesta-limpieza

# 2. Crear el entorno virtual (una sola vez)
python -m venv .venv

# 3. Activar el entorno virtual
.venv\Scripts\activate           # Windows (PowerShell)
# source .venv/bin/activate      # macOS / Linux

# 4. Instalar las dependencias (una sola vez)
python -m pip install -r requirements.txt
```

**¿Cuáles de estos pasos se repiten?**

| Paso | Frecuencia |
|---|---|
| Crear el entorno (`python -m venv .venv`) | **Una sola vez** |
| Instalar dependencias (`pip install -r requirements.txt`) | **Una sola vez** (o de nuevo si cambia `requirements.txt`) |
| Activar el entorno (`.venv\Scripts\activate`) | **Cada vez que se abre una terminal nueva** |

El entorno y las librerías quedan guardados en la carpeta `.venv`; lo único que hay que repetir es la activación. Se sabe que está activo cuando aparece `(.venv)` al principio de la línea de la terminal.

## Dataset

El CSV original **no se incluye en el repositorio** (está en `.gitignore`). Para obtenerlo:

1. Descargá *Telco Customer Churn* desde una de estas fuentes:
   - Hugging Face: https://huggingface.co/datasets/scikit-learn/churn-prediction (pestaña *Files and versions* se encuentra uno que dice "dataset.csv" descargamos ese y lo guardamos en /data/raw/Nombre_del_csv)
2. Se guarda en la ruta `data/raw/telco_customer_churn.csv` recomendable usar ese nombre para el CSV.

Es un dataset de ejemplo de una empresa ficticia (IBM Sample Datasets): 7.043 clientes y 21 columnas, con la etiqueta `Churn` (si el cliente abandonó el servicio).

## Ejecución

Con el entorno activado y desde la raíz del proyecto:

```bash
python main.py
```

Opciones (todas con valor por defecto):

```bash
python main.py --input data/raw/telco_customer_churn.csv --output data/processed/telco_churn_limpio.parquet
python main.py --help
```

El resultado queda en `data/processed/telco_churn_limpio.parquet`. El programa termina con código `0` si todo salió bien y `1` si hubo un error (por ejemplo, si falta el CSV), mostrando un mensaje claro.

## Resultado de la ejecución

Con el dataset completo:

| Métrica | Valor |
|---|---|
| Filas leídas | 7.043 (21 columnas) |
| Memoria en pandas | 1,86 MB con tipos por defecto -> 0,37 MB optimizado (≈ 80 % menos) |
| Duplicados encontrados | 0 |
| Nulos encontrados | 11 (todos en `total_charges`) |
| Filas finales | 7.043 |
| Tamaño del Parquet | 185,8 KB (el CSV original pesa ≈ 974 KB) |

## Decisiones de limpieza

- **Nombres de columnas:** se pasan a `snake_case` (`customerID` -> `customer_id`, `MonthlyCharges` -> `monthly_charges`) para trabajar de forma consistente.
- **`total_charges` llega como texto:** el CSV trae celdas con un espacio en blanco. Se lee como texto y se convierte a número en la transformación, donde los vacíos pasan a nulos y se pueden tratar.
- **Nulos en `total_charges` -> 0:** las 11 filas con este valor vacío corresponden a clientes con `tenure = 0` (recién dados de alta, todavía sin facturar), por lo que el total acumulado real es 0. Se comprobó con el dataset real: los 11 casos cumplen esa condición.
- **Otras reglas de nulos (el dataset actual no las necesitó, pero el pipeline las contempla):**
  - Sin `customer_id` o sin `churn`: se descarta la fila (no se sabe de quién es ni qué predecir; inventar la etiqueta falsearía el dato).
  - Otros nulos numéricos: se completan con la mediana, que es robusta a valores extremos.
  - Nulos en columnas categóricas: se completan con la categoría `Unknown`.
- **Duplicados:** se eliminan las filas idénticas y los `customer_id` repetidos. (en este dataset no había ninguno)
- **Validación final:** si quedara algún nulo o duplicado, el pipeline se detiene con un error en lugar de guardar datos sucios.

## ¿Por qué Parquet?

- **Conserva los tipos de datos** (`category`, `int8`, `float32`): un CSV los pierde y hay que volver a convertirlos en cada lectura.
- **Es columnar:** permite leer solo las columnas que se necesitan, algo muy útil con muchas variables.
- **Comprime los datos:** en este proyecto pasó de ≈ 974 KB (CSV) a 185,8 KB.
- **Se lee más rápido** que un CSV, lo que importa cuando el volumen crece.

## ¿Por qué Pandas y no Dask?

El dataset es chico (7.043 filas, menos de 1 MB) y entra sin problemas en memoria. 
Dask, pensado para datos que no caben en una sola máquina, agregaría complejidad sin beneficio. 
Si el volumen creciera a millones de filas, se podría migrar a Dask o Polars sin cambiar la estructura de etapas.
Pero como el volumen es chico trabajamos con -> pandas.

## Limitaciones

- Las medianas usadas para completar nulos numéricos se calculan con todo el dataset. Si este resultado se usara luego para entrenar un modelo, lo correcto sería dividir primero en entrenamiento y prueba y calcular esos valores solo con el set de entrenamiento, para evitar *data leakage*.
- El pipeline está escrito para las columnas de este dataset (por ejemplo `customer_id`, `churn`, `tenure`); para otro dataset habría que adaptar los nombres y las reglas.

# Book Manager - Grupo 06

## Sprint Actual: Sprint 1

## Objetivo

Desarrollar una aplicación de consola (CLI) robusta en Python que permita gestionar el inventario de una librería, cotizar los libros en tiempo real según el valor del dólar y comparar precios automáticamente con la competencia web.

## Introducción y Contexto

Una librería con venta al público necesita modernizar su sistema de gestión de inventario de libros. Debido a la fluctuación en los costos de importación de material bibliográfico, el sistema debe gestionar precios en diferentes monedas y seguir de cerca la cotización del dólar para actualizar sus valores en tiempo real.

## Integrantes

- Mattias Daniel Peralta Fernandez
- Solange Galaz
- Sebastian Fuentes

## Estructura del Proyecto

```
book_manager/
├── src/
│   └── book_manager/
│       ├── entities/          # Clases de dominio
│       ├── repositories/      # Persistencia de datos (CRUD)
│       ├── services/          # Lógica de negocio
│       ├── preload_data/      # Carga inicial de datos
│       ├── migrations/csv/    # Datos CSV iniciales
│       ├── ui/                # Interfaz de consola
│       └── main.py            # Punto de entrada
├── CHANGELOG.md
├── README.md
└── requirements.txt
```

## Ejecución

```bash
cd src
python -m book_manager.main
```

## Repositorio

https://github.com/MperaltaX/Book_Manager-Grupo_06
## Persistencia y bajas

Las altas, modificaciones y bajas se guardan automáticamente en los CSV de
`data/`. Al reiniciar se recuperan los cambios. Los CSV de `migrations/csv/`
son la precarga inicial; no sobrescriben los datos de trabajo. Los IDs eliminados
no se reutilizan. La carpeta `data/` se crea al iniciar y no se sube a Git.

La llamada del notebook `main(import_default_data=False)` se conserva: carga
los datos iniciales cuando no existe estado previo y recupera el estado guardado
en las siguientes ejecuciones. `True` tiene el mismo comportamiento de inicio;
ninguno vuelve a cargar registros eliminados ni sobrescribe modificaciones.
Los ocho CSV de `src/book_manager/migrations/csv/` deben estar en el repositorio,
incluido `cotizaciones.csv`.

Antes de una baja se muestran los registros afectados y se pide confirmación.
Enter o `n` cancelan; `s` confirma y elimina también todas las dependencias:

- Género o editorial: sus libros, precios y stock.
- Libro: sus precios y stock.
- Moneda: los precios expresados en ella.
- Tipo de cotización: sus cotizaciones.

Los importes deben ser finitos y no negativos. NaN, infinito y valores negativos
se rechazan sin guardar ni anunciar éxito. En consola se admite punto o coma
como separador decimal.

Requiere Python 3.10 o posterior. Usar una instancia por carpeta de datos.
Las cotizaciones de este sprint se cargan manualmente; la consulta automática
en tiempo real forma parte de la evolución del proyecto.

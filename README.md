# Book Manager — Grupo 06

**Sprint 1 · Versión 1.1.0 · 30/09/2026**

## Objetivo

Aplicar programación orientada a objetos para gestionar el inventario de una
librería, conservando las entidades y sus cambios en archivos CSV.

## Introducción y contexto

Una librería necesita administrar libros, géneros, editoriales, monedas, precios,
existencias y cotizaciones históricas. Este sprint entrega una aplicación de
consola con CRUD de las ocho entidades, carga inicial validada, persistencia y
bajas confirmadas en cascada.

La cotización automática en tiempo real y la comparación con sitios de la
competencia forman parte de la evolución del proyecto. En esta versión las
cotizaciones se administran manualmente; no se consulta una API externa.

## Integrantes

- Mattias Daniel Peralta Fernandez
- Solange Galaz
- Sebastian Fuentes

Repositorio del grupo: https://github.com/MperaltaX/Book_Manager-Grupo_06
Rama de trabajo: `Sprint_1`. El ZIP contiene la versión corregida; los cambios
deben incorporarse al repositorio del grupo para que el modo GitHub del notebook
recupere esa misma versión.

## Inicio rápido

Requiere **Python 3.10 o posterior** y su biblioteca estándar.

1. Extraer el ZIP en una carpeta de trabajo.
2. Abrir una terminal en esa carpeta.
3. Ejecutar:

```bash
python iniciar.py
```

También funciona el comando original:

```bash
cd src
python -m book_manager.main
```

El sistema prepara los datos iniciales al abrir una carpeta nueva. A partir de
allí, cada alta, modificación y baja se guarda automáticamente. Al salir y
volver a abrir se recupera el estado vigente.

Para elegir otra carpeta de datos:

```bash
python iniciar.py --datos ./mis_datos
```

Para iniciar una carpeta nueva vacía:

```bash
python iniciar.py --datos ./datos_vacios --sin-precarga
```

`--sin-precarga` conserva los datos cuando la carpeta ya está inicializada.
La variable `BOOK_MANAGER_DATA_DIR` permite configurar la ruta al usar `main()`.
Utilizar una instancia de la aplicación por carpeta de datos. Esta entrega es
una CLI local; no implementa edición concurrente entre varios procesos.

## Persistencia

- `src/book_manager/migrations/csv/`: semillas de datos versionadas.
- `data/`: CSV de trabajo, creados durante el primer inicio.
- `data/secuencias.csv`: último ID utilizado por cada entidad con ID.
- `data/.transaccion.json`: diario temporal para recuperar una operación
  interrumpida; desaparece al completarla.

Hay ocho CSV de entidades y un CSV de secuencias. Los IDs no se reutilizan al
borrar el último registro, al vaciar una entidad ni al reiniciar. Stock se
identifica por libro; Cotización, por tipo y fecha.

Una carpeta existente vacía por operaciones del usuario sigue vacía al abrirla.
Los CSV incompletos o inválidos generan un diagnóstico y se conservan para
revisión. Los datos iniciales se incorporan sólo cuando no existe estado previo.

Se escribe primero un archivo temporal y luego se reemplaza el archivo de
trabajo. Una cascada agrupa todos sus archivos en una transacción: ante un error
se restaura el estado anterior; al reiniciar se recupera una interrupción usando
el diario. Para respaldar el inventario, cerrar la aplicación y copiar la carpeta
completa de datos, incluyendo `secuencias.csv`.

## Política de bajas

Todas las bajas de la consola muestran el registro, los tipos y la cantidad de
registros afectados. La pregunta predeterminada es **No**:

```text
¿Continuar y eliminar todos los registros indicados? [s/N]:
```

- Enter, `n` o `no`: se cancela y se conservan los datos.
- `s`, `si` o `sí`: se elimina todo el conjunto indicado.
- Una respuesta distinta vuelve a solicitar confirmación.

| Entidad elegida | Dependientes eliminados al confirmar |
|---|---|
| Género | Sus libros y los precios/stock de esos libros |
| Editorial | Sus libros y los precios/stock de esos libros |
| Libro | Sus precios y su stock |
| Moneda | Los precios expresados en esa moneda |
| Tipo de cotización | Todas sus cotizaciones históricas |
| Precio | Sólo ese precio |
| Stock | Sólo ese registro de stock |
| Cotización | Sólo esa cotización por tipo y fecha |

Borrar una moneda conserva los libros y su stock. Borrar una editorial conserva
los géneros y las otras editoriales. La API de servicios exige
`confirmar_cascada=True` cuando existen dependientes; una llamada directa al
repositorio tampoco puede dejar relaciones huérfanas.

## Validaciones

- IDs positivos y cantidades enteras no negativas; se rechazan booleanos.
- Texto obligatorio no vacío; códigos de moneda normalizados a mayúsculas.
- Importes finitos y no negativos: se rechazan NaN, infinito y negativos en
  entidades, servicios, importaciones y consola. Cero es un valor permitido.
- Punto o coma decimal en consola, sin separadores de miles.
- Referencias existentes en todas las entidades relacionadas.
- ISBN único, código de moneda único y un precio vigente por libro/moneda.
- Un stock por libro y una cotización por tipo/fecha.
- Identidades inmutables y lecturas que reconstruyen objetos independientes.

Los ISBN de la precarga son datos de demostración. Se valida texto y unicidad;
esta versión no verifica el dígito de control ni consulta ediciones reales.
Los importes conservan `float`, como en la versión inicial.

En edición, Enter conserva un valor; las claves de Stock y Cotización se
mantienen y se modifican sus atributos editables.

## Notebook

`Copia_de_01_Book_Manager_Grupo_XX.ipynb` conserva la plantilla y sus consignas,
completa los integrantes y la URL y agrega explicación y código por ejercicio.

El modo predeterminado `ORIGEN = "incluido"` reconstruye el proyecto de esta
versión desde una copia integrada en el propio notebook. Permite ejecutar todo
sin token, descarga externa ni ingreso manual durante las demostraciones. El
notebook conserva la comprobación opcional por GitHub en `ORIGEN = "github"`.

La demostración recorre la consola de las ocho entidades, comenzando por Libro.
Utiliza una carpeta temporal para que la repetición no altere el inventario de
trabajo. Otras demostraciones comprueban reinicio, bajas y validación de importes.
La consola interactiva se habilita al cambiar
`EJECUTAR_CONSOLA_INTERACTIVA = True` en su celda.

La versión incluida fue ejecutada localmente, celda por celda en orden con una
sesión de Python nueva. La autenticación de Google Colab y el estado actual del
repositorio remoto no se verificaron desde esta entrega. Antes de presentar en
el aula, ejecutar también **Restart session and run all** en Colab y confirmar
los accesos docentes requeridos por la consigna.

## Pruebas

Desde la raíz del proyecto:

```bash
python -m unittest discover -s tests -v
```

**62 pruebas automatizadas**, incluyendo recorridos de las ocho entidades,
persistencia entre procesos, cascadas, cancelación, integridad, secuencias,
importes inválidos y fallos de escritura. Ver `VALIDACION.md` y
`tests/resultados.json` para la evidencia de esta versión.

## Estructura

```text
Book_Manager-Grupo_06-Sprint_1/
├── iniciar.py
├── Copia_de_01_Book_Manager_Grupo_XX.ipynb
├── src/book_manager/
│   ├── entities/entities.py
│   ├── repositories/almacen_csv.py
│   ├── repositories/repositories.py
│   ├── services/bajas.py
│   ├── services/services.py
│   ├── preload_data/preload_data.py
│   ├── migrations/csv/
│   ├── ui/console.py
│   └── main.py
├── data/
├── tests/test_sistema.py
├── tests/resultados.json
├── CHANGELOG.md
├── VALIDACION.md
├── README.md
└── requirements.txt
```

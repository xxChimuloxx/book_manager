# Changelog

## [Ejercicio 07] - Versión 1.1.0 - 2026-09-30
- Creación de `crear_sistema()` para abrir el estado persistido y de `iniciar.py`.
- Configuración de la carpeta de datos y recuperación al volver a abrir.
- Notebook de la plantilla actualizado y ejecutado en orden con demostraciones.
- Incorporación de 62 pruebas automatizadas y evidencia de validación.

## [Ejercicio 06] - Versión 1.1.0 - 2026-09-30
- Confirmación de todas las bajas con resumen de los registros afectados.
- Cancelación predeterminada y cascada completa al responder afirmativamente.
- Edición con Enter para conservar valores y listados directos de las entidades.
- Rechazo de NaN, infinito y negativos en los ingresos de importes.
- Corrección de mensajes y simplificación de los recorridos repetidos de consola.

## [Ejercicio 05] - Versión 1.1.0 - 2026-09-30
- Moneda ampliada a diez registros; todas las entidades cumplen el mínimo.
- Precarga única y validada de todo el conjunto, sin cargas parciales.
- Las semillas no sobrescriben los datos modificados ni reaparecen tras las bajas.

## [Ejercicio 04] - Versión 1.1.0 - 2026-09-30
- Planes de bajas para géneros, editoriales, libros, monedas y tipos.
- Aplicación de cascadas en una transacción, con validación de las relaciones.
- Identificación de todos los dependientes y protección de la API de servicios.

## [Ejercicio 03] - Versión 1.1.0 - 2026-09-30
- Repositorios CRUD con almacenamiento CSV y objetos independientes al leer.
- Escritura temporal, reemplazo y recuperación mediante diario de transacción.
- Secuencias persistentes para evitar reutilizar IDs eliminados.
- Validación de integridad incluso en operaciones directas de repositorios.

## [Ejercicio 02] - Versión 1.1.0 - 2026-09-30
- Validación de importes finitos y no negativos en Precio y CotizacionDolar.
- Identidades inmutables, booleanos rechazados y fechas normalizadas.
- Validaciones de texto e integridad/unicidad al persistir las entidades.

## [Ejercicio 01] - Versión 1.1.0 - 2026-09-30
- README actualizado con alcance, ejecución, datos y política de eliminación.
- Preparación del notebook ordenada, con proyecto incluido y modo GitHub opcional.
- Las versiones posteriores de IDs y UI visibles en el historial inicial se
  incorporan a la documentación mediante esta revisión.

## Historial de la versión inicial

## [Ejercicio 07] - Main
- Creación del archivo main.py como punto de entrada del sistema.
- Función main() con parámetro import_default_data para control de carga inicial.

## [Ejercicio 06] - Interfaz de Consola
- Implementación de la clase ConsolaUI con menú interactivo.
- Submenús CRUD para cada entidad del sistema.
- Validación de entrada de usuario con manejo de excepciones.

## [Ejercicio 05] - Datos Iniciales
- Creación de archivos CSV con datos sintéticos para todas las entidades.
- Implementación del módulo preload_data para carga desde CSV.
- Datos iniciales de las ocho entidades; el mínimo de Moneda se completa en v1.1.0.

## [Ejercicio 04] - Servicios
- Implementación de la capa de servicios con lógica de negocio.
- Validaciones cruzadas entre entidades (editorial, género, libro, etc.).

## [Ejercicio 03] - Repositorios
- Implementación de interfaces IRepositorio, IRepositorioStock, IRepositorioCotizacionDolar.
- Repositorios en memoria con CRUD completo para todas las entidades.

## [Ejercicio 02] - Entidades
- Definición de clases: EntidadBase, Genero, Editorial, Moneda, TipoCotizacion, Libro, Precio, Stock, CotizacionDolar.
- Encapsulamiento con properties y validaciones.
- Type hints y docstrings en todas las clases.

## [Ejercicio 01] - Inicialización
- Creación de la estructura de directorios del proyecto.
- Inicialización del repositorio Git.
- Creación de la rama Sprint_1.
- Configuración de README.md y CHANGELOG.md.

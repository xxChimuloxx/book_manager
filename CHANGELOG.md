# Changelog

## Versión 1.1.0 - Correcciones de Sprint 1

- Persistencia real en CSV para las ocho entidades, con recuperación al reiniciar.
- IDs persistentes y precarga inicial sin sobrescribir cambios posteriores.
- Bajas con confirmación y eliminación coherente de los registros dependientes.
- Validación de precios y cotizaciones: rechazo de negativos, NaN e infinito.
- Ampliación de la precarga de monedas a diez registros.
- Restauración de los saltos de línea para limpiar los menús de consola.

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
- Mínimo de 10 registros por entidad.

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

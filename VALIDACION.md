# Validación — Book Manager v1.1.0

Fecha: 30/09/2026. Entorno local: Python 3.12.14, Linux.

## Pruebas automatizadas

Comando desde la raíz del proyecto:

```bash
python -m unittest discover -s tests -v
```

Resultado: **62 pruebas aprobadas; cero fallos y cero errores**.
Las pruebas utilizan carpetas temporales y pueden repetirse sin modificar el
inventario de trabajo. El listado individual está en `tests/resultados.json`.

Se verificaron:

- Alta, lectura, modificación y baja persistidas de las ocho entidades.
- Recuperación al reiniciar y desde un proceso Python independiente.
- Precarga inicial única y conservación de estados vacíos por bajas.
- Confirmación, cancelación y cascadas completas de las entidades relacionadas.
- Conservación de entidades no dependientes durante una cascada.
- IDs que no se reutilizan después de eliminar o volver a abrir.
- Rechazo de importes no finitos, negativos y tipos inválidos.
- Coma decimal, edición con Enter y listados completos de stock/cotizaciones.
- Referencias existentes, claves únicas y protección de identidades.
- Escritura fallida a mitad de una cascada con restauración de todos los CSV.
- Recuperación de transacciones pendientes y confirmadas al volver a abrir.
- Diagnóstico de CSV inválidos, carpeta incompleta e importaciones inconsistentes.
- Inicio desde `iniciar.py`, desde `src` y salida por EOF.

## Notebook y entrega

El notebook conserva las consignas y agrega demostraciones programadas de las
ocho entidades, comenzando por Libro, y comprobaciones de persistencia, bajas e
importes. Sus celdas Python se ejecutan en orden en una sesión local nueva y las
salidas se guardan en el archivo entregado. Los recorridos de consola usan
entradas programadas para permitir una ejecución completa sin intervención.

El modo predeterminado utiliza una copia integrada de este proyecto. La consola
interactiva puede habilitarse desde la celda indicada. El modo opcional GitHub
requiere que la versión esté publicada en la rama Sprint_1.

No se validó la autenticación de Google Colab ni se modificó el repositorio
remoto. Antes de la entrega académica corresponde ejecutar también el notebook
en Colab y verificar los accesos docentes establecidos en la consigna.

## Alcance

CLI local con una instancia por carpeta. Las cotizaciones se gestionan
manualmente. Se conserva el uso de flotantes para importes y se valida que sean
finitos y no negativos; no se implementa un servicio externo de cotización ni
verificación de ediciones reales de ISBN.

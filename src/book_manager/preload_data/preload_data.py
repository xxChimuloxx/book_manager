"""Carga inicial validada para una carpeta de datos nueva."""

from __future__ import annotations

from pathlib import Path

from book_manager.repositories.almacen_csv import (
    AlmacenCSV, ESQUEMAS, leer_csv,
)


def obtener_ruta_csv(nombre_archivo: str) -> str:
    base = Path(__file__).resolve().parents[1] / "migrations" / "csv"
    return str(base / nombre_archivo)


def cargar_todos_los_datos(
    almacen: AlmacenCSV, cargar_semillas: bool = True
) -> None:
    """Inicializa todos los archivos juntos y conserva estados existentes.

    Una carpeta inicializada, incluso vacía por bajas del usuario, no vuelve
    a importar semillas. Una carga inválida no deja altas parciales.
    """
    if almacen.inicializado:
        return
    with almacen.transaccion():
        for nombre, (_, campos) in ESQUEMAS.items():
            filas = (
                leer_csv(Path(obtener_ruta_csv(f"{nombre}.csv")), campos)
                if cargar_semillas else []
            )
            almacen.reemplazar(nombre, filas)

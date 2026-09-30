"""Construcción del sistema y ejecución de la consola."""

from __future__ import annotations

import os
from pathlib import Path

from book_manager.preload_data.preload_data import cargar_todos_los_datos
from book_manager.repositories.almacen_csv import AlmacenCSV
from book_manager.repositories.repositories import (
    RepositorioCotizacionDolar, RepositorioEditorial, RepositorioGenero,
    RepositorioLibro, RepositorioMoneda, RepositorioPrecio, RepositorioStock,
    RepositorioTipoCotizacion,
)
from book_manager.services.services import (
    ServicioCotizacionDolar, ServicioEditorial, ServicioGenero, ServicioLibro,
    ServicioMoneda, ServicioPrecio, ServicioStock, ServicioTipoCotizacion,
)
from book_manager.ui.console import ConsolaUI


def crear_sistema(
    import_default_data: bool = True, data_dir: str | Path | None = None
) -> ConsolaUI:
    """Recupera datos; importa semillas sólo en el primer inicio."""
    if data_dir is None:
        data_dir = os.environ.get("BOOK_MANAGER_DATA_DIR") or (
            Path(__file__).resolve().parents[2] / "data"
        )
    almacen = AlmacenCSV(data_dir)
    cargar_todos_los_datos(almacen, cargar_semillas=import_default_data)
    genero = RepositorioGenero(almacen)
    editorial = RepositorioEditorial(almacen)
    moneda = RepositorioMoneda(almacen)
    tipo = RepositorioTipoCotizacion(almacen)
    libro = RepositorioLibro(almacen)
    precio = RepositorioPrecio(almacen)
    stock = RepositorioStock(almacen)
    cotizacion = RepositorioCotizacionDolar(almacen)
    return ConsolaUI(
        ServicioGenero(genero), ServicioEditorial(editorial),
        ServicioMoneda(moneda), ServicioTipoCotizacion(tipo),
        ServicioLibro(libro, editorial, genero),
        ServicioPrecio(precio, libro, moneda), ServicioStock(stock, libro),
        ServicioCotizacionDolar(cotizacion, tipo),
    )


def main(
    import_default_data: bool = True, data_dir: str | Path | None = None
) -> None:
    """Inicia con semillas si no hay estado previo; luego restaura los CSV.

    import_default_data se conserva por compatibilidad con el notebook fijo.
    Incluso con False, el primer inicio carga las semillas. Un estado ya
    inicializado, aunque quede vacío por bajas, nunca se vuelve a precargar.
    """
    try:
        consola = crear_sistema(data_dir=data_dir)
        print("Datos listos. Cada cambio se guarda automáticamente en CSV.")
        consola.ejecutar()
    except (EOFError, KeyboardInterrupt):
        print(
            "\nSesión finalizada. Los cambios confirmados ya están guardados.",
        )


if __name__ == "__main__":
    main()

"""Ejecutar desde la raíz: python iniciar.py."""

from pathlib import Path
import argparse
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from book_manager.main import main


def iniciar() -> None:
    parser = argparse.ArgumentParser(description="Book Manager - Grupo 06")
    parser.add_argument(
        "--datos",
        help="Carpeta de datos; por defecto, data/.",
    )
    parser.add_argument(
        "--sin-precarga", action="store_true",
        help="Inicializa vacía una carpeta nueva; conserva los datos existentes.",
    )
    argumentos = parser.parse_args()
    try:
        main(not argumentos.sin_precarga, argumentos.datos)
    except (ValueError, OSError) as error:
        print(f"No se pudo iniciar el sistema: {error}", file=sys.stderr)
        raise SystemExit(1) from error


if __name__ == "__main__":
    iniciar()

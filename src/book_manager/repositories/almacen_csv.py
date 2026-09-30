"""CSV con validación de relaciones y transacciones recuperables."""

from __future__ import annotations

import copy
import csv
import datetime
import io
import json
import os
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from book_manager.entities.entities import (
    CotizacionDolar, Editorial, Entidad, Genero, Libro, Moneda,
    Precio, Stock, TipoCotizacion,
)


ESQUEMAS: dict[str, tuple[type[Entidad], tuple[str, ...]]] = {
    "generos": (Genero, ("id", "nombre")),
    "editoriales": (Editorial, ("id", "nombre", "pais")),
    "monedas": (Moneda, ("id", "codigo", "nombre", "simbolo")),
    "tipos_cotizacion": (TipoCotizacion, ("id", "nombre", "descripcion")),
    "libros": (Libro, (
        "id", "isbn", "titulo", "autor", "editorial_id", "genero_id",
        "anio_publicacion",
    )),
    "precios": (Precio, ("id", "libro_id", "moneda_id", "monto")),
    "stock": (Stock, ("libro_id", "cantidad", "ubicacion")),
    "cotizaciones": (CotizacionDolar, (
        "tipo_cotizacion_id", "fecha", "valor_compra", "valor_venta",
    )),
}
TABLAS_CON_ID = tuple(
    nombre for nombre, (_, campos) in ESQUEMAS.items() if "id" in campos
)
CAMPOS_ENTEROS = {
    "id", "libro_id", "editorial_id", "genero_id", "moneda_id",
    "tipo_cotizacion_id", "anio_publicacion", "cantidad",
}
CAMPOS_IMPORTES = {"monto", "valor_compra", "valor_venta"}
Clave = int | tuple[int, datetime.date]
Fila = dict[str, str]


def decodificar(nombre: str, fila: Fila) -> Entidad:
    """Reconstruye y valida una entidad a partir de una fila CSV."""
    tipo, campos = ESQUEMAS[nombre]
    argumentos = {}
    for campo in campos:
        valor = fila[campo]
        if campo in CAMPOS_ENTEROS:
            argumentos[campo] = int(valor)
        elif campo in CAMPOS_IMPORTES:
            argumentos[campo] = float(valor)
        elif campo == "fecha":
            argumentos[campo] = datetime.date.fromisoformat(valor)
        else:
            argumentos[campo] = valor
    return tipo(**argumentos)


def codificar(nombre: str, entidad: Entidad) -> Fila:
    """Usa los nombres del esquema, evitando guardar atributos privados."""
    tipo, campos = ESQUEMAS[nombre]
    if not isinstance(entidad, tipo):
        raise ValueError(f"{nombre} requiere objetos {tipo.__name__}.")
    fila = {}
    for campo in campos:
        valor = getattr(entidad, campo)
        fila[campo] = (
            valor.isoformat()
            if isinstance(valor, datetime.date) else str(valor)
        )
    return fila


def clave_fila(nombre: str, fila: Fila) -> Clave:
    if nombre == "stock":
        return int(fila["libro_id"])
    if nombre == "cotizaciones":
        return (
            int(fila["tipo_cotizacion_id"]),
            datetime.date.fromisoformat(fila["fecha"]),
        )
    return int(fila["id"])


def leer_csv(ruta: Path, campos: tuple[str, ...]) -> list[Fila]:
    """Exige encabezado completo y diagnostica el archivo y la fila."""
    with ruta.open("r", encoding="utf-8-sig", newline="") as archivo:
        lector = csv.DictReader(archivo)
        if lector.fieldnames != list(campos):
            raise ValueError(
                f"{ruta.name}: encabezado inválido; "
                f"se esperaba {', '.join(campos)}."
            )
        filas = []
        for numero, fila in enumerate(lector, 2):
            if None in fila or any(valor is None for valor in fila.values()):
                raise ValueError(
                    f"{ruta.name}, fila {numero}: columnas incompletas.",
                )
            filas.append(fila)
        return filas


def texto_csv(campos: tuple[str, ...], filas: list[Fila]) -> str:
    salida = io.StringIO(newline="")
    escritor = csv.DictWriter(salida, fieldnames=campos, lineterminator="\n")
    escritor.writeheader()
    escritor.writerows(filas)
    return salida.getvalue()


def escribir_atomico(ruta: Path, contenido: str) -> None:
    """Reemplaza el archivo después de completar la escritura temporal."""
    descriptor, temporal = tempfile.mkstemp(
        dir=ruta.parent, prefix=f".{ruta.name}.", suffix=".tmp"
    )
    try:
        with os.fdopen(
            descriptor,
            "w",
            encoding="utf-8",
            newline="",
        ) as archivo:
            archivo.write(contenido)
            archivo.flush()
            os.fsync(archivo.fileno())
        os.replace(temporal, ruta)
    finally:
        Path(temporal).unlink(missing_ok=True)


class AlmacenCSV:
    """Una carpeta de datos compartida por los ocho repositorios.

    Las operaciones modifican una copia del estado y se confirman juntas.
    El diario temporal permite recuperar una interrupción entre archivos.
    Se utiliza una instancia de la aplicación por carpeta de datos.
    """

    def __init__(self, directorio: str | Path) -> None:
        self.directorio = Path(directorio).resolve()
        self.directorio.mkdir(parents=True, exist_ok=True)
        self._diario = self.directorio / ".transaccion.json"
        self._tablas: dict[str, list[Fila]] = {
            nombre: [] for nombre in ESQUEMAS
        }
        self._secuencias = {nombre: 0 for nombre in TABLAS_CON_ID}
        self._profundidad = 0
        self._recuperar()
        nombres = [f"{nombre}.csv" for nombre in ESQUEMAS] + ["secuencias.csv"]
        presentes = [n for n in nombres if (self.directorio / n).exists()]
        self.inicializado = bool(presentes)
        if presentes and len(presentes) != len(nombres):
            faltantes = sorted(set(nombres) - set(presentes))
            raise ValueError(
                "Carpeta de datos incompleta; faltan: " + ", ".join(faltantes)
            )
        if self.inicializado:
            for nombre, (_, campos) in ESQUEMAS.items():
                self._tablas[nombre] = leer_csv(
                    self.directorio / f"{nombre}.csv", campos
                )
            secuencias = leer_csv(
                self.directorio / "secuencias.csv", ("entidad", "ultimo_id")
            )
            if (
                len(secuencias) != len(TABLAS_CON_ID)
                or {fila["entidad"] for fila in secuencias}
                != set(TABLAS_CON_ID)
            ):
                raise ValueError(
                    "secuencias.csv contiene entidades inválidas.",
                )
            try:
                self._secuencias = {
                    fila["entidad"]: int(fila["ultimo_id"])
                    for fila in secuencias
                }
            except ValueError as error:
                raise ValueError(
                    "secuencias.csv contiene IDs inválidos.",
                ) from error
            self.validar()

    def filas(self, nombre: str) -> list[Fila]:
        """Devuelve copias: una lectura no puede cambiar el almacenamiento."""
        return copy.deepcopy(self._tablas[nombre])

    def proximo_id(self, nombre: str) -> int:
        return self._secuencias[nombre] + 1

    def reemplazar(self, nombre: str, filas: list[Fila]) -> None:
        """La confirmación se hace al cerrar la transacción exterior."""
        if not self._profundidad:
            raise RuntimeError("Modificar CSV requiere una transacción.")
        self._tablas[nombre] = copy.deepcopy(filas)
        if nombre in TABLAS_CON_ID:
            mayor = max((int(fila["id"]) for fila in filas), default=0)
            self._secuencias[nombre] = max(self._secuencias[nombre], mayor)

    @contextmanager
    def transaccion(self) -> Iterator[None]:
        """Revierte la memoria si la validación o el guardado fallan."""
        exterior = self._profundidad == 0
        anterior = (
            copy.deepcopy(self._tablas), self._secuencias.copy(),
            self.inicializado,
        ) if exterior else None
        self._profundidad += 1
        try:
            yield
            if exterior:
                self.validar()
                self._guardar()
                self.inicializado = True
        except BaseException:
            if exterior and anterior is not None:
                self._tablas, self._secuencias, self.inicializado = anterior
            raise
        finally:
            self._profundidad -= 1

    def validar(self) -> None:
        """Comprueba valores, unicidad y relaciones de todas las tablas."""
        objetos: dict[str, list[Entidad]] = {}
        for nombre, filas in self._tablas.items():
            claves = set()
            objetos[nombre] = []
            for numero, fila in enumerate(filas, 2):
                try:
                    entidad = decodificar(nombre, fila)
                    clave = clave_fila(nombre, fila)
                    if clave in claves:
                        raise ValueError(f"clave repetida: {clave}")
                    claves.add(clave)
                    objetos[nombre].append(entidad)
                except (
                    ValueError,
                    TypeError,
                    KeyError,
                    OverflowError,
                ) as error:
                    raise ValueError(
                        f"{nombre}.csv, fila {numero}: {error}"
                    ) from error
            if nombre in TABLAS_CON_ID:
                mayor = max((int(fila["id"]) for fila in filas), default=0)
                if (
                    self._secuencias[nombre] < mayor
                    or self._secuencias[nombre] < 0
                ):
                    raise ValueError(f"Secuencia inválida para {nombre}.")

        ids = {
            nombre: {int(fila["id"]) for fila in self._tablas[nombre]}
            for nombre in TABLAS_CON_ID
        }
        relaciones = (
            ("libros", "genero_id", "generos"),
            ("libros", "editorial_id", "editoriales"),
            ("precios", "libro_id", "libros"),
            ("precios", "moneda_id", "monedas"),
            ("stock", "libro_id", "libros"),
            ("cotizaciones", "tipo_cotizacion_id", "tipos_cotizacion"),
        )
        for origen, campo, destino in relaciones:
            for fila in self._tablas[origen]:
                if int(fila[campo]) not in ids[destino]:
                    raise ValueError(
                        f"{origen}.csv: {campo}={fila[campo]} "
                        f"no existe en {destino}."
                    )
        self._validar_unicos(objetos["libros"], ("isbn",), "ISBN")
        self._validar_unicos(
            objetos["monedas"],
            ("codigo",),
            "Código de moneda",
        )
        self._validar_unicos(
            objetos["precios"], ("libro_id", "moneda_id"),
            "Precio vigente para libro y moneda",
        )

    @staticmethod
    def _validar_unicos(
        objetos: list[Entidad], campos: tuple[str, ...], etiqueta: str
    ) -> None:
        vistos = set()
        for entidad in objetos:
            clave = tuple(getattr(entidad, campo) for campo in campos)
            if clave in vistos:
                raise ValueError(f"{etiqueta} duplicado: {clave}.")
            vistos.add(clave)

    def _guardar(self) -> None:
        nuevos = {
            f"{nombre}.csv": texto_csv(ESQUEMAS[nombre][1], filas)
            for nombre, filas in self._tablas.items()
        }
        nuevos["secuencias.csv"] = texto_csv(
            ("entidad", "ultimo_id"),
            [
                {"entidad": nombre, "ultimo_id": str(valor)}
                for nombre, valor in self._secuencias.items()
            ],
        )
        cambios = {}
        for nombre, contenido in nuevos.items():
            ruta = self.directorio / nombre
            anterior = ruta.read_text(
                encoding="utf-8",
            ) if ruta.exists() else None
            if anterior != contenido:
                cambios[nombre] = {"anterior": anterior, "nuevo": contenido}
        if not cambios:
            return
        diario = {"estado": "pendiente", "archivos": cambios}
        escribir_atomico(self._diario, json.dumps(diario, ensure_ascii=False))
        try:
            for nombre, versiones in cambios.items():
                escribir_atomico(self.directorio / nombre, versiones["nuevo"])
            diario["estado"] = "confirmada"
            escribir_atomico(
                self._diario,
                json.dumps(diario, ensure_ascii=False),
            )
        except BaseException:
            self._recuperar()
            raise
        # Una confirmación ya escrita se recuperará aunque falle la limpieza.
        try:
            self._diario.unlink()
        except OSError:
            pass

    def _recuperar(self) -> None:
        if not self._diario.exists():
            return
        try:
            diario = json.loads(self._diario.read_text(encoding="utf-8"))
            estado = diario["estado"]
            archivos = diario["archivos"]
            permitidos = {f"{n}.csv" for n in ESQUEMAS} | {"secuencias.csv"}
            if estado not in {"pendiente", "confirmada"}:
                raise ValueError("estado desconocido")
            if not isinstance(archivos, dict) or not archivos:
                raise ValueError("archivos inválidos")
            if set(archivos) - permitidos:
                raise ValueError("archivo fuera del esquema")
            for versiones in archivos.values():
                if not isinstance(versiones["nuevo"], str):
                    raise ValueError("versión nueva inválida")
                if versiones["anterior"] is not None and not isinstance(
                    versiones["anterior"], str
                ):
                    raise ValueError("versión anterior inválida")
        except (ValueError, TypeError, KeyError) as error:
            raise ValueError(
                "Diario de recuperación inválido; "
                "conservar la carpeta para revisar."
            ) from error
        for nombre, versiones in archivos.items():
            contenido = versiones[
                "nuevo" if estado == "confirmada" else "anterior"
            ]
            ruta = self.directorio / nombre
            if contenido is None:
                ruta.unlink(missing_ok=True)
            else:
                escribir_atomico(ruta, contenido)
        self._diario.unlink()

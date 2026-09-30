"""Interfaces CRUD y repositorios respaldados por el almacén CSV."""

from __future__ import annotations

import abc
import datetime
from typing import Generic, TypeVar, cast

from book_manager.entities.entities import (
    CotizacionDolar, Editorial, EntidadBase, Genero, Libro, Moneda,
    Precio, Stock, TipoCotizacion,
)
from book_manager.repositories.almacen_csv import (
    AlmacenCSV, Clave, clave_fila, codificar, decodificar,
)

T = TypeVar("T", bound=EntidadBase)


class IRepositorio(abc.ABC, Generic[T]):
    """CRUD para entidades con ID y una secuencia del almacenamiento."""

    @abc.abstractmethod
    def crear(self, entidad: T) -> T:
        pass

    @abc.abstractmethod
    def leer_por_id(self, id: int) -> T | None:
        pass

    @abc.abstractmethod
    def leer_todos(self) -> list[T]:
        pass

    @abc.abstractmethod
    def actualizar(self, entidad: T) -> T:
        pass

    @abc.abstractmethod
    def eliminar(self, id: int) -> bool:
        pass

    @abc.abstractmethod
    def proximo_id(self) -> int:
        pass


class IRepositorioStock(abc.ABC):
    """Contrato para existencias, cuya clave es el libro."""

    @abc.abstractmethod
    def crear(self, stock: Stock) -> Stock:
        pass

    @abc.abstractmethod
    def leer_por_libro(self, libro_id: int) -> Stock | None:
        pass

    @abc.abstractmethod
    def leer_todos(self) -> list[Stock]:
        pass

    @abc.abstractmethod
    def actualizar(self, stock: Stock) -> Stock:
        pass

    @abc.abstractmethod
    def eliminar(self, libro_id: int) -> bool:
        pass


class IRepositorioCotizacionDolar(abc.ABC):
    """Contrato para cotizaciones con clave compuesta de tipo y fecha."""

    @abc.abstractmethod
    def crear(self, cotizacion: CotizacionDolar) -> CotizacionDolar:
        pass

    @abc.abstractmethod
    def leer_por_tipo_y_fecha(
        self, tipo_id: int, fecha: datetime.date
    ) -> CotizacionDolar | None:
        pass

    @abc.abstractmethod
    def leer_historico_por_tipo(self, tipo_id: int) -> list[CotizacionDolar]:
        pass

    @abc.abstractmethod
    def leer_todos(self) -> list[CotizacionDolar]:
        pass

    @abc.abstractmethod
    def actualizar(self, cotizacion: CotizacionDolar) -> CotizacionDolar:
        pass

    @abc.abstractmethod
    def eliminar(self, tipo_id: int, fecha: datetime.date) -> bool:
        pass


class RepositorioCSV(IRepositorio[T]):
    """CRUD genérico: reconstruye objetos y confirma cambios en archivos."""

    nombre: str

    def __init__(self, almacen: AlmacenCSV) -> None:
        self.almacen = almacen

    def proximo_id(self) -> int:
        return self.almacen.proximo_id(self.nombre)

    def crear(self, entidad: T) -> T:
        if self.leer_por_id(entidad.id) is not None:
            raise ValueError(f"Ya existe el ID {entidad.id} en {self.nombre}.")
        if entidad.id < self.proximo_id():
            raise ValueError("El ID ya fue utilizado; solicitar un ID nuevo.")
        fila = codificar(self.nombre, entidad)
        with self.almacen.transaccion():
            filas = self.almacen.filas(self.nombre)
            filas.append(fila)
            self.almacen.reemplazar(self.nombre, filas)
        return cast(T, decodificar(self.nombre, fila))

    def leer_por_id(self, id: int) -> T | None:
        for fila in self.almacen.filas(self.nombre):
            if int(fila["id"]) == id:
                return cast(T, decodificar(self.nombre, fila))
        return None

    def leer_todos(self) -> list[T]:
        return [
            cast(T, decodificar(self.nombre, fila))
            for fila in self.almacen.filas(self.nombre)
        ]

    def actualizar(self, entidad: T) -> T:
        fila_nueva = codificar(self.nombre, entidad)
        with self.almacen.transaccion():
            filas = self.almacen.filas(self.nombre)
            for posicion, fila in enumerate(filas):
                if int(fila["id"]) == entidad.id:
                    filas[posicion] = fila_nueva
                    self.almacen.reemplazar(self.nombre, filas)
                    break
            else:
                raise ValueError(
                    f"No existe el ID {entidad.id} en {self.nombre}.",
                )
        return cast(T, decodificar(self.nombre, fila_nueva))

    def eliminar(self, id: int) -> bool:
        return eliminar_clave(self.almacen, self.nombre, id)


class RepositorioGenero(RepositorioCSV[Genero]):
    nombre = "generos"


class RepositorioEditorial(RepositorioCSV[Editorial]):
    nombre = "editoriales"


class RepositorioMoneda(RepositorioCSV[Moneda]):
    nombre = "monedas"


class RepositorioTipoCotizacion(RepositorioCSV[TipoCotizacion]):
    nombre = "tipos_cotizacion"


class RepositorioLibro(RepositorioCSV[Libro]):
    nombre = "libros"


class RepositorioPrecio(RepositorioCSV[Precio]):
    nombre = "precios"


def eliminar_clave(almacen: AlmacenCSV, nombre: str, clave: Clave) -> bool:
    filas = almacen.filas(nombre)
    restantes = [fila for fila in filas if clave_fila(nombre, fila) != clave]
    if len(restantes) == len(filas):
        return False
    with almacen.transaccion():
        almacen.reemplazar(nombre, restantes)
    return True


class RepositorioStock(IRepositorioStock):
    """Un registro de stock por libro, conservado en stock.csv."""

    nombre = "stock"

    def __init__(self, almacen: AlmacenCSV) -> None:
        self.almacen = almacen

    def crear(self, stock: Stock) -> Stock:
        if self.leer_por_libro(stock.libro_id) is not None:
            raise ValueError(f"Ya existe stock del libro {stock.libro_id}.")
        fila = codificar(self.nombre, stock)
        with self.almacen.transaccion():
            filas = self.almacen.filas(self.nombre)
            filas.append(fila)
            self.almacen.reemplazar(self.nombre, filas)
        return cast(Stock, decodificar(self.nombre, fila))

    def leer_por_libro(self, libro_id: int) -> Stock | None:
        for fila in self.almacen.filas(self.nombre):
            if int(fila["libro_id"]) == libro_id:
                return cast(Stock, decodificar(self.nombre, fila))
        return None

    def leer_todos(self) -> list[Stock]:
        return [
            cast(Stock, decodificar(self.nombre, fila))
            for fila in self.almacen.filas(self.nombre)
        ]

    def actualizar(self, stock: Stock) -> Stock:
        fila_nueva = codificar(self.nombre, stock)
        with self.almacen.transaccion():
            filas = self.almacen.filas(self.nombre)
            for posicion, fila in enumerate(filas):
                if int(fila["libro_id"]) == stock.libro_id:
                    filas[posicion] = fila_nueva
                    self.almacen.reemplazar(self.nombre, filas)
                    break
            else:
                raise ValueError(
                    f"No existe stock del libro {stock.libro_id}.",
                )
        return cast(Stock, decodificar(self.nombre, fila_nueva))

    def eliminar(self, libro_id: int) -> bool:
        return eliminar_clave(self.almacen, self.nombre, libro_id)


class RepositorioCotizacionDolar(IRepositorioCotizacionDolar):
    """Histórico CSV con una cotización por tipo y fecha."""

    nombre = "cotizaciones"

    def __init__(self, almacen: AlmacenCSV) -> None:
        self.almacen = almacen

    def crear(self, cotizacion: CotizacionDolar) -> CotizacionDolar:
        clave = (cotizacion.tipo_cotizacion_id, cotizacion.fecha)
        if self.leer_por_tipo_y_fecha(*clave) is not None:
            raise ValueError("Ya existe una cotización para ese tipo y fecha.")
        fila = codificar(self.nombre, cotizacion)
        with self.almacen.transaccion():
            filas = self.almacen.filas(self.nombre)
            filas.append(fila)
            self.almacen.reemplazar(self.nombre, filas)
        return cast(CotizacionDolar, decodificar(self.nombre, fila))

    def leer_por_tipo_y_fecha(
        self, tipo_id: int, fecha: datetime.date
    ) -> CotizacionDolar | None:
        for fila in self.almacen.filas(self.nombre):
            if clave_fila(self.nombre, fila) == (tipo_id, fecha):
                return cast(CotizacionDolar, decodificar(self.nombre, fila))
        return None

    def leer_todos(self) -> list[CotizacionDolar]:
        return [
            cast(CotizacionDolar, decodificar(self.nombre, fila))
            for fila in self.almacen.filas(self.nombre)
        ]

    def leer_historico_por_tipo(self, tipo_id: int) -> list[CotizacionDolar]:
        return sorted(
            [c for c in self.leer_todos() if c.tipo_cotizacion_id == tipo_id],
            key=lambda cotizacion: cotizacion.fecha,
        )

    def actualizar(self, cotizacion: CotizacionDolar) -> CotizacionDolar:
        clave = (cotizacion.tipo_cotizacion_id, cotizacion.fecha)
        fila_nueva = codificar(self.nombre, cotizacion)
        with self.almacen.transaccion():
            filas = self.almacen.filas(self.nombre)
            for posicion, fila in enumerate(filas):
                if clave_fila(self.nombre, fila) == clave:
                    filas[posicion] = fila_nueva
                    self.almacen.reemplazar(self.nombre, filas)
                    break
            else:
                raise ValueError(
                    "No existe una cotización para ese tipo y fecha.",
                )
        return cast(CotizacionDolar, decodificar(self.nombre, fila_nueva))

    def eliminar(self, tipo_id: int, fecha: datetime.date) -> bool:
        return eliminar_clave(self.almacen, self.nombre, (tipo_id, fecha))

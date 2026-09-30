from __future__ import annotations
import datetime

from book_manager.entities.entities import validar_entero, validar_fecha
from book_manager.services.bajas import PlanBaja, ServicioBajas
from typing import List, Optional

from book_manager.entities.entities import (
    Genero, Editorial, Moneda, TipoCotizacion,
    Libro, Precio, Stock, CotizacionDolar
)
from book_manager.repositories.repositories import (
    RepositorioGenero, RepositorioEditorial, RepositorioMoneda,
    RepositorioTipoCotizacion, RepositorioLibro, RepositorioPrecio,
    RepositorioStock, RepositorioCotizacionDolar
)


class ServicioBase:
    """Lectura del plan y baja protegida, comunes a todas las entidades."""

    def planificar_baja(self, id: int) -> PlanBaja | None:
        validar_entero(id, "id", 1)
        return ServicioBajas(self.repositorio.almacen).planificar(
            self.repositorio.nombre, id
        )

    def eliminar(self, id: int, confirmar_cascada: bool = False) -> bool:
        validar_entero(id, "id", 1)
        return ServicioBajas(self.repositorio.almacen).eliminar(
            self.repositorio.nombre, id, confirmar_cascada
        )


class ServicioGenero(ServicioBase):
    """Servicio para la entidad Genero."""
    def __init__(self, repositorio: RepositorioGenero) -> None:
        self.repositorio = repositorio

    def crear(self, nombre: str) -> Genero:
        nuevo_id = self.repositorio.proximo_id()
        genero = Genero(id=nuevo_id, nombre=nombre)
        return self.repositorio.crear(genero)

    def leer_por_id(self, id: int) -> Optional[Genero]:
        return self.repositorio.leer_por_id(id)

    def leer_todos(self) -> List[Genero]:
        return self.repositorio.leer_todos()

    def actualizar(self, id: int, nombre: str) -> Genero:
        genero = Genero(id=id, nombre=nombre)
        return self.repositorio.actualizar(genero)


class ServicioEditorial(ServicioBase):
    """Servicio para la entidad Editorial."""
    def __init__(self, repositorio: RepositorioEditorial) -> None:
        self.repositorio = repositorio

    def crear(self, nombre: str, pais: str) -> Editorial:
        nuevo_id = self.repositorio.proximo_id()
        editorial = Editorial(id=nuevo_id, nombre=nombre, pais=pais)
        return self.repositorio.crear(editorial)

    def leer_por_id(self, id: int) -> Optional[Editorial]:
        return self.repositorio.leer_por_id(id)

    def leer_todos(self) -> List[Editorial]:
        return self.repositorio.leer_todos()

    def actualizar(self, id: int, nombre: str, pais: str) -> Editorial:
        editorial = Editorial(id=id, nombre=nombre, pais=pais)
        return self.repositorio.actualizar(editorial)


class ServicioMoneda(ServicioBase):
    """Servicio para la entidad Moneda."""
    def __init__(self, repositorio: RepositorioMoneda) -> None:
        self.repositorio = repositorio

    def crear(self, codigo: str, nombre: str, simbolo: str) -> Moneda:
        nuevo_id = self.repositorio.proximo_id()
        moneda = Moneda(
            id=nuevo_id,
            codigo=codigo,
            nombre=nombre,
            simbolo=simbolo,
        )
        return self.repositorio.crear(moneda)

    def leer_por_id(self, id: int) -> Optional[Moneda]:
        return self.repositorio.leer_por_id(id)

    def leer_todos(self) -> List[Moneda]:
        return self.repositorio.leer_todos()

    def actualizar(
        self,
        id: int,
        codigo: str,
        nombre: str,
        simbolo: str,
    ) -> Moneda:
        moneda = Moneda(id=id, codigo=codigo, nombre=nombre, simbolo=simbolo)
        return self.repositorio.actualizar(moneda)


class ServicioTipoCotizacion(ServicioBase):
    """Servicio para la entidad TipoCotizacion."""
    def __init__(self, repositorio: RepositorioTipoCotizacion) -> None:
        self.repositorio = repositorio

    def crear(self, nombre: str, descripcion: str) -> TipoCotizacion:
        nuevo_id = self.repositorio.proximo_id()
        tipo = TipoCotizacion(
            id=nuevo_id,
            nombre=nombre,
            descripcion=descripcion,
        )
        return self.repositorio.crear(tipo)

    def leer_por_id(self, id: int) -> Optional[TipoCotizacion]:
        return self.repositorio.leer_por_id(id)

    def leer_todos(self) -> List[TipoCotizacion]:
        return self.repositorio.leer_todos()

    def actualizar(
        self,
        id: int,
        nombre: str,
        descripcion: str,
    ) -> TipoCotizacion:
        tipo = TipoCotizacion(id=id, nombre=nombre, descripcion=descripcion)
        return self.repositorio.actualizar(tipo)


class ServicioLibro(ServicioBase):
    """Servicio para la entidad Libro."""
    def __init__(
        self,
        repositorio: RepositorioLibro,
        repo_editorial: RepositorioEditorial,
        repo_genero: RepositorioGenero,
    ) -> None:
        self.repositorio = repositorio
        self.repo_editorial = repo_editorial
        self.repo_genero = repo_genero

    def crear(
        self,
        isbn: str,
        titulo: str,
        autor: str,
        editorial_id: int,
        genero_id: int,
        anio_publicacion: int,
    ) -> Libro:
        if not self.repo_editorial.leer_por_id(editorial_id):
            raise ValueError(f"Editorial con ID {editorial_id} no existe.")
        if not self.repo_genero.leer_por_id(genero_id):
            raise ValueError(f"Genero con ID {genero_id} no existe.")

        nuevo_id = self.repositorio.proximo_id()
        libro = Libro(
            id=nuevo_id,
            isbn=isbn,
            titulo=titulo,
            autor=autor,
            editorial_id=editorial_id,
            genero_id=genero_id,
            anio_publicacion=anio_publicacion,
        )
        return self.repositorio.crear(libro)

    def leer_por_id(self, id: int) -> Optional[Libro]:
        return self.repositorio.leer_por_id(id)

    def leer_todos(self) -> List[Libro]:
        return self.repositorio.leer_todos()

    def actualizar(
        self,
        id: int,
        isbn: str,
        titulo: str,
        autor: str,
        editorial_id: int,
        genero_id: int,
        anio_publicacion: int,
    ) -> Libro:
        if not self.repo_editorial.leer_por_id(editorial_id):
            raise ValueError(f"Editorial con ID {editorial_id} no existe.")
        if not self.repo_genero.leer_por_id(genero_id):
            raise ValueError(f"Genero con ID {genero_id} no existe.")

        libro = Libro(
            id=id,
            isbn=isbn,
            titulo=titulo,
            autor=autor,
            editorial_id=editorial_id,
            genero_id=genero_id,
            anio_publicacion=anio_publicacion,
        )
        return self.repositorio.actualizar(libro)


class ServicioPrecio(ServicioBase):
    """Servicio para la entidad Precio."""
    def __init__(
        self,
        repositorio: RepositorioPrecio,
        repo_libro: RepositorioLibro,
        repo_moneda: RepositorioMoneda,
    ) -> None:
        self.repositorio = repositorio
        self.repo_libro = repo_libro
        self.repo_moneda = repo_moneda

    def crear(self, libro_id: int, moneda_id: int, monto: float) -> Precio:
        if not self.repo_libro.leer_por_id(libro_id):
            raise ValueError(f"Libro con ID {libro_id} no existe.")
        if not self.repo_moneda.leer_por_id(moneda_id):
            raise ValueError(f"Moneda con ID {moneda_id} no existe.")

        nuevo_id = self.repositorio.proximo_id()
        precio = Precio(
            id=nuevo_id,
            libro_id=libro_id,
            moneda_id=moneda_id,
            monto=monto,
        )
        return self.repositorio.crear(precio)

    def leer_por_id(self, id: int) -> Optional[Precio]:
        return self.repositorio.leer_por_id(id)

    def leer_todos(self) -> List[Precio]:
        return self.repositorio.leer_todos()

    def leer_por_libro(self, libro_id: int) -> List[Precio]:
        return [
            p for p in self.repositorio.leer_todos()
            if p.libro_id == libro_id
        ]

    def actualizar(
        self,
        id: int,
        libro_id: int,
        moneda_id: int,
        monto: float,
    ) -> Precio:
        if not self.repo_libro.leer_por_id(libro_id):
            raise ValueError(f"Libro con ID {libro_id} no existe.")
        if not self.repo_moneda.leer_por_id(moneda_id):
            raise ValueError(f"Moneda con ID {moneda_id} no existe.")

        precio = Precio(
            id=id,
            libro_id=libro_id,
            moneda_id=moneda_id,
            monto=monto,
        )
        return self.repositorio.actualizar(precio)


class ServicioStock(ServicioBase):
    """Servicio para la entidad Stock."""
    def __init__(
        self,
        repositorio: RepositorioStock,
        repo_libro: RepositorioLibro,
    ) -> None:
        self.repositorio = repositorio
        self.repo_libro = repo_libro

    def crear(self, libro_id: int, cantidad: int, ubicacion: str) -> Stock:
        if not self.repo_libro.leer_por_id(libro_id):
            raise ValueError(f"Libro con ID {libro_id} no existe.")

        stock = Stock(
            libro_id=libro_id,
            cantidad=cantidad,
            ubicacion=ubicacion,
        )
        return self.repositorio.crear(stock)

    def leer_todos(self) -> List[Stock]:
        return self.repositorio.leer_todos()

    def leer_por_libro(self, libro_id: int) -> Optional[Stock]:
        return self.repositorio.leer_por_libro(libro_id)

    def actualizar(
        self,
        libro_id: int,
        cantidad: int,
        ubicacion: str,
    ) -> Stock:
        if not self.repo_libro.leer_por_id(libro_id):
            raise ValueError(f"Libro con ID {libro_id} no existe.")

        stock = Stock(
            libro_id=libro_id,
            cantidad=cantidad,
            ubicacion=ubicacion,
        )
        return self.repositorio.actualizar(stock)


class ServicioCotizacionDolar(ServicioBase):
    """Servicio para la entidad CotizacionDolar."""
    def __init__(
        self,
        repositorio: RepositorioCotizacionDolar,
        repo_tipo: RepositorioTipoCotizacion,
    ) -> None:
        self.repositorio = repositorio
        self.repo_tipo = repo_tipo

    def crear(
        self,
        tipo_cotizacion_id: int,
        fecha_str_or_date: str | datetime.date,
        valor_compra: float,
        valor_venta: float,
    ) -> CotizacionDolar:
        if not self.repo_tipo.leer_por_id(tipo_cotizacion_id):
            raise ValueError(
                f"TipoCotizacion con ID {tipo_cotizacion_id} no existe.",
            )

        if isinstance(fecha_str_or_date, str):
            fecha = datetime.date.fromisoformat(fecha_str_or_date)
        else:
            fecha = validar_fecha(fecha_str_or_date)

        cotizacion = CotizacionDolar(
            tipo_cotizacion_id=tipo_cotizacion_id,
            fecha=fecha,
            valor_compra=valor_compra,
            valor_venta=valor_venta,
        )
        return self.repositorio.crear(cotizacion)

    def leer_por_tipo_y_fecha(
        self,
        tipo_id: int,
        fecha: datetime.date,
    ) -> Optional[CotizacionDolar]:
        """Lee una cotización por tipo y fecha."""
        return self.repositorio.leer_por_tipo_y_fecha(
            tipo_id, validar_fecha(fecha)
        )

    def leer_historico_por_tipo(self, tipo_id: int) -> List[CotizacionDolar]:
        """Lee el histórico de cotizaciones para un tipo específico."""
        return self.repositorio.leer_historico_por_tipo(tipo_id)

    def actualizar(
        self,
        tipo_cotizacion_id: int,
        fecha_str_or_date: str | datetime.date,
        valor_compra: float,
        valor_venta: float,
    ) -> CotizacionDolar:
        """Actualiza una cotización existente."""
        if not self.repo_tipo.leer_por_id(tipo_cotizacion_id):
            raise ValueError(
                f"TipoCotizacion con ID {tipo_cotizacion_id} no existe.",
            )

        if isinstance(fecha_str_or_date, str):
            fecha = datetime.date.fromisoformat(fecha_str_or_date)
        else:
            fecha = validar_fecha(fecha_str_or_date)

        cotizacion = CotizacionDolar(
            tipo_cotizacion_id=tipo_cotizacion_id,
            fecha=fecha,
            valor_compra=valor_compra,
            valor_venta=valor_venta,
        )
        return self.repositorio.actualizar(cotizacion)


    def leer_todos(self) -> List[CotizacionDolar]:
        return self.repositorio.leer_todos()

    def planificar_baja(
        self, tipo_cotizacion_id: int, fecha: datetime.date
    ) -> PlanBaja | None:
        validar_entero(tipo_cotizacion_id, "tipo_cotizacion_id", 1)
        return ServicioBajas(self.repositorio.almacen).planificar(
            self.repositorio.nombre,
            (tipo_cotizacion_id, validar_fecha(fecha)),
        )

    def eliminar(
        self, tipo_cotizacion_id: int, fecha: datetime.date,
        confirmar_cascada: bool = False,
    ) -> bool:
        validar_entero(tipo_cotizacion_id, "tipo_cotizacion_id", 1)
        return ServicioBajas(self.repositorio.almacen).eliminar(
            self.repositorio.nombre,
            (tipo_cotizacion_id, validar_fecha(fecha)), confirmar_cascada,
        )

    def obtener_ultima_cotizacion(
        self,
        tipo_id: int,
    ) -> Optional[CotizacionDolar]:
        cotizaciones = self.leer_historico_por_tipo(tipo_id)
        if not cotizaciones:
            return None
        return max(cotizaciones, key=lambda c: c.fecha)

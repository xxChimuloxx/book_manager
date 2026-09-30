"""Entidades del inventario y validaciones de sus valores."""

from __future__ import annotations

import datetime
import math


def validar_texto(valor: str, campo: str) -> str:
    """Exige texto no vacío y quita espacios exteriores."""
    if not isinstance(valor, str) or not valor.strip():
        raise ValueError(f"{campo} debe ser un texto no vacío.")
    return valor.strip()


def validar_entero(valor: int, campo: str, minimo: int = 0) -> int:
    """Valida enteros reales; los booleanos no son cantidades ni IDs."""
    if type(valor) is not int or valor < minimo:
        raise ValueError(
            f"{campo} debe ser un entero mayor o igual a {minimo}.",
        )
    return valor


def validar_importe(valor: float, campo: str) -> float:
    """Exige un número finito y no negativo, también fuera de la consola."""
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ValueError(f"{campo} debe ser numérico.")
    try:
        numero = float(valor)
    except (ValueError, TypeError, OverflowError) as error:
        raise ValueError(f"{campo} debe ser un número finito.") from error
    if not math.isfinite(numero) or numero < 0:
        raise ValueError(f"{campo} debe ser finito y no negativo.")
    return numero


def validar_fecha(valor: datetime.date) -> datetime.date:
    """Normaliza datetime a date para mantener claves homogéneas."""
    if isinstance(valor, datetime.datetime):
        valor = valor.date()
    if type(valor) is not datetime.date:
        raise ValueError("fecha debe ser una fecha válida.")
    return valor


class Entidad:
    """Representación legible común a las entidades."""

    _campos: tuple[str, ...] = ()

    def __str__(self) -> str:
        contenido = ", ".join(
            f"{campo}={getattr(self, campo)!r}" for campo in self._campos
        )
        return f"{type(self).__name__}({contenido})"

    def __repr__(self) -> str:
        return str(self)


class EntidadBase(Entidad):
    """Entidad con identidad positiva e inmutable."""

    def __init__(self, id: int) -> None:
        self._id = validar_entero(id, "id", 1)

    @property
    def id(self) -> int:
        return self._id


class Genero(EntidadBase):
    """Categoría literaria."""

    _campos = ('id', 'nombre')

    def __init__(
        self,
        id: int,
        nombre: str,
    ) -> None:
        super().__init__(id)
        self.nombre = nombre

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        self._nombre = validar_texto(valor, "nombre")


class Editorial(EntidadBase):
    """Editorial o distribuidora."""

    _campos = ('id', 'nombre', 'pais')

    def __init__(
        self,
        id: int,
        nombre: str,
        pais: str,
    ) -> None:
        super().__init__(id)
        self.nombre = nombre
        self.pais = pais

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        self._nombre = validar_texto(valor, "nombre")

    @property
    def pais(self) -> str:
        return self._pais

    @pais.setter
    def pais(self, valor: str) -> None:
        self._pais = validar_texto(valor, "pais")


class Moneda(EntidadBase):
    """Moneda identificada por un código normalizado."""

    _campos = ('id', 'codigo', 'nombre', 'simbolo')

    def __init__(
        self,
        id: int,
        codigo: str,
        nombre: str,
        simbolo: str,
    ) -> None:
        super().__init__(id)
        self.codigo = codigo
        self.nombre = nombre
        self.simbolo = simbolo

    @property
    def codigo(self) -> str:
        return self._codigo

    @codigo.setter
    def codigo(self, valor: str) -> None:
        self._codigo = validar_texto(valor, "codigo").upper()

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        self._nombre = validar_texto(valor, "nombre")

    @property
    def simbolo(self) -> str:
        return self._simbolo

    @simbolo.setter
    def simbolo(self, valor: str) -> None:
        self._simbolo = validar_texto(valor, "simbolo")


class TipoCotizacion(EntidadBase):
    """Tipo de cotización del dólar."""

    _campos = ('id', 'nombre', 'descripcion')

    def __init__(
        self,
        id: int,
        nombre: str,
        descripcion: str,
    ) -> None:
        super().__init__(id)
        self.nombre = nombre
        self.descripcion = descripcion

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        self._nombre = validar_texto(valor, "nombre")

    @property
    def descripcion(self) -> str:
        return self._descripcion

    @descripcion.setter
    def descripcion(self, valor: str) -> None:
        self._descripcion = validar_texto(valor, "descripcion")


class Libro(EntidadBase):
    """Título y sus referencias a editorial y género."""

    _campos = (
        'id',
        'isbn',
        'titulo',
        'autor',
        'editorial_id',
        'genero_id',
        'anio_publicacion',
    )

    def __init__(
        self,
        id: int,
        isbn: str,
        titulo: str,
        autor: str,
        editorial_id: int,
        genero_id: int,
        anio_publicacion: int,
    ) -> None:
        super().__init__(id)
        self.isbn = isbn
        self.titulo = titulo
        self.autor = autor
        self.editorial_id = editorial_id
        self.genero_id = genero_id
        self.anio_publicacion = anio_publicacion

    @property
    def isbn(self) -> str:
        return self._isbn

    @isbn.setter
    def isbn(self, valor: str) -> None:
        self._isbn = validar_texto(valor, "isbn")

    @property
    def titulo(self) -> str:
        return self._titulo

    @titulo.setter
    def titulo(self, valor: str) -> None:
        self._titulo = validar_texto(valor, "titulo")

    @property
    def autor(self) -> str:
        return self._autor

    @autor.setter
    def autor(self, valor: str) -> None:
        self._autor = validar_texto(valor, "autor")

    @property
    def editorial_id(self) -> int:
        return self._editorial_id

    @editorial_id.setter
    def editorial_id(self, valor: int) -> None:
        self._editorial_id = validar_entero(valor, "editorial_id", 1)

    @property
    def genero_id(self) -> int:
        return self._genero_id

    @genero_id.setter
    def genero_id(self, valor: int) -> None:
        self._genero_id = validar_entero(valor, "genero_id", 1)

    @property
    def anio_publicacion(self) -> int:
        return self._anio_publicacion

    @anio_publicacion.setter
    def anio_publicacion(self, valor: int) -> None:
        self._anio_publicacion = validar_entero(valor, "anio_publicacion")


class Precio(EntidadBase):
    """Precio vigente de un libro en una moneda."""

    _campos = ('id', 'libro_id', 'moneda_id', 'monto')

    def __init__(
        self,
        id: int,
        libro_id: int,
        moneda_id: int,
        monto: float,
    ) -> None:
        super().__init__(id)
        self.libro_id = libro_id
        self.moneda_id = moneda_id
        self.monto = monto

    @property
    def libro_id(self) -> int:
        return self._libro_id

    @libro_id.setter
    def libro_id(self, valor: int) -> None:
        self._libro_id = validar_entero(valor, "libro_id", 1)

    @property
    def moneda_id(self) -> int:
        return self._moneda_id

    @moneda_id.setter
    def moneda_id(self, valor: int) -> None:
        self._moneda_id = validar_entero(valor, "moneda_id", 1)

    @property
    def monto(self) -> float:
        return self._monto

    @monto.setter
    def monto(self, valor: float) -> None:
        self._monto = validar_importe(valor, "monto")


class Stock(Entidad):
    """Existencias identificadas por el libro."""

    _campos = ('libro_id', 'cantidad', 'ubicacion')

    def __init__(
        self,
        libro_id: int,
        cantidad: int,
        ubicacion: str,
    ) -> None:
        self._libro_id = validar_entero(libro_id, "libro_id", 1)
        self.cantidad = cantidad
        self.ubicacion = ubicacion

    @property
    def libro_id(self) -> int:
        return self._libro_id

    @property
    def cantidad(self) -> int:
        return self._cantidad

    @cantidad.setter
    def cantidad(self, valor: int) -> None:
        self._cantidad = validar_entero(valor, "cantidad")

    @property
    def ubicacion(self) -> str:
        return self._ubicacion

    @ubicacion.setter
    def ubicacion(self, valor: str) -> None:
        self._ubicacion = validar_texto(valor, "ubicacion")


class CotizacionDolar(Entidad):
    """Cotización identificada por tipo y fecha."""

    _campos = ('tipo_cotizacion_id', 'fecha', 'valor_compra', 'valor_venta')

    def __init__(
        self,
        tipo_cotizacion_id: int,
        fecha: datetime.date,
        valor_compra: float,
        valor_venta: float,
    ) -> None:
        self._tipo_cotizacion_id = validar_entero(
            tipo_cotizacion_id,
            "tipo_cotizacion_id",
            1,
        )
        self._fecha = validar_fecha(fecha)
        self.valor_compra = valor_compra
        self.valor_venta = valor_venta

    @property
    def tipo_cotizacion_id(self) -> int:
        return self._tipo_cotizacion_id

    @property
    def fecha(self) -> datetime.date:
        return self._fecha

    @property
    def valor_compra(self) -> float:
        return self._valor_compra

    @valor_compra.setter
    def valor_compra(self, valor: float) -> None:
        self._valor_compra = validar_importe(valor, "valor_compra")

    @property
    def valor_venta(self) -> float:
        return self._valor_venta

    @valor_venta.setter
    def valor_venta(self, valor: float) -> None:
        self._valor_venta = validar_importe(valor, "valor_venta")

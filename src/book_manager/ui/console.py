"""Interfaz de consola con CRUD, edición y bajas confirmadas."""

from __future__ import annotations

import datetime
import math
from typing import Any

from book_manager.entities.entities import Entidad
from book_manager.services.bajas import ETIQUETAS
from book_manager.services.services import (
    ServicioCotizacionDolar, ServicioEditorial, ServicioGenero, ServicioLibro,
    ServicioMoneda, ServicioPrecio, ServicioStock, ServicioTipoCotizacion,
)

# Campo, etiqueta y tipo de entrada. Los nombres coinciden con los servicios.
CAMPOS = {
    "generos": (("nombre", "Nombre", "texto"),),
    "editoriales": (
        ("nombre", "Nombre", "texto"), ("pais", "País", "texto"),
    ),
    "monedas": (
        ("codigo", "Código (ARS, USD...)", "texto"),
        ("nombre", "Nombre", "texto"), ("simbolo", "Símbolo", "texto"),
    ),
    "tipos_cotizacion": (
        ("nombre", "Nombre", "texto"),
        ("descripcion", "Descripción", "texto"),
    ),
    "libros": (
        ("isbn", "ISBN", "texto"), ("titulo", "Título", "texto"),
        ("autor", "Autor", "texto"),
        ("editorial_id", "ID Editorial", "id"),
        ("genero_id", "ID Género", "id"),
        ("anio_publicacion", "Año de publicación", "entero"),
    ),
    "precios": (
        ("libro_id", "ID Libro", "id"),
        ("moneda_id", "ID Moneda", "id"), ("monto", "Monto", "importe"),
    ),
    "stock": (
        ("libro_id", "ID Libro", "id"),
        ("cantidad", "Cantidad", "entero"),
        ("ubicacion", "Ubicación", "texto"),
    ),
    "cotizaciones": (
        ("tipo_cotizacion_id", "ID Tipo de Cotización", "id"),
        ("fecha_str_or_date", "Fecha (YYYY-MM-DD)", "fecha"),
        ("valor_compra", "Valor de compra", "importe"),
        ("valor_venta", "Valor de venta", "importe"),
    ),
}
DEPENDENCIAS = {
    "libros": ("generos", "editoriales"),
    "precios": ("libros", "monedas"),
    "stock": ("libros",),
    "cotizaciones": ("tipos_cotizacion",),
}


class ConsolaUI:
    """Los menús comparten un recorrido; las reglas permanecen en servicios."""

    def __init__(
        self,
        servicio_genero: ServicioGenero,
        servicio_editorial: ServicioEditorial,
        servicio_moneda: ServicioMoneda,
        servicio_tipo_cotizacion: ServicioTipoCotizacion,
        servicio_libro: ServicioLibro,
        servicio_precio: ServicioPrecio,
        servicio_stock: ServicioStock,
        servicio_cotizacion: ServicioCotizacionDolar,
    ) -> None:
        self.servicio_genero = servicio_genero
        self.servicio_editorial = servicio_editorial
        self.servicio_moneda = servicio_moneda
        self.servicio_tipo_cotizacion = servicio_tipo_cotizacion
        self.servicio_libro = servicio_libro
        self.servicio_precio = servicio_precio
        self.servicio_stock = servicio_stock
        self.servicio_cotizacion = servicio_cotizacion
        self.servicios = {
            "generos": servicio_genero, "editoriales": servicio_editorial,
            "monedas": servicio_moneda,
            "tipos_cotizacion": servicio_tipo_cotizacion,
            "libros": servicio_libro, "precios": servicio_precio,
            "stock": servicio_stock, "cotizaciones": servicio_cotizacion,
        }

    def _input(self, prompt: str = "") -> str:
        if prompt:
            print(prompt, flush=True)
        return input()

    def _pausar(self) -> None:
        self._input("\nPresione ENTER para continuar...")

    def _limpiar_pantalla(self) -> None:
        # Conserva la limpieza original, compatible con la entrada de Colab.
        print("\n" * 10)

    def _solicitar_int(
        self, prompt: str, defecto: int | None = None, minimo: int = 1
    ) -> int:
        while True:
            texto = self._input(prompt).strip()
            if not texto and defecto is not None:
                return defecto
            try:
                valor = int(texto)
                if valor >= minimo:
                    return valor
            except ValueError:
                pass
            print(f"Error: ingrese un entero mayor o igual a {minimo}.")

    def _solicitar_float(
        self, prompt: str, defecto: float | None = None
    ) -> float:
        """Admite punto o coma decimal, sin separadores de miles."""
        while True:
            texto = self._input(prompt).strip()
            if not texto and defecto is not None:
                return defecto
            try:
                valor = float(texto.replace(",", "."))
                if math.isfinite(valor) and valor >= 0:
                    return valor
            except (ValueError, OverflowError):
                pass
            print(
                "Error: ingrese un importe finito y no negativo, "
                "sin separadores de miles."
            )

    def _solicitar_fecha(
        self, prompt: str, defecto: datetime.date | None = None
    ) -> datetime.date:
        while True:
            texto = self._input(prompt).strip()
            if not texto and defecto is not None:
                return defecto
            try:
                return datetime.date.fromisoformat(texto)
            except ValueError:
                print(
                    "Error: ingrese una fecha válida con formato YYYY-MM-DD.",
                )

    def _solicitar_texto(self, prompt: str, defecto: str | None = None) -> str:
        while True:
            texto = self._input(prompt).strip()
            if texto:
                return texto
            if defecto is not None:
                return defecto
            print("Error: el texto no puede estar vacío.")

    def ejecutar(self) -> None:
        tablas = tuple(self.servicios)
        while True:
            self._limpiar_pantalla()
            print("\n========================================")
            print("       BOOK MANAGER - Sprint 1 - v1.1.2")
            print("========================================")
            for numero, tabla in enumerate(tablas, 1):
                print(f"{numero}. Gestionar {ETIQUETAS[tabla]}")
            print("0. Salir")
            opcion = self._input("Seleccione una opción:").strip()
            if opcion == "0":
                print("Saliendo del sistema. Cambios guardados.")
                return
            if opcion in {str(n) for n in range(1, len(tablas) + 1)}:
                self._menu_entidad(tablas[int(opcion) - 1])
            else:
                print("Opción inválida.")
                self._pausar()

    def _mostrar_submenu(self, nombre_entidad: str) -> str:
        self._limpiar_pantalla()
        print(f"\n--- Gestión de {nombre_entidad} ---")
        print("1. Listar todos")
        print("2. Buscar por clave")
        print("3. Crear nuevo")
        print("4. Modificar existente")
        print("5. Eliminar")
        print("0. Volver al menú principal")
        return self._input("Seleccione una opción:").strip()

    def _clave(self, tabla: str) -> tuple:
        if tabla == "stock":
            return (self._solicitar_int("ID del Libro:"),)
        if tabla == "cotizaciones":
            return (
                self._solicitar_int("ID del Tipo de Cotización:"),
                self._solicitar_fecha("Fecha (YYYY-MM-DD):"),
            )
        return (self._solicitar_int("ID del registro:"),)

    def _buscar(self, tabla: str, clave: tuple) -> Entidad | None:
        servicio = self.servicios[tabla]
        if tabla == "stock":
            return servicio.leer_por_libro(*clave)
        if tabla == "cotizaciones":
            return servicio.leer_por_tipo_y_fecha(*clave)
        return servicio.leer_por_id(*clave)

    def _listar(self, tabla: str) -> None:
        registros = self.servicios[tabla].leer_todos()
        if not registros:
            print("No hay registros.")
        for registro in registros:
            print(registro)

    def _pedir_datos(
        self, tabla: str, actual: Entidad | None = None
    ) -> dict[str, Any]:
        for dependencia in DEPENDENCIAS.get(tabla, ()):
            print(f"\n--- {ETIQUETAS[dependencia]} disponibles ---")
            self._listar(dependencia)
        datos = {}
        for campo, etiqueta, tipo in CAMPOS[tabla]:
            atributo = "fecha" if campo == "fecha_str_or_date" else campo
            defecto = getattr(actual, atributo) if actual is not None else None
            inmutable = (
                (tabla == "stock" and campo == "libro_id")
                or (tabla == "cotizaciones" and campo in {
                    "tipo_cotizacion_id", "fecha_str_or_date",
                })
            )
            if actual is not None and inmutable:
                datos[campo] = defecto
                continue
            prompt = etiqueta
            if actual is not None:
                prompt += f" [actual: {defecto}; ENTER conserva]"
            prompt += ":"
            if tipo == "id":
                datos[campo] = self._solicitar_int(prompt, defecto)
            elif tipo == "entero":
                datos[campo] = self._solicitar_int(prompt, defecto, 0)
            elif tipo == "importe":
                datos[campo] = self._solicitar_float(prompt, defecto)
            elif tipo == "fecha":
                datos[campo] = self._solicitar_fecha(prompt, defecto)
            else:
                datos[campo] = self._solicitar_texto(prompt, defecto)
        return datos

    def _eliminar_con_confirmacion(self, tabla: str, clave: tuple) -> None:
        servicio = self.servicios[tabla]
        plan = servicio.planificar_baja(*clave)
        if plan is None:
            print("No encontrado.")
            return
        print(f"\nRegistro seleccionado: {plan.objetivo}")
        print(f"Se eliminarán {plan.total} registros: {plan.resumen()}.")
        while True:
            respuesta = self._input(
                "¿Continuar y eliminar todos los registros indicados? [s/N]:"
            ).strip().casefold()
            if respuesta in {"", "n", "no"}:
                print("Baja cancelada.")
                return
            if respuesta in {"s", "si", "sí"}:
                break
            print("Ingrese s para confirmar o n para cancelar.")
        if servicio.eliminar(*clave, confirmar_cascada=True):
            print(
                "Baja completada. "
                "Todos los registros indicados se eliminaron.",
            )
        else:
            print("No encontrado.")

    def _menu_entidad(self, tabla: str) -> None:
        servicio = self.servicios[tabla]
        while True:
            opcion = self._mostrar_submenu(ETIQUETAS[tabla])
            if opcion == "0":
                return
            try:
                if opcion == "1":
                    self._listar(tabla)
                elif opcion == "2":
                    registro = self._buscar(tabla, self._clave(tabla))
                    print(
                        registro if registro is not None else "No encontrado.",
                    )
                elif opcion == "3":
                    servicio.crear(**self._pedir_datos(tabla))
                    print("Registro creado exitosamente.")
                elif opcion == "4":
                    clave = self._clave(tabla)
                    registro = self._buscar(tabla, clave)
                    if registro is None:
                        print("No encontrado.")
                    else:
                        print(f"Registro actual: {registro}")
                        datos = self._pedir_datos(tabla, registro)
                        if tabla not in {"stock", "cotizaciones"}:
                            datos["id"] = clave[0]
                        servicio.actualizar(**datos)
                        print("Registro modificado exitosamente.")
                elif opcion == "5":
                    self._eliminar_con_confirmacion(tabla, self._clave(tabla))
                else:
                    print("Opción inválida.")
            except (ValueError, OSError) as error:
                print(f"Error: {error}")
            self._pausar()

    def _menu_genero(self) -> None:
        self._menu_entidad("generos")

    def _menu_editorial(self) -> None:
        self._menu_entidad("editoriales")

    def _menu_moneda(self) -> None:
        self._menu_entidad("monedas")

    def _menu_tipo_cotizacion(self) -> None:
        self._menu_entidad("tipos_cotizacion")

    def _menu_libro(self) -> None:
        self._menu_entidad("libros")

    def _menu_precio(self) -> None:
        self._menu_entidad("precios")

    def _menu_stock(self) -> None:
        self._menu_entidad("stock")

    def _menu_cotizacion(self) -> None:
        self._menu_entidad("cotizaciones")

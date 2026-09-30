"""Cálculo y aplicación de bajas en cascada dentro de una transacción."""

from __future__ import annotations

from dataclasses import dataclass

from book_manager.repositories.almacen_csv import (
    AlmacenCSV, Clave, clave_fila, decodificar,
)

ETIQUETAS = {
    "generos": "géneros", "editoriales": "editoriales", "monedas": "monedas",
    "tipos_cotizacion": "tipos de cotización", "libros": "libros",
    "precios": "precios", "stock": "registros de stock",
    "cotizaciones": "cotizaciones",
}


@dataclass(frozen=True)
class PlanBaja:
    """Registro elegido y claves de todos los registros afectados."""

    tabla: str
    clave: Clave
    objetivo: str
    afectados: dict[str, tuple[Clave, ...]]

    @property
    def total(self) -> int:
        return sum(len(claves) for claves in self.afectados.values())

    @property
    def tiene_dependientes(self) -> bool:
        return self.total > 1

    def resumen(self) -> str:
        return "; ".join(
            f"{ETIQUETAS[tabla]}: {len(claves)}"
            for tabla, claves in self.afectados.items() if claves
        )


class DependenciasError(ValueError):
    """La API exige autorización explícita para borrar dependencias."""

    def __init__(self, plan: PlanBaja) -> None:
        self.plan = plan
        super().__init__(
            "La baja tiene dependientes. " + plan.resumen()
            + ". Requiere confirmación de cascada."
        )


class ServicioBajas:
    """Recorre relaciones y elimina el conjunto completo o no elimina nada."""

    def __init__(self, almacen: AlmacenCSV) -> None:
        self.almacen = almacen

    def planificar(self, tabla: str, clave: Clave) -> PlanBaja | None:
        fila_raiz = next(
            (
                fila for fila in self.almacen.filas(tabla)
                if clave_fila(tabla, fila) == clave
            ),
            None,
        )
        if fila_raiz is None:
            return None
        afectados: dict[str, set[Clave]] = {tabla: {clave}}
        if tabla in {"generos", "editoriales"}:
            campo = "genero_id" if tabla == "generos" else "editorial_id"
            afectados["libros"] = {
                int(fila["id"]) for fila in self.almacen.filas("libros")
                if int(fila[campo]) == clave
            }
        libros = afectados.get("libros", set())
        if libros:
            afectados["precios"] = {
                int(fila["id"]) for fila in self.almacen.filas("precios")
                if int(fila["libro_id"]) in libros
            }
            afectados["stock"] = {
                int(fila["libro_id"]) for fila in self.almacen.filas("stock")
                if int(fila["libro_id"]) in libros
            }
        if tabla == "monedas":
            afectados["precios"] = {
                int(fila["id"]) for fila in self.almacen.filas("precios")
                if int(fila["moneda_id"]) == clave
            }
        if tabla == "tipos_cotizacion":
            afectados["cotizaciones"] = {
                clave_fila("cotizaciones", fila)
                for fila in self.almacen.filas("cotizaciones")
                if int(fila["tipo_cotizacion_id"]) == clave
            }
        return PlanBaja(
            tabla, clave, str(decodificar(tabla, fila_raiz)),
            {
                nombre: tuple(sorted(claves))
                for nombre, claves in afectados.items() if claves
            },
        )

    def eliminar(
        self, tabla: str, clave: Clave, confirmar_cascada: bool = False
    ) -> bool:
        if type(confirmar_cascada) is not bool:
            raise ValueError("La confirmación de cascada debe ser booleana.")
        plan = self.planificar(tabla, clave)
        if plan is None:
            return False
        if plan.tiene_dependientes and not confirmar_cascada:
            raise DependenciasError(plan)
        with self.almacen.transaccion():
            for nombre, claves in plan.afectados.items():
                restantes = [
                    fila for fila in self.almacen.filas(nombre)
                    if clave_fila(nombre, fila) not in claves
                ]
                self.almacen.reemplazar(nombre, restantes)
        return True

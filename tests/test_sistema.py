"""Regresiones de persistencia, cascadas, validaciones y recuperación."""

import contextlib
import csv
import datetime
import io
import json
import math
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from book_manager.entities.entities import (
    CotizacionDolar, Genero, Libro, Precio, Stock,
)
from book_manager.main import crear_sistema, main
from book_manager.preload_data import preload_data
from book_manager.repositories import almacen_csv
from book_manager.repositories.almacen_csv import AlmacenCSV
from book_manager.services.bajas import DependenciasError


class SistemaTest(unittest.TestCase):
    def setUp(self):
        self.temporal = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporal.cleanup)
        self.directorio = Path(self.temporal.name)
        self.ui = crear_sistema(data_dir=self.directorio)

    def reabrir(self, precarga=True):
        return crear_sistema(precarga, self.directorio)

    def contenido(self):
        return {
            p.name: p.read_bytes() for p in self.directorio.glob("*.csv")
        }

    def recorrer(self, tabla, entradas):
        with patch("builtins.input", side_effect=entradas):
            salida = io.StringIO()
            with contextlib.redirect_stdout(salida):
                self.ui._menu_entidad(tabla)
        return salida.getvalue()

    def test_precarga_minima_ocho_entidades(self):
        for tabla, servicio in self.ui.servicios.items():
            with self.subTest(tabla=tabla):
                self.assertGreaterEqual(len(servicio.leer_todos()), 10)
        self.assertEqual(len(self.contenido()), 9)

    def test_crud_genero_persiste(self):
        s = self.ui.servicio_genero
        nuevo = s.crear("Auditoría")
        self.assertEqual(
            self.reabrir().servicio_genero.leer_por_id(nuevo.id).nombre,
            "Auditoría",
        )
        s.actualizar(nuevo.id, "Cambio")
        self.assertEqual(
            self.reabrir().servicio_genero.leer_por_id(nuevo.id).nombre,
            "Cambio",
        )
        s.eliminar(nuevo.id)
        self.assertIsNone(self.reabrir().servicio_genero.leer_por_id(nuevo.id))

    def test_crud_editorial_persiste(self):
        s = self.ui.servicio_editorial
        nuevo = s.crear("Auditoría", "Argentina")
        self.assertIsNotNone(
            self.reabrir().servicio_editorial.leer_por_id(nuevo.id),
        )
        s.actualizar(nuevo.id, "Cambio", "Chile")
        self.assertEqual(
            self.reabrir().servicio_editorial.leer_por_id(nuevo.id).pais,
            "Chile",
        )
        s.eliminar(nuevo.id)
        self.assertIsNone(
            self.reabrir().servicio_editorial.leer_por_id(nuevo.id),
        )

    def test_crud_moneda_persiste(self):
        s = self.ui.servicio_moneda
        nuevo = s.crear("AUD", "Dólar australiano", "A$")
        self.assertIsNotNone(
            self.reabrir().servicio_moneda.leer_por_id(nuevo.id),
        )
        s.actualizar(nuevo.id, "NZD", "Dólar neozelandés", "NZ$")
        self.assertEqual(
            self.reabrir().servicio_moneda.leer_por_id(nuevo.id).codigo,
            "NZD",
        )
        s.eliminar(nuevo.id)
        self.assertIsNone(self.reabrir().servicio_moneda.leer_por_id(nuevo.id))

    def test_crud_tipo_persiste(self):
        s = self.ui.servicio_tipo_cotizacion
        nuevo = s.crear("Prueba", "Cotización de prueba")
        self.assertIsNotNone(
            self.reabrir().servicio_tipo_cotizacion.leer_por_id(nuevo.id),
        )
        s.actualizar(nuevo.id, "Cambio", "Nuevo texto")
        self.assertEqual(
            self.reabrir().servicio_tipo_cotizacion.leer_por_id(nuevo.id).nombre,
            "Cambio",
        )
        s.eliminar(nuevo.id)
        self.assertIsNone(
            self.reabrir().servicio_tipo_cotizacion.leer_por_id(nuevo.id),
        )

    def test_crud_libro_persiste(self):
        s = self.ui.servicio_libro
        nuevo = s.crear("9780306406157", "Prueba", "Autor", 1, 1, 2000)
        self.assertIsNotNone(
            self.reabrir().servicio_libro.leer_por_id(nuevo.id),
        )
        s.actualizar(nuevo.id, nuevo.isbn, "Cambio", "Autor", 2, 2, 2001)
        self.assertEqual(
            self.reabrir().servicio_libro.leer_por_id(nuevo.id).titulo,
            "Cambio",
        )
        s.eliminar(nuevo.id)
        self.assertIsNone(self.reabrir().servicio_libro.leer_por_id(nuevo.id))

    def test_crud_precio_persiste(self):
        s = self.ui.servicio_precio
        nuevo = s.crear(1, 2, 10.5)
        self.assertEqual(
            self.reabrir().servicio_precio.leer_por_id(nuevo.id).monto,
            10.5,
        )
        s.actualizar(nuevo.id, 2, 2, 20)
        self.assertEqual(
            self.reabrir().servicio_precio.leer_por_id(nuevo.id).monto,
            20,
        )
        s.eliminar(nuevo.id)
        self.assertIsNone(self.reabrir().servicio_precio.leer_por_id(nuevo.id))

    def test_crud_stock_persiste(self):
        s = self.ui.servicio_stock
        s.eliminar(1)
        s.crear(1, 4, "Prueba")
        self.assertEqual(
            self.reabrir().servicio_stock.leer_por_libro(1).cantidad,
            4,
        )
        s.actualizar(1, 7, "Cambio")
        self.assertEqual(
            self.reabrir().servicio_stock.leer_por_libro(1).cantidad,
            7,
        )
        s.eliminar(1)
        self.assertIsNone(self.reabrir().servicio_stock.leer_por_libro(1))

    def test_crud_cotizacion_persiste(self):
        s = self.ui.servicio_cotizacion
        fecha = datetime.date(2026, 9, 30)
        s.crear(1, fecha, 100, 110)
        self.assertEqual(
            self.reabrir().servicio_cotizacion.leer_por_tipo_y_fecha(1, fecha).valor_venta,
            110,
        )
        s.actualizar(1, fecha, 120, 130)
        self.assertEqual(
            self.reabrir().servicio_cotizacion.leer_por_tipo_y_fecha(1, fecha).valor_venta,
            130,
        )
        s.eliminar(1, fecha)
        self.assertIsNone(
            self.reabrir().servicio_cotizacion.leer_por_tipo_y_fecha(1, fecha),
        )

    def test_apertura_false_recupera_datos_existentes(self):
        nuevo = self.ui.servicio_genero.crear("Persistente")
        self.assertIsNotNone(
            self.reabrir(False).servicio_genero.leer_por_id(nuevo.id),
        )

    def test_primera_apertura_sin_precarga(self):
        with tempfile.TemporaryDirectory() as d:
            vacio = crear_sistema(False, d)
            self.assertTrue(all(not s.leer_todos() for s in vacio.servicios.values()))
            restaurado = crear_sistema(True, d)
            self.assertTrue(all(not s.leer_todos() for s in restaurado.servicios.values()))

    def test_reimportacion_no_sobrescribe_modificaciones(self):
        self.ui.servicio_genero.actualizar(1, "Mi género")
        almacen = self.ui.servicio_genero.repositorio.almacen
        preload_data.cargar_todos_los_datos(almacen)
        self.assertEqual(
            self.reabrir().servicio_genero.leer_por_id(1).nombre,
            "Mi género",
        )

    def test_baja_libro_requiere_confirmacion(self):
        anterior = self.contenido()
        with self.assertRaises(DependenciasError):
            self.ui.servicio_libro.eliminar(12)
        self.assertEqual(self.contenido(), anterior)

    def test_confirmacion_api_exige_bool(self):
        antes = self.contenido()
        with self.assertRaises(ValueError):
            self.ui.servicio_libro.eliminar(12, confirmar_cascada="n")
        self.assertEqual(self.contenido(), antes)

    def test_baja_libro_cascada_persiste(self):
        self.ui.servicio_libro.eliminar(12, confirmar_cascada=True)
        ui = self.reabrir()
        self.assertIsNone(ui.servicio_libro.leer_por_id(12))
        self.assertEqual(ui.servicio_precio.leer_por_libro(12), [])
        self.assertIsNone(ui.servicio_stock.leer_por_libro(12))
        self.assertIsNotNone(ui.servicio_libro.leer_por_id(11))

    def test_baja_genero_cascada(self):
        plan = self.ui.servicio_genero.planificar_baja(1)
        self.assertEqual(len(plan.afectados["libros"]), 6)
        afectados = set(plan.afectados["libros"])
        self.ui.servicio_genero.eliminar(1, confirmar_cascada=True)
        ui = self.reabrir()
        self.assertIsNone(ui.servicio_genero.leer_por_id(1))
        self.assertFalse(any(b.id in afectados for b in ui.servicio_libro.leer_todos()))
        self.assertFalse(any(p.libro_id in afectados for p in ui.servicio_precio.leer_todos()))
        self.assertFalse(any(s.libro_id in afectados for s in ui.servicio_stock.leer_todos()))
        self.assertIsNotNone(ui.servicio_editorial.leer_por_id(2))

    def test_baja_editorial_cascada(self):
        self.ui.servicio_editorial.eliminar(2, confirmar_cascada=True)
        ui = self.reabrir()
        self.assertIsNone(ui.servicio_editorial.leer_por_id(2))
        for clave in (1, 5, 6):
            self.assertIsNone(ui.servicio_libro.leer_por_id(clave))
            self.assertIsNone(ui.servicio_stock.leer_por_libro(clave))
            self.assertEqual(ui.servicio_precio.leer_por_libro(clave), [])
        self.assertIsNotNone(ui.servicio_genero.leer_por_id(1))

    def test_baja_moneda_elimina_precios_no_libros(self):
        self.ui.servicio_moneda.eliminar(1, confirmar_cascada=True)
        ui = self.reabrir()
        self.assertFalse(any(p.moneda_id == 1 for p in ui.servicio_precio.leer_todos()))
        self.assertEqual(len(ui.servicio_libro.leer_todos()), 12)
        self.assertEqual(len(ui.servicio_stock.leer_todos()), 12)
        self.assertEqual(len(ui.servicio_precio.leer_todos()), 3)

    def test_baja_tipo_elimina_historico(self):
        self.ui.servicio_tipo_cotizacion.eliminar(1, confirmar_cascada=True)
        ui = self.reabrir()
        self.assertEqual(ui.servicio_cotizacion.leer_historico_por_tipo(1), [])
        self.assertEqual(
            len(ui.servicio_cotizacion.leer_historico_por_tipo(2)),
            3,
        )

    def test_baja_inexistente_no_escribe(self):
        anterior = self.contenido()
        self.assertFalse(self.ui.servicio_libro.eliminar(999))
        self.assertEqual(self.contenido(), anterior)

    def test_cancelacion_baja_por_enter(self):
        anterior = self.contenido()
        texto = self.recorrer("editoriales", ["5", "2", "", "", "0"])
        self.assertIn("Baja cancelada", texto)
        self.assertIn("libros: 3", texto)
        self.assertEqual(self.contenido(), anterior)

    def test_cancelacion_baja_por_no(self):
        anterior = self.contenido()
        texto = self.recorrer("libros", ["5", "12", "n", "", "0"])
        self.assertIn("precios: 2", texto)
        self.assertEqual(self.contenido(), anterior)

    def test_confirmacion_invalida_no_acepta_accidentalmente(self):
        anterior = self.contenido()
        texto = self.recorrer(
            "libros",
            ["5", "12", "cualquier cosa", "no", "", "0"],
        )
        self.assertIn("Ingrese s", texto)
        self.assertEqual(self.contenido(), anterior)

    def test_baja_confirmada_por_consola(self):
        texto = self.recorrer("editoriales", ["5", "2", "Sí", "", "0"])
        self.assertIn("Baja completada", texto)
        self.assertIsNone(self.reabrir().servicio_libro.leer_por_id(1))

    def test_id_no_se_reutiliza_tras_baja_y_reinicio(self):
        self.ui.servicio_libro.eliminar(12, confirmar_cascada=True)
        ui = self.reabrir()
        nuevo = ui.servicio_libro.crear(
            "9780306406157",
            "Nuevo",
            "Autor",
            1,
            1,
            2000,
        )
        self.assertEqual(nuevo.id, 13)
        self.assertEqual(ui.servicio_precio.leer_por_libro(nuevo.id), [])
        self.assertIsNone(ui.servicio_stock.leer_por_libro(nuevo.id))

    def test_secuencia_se_conserva_aun_si_se_eliminan_todos(self):
        for genero in self.ui.servicio_genero.leer_todos():
            self.ui.servicio_genero.eliminar(genero.id, confirmar_cascada=True)
        nuevo = self.reabrir().servicio_genero.crear("Después de todos")
        self.assertEqual(nuevo.id, 11)

    def test_api_no_permite_reutilizar_id(self):
        s = self.ui.servicio_genero
        nuevo = s.crear("Prueba")
        s.eliminar(nuevo.id)
        with self.assertRaises(ValueError):
            s.repositorio.crear(Genero(nuevo.id, "Otro"))

    def test_importes_no_finitos_y_negativos_en_entidades(self):
        for monto in (
            float("nan"),
            float("inf"),
            float("-inf"),
            -1,
            True,
            "12",
        ):
            with self.subTest(monto=str(monto)):
                with self.assertRaises(ValueError):
                    Precio(1, 1, 1, monto)
                with self.assertRaises(ValueError):
                    CotizacionDolar(1, datetime.date.today(), monto, 100)
                with self.assertRaises(ValueError):
                    CotizacionDolar(1, datetime.date.today(), 100, monto)

    def test_actualizacion_invalida_conserva_archivo(self):
        anterior = self.contenido()
        with self.assertRaises(ValueError):
            self.ui.servicio_precio.actualizar(1, 1, 1, float("nan"))
        self.assertEqual(self.contenido(), anterior)
        self.assertEqual(
            self.reabrir().servicio_precio.leer_por_id(1).monto,
            24500,
        )

    def test_cotizacion_invalida_no_persiste(self):
        anterior = self.contenido()
        with self.assertRaises(ValueError):
            self.ui.servicio_cotizacion.crear(
                1,
                "2026-09-30",
                10,
                float("inf"),
            )
        self.assertEqual(self.contenido(), anterior)

    def test_consola_repregunta_importes_invalidos(self):
        with patch(
            "builtins.input",
            side_effect=["nan", "inf", "-1", "abc", "12,50"],
        ):
            salida = io.StringIO()
            with contextlib.redirect_stdout(salida):
                monto = self.ui._solicitar_float("Monto:")
        self.assertEqual(monto, 12.5)
        self.assertEqual(salida.getvalue().count("Error:"), 4)

    def test_precio_cero_es_valido(self):
        p = self.ui.servicio_precio.crear(1, 2, 0)
        self.assertEqual(
            self.reabrir().servicio_precio.leer_por_id(p.id).monto,
            0,
        )

    def test_isbn_duplicado_se_rechaza(self):
        anterior = self.contenido()
        isbn = self.ui.servicio_libro.leer_por_id(1).isbn
        with self.assertRaisesRegex(ValueError, "ISBN duplicado"):
            self.ui.servicio_libro.crear(isbn, "Otro", "Autor", 1, 1, 2000)
        self.assertEqual(self.contenido(), anterior)

    def test_codigo_moneda_normalizado_y_unico(self):
        with self.assertRaisesRegex(ValueError, "Código de moneda duplicado"):
            self.ui.servicio_moneda.crear(" ars ", "Duplicada", "$")
        m = self.ui.servicio_moneda.crear(" aud ", "Prueba", "A$")
        self.assertEqual(
            self.reabrir().servicio_moneda.leer_por_id(m.id).codigo,
            "AUD",
        )

    def test_precio_vigente_unico(self):
        with self.assertRaisesRegex(ValueError, "Precio vigente"):
            self.ui.servicio_precio.crear(1, 1, 999)
        self.assertEqual(len(self.reabrir().servicio_precio.leer_todos()), 15)

    def test_referencias_inexistentes_se_rechazan(self):
        acciones = (
            lambda: self.ui.servicio_libro.crear("X", "X", "X", 999, 1, 2000),
            lambda: self.ui.servicio_precio.crear(999, 1, 10),
            lambda: self.ui.servicio_stock.crear(999, 1, "X"),
            lambda: self.ui.servicio_cotizacion.crear(
                999,
                "2026-09-30",
                10,
                11,
            ),
        )
        anterior = self.contenido()
        for accion in acciones:
            with self.assertRaises(ValueError):
                accion()
        self.assertEqual(self.contenido(), anterior)

    def test_repositorio_no_puede_borrar_dependencias_por_fuera(self):
        anterior = self.contenido()
        with self.assertRaises(ValueError):
            self.ui.servicio_libro.repositorio.eliminar(12)
        self.assertEqual(self.contenido(), anterior)
        self.assertIsNotNone(self.ui.servicio_libro.leer_por_id(12))

    def test_actualizacion_no_existente_no_cambia_secuencia(self):
        antes = self.contenido()
        with self.assertRaises(ValueError):
            self.ui.servicio_genero.actualizar(999, "No existe")
        self.assertEqual(self.contenido(), antes)
        self.assertEqual(self.ui.servicio_genero.crear("Nuevo").id, 11)

    def test_lectura_no_muta_estado(self):
        g = self.ui.servicio_genero.leer_por_id(1)
        g.nombre = "Sin actualizar"
        self.assertEqual(
            self.ui.servicio_genero.leer_por_id(1).nombre,
            "Novela",
        )
        with self.assertRaises(AttributeError):
            g.id = 99

    def test_claves_stock_y_cotizacion_son_inmutables(self):
        stock = self.ui.servicio_stock.leer_por_libro(1)
        c = self.ui.servicio_cotizacion.leer_historico_por_tipo(1)[0]
        with self.assertRaises(AttributeError):
            stock.libro_id = 99
        with self.assertRaises(AttributeError):
            c.fecha = datetime.date.today()
        with self.assertRaises(AttributeError):
            c.tipo_cotizacion_id = 99

    def test_booleanos_no_son_ids_o_cantidades(self):
        with self.assertRaises(ValueError):
            Genero(True, "Prueba")
        with self.assertRaises(ValueError):
            Stock(1, True, "Prueba")

    def test_fecha_datetime_normalizada(self):
        c = self.ui.servicio_cotizacion.crear(
            1,
            datetime.datetime(2026, 9, 30, 15),
            10,
            11,
        )
        self.assertEqual(type(c.fecha), datetime.date)
        self.assertIsNotNone(
            self.reabrir().servicio_cotizacion.leer_por_tipo_y_fecha(1, datetime.date(2026, 9, 30)),
        )

    def test_csv_con_comas_comillas_y_saltos(self):
        texto = 'Título, con "comillas"\ny otra línea'
        b = self.ui.servicio_libro.crear(
            "9780306406157",
            texto,
            "Autor",
            1,
            1,
            2000,
        )
        self.assertEqual(
            self.reabrir().servicio_libro.leer_por_id(b.id).titulo,
            texto,
        )

    def test_fallo_de_guardado_revierte_cascada_completa(self):
        antes = self.contenido()
        original = almacen_csv.escribir_atomico
        fallo = [False]
        def escribir(ruta, contenido):
            if ruta.name == "precios.csv" and not fallo[0]:
                fallo[0] = True
                raise OSError("Fallo de escritura simulado")
            original(ruta, contenido)
        with patch.object(almacen_csv, "escribir_atomico", escribir):
            with self.assertRaises(OSError):
                self.ui.servicio_libro.eliminar(12, confirmar_cascada=True)
        self.assertEqual(self.contenido(), antes)
        self.assertIsNotNone(self.ui.servicio_libro.leer_por_id(12))
        self.assertIsNotNone(self.reabrir().servicio_stock.leer_por_libro(12))
        self.assertFalse((self.directorio / ".transaccion.json").exists())

    def test_fallo_guardado_alta_no_consume_id(self):
        antes = self.contenido()
        original = almacen_csv.escribir_atomico
        fallo = [False]
        def escribir(ruta, contenido):
            if ruta.name == "secuencias.csv" and not fallo[0]:
                fallo[0] = True
                raise OSError("Fallo simulado")
            original(ruta, contenido)
        with patch.object(almacen_csv, "escribir_atomico", escribir):
            with self.assertRaises(OSError):
                self.ui.servicio_genero.crear("Fallida")
        self.assertEqual(self.contenido(), antes)
        self.assertEqual(self.ui.servicio_genero.crear("Válida").id, 11)

    def test_recuperacion_transaccion_interrumpida_revierte(self):
        ruta = self.directorio / "generos.csv"
        anterior = ruta.read_text()
        nuevo = anterior.replace("1,Novela", "1,Modificado")
        diario = {"estado": "pendiente", "archivos": {"generos.csv": {"anterior": anterior, "nuevo": nuevo}}}
        (self.directorio / ".transaccion.json").write_text(json.dumps(diario))
        ruta.write_text(nuevo)
        self.assertEqual(
            self.reabrir().servicio_genero.leer_por_id(1).nombre,
            "Novela",
        )
        self.assertFalse((self.directorio / ".transaccion.json").exists())

    def test_recuperacion_confirmada_completa_archivos(self):
        ruta = self.directorio / "generos.csv"
        anterior = ruta.read_text()
        nuevo = anterior.replace("1,Novela", "1,Confirmado")
        diario = {"estado": "confirmada", "archivos": {"generos.csv": {"anterior": anterior, "nuevo": nuevo}}}
        (self.directorio / ".transaccion.json").write_text(json.dumps(diario))
        self.assertEqual(
            self.reabrir().servicio_genero.leer_por_id(1).nombre,
            "Confirmado",
        )

    def test_diario_fuera_de_carpeta_se_rechaza(self):
        diario = {"estado": "pendiente", "archivos": {"../externo.csv": {"anterior": None, "nuevo": "X"}}}
        (self.directorio / ".transaccion.json").write_text(json.dumps(diario))
        with self.assertRaises(ValueError):
            AlmacenCSV(self.directorio)

    def test_csv_invalido_no_se_reemplaza_por_semillas(self):
        ruta = self.directorio / "generos.csv"
        ruta.write_text("encabezado_incorrecto\nX\n")
        contenido = ruta.read_bytes()
        with self.assertRaises(ValueError):
            self.reabrir()
        self.assertEqual(ruta.read_bytes(), contenido)

    def test_carpeta_parcial_no_se_reinicializa(self):
        (self.directorio / "precios.csv").unlink()
        antes = self.contenido()
        with self.assertRaises(ValueError):
            self.reabrir()
        self.assertEqual(self.contenido(), antes)

    def test_importacion_invalida_no_deja_carga_parcial(self):
        with tempfile.TemporaryDirectory() as origen, tempfile.TemporaryDirectory() as destino:
            ruta = Path(origen) / "libros.csv"
            ruta.write_text(
                "id,isbn,titulo,autor,editorial_id,genero_id,anio_publicacion\n1,X,X,X,999,999,2000\n",
            )
            original = preload_data.obtener_ruta_csv
            def localizar(nombre):
                return str(
                    ruta,
                ) if nombre == "libros.csv" else original(nombre)
            with patch.object(preload_data, "obtener_ruta_csv", localizar):
                with self.assertRaises(ValueError):
                    crear_sistema(data_dir=destino)
            self.assertEqual(list(Path(destino).glob("*.csv")), [])

    def test_vaciar_todas_las_entidades_no_resucita_semillas(self):
        for tabla in ("generos", "editoriales", "monedas", "tipos_cotizacion"):
            servicio = self.ui.servicios[tabla]
            for registro in servicio.leer_todos():
                servicio.eliminar(registro.id, confirmar_cascada=True)
        ui = self.reabrir()
        self.assertTrue(all(not s.leer_todos() for s in ui.servicios.values()))

    def test_consola_crud_ocho_entidades(self):
        secuencias = {
            "generos": ["1", "", "2", "1", "", "3", "Prueba", "", "4", "11", "Nuevo", "", "5", "11", "s", "", "0"],
            "editoriales": ["1", "", "2", "1", "", "3", "Prueba", "Argentina", "", "4", "11", "Nuevo", "Chile", "", "5", "11", "s", "", "0"],
            "monedas": ["1", "", "2", "1", "", "3", "AUD", "Prueba", "A$", "", "4", "11", "NZD", "Nuevo", "NZ$", "", "5", "11", "s", "", "0"],
            "tipos_cotizacion": ["1", "", "2", "1", "", "3", "Prueba", "Texto", "", "4", "11", "Nuevo", "Texto", "", "5", "11", "s", "", "0"],
            "libros": ["1", "", "2", "1", "", "3", "9780306406157", "Prueba", "Autor", "1", "1", "2000", "", "4", "13", "", "Nuevo", "", "", "", "", "", "5", "13", "s", "", "0"],
            "precios": ["1", "", "2", "1", "", "3", "1", "2", "10", "", "4", "16", "2", "2", "20", "", "5", "16", "s", "", "0"],
            "stock": ["1", "", "2", "1", "", "5", "1", "s", "", "3", "1", "5", "A", "", "4", "1", "7", "B", "", "5", "1", "s", "", "0"],
            "cotizaciones": ["1", "", "2", "1", "2024-01-02", "", "3", "1", "2026-09-30", "100", "110", "", "4", "1", "2026-09-30", "120", "130", "", "5", "1", "2026-09-30", "s", "", "0"],
        }
        for tabla, entradas in secuencias.items():
            with self.subTest(tabla=tabla):
                texto = self.recorrer(tabla, entradas)
                self.assertNotIn("Error:", texto)
                self.assertIn("creado exitosamente", texto)
                self.assertIn("modificado exitosamente", texto)
                self.assertIn("Baja completada", texto)
        self.reabrir()

    def test_edicion_enter_conserva_campos(self):
        antes = self.ui.servicio_libro.leer_por_id(1)
        self.recorrer(
            "libros",
            ["4", "1", "", "Nuevo título", "", "", "", "", "", "0"],
        )
        despues = self.reabrir().servicio_libro.leer_por_id(1)
        self.assertEqual(despues.titulo, "Nuevo título")
        self.assertEqual(despues.isbn, antes.isbn)
        self.assertEqual(despues.editorial_id, antes.editorial_id)

    def test_consola_precio_nan_se_corrige_antes_del_alta(self):
        texto = self.recorrer("precios", ["3", "1", "2", "nan", "15", "", "0"])
        self.assertIn("Error:", texto)
        self.assertEqual(
            self.reabrir().servicio_precio.leer_por_id(16).monto,
            15,
        )
        self.assertTrue(all(math.isfinite(p.monto) for p in self.ui.servicio_precio.leer_todos()))

    def test_consola_stock_lista_directamente(self):
        texto = self.recorrer("stock", ["1", "", "0"])
        self.assertEqual(texto.count("Stock(libro_id="), 12)

    def test_consola_cotizaciones_lista_todo(self):
        texto = self.recorrer("cotizaciones", ["1", "", "0"])
        self.assertEqual(texto.count("CotizacionDolar("), 14)

    def test_ultima_cotizacion(self):
        c = self.ui.servicio_cotizacion
        c.crear(1, "2026-09-30", 100, 110)
        self.assertEqual(
            c.obtener_ultima_cotizacion(1).fecha,
            datetime.date(2026, 9, 30),
        )

    def test_programa_raiz_subproceso(self):
        resultado = subprocess.run(
            [sys.executable, str(ROOT / "iniciar.py"), "--datos", str(self.directorio)],
            input="0\n", capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertIn("Cambios guardados", resultado.stdout)

    def test_programa_src_subproceso(self):
        ambiente = os.environ.copy()
        ambiente["BOOK_MANAGER_DATA_DIR"] = str(self.directorio)
        resultado = subprocess.run(
            [sys.executable, "-m", "book_manager.main"], cwd=ROOT / "src",
            input="0\n", capture_output=True, text=True,
            env=ambiente, timeout=30,
        )
        self.assertEqual(resultado.returncode, 0, resultado.stderr)

    def test_main_eof_no_pierde_cambios(self):
        nuevo = self.ui.servicio_genero.crear("Antes de EOF")
        with patch(
            "builtins.input",
            side_effect=EOFError,
        ), contextlib.redirect_stdout(io.StringIO()):
            main(data_dir=self.directorio)
        self.assertIsNotNone(
            self.reabrir().servicio_genero.leer_por_id(nuevo.id),
        )

    def test_persistencia_en_proceso_nuevo(self):
        nuevo = self.ui.servicio_genero.crear("Proceso independiente")
        ambiente = os.environ.copy()
        ambiente["PYTHONPATH"] = str(ROOT / "src")
        codigo = (
            "from book_manager.main import crear_sistema; "
            f"s=crear_sistema(data_dir={str(self.directorio)!r}); "
            f"assert s.servicio_genero.leer_por_id({nuevo.id}).nombre == 'Proceso independiente'"
        )
        r = subprocess.run(
            [sys.executable, "-c", codigo],
            env=ambiente,
            capture_output=True,
            text=True,
        )
        self.assertEqual(r.returncode, 0, r.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)

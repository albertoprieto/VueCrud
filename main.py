from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import mysql.connector
from fastapi import FastAPI, Query, Body, HTTPException, Depends, status
from typing import Optional, List
import datetime
from fastapi.responses import PlainTextResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
import json
import smtplib
from email.mime.text import MIMEText
from fastapi import APIRouter


app = FastAPI()


# Permitir CORS para tu frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://albertoprieto.github.io",
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MODELO IMEI
class IMEI(BaseModel):
    name: str
    description: str
    imei: str
    registeredBy: str
    date: str
    status: str
    technician: str | None = None
    gpsModel: str | None = None

@app.get("/ok")
def get_ok():
    return {"status": "Ok"}


@app.get("/google5bd3c87fea64a137.html", response_class=PlainTextResponse)
def google_verification():
    return "google-site-verification: google5bd3c87fea64a137.html"


@app.get("/imeis")
def get_imeis(articulo_nombre: str = None):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor(dictionary=True)
    if articulo_nombre:
        cursor.execute("SELECT * FROM imeis WHERE articulo_nombre=%s", (articulo_nombre,))
    else:
        cursor.execute("SELECT * FROM imeis")
    items = cursor.fetchall()
    cursor.close()
    db.close()
    return items

@app.get("/imeis-vendidos")
def get_imeis_vendidos(articulo_nombre: str = None):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor(dictionary=True)
    if articulo_nombre:
        cursor.execute("SELECT * FROM imeis WHERE articulo_nombre=%s", (articulo_nombre,))
    else:
        cursor.execute("SELECT * FROM imeis")
    items = cursor.fetchall()
    cursor.close()
    db.close()
    return items

@app.post("/imeis")
def add_imei(item: IMEI):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO imeis (name, description, imei, registeredBy, date, status, technician, gpsModel) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
        (item.name, item.description, item.imei, item.registeredBy, item.date, item.status, item.technician, item.gpsModel)
    )
    db.commit()
    cursor.close()
    db.close()
    return {"message": "IMEI registrado exitosamente"}

@app.put("/imeis/{imei_value}")
def update_imei(imei_value: str, imei: dict):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor()
    cursor.execute(
        "UPDATE imeis SET name=%s, description=%s, registeredBy=%s, date=%s, status=%s, technician=%s, gpsModel=%s WHERE imei=%s",
        (
            imei.get("name"),
            imei.get("description"),
            imei.get("registeredBy"),
            imei.get("date"),
            imei.get("status"),
            imei.get("technician"),
            imei.get("gpsModel"),
            imei_value
        )
    )
    db.commit()
    cursor.close()
    db.close()
    return {"message": "IMEI actualizado"}

# MODELO COTIZACION
class Cotizacion(BaseModel):
    id: Optional[int]
    cliente_id: int
    fecha: str
    descripcion: Optional[str] = ""
    monto: float
    status: Optional[str] = "Pendiente"
    usuario_id: Optional[int] = None
    observaciones: Optional[str] = ""
    articulos: Optional[dict] = None
    autorizada: Optional[bool] = False
    fecha_autorizacion: Optional[str] = None
    venta_id: Optional[int] = None

@app.get("/cotizaciones")
def get_cotizaciones():
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM cotizaciones")
    cotizaciones = cursor.fetchall()
    cursor.close()
    db.close()
    return cotizaciones

@app.get("/cotizaciones/{cotizacion_id}")
def get_cotizacion(cotizacion_id: int):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM cotizaciones WHERE id=%s", (cotizacion_id,))
    cotizacion = cursor.fetchone()
    cursor.close()
    db.close()
    if not cotizacion:
        raise HTTPException(status_code=404, detail="Cotización no encontrada")
    return cotizacion

@app.post("/cotizaciones")
def add_cotizacion(cotizacion: Cotizacion):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO cotizaciones (cliente_id, fecha, descripcion, monto, status, usuario_id, observaciones, articulos, autorizada, fecha_autorizacion, venta_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
        (
            cotizacion.cliente_id,
            cotizacion.fecha,
            cotizacion.descripcion,
            cotizacion.monto,
            cotizacion.status,
            cotizacion.usuario_id,
            cotizacion.observaciones,
            json.dumps(cotizacion.articulos) if cotizacion.articulos else None,
            cotizacion.autorizada,
            cotizacion.fecha_autorizacion,
            cotizacion.venta_id
        )
    )
    db.commit()
    cursor.close()
    db.close()
    return {"message": "Cotización registrada exitosamente"}

@app.put("/cotizaciones/{cotizacion_id}")
def update_cotizacion(cotizacion_id: int, cotizacion: Cotizacion):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor()
    cursor.execute(
        "UPDATE cotizaciones SET cliente_id=%s, fecha=%s, descripcion=%s, monto=%s, status=%s, usuario_id=%s, observaciones=%s, articulos=%s, autorizada=%s, fecha_autorizacion=%s, venta_id=%s WHERE id=%s",
        (
            cotizacion.cliente_id,
            cotizacion.fecha,
            cotizacion.descripcion,
            cotizacion.monto,
            cotizacion.status,
            cotizacion.usuario_id,
            cotizacion.observaciones,
            json.dumps(cotizacion.articulos) if cotizacion.articulos else None,
            cotizacion.autorizada,
            cotizacion.fecha_autorizacion,
            cotizacion.venta_id,
            cotizacion_id
        )
    )
    db.commit()
    cursor.close()
    db.close()
    return {"message": "Cotización actualizada exitosamente"}

@app.delete("/cotizaciones/{cotizacion_id}")
def delete_cotizacion(cotizacion_id: int):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor()
    cursor.execute("DELETE FROM cotizaciones WHERE id=%s", (cotizacion_id,))
    db.commit()
    cursor.close()
    db.close()
    return {"message": "Cotización eliminada"}

# MODELO EVENTO (imei eliminado)
class Evento(BaseModel):
    title: str
    descripcion: str
    cliente: str
    technician: str
    start: str
    status: str

@app.get("/eventos")
def get_eventos():
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM eventos")
    eventos = cursor.fetchall()
    cursor.close()
    db.close()
    return eventos

@app.patch("/eventos/{evento_id}")
def update_evento_status(evento_id: int, data: dict):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor()
    cursor.execute(
        "UPDATE eventos SET status=%s WHERE id=%s",
        (data.get("status"), evento_id)
    )
    db.commit()
    cursor.close()
    db.close()
    return {"message": "Estado del evento actualizado"}

@app.post("/eventos")
def add_evento(evento: Evento):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO eventos (title, descripcion, cliente, technician, start, status) VALUES (%s, %s, %s, %s, %s, %s)",
        (evento.title, evento.descripcion, evento.cliente, evento.technician, evento.start, evento.status)
    )
    db.commit()
    cursor.close()
    return {"message": "Evento creado exitosamente"}

class Reporte(BaseModel):
    eventoId: Optional[int] = None
    imei: Optional[str] = None
    cotizacion: str
    technician: Optional[str] = None
    start: str
    status: str
    modelo: str
    placa: str
    cliente: str
    observaciones: str
    medio_pago: Optional[str] = None
    pagado: Optional[bool] = False

@app.post("/reportes")
def add_reporte(reporte: Reporte):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO reportes (eventoId, imei, cotizacion, technician, start, status, modelo, placa, cliente, observaciones, medio_pago, pagado) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
        (
            reporte.eventoId,
            reporte.imei,
            reporte.cotizacion,
            reporte.technician,
            reporte.start,
            reporte.status,
            reporte.modelo,
            reporte.placa,
            reporte.cliente,
            reporte.observaciones,
            reporte.medio_pago,
            int(reporte.pagado) if reporte.pagado is not None else 0

        )
    )
    db.commit()
    cursor.close()
    return {"message": "Reporte creado exitosamente"}

@app.get("/reportes")
def get_reportes(eventoId: int = Query(...)):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM reportes WHERE eventoId = %s", (eventoId,))
    reportes = cursor.fetchall()
    cursor.close()
    db.close()
    return reportes

# MODELO USUARIO
class Usuario(BaseModel):
    username: str
    password: str
    perfil: str

@app.get("/usuarios")
def get_usuarios():
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, username, perfil FROM usuarios")
    usuarios = cursor.fetchall()
    cursor.close()
    db.close()
    return usuarios

@app.post("/usuarios")
def add_usuario(usuario: Usuario):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO usuarios (username, password, perfil) VALUES (%s, %s, %s)",
        (usuario.username, usuario.password, usuario.perfil)
    )
    db.commit()
    cursor.close()
    db.close()
    return {"message": "Usuario registrado exitosamente"}

class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/usuarios/login")
def login_usuario(login: LoginRequest):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "SELECT username, perfil FROM usuarios WHERE username=%s AND password=%s",
        (login.username, login.password)
    )
    user = cursor.fetchone()
    cursor.close()
    db.close()
    if user:
        return {"success": True, "user": user}
    else:
        return {"success": False}

# MODELO ARTICULO
class Articulo(BaseModel):
    id: Optional[int]
    codigo: str
    nombre: str
    pagina: str
    tipo: Optional[str]
    sku: Optional[str]
    unidad: Optional[str]
    precioVenta: Optional[float]
    impuesto: Optional[str]   # <-- AGREGA ESTA LÍNEA
    descripcion: Optional[str]
    stock: Optional[int]
    ubicacion_id: Optional[int]
    precioCompra: Optional[float]
    codigoSat: Optional[str]
    unidadSat: Optional[str]
    codigoUnidadSat: Optional[str]
    codigo: Optional[str] = ""
    pagina: Optional[str] = ""

@app.get("/articulos")
def get_articulos():
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM articulos WHERE stock > 0")
    articulos = cursor.fetchall()
    cursor.close()
    db.close()
    return articulos

@app.post("/articulos")
def add_articulo(articulo: Articulo):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO articulos (codigo, nombre, pagina, tipo, sku, unidad, precioVenta, impuesto, descripcion, precioCompra, codigoSat, unidadSat, codigoUnidadSat) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
        (
            articulo.codigo,
            articulo.nombre,
            articulo.pagina,
            articulo.tipo,
            articulo.sku,
            articulo.unidad,
            articulo.precioVenta,
            articulo.impuesto,
            articulo.descripcion,
            articulo.precioCompra,
            articulo.codigoSat,
            articulo.unidadSat,
            articulo.codigoUnidadSat
        )
    )
    db.commit()
    cursor.close()
    db.close()
    return {"message": "Artículo registrado exitosamente"}

@app.put("/articulos/{articulo_id}")
def update_articulo(articulo_id: int, articulo: dict):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor()
    cursor.execute(
        "UPDATE articulos SET codigo=%s, nombre=%s, pagina=%s, tipo=%s, sku=%s, unidad=%s, precioVenta=%s, impuesto=%s, descripcion=%s, precioCompra=%s, codigoSat=%s, unidadSat=%s, codigoUnidadSat=%s WHERE id=%s",
        (
            articulo.get("codigo"),
            articulo.get("nombre"),
            articulo.get("pagina"),
            articulo.get("tipo"),
            articulo.get("sku"),
            articulo.get("unidad"),
            articulo.get("precioVenta"),
            articulo.get("impuesto"),
            articulo.get("descripcion"),
            articulo.get("precioCompra"),
            articulo.get("codigoSat"),
            articulo.get("unidadSat"),
            articulo.get("codigoUnidadSat"),
            articulo_id
        )
    )
    db.commit()
    cursor.close()
    db.close()
    return {"message": "Artículo actualizado"}

@app.delete("/articulos/{articulo_id}")
def delete_articulo(articulo_id: int):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor()
    cursor.execute("DELETE FROM articulos WHERE id=%s", (articulo_id,))
    db.commit()
    cursor.close()
    db.close()
    return {"message": "Artículo eliminado"}

@app.get("/articulos/{articulo_id}/stock")
def get_stock_articulo(articulo_id: int):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM imeis WHERE articulo_id=%s", (articulo_id,))
    stock = cursor.fetchone()[0]
    cursor.close()
    db.close()
    return {"stock": stock}

@app.post("/articulos/{articulo_id}/asignar-imeis")
def asignar_imeis_a_articulo(articulo_id: int, imeis: list[str]):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor()
    for imei in imeis:
        cursor.execute("UPDATE imeis SET articulo_id=%s WHERE imei=%s", (articulo_id, imei))
    db.commit()
    cursor.close()
    db.close()
    return {"message": "IMEIs asignados"}

from pydantic import BaseModel

class RegistrarAsignarIMEIsRequest(BaseModel):
    imeis: list[str]
    registeredBy: str = "Sistema"

@app.post("/articulos/{articulo_id}/registrar-y-asignar-imeis")
def registrar_y_asignar_imeis(articulo_id: int, data: RegistrarAsignarIMEIsRequest):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for imei in data.imeis:
        cursor.execute("UPDATE imeis SET articulo_id=%s WHERE imei=%s", (articulo_id, imei))
        if cursor.rowcount == 0:
            cursor.execute(
                "INSERT INTO imeis (name, description, imei, registeredBy, date, status, articulo_id) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                ("IMEI", data.registeredBy, imei, data.registeredBy, now, "Disponible", articulo_id)
            )
    db.commit()
    cursor.close()
    db.close()
    return {"message": "IMEIs registrados y asignados"}

class RegistrarAsignarIMEIsNombreRequest(BaseModel):
    imeis: list[str]
    registeredBy: str = "Sistema"

@app.post("/articulos/nombre/{articulo_nombre}/registrar-y-asignar-imeis")
def registrar_y_asignar_imeis_nombre(articulo_nombre: str, data: RegistrarAsignarIMEIsNombreRequest):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for imei in data.imeis:
        cursor.execute("UPDATE imeis SET articulo_nombre=%s WHERE imei=%s", (articulo_nombre, imei))
        if cursor.rowcount == 0:
            cursor.execute(
                "INSERT INTO imeis (name, description, imei, registeredBy, date, status, articulo_nombre) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                ("IMEI", data.registeredBy, imei, data.registeredBy, now, "Disponible", articulo_nombre)
            )
    db.commit()
    cursor.close()
    db.close()
    return {"message": "IMEIs registrados y asignados"}

@app.get("/articulos/nombre/{articulo_nombre}/stock")
def get_stock_articulo_nombre(articulo_nombre: str):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM imeis WHERE articulo_nombre=%s", (articulo_nombre,))
    stock = cursor.fetchone()[0]
    cursor.close()
    db.close()
    return {"stock": stock}

# MODELO CLIENTE
class Cliente(BaseModel):
    nombre: str
    correo: Optional[str] = ""
    direccion: Optional[str] = ""
    telefonos: Optional[list[str]] = []
    usuarios: Optional[list[str]] = []
    plataformas: Optional[list[str]] = []

@app.get("/clientes")
def get_clientes():
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM clientes")
    clientes = cursor.fetchall()
    for cliente in clientes:
        # Obtener teléfonos
        cursor.execute("SELECT telefono FROM telefonos_cliente WHERE cliente_id=%s", (cliente["id"],))
        cliente["telefonos"] = [t["telefono"] for t in cursor.fetchall()]
        # Obtener usuarios
        cursor.execute("SELECT usuario FROM usuarios_cliente WHERE cliente_id=%s", (cliente["id"],))
        cliente["usuarios"] = [u["usuario"] for u in cursor.fetchall()]
        # Obtener plataformas
        cursor.execute("SELECT plataforma FROM plataformas_cliente WHERE cliente_id=%s", (cliente["id"],))
        cliente["plataformas"] = [p["plataforma"] for p in cursor.fetchall()]
    cursor.close()
    db.close()
    return clientes

@app.post("/clientes")
def add_cliente(cliente: Cliente):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO clientes (nombre, correo, direccion) VALUES (%s, %s, %s)",
        (cliente.nombre, cliente.correo, cliente.direccion)
    )
    cliente_id = cursor.lastrowid
    for tel in cliente.telefonos or []:
        cursor.execute("INSERT INTO telefonos_cliente (cliente_id, telefono) VALUES (%s, %s)", (cliente_id, tel))
    for usuario in cliente.usuarios or []:
        cursor.execute("INSERT INTO usuarios_cliente (cliente_id, usuario) VALUES (%s, %s)", (cliente_id, usuario))
    for plataforma in cliente.plataformas or []:
        cursor.execute("INSERT INTO plataformas_cliente (cliente_id, plataforma) VALUES (%s, %s)", (cliente_id, plataforma))
    db.commit()
    cursor.close()
    db.close()
    return {"message": "Cliente registrado exitosamente"}

@app.put("/clientes/{cliente_id}")
def update_cliente(cliente_id: int, cliente: Cliente):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor()
    cursor.execute(
        "UPDATE clientes SET nombre=%s, correo=%s, direccion=%s WHERE id=%s",
        (cliente.nombre, cliente.correo, cliente.direccion, cliente_id)
    )
    cursor.execute("DELETE FROM telefonos_cliente WHERE cliente_id=%s", (cliente_id,))
    for tel in cliente.telefonos or []:
        cursor.execute("INSERT INTO telefonos_cliente (cliente_id, telefono) VALUES (%s, %s)", (cliente_id, tel))
    cursor.execute("DELETE FROM usuarios_cliente WHERE cliente_id=%s", (cliente_id,))
    for usuario in cliente.usuarios or []:
        cursor.execute("INSERT INTO usuarios_cliente (cliente_id, usuario) VALUES (%s, %s)", (cliente_id, usuario))
    cursor.execute("DELETE FROM plataformas_cliente WHERE cliente_id=%s", (cliente_id,))
    for plataforma in cliente.plataformas or []:
        cursor.execute("INSERT INTO plataformas_cliente (cliente_id, plataforma) VALUES (%s, %s)", (cliente_id, plataforma))
    db.commit()
    cursor.close()
    db.close()
    return {"message": "Cliente actualizado"}

@app.delete("/clientes/{cliente_id}")
def delete_cliente(cliente_id: int):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor()
    cursor.execute("DELETE FROM clientes WHERE id=%s", (cliente_id,))
    db.commit()
    cursor.close()
    db.close()
    return {"message": "Cliente eliminado"}

class DetalleVenta(BaseModel):
    articulo_id: int
    cantidad: int
    precio_unitario: float
    imei: Optional[str] = None  # Si aplica

class Venta(BaseModel):
    cliente_id: int
    fecha: Optional[str] = None
    folio: Optional[str] = None
    referencia: Optional[str] = None
    fecha_envio: Optional[str] = None
    terminos_pago: Optional[str] = None
    metodo_entrega: Optional[str] = None
    vendedor: Optional[str] = None
    almacen: Optional[str] = None
    descuento: Optional[float] = 0
    notas_cliente: Optional[str] = ""
    terminos_condiciones: Optional[str] = ""
    total: float
    observaciones: Optional[str] = ""
    articulos: list[DetalleVenta]

@app.post("/ventas")
def crear_venta(venta: Venta):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor()
    fecha = venta.fecha or datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        """
        INSERT INTO ventas
        (cliente_id, fecha, folio, referencia, fecha_envio, terminos_pago, metodo_entrega, vendedor, almacen, descuento, notas_cliente, terminos_condiciones, total, observaciones)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            venta.cliente_id, fecha, venta.folio, venta.referencia, venta.fecha_envio, venta.terminos_pago,
            venta.metodo_entrega, venta.vendedor, venta.almacen, venta.descuento, venta.notas_cliente,
            venta.terminos_condiciones, venta.total, venta.observaciones
        )
    )
    venta_id = cursor.lastrowid

    for item in venta.articulos:
        # Obtener el tipo de artículo
        cursor.execute("SELECT tipo FROM articulos WHERE id=%s", (item.articulo_id,))
        tipo_row = cursor.fetchone()
        tipo = tipo_row[0].lower() if tipo_row and tipo_row[0] else ""

        # Validar duplicado de IMEI solo si no es servicio y tiene IMEI
        if tipo != "servicio" and getattr(item, "imei", None):
            cursor.execute("SELECT COUNT(*) FROM detalle_venta WHERE imei=%s", (item.imei,))
            if cursor.fetchone()[0] > 0:
                db.rollback()
                cursor.close()
                db.close()
                raise HTTPException(status_code=400, detail=f"El IMEI {item.imei} ya fue vendido.")

        cursor.execute(
            "INSERT INTO detalle_venta (venta_id, articulo_id, cantidad, precio_unitario, subtotal, imei) VALUES (%s, %s, %s, %s, %s, %s)",
            (venta_id, item.articulo_id, item.cantidad, item.precio_unitario, item.cantidad * item.precio_unitario, getattr(item, "imei", None))
        )

        # Si es servicio, NO descontar stock ni validar stock ni IMEI
        if tipo == "servicio":
            continue

        # Descontar inventario solo si NO es servicio
        if getattr(item, "imei", None):
            # Actualiza el status del IMEI
            cursor.execute(
                "UPDATE imeis SET status='Vendido' WHERE imei=%s AND status IN ('Disponible', 'Devuelto')",
                (item.imei,)
            )
            # Descuenta stock del artículo también
            cursor.execute(
                "UPDATE articulos SET stock = stock - 1 WHERE id = %s AND stock >= 1",
                (item.articulo_id,)
            )
        else:
            cursor.execute(
                "UPDATE articulos SET stock = stock - %s WHERE id = %s AND stock >= %s",
                (item.cantidad, item.articulo_id, item.cantidad)
            )
            if cursor.rowcount == 0:
                db.rollback()
                cursor.close()
                db.close()
                raise HTTPException(status_code=400, detail=f"Stock insuficiente para el artículo {item.articulo_id}")

    db.commit()
    cursor.close()
    db.close()
    return {"message": "Venta registrada exitosamente", "venta_id": venta_id}

@app.get("/ventas")
def listar_ventas():
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT v.*, c.nombre as cliente_nombre
        FROM ventas v
        JOIN clientes c ON v.cliente_id = c.id
        ORDER BY v.fecha DESC
    """)
    ventas = cursor.fetchall()
    cursor.close()
    db.close()
    return ventas

@app.get("/ventas/{venta_id}/detalle")
def detalle_venta(venta_id: int):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT dv.*, a.nombre as articulo_nombre
        FROM detalle_venta dv
        JOIN articulos a ON dv.articulo_id = a.id
        WHERE dv.venta_id = %s
    """, (venta_id,))
    detalle = cursor.fetchall()
    cursor.close()
    db.close()
    return detalle

@app.get("/articulos/todos")
def get_todos_articulos():
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM articulos")
    articulos = cursor.fetchall()
    cursor.close()
    db.close()
    return articulos

# MODELO UBICACION
class Ubicacion(BaseModel):
    id: int
    nombre: str
    descripcion: str = ""
    encargado: str = ""
    telefonos: list[str] = []
    correo: str = ""
    direccion: str = ""
    capacidad_maxima: int = 0
    estado: str = "activa"  # activa/inactiva

@app.get("/ubicaciones")
def get_ubicaciones():
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT 
            id, 
            nombre, 
            descripcion, 
            encargado, 
            telefonos, 
            correo, 
            direccion, 
            capacidad_maxima, 
            estado
        FROM ubicaciones
    """)
    ubicaciones = cursor.fetchall()
    # Si telefonos es string, conviértelo a lista
    for u in ubicaciones:
        if isinstance(u.get("telefonos"), str):
            try:
                import json
                u["telefonos"] = json.loads(u["telefonos"])
            except Exception:
                u["telefonos"] = [u["telefonos"]]
    cursor.close()
    db.close()
    return ubicaciones

@app.post("/ubicaciones")
def add_ubicacion(ubicacion: Ubicacion):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO ubicaciones (nombre, descripcion, encargado, telefonos, correo, direccion, capacidad_maxima, estado) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
        (
            ubicacion.nombre,
            ubicacion.descripcion,
            ubicacion.encargado,
            json.dumps(ubicacion.telefonos),
            ubicacion.correo,
            ubicacion.direccion,
            ubicacion.capacidad_maxima,
            ubicacion.estado
        )
    )
    db.commit()
    cursor.close()
    db.close()
    return {"message": "Ubicación registrada exitosamente"}

@app.put("/ubicaciones/{ubicacion_id}")
def update_ubicacion(ubicacion_id: int, ubicacion: Ubicacion):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor()
    cursor.execute(
        "UPDATE ubicaciones SET nombre=%s, descripcion=%s, encargado=%s, telefonos=%s, correo=%s, direccion=%s, capacidad_maxima=%s, estado=%s WHERE id=%s",
        (
            ubicacion.nombre,
            ubicacion.descripcion,
            ubicacion.encargado,
            json.dumps(ubicacion.telefonos),
            ubicacion.correo,
            ubicacion.direccion,
            ubicacion.capacidad_maxima,
            ubicacion.estado,
            ubicacion_id
        )
    )
    db.commit()
    cursor.close()
    db.close()
    return {"message": "Ubicación actualizada"}

@app.delete("/ubicaciones/{ubicacion_id}")
def delete_ubicacion(ubicacion_id: int):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor()
    cursor.execute("DELETE FROM ubicaciones WHERE id=%s", (ubicacion_id,))
    db.commit()
    cursor.close()
    db.close()
    return {"message": "Ubicación eliminada"}

from typing import List

class AsignarIMEIsUbicacionRequest(BaseModel):
    imeis: List[str]

@app.get("/ubicaciones/{ubicacion_id}/imeis")
def get_imeis_por_ubicacion(ubicacion_id: int):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT i.*, a.nombre as articulo_nombre, a.sku as sku
        FROM imeis i
        LEFT JOIN articulos a ON i.articulo_nombre = a.nombre
        WHERE i.ubicacion_id = %s
    """, (ubicacion_id,))
    imeis = cursor.fetchall()
    cursor.close()
    db.close()
    return imeis

@app.post("/ubicaciones/{ubicacion_id}/asignar-imeis")
def asignar_imeis_a_ubicacion(ubicacion_id: int, data: AsignarIMEIsUbicacionRequest):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor()
    for imei in data.imeis:
        cursor.execute("UPDATE imeis SET ubicacion_id=%s WHERE imei=%s", (ubicacion_id, imei))
    db.commit()
    cursor.close()
    db.close()
    return {"message": "IMEIs asignados a la ubicación"}

@app.post("/ubicaciones/{ubicacion_id}/remover-imeis")
def remover_ubicacion(ubicacion_id: int, data: AsignarIMEIsUbicacionRequest):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor()
    for imei in data.imeis:
        cursor.execute("UPDATE imeis SET ubicacion_id=NULL WHERE imei=%s AND ubicacion_id=%s", (imei, ubicacion_id))
    db.commit()
    cursor.close()
    db.close()
    return {"message": "IMEIs removidos de la ubicación"}

class TransferirIMEIsRequest(BaseModel):
    imeis: List[str]
    destino_id: int

@app.post("/ubicaciones/transferir-imeis")
def transferir_imeis(request: TransferirIMEIsRequest):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor()
    for imei in request.imeis:
        cursor.execute("UPDATE imeis SET ubicacion_id=%s WHERE imei=%s", (request.destino_id, imei))
    db.commit()
    cursor.close()
    db.close()
    return {"message": "IMEIs transferidos correctamente"}

@app.get("/buscar-imei")
def buscar_imei(digitos: str):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor(dictionary=True)
    query = """
        SELECT i.imei, i.articulo_nombre, a.sku, i.status, u.nombre as ubicacion
        FROM imeis i
        LEFT JOIN ubicaciones u ON i.ubicacion_id = u.id
        LEFT JOIN articulos a ON i.articulo_nombre = a.nombre
        WHERE i.imei LIKE %s
    """
    cursor.execute(query, ('%' + digitos,))
    resultados = cursor.fetchall()
    cursor.close()
    db.close()
    return resultados

@app.post("/imeis/{imei}/devolver")
def devolver_imei(imei: str, data: dict = Body(...)):
    motivo = data.get("motivo")
    usuario = data.get("usuario", "sistema")
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT articulo_id FROM imeis WHERE imei=%s", (imei,))
    row = cursor.fetchone()
    articulo_id = row["articulo_id"] if row else None
    articulo_nombre = ""
    if articulo_id:
        cursor.execute("SELECT nombre FROM articulos WHERE id=%s", (articulo_id,))
        art = cursor.fetchone()
        articulo_nombre = art["nombre"] if art else ""
    cursor.execute(
        "UPDATE imeis SET status='Devuelto', motivo_devolucion=%s WHERE imei=%s",
        (motivo, imei)
    )
    db.commit()
    cursor.close()
    db.close()
    registrar_movimiento(usuario, "devolucion", articulo_id, articulo_nombre, imei, None, None, motivo)
    return {"message": "IMEI marcado como devuelto"}

@app.post("/articulos/sincronizar-stock-imeis")
def sincronizar_stock_articulos():
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor()
    # Actualiza el stock de todos los artículos según la cantidad de IMEIs disponibles o devueltos
    cursor.execute("""
        UPDATE articulos a
        SET stock = (
            SELECT COUNT(*) FROM imeis i
            WHERE i.articulo_id = a.id AND i.status IN ('Disponible', 'Devuelto')
        )
    """)
    db.commit()
    cursor.close()
    db.close()
    return {"message": "Stock de artículos sincronizado con IMEIs"}

@app.post("/ventas/{venta_id}/asignar-tecnico")
def asignar_tecnico_venta(venta_id: int, data: dict = Body(...)):
    tecnico_id = data.get("tecnico_id")
    fecha_servicio = data.get("fecha_servicio")
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO venta_tecnico (venta_id, tecnico_id, fecha_servicio) VALUES (%s, %s, %s)",
        (venta_id, tecnico_id, fecha_servicio)
    )
    db.commit()
    cursor.close()
    db.close()
    return {"message": "Técnico asignado a la venta"}

@app.get("/ventas/{venta_id}/tecnico")
def get_tecnico_venta(venta_id: int):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT u.* FROM venta_tecnico vt
        JOIN usuarios u ON vt.tecnico_id = u.id
        WHERE vt.venta_id = %s
        ORDER BY vt.fecha_asignacion DESC LIMIT 1
    """, (venta_id,))
    tecnico = cursor.fetchone()
    cursor.close()
    db.close()
    return tecnico

@app.delete("/ventas/{venta_id}/asignar-tecnico")
def eliminar_asignacion_tecnico(venta_id: int):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor()
    cursor.execute("DELETE FROM venta_tecnico WHERE venta_id = %s", (venta_id,))
    db.commit()
    cursor.close()
    db.close()
    return {"message": "Asignación eliminada"}

@app.get("/asignaciones-tecnicos")
def get_asignaciones_tecnicos():
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT vt.id, vt.fecha_servicio, vt.venta_id, v.cliente_id, u.username as tecnico, v.fecha as fecha_venta
        FROM venta_tecnico vt
        JOIN usuarios u ON vt.tecnico_id = u.id
        JOIN ventas v ON vt.venta_id = v.id
    """)
    asignaciones = cursor.fetchall()
    cursor.close()
    db.close()
    return asignaciones

class ReporteServicio(BaseModel):
    asignacion_id: int
    tipo_servicio: str
    lugar_instalacion: str = ""
    marca: str = ""
    submarca: str = ""
    modelo: str = ""
    placas: str = ""
    color: str = ""
    numero_economico: str = ""
    equipo_plan: str = ""
    imei: str = ""
    serie: str = ""
    accesorios: str = ""
    sim_proveedor: str = ""
    sim_serie: str = ""
    sim_instalador: str = ""
    sim_telefono: str = ""
    bateria: str = ""
    ignicion: str = ""
    corte: str = ""
    ubicacion_corte: str = ""
    observaciones: str = ""
    plataforma: str = ""
    usuario: str = ""
    subtotal: str = ""
    forma_pago: str = ""
    pagado: bool = False
    nombre_cliente: str = ""
    firma_cliente: str = ""
    nombre_instalador: str = ""
    firma_instalador: str = ""
    monto_tecnico: float = 0
    viaticos: float = 0

@app.post("/reportes-servicio")
def add_reporte_servicio(reporte: ReporteServicio):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO reportes_servicio (asignacion_id, tipo_servicio, lugar_instalacion, marca, submarca, modelo, placas, color, numero_economico, equipo_plan, imei, serie, accesorios, sim_proveedor, sim_serie, sim_instalador, sim_telefono, bateria, ignicion, corte, ubicacion_corte, observaciones, plataforma, usuario, subtotal, forma_pago, pagado, nombre_cliente, firma_cliente, nombre_instalador, firma_instalador, monto_tecnico, viaticos) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
        (
            reporte.asignacion_id, reporte.tipo_servicio, reporte.lugar_instalacion, reporte.marca, reporte.submarca,
            reporte.modelo, reporte.placas, reporte.color, reporte.numero_economico, reporte.equipo_plan,
            reporte.imei, reporte.serie, reporte.accesorios, reporte.sim_proveedor, reporte.sim_serie,
            reporte.sim_instalador, reporte.sim_telefono, reporte.bateria, reporte.ignicion, reporte.corte,
            reporte.ubicacion_corte, reporte.observaciones, reporte.plataforma, reporte.usuario, reporte.subtotal,
            reporte.forma_pago, int(reporte.pagado), reporte.nombre_cliente, reporte.firma_cliente,
            reporte.nombre_instalador, reporte.firma_instalador, reporte.monto_tecnico,
            reporte.viaticos
        )
    )
    db.commit()
    cursor.close()
    db.close()
    return {"message": "Reporte de servicio creado exitosamente"}

@app.get("/reportes-servicio")
def get_reporte_servicio(asignacion_id: int = Query(...)):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM reportes_servicio WHERE asignacion_id = %s", (asignacion_id,))
    reporte = cursor.fetchone()
    cursor.close()
    db.close()
    return reporte

@app.get("/reportes-servicio-todos")
def get_reportes_servicio_todos():
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM reportes_servicio ORDER BY id DESC")
    reportes = cursor.fetchall()
    cursor.close()
    db.close()
    return reportes

@app.put("/reportes-servicio/{reporte_id}")
def update_reporte_servicio(reporte_id: int, reporte: dict):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor()
    campos = []
    valores = []
    for k, v in reporte.items():
        if k != "id":
            campos.append(f"{k}=%s")
            valores.append(v)
    valores.append(reporte_id)
    sql = f"UPDATE reportes_servicio SET {', '.join(campos)} WHERE id=%s"
    cursor.execute(sql, valores)
    db.commit()
    cursor.close()
    db.close()
    return {"message": "Reporte actualizado"}

@app.delete("/reportes-servicio/{reporte_id}")
def delete_reporte_servicio(reporte_id: int):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor()
    cursor.execute("DELETE FROM reportes_servicio WHERE id=%s", (reporte_id,))
    db.commit()
    cursor.close()
    db.close()
    return {"message": "Reporte eliminado"}

@app.delete("/imeis/{imei}")
def delete_imei(imei: str):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor()
    cursor.execute("DELETE FROM imeis WHERE imei=%s", (imei,))
    db.commit()
    cursor.close()
    db.close()
    return {"message": "IMEI eliminado"}

SECRET_KEY = "super-secret-key"  # Usa una variable de entorno en producción
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_user(username, password):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios WHERE username=%s", (username,))
    user = cursor.fetchone()
    cursor.close()
    db.close()
    if not user or not verify_password(password, user["password"]):
        return None
    return user

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user["username"], "user_id": user["id"]})
    return {"access_token": access_token, "token_type": "bearer"}

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        if username is None or user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    # Aquí puedes consultar el usuario en la base de datos si lo necesitas
    return {"username": username, "user_id": user_id}

@app.get("/ubicaciones/{ubicacion_id}/articulos-stock")
def get_articulos_stock_por_ubicacion(ubicacion_id: int):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT a.*, COUNT(i.id) as stock
        FROM articulos a
        JOIN imeis i ON i.articulo_id = a.id
        WHERE i.ubicacion_id = %s AND i.status IN ('Disponible', 'Devuelto')
        GROUP BY a.id
    """, (ubicacion_id,))
    articulos = cursor.fetchall()
    cursor.close()
    db.close()
    return articulos

class EmailRequest(BaseModel):
    destinatario: str
    asunto: str
    cuerpo: str

@app.post("/enviar-cotizacion")
def enviar_cotizacion(req: EmailRequest):
    smtp_server = "smtpout.secureserver.net"
    smtp_port = 465
    smtp_user = "pepe@gpsubicacionapi.com"
    smtp_pass = ""

    msg = MIMEText(req.cuerpo)
    msg["Subject"] = req.asunto
    msg["From"] = smtp_user
    msg["To"] = req.destinatario

    try:
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, [req.destinatario], msg.as_string())
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/cotizaciones/enviar")
def enviar_cotizacion_al_cliente(data: dict = Body(...)):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO cotizaciones_enviadas (cotizacion_id, cliente_id, fecha_envio, status, email_destino) VALUES (%s, %s, NOW(), %s, %s)",
        (
            data["cotizacion_id"],
            data["cliente_id"],
            data.get("status", "Sin aprobar"),
            data.get("email_destino", "")
        )
    )
    db.commit()
    cursor.close()
    db.close()
    return {"message": "Cotización enviada y registrada"}

@app.get("/imeis/{imei}")
def get_imei(imei: str):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor()
    cursor.execute("SELECT motivo_devolucion FROM imeis WHERE imei=%s", (imei,))
    row = cursor.fetchone()
    return {"motivo_devolucion": row[0] if row else ""}

def registrar_movimiento(usuario, evento, articulo_id, articulo_nombre, imei, ubicacion_origen, ubicacion_destino, motivo):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO movimientos_inventario
        (usuario, evento, articulo_id, articulo_nombre, imei, ubicacion_origen, ubicacion_destino, motivo)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (usuario, evento, articulo_id, articulo_nombre, imei, ubicacion_origen, ubicacion_destino, motivo))
    db.commit()
    cursor.close()
    db.close()

@app.get("/movimientos-inventario")
def get_movimientos_inventario():
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM movimientos_inventario ORDER BY fecha DESC")
    movimientos = cursor.fetchall()
    cursor.close()
    db.close()
    return movimientos

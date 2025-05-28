from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import mysql.connector
from fastapi import FastAPI, Query, Body, HTTPException
from typing import Optional, List
import datetime

app = FastAPI()

# Permitir CORS para tu frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cambia esto a tu dominio en producción
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
    cliente: str
    telefono: str
    correo: str
    descripcion: str
    modelo: str
    tipo: str
    monto: float
    observaciones: str = ""
    fecha: str
    status: str

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
        "INSERT INTO cotizaciones (cliente, telefono, correo, descripcion, modelo, tipo, monto, observaciones, fecha, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
        (
            cotizacion.cliente,
            cotizacion.telefono,
            cotizacion.correo,
            cotizacion.descripcion,
            cotizacion.modelo,
            cotizacion.tipo,
            cotizacion.monto,
            cotizacion.observaciones,
            cotizacion.fecha,
            cotizacion.status
        )
    )
    db.commit()
    cursor.close()
    db.close()
    return {"message": "Cotización registrada exitosamente"}

@app.put("/cotizaciones/{cotizacion_id}")
def update_cotizacion(cotizacion_id: int, cotizacion: dict):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor()
    cursor.execute(
        "UPDATE cotizaciones SET cliente=%s, telefono=%s, correo=%s, descripcion=%s, modelo=%s, tipo=%s, monto=%s, observaciones=%s, fecha=%s, status=%s WHERE id=%s",
        (
            cotizacion.get("cliente"),
            cotizacion.get("telefono"),
            cotizacion.get("correo"),
            cotizacion.get("descripcion"),
            cotizacion.get("modelo"),
            cotizacion.get("tipo"),
            cotizacion.get("monto"),
            cotizacion.get("observaciones"),
            cotizacion.get("fecha"),
            cotizacion.get("status"),
            cotizacion_id
        )
    )
    db.commit()
    cursor.close()
    db.close()
    return {"message": "Cotización actualizada exitosamente"}

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
    db.close()
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
    cursor.execute("SELECT username, perfil FROM usuarios")
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
    codigo: str
    nombre: str
    pagina: str
    tipo: str | None = None
    sku: str | None = None
    unidad: str | None = None
    precioVenta: float | None = None
    impuesto: str | None = None
    descripcion: str | None = None
    precioCompra: float | None = None
    codigoSat: str | None = None
    unidadSat: str | None = None
    codigoUnidadSat: str | None = None

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
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
    telefono: Optional[str] = None
    correo: Optional[str] = None
    direccion: Optional[str] = None
    usuario: Optional[str] = None
    plataforma: Optional[str] = None

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
        "INSERT INTO clientes (nombre, telefono, correo, direccion, usuario, plataforma) VALUES (%s, %s, %s, %s, %s, %s)",
        (cliente.nombre, cliente.telefono, cliente.correo, cliente.direccion, cliente.usuario, cliente.plataforma)
    )
    db.commit()
    cursor.close()
    db.close()
    return {"message": "Cliente registrado exitosamente"}

@app.put("/clientes/{cliente_id}")
def update_cliente(cliente_id: int, cliente: dict):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor()
    cursor.execute(
        "UPDATE clientes SET nombre=%s, telefono=%s, correo=%s, direccion=%s, usuario=%s, plataforma=%s WHERE id=%s",
        (
            cliente.get("nombre"),
            cliente.get("telefono"),
            cliente.get("correo"),
            cliente.get("direccion"),
            cliente.get("usuario"),
            cliente.get("plataforma"),
            cliente_id
        )
    )
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
        "INSERT INTO ventas (cliente_id, fecha, total, observaciones) VALUES (%s, %s, %s, %s)",
        (venta.cliente_id, fecha, venta.total, venta.observaciones)
    )
    venta_id = cursor.lastrowid

    for item in venta.articulos:
        # Obtener el tipo de artículo
        cursor.execute("SELECT tipo FROM articulos WHERE id=%s", (item.articulo_id,))
        tipo_row = cursor.fetchone()
        tipo = tipo_row[0].lower() if tipo_row and tipo_row[0] else ""

        cursor.execute(
            "INSERT INTO detalle_venta (venta_id, articulo_id, cantidad, precio_unitario, subtotal, imei) VALUES (%s, %s, %s, %s, %s, %s)",
            (venta_id, item.articulo_id, item.cantidad, item.precio_unitario, item.cantidad * item.precio_unitario, getattr(item, "imei", None))
        )

        # Si es servicio, NO descontar stock ni validar stock ni IMEI
        if tipo == "servicio":
            continue

        # Descontar inventario solo si NO es servicio
        if getattr(item, "imei", None):
            cursor.execute("UPDATE imeis SET status='Vendido' WHERE imei=%s AND status='Disponible'", (item.imei,))
            if cursor.rowcount == 0:
                db.rollback()
                cursor.close()
                db.close()
                raise HTTPException(status_code=400, detail=f"IMEI {item.imei} no disponible")
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
    nombre: str
    descripcion: Optional[str] = None

@app.get("/ubicaciones")
def get_ubicaciones():
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM ubicaciones")
    ubicaciones = cursor.fetchall()
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
        "INSERT INTO ubicaciones (nombre, descripcion) VALUES (%s, %s)",
        (ubicacion.nombre, ubicacion.descripcion)
    )
    db.commit()
    cursor.close()
    db.close()
    return {"message": "Ubicación registrada exitosamente"}

@app.put("/ubicaciones/{ubicacion_id}")
def update_ubicacion(ubicacion_id: int, ubicacion: dict):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor()
    cursor.execute(
        "UPDATE ubicaciones SET nombre=%s, descripcion=%s WHERE id=%s",
        (ubicacion.get("nombre"), ubicacion.get("descripcion"), ubicacion_id)
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
def remover_imeis_de_ubicacion(ubicacion_id: int, data: AsignarIMEIsUbicacionRequest):
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
        SELECT i.imei, i.articulo_nombre, i.status, u.nombre as ubicacion
        FROM imeis i
        LEFT JOIN ubicaciones u ON i.ubicacion_id = u.id
        WHERE i.imei LIKE %s
    """
    cursor.execute(query, ('%' + digitos,))
    resultados = cursor.fetchall()
    cursor.close()
    db.close()
    return resultados

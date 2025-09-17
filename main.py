from dotenv import load_dotenv
# satcfdi para facturación oficial SAT
from decimal import Decimal
from satcfdi.models import Signer
from satcfdi.create.cfd import cfdi40
from satcfdi.create.cfd.cfdi40 import Comprobante, Emisor, Receptor, Concepto, Traslado
from satcfdi.create.cfd.catalogos import RegimenFiscal, UsoCFDI, MetodoPago, Impuesto, TipoFactor

import base64
import os
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
from twilio.rest import Client
from fastapi import Request
from fastapi import UploadFile, File, Form
from fastapi.staticfiles import StaticFiles


app = FastAPI()

# Helper para construir URL pública consistente
def build_public_url(rel_path: str, request: Request | None = None) -> str:
    import os as _os
    if not rel_path:
        return None
    # Normalizar ruta relativa eliminando prefijos ./
    rel = rel_path.lstrip('./')
    # Asegurar que empiece por uploads/
    if not rel.startswith('uploads/'):
        if rel.startswith('/'):
            rel = rel.lstrip('/')
        if not rel.startswith('uploads/'):
            rel = f"uploads/{rel}"
    base_env = _os.getenv('BASE_URL_PUBLIC', '').strip()
    if not base_env and request is not None:
        # Fallback a base_url de la request solo si no hay var de entorno
        base_env = str(request.base_url)
    if base_env and not base_env.endswith('/'):
        base_env += '/'
    return f"{base_env}{rel}" if base_env else rel

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

# Servir archivos de comprobantes
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")



load_dotenv()

class Producto(BaseModel):
    ClaveProdServ: str
    ClaveUnidad: str
    Unidad: str
    Descripcion: str
    ValorUnitario: float
    Importe: float
    Cantidad: float

class FacturaRequest(BaseModel):
    nombre_cliente: str
    rfc_cliente: str
    uso_cfdi: str
    productos: list[Producto]
    metodo_pago: str
    forma_pago: str
    total: float


@app.post("/api/facturar")
def facturar(data: FacturaRequest):
    from satcfdi import render
    from satcfdi.render import BODY_TEMPLATE
    CERT_PATH = os.getenv("CSD_CERT_PATH")
    KEY_PATH = os.getenv("CSD_KEY_PATH")
    KEY_PASS = os.getenv("CSD_KEY_PASS")
    RFC = os.getenv("CSD_RFC", "RAQÑ7701212M3")

    # Crear conceptos
    conceptos = [
        Concepto(
            clave_prod_serv=p.ClaveProdServ,
            cantidad=p.Cantidad,
            clave_unidad=p.ClaveUnidad,
            unidad=p.Unidad,
            descripcion=p.Descripcion,
            valor_unitario=p.ValorUnitario
        ) for p in data.productos
    ]


    # Crear comprobante CFDI
    comprobante = cfdi40.Comprobante(
        emisor=cfdi40.Emisor(
            rfc=RFC,
            nombre="Empresa de Pruebas",
            regimen_fiscal=RegimenFiscal.GENERAL_DE_LEY_PERSONAS_MORALES
        ),
        lugar_expedicion="64000",
        receptor=cfdi40.Receptor(
            rfc=data.rfc_cliente,
            nombre=data.nombre_cliente,
            uso_cfdi=UsoCFDI.GASTOS_EN_GENERAL,
            domicilio_fiscal_receptor="64000",
            regimen_fiscal_receptor=RegimenFiscal.GENERAL_DE_LEY_PERSONAS_MORALES
        ),
        metodo_pago=MetodoPago.PAGO_EN_PARCIALIDADES_O_DIFERIDO,
        serie="A",
        folio="1",
        conceptos=[
            cfdi40.Concepto(
                clave_prod_serv=p.ClaveProdServ,
                cantidad=Decimal(str(p.Cantidad)),
                clave_unidad=p.ClaveUnidad,
                descripcion=p.Descripcion,
                valor_unitario=Decimal(str(p.ValorUnitario)),
                impuestos=cfdi40.Impuestos(
                    traslados=cfdi40.Traslado(
                        impuesto=Impuesto.IVA,
                        tipo_factor=TipoFactor.TASA,
                        tasa_o_cuota=Decimal("0.160000"),
                    )
                ),
                _traslados_incluidos=False
            ) for p in data.productos
        ]
    )

    # Generar XML
    signer = Signer.load(
        certificate=open(CERT_PATH, "rb").read(),
        key=open(KEY_PATH, "rb").read(),
        password=KEY_PASS
    )
    comprobante.sign(signer)
    comprobante = comprobante.process()
    # Generar XML en archivo y en string
    xml_path = "factura.xml"
    comprobante.xml_write(xml_path)
    with open(xml_path, "r", encoding="utf-8") as f:
        xml_content = f.read()
    # Generar PDF en archivo y en base64
    pdf_path = "factura.pdf"
    from satcfdi.render import pdf_write
    pdf_write([comprobante], pdf_path)
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()
    import base64
    pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")
    return {
        "cfdi_xml": xml_content,
        "cfdi_pdf": pdf_base64
    }


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





class MovimientoDinero(BaseModel):
    fecha: str
    tipo: str  # 'Ingreso' o 'Egreso'
    concepto: str
    monto: float
    referencia: str = ""

@app.get("/movimientos-dinero")
def get_movimientos_dinero():
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM movimientos_dinero ORDER BY fecha DESC")
    movimientos = cursor.fetchall()
    cursor.close()
    db.close()
    return movimientos

@app.post("/movimientos-dinero")
def add_movimiento_dinero(mov: MovimientoDinero):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO movimientos_dinero (fecha, tipo, concepto, monto, referencia) VALUES (%s, %s, %s, %s, %s)",
        (mov.fecha, mov.tipo, mov.concepto, mov.monto, mov.referencia)
    )
    db.commit()
    cursor.close()
    db.close()
    return {"message": "Movimiento registrado"}

@app.delete("/movimientos-dinero/{movimiento_id}")
def delete_movimiento_dinero(movimiento_id: int):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor()
    cursor.execute("DELETE FROM movimientos_dinero WHERE id=%s", (movimiento_id,))
    db.commit()
    cursor.close()
    db.close()
    return {"message": "Movimiento de dinero eliminado"}


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
    vendedor: Optional[str] = None         # <-- AGREGAR
    descuento: Optional[float] = 0         # <-- AGREGAR

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
        "INSERT INTO cotizaciones (cliente_id, fecha, descripcion, monto, status, usuario_id, observaciones, articulos, autorizada, fecha_autorizacion, venta_id, vendedor, descuento) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
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
            cotizacion.vendedor,           # <-- AGREGAR
            cotizacion.descuento           # <-- AGREGAR
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
        "UPDATE cotizaciones SET cliente_id=%s, fecha=%s, descripcion=%s, monto=%s, status=%s, usuario_id=%s, observaciones=%s, articulos=%s, autorizada=%s, fecha_autorizacion=%s, venta_id=%s, vendedor=%s, descuento=%s WHERE id=%s",
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
            cotizacion.vendedor,           # <-- AGREGAR
            cotizacion.descuento,          # <-- AGREGAR
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
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hashed_password = pwd_context.hash(usuario.password)
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO usuarios (username, password, perfil) VALUES (%s, %s, %s)",
        (usuario.username, hashed_password, usuario.perfil)
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
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "SELECT id, username, password, perfil FROM usuarios WHERE username=%s",
        (login.username,)
    )
    user = cursor.fetchone()
    cursor.close()
    db.close()
    if user and pwd_context.verify(login.password, user["password"]):
        return {"success": True, "user": {"id": user["id"], "username": user["username"], "perfil": user["perfil"]}}
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
    # Indica si el cliente requiere factura (para IVA en PDF/consultas)
    requiereFactura: Optional[bool] = False
    total: float
    observaciones: Optional[str] = ""
    articulos: list[DetalleVenta]
    rfc: Optional[str] = None  # nuevo campo opcional

@app.post("/ventas")
def crear_venta(venta: Venta):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor()

    # Normaliza fecha a formato MySQL DATETIME
    try:
        if venta.fecha:
            fecha = str(venta.fecha).replace("T", " ")[:19]
        else:
            fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        # --- FOLIO GENERATION (SAFE, UNIQUE) ---
        cursor.execute("LOCK TABLES ventas WRITE")
        cursor.execute("SELECT folio FROM ventas WHERE folio LIKE 'SERVICIO-%' ORDER BY id DESC LIMIT 1")
        last_folio_row = cursor.fetchone()
        if last_folio_row and last_folio_row[0]:
            import re
            match = re.match(r"SERVICIO-(\d+)", last_folio_row[0])
            last_num = int(match.group(1)) if match else 0
        else:
            last_num = 0
        new_folio = f"SERVICIO-{str(last_num + 1).zfill(5)}"
        cursor.execute("UNLOCK TABLES")
        # --- END FOLIO GENERATION ---

        cursor.execute(
            """
            INSERT INTO ventas
            (cliente_id, fecha, folio, referencia, fecha_envio, terminos_pago, metodo_entrega, vendedor, almacen, descuento, notas_cliente, terminos_condiciones, total, observaciones, requiere_factura)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                venta.cliente_id, fecha, new_folio, venta.referencia, venta.fecha_envio, venta.terminos_pago,
                venta.metodo_entrega, venta.vendedor, venta.almacen, venta.descuento, venta.notas_cliente,
                venta.terminos_condiciones, venta.total, venta.observaciones, int(1 if getattr(venta, "requiereFactura", False) else 0)
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
                    raise HTTPException(status_code=400, detail=f"El IMEI {item.imei} ya fue vendido.")

            cursor.execute(
                "INSERT INTO detalle_venta (venta_id, articulo_id, cantidad, precio_unitario, subtotal, imei) VALUES (%s, %s, %s, %s, %s, %s)",
                (venta_id, item.articulo_id, item.cantidad, item.precio_unitario, item.cantidad * item.precio_unitario, getattr(item, "imei", None))
            )

        # Confirma la transacción
        db.commit()
    except HTTPException:
        db.rollback()
        cursor.close()
        db.close()
        raise
    except Exception as e:
        db.rollback()
        cursor.close()
        db.close()
        raise HTTPException(status_code=500, detail=f"Error al crear venta: {str(e)}")
    finally:
        try:
            cursor.execute("UNLOCK TABLES")
        except Exception:
            pass
        try:
            cursor.close()
        except Exception:
            pass
        try:
            db.close()
        except Exception:
            pass

    return {"message": "Venta registrada exitosamente", "venta_id": venta_id, "folio": new_folio}

@app.get("/ventas")
def listar_ventas(request: Request = None):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT v.*, c.nombre as cliente_nombre
        FROM ventas v
        LEFT JOIN clientes c ON v.cliente_id = c.id
        ORDER BY v.fecha DESC
        """
    )
    ventas = cursor.fetchall()
    for v in ventas:
        try:
            v["requiereFactura"] = bool(v.get("requiere_factura", 0))
        except Exception:
            pass
        if 'rfc' not in v:
            v['rfc'] = None
        if v.get('constancia_path'):
            try:
                v['constancia_url'] = build_public_url(v['constancia_path'], request)
            except Exception:
                v['constancia_url'] = None
        else:
            v['constancia_url'] = None
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

@app.delete("/ventas/{venta_id}")
def eliminar_venta(venta_id: int):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor()
    try:
        # 1. Eliminar reportes_servicio relacionados
        cursor.execute("SELECT id FROM venta_tecnico WHERE venta_id = %s", (venta_id,))
        asignaciones = cursor.fetchall()
        asignacion_ids = [row[0] for row in asignaciones]
        if asignacion_ids:
            format_strings = ','.join(['%s'] * len(asignacion_ids))
            cursor.execute(f"DELETE FROM reportes_servicio WHERE asignacion_id IN ({format_strings})", tuple(asignacion_ids))
        # 2. Eliminar detalle_venta
        cursor.execute("DELETE FROM detalle_venta WHERE venta_id = %s", (venta_id,))
        # 3. Eliminar venta_tecnico
        cursor.execute("DELETE FROM venta_tecnico WHERE venta_id = %s", (venta_id,))
        # 4. Eliminar venta principal
        cursor.execute("DELETE FROM ventas WHERE id = %s", (venta_id,))
        db.commit()
    except Exception as e:
        db.rollback()
        cursor.close()
        db.close()
        raise HTTPException(status_code=500, detail=f"Error al eliminar venta: {str(e)}")
    cursor.close()
    db.close()
    return {"message": f"Venta {venta_id} eliminada correctamente"}

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
    """
    Acepta payload extendido:
    {
      tecnico_id, fecha_servicio, hora_servicio?, direccion?, cp?, link_ubicacion?, cliente_info?{telefonos,usuario,plataforma,descripcion}
    }
    Guarda lo que haya disponible. Si la tabla no tiene aún las columnas nuevas, intenta insert básico.
    """
    tecnico_id = data.get("tecnico_id")
    fecha_servicio = data.get("fecha_servicio")
    hora_servicio = data.get("hora_servicio")
    direccion = data.get("direccion")
    cp = data.get("cp")
    link_ubicacion = data.get("link_ubicacion")
    cliente_info = data.get("cliente_info") or {}
    # Serializar cliente_info si existe
    cliente_info_json = json.dumps(cliente_info) if cliente_info else None

    if not tecnico_id or not fecha_servicio:
        raise HTTPException(status_code=400, detail="tecnico_id y fecha_servicio son obligatorios")

    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor()
    # UPSERT (clave única en venta_id)
    cursor.execute(
        """
        INSERT INTO venta_tecnico
            (venta_id, tecnico_id, fecha_servicio, hora_servicio, direccion, cp, link_ubicacion, cliente_info)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        ON DUPLICATE KEY UPDATE
            tecnico_id=VALUES(tecnico_id),
            fecha_servicio=VALUES(fecha_servicio),
            hora_servicio=VALUES(hora_servicio),
            direccion=VALUES(direccion),
            cp=VALUES(cp),
            link_ubicacion=VALUES(link_ubicacion),
            cliente_info=VALUES(cliente_info),
            fecha_asignacion=NOW()
        """,
        (venta_id, tecnico_id, fecha_servicio, hora_servicio, direccion, cp, link_ubicacion, cliente_info_json)
    )
    db.commit()
    cursor.close()
    db.close()
    return {"message": "Técnico asignado/actualizado", "upsert": True, "extended": bool(hora_servicio or direccion or cp or link_ubicacion or cliente_info)}

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
        SELECT vt.id,
               vt.fecha_servicio,
               vt.hora_servicio,
               vt.direccion,
               vt.cp,
               vt.link_ubicacion,
               vt.cliente_info,
               vt.venta_id,
               v.cliente_id,
               u.username as tecnico,
               v.fecha as fecha_venta
        FROM venta_tecnico vt
        JOIN usuarios u ON vt.tecnico_id = u.id
        JOIN ventas v ON vt.venta_id = v.id
    """)
    asignaciones = cursor.fetchall()
    cursor.close()
    db.close()
    return asignaciones

class ReporteServicio(BaseModel):
    # ...existing code...
    modelo_gps: str = ""
    ubicacion_gps: str = ""
    ubicacion_bloqueo: str = ""
    # ...existing code...
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
    total: float = 0
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
    "INSERT INTO reportes_servicio (asignacion_id, tipo_servicio, lugar_instalacion, marca, submarca, modelo, placas, color, numero_economico, equipo_plan, imei, serie, accesorios, sim_proveedor, sim_serie, sim_instalador, sim_telefono, bateria, ignicion, corte, ubicacion_corte, modelo_gps, ubicacion_gps, ubicacion_bloqueo, observaciones, plataforma, usuario, subtotal, forma_pago, pagado, nombre_cliente, firma_cliente, nombre_instalador, firma_instalador, total, monto_tecnico, viaticos) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
    (
        reporte.asignacion_id, reporte.tipo_servicio, reporte.lugar_instalacion, reporte.marca, reporte.submarca,
        reporte.modelo, reporte.placas, reporte.color, reporte.numero_economico, reporte.equipo_plan,
        reporte.imei, reporte.serie, reporte.accesorios, reporte.sim_proveedor, reporte.sim_serie,
        reporte.sim_instalador, reporte.sim_telefono, reporte.bateria, reporte.ignicion, reporte.corte,
        reporte.ubicacion_corte, reporte.modelo_gps, reporte.ubicacion_gps, reporte.ubicacion_bloqueo,
        reporte.observaciones, reporte.plataforma, reporte.usuario, reporte.subtotal,
        reporte.forma_pago, int(reporte.pagado), reporte.nombre_cliente, reporte.firma_cliente,
        reporte.nombre_instalador, reporte.firma_instalador, reporte.total,
        reporte.monto_tecnico, reporte.viaticos
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
    # Lista de columnas válidas según DESCRIBE reportes_servicio
    valid_columns = [
        "asignacion_id", "tipo_servicio", "lugar_instalacion", "marca", "submarca", "modelo", "placas", "color", "numero_economico", "equipo_plan", "imei", "serie", "accesorios", "sim_proveedor", "sim_serie", "sim_instalador", "sim_telefono", "bateria", "ignicion", "corte", "ubicacion_corte", "observaciones", "plataforma", "usuario", "subtotal", "forma_pago", "pagado", "nombre_cliente", "firma_cliente", "nombre_instalador", "firma_instalador", "fecha", "monto_tecnico", "viaticos",
        # nuevas columnas para comprobantes
        "comprobante_path", "comprobante_estado", "aprobado_por", "aprobado_fecha"
    ]
    campos = []
    valores = []
    for k, v in reporte.items():
        if k in valid_columns:
            campos.append(f"{k}=%s")
            valores.append(v)
    if not campos:
        cursor.close()
        db.close()
        raise HTTPException(status_code=400, detail="No hay campos válidos para actualizar.")
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
    # Obtener los datos del usuario para devolverlos junto con el token
    user_data = {
        "id": user["id"],
        "username": user["username"],
        "perfil": user["perfil"]
    }
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_data
    }

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

@app.get("/usuarios/me")
def get_usuario_actual(request: Request, token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        if username is None or user_id is None:
            raise HTTPException(status_code=401, detail="Token inválido")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, username, perfil FROM usuarios WHERE id=%s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    db.close()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user

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

@app.put("/usuarios/{usuario_id}")
def update_usuario(usuario_id: int, usuario: dict):
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor()
    campos = []
    valores = []
    if "username" in usuario:
        campos.append("username=%s")
        valores.append(usuario["username"])
    if "perfil" in usuario:
        campos.append("perfil=%s")
        valores.append(usuario["perfil"])
    if "password" in usuario and usuario["password"]:
        hashed_password = pwd_context.hash(usuario["password"])
        campos.append("password=%s")
        valores.append(hashed_password)
    if not campos:
        cursor.close()
        db.close()
        return {"message": "Nada que actualizar"}
    valores.append(usuario_id)
    sql = f"UPDATE usuarios SET {', '.join(campos)} WHERE id=%s"
    cursor.execute(sql, valores)
    db.commit()
    cursor.close()
    db.close()
    return {"message": "Usuario actualizado"}

@app.delete("/usuarios/{usuario_id}")
def delete_usuario(usuario_id: int):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor()
    cursor.execute("DELETE FROM usuarios WHERE id=%s", (usuario_id,))
    db.commit()
    cursor.close()
    db.close()
    return {"message": "Usuario eliminado"}

@app.get("/ventas/{venta_id}/asignacion")
def get_asignacion_venta(venta_id: int):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT venta_id, tecnico_id, fecha_servicio, hora_servicio, direccion, cp, link_ubicacion, cliente_info, fecha_asignacion
        FROM venta_tecnico
        WHERE venta_id = %s
        ORDER BY fecha_asignacion DESC LIMIT 1
    """, (venta_id,))
    asignacion = cursor.fetchone()
    cursor.close()
    db.close()
    # Deserializar cliente_info si existe
    if asignacion and asignacion.get('cliente_info'):
        try:
            asignacion['cliente_info'] = json.loads(asignacion['cliente_info'])
        except Exception:
            asignacion['cliente_info'] = None
    return asignacion or {}

@app.post("/reportes-servicio/{reporte_id}/comprobante")
def subir_comprobante_reporte(reporte_id: int, archivo: UploadFile = File(...), request: Request = None):
    """Sube un comprobante de pago para un reporte de servicio.
    Guarda bajo uploads/servicios/<folio>/ y marca comprobante_estado='pendiente'.
    """
    # Validar reporte y obtener asignacion_id
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, asignacion_id FROM reportes_servicio WHERE id=%s", (reporte_id,))
    rep = cursor.fetchone()
    if not rep:
        cursor.close()
        db.close()
        raise HTTPException(status_code=404, detail="Reporte no encontrado")

    # Obtener folio de la venta asociada a la asignación
    folio = None
    try:
        cursor.execute("SELECT venta_id FROM venta_tecnico WHERE id=%s", (rep["asignacion_id"],))
        row = cursor.fetchone()
        if row and row.get("venta_id"):
            cursor.execute("SELECT folio FROM ventas WHERE id=%s", (row["venta_id"],))
            v = cursor.fetchone()
            folio = v.get("folio") if v else None
    except Exception:
        folio = None
    if not folio:
        # fallback
        folio = f"ReporteServicio-{reporte_id}"

    # Crear carpeta y guardar archivo
    import pathlib, shutil
    safe_folio = ''.join(c for c in folio if c.isalnum() or c in ('-', '_'))
    base_dir = os.path.join("uploads", "servicios", safe_folio)
    os.makedirs(base_dir, exist_ok=True)
    filename = archivo.filename or "comprobante"
    # sanitizar nombre
    filename = ''.join(c for c in filename if c.isalnum() or c in ('-', '_', '.', ' ')).strip()
    dest_path = os.path.join(base_dir, filename)
    with open(dest_path, "wb") as out:
        shutil.copyfileobj(archivo.file, out)

    # Guardar en DB ruta y estado pendiente
    rel_path = os.path.relpath(dest_path, start=".")  # relativo al proyecto
    cursor2 = db.cursor()
    try:
        cursor2.execute(
            "UPDATE reportes_servicio SET comprobante_path=%s, comprobante_estado=%s WHERE id=%s",
            (rel_path, "pendiente", reporte_id)
        )
        db.commit()
    finally:
        cursor2.close()
        cursor.close()
        db.close()

    file_url = build_public_url(rel_path, request)
    return {"message": "Comprobante subido", "comprobante_path": rel_path, "comprobante_url": file_url, "estado": "pendiente"}

@app.put("/reportes-servicio/{reporte_id}/aprobar-comprobante")
def aprobar_comprobante_reporte(reporte_id: int, current=Depends(get_current_user)):
    """Aprueba el comprobante de un reporte. Requiere rol Admin. Marca pagado=1."""
    # Obtener perfil del usuario
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, username, perfil FROM usuarios WHERE id=%s", (current["user_id"],))
    user = cursor.fetchone()
    if not user or user.get("perfil") != "Admin":
        cursor.close()
        db.close()
        raise HTTPException(status_code=403, detail="No autorizado")

    # Verificar que exista un comprobante cargado
    cursor.execute("SELECT comprobante_path, comprobante_estado FROM reportes_servicio WHERE id=%s", (reporte_id,))
    rep = cursor.fetchone()
    if not rep:
        cursor.close()
        db.close()
        raise HTTPException(status_code=404, detail="Reporte no encontrado")
    if not rep.get("comprobante_path"):
        cursor.close()
        db.close()
        raise HTTPException(status_code=400, detail="No hay comprobante para aprobar")

    # Aprobar
    cursor2 = db.cursor()
    try:
        cursor2.execute(
            "UPDATE reportes_servicio SET comprobante_estado=%s, aprobado_por=%s, aprobado_fecha=NOW(), pagado=1 WHERE id=%s",
            ("aprobado", user.get("username"), reporte_id)
        )
        db.commit()
    finally:
        cursor2.close()
        cursor.close()
        db.close()
    return {"message": "Comprobante aprobado y reporte marcado como pagado"}

@app.put("/reportes-servicio/{reporte_id}/rechazar-comprobante")
def rechazar_comprobante_reporte(reporte_id: int, current=Depends(get_current_user)):
    """Rechaza el comprobante de un reporte. Requiere rol Admin."""
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, username, perfil FROM usuarios WHERE id=%s", (current["user_id"],))
    user = cursor.fetchone()
    if not user or user.get("perfil") != "Admin":
        cursor.close()
        db.close()
        raise HTTPException(status_code=403, detail="No autorizado")

    cursor2 = db.cursor()
    try:
        cursor2.execute(
            "UPDATE reportes_servicio SET comprobante_estado=%s WHERE id=%s",
            ("rechazado", reporte_id)
        )
        db.commit()
    finally:
        cursor2.close()
        cursor.close()
        db.close()
    return {"message": "Comprobante rechazado"}

@app.post("/ventas/{venta_id}/constancia")
async def subir_constancia_fiscal(venta_id: int, archivo: UploadFile = File(...), rfc: str = Form(None), request: Request = None):
    ALLOWED_EXT = {'.pdf', '.png', '.jpg', '.jpeg'}
    MAX_SIZE_MB = 8
    import shutil

    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, folio FROM ventas WHERE id=%s", (venta_id,))
    venta_row = cursor.fetchone()
    if not venta_row:
        cursor.close(); db.close()
        raise HTTPException(status_code=404, detail="Venta no encontrada")

    folio = venta_row.get("folio") or f"VENTA-{venta_id}"
    safe_folio = ''.join(c for c in folio if c.isalnum() or c in ('-', '_'))

    filename = archivo.filename or 'constancia'
    filename = ''.join(c for c in filename if c.isalnum() or c in ('-', '_', '.', ' ')).strip()
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXT:
        cursor.close(); db.close()
        raise HTTPException(status_code=400, detail=f"Extensión no permitida {ext}")

    data = await archivo.read()
    size_mb = len(data)/(1024*1024)
    if size_mb > MAX_SIZE_MB:
        cursor.close(); db.close()
        raise HTTPException(status_code=400, detail=f"Archivo supera {MAX_SIZE_MB}MB")

    base_dir = os.path.join('uploads', 'constancias', safe_folio)
    os.makedirs(base_dir, exist_ok=True)

    base_name, ext2 = os.path.splitext(filename)
    final_name = filename
    idx = 1
    while os.path.exists(os.path.join(base_dir, final_name)):
        final_name = f"{base_name}_{idx}{ext2}"; idx += 1

    dest_path = os.path.join(base_dir, final_name)
    with open(dest_path, 'wb') as f:
        f.write(data)

    rel_path = os.path.relpath(dest_path, start='.')

    cursor2 = db.cursor()
    try:
        try:
            cursor2.execute("ALTER TABLE ventas ADD COLUMN IF NOT EXISTS constancia_path VARCHAR(255) NULL")
        except Exception:
            pass
        try:
            cursor2.execute("ALTER TABLE ventas ADD COLUMN IF NOT EXISTS rfc VARCHAR(20) NULL")
        except Exception:
            pass
        cursor2.execute("UPDATE ventas SET constancia_path=%s, rfc=COALESCE(%s, rfc) WHERE id=%s", (rel_path, rfc, venta_id))
        db.commit()
    finally:
        cursor2.close(); cursor.close(); db.close()

    file_url = build_public_url(rel_path, request)
    return {"message": "Constancia subida", "constancia_path": rel_path, "constancia_url": file_url, "rfc": rfc}

@app.get("/clientes/{cliente_id}/constancia-venta-reciente")
def get_constancia_venta_reciente(cliente_id: int, request: Request = None):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("ALTER TABLE ventas ADD COLUMN IF NOT EXISTS constancia_path VARCHAR(255) NULL")
    except Exception:
        pass
    cursor.execute(
        """
        SELECT id, folio, cliente_id, constancia_path, rfc, fecha
        FROM ventas
        WHERE cliente_id=%s AND constancia_path IS NOT NULL
        ORDER BY fecha DESC, id DESC
        LIMIT 1
        """,
        (cliente_id,)
    )
    row = cursor.fetchone()
    cursor.close(); db.close()
    if not row:
        return {"hasConstancia": False}
    rel = row.get('constancia_path')
    file_url = build_public_url(rel, request) if rel else None
    return {
        "hasConstancia": True,
        "venta_id": row.get('id'),
        "folio": row.get('folio'),
        "rfc": row.get('rfc'),
        "fecha": row.get('fecha'),
        "constancia_url": file_url
    }

@app.delete("/ventas/{venta_id}/constancia")
async def eliminar_constancia_fiscal(venta_id: int, request: Request = None):
    import os
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor(dictionary=True)
    try:
        # Asegurar columnas existen
        try:
            cursor.execute("ALTER TABLE ventas ADD COLUMN IF NOT EXISTS constancia_path VARCHAR(255) NULL")
        except Exception:
            pass
        try:
            cursor.execute("ALTER TABLE ventas ADD COLUMN IF NOT EXISTS rfc VARCHAR(20) NULL")
        except Exception:
            pass
        cursor.execute("SELECT constancia_path FROM ventas WHERE id=%s", (venta_id,))
        row = cursor.fetchone()
        if not row:
            cursor.close(); db.close()
            raise HTTPException(status_code=404, detail="Venta no encontrada")
        path = row.get('constancia_path')
        # Borrar archivo físico si existe
        if path and os.path.isfile(path):
            try:
                os.remove(path)
            except Exception:
                pass
        # Limpiar campos
        cursor.execute("UPDATE ventas SET constancia_path=NULL WHERE id=%s", (venta_id,))
        db.commit()
    finally:
        cursor.close(); db.close()
    return {"message": "Constancia eliminada", "venta_id": venta_id}

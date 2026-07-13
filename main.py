from dotenv import load_dotenv
# satcfdi para facturación oficial SAT
from decimal import Decimal
from satcfdi.models import Signer
from satcfdi.create.cfd import cfdi40
from satcfdi.create.cfd.cfdi40 import Comprobante, Emisor, Receptor, Concepto, Traslado
from satcfdi.create.cfd.catalogos import RegimenFiscal, UsoCFDI, MetodoPago, Impuesto, TipoFactor

import base64
import os
import io
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

@app.on_event("startup")
def crear_tabla_retiros_banco():
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS retiros_banco (
            id INT AUTO_INCREMENT PRIMARY KEY,
            banco VARCHAR(100) NOT NULL,
            monto DECIMAL(12,2) NOT NULL,
            motivo VARCHAR(255) NULL,
            comprobante_path VARCHAR(500) NULL,
            estatus VARCHAR(20) NOT NULL DEFAULT 'pendiente',
            creado_por VARCHAR(100) NULL,
            creado_fecha DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            aprobado_por VARCHAR(100) NULL,
            aprobado_fecha DATETIME NULL
        )
    """)
    db.commit()
    cursor.close()
    db.close()



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
    serie: Optional[str] = "A"
    folio: Optional[str] = None
    domicilio_fiscal_receptor: Optional[str] = None
    regimen_fiscal_receptor: Optional[str] = None

# RFC genérico que el SAT reserva para ventas a público en general
RFC_PUBLICO_GENERAL = "XAXX010101000"


def _sw_base_url(pac_env: str) -> str:
    return "https://services.test.sw.com.mx" if pac_env.upper() == "TEST" else "https://services.sw.com.mx"


def _construir_y_timbrar_cfdi(nombre_cliente, rfc_cliente, uso_cfdi, metodo_pago, forma_pago,
                               productos, serie="A", folio=None,
                               domicilio_fiscal_receptor=None, regimen_fiscal_receptor=None):
    """Arma el CFDI 4.0 en JSON y lo timbra con el servicio 'Emision Timbrado JSON' de SW Sapien.
    SW sella el comprobante server-side usando el CSD que el usuario haya cargado en su cuenta SW
    (portal ADT), por lo que Sello/Certificado/NoCertificado van vacios. Devuelve uuid + rutas de
    xml/pdf guardados."""
    import requests
    from satcfdi.cfdi import CFDI
    from satcfdi.render import pdf_write

    RFC = os.getenv("CSD_RFC", "RAQÑ7701212M3")
    RAZON_SOCIAL = os.getenv("CSD_RAZON_SOCIAL", "Empresa de Pruebas")
    REGIMEN_FISCAL_EMISOR = os.getenv("CSD_REGIMEN_FISCAL", "601")
    LUGAR_EXPEDICION = os.getenv("CSD_LUGAR_EXPEDICION", "64000")

    PAC_USER = os.getenv("PAC_USER")
    PAC_PASS = os.getenv("PAC_PASS")
    PAC_ENV = os.getenv("PAC_ENV", "TEST")
    sw_base = _sw_base_url(PAC_ENV)

    if not (PAC_USER and PAC_PASS):
        raise HTTPException(status_code=500, detail="PAC no configurado (PAC_USER/PAC_PASS)")

    # El SAT exige datos fijos cuando se factura al RFC genérico de público en general
    if rfc_cliente == RFC_PUBLICO_GENERAL:
        uso_cfdi = "S01"
        domicilio_receptor = "00000"
        regimen_receptor = "616"
    else:
        domicilio_receptor = domicilio_fiscal_receptor or LUGAR_EXPEDICION
        regimen_receptor = regimen_fiscal_receptor or REGIMEN_FISCAL_EMISOR

    conceptos_json = []
    subtotal = Decimal("0")
    total_iva = Decimal("0")
    for p in productos:
        cantidad = Decimal(str(p.Cantidad))
        valor_unitario = Decimal(str(p.ValorUnitario))
        importe = (cantidad * valor_unitario).quantize(Decimal("0.01"))
        iva = (importe * Decimal("0.16")).quantize(Decimal("0.01"))
        subtotal += importe
        total_iva += iva
        conceptos_json.append({
            "ClaveProdServ": p.ClaveProdServ,
            "Cantidad": str(cantidad),
            "ClaveUnidad": p.ClaveUnidad,
            "Unidad": p.Unidad,
            "Descripcion": p.Descripcion,
            "ValorUnitario": str(valor_unitario),
            "Importe": str(importe),
            "Descuento": "0.00",
            "ObjetoImp": "02",
            "Impuestos": {
                "Traslados": [{
                    "Base": str(importe),
                    "Importe": str(iva),
                    "Impuesto": "002",
                    "TasaOCuota": "0.160000",
                    "TipoFactor": "Tasa"
                }]
            }
        })

    total = subtotal + total_iva

    comprobante_json = {
        "Version": "4.0",
        "FormaPago": forma_pago,
        "Serie": serie or "A",
        "Folio": folio or str(int(datetime.utcnow().timestamp())),
        "Fecha": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "Sello": "",
        "NoCertificado": "",
        "Certificado": "",
        "SubTotal": str(subtotal),
        "Descuento": "0.00",
        "Moneda": "MXN",
        "TipoCambio": "1",
        "Total": str(total),
        "TipoDeComprobante": "I",
        "Exportacion": "01",
        "MetodoPago": metodo_pago,
        "LugarExpedicion": LUGAR_EXPEDICION,
        "Emisor": {
            "Rfc": RFC,
            "Nombre": RAZON_SOCIAL,
            "RegimenFiscal": REGIMEN_FISCAL_EMISOR
        },
        "Receptor": {
            "Rfc": rfc_cliente,
            "Nombre": nombre_cliente,
            "DomicilioFiscalReceptor": domicilio_receptor,
            "RegimenFiscalReceptor": regimen_receptor,
            "UsoCFDI": uso_cfdi
        },
        "Conceptos": conceptos_json,
        "Impuestos": {
            "TotalImpuestosTrasladados": str(total_iva),
            "Traslados": [{
                "Base": str(subtotal),
                "Importe": str(total_iva),
                "Impuesto": "002",
                "TasaOCuota": "0.160000",
                "TipoFactor": "Tasa"
            }]
        }
    }

    try:
        auth_resp = requests.post(
            f"{sw_base}/v2/security/authenticate",
            json={"user": PAC_USER, "password": PAC_PASS},
            headers={"Content-Type": "application/json"},
            timeout=20,
        )
        auth_data = auth_resp.json()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error conectando con SW (auth): {e}")
    if auth_data.get("status") != "success":
        raise HTTPException(status_code=502, detail=f"Error al autenticar con SW: {auth_data.get('message') or auth_data}")
    token = auth_data["data"]["token"]

    try:
        stamp_resp = requests.post(
            f"{sw_base}/v3/cfdi33/issue/json/v4",
            data=json.dumps(comprobante_json),
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/jsontoxml",
            },
            timeout=30,
        )
        stamp_data = stamp_resp.json()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error conectando con SW (timbrado): {e}")
    if stamp_data.get("status") != "success":
        raise HTTPException(status_code=502, detail=f"Error al timbrar con SW: {stamp_data.get('message') or stamp_data.get('messageDetail') or stamp_data}")

    data = stamp_data["data"]
    uuid_ = data["uuid"]
    xml_bytes = data["cfdi"].encode("utf-8")
    stamped_cfdi = CFDI.from_string(xml_bytes)

    folder = os.path.join("uploads", "facturas")
    os.makedirs(folder, exist_ok=True)
    xml_path = os.path.join(folder, f"{uuid_}.xml")
    with open(xml_path, "wb") as f:
        f.write(xml_bytes)

    pdf_path = os.path.join(folder, f"{uuid_}.pdf")
    pdf_write([stamped_cfdi], pdf_path)
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    return {
        "uuid": uuid_,
        "xml_bytes": xml_bytes,
        "pdf_bytes": pdf_bytes,
        "xml_path": xml_path,
        "pdf_path": pdf_path,
    }


@app.post("/api/facturar")
def facturar(data: FacturaRequest):
    resultado = _construir_y_timbrar_cfdi(
        nombre_cliente=data.nombre_cliente,
        rfc_cliente=data.rfc_cliente,
        uso_cfdi=data.uso_cfdi,
        metodo_pago=data.metodo_pago,
        forma_pago=data.forma_pago,
        productos=data.productos,
        serie=data.serie,
        folio=data.folio,
        domicilio_fiscal_receptor=data.domicilio_fiscal_receptor,
        regimen_fiscal_receptor=data.regimen_fiscal_receptor,
    )
    return {
        "uuid": resultado["uuid"],
        "cfdi_xml": resultado["xml_bytes"].decode("utf-8"),
        "cfdi_pdf": base64.b64encode(resultado["pdf_bytes"]).decode("utf-8"),
        "xml_url": build_public_url(resultado["xml_path"]),
        "pdf_url": build_public_url(resultado["pdf_path"])
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
    cursor.execute("""
        SELECT 
            ROW_NUMBER() OVER (ORDER BY id) AS consecutivo,
            id,
            username, 
            perfil,
            ultima_sesion
        FROM usuarios
    """)
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

@app.post("/usuarios/registrar-sesion")
def registrar_sesion(data: dict = Body(...)):
    user_id = data.get("user_id")
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id requerido")
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor()
    cursor.execute("UPDATE usuarios SET ultima_sesion = NOW() WHERE id = %s", (user_id,))
    db.commit()
    cursor.close()
    db.close()
    return {"success": True}

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
    
    if user and pwd_context.verify(login.password, user["password"]):
        # Actualizar ultima_sesion
        cursor.execute(
            "UPDATE usuarios SET ultima_sesion = NOW() WHERE id = %s",
            (user["id"],)
        )
        db.commit()
        cursor.close()
        db.close()
        return {"success": True, "user": {"id": user["id"], "username": user["username"], "perfil": user["perfil"]}}
    else:
        cursor.close()
        db.close()
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
    atendidoPor: Optional[str] = ""
    usuarioSesion: Optional[str] = ""
    rfc: Optional[str] = None
    constancia_path: Optional[str] = None

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
        # Build public URL for constancia
        if cliente.get("constancia_path"):
            cliente["constancia_path"] = build_public_url(cliente["constancia_path"])
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
    try:
        cursor.execute("ALTER TABLE clientes ADD COLUMN IF NOT EXISTS atendidoPor VARCHAR(255) NULL")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE clientes ADD COLUMN IF NOT EXISTS usuarioSesion VARCHAR(255) NULL")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE clientes ADD COLUMN IF NOT EXISTS rfc VARCHAR(20) NULL")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE clientes ADD COLUMN IF NOT EXISTS constancia_path VARCHAR(255) NULL")
    except Exception:
        pass
    cursor.execute(
        "INSERT INTO clientes (nombre, correo, direccion, atendidoPor, usuarioSesion, rfc, constancia_path) VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (cliente.nombre, cliente.correo, cliente.direccion, cliente.atendidoPor, cliente.usuarioSesion, cliente.rfc, cliente.constancia_path)
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
    try:
        cursor.execute("ALTER TABLE clientes ADD COLUMN IF NOT EXISTS atendidoPor VARCHAR(255) NULL")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE clientes ADD COLUMN IF NOT EXISTS usuarioSesion VARCHAR(255) NULL")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE clientes ADD COLUMN IF NOT EXISTS rfc VARCHAR(20) NULL")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE clientes ADD COLUMN IF NOT EXISTS constancia_path VARCHAR(255) NULL")
    except Exception:
        pass
    cursor.execute(
        "UPDATE clientes SET nombre=%s, correo=%s, direccion=%s, atendidoPor=%s, usuarioSesion=%s, rfc=%s, constancia_path=%s WHERE id=%s",
        (cliente.nombre, cliente.correo, cliente.direccion, cliente.atendidoPor, cliente.usuarioSesion, cliente.rfc, cliente.constancia_path, cliente_id)
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
    hora_servicio = data.get("hora_servicio")  # sigue siendo hora de inicio
    hora_fin = data.get("hora_fin")  # ahora se guarda como string, igual que hora_servicio
    direccion = data.get("direccion")
    cp = data.get("cp")
    link_ubicacion = data.get("link_ubicacion")
    cliente_info = data.get("cliente_info") or {}
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
    cursor.execute(
        """
        INSERT INTO venta_tecnico
            (venta_id, tecnico_id, fecha_servicio, hora_servicio, hora_fin, direccion, cp, link_ubicacion, cliente_info)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON DUPLICATE KEY UPDATE
            tecnico_id=VALUES(tecnico_id),
            fecha_servicio=VALUES(fecha_servicio),
            hora_servicio=VALUES(hora_servicio),
            hora_fin=VALUES(hora_fin),
            direccion=VALUES(direccion),
            cp=VALUES(cp),
            link_ubicacion=VALUES(link_ubicacion),
            cliente_info=VALUES(cliente_info),
            fecha_asignacion=NOW()
        """,
        (venta_id, tecnico_id, fecha_servicio, hora_servicio, hora_fin, direccion, cp, link_ubicacion, cliente_info_json)
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
               vt.hora_fin,
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
    hora_fin: Optional[str] = None  # nuevo campo para hora final
    modelo_gps: str = ""
    ubicacion_gps: str = ""
    ubicacion_bloqueo: str = ""
    # ...existing code...
    asignacion_id: Optional[int] = None
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
    vendedor: str = ""
    total: float = 0
    monto_tecnico: float = 0
    viaticos: float = 0
    # NUEVO: soporte multi-instalación
    imeis_articulos: Optional[List[dict]] = None
    sim_series: Optional[List[str]] = None
    # NUEVO: indica si el reporte NO debe modificar el stock de IMEIs/SIMs (separados)
    no_modifica_stock: bool = False  # mantener por compatibilidad
    no_modifica_imei: bool = False
    no_modifica_sim: bool = False
    # NUEVO: campos para Cambio de Equipo y Cambio de Chip
    imei_devolver: str = ""  # IMEI que se devuelve en Cambio de Equipo
    sim_devolver: str = ""   # SIM que se devuelve en Cambio de Chip

@app.post("/reportes-servicio")
def add_reporte_servicio(reporte: ReporteServicio):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor(dictionary=True)
    
    # Permitir reportes con o sin asignacion_id
    folio_venta = None
    if getattr(reporte, "asignacion_id", None):
        # ...existing code para asignación...
        try:
            cursor.execute("SELECT id FROM reportes_servicio WHERE asignacion_id = %s", (reporte.asignacion_id,))
            existing_report = cursor.fetchone()
            if existing_report:
                cursor.close()
                db.close()
                raise HTTPException(status_code=400, detail=f"Ya existe un reporte de servicio para la asignación {reporte.asignacion_id}")
        except mysql.connector.Error as e:
            cursor.close()
            db.close()
            raise HTTPException(status_code=500, detail=f"Error al validar reporte existente: {str(e)}")
        try:
            cursor.execute("SELECT venta_id FROM venta_tecnico WHERE id=%s", (reporte.asignacion_id,))
            row = cursor.fetchone()
            if row and row.get("venta_id"):
                cursor.execute("SELECT folio FROM ventas WHERE id=%s", (row["venta_id"],))
                v = cursor.fetchone()
                folio_venta = v.get("folio") if v else None
        except Exception:
            folio_venta = None
    else:
        # Generar folio consecutivo para reportes sin asignación
        cursor.execute("SELECT folio FROM reportes_servicio WHERE folio LIKE 'SERVICIO-%' ORDER BY id DESC LIMIT 1")
        last_folio_row = cursor.fetchone()
        if last_folio_row and last_folio_row.get("folio"):
            import re
            match = re.match(r"SERVICIO-(\d+)", last_folio_row["folio"])
            last_num = int(match.group(1)) if match else 0
        else:
            last_num = 0
        folio_venta = f"SERVICIO-{str(last_num + 1).zfill(5)}"
    
    # Serializar campos JSON si vienen en el payload
    imeis_json = json.dumps(reporte.imeis_articulos) if getattr(reporte, "imeis_articulos", None) is not None else None
    sim_json = json.dumps(reporte.sim_series) if getattr(reporte, "sim_series", None) is not None else None
    
    # Buscar nombre del cliente y técnico si no vienen en el payload
    nombre_cliente = reporte.nombre_cliente
    if not nombre_cliente and getattr(reporte, "cliente_id", None):
        cursor.execute("SELECT nombre FROM clientes WHERE id=%s", (reporte.cliente_id,))
        row = cursor.fetchone()
        nombre_cliente = row["nombre"] if row else ""
    nombre_instalador = reporte.nombre_instalador
    try:
        cursor.execute(
        """
        INSERT INTO reportes_servicio (
            asignacion_id, folio, tipo_servicio, lugar_instalacion, marca, submarca, modelo, placas, color, numero_economico,
            equipo_plan, imei, serie, accesorios, sim_proveedor, sim_serie, sim_instalador, sim_telefono, bateria,
            ignicion, corte, ubicacion_corte, modelo_gps, ubicacion_gps, ubicacion_bloqueo, observaciones, plataforma,
            usuario, subtotal, forma_pago, pagado, nombre_cliente, firma_cliente, nombre_instalador, firma_instalador,
            vendedor, total, monto_tecnico, viaticos, imeis_articulos, sim_series, hora_fin, imei_devolver, sim_devolver
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        """,
        (
            getattr(reporte, "asignacion_id", None), folio_venta, reporte.tipo_servicio, reporte.lugar_instalacion, reporte.marca, reporte.submarca,
            reporte.modelo, reporte.placas, reporte.color, reporte.numero_economico, reporte.equipo_plan,
            reporte.imei, reporte.serie, reporte.accesorios, reporte.sim_proveedor, reporte.sim_serie,
            reporte.sim_instalador, reporte.sim_telefono, reporte.bateria, reporte.ignicion, reporte.corte,
            reporte.ubicacion_corte, reporte.modelo_gps, reporte.ubicacion_gps, reporte.ubicacion_bloqueo,
            reporte.observaciones, reporte.plataforma, reporte.usuario, reporte.subtotal,
            reporte.forma_pago, int(reporte.pagado), nombre_cliente, reporte.firma_cliente,
            nombre_instalador, reporte.firma_instalador, reporte.vendedor, reporte.total,
            reporte.monto_tecnico, reporte.viaticos, imeis_json, sim_json, reporte.hora_fin,
            reporte.imei_devolver or None, reporte.sim_devolver or None
        )
    )
    except mysql.connector.IntegrityError as e:
        cursor.close()
        db.close()
        if "idx_unique_asignacion" in str(e) or "Duplicate entry" in str(e):
            raise HTTPException(status_code=400, detail=f"Ya existe un reporte de servicio para la asignación {reporte.asignacion_id}")
        else:
            raise HTTPException(status_code=500, detail=f"Error de integridad en la base de datos: {str(e)}")
    except mysql.connector.Error as e:
        cursor.close()
        db.close()
        raise HTTPException(status_code=500, detail=f"Error al guardar reporte de servicio: {str(e)}")
    # NUEVO: marcar IMEIs y SIMs involucrados como "Vendido"
    nuevo_id = cursor.lastrowid
    imeis_a_vender = set()
    sims_a_vender = set()
    
    # Obtener flags separados para IMEI y SIM
    # Primero revisar si hay flag legacy no_modifica_stock (para compatibilidad)
    no_modifica_stock_legacy = getattr(reporte, 'no_modifica_stock', False)
    no_modifica_imei = getattr(reporte, 'no_modifica_imei', False) or no_modifica_stock_legacy
    no_modifica_sim = getattr(reporte, 'no_modifica_sim', False) or no_modifica_stock_legacy
    
    def _add_imei(v):
        vv = (v or '').strip()
        if vv:
            imeis_a_vender.add(vv)
    
    def _add_sim(v):
        vv = (v or '').strip()
        if vv:
            sims_a_vender.add(vv)
    
    try:
        # Solo recolectar IMEIs si no está marcado no_modifica_imei
        if not no_modifica_imei:
            _add_imei(reporte.imei)
            if getattr(reporte, 'imeis_articulos', None):
                for li in (reporte.imeis_articulos or []):
                    try:
                        for im in (li.get('imeis') or []):
                            _add_imei(im)
                    except Exception:
                        continue
        
        # Solo recolectar SIMs si no está marcado no_modifica_sim
        if not no_modifica_sim:
            _add_sim(reporte.sim_serie)
            if getattr(reporte, 'imeis_articulos', None):
                for li in (reporte.imeis_articulos or []):
                    try:
                        for s in (li.get('sims') or []):
                            _add_sim(s)
                    except Exception:
                        continue
            if getattr(reporte, 'sim_series', None):
                for s in (reporte.sim_series or []):
                    _add_sim(s)
    except Exception:
        pass
    
    # Combinar todos los items a actualizar
    todos_a_vender = imeis_a_vender | sims_a_vender

    imeis_actualizados = 0
    if todos_a_vender:
        cur2 = db.cursor()
        try:
            cur2.executemany(
                "UPDATE imeis SET status='Vendido' WHERE imei=%s",
                [(i,) for i in todos_a_vender]
            )
            imeis_actualizados = cur2.rowcount or 0
        finally:
            cur2.close()
        # Registrar movimientos por cada IMEI/SIM actualizado
        try:
            cur3 = db.cursor(dictionary=True)
            usuario_evt = getattr(reporte, 'usuario', None) or 'sistema'
            for imei_val in todos_a_vender:
                try:
                    cur3.execute("SELECT articulo_id, articulo_nombre FROM imeis WHERE imei=%s", (imei_val,))
                    row = cur3.fetchone() or {}
                    # CAMBIO: Consumir resultados pendientes
                    cur3.fetchall()
                    articulo_id = row.get('articulo_id')
                    articulo_nombre = row.get('articulo_nombre') or ''
                    try:
                        registrar_movimiento(usuario_evt, 'instalacion', articulo_id, articulo_nombre, imei_val, None, None, f'reporte_servicio_id={nuevo_id}')
                    except Exception:
                        pass
                except Exception:
                    continue
            cur3.close()
        except Exception:
            pass

    db.commit()
    # Sincronizar stock de artículos tras marcar IMEIs/SIM como vendidos
    try:
        sincronizar_stock_articulos()
    except Exception:
        pass
    
    # NUEVO: Lógica para Cambio de Equipo - devolver IMEI al stock
    imei_devuelto = False
    if reporte.tipo_servicio == 'Cambio de Equipo' and reporte.imei_devolver:
        try:
            cur_dev = db.cursor()
            # Marcar el IMEI devuelto como 'Devuelto' (disponible nuevamente)
            cur_dev.execute(
                "UPDATE imeis SET status='Devuelto' WHERE imei=%s",
                (reporte.imei_devolver,)
            )
            db.commit()
            imei_devuelto = cur_dev.rowcount > 0
            cur_dev.close()
            # Registrar movimiento de devolución
            if imei_devuelto:
                try:
                    cur_info = db.cursor(dictionary=True)
                    cur_info.execute("SELECT articulo_id, articulo_nombre FROM imeis WHERE imei=%s", (reporte.imei_devolver,))
                    row_info = cur_info.fetchone() or {}
                    # CAMBIO: Consumir resultados pendientes
                    cur_info.fetchall()
                    cur_info.close()
                    registrar_movimiento(
                        reporte.usuario or 'sistema',
                        'devolucion_cambio_equipo',
                        row_info.get('articulo_id'),
                        row_info.get('articulo_nombre', ''),
                        reporte.imei_devolver,
                        None, None,
                        f'reporte_servicio_id={nuevo_id}'
                    )
                except Exception:
                    pass
        except Exception:
            pass
    
    cursor.close()
    db.close()
    return {
        "message": "Reporte de servicio creado exitosamente",
        "reporte_id": nuevo_id,
        "imeis_actualizados": imeis_actualizados,
        "imei_devuelto": imei_devuelto,
        "tipo_servicio": reporte.tipo_servicio
    }
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
    
    if not reporte:
        raise HTTPException(status_code=404, detail=f"No se encontró reporte de servicio para la asignación {asignacion_id}")
    
    # Deserializar JSON si aplica
    try:
        if isinstance(reporte.get("imeis_articulos"), str):
            reporte["imeis_articulos"] = json.loads(reporte["imeis_articulos"]) if reporte["imeis_articulos"] else []
    except Exception:
        pass
    try:
        if isinstance(reporte.get("sim_series"), str):
            reporte["sim_series"] = json.loads(reporte["sim_series"]) if reporte["sim_series"] else []
    except Exception:
        pass
    return reporte

# NUEVO: detalle por ID
@app.get("/reportes-servicio/{reporte_id}")
def get_reporte_servicio_por_id(reporte_id: int):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM reportes_servicio WHERE id = %s", (reporte_id,))
    reporte = cursor.fetchone()
    cursor.close()
    db.close()
    if reporte:
        try:
            if isinstance(reporte.get("imeis_articulos"), str):
                reporte["imeis_articulos"] = json.loads(reporte["imeis_articulos"]) if reporte["imeis_articulos"] else []
        except Exception:
            pass
        try:
            if isinstance(reporte.get("sim_series"), str):
                reporte["sim_series"] = json.loads(reporte["sim_series"]) if reporte["sim_series"] else []
        except Exception:
            pass
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
    # Deserializar JSON en colección y asegurar campo vendedor
    for rep in reportes or []:
        try:
            if isinstance(rep.get("imeis_articulos"), str):
                rep["imeis_articulos"] = json.loads(rep["imeis_articulos"]) if rep["imeis_articulos"] else []
        except Exception:
            pass
        try:
            if isinstance(rep.get("sim_series"), str):
                rep["sim_series"] = json.loads(rep["sim_series"]) if rep["sim_series"] else []
        except Exception:
            pass
        if "vendedor" not in rep:
            rep["vendedor"] = ""
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
        "asignacion_id", "tipo_servicio", "lugar_instalacion", "marca", "submarca", "modelo", "placas", "color", "numero_economico", "equipo_plan", "imei", "serie", "accesorios", "sim_proveedor", "sim_serie", "sim_instalador", "sim_telefono", "bateria", "ignicion", "corte", "ubicacion_corte", "observaciones", "plataforma", "usuario", "subtotal", "forma_pago", "pagado", "nombre_cliente", "firma_cliente", "nombre_instalador", "firma_instalador", "fecha", "monto_tecnico", "viaticos", "vendedor",
        # nuevas columnas para comprobantes
        "comprobante_path", "comprobante_estado", "aprobado_por", "aprobado_fecha",
        # NUEVO: columnas JSON
        "imeis_articulos", "sim_series"
    ]

    vendedor_update = reporte.get("vendedor", None) if isinstance(reporte, dict) else None
    incluye_vendedor = isinstance(reporte, dict) and ("vendedor" in reporte)

    campos = []
    valores = []
    for k, v in reporte.items():
        if k in valid_columns:
            # Serializar JSON para columnas nuevas si viene como lista/dict
            if k in ("imeis_articulos", "sim_series") and v is not None and not isinstance(v, str):
                try:
                    v = json.dumps(v)
                except Exception:
                    pass
            campos.append(f"{k}=%s")
            valores.append(v)

    if not campos and not incluye_vendedor:
        cursor.close()
        db.close()
        raise HTTPException(status_code=400, detail="No hay campos válidos para actualizar.")

    if campos:
        valores.append(reporte_id)
        sql = f"UPDATE reportes_servicio SET {', '.join(campos)} WHERE id=%s"
        cursor.execute(sql, valores)

    # Si viene vendedor, se actualiza en la venta relacionada a la asignación del reporte.
    if incluye_vendedor:
        cursor.execute("SELECT asignacion_id FROM reportes_servicio WHERE id=%s", (reporte_id,))
        row_asig = cursor.fetchone()
        if row_asig and row_asig[0]:
            asignacion_id = row_asig[0]
            cursor.execute("SELECT venta_id FROM venta_tecnico WHERE id=%s", (asignacion_id,))
            row_venta = cursor.fetchone()
            if row_venta and row_venta[0]:
                cursor.execute("UPDATE ventas SET vendedor=%s WHERE id=%s", (vendedor_update, row_venta[0]))

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
    cursor = db.cursor(dictionary=True)
    imeis_to_revert = set()
    try:
        # Intentar leer con columnas nuevas; si falla, fallback a columnas básicas
        try:
            cursor.execute(
                "SELECT imei, sim_serie, imeis_articulos, sim_series FROM reportes_servicio WHERE id=%s",
                (reporte_id,)
            )
        except Exception:
            cursor.execute(
                "SELECT imei, sim_serie FROM reportes_servicio WHERE id=%s",
                (reporte_id,)
            )
        rep = cursor.fetchone()

        def add_imei(val: str | None):
            v = (val or '').strip()
            if v:
                imeis_to_revert.add(v)

        if rep:
            add_imei(rep.get("imei"))
            add_imei(rep.get("sim_serie"))
            # imeis_articulos puede venir como JSON string
            ia = rep.get("imeis_articulos") if isinstance(rep, dict) else None
            if isinstance(ia, (str, bytes)):
                try:
                    ia = json.loads(ia)
                except Exception:
                    ia = None
            if isinstance(ia, list):
                for li in ia:
                    try:
                        for im in (li.get("imeis") or []):
                            add_imei(im)
                        # NUEVO: también considerar SIMs por línea
                        for s in (li.get("sims") or []):
                            add_imei(s)
                    except Exception:
                        continue
            # sim_series puede venir como JSON string
            ss = rep.get("sim_series") if isinstance(rep, dict) else None
            if isinstance(ss, (str, bytes)):
                try:
                    ss = json.loads(ss)
                except Exception:
                    ss = None
            if isinstance(ss, list):
                for s in ss:
                    add_imei(s)

        # Revertir IMEIs a Disponible
        if imeis_to_revert:
            cur2 = db.cursor()
            try:
                cur2.executemany(
                    "UPDATE imeis SET status='Disponible' WHERE imei=%s",
                    [(i,) for i in imeis_to_revert]
                )
            finally:
                cur2.close()

        # Eliminar el reporte
        cur3 = db.cursor()
        try:
            cur3.execute("DELETE FROM reportes_servicio WHERE id=%s", (reporte_id,))
        finally:
            cur3.close()

        db.commit()
    except Exception as e:
        db.rollback()
        cursor.close(); db.close()
        raise HTTPException(status_code=500, detail=f"Error al eliminar reporte: {str(e)}")
    # Sincronizar stock de artículos tras revertir IMEIs/SIM a Disponible
    try:
        sincronizar_stock_articulos()
    except Exception:
        pass
    cursor.close(); db.close()
    return {"message": "Reporte eliminado", "imeis_revertidos": len(imeis_to_revert)}

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
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 días

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
    
    # Actualizar ultima_sesion
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor()
    cursor.execute("UPDATE usuarios SET ultima_sesion = NOW() WHERE id = %s", (user["id"],))
    db.commit()
    cursor.close()
    db.close()
    
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
    if not user:
        cursor.close()
        db.close()
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Actualizar ultima_sesion cada vez que se consulta el usuario
    cursor.execute("UPDATE usuarios SET ultima_sesion = NOW() WHERE id = %s", (user_id,))
    db.commit()
    cursor.close()
    db.close()
    return user

# ---------------------
# Tickets: endpoints básicos
# ---------------------

class TicketCreate(BaseModel):
    cliente: str | None = None
    telefono: str
    usuario_plataforma: str
    titulo: str
    descripcion: str
    prioridad: str
    tipo: str
    imeis: list[str]
    autor: str
    created_by_user_id: int | None = None

class TicketUpdate(BaseModel):
    titulo: str | None = None
    descripcion: str | None = None
    prioridad: str | None = None
    tipo: str | None = None
    estado: str | None = None
    imeis: list[str] | None = None

class TicketComment(BaseModel):
    comment: str
    usuario: str

@app.post("/tickets")
def create_ticket(ticket: TicketCreate):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor()
    try:
        imeis_json = json.dumps(ticket.imeis)
        cursor.execute(
            """
            INSERT INTO tickets (
              cliente, telefono, usuario_plataforma, titulo, descripcion, prioridad, tipo,
              imeis, autor, created_by_user_id, estado
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'nuevo')
            """,
            (
                ticket.cliente, ticket.telefono, ticket.usuario_plataforma, ticket.titulo,
                ticket.descripcion, ticket.prioridad, ticket.tipo, imeis_json,
                ticket.autor, ticket.created_by_user_id
            )
        )
        db.commit()
        new_id = cursor.lastrowid
    except mysql.connector.Error as e:
        db.rollback(); cursor.close(); db.close()
        raise HTTPException(status_code=500, detail=f"Error al crear ticket: {str(e)}")
    cursor.close(); db.close()
    return {"id": new_id}

@app.get("/tickets")
def list_tickets(estado: str | None = Query(None), reporteId: int | None = Query(None)):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor(dictionary=True)
    try:
        base = "SELECT * FROM tickets"
        where = []
        vals = []
        if estado:
            where.append("estado=%s"); vals.append(estado)
        sql = base + (" WHERE " + " AND ".join(where) if where else "") + " ORDER BY id DESC"
        cursor.execute(sql, tuple(vals))
        rows = cursor.fetchall() or []
        for r in rows:
            try:
                if isinstance(r.get("imeis"), str):
                    r["imeis"] = json.loads(r["imeis"]) if r["imeis"] else []
            except Exception:
                r["imeis"] = []
    except mysql.connector.Error as e:
        cursor.close(); db.close()
        raise HTTPException(status_code=500, detail=f"Error al listar tickets: {str(e)}")
    cursor.close(); db.close()
    return rows

@app.get("/tickets/{ticket_id}")
def get_ticket(ticket_id: int):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cur = db.cursor(dictionary=True)
    try:
        cur.execute("SELECT * FROM tickets WHERE id=%s", (ticket_id,))
        row = cur.fetchone()
        if not row:
            cur.close(); db.close()
            raise HTTPException(status_code=404, detail="Ticket no encontrado")
        try:
            if isinstance(row.get("imeis"), str):
                row["imeis"] = json.loads(row["imeis"]) if row["imeis"] else []
        except Exception:
            row["imeis"] = []
        # Comentarios
        try:
            c2 = db.cursor(dictionary=True)
            c2.execute("SELECT id, text, usuario, created_at FROM ticket_comments WHERE ticket_id=%s ORDER BY id ASC", (ticket_id,))
            row["comentarios"] = c2.fetchall() or []
            c2.close()
        except Exception:
            row["comentarios"] = []
    except mysql.connector.Error as e:
        cur.close(); db.close()
        raise HTTPException(status_code=500, detail=f"Error al obtener ticket: {str(e)}")
    cur.close(); db.close()
    return row

@app.patch("/tickets/{ticket_id}")
def update_ticket(ticket_id: int, patch: TicketUpdate):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor()
    try:
        campos = []
        valores = []
        data = patch.model_dump(exclude_unset=True)
        for k, v in data.items():
            col = None
            if k == 'titulo': col = 'titulo'
            elif k == 'descripcion': col = 'descripcion'
            elif k == 'prioridad': col = 'prioridad'
            elif k == 'tipo': col = 'tipo'
            elif k == 'estado': col = 'estado'
            elif k == 'imeis':
                col = 'imeis'
                v = json.dumps(v) if v is not None else None
            # Add support for new fields
            elif k == 'cliente': col = 'cliente'
            elif k == 'telefono': col = 'telefono'
            elif k == 'usuario_plataforma': col = 'usuario_plataforma'
            elif k == 'autor': col = 'autor'
            elif k == 'created_by_user_id': col = 'created_by_user_id'
            if col:
                campos.append(f"{col}=%s")
                valores.append(v)
        if not campos:
            cursor.close(); db.close()
            raise HTTPException(status_code=400, detail="Sin campos para actualizar")
        valores.append(ticket_id)
        sql = f"UPDATE tickets SET {', '.join(campos)} WHERE id=%s"
        cursor.execute(sql, valores)
        db.commit()
    except mysql.connector.Error as e:
        db.rollback(); cursor.close(); db.close()
        raise HTTPException(status_code=500, detail=f"Error al actualizar ticket: {str(e)}")
    cursor.close(); db.close()
    return {"message": "Ticket actualizado"}

@app.post("/tickets/{ticket_id}/comments")
def add_ticket_comment(ticket_id: int, body: TicketComment):
    text = (body.comment or '').strip()
    usuario = (body.usuario or '').strip()
    if not text:
        raise HTTPException(status_code=400, detail="Comentario vacío")
    if not usuario:
        raise HTTPException(status_code=400, detail="Usuario vacío")
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cur = db.cursor()
    try:
        cur.execute("INSERT INTO ticket_comments (ticket_id, text, usuario) VALUES (%s,%s,%s)", (ticket_id, text, usuario))
        db.commit()
    except mysql.connector.Error as e:
        db.rollback(); cur.close(); db.close()
        raise HTTPException(status_code=500, detail=f"Error al comentar: {str(e)}")
    cur.close(); db.close()
    return {"message": "Comentario agregado"}

@app.delete("/tickets/{ticket_id}")
def delete_ticket(ticket_id: int):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cur = db.cursor()
    try:
        # Primero borrar comentarios asociados
        cur.execute("DELETE FROM ticket_comments WHERE ticket_id=%s", (ticket_id,))
        # Luego el ticket
        cur.execute("DELETE FROM tickets WHERE id=%s", (ticket_id,))
        db.commit()
    except mysql.connector.Error as e:
        db.rollback(); cur.close(); db.close()
        raise HTTPException(status_code=500, detail=f"Error al eliminar ticket: {str(e)}")
    cur.close(); db.close()
    return {"message": "Ticket eliminado"}

@app.get("/reportes-servicio/{reporte_id}/context")
def get_reporte_context(reporte_id: int):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor(dictionary=True)
    base = None
    try:
        cursor.execute(
            """
            SELECT rs.id AS reporte_id, rs.folio AS folio_reporte, rs.fecha AS fecha_reporte,
                   vt.id AS asignacion_id, v.id AS venta_id, v.folio AS folio_venta,
                   v.cliente_id, cte.nombre AS cliente_nombre, cte.correo AS cliente_correo,
                   cot.id AS cotizacion_id, cot.status AS cotizacion_status,
                   cot.autorizada AS cotizacion_autorizada, cot.fecha_autorizacion
            FROM reportes_servicio rs
            JOIN venta_tecnico vt ON vt.id = rs.asignacion_id
            JOIN ventas v ON v.id = vt.venta_id
            LEFT JOIN clientes cte ON cte.id = v.cliente_id
            LEFT JOIN cotizaciones cot ON cot.venta_id = v.id
            WHERE rs.id = %s
            LIMIT 1
            """,
            (reporte_id,)
        )
        base = cursor.fetchone()
        if not base:
            cursor.close(); db.close()
            raise HTTPException(status_code=404, detail="Reporte no encontrado")
        # IMEIs desde reporte
        imeis_set = set()
        try:
            c2 = db.cursor(dictionary=True)
            c2.execute("SELECT imei, imeis_articulos FROM reportes_servicio WHERE id=%s", (reporte_id,))
            rep = c2.fetchone() or {}
            c2.close()
            if rep.get("imei"):
                s = (rep["imei"] or '').strip()
                if s:
                    imeis_set.add(s)
            ia = rep.get("imeis_articulos")
            if isinstance(ia, (str, bytes)):
                try: ia = json.loads(ia)
                except Exception: ia = None
            if isinstance(ia, list):
                for li in ia:
                    try:
                        for im in (li.get('imeis') or []):
                            v = (im or '').strip()
                            if v: imeis_set.add(v)
                    except Exception:
                        continue
        except Exception:
            pass
        # IMEIs desde detalle_venta
        try:
            venta_id = base.get('venta_id')
            if venta_id:
                c3 = db.cursor()
                c3.execute("SELECT imei FROM detalle_venta WHERE venta_id=%s AND imei IS NOT NULL AND imei<>''", (venta_id,))
                for (im,) in c3.fetchall() or []:
                    vv = (im or '').strip()
                    if vv: imeis_set.add(vv)
                c3.close()
        except Exception:
            pass
        # Filtrar números de 10-20 dígitos
        def is_valid_imei(s: str) -> bool:
            return s.isdigit() and (10 <= len(s) <= 20)
        imeis_list = [s for s in sorted(imeis_set) if is_valid_imei(s)]
        base['imeis_json'] = imeis_list
        base['imeis_concat'] = ','.join(imeis_list) if imeis_list else None
    except mysql.connector.Error as e:
        cursor.close(); db.close()
        raise HTTPException(status_code=500, detail=f"Error al obtener contexto: {str(e)}")
    cursor.close(); db.close()
    return base

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
    cursor.execute("SELECT id, asignacion_id, folio FROM reportes_servicio WHERE id=%s", (reporte_id,))
    rep = cursor.fetchone()
    if not rep:
        cursor.close()
        db.close()
        raise HTTPException(status_code=404, detail="Reporte no encontrado")

    # Usar el folio del reporte (que ahora es el mismo que el de la venta)
    folio = rep.get("folio")
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

@app.post("/clientes/{cliente_id}/constancia")
async def subir_constancia_fiscal_cliente(cliente_id: int, archivo: UploadFile = File(...), rfc: str = Form(None), request: Request = None):
    ALLOWED_EXT = {'.pdf', '.png', '.jpg', '.jpeg'}
    MAX_SIZE_MB = 8

    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, nombre FROM clientes WHERE id=%s", (cliente_id,))
    cliente_row = cursor.fetchone()
    if not cliente_row:
        cursor.close(); db.close()
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    nombre = cliente_row.get("nombre") or f"CLIENTE-{cliente_id}"
    safe_nombre = ''.join(c for c in nombre if c.isalnum() or c in ('-', '_'))

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

    base_dir = os.path.join('uploads', 'constancias_clientes', safe_nombre)
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
        cursor2.execute("UPDATE clientes SET constancia_path=%s, rfc=COALESCE(%s, rfc) WHERE id=%s", (rel_path, rfc, cliente_id))
        db.commit()
    finally:
        cursor2.close(); cursor.close(); db.close()

    file_url = build_public_url(rel_path, request)
    return {"message": "Constancia fiscal subida exitosamente", "file_url": file_url}

@app.post("/extract-rfc")
async def extract_rfc_from_pdf(archivo: UploadFile = File(...)):
    import PyPDF2
    import re

    if archivo.content_type != 'application/pdf':
        raise HTTPException(status_code=400, detail="Solo archivos PDF")

    data = await archivo.read()
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(data))
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()

    # Buscar RFC: patrón de 12-13 caracteres alfanuméricos, empezando con letras
    rfc_pattern = re.search(r'\b[A-Z]{4}\d{6}[A-Z0-9]{3}\b', text)
    if rfc_pattern:
        rfc = rfc_pattern.group(0)
        return {"rfc": rfc}
    else:
        raise HTTPException(status_code=400, detail="RFC no encontrado en el PDF")


# =====================================================
# ACTIVACIONES RECIENTES - Endpoints
# =====================================================

class ActivacionReciente(BaseModel):
    cuenta: str
    numero_dispositivo: str
    nombre_dispositivo: str = ""
    modelo_dispositivo: str = ""
    numero_tarjeta_sim: str = ""
    hora_activacion: Optional[str] = None
    plataforma: str = ""

class BulkActivacionesRequest(BaseModel):
    activaciones: List[ActivacionReciente]
    cargado_por: str = "sistema"

@app.get("/activaciones-recientes")
def get_activaciones_recientes(
    status: Optional[str] = Query(None, description="Filtrar por status: pendiente, con_reporte, sin_reporte"),
    dias: Optional[int] = Query(30, description="Filtrar por días de antigüedad"),
    cuenta: Optional[str] = Query(None, description="Filtrar por cuenta"),
    limit: Optional[int] = Query(500, description="Límite de registros")
):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor(dictionary=True)
    
    # Construir query con filtros
    query = """
        SELECT 
            ar.id,
            ar.cuenta,
            ar.numero_dispositivo,
            ar.nombre_dispositivo,
            ar.modelo_dispositivo,
            ar.numero_tarjeta_sim,
            ar.hora_activacion,
            ar.plataforma,
            ar.status,
            ar.reporte_servicio_id,
            ar.fecha_carga,
            rs.folio AS folio_reporte,
            rs.tipo_servicio,
            rs.nombre_instalador AS tecnico
        FROM activaciones_recientes ar
        LEFT JOIN reportes_servicio rs ON ar.reporte_servicio_id = rs.id
        WHERE 1=1
    """
    params = []
    
    if status:
        query += " AND ar.status = %s"
        params.append(status)
    
    if dias:
        # Incluir registros con hora_activacion en rango O con hora_activacion NULL pero fecha_carga en rango
        query += """ AND (
            ar.hora_activacion >= DATE_SUB(NOW(), INTERVAL %s DAY)
            OR (ar.hora_activacion IS NULL AND ar.fecha_carga >= DATE_SUB(NOW(), INTERVAL %s DAY))
        )"""
        params.append(dias)
        params.append(dias)
    
    if cuenta:
        query += " AND ar.cuenta LIKE %s"
        params.append(f"%{cuenta}%")
    
    query += " ORDER BY ar.hora_activacion DESC"
    
    if limit:
        query += " LIMIT %s"
        params.append(limit)
    
    cursor.execute(query, params)
    activaciones = cursor.fetchall()
    
    # Convertir datetime a string
    for a in activaciones:
        if a.get('hora_activacion'):
            a['hora_activacion'] = a['hora_activacion'].isoformat() if hasattr(a['hora_activacion'], 'isoformat') else str(a['hora_activacion'])
        if a.get('fecha_carga'):
            a['fecha_carga'] = a['fecha_carga'].isoformat() if hasattr(a['fecha_carga'], 'isoformat') else str(a['fecha_carga'])
    
    cursor.close()
    db.close()
    
    return {
        "total": len(activaciones),
        "activaciones": activaciones
    }

@app.post("/activaciones-recientes/bulk")
def bulk_upsert_activaciones(data: BulkActivacionesRequest):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor(dictionary=True)
    
    insertados = 0
    actualizados = 0
    errores = []
    
    for activacion in data.activaciones:
        try:
            # Parsear fecha si viene como string
            hora_activacion = None
            if activacion.hora_activacion:
                try:
                    # Intentar varios formatos
                    for fmt in ['%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S', '%d/%m/%Y %H:%M:%S', '%Y-%m-%dT%H:%M:%S.%fZ']:
                        try:
                            hora_activacion = datetime.strptime(activacion.hora_activacion.replace('Z', ''), fmt.replace('Z', ''))
                            break
                        except:
                            continue
                    if not hora_activacion:
                        hora_activacion = datetime.fromisoformat(activacion.hora_activacion.replace('Z', '+00:00').replace('+00:00', ''))
                except:
                    hora_activacion = None
            
            # UPSERT: INSERT ... ON DUPLICATE KEY UPDATE
            cursor.execute("""
                INSERT INTO activaciones_recientes (
                    cuenta, numero_dispositivo, nombre_dispositivo, 
                    modelo_dispositivo, numero_tarjeta_sim, hora_activacion,
                    plataforma, cargado_por, status
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'pendiente')
                ON DUPLICATE KEY UPDATE
                    nombre_dispositivo = VALUES(nombre_dispositivo),
                    modelo_dispositivo = VALUES(modelo_dispositivo),
                    numero_tarjeta_sim = VALUES(numero_tarjeta_sim),
                    hora_activacion = VALUES(hora_activacion),
                    plataforma = VALUES(plataforma),
                    fecha_actualizacion = CURRENT_TIMESTAMP
            """, (
                activacion.cuenta,
                activacion.numero_dispositivo,
                activacion.nombre_dispositivo,
                activacion.modelo_dispositivo,
                activacion.numero_tarjeta_sim,
                hora_activacion,
                activacion.plataforma,
                data.cargado_por
            ))
            
            if cursor.rowcount == 1:
                insertados += 1
            elif cursor.rowcount == 2:  # MySQL devuelve 2 en UPDATE
                actualizados += 1
                
        except mysql.connector.Error as e:
            errores.append({
                "dispositivo": activacion.numero_dispositivo,
                "error": str(e)
            })
    
    db.commit()
    
    # Después de insertar, actualizar status basado en reportes existentes
    try:
        cursor.execute("""
            UPDATE activaciones_recientes ar
            INNER JOIN reportes_servicio rs ON ar.numero_dispositivo = rs.imei
            SET ar.status = 'con_reporte', ar.reporte_servicio_id = rs.id
            WHERE ar.status = 'pendiente'
        """)
        
        # Marcar como sin_reporte los que no tienen reporte
        cursor.execute("""
            UPDATE activaciones_recientes
            SET status = 'sin_reporte'
            WHERE status = 'pendiente'
            AND reporte_servicio_id IS NULL
        """)
        
        db.commit()
    except Exception as e:
        print(f"Error actualizando status: {e}")
    
    cursor.close()
    db.close()
    
    return {
        "message": "Carga completada",
        "insertados": insertados,
        "actualizados": actualizados,
        "errores": errores,
        "total_procesados": len(data.activaciones)
    }

@app.get("/activaciones-recientes/verificar-reportes")
def verificar_reportes_activaciones():
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor(dictionary=True)
    
    # Actualizar status basándose en reportes existentes
    # Buscar por IMEI en el campo imei de reportes_servicio
    cursor.execute("""
        UPDATE activaciones_recientes ar
        INNER JOIN reportes_servicio rs ON ar.numero_dispositivo = rs.imei
        SET ar.status = 'con_reporte', ar.reporte_servicio_id = rs.id
        WHERE ar.reporte_servicio_id IS NULL
    """)
    actualizados_imei = cursor.rowcount
    
    # También buscar en imeis_articulos (JSON array)
    cursor.execute("""
        SELECT ar.id, ar.numero_dispositivo, rs.id as reporte_id
        FROM activaciones_recientes ar
        CROSS JOIN reportes_servicio rs
        WHERE ar.reporte_servicio_id IS NULL
        AND rs.imeis_articulos IS NOT NULL
        AND JSON_SEARCH(rs.imeis_articulos, 'all', ar.numero_dispositivo) IS NOT NULL
    """)
    matches_json = cursor.fetchall()
    
    for match in matches_json:
        cursor.execute("""
            UPDATE activaciones_recientes 
            SET status = 'con_reporte', reporte_servicio_id = %s
            WHERE id = %s
        """, (match['reporte_id'], match['id']))
    
    actualizados_json = len(matches_json)
    
    # Marcar como sin_reporte los que no tienen reporte
    cursor.execute("""
        UPDATE activaciones_recientes
        SET status = 'sin_reporte'
        WHERE status = 'pendiente'
        AND reporte_servicio_id IS NULL
    """)
    sin_reporte = cursor.rowcount
    
    db.commit()
    
    # Obtener conteos
    cursor.execute("SELECT status, COUNT(*) as cantidad FROM activaciones_recientes GROUP BY status")
    conteos = {row['status']: row['cantidad'] for row in cursor.fetchall()}
    
    cursor.close()
    db.close()
    
    return {
        "message": "Verificación completada",
        "actualizados_por_imei": actualizados_imei,
        "actualizados_por_json": actualizados_json,
        "marcados_sin_reporte": sin_reporte,
        "conteos": conteos
    }

@app.put("/activaciones-recientes/por-dispositivo/status")
def update_activacion_status_por_dispositivo(data: dict = Body(...)):
    """Actualiza el status de una activación por cuenta y número de dispositivo (IMEI)"""
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor()
    
    cuenta = data.get('cuenta', '').strip() if data.get('cuenta') else ''
    numero_dispositivo = data.get('numero_dispositivo', '').strip() if data.get('numero_dispositivo') else ''
    status = data.get('status')
    
    if not numero_dispositivo:
        raise HTTPException(status_code=400, detail="Número de dispositivo requerido")
    
    if status not in ['pendiente', 'con_reporte', 'sin_reporte', 'es_envio', 'no_requiere', 'desconocido', 'no_encontrado']:
        raise HTTPException(status_code=400, detail="Status inválido")
    
    # Actualizar por IMEI (y opcionalmente cuenta)
    if cuenta:
        cursor.execute("""
            UPDATE activaciones_recientes 
            SET status = %s
            WHERE cuenta = %s AND numero_dispositivo = %s
        """, (status, cuenta, numero_dispositivo))
    else:
        cursor.execute("""
            UPDATE activaciones_recientes 
            SET status = %s
            WHERE numero_dispositivo = %s
        """, (status, numero_dispositivo))
    
    db.commit()
    affected = cursor.rowcount
    cursor.close()
    db.close()
    
    return {"message": "Status actualizado", "actualizados": affected, "status": status}

@app.put("/activaciones-recientes/{activacion_id}/status")
def update_activacion_status(activacion_id: int, data: dict = Body(...)):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor()
    
    status = data.get('status')
    reporte_id = data.get('reporte_servicio_id')
    
    if status not in ['pendiente', 'con_reporte', 'sin_reporte', 'es_envio', 'no_requiere', 'desconocido', 'no_encontrado']:
        raise HTTPException(status_code=400, detail="Status inválido")
    
    cursor.execute("""
        UPDATE activaciones_recientes 
        SET status = %s, reporte_servicio_id = %s
        WHERE id = %s
    """, (status, reporte_id, activacion_id))
    
    db.commit()
    affected = cursor.rowcount
    cursor.close()
    db.close()
    
    if affected == 0:
        raise HTTPException(status_code=404, detail="Activación no encontrada")
    
    return {"message": "Status actualizado", "id": activacion_id, "status": status}

@app.get("/activaciones-recientes/por-imei/{imei}")
def buscar_activacion_por_imei(imei: str):
    """Busca una activación por su IMEI (número de dispositivo)"""
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor(dictionary=True)
    
    imei_limpio = imei.strip()
    
    if not imei_limpio:
        raise HTTPException(status_code=400, detail="IMEI requerido")
    
    cursor.execute("""
        SELECT ar.*, rs.folio as folio_reporte
        FROM activaciones_recientes ar
        LEFT JOIN reportes_servicio rs ON ar.reporte_servicio_id = rs.id
        WHERE ar.numero_dispositivo = %s
        ORDER BY ar.hora_activacion DESC
        LIMIT 1
    """, (imei_limpio,))
    
    activacion = cursor.fetchone()
    cursor.close()
    db.close()
    
    if not activacion:
        raise HTTPException(status_code=404, detail="Activación no encontrada")
    
    # Convertir fechas a string
    for key in ['hora_activacion', 'fecha_carga', 'fecha_actualizacion']:
        if activacion.get(key) and hasattr(activacion[key], 'isoformat'):
            activacion[key] = activacion[key].isoformat()
    
    return activacion

@app.put("/activaciones-recientes/por-imei/sin-reporte")
def marcar_sin_reporte_por_imei(data: dict = Body(...)):
    """Marca una activación como sin_reporte usando solo el IMEI"""
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor()
    
    imei = data.get('imei', '').strip()
    
    if not imei:
        raise HTTPException(status_code=400, detail="IMEI requerido")
    
    cursor.execute("""
        UPDATE activaciones_recientes 
        SET status = 'sin_reporte', reporte_servicio_id = NULL
        WHERE numero_dispositivo = %s
    """, (imei,))
    
    db.commit()
    affected = cursor.rowcount
    cursor.close()
    db.close()
    
    return {"message": "Activación marcada como sin reporte", "imei": imei, "actualizados": affected}

@app.delete("/activaciones-recientes")
def delete_activaciones_antiguas(dias_antiguedad: int = Query(90, description="Eliminar registros más antiguos que X días")):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor()
    
    cursor.execute("""
        DELETE FROM activaciones_recientes 
        WHERE fecha_carga < DATE_SUB(NOW(), INTERVAL %s DAY)
    """, (dias_antiguedad,))
    
    eliminados = cursor.rowcount
    db.commit()
    cursor.close()
    db.close()
    
    return {"message": f"Limpieza completada", "eliminados": eliminados}

@app.get("/activaciones-recientes/stats")
def get_activaciones_stats():
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor(dictionary=True)
    
    # Conteo por status
    cursor.execute("""
        SELECT status, COUNT(*) as cantidad 
        FROM activaciones_recientes 
        GROUP BY status
    """)
    por_status = {row['status']: row['cantidad'] for row in cursor.fetchall()}
    
    # Conteo por modelo
    cursor.execute("""
        SELECT modelo_dispositivo, COUNT(*) as cantidad 
        FROM activaciones_recientes 
        GROUP BY modelo_dispositivo 
        ORDER BY cantidad DESC 
        LIMIT 10
    """)
    por_modelo = cursor.fetchall()
    
    # Activaciones últimos 7 días
    cursor.execute("""
        SELECT DATE(hora_activacion) as fecha, COUNT(*) as cantidad 
        FROM activaciones_recientes 
        WHERE hora_activacion >= DATE_SUB(NOW(), INTERVAL 7 DAY)
        GROUP BY DATE(hora_activacion) 
        ORDER BY fecha DESC
    """)
    ultimos_7_dias = cursor.fetchall()
    for row in ultimos_7_dias:
        if row.get('fecha'):
            row['fecha'] = row['fecha'].isoformat() if hasattr(row['fecha'], 'isoformat') else str(row['fecha'])
    
    cursor.close()
    db.close()
    
    return {
        "por_status": por_status,
        "por_modelo": por_modelo,
        "ultimos_7_dias": ultimos_7_dias,
        "total": sum(por_status.values()) if por_status else 0
    }


# =====================================================
# ENDPOINTS: RENOVACIONES RECIENTES
# =====================================================

@app.get("/renovaciones-recientes")
def get_renovaciones_recientes(
    status: str = Query(None, description="Filtrar por status"),
    dias: int = Query(30, description="Días de antigüedad"),
    cuenta: str = Query(None, description="Filtrar por cuenta"),
    limit: int = Query(1000, description="Límite de registros")
):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor(dictionary=True)
    
    query = """
        SELECT rr.*, rs.folio as folio_reporte
        FROM renovaciones_recientes rr
        LEFT JOIN reportes_servicio rs ON rr.reporte_servicio_id = rs.id
        WHERE (rr.hora_activacion >= DATE_SUB(NOW(), INTERVAL %s DAY) 
               OR rr.hora_activacion IS NULL 
               OR rr.fecha_carga >= DATE_SUB(NOW(), INTERVAL %s DAY))
    """
    params = [dias, dias]
    
    if status:
        query += " AND rr.status = %s"
        params.append(status)
    if cuenta:
        query += " AND rr.cuenta LIKE %s"
        params.append(f"%{cuenta}%")
    
    query += " ORDER BY rr.hora_activacion DESC LIMIT %s"
    params.append(limit)
    
    cursor.execute(query, params)
    renovaciones = cursor.fetchall()
    
    # Convertir fechas a string
    for r in renovaciones:
        for key in ['hora_activacion', 'fecha_carga', 'fecha_actualizacion', 'tiempo_vencimiento_plataforma', 'hora_vencimiento_usuario']:
            if r.get(key) and hasattr(r[key], 'isoformat'):
                r[key] = r[key].isoformat()
    
    cursor.close()
    db.close()
    
    return {"total": len(renovaciones), "renovaciones": renovaciones}

@app.post("/renovaciones-recientes/bulk")
def guardar_renovaciones_bulk(data: dict = Body(...)):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor()
    
    renovaciones = data.get('renovaciones', [])
    cargado_por = data.get('cargado_por', 'sistema')
    
    insertados = 0
    actualizados = 0
    errores = []
    
    for r in renovaciones:
        try:
            cuenta = str(r.get('cuenta', 'SIN_CUENTA')).strip()
            numero_dispositivo = str(r.get('numero_dispositivo', '')).strip()
            
            if not numero_dispositivo:
                continue
            
            # Si no tiene cuenta, usar valor por defecto
            if not cuenta:
                cuenta = 'SIN_CUENTA'
            
            # Parsear fecha de activación
            hora_activacion = None
            hora_raw = r.get('hora_activacion')
            if hora_raw and hora_raw != '-':
                try:
                    if isinstance(hora_raw, str):
                        hora_activacion = hora_raw if hora_raw not in ['', '-', 'null', 'None'] else None
                    elif isinstance(hora_raw, (int, float)):
                        from datetime import datetime, timedelta
                        excel_epoch = datetime(1899, 12, 30)
                        hora_activacion = (excel_epoch + timedelta(days=hora_raw)).strftime('%Y-%m-%d %H:%M:%S')
                except:
                    hora_activacion = None
            
            # Parsear fecha de renovación (nuevo campo)
            fecha_renovacion = None
            fecha_ren_raw = r.get('fecha_renovacion')
            if fecha_ren_raw and fecha_ren_raw != '-':
                try:
                    if isinstance(fecha_ren_raw, str):
                        fecha_renovacion = fecha_ren_raw if fecha_ren_raw not in ['', '-', 'null', 'None'] else None
                    elif isinstance(fecha_ren_raw, (int, float)):
                        from datetime import datetime, timedelta
                        excel_epoch = datetime(1899, 12, 30)
                        fecha_renovacion = (excel_epoch + timedelta(days=fecha_ren_raw)).strftime('%Y-%m-%d %H:%M:%S')
                except:
                    fecha_renovacion = None
            
            # Parsear fechas de vencimiento
            # Valores especiales que indican "de por vida" y no son fechas válidas
            VALORES_VIDA = ['vida', 'para toda la vida', 'lifetime', 'ilimitado', 'unlimited', 'permanente', '-']
            
            tiempo_venc_plat = None
            tiempo_venc_raw = r.get('tiempo_vencimiento_plataforma')
            if tiempo_venc_raw:
                try:
                    if isinstance(tiempo_venc_raw, str):
                        # Verificar si es un valor especial de "vida"
                        if tiempo_venc_raw.strip().lower() in VALORES_VIDA:
                            tiempo_venc_plat = None  # Guardar como NULL
                        elif len(tiempo_venc_raw) >= 10 and tiempo_venc_raw[4] == '-':
                            # Parece una fecha válida (YYYY-MM-DD...)
                            tiempo_venc_plat = tiempo_venc_raw[:10]
                        else:
                            tiempo_venc_plat = None  # No es fecha válida
                    elif isinstance(tiempo_venc_raw, (int, float)):
                        from datetime import datetime, timedelta
                        excel_epoch = datetime(1899, 12, 30)
                        tiempo_venc_plat = (excel_epoch + timedelta(days=tiempo_venc_raw)).strftime('%Y-%m-%d')
                except:
                    tiempo_venc_plat = None
            
            hora_venc_usuario = None
            hora_venc_raw = r.get('hora_vencimiento_usuario')
            if hora_venc_raw:
                try:
                    if isinstance(hora_venc_raw, str):
                        # Verificar si es un valor especial de "vida"
                        if hora_venc_raw.strip().lower() in VALORES_VIDA:
                            hora_venc_usuario = None  # Guardar como NULL
                        elif len(hora_venc_raw) >= 10 and hora_venc_raw[4] == '-':
                            hora_venc_usuario = hora_venc_raw[:10]
                        else:
                            hora_venc_usuario = None
                    elif isinstance(hora_venc_raw, (int, float)):
                        from datetime import datetime, timedelta
                        excel_epoch = datetime(1899, 12, 30)
                        hora_venc_usuario = (excel_epoch + timedelta(days=hora_venc_raw)).strftime('%Y-%m-%d')
                except:
                    hora_venc_usuario = None
            
            # Obtener status del registro
            status = str(r.get('status', 'pendiente')).strip()
            if status not in ['pendiente', 'con_reporte', 'sin_reporte', 'es_envio', 'no_requiere', 'desconocido', 'no_encontrado']:
                status = 'pendiente'
            
            # Si es Tracksolid, guardar tipo_de_servicio
            plataforma_reg = str(r.get('plataforma', 'IOP'))[:50]
            tipo_de_servicio = str(r.get('tipo_de_servicio', ''))[:100] if plataforma_reg.lower() == 'tracksolid' else None
            if plataforma_reg.lower() == 'tracksolid':
                cursor.execute("""
                    INSERT INTO renovaciones_recientes 
                    (cuenta, numero_dispositivo, nombre_dispositivo, modelo_dispositivo, 
                     numero_tarjeta_sim, hora_activacion, plataforma, periodo_de_renovacion,
                     tiempo_vencimiento_plataforma, hora_vencimiento_usuario, cargado_por, status, tipo_de_servicio)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        nombre_dispositivo = VALUES(nombre_dispositivo),
                        modelo_dispositivo = VALUES(modelo_dispositivo),
                        numero_tarjeta_sim = VALUES(numero_tarjeta_sim),
                        hora_activacion = COALESCE(VALUES(hora_activacion), hora_activacion),
                        plataforma = VALUES(plataforma),
                        periodo_de_renovacion = VALUES(periodo_de_renovacion),
                        tiempo_vencimiento_plataforma = VALUES(tiempo_vencimiento_plataforma),
                        hora_vencimiento_usuario = VALUES(hora_vencimiento_usuario),
                        status = VALUES(status),
                        tipo_de_servicio = VALUES(tipo_de_servicio),
                        fecha_actualizacion = NOW()
                """, (
                    cuenta,
                    numero_dispositivo,
                    str(r.get('nombre_dispositivo', ''))[:255],
                    str(r.get('modelo_dispositivo', ''))[:100],
                    str(r.get('numero_tarjeta_sim', ''))[:100],
                    hora_activacion,
                    plataforma_reg,
                    str(r.get('periodo_de_renovacion', ''))[:50],
                    tiempo_venc_plat,
                    hora_venc_usuario,
                    cargado_por,
                    status,
                    tipo_de_servicio
                ))
            else:
                cursor.execute("""
                    INSERT INTO renovaciones_recientes 
                    (cuenta, numero_dispositivo, nombre_dispositivo, modelo_dispositivo, 
                     numero_tarjeta_sim, hora_activacion, plataforma, periodo_de_renovacion,
                     tiempo_vencimiento_plataforma, hora_vencimiento_usuario, cargado_por, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        nombre_dispositivo = VALUES(nombre_dispositivo),
                        modelo_dispositivo = VALUES(modelo_dispositivo),
                        numero_tarjeta_sim = VALUES(numero_tarjeta_sim),
                        hora_activacion = COALESCE(VALUES(hora_activacion), hora_activacion),
                        plataforma = VALUES(plataforma),
                        periodo_de_renovacion = VALUES(periodo_de_renovacion),
                        tiempo_vencimiento_plataforma = VALUES(tiempo_vencimiento_plataforma),
                        hora_vencimiento_usuario = VALUES(hora_vencimiento_usuario),
                        status = VALUES(status),
                        fecha_actualizacion = NOW()
                """, (
                    cuenta,
                    numero_dispositivo,
                    str(r.get('nombre_dispositivo', ''))[:255],
                    str(r.get('modelo_dispositivo', ''))[:100],
                    str(r.get('numero_tarjeta_sim', ''))[:100],
                    hora_activacion,
                    plataforma_reg,
                    str(r.get('periodo_de_renovacion', ''))[:50],
                    tiempo_venc_plat,
                    hora_venc_usuario,
                    cargado_por,
                    status
                ))
            
            if cursor.rowcount == 1:
                insertados += 1
            else:
                actualizados += 1
                
        except Exception as e:
            errores.append({"registro": r, "error": str(e)})
    
    db.commit()
    cursor.close()
    db.close()
    
    return {
        "insertados": insertados,
        "actualizados": actualizados,
        "errores": errores[:10]  # Limitar errores mostrados
    }

@app.get("/renovaciones-recientes/verificar-reportes")
def verificar_reportes_renovaciones():
    """Verifica y actualiza el status de reportes para renovaciones"""
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor(dictionary=True)
    
    # Buscar renovaciones que tienen reporte por IMEI
    cursor.execute("""
        UPDATE renovaciones_recientes rr
        INNER JOIN reportes_servicio rs ON rr.numero_dispositivo = rs.imei
        SET rr.status = 'con_reporte', rr.reporte_servicio_id = rs.id
        WHERE rr.status != 'con_reporte'
    """)
    actualizados_imei = cursor.rowcount
    
    # Marcar como sin_reporte los que no tienen reporte
    cursor.execute("""
        UPDATE renovaciones_recientes 
        SET status = 'sin_reporte'
        WHERE status = 'pendiente' 
        AND reporte_servicio_id IS NULL
        AND status NOT IN ('es_envio', 'no_requiere')
    """)
    sin_reporte = cursor.rowcount
    
    # Obtener conteos actualizados
    cursor.execute("""
        SELECT status, COUNT(*) as cantidad 
        FROM renovaciones_recientes 
        GROUP BY status
    """)
    conteos = {row['status']: row['cantidad'] for row in cursor.fetchall()}
    
    db.commit()
    cursor.close()
    db.close()
    
    return {
        "actualizados_por_imei": actualizados_imei,
        "marcados_sin_reporte": sin_reporte,
        "conteos": conteos
    }

@app.put("/renovaciones-recientes/{renovacion_id}/status")
def update_renovacion_status(renovacion_id: int, data: dict = Body(...)):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor()
    
    status = data.get('status')
    reporte_id = data.get('reporte_servicio_id')
    
    if status not in ['pendiente', 'con_reporte', 'sin_reporte', 'es_envio', 'no_requiere', 'desconocido', 'no_encontrado']:
        raise HTTPException(status_code=400, detail="Status inválido")
    
    cursor.execute("""
        UPDATE renovaciones_recientes 
        SET status = %s, reporte_servicio_id = %s
        WHERE id = %s
    """, (status, reporte_id, renovacion_id))
    
    db.commit()
    affected = cursor.rowcount
    cursor.close()
    db.close()
    
    if affected == 0:
        raise HTTPException(status_code=404, detail="Renovación no encontrada")
    
    return {"message": "Status actualizado", "id": renovacion_id, "status": status}

@app.put("/renovaciones-recientes/por-imei/sin-reporte")
def marcar_renovacion_sin_reporte_por_imei(data: dict = Body(...)):
    """Marca una renovación como sin_reporte usando solo el IMEI"""
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor()
    
    imei = data.get('imei', '').strip()
    
    if not imei:
        raise HTTPException(status_code=400, detail="IMEI requerido")
    
    cursor.execute("""
        UPDATE renovaciones_recientes 
        SET status = 'sin_reporte', reporte_servicio_id = NULL
        WHERE numero_dispositivo = %s
    """, (imei,))
    
    db.commit()
    affected = cursor.rowcount
    cursor.close()
    db.close()
    
    return {"message": "Renovación marcada como sin reporte", "imei": imei, "actualizados": affected}

@app.put("/renovaciones-recientes/por-dispositivo/status")
def update_renovacion_status_por_dispositivo(data: dict = Body(...)):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor()
    
    cuenta = data.get('cuenta', '').strip()
    numero_dispositivo = data.get('numero_dispositivo', '').strip()
    status = data.get('status')
    
    if not numero_dispositivo:
        raise HTTPException(status_code=400, detail="Número de dispositivo requerido")
    
    if status not in ['pendiente', 'con_reporte', 'sin_reporte', 'es_envio', 'no_requiere', 'desconocido', 'no_encontrado']:
        raise HTTPException(status_code=400, detail="Status inválido")
    
    if cuenta:
        cursor.execute("""
            UPDATE renovaciones_recientes 
            SET status = %s
            WHERE cuenta = %s AND numero_dispositivo = %s
        """, (status, cuenta, numero_dispositivo))
    else:
        cursor.execute("""
            UPDATE renovaciones_recientes 
            SET status = %s
            WHERE numero_dispositivo = %s
        """, (status, numero_dispositivo))
    
    db.commit()
    affected = cursor.rowcount
    cursor.close()
    db.close()
    
    return {"message": "Status actualizado", "actualizados": affected}

@app.delete("/renovaciones-recientes")
def delete_renovaciones_antiguas(dias_antiguedad: int = Query(90, description="Eliminar registros más antiguos que X días")):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor()
    
    cursor.execute("""
        DELETE FROM renovaciones_recientes 
        WHERE fecha_carga < DATE_SUB(NOW(), INTERVAL %s DAY)
    """, (dias_antiguedad,))
    
    eliminados = cursor.rowcount
    db.commit()
    cursor.close()
    db.close()
    
    return {"message": "Limpieza completada", "eliminados": eliminados}

@app.get("/renovaciones-recientes/stats")
def get_renovaciones_stats():
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor(dictionary=True)
    
    # Conteo por status
    cursor.execute("""
        SELECT status, COUNT(*) as cantidad 
        FROM renovaciones_recientes 
        GROUP BY status
    """)
    por_status = {row['status']: row['cantidad'] for row in cursor.fetchall()}
    
    # Conteo por periodo de renovación
    cursor.execute("""
        SELECT periodo_de_renovacion, COUNT(*) as cantidad 
        FROM renovaciones_recientes 
        GROUP BY periodo_de_renovacion 
        ORDER BY cantidad DESC
    """)
    por_periodo = cursor.fetchall()
    
    # Renovaciones últimos 7 días
    cursor.execute("""
        SELECT DATE(hora_activacion) as fecha, COUNT(*) as cantidad 
        FROM renovaciones_recientes 
        WHERE hora_activacion >= DATE_SUB(NOW(), INTERVAL 7 DAY)
        GROUP BY DATE(hora_activacion) 
        ORDER BY fecha DESC
    """)
    ultimos_7_dias = cursor.fetchall()
    for row in ultimos_7_dias:
        if row.get('fecha'):
            row['fecha'] = row['fecha'].isoformat() if hasattr(row['fecha'], 'isoformat') else str(row['fecha'])
    
    cursor.close()
    db.close()
    
    return {
        "por_status": por_status,
        "por_periodo": por_periodo,
        "ultimos_7_dias": ultimos_7_dias,
        "total": sum(por_status.values()) if por_status else 0
    }

@app.post("/renovaciones-recientes/datos-reporte")
def get_datos_reporte_renovacion(data: dict = Body(...)):
    """
    Recibe: imei, plataforma, sim, tipo_servicio, total, forma_pago
    Devuelve: todos los datos necesarios para generar el reporte de renovación:
      - datos de renovaciones_recientes (BD interna)
      - datos en vivo del dispositivo desde la API de la plataforma (IOP o Tracksolid)
      - datos del cliente relacionado
    """
    imei_input = str(data.get("imei", "")).strip()
    plataforma_input = str(data.get("plataforma", "")).strip()
    sim_input = str(data.get("sim", "")).strip()
    tipo_servicio_input = str(data.get("tipo_servicio", "")).strip()
    total_input = data.get("total", 0)
    forma_pago_input = str(data.get("forma_pago", "")).strip()

    if not imei_input:
        raise HTTPException(status_code=400, detail="El campo 'imei' es requerido")

    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor(dictionary=True)

    # 1. Buscar renovación reciente por IMEI en BD interna
    if plataforma_input:
        cursor.execute("""
            SELECT * FROM renovaciones_recientes
            WHERE numero_dispositivo = %s AND plataforma = %s
            ORDER BY hora_activacion DESC
            LIMIT 1
        """, (imei_input, plataforma_input))
    else:
        cursor.execute("""
            SELECT * FROM renovaciones_recientes
            WHERE numero_dispositivo = %s
            ORDER BY hora_activacion DESC
            LIMIT 1
        """, (imei_input,))
    renovacion = cursor.fetchone()

    # Convertir fechas a string
    if renovacion:
        for key in ['hora_activacion', 'fecha_carga', 'fecha_actualizacion',
                    'tiempo_vencimiento_plataforma', 'hora_vencimiento_usuario']:
            if renovacion.get(key) and hasattr(renovacion[key], 'isoformat'):
                renovacion[key] = renovacion[key].isoformat()

    cuenta = renovacion["cuenta"] if renovacion else ""
    nombre_dispositivo = renovacion["nombre_dispositivo"] if renovacion else ""
    modelo_dispositivo = renovacion["modelo_dispositivo"] if renovacion else ""
    sim_renovacion = renovacion["numero_tarjeta_sim"] if renovacion else ""
    periodo_renovacion = renovacion["periodo_de_renovacion"] if renovacion else ""
    vencimiento_plataforma = renovacion.get("tiempo_vencimiento_plataforma") if renovacion else None
    plataforma_final = renovacion["plataforma"] if renovacion else plataforma_input

    sim_final = sim_input if sim_input else sim_renovacion

    # 2. Buscar cliente por cuenta de plataforma
    cliente_id = None
    nombre_cliente = "NA"
    telefono_cliente = ""
    correo_cliente = ""
    direccion_cliente = ""

    if cuenta:
        cursor.execute("""
            SELECT c.id, c.nombre, c.correo, c.direccion
            FROM clientes c
            INNER JOIN usuarios_cliente uc ON uc.cliente_id = c.id
            WHERE LOWER(uc.usuario) = LOWER(%s)
            LIMIT 1
        """, (cuenta,))
        cliente_row = cursor.fetchone()
        if cliente_row:
            cliente_id = cliente_row["id"]
            nombre_cliente = cliente_row["nombre"]
            correo_cliente = cliente_row["correo"] or ""
            direccion_cliente = cliente_row["direccion"] or ""
            cursor.execute("SELECT telefono FROM telefonos_cliente WHERE cliente_id = %s LIMIT 1", (cliente_id,))
            tel_row = cursor.fetchone()
            telefono_cliente = tel_row["telefono"] if tel_row else ""

    cursor.close()
    db.close()

    # 3. Consultar la API de la plataforma en vivo por IMEI
    plataforma_data = None
    plataforma_error = None
    plat_lower = plataforma_final.lower().strip() if plataforma_final else plataforma_input.lower().strip()

    try:
        if plat_lower == "iop":
            if not os.getenv("IOPGPS_APPID"):
                plataforma_error = "Credenciales IOP no configuradas en .env"
            else:
                iop = IOPGPSClient()
                resp = iop.get_device_detail(imei_input)
                if resp.get("code") == 0 and resp.get("data"):
                    raw = resp["data"]
                    # raw puede ser dict o list; normalizar a dict
                    if isinstance(raw, list) and raw:
                        raw = raw[0]
                    plataforma_data = raw
                    # Rellenar campos vacíos con datos de la plataforma si los tenemos
                    if not nombre_dispositivo:
                        nombre_dispositivo = raw.get("deviceName") or raw.get("name") or ""
                    if not modelo_dispositivo:
                        modelo_dispositivo = raw.get("model") or raw.get("deviceModel") or ""
                    if not cuenta:
                        cuenta = raw.get("account") or raw.get("accountId") or ""
                    if not sim_final:
                        sim_final = raw.get("sim") or raw.get("simNum") or ""
                else:
                    plataforma_error = resp.get("result") or resp.get("message") or "Sin datos"

        elif plat_lower in ("tracksolid", "tracksolidpro", "track"):
            if not os.getenv("TRACKSOLID_APP_KEY"):
                plataforma_error = "Credenciales Tracksolid no configuradas en .env"
            else:
                ts = _get_tracksolid_client()
                resp = ts.fetch_device_detail(imei_input)
                if resp.get("code") == 0 and resp.get("result"):
                    raw = resp["result"]
                    if isinstance(raw, list) and raw:
                        raw = raw[0]
                    plataforma_data = raw
                    if not nombre_dispositivo:
                        nombre_dispositivo = raw.get("deviceName") or raw.get("name") or ""
                    if not modelo_dispositivo:
                        modelo_dispositivo = raw.get("model") or raw.get("deviceModel") or ""
                    if not cuenta:
                        cuenta = raw.get("_account") or raw.get("account") or ""
                    if not sim_final:
                        sim_final = raw.get("sim") or raw.get("simNum") or ""
                    if not vencimiento_plataforma:
                        vencimiento_plataforma = raw.get("expireTime") or raw.get("serviceExpiredTime") or None
                else:
                    plataforma_error = resp.get("message") or f"code={resp.get('code')}"
        else:
            plataforma_error = f"Plataforma no reconocida: '{plataforma_final}'"

    except Exception as e:
        plataforma_error = str(e)

    return {
        # Datos que llegaron del frontend
        "imei": imei_input,
        "sim": sim_final,
        "plataforma": plataforma_final,
        "tipo_servicio": tipo_servicio_input,
        "total": total_input,
        "forma_pago": forma_pago_input,
        # Datos del dispositivo (combinados: BD interna + plataforma en vivo)
        "nombre_dispositivo": nombre_dispositivo,
        "modelo_dispositivo": modelo_dispositivo,
        "periodo_renovacion": periodo_renovacion,
        "vencimiento_plataforma": vencimiento_plataforma,
        "cuenta_plataforma": cuenta,
        # Datos del cliente
        "cliente_id": cliente_id,
        "nombre_cliente": nombre_cliente,
        "telefono_cliente": telefono_cliente,
        "correo_cliente": correo_cliente,
        "direccion_cliente": direccion_cliente,
        # Datos en vivo de la plataforma (respuesta RAW para uso adicional)
        "plataforma_live": plataforma_data,
        "plataforma_error": plataforma_error,
        # Registro completo de renovacion_reciente (BD interna)
        "renovacion_reciente": renovacion,
    }

# ═══════════════════════════════════════════════════════════════════════
# ══════════════ NOTAS DE PAGO ═════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════════════

class NotaPagoCreate(BaseModel):
    ordenes: List[str]
    cliente: str
    total: float
    status: str = "pendiente de pago"
    reporte_ids: List[int] = []

@app.get("/notas-pago")
def get_notas_pago():
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM notas_pago ORDER BY id DESC")
    rows = cursor.fetchall()
    # Parsear ordenes JSON
    for r in rows:
        if isinstance(r.get('ordenes'), str):
            try:
                r['ordenes'] = json.loads(r['ordenes'])
            except Exception:
                r['ordenes'] = []
        if isinstance(r.get('reporte_ids'), str):
            try:
                r['reporte_ids'] = json.loads(r['reporte_ids'])
            except Exception:
                r['reporte_ids'] = []
        if r.get('fecha') and hasattr(r['fecha'], 'isoformat'):
            r['fecha'] = r['fecha'].isoformat()
        # Obtener IMEIs asociados desde reportes_servicio
        r['imeis'] = []
        rids = r.get('reporte_ids') or []
        if rids:
            placeholders = ','.join(['%s'] * len(rids))
            cursor.execute(f"SELECT imei, imeis_articulos FROM reportes_servicio WHERE id IN ({placeholders})", tuple(rids))
            reps = cursor.fetchall()
            imeis_set = []
            for rep in reps:
                if rep.get('imei'):
                    imeis_set.append(rep['imei'])
                ia = rep.get('imeis_articulos')
                if isinstance(ia, str):
                    try:
                        ia = json.loads(ia)
                    except Exception:
                        ia = []
                if isinstance(ia, list):
                    for item in ia:
                        for im in (item.get('imeis') or []):
                            if im:
                                imeis_set.append(im)
            r['imeis'] = imeis_set
        # Obtener instalador y vendedor desde reportes_servicio
        r['instalador'] = ''
        r['vendedor'] = ''
        if rids:
            placeholders2 = ','.join(['%s'] * len(rids))
            cursor.execute(f"SELECT nombre_instalador, vendedor FROM reportes_servicio WHERE id IN ({placeholders2})", tuple(rids))
            reps2 = cursor.fetchall()
            instaladores = list({rep['nombre_instalador'] for rep in reps2 if rep.get('nombre_instalador')})
            vendedores_list = list({rep['vendedor'] for rep in reps2 if rep.get('vendedor')})
            r['instalador'] = ', '.join(instaladores)
            r['vendedor'] = ', '.join(vendedores_list)
    cursor.close()
    db.close()
    return rows

@app.get("/notas-pago/{nota_id}")
def get_nota_pago(nota_id: int):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM notas_pago WHERE id=%s", (nota_id,))
    row = cursor.fetchone()
    # Buscar detalle de órdenes (reportes asociados)
    detalle_ordenes = []
    if row:
        if isinstance(row.get('ordenes'), str):
            try:
                row['ordenes'] = json.loads(row['ordenes'])
            except Exception:
                row['ordenes'] = []
        reporte_ids = []
        if isinstance(row.get('reporte_ids'), str):
            try:
                reporte_ids = json.loads(row['reporte_ids'])
            except Exception:
                reporte_ids = []
        row['reporte_ids'] = reporte_ids
        if reporte_ids:
            placeholders = ','.join(['%s'] * len(reporte_ids))
            cursor.execute(f"SELECT id, folio, tipo_servicio, nombre_cliente, total, plataforma, usuario, imei FROM reportes_servicio WHERE id IN ({placeholders})", tuple(reporte_ids))
            detalle_ordenes = cursor.fetchall()
            for d in detalle_ordenes:
                if d.get('total') is not None:
                    d['total'] = float(d['total'])
        row['detalle_ordenes'] = detalle_ordenes
        if row.get('fecha') and hasattr(row['fecha'], 'isoformat'):
            row['fecha'] = row['fecha'].isoformat()
        # Parsear comprobantes JSON
        if isinstance(row.get('comprobantes'), str):
            try:
                row['comprobantes'] = json.loads(row['comprobantes'])
            except Exception:
                row['comprobantes'] = []
        if row.get('comprobantes') is None:
            row['comprobantes'] = []
    cursor.close()
    db.close()
    if not row:
        raise HTTPException(status_code=404, detail="Nota no encontrada")
    return row

@app.post("/notas-pago")
def crear_nota_pago(data: NotaPagoCreate):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor()
    cursor.execute(
        """INSERT INTO notas_pago (ordenes, cliente, total, status, reporte_ids, fecha)
           VALUES (%s, %s, %s, %s, %s, NOW())""",
        (
            json.dumps(data.ordenes),
            data.cliente,
            data.total,
            data.status,
            json.dumps(data.reporte_ids)
        )
    )
    db.commit()
    new_id = cursor.lastrowid
    cursor.close()
    db.close()
    return {"message": "Nota creada exitosamente", "id": new_id}

@app.put("/notas-pago/{nota_id}/status")
def actualizar_status_nota(nota_id: int, data: dict = Body(...)):
    new_status = data.get('status', '').strip()
    if new_status not in ('pendiente de pago', 'pagado', 'cancelado'):
        raise HTTPException(status_code=400, detail="Status inválido. Valores: pendiente de pago, pagado, cancelado")
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor()
    if new_status == 'cancelado':
        cursor.execute("UPDATE notas_pago SET status=%s, reporte_ids=%s WHERE id=%s", (new_status, json.dumps([]), nota_id))
    else:
        cursor.execute("UPDATE notas_pago SET status=%s WHERE id=%s", (new_status, nota_id))
    db.commit()
    affected = cursor.rowcount
    cursor.close()
    db.close()
    if affected == 0:
        raise HTTPException(status_code=404, detail="Nota no encontrada")
    return {"message": "Status actualizado", "id": nota_id, "status": new_status}

@app.put("/notas-pago/{nota_id}/lugar-pago")
def actualizar_lugar_pago_nota(nota_id: int, data: dict = Body(...)):
    lugar_pago = data.get('lugar_pago', '').strip()
    lugares_validos = ['ASP Vianey', 'ASP Renovaciones', 'Comercializadora', 'BBVA PAU', 'Tecnico', 'Oficina', 'Mercadopago']
    if lugar_pago and lugar_pago not in lugares_validos:
        raise HTTPException(status_code=400, detail=f"Lugar de pago inválido. Valores: {', '.join(lugares_validos)}")
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor()
    cursor.execute("UPDATE notas_pago SET lugar_pago=%s WHERE id=%s", (lugar_pago if lugar_pago else None, nota_id))
    db.commit()
    affected = cursor.rowcount
    cursor.close()
    db.close()
    if affected == 0:
        raise HTTPException(status_code=404, detail="Nota no encontrada")
    return {"message": "Lugar de pago actualizado", "id": nota_id, "lugar_pago": lugar_pago or None}

@app.put("/notas-pago/{nota_id}/observaciones")
def actualizar_observaciones_nota(nota_id: int, data: dict = Body(...)):
    observaciones = data.get('observaciones', '')
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor()
    cursor.execute("UPDATE notas_pago SET observaciones=%s WHERE id=%s", (observaciones or None, nota_id))
    db.commit()
    affected = cursor.rowcount
    cursor.close()
    db.close()
    if affected == 0:
        raise HTTPException(status_code=404, detail="Nota no encontrada")
    return {"message": "Observaciones actualizadas", "id": nota_id}

@app.delete("/notas-pago/{nota_id}")
def eliminar_nota_pago(nota_id: int):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor()
    cursor.execute("DELETE FROM notas_pago WHERE id=%s", (nota_id,))
    db.commit()
    affected = cursor.rowcount
    cursor.close()
    db.close()
    if affected == 0:
        raise HTTPException(status_code=404, detail="Nota no encontrada")
    return {"message": "Nota eliminada"}

@app.post("/notas-pago/{nota_id}/comprobante")
def subir_comprobante_nota(nota_id: int, archivo: UploadFile = File(...)):
    import shutil
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, comprobantes FROM notas_pago WHERE id=%s", (nota_id,))
    row = cursor.fetchone()
    if not row:
        cursor.close()
        db.close()
        raise HTTPException(status_code=404, detail="Nota no encontrada")
    # Parsear lista existente
    existentes = []
    if row.get('comprobantes'):
        try:
            existentes = json.loads(row['comprobantes']) if isinstance(row['comprobantes'], str) else row['comprobantes']
        except Exception:
            existentes = []
    base_dir = os.path.join("uploads", "pagos", "notas", str(nota_id))
    os.makedirs(base_dir, exist_ok=True)
    filename = archivo.filename or "comprobante"
    filename = ''.join(c for c in filename if c.isalnum() or c in ('-', '_', '.', ' ')).strip()
    # Evitar colisión de nombres
    dest_path = os.path.join(base_dir, filename)
    base_name, ext = os.path.splitext(filename)
    counter = 1
    while os.path.exists(dest_path):
        dest_path = os.path.join(base_dir, f"{base_name}_{counter}{ext}")
        counter += 1
    with open(dest_path, "wb") as out:
        shutil.copyfileobj(archivo.file, out)
    rel_path = dest_path.replace("\\", "/")
    existentes.append(rel_path)
    cursor2 = db.cursor()
    cursor2.execute("UPDATE notas_pago SET comprobantes=%s WHERE id=%s", (json.dumps(existentes), nota_id))
    db.commit()
    cursor2.close()
    cursor.close()
    db.close()
    return {"message": "Comprobante subido", "path": rel_path, "comprobantes": existentes}

@app.delete("/notas-pago/{nota_id}/comprobante")
def eliminar_comprobante_nota(nota_id: int, data: dict = Body(...)):
    path = data.get('path', '').strip()
    if not path:
        raise HTTPException(status_code=400, detail="Se requiere 'path' del comprobante a eliminar")
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, comprobantes FROM notas_pago WHERE id=%s", (nota_id,))
    row = cursor.fetchone()
    if not row:
        cursor.close()
        db.close()
        raise HTTPException(status_code=404, detail="Nota no encontrada")
    existentes = []
    if row.get('comprobantes'):
        try:
            existentes = json.loads(row['comprobantes']) if isinstance(row['comprobantes'], str) else row['comprobantes']
        except Exception:
            existentes = []
    if path not in existentes:
        cursor.close()
        db.close()
        raise HTTPException(status_code=404, detail="Comprobante no encontrado en la lista")
    existentes.remove(path)
    # Eliminar archivo físico
    if os.path.exists(path):
        os.remove(path)
    cursor2 = db.cursor()
    cursor2.execute("UPDATE notas_pago SET comprobantes=%s WHERE id=%s", (json.dumps(existentes), nota_id))
    db.commit()
    cursor2.close()
    cursor.close()
    db.close()
    return {"message": "Comprobante eliminado", "comprobantes": existentes}

@app.put("/notas-pago/{nota_id}/agregar-reportes")
def agregar_reportes_nota(nota_id: int, data: dict = Body(...)):
    nuevos_ids = data.get('reporte_ids', [])
    if not nuevos_ids:
        raise HTTPException(status_code=400, detail="Se requiere 'reporte_ids'")
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, reporte_ids, status FROM notas_pago WHERE id=%s", (nota_id,))
    nota = cursor.fetchone()
    if not nota:
        cursor.close(); db.close()
        raise HTTPException(status_code=404, detail="Nota no encontrada")
    if nota.get('status') == 'pagado':
        cursor.close(); db.close()
        raise HTTPException(status_code=400, detail="No se puede modificar una nota pagada")
    existing_ids = []
    if nota.get('reporte_ids'):
        try:
            existing_ids = json.loads(nota['reporte_ids']) if isinstance(nota['reporte_ids'], str) else nota['reporte_ids']
        except Exception:
            existing_ids = []
    combined_ids = list(dict.fromkeys(existing_ids + nuevos_ids))  # preservar orden, sin duplicados
    new_ordenes = []
    new_total = 0.0
    if combined_ids:
        placeholders = ','.join(['%s'] * len(combined_ids))
        cursor.execute(f"SELECT id, folio, total FROM reportes_servicio WHERE id IN ({placeholders})", tuple(combined_ids))
        reportes = cursor.fetchall()
        new_ordenes = [r['folio'] for r in reportes if r.get('folio')]
        new_total = sum(float(r['total'] or 0) for r in reportes)
    cursor2 = db.cursor()
    cursor2.execute(
        "UPDATE notas_pago SET reporte_ids=%s, ordenes=%s, total=%s WHERE id=%s",
        (json.dumps(combined_ids), json.dumps(new_ordenes), new_total, nota_id)
    )
    db.commit()
    cursor2.close(); cursor.close(); db.close()
    return {"message": "Reportes agregados", "id": nota_id, "reporte_ids": combined_ids}

@app.put("/notas-pago/{nota_id}/quitar-reportes")
def quitar_reportes_nota(nota_id: int, data: dict = Body(...)):
    ids_a_quitar = data.get('reporte_ids', [])
    if not ids_a_quitar:
        raise HTTPException(status_code=400, detail="Se requiere 'reporte_ids'")
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, reporte_ids, status FROM notas_pago WHERE id=%s", (nota_id,))
    nota = cursor.fetchone()
    if not nota:
        cursor.close(); db.close()
        raise HTTPException(status_code=404, detail="Nota no encontrada")
    if nota.get('status') == 'pagado':
        cursor.close(); db.close()
        raise HTTPException(status_code=400, detail="No se puede modificar una nota pagada")
    existing_ids = []
    if nota.get('reporte_ids'):
        try:
            existing_ids = json.loads(nota['reporte_ids']) if isinstance(nota['reporte_ids'], str) else nota['reporte_ids']
        except Exception:
            existing_ids = []
    quitar_set = set(ids_a_quitar)
    combined_ids = [rid for rid in existing_ids if rid not in quitar_set]
    new_ordenes = []
    new_total = 0.0
    if combined_ids:
        placeholders = ','.join(['%s'] * len(combined_ids))
        cursor.execute(f"SELECT id, folio, total FROM reportes_servicio WHERE id IN ({placeholders})", tuple(combined_ids))
        reportes = cursor.fetchall()
        new_ordenes = [r['folio'] for r in reportes if r.get('folio')]
        new_total = sum(float(r['total'] or 0) for r in reportes)
    cursor2 = db.cursor()
    cursor2.execute(
        "UPDATE notas_pago SET reporte_ids=%s, ordenes=%s, total=%s WHERE id=%s",
        (json.dumps(combined_ids), json.dumps(new_ordenes), new_total, nota_id)
    )
    db.commit()
    cursor2.close(); cursor.close(); db.close()
    return {"message": "Reportes quitados", "id": nota_id, "reporte_ids": combined_ids}


# ═══════════════════════════════════════════════════════════════════════
# ══════════════ FACTURAS DE PAGO ═════════════════════════════════════
# ═══════════════════════════════════════════════════════════════════════

class FacturaPagoCreate(BaseModel):
    ordenes: List[str]
    cliente: str
    total: float
    status: str = "Pendiente timbre"
    reporte_ids: List[int] = []

@app.get("/facturas-pago")
def get_facturas_pago():
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM facturas_pago ORDER BY id DESC")
    rows = cursor.fetchall()
    for r in rows:
        if isinstance(r.get('ordenes'), str):
            try:
                r['ordenes'] = json.loads(r['ordenes'])
            except Exception:
                r['ordenes'] = []
        if isinstance(r.get('reporte_ids'), str):
            try:
                r['reporte_ids'] = json.loads(r['reporte_ids'])
            except Exception:
                r['reporte_ids'] = []
        if r.get('fecha') and hasattr(r['fecha'], 'isoformat'):
            r['fecha'] = r['fecha'].isoformat()
        # Obtener IMEIs asociados desde reportes_servicio
        r['imeis'] = []
        rids = r.get('reporte_ids') or []
        if rids:
            placeholders = ','.join(['%s'] * len(rids))
            cursor.execute(f"SELECT imei, imeis_articulos FROM reportes_servicio WHERE id IN ({placeholders})", tuple(rids))
            reps = cursor.fetchall()
            imeis_set = []
            for rep in reps:
                if rep.get('imei'):
                    imeis_set.append(rep['imei'])
                ia = rep.get('imeis_articulos')
                if isinstance(ia, str):
                    try:
                        ia = json.loads(ia)
                    except Exception:
                        ia = []
                if isinstance(ia, list):
                    for item in ia:
                        for im in (item.get('imeis') or []):
                            if im:
                                imeis_set.append(im)
            r['imeis'] = imeis_set
        # Obtener instalador y vendedor desde reportes_servicio
        r['instalador'] = ''
        r['vendedor'] = ''
        if rids:
            placeholders2 = ','.join(['%s'] * len(rids))
            cursor.execute(f"SELECT nombre_instalador, vendedor FROM reportes_servicio WHERE id IN ({placeholders2})", tuple(rids))
            reps2 = cursor.fetchall()
            instaladores = list({rep['nombre_instalador'] for rep in reps2 if rep.get('nombre_instalador')})
            vendedores_list = list({rep['vendedor'] for rep in reps2 if rep.get('vendedor')})
            r['instalador'] = ', '.join(instaladores)
            r['vendedor'] = ', '.join(vendedores_list)
    cursor.close()
    db.close()
    return rows

@app.get("/facturas-pago/{factura_id}")
def get_factura_pago(factura_id: int):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM facturas_pago WHERE id=%s", (factura_id,))
    row = cursor.fetchone()
    detalle_ordenes = []
    if row:
        if isinstance(row.get('ordenes'), str):
            try:
                row['ordenes'] = json.loads(row['ordenes'])
            except Exception:
                row['ordenes'] = []
        reporte_ids = []
        if isinstance(row.get('reporte_ids'), str):
            try:
                reporte_ids = json.loads(row['reporte_ids'])
            except Exception:
                reporte_ids = []
        row['reporte_ids'] = reporte_ids
        if reporte_ids:
            placeholders = ','.join(['%s'] * len(reporte_ids))
            cursor.execute(f"SELECT id, folio, tipo_servicio, nombre_cliente, total, plataforma, usuario, imei FROM reportes_servicio WHERE id IN ({placeholders})", tuple(reporte_ids))
            detalle_ordenes = cursor.fetchall()
            for d in detalle_ordenes:
                if d.get('total') is not None:
                    d['total'] = float(d['total'])
        row['detalle_ordenes'] = detalle_ordenes
        if row.get('fecha') and hasattr(row['fecha'], 'isoformat'):
            row['fecha'] = row['fecha'].isoformat()
        # Parsear comprobantes JSON
        if isinstance(row.get('comprobantes'), str):
            try:
                row['comprobantes'] = json.loads(row['comprobantes'])
            except Exception:
                row['comprobantes'] = []
        if row.get('comprobantes') is None:
            row['comprobantes'] = []
    cursor.close()
    db.close()
    if not row:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    return row

@app.post("/facturas-pago")
def crear_factura_pago(data: FacturaPagoCreate):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor()
    cursor.execute(
        """INSERT INTO facturas_pago (ordenes, cliente, total, status, reporte_ids, fecha)
           VALUES (%s, %s, %s, %s, %s, NOW())""",
        (
            json.dumps(data.ordenes),
            data.cliente,
            data.total,
            data.status,
            json.dumps(data.reporte_ids)
        )
    )
    db.commit()
    new_id = cursor.lastrowid
    cursor.close()
    db.close()
    return {"message": "Factura creada exitosamente", "id": new_id}


class TimbrarFacturaPagoRequest(BaseModel):
    rfc_cliente: str
    uso_cfdi: str
    forma_pago: str
    metodo_pago: str
    domicilio_fiscal_receptor: Optional[str] = None
    regimen_fiscal_receptor: Optional[str] = None


@app.post("/facturas-pago/{factura_id}/timbrar")
def timbrar_factura_pago(factura_id: int, data: TimbrarFacturaPagoRequest):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor(dictionary=True)
    for _col_sql in (
        "ALTER TABLE facturas_pago ADD COLUMN rfc_cliente VARCHAR(20) NULL",
        "ALTER TABLE facturas_pago ADD COLUMN uso_cfdi VARCHAR(5) NULL",
        "ALTER TABLE facturas_pago ADD COLUMN forma_pago VARCHAR(5) NULL",
        "ALTER TABLE facturas_pago ADD COLUMN metodo_pago VARCHAR(5) NULL",
        "ALTER TABLE facturas_pago ADD COLUMN cfdi_uuid VARCHAR(36) NULL",
        "ALTER TABLE facturas_pago ADD COLUMN cfdi_xml_path VARCHAR(255) NULL",
        "ALTER TABLE facturas_pago ADD COLUMN cfdi_pdf_path VARCHAR(255) NULL",
    ):
        try:
            cursor.execute(_col_sql)
        except Exception:
            pass

    cursor.execute("SELECT * FROM facturas_pago WHERE id=%s", (factura_id,))
    factura = cursor.fetchone()
    if not factura:
        cursor.close()
        db.close()
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    if factura.get('status') == 'Timbrado':
        cursor.close()
        db.close()
        raise HTTPException(status_code=400, detail="La factura ya está timbrada")

    reporte_ids = factura.get('reporte_ids')
    if isinstance(reporte_ids, str):
        try:
            reporte_ids = json.loads(reporte_ids)
        except Exception:
            reporte_ids = []
    reporte_ids = reporte_ids or []
    if not reporte_ids:
        cursor.close()
        db.close()
        raise HTTPException(status_code=400, detail="La factura no tiene reportes de servicio asociados")

    placeholders = ','.join(['%s'] * len(reporte_ids))
    cursor.execute(f"SELECT id, tipo_servicio, total, folio FROM reportes_servicio WHERE id IN ({placeholders})", tuple(reporte_ids))
    reportes = cursor.fetchall()
    cursor.close()
    db.close()

    if not reportes:
        raise HTTPException(status_code=400, detail="No se encontraron los reportes de servicio asociados a esta factura")

    productos = [
        Producto(
            ClaveProdServ="81112100",
            ClaveUnidad="E48",
            Unidad="Servicio",
            Descripcion=r.get('tipo_servicio') or f"Servicio {r.get('folio') or r['id']}",
            ValorUnitario=float(r.get('total') or 0),
            Importe=float(r.get('total') or 0),
            Cantidad=1
        ) for r in reportes
    ]

    resultado = _construir_y_timbrar_cfdi(
        nombre_cliente=factura['cliente'],
        rfc_cliente=data.rfc_cliente,
        uso_cfdi=data.uso_cfdi,
        metodo_pago=data.metodo_pago,
        forma_pago=data.forma_pago,
        productos=productos,
        serie="F",
        folio=str(factura_id),
        domicilio_fiscal_receptor=data.domicilio_fiscal_receptor,
        regimen_fiscal_receptor=data.regimen_fiscal_receptor,
    )

    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor()
    cursor.execute(
        """UPDATE facturas_pago
           SET status='Timbrado', rfc_cliente=%s, uso_cfdi=%s, forma_pago=%s, metodo_pago=%s,
               cfdi_uuid=%s, cfdi_xml_path=%s, cfdi_pdf_path=%s
           WHERE id=%s""",
        (data.rfc_cliente, data.uso_cfdi, data.forma_pago, data.metodo_pago,
         resultado['uuid'], resultado['xml_path'], resultado['pdf_path'], factura_id)
    )
    db.commit()
    cursor.close()
    db.close()

    return {
        "message": "Factura timbrada correctamente",
        "id": factura_id,
        "status": "Timbrado",
        "uuid": resultado['uuid'],
        "xml_url": build_public_url(resultado['xml_path']),
        "pdf_url": build_public_url(resultado['pdf_path'])
    }


@app.put("/facturas-pago/{factura_id}/status")
def actualizar_status_factura_pago(factura_id: int, data: dict = Body(...)):
    new_status = data.get('status', '').strip()
    if new_status not in ('Pendiente timbre', 'Cancelado'):
        raise HTTPException(status_code=400, detail="Status inválido. Usa POST /facturas-pago/{id}/timbrar para timbrar. Valores manuales: Pendiente timbre, Cancelado")
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor()
    if new_status == 'Cancelado':
        cursor.execute("UPDATE facturas_pago SET status=%s, reporte_ids=%s WHERE id=%s", (new_status, json.dumps([]), factura_id))
    else:
        cursor.execute("UPDATE facturas_pago SET status=%s WHERE id=%s", (new_status, factura_id))
    db.commit()
    affected = cursor.rowcount
    cursor.close()
    db.close()
    if affected == 0:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    return {"message": "Status actualizado", "id": factura_id, "status": new_status}

@app.put("/facturas-pago/{factura_id}/lugar-pago")
def actualizar_lugar_pago_factura(factura_id: int, data: dict = Body(...)):
    lugar_pago = data.get('lugar_pago', '').strip()
    lugares_validos = ['ASP Vianey', 'ASP Renovaciones', 'Comercializadora', 'BBVA PAU', 'Tecnico', 'Oficina', 'Mercadopago']
    if lugar_pago and lugar_pago not in lugares_validos:
        raise HTTPException(status_code=400, detail=f"Lugar de pago inválido. Valores: {', '.join(lugares_validos)}")
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor()
    cursor.execute("UPDATE facturas_pago SET lugar_pago=%s WHERE id=%s", (lugar_pago if lugar_pago else None, factura_id))
    db.commit()
    affected = cursor.rowcount
    cursor.close()
    db.close()
    if affected == 0:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    return {"message": "Lugar de pago actualizado", "id": factura_id, "lugar_pago": lugar_pago or None}

@app.put("/facturas-pago/{factura_id}/observaciones")
def actualizar_observaciones_factura(factura_id: int, data: dict = Body(...)):
    observaciones = data.get('observaciones', '')
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor()
    cursor.execute("UPDATE facturas_pago SET observaciones=%s WHERE id=%s", (observaciones or None, factura_id))
    db.commit()
    affected = cursor.rowcount
    cursor.close()
    db.close()
    if affected == 0:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    return {"message": "Observaciones actualizadas", "id": factura_id}

@app.delete("/facturas-pago/{factura_id}")
def eliminar_factura_pago(factura_id: int):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor()
    cursor.execute("DELETE FROM facturas_pago WHERE id=%s", (factura_id,))
    db.commit()
    affected = cursor.rowcount
    cursor.close()
    db.close()
    if affected == 0:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    return {"message": "Factura eliminada"}

@app.post("/facturas-pago/{factura_id}/comprobante")
def subir_comprobante_factura(factura_id: int, archivo: UploadFile = File(...)):
    import shutil
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, comprobantes FROM facturas_pago WHERE id=%s", (factura_id,))
    row = cursor.fetchone()
    if not row:
        cursor.close()
        db.close()
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    existentes = []
    if row.get('comprobantes'):
        try:
            existentes = json.loads(row['comprobantes']) if isinstance(row['comprobantes'], str) else row['comprobantes']
        except Exception:
            existentes = []
    base_dir = os.path.join("uploads", "pagos", "facturas", str(factura_id))
    os.makedirs(base_dir, exist_ok=True)
    filename = archivo.filename or "comprobante"
    filename = ''.join(c for c in filename if c.isalnum() or c in ('-', '_', '.', ' ')).strip()
    dest_path = os.path.join(base_dir, filename)
    base_name, ext = os.path.splitext(filename)
    counter = 1
    while os.path.exists(dest_path):
        dest_path = os.path.join(base_dir, f"{base_name}_{counter}{ext}")
        counter += 1
    with open(dest_path, "wb") as out:
        shutil.copyfileobj(archivo.file, out)
    rel_path = dest_path.replace("\\", "/")
    existentes.append(rel_path)
    cursor2 = db.cursor()
    cursor2.execute("UPDATE facturas_pago SET comprobantes=%s WHERE id=%s", (json.dumps(existentes), factura_id))
    db.commit()
    cursor2.close()
    cursor.close()
    db.close()
    return {"message": "Comprobante subido", "path": rel_path, "comprobantes": existentes}

@app.delete("/facturas-pago/{factura_id}/comprobante")
def eliminar_comprobante_factura(factura_id: int, data: dict = Body(...)):
    path = data.get('path', '').strip()
    if not path:
        raise HTTPException(status_code=400, detail="Se requiere 'path' del comprobante a eliminar")
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, comprobantes FROM facturas_pago WHERE id=%s", (factura_id,))
    row = cursor.fetchone()
    if not row:
        cursor.close()
        db.close()
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    existentes = []
    if row.get('comprobantes'):
        try:
            existentes = json.loads(row['comprobantes']) if isinstance(row['comprobantes'], str) else row['comprobantes']
        except Exception:
            existentes = []
    if path not in existentes:
        cursor.close()
        db.close()
        raise HTTPException(status_code=404, detail="Comprobante no encontrado en la lista")
    existentes.remove(path)
    if os.path.exists(path):
        os.remove(path)
    cursor2 = db.cursor()
    cursor2.execute("UPDATE facturas_pago SET comprobantes=%s WHERE id=%s", (json.dumps(existentes), factura_id))
    db.commit()
    cursor2.close()
    cursor.close()
    db.close()
    return {"message": "Comprobante eliminado", "comprobantes": existentes}

@app.put("/facturas-pago/{factura_id}/agregar-reportes")
def agregar_reportes_factura(factura_id: int, data: dict = Body(...)):
    nuevos_ids = data.get('reporte_ids', [])
    if not nuevos_ids:
        raise HTTPException(status_code=400, detail="Se requiere 'reporte_ids'")
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, reporte_ids, status FROM facturas_pago WHERE id=%s", (factura_id,))
    factura = cursor.fetchone()
    if not factura:
        cursor.close(); db.close()
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    if factura.get('status') in ('pagado', 'Timbrado', 'Cancelado'):
        cursor.close(); db.close()
        raise HTTPException(status_code=400, detail="No se puede modificar una factura en ese estado")
    existing_ids = []
    if factura.get('reporte_ids'):
        try:
            existing_ids = json.loads(factura['reporte_ids']) if isinstance(factura['reporte_ids'], str) else factura['reporte_ids']
        except Exception:
            existing_ids = []
    combined_ids = list(dict.fromkeys(existing_ids + nuevos_ids))
    new_ordenes = []
    new_total = 0.0
    if combined_ids:
        placeholders = ','.join(['%s'] * len(combined_ids))
        cursor.execute(f"SELECT id, folio, total FROM reportes_servicio WHERE id IN ({placeholders})", tuple(combined_ids))
        reportes = cursor.fetchall()
        new_ordenes = [r['folio'] for r in reportes if r.get('folio')]
        new_total = sum(float(r['total'] or 0) for r in reportes)
    cursor2 = db.cursor()
    cursor2.execute(
        "UPDATE facturas_pago SET reporte_ids=%s, ordenes=%s, total=%s WHERE id=%s",
        (json.dumps(combined_ids), json.dumps(new_ordenes), new_total, factura_id)
    )
    db.commit()
    cursor2.close(); cursor.close(); db.close()
    return {"message": "Reportes agregados", "id": factura_id, "reporte_ids": combined_ids}

@app.put("/facturas-pago/{factura_id}/quitar-reportes")
def quitar_reportes_factura(factura_id: int, data: dict = Body(...)):
    ids_a_quitar = data.get('reporte_ids', [])
    if not ids_a_quitar:
        raise HTTPException(status_code=400, detail="Se requiere 'reporte_ids'")
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, reporte_ids, status FROM facturas_pago WHERE id=%s", (factura_id,))
    factura = cursor.fetchone()
    if not factura:
        cursor.close(); db.close()
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    if factura.get('status') in ('pagado', 'Timbrado', 'Cancelado'):
        cursor.close(); db.close()
        raise HTTPException(status_code=400, detail="No se puede modificar una factura en ese estado")
    existing_ids = []
    if factura.get('reporte_ids'):
        try:
            existing_ids = json.loads(factura['reporte_ids']) if isinstance(factura['reporte_ids'], str) else factura['reporte_ids']
        except Exception:
            existing_ids = []
    quitar_set = set(ids_a_quitar)
    combined_ids = [rid for rid in existing_ids if rid not in quitar_set]
    new_ordenes = []
    new_total = 0.0
    if combined_ids:
        placeholders = ','.join(['%s'] * len(combined_ids))
        cursor.execute(f"SELECT id, folio, total FROM reportes_servicio WHERE id IN ({placeholders})", tuple(combined_ids))
        reportes = cursor.fetchall()
        new_ordenes = [r['folio'] for r in reportes if r.get('folio')]
        new_total = sum(float(r['total'] or 0) for r in reportes)
    cursor2 = db.cursor()
    cursor2.execute(
        "UPDATE facturas_pago SET reporte_ids=%s, ordenes=%s, total=%s WHERE id=%s",
        (json.dumps(combined_ids), json.dumps(new_ordenes), new_total, factura_id)
    )
    db.commit()
    cursor2.close(); cursor.close(); db.close()
    return {"message": "Reportes quitados", "id": factura_id, "reporte_ids": combined_ids}


# ═══════════════════════════════════════════════════════════════════════
# ══════════════════════════ RETIROS DE BANCO ═════════════════════════
# ═══════════════════════════════════════════════════════════════════════

@app.get("/retiros-banco")
def get_retiros_banco(banco: str = None, request: Request = None):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor(dictionary=True)
    if banco:
        cursor.execute("SELECT * FROM retiros_banco WHERE banco=%s ORDER BY id DESC", (banco,))
    else:
        cursor.execute("SELECT * FROM retiros_banco ORDER BY id DESC")
    rows = cursor.fetchall()
    for r in rows:
        for campo in ("creado_fecha", "aprobado_fecha"):
            if r.get(campo) and hasattr(r[campo], "isoformat"):
                r[campo] = r[campo].isoformat()
        r["comprobante_url"] = build_public_url(r.get("comprobante_path"), request)
        if r.get("monto") is not None:
            r["monto"] = float(r["monto"])
    cursor.close()
    db.close()
    return rows

@app.post("/retiros-banco")
def crear_retiro_banco(
    banco: str = Form(...),
    monto: float = Form(...),
    motivo: str = Form(None),
    archivo: UploadFile = File(...),
    current=Depends(get_current_user),
    request: Request = None
):
    import shutil
    if monto <= 0:
        raise HTTPException(status_code=400, detail="El monto debe ser mayor a 0")

    safe_banco = ''.join(c for c in banco if c.isalnum() or c in ('-', '_', ' ')).strip() or "SinBanco"
    base_dir = os.path.join("uploads", "retiros", safe_banco)
    os.makedirs(base_dir, exist_ok=True)
    filename = archivo.filename or "comprobante"
    filename = ''.join(c for c in filename if c.isalnum() or c in ('-', '_', '.', ' ')).strip()
    dest_path = os.path.join(base_dir, filename)
    base_name, ext = os.path.splitext(filename)
    counter = 1
    while os.path.exists(dest_path):
        dest_path = os.path.join(base_dir, f"{base_name}_{counter}{ext}")
        counter += 1
    with open(dest_path, "wb") as out:
        shutil.copyfileobj(archivo.file, out)
    rel_path = dest_path.replace("\\", "/")

    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor()
    cursor.execute(
        """INSERT INTO retiros_banco (banco, monto, motivo, comprobante_path, estatus, creado_por, creado_fecha)
           VALUES (%s, %s, %s, %s, 'pendiente', %s, NOW())""",
        (banco, monto, motivo or None, rel_path, current.get("username"))
    )
    db.commit()
    new_id = cursor.lastrowid
    cursor.close()
    db.close()
    return {
        "message": "Retiro registrado",
        "id": new_id,
        "comprobante_path": rel_path,
        "comprobante_url": build_public_url(rel_path, request),
        "estatus": "pendiente"
    }

@app.put("/retiros-banco/{retiro_id}/aprobar")
def aprobar_retiro_banco(retiro_id: int, current=Depends(get_current_user)):
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
        cursor.close(); db.close()
        raise HTTPException(status_code=403, detail="No autorizado")

    cursor.execute("SELECT id, estatus FROM retiros_banco WHERE id=%s", (retiro_id,))
    retiro = cursor.fetchone()
    if not retiro:
        cursor.close(); db.close()
        raise HTTPException(status_code=404, detail="Retiro no encontrado")

    cursor2 = db.cursor()
    cursor2.execute(
        "UPDATE retiros_banco SET estatus='aprobado', aprobado_por=%s, aprobado_fecha=NOW() WHERE id=%s",
        (user.get("username"), retiro_id)
    )
    db.commit()
    cursor2.close(); cursor.close(); db.close()
    return {"message": "Retiro aprobado"}

@app.put("/retiros-banco/{retiro_id}/rechazar")
def rechazar_retiro_banco(retiro_id: int, current=Depends(get_current_user)):
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
        cursor.close(); db.close()
        raise HTTPException(status_code=403, detail="No autorizado")

    cursor.execute("SELECT id FROM retiros_banco WHERE id=%s", (retiro_id,))
    if not cursor.fetchone():
        cursor.close(); db.close()
        raise HTTPException(status_code=404, detail="Retiro no encontrado")

    cursor2 = db.cursor()
    cursor2.execute(
        "UPDATE retiros_banco SET estatus='rechazado', aprobado_por=%s, aprobado_fecha=NOW() WHERE id=%s",
        (user.get("username"), retiro_id)
    )
    db.commit()
    cursor2.close(); cursor.close(); db.close()
    return {"message": "Retiro rechazado"}

@app.delete("/retiros-banco/{retiro_id}")
def eliminar_retiro_banco(retiro_id: int):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, estatus, comprobante_path FROM retiros_banco WHERE id=%s", (retiro_id,))
    retiro = cursor.fetchone()
    if not retiro:
        cursor.close(); db.close()
        raise HTTPException(status_code=404, detail="Retiro no encontrado")
    if retiro.get("estatus") != "pendiente":
        cursor.close(); db.close()
        raise HTTPException(status_code=400, detail="Solo se puede eliminar un retiro pendiente")

    cursor2 = db.cursor()
    cursor2.execute("DELETE FROM retiros_banco WHERE id=%s", (retiro_id,))
    db.commit()
    cursor2.close(); cursor.close(); db.close()

    path = retiro.get("comprobante_path")
    if path and os.path.exists(path):
        os.remove(path)
    return {"message": "Retiro eliminado"}


# ═══════════════════════════════════════════════════════════════════════
# ══════════════ PLATAFORMAS IOP / TRACKSOLID ═════════════════════════
# ═══════════════════════════════════════════════════════════════════════

import hashlib
import time as _time
import requests as _requests
import threading as _threading

# ---------- IOP GPS Client ----------
class IOPGPSClient:
    TOKEN_MARGIN_SECONDS = 300

    def __init__(self):
        self.appid = os.getenv("IOPGPS_APPID", "")
        self.secret_key = os.getenv("IOPGPS_SECRET_KEY", "")
        self.base_url = os.getenv("IOPGPS_BASE_URL", "https://open.iopgps.com")
        self._access_token = None
        self._token_expires_at = 0

    def _md5(self, text: str) -> str:
        return hashlib.md5(text.encode()).hexdigest().lower()

    def _is_token_valid(self) -> bool:
        return (
            self._access_token is not None
            and _time.time() < (self._token_expires_at - self.TOKEN_MARGIN_SECONDS)
        )

    def authenticate(self):
        timestamp = int(_time.time())
        signature = self._md5(self._md5(self.secret_key) + str(timestamp))
        resp = _requests.post(
            f"{self.base_url}/api/auth",
            json={"appid": self.appid, "time": timestamp, "signature": signature},
            headers={"Content-Type": "application/json"},
            timeout=15,
        )
        data = resp.json()
        if data.get("code") != 0:
            raise Exception(f"IOP auth error: {data.get('result')}")
        self._access_token = data["accessToken"]
        self._token_expires_at = _time.time() + data.get("expiresIn", 7200000) / 1000

    def _get_token(self) -> str:
        if not self._is_token_valid():
            self.authenticate()
        return self._access_token

    def _headers(self):
        return {"accessToken": self._get_token(), "Content-Type": "application/json"}

    # --- Endpoints directos (eficientes) ---

    def get_device_detail(self, imei_val: str):
        """GET /api/device/detail?imei=XXX - Consulta directa por IMEI."""
        resp = _requests.get(
            f"{self.base_url}/api/device/detail",
            params={"imei": imei_val},
            headers=self._headers(), timeout=15,
        )
        return resp.json()

    def get_device_detail_page(self, imeis: list = None, license_numbers: list = None, vins: list = None, account_id: str = None):
        """POST /api/device/detail/page - Búsqueda batch por IMEI, placa, VIN o cuenta."""
        body = {"pageSize": "100", "currentPage": "1"}
        if account_id:
            body["accountId"] = account_id
        elif imeis:
            body["imei"] = imeis
        elif license_numbers:
            body["licenseNumber"] = license_numbers
        elif vins:
            body["vin"] = vins
        resp = _requests.post(
            f"{self.base_url}/api/device/detail/page",
            json=body,
            headers=self._headers(), timeout=15,
        )
        return resp.json()

    def get_vehicle_status(self, content: str):
        """GET /api/vehicle/status?content=XXX - Busca dispositivo por contenido (IMEI, placa, etc.)."""
        resp = _requests.get(
            f"{self.base_url}/api/vehicle/status",
            params={"content": content},
            headers=self._headers(), timeout=15,
        )
        return resp.json()

    def get_device_info(self, imei_val: str = None, account: str = None):
        """GET /api/device/info - Detalle del dispositivo por IMEI o cuenta."""
        params = {}
        if imei_val:
            params["imei"] = imei_val
        if account:
            params["account"] = account
        resp = _requests.get(
            f"{self.base_url}/api/device/info",
            params=params,
            headers=self._headers(), timeout=15,
        )
        return resp.json()

    def search_devices(self, query: str):
        """
        Búsqueda inteligente: intenta primero endpoints directos.
        1. Si parece IMEI (solo dígitos, >=10 chars) → device/detail/page por IMEI
        2. Si no → vehicle/status por contenido (busca IMEI, placa, nombre)
        3. Fallback → device/info por cuenta
        Retorna siempre una lista de resultados raw.
        """
        results = []

        # Estrategia 1: Si parece IMEI, buscar directo
        q_stripped = query.strip()
        if q_stripped.isdigit() and len(q_stripped) >= 6:
            detail = self.get_device_detail(q_stripped)
            if detail.get("code") == 0 and detail.get("data"):
                data = detail["data"]
                if isinstance(data, dict):
                    results = [data]
                elif isinstance(data, list):
                    results = data
                if results:
                    return results

            # Intentar batch search
            page_resp = self.get_device_detail_page(imeis=[q_stripped])
            if page_resp.get("code") == 0:
                data = page_resp.get("data", {})
                items = data.get("list", data.get("data", []))  # estructura puede variar
                if isinstance(items, list) and items:
                    return items

        # Estrategia 2: Buscar por vehicle/status (acepta contenido libre)
        vs_resp = self.get_vehicle_status(query)
        if vs_resp.get("code") == 0 and vs_resp.get("data"):
            data = vs_resp["data"]
            if isinstance(data, list) and data:
                return data

        # Estrategia 3: Buscar por device/info como cuenta
        info_resp = self.get_device_info(account=query)
        if info_resp.get("code") == 0 and info_resp.get("data"):
            data = info_resp["data"]
            if isinstance(data, list) and data:
                return data
            elif isinstance(data, dict):
                return [data]

        return results


# ---------- TrackSolid Client ----------
# Usando EXACTAMENTE la misma lógica de generate_sign y get_current_date
# que ya funciona en el script original del usuario.
import pytz as _pytz

def _tracksolid_current_date():
    """Exacto de utils.py original."""
    formatter = "%Y-%m-%d %H:%M:%S"
    utc_now = datetime.now(_pytz.utc)
    return utc_now.strftime(formatter)

def _tracksolid_generate_sign(params, app_secret):
    """Exacto de utils.py original."""
    sorted_params = ''.join(f"{k}{v}" for k, v in sorted(params.items()))
    sign_str = f"{app_secret}{sorted_params}{app_secret}"
    return hashlib.md5(sign_str.encode('utf-8')).hexdigest().upper()


class TrackSolidClient:
    def __init__(self):
        self.openapi_url = os.getenv("TRACKSOLID_OPENAPI_URL", "").strip()
        self.app_key = os.getenv("TRACKSOLID_APP_KEY", "").strip()
        self.app_secret = os.getenv("TRACKSOLID_APP_SECRET", "").strip()
        self.account = os.getenv("TRACKSOLID_ACCOUNT", "").strip()
        self.password_md5 = os.getenv("TRACKSOLID_PASSWORD_MD5", "").strip()
        self._access_token = None
        self._refresh_token = None
        self._token_expires_in = 60
        self._token_time = None
        self._token_lock = _threading.Lock()
        self._last_api_call = 0.0
        self._min_api_interval = 1.5  # mínimo 1.5s entre llamadas a JIMI
        self._child_list_cache = None
        self._child_list_cache_time = None
        self._child_list_cache_ttl = 300  # 5 min cache para child_list
        self._device_list_cache = {}     # {account: {"resp": ..., "time": ...}}
        self._device_list_cache_ttl = 180  # 3 min cache para device_list por cuenta
        self._search_cache = {}           # {query: {"result": [...], "time": ...}}
        self._search_cache_ttl = 120      # 2 min cache para resultados de búsqueda

    def _send_post(self, params):
        try:
            resp = _requests.post(
                self.openapi_url,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data=params,
                timeout=15,
            )
            return resp.json()
        except _requests.exceptions.Timeout:
            raise Exception(f"Timeout conectando a Tracksolid API: {self.openapi_url}")
        except _requests.exceptions.ConnectionError as ce:
            raise Exception(f"No se pudo conectar a Tracksolid API ({self.openapi_url}): {ce}")
        except Exception as e:
            raise Exception(f"Error en llamada a Tracksolid API: {type(e).__name__}: {e}")

    def _has_token(self):
        """Retorna True si tenemos un access_token (sin importar si creemos que expiró)."""
        return self._access_token is not None

    def _is_token_expired(self):
        if not self._token_time:
            return True
        return (_time.time() - self._token_time) >= (self._token_expires_in - 10)

    def _ensure_valid_token(self):
        """Solo obtiene token si no tenemos uno. NO re-autentica proactivamente."""
        with self._token_lock:
            if not self._has_token():
                self._get_access_token()

    def _get_access_token(self):
        self._throttle()
        param_map = {
            "app_key": self.app_key,
            "v": "1.0",
            "timestamp": _tracksolid_current_date(),
            "sign_method": "md5",
            "format": "json",
            "method": "jimi.oauth.token.get",
            "user_id": self.account,
            "user_pwd_md5": self.password_md5,
            "expires_in": "7200",
        }
        sign = _tracksolid_generate_sign(param_map, self.app_secret)
        param_map["sign"] = sign
        resp = self._send_post(param_map)
        if resp.get("code") == 0:
            self._update_token(resp["result"])
        else:
            raise Exception(f"TrackSolid auth error: {resp.get('message')} (code: {resp.get('code')})")

    def _refresh_access_token(self):
        self._throttle()
        param_map = {
            "app_key": self.app_key,
            "v": "1.0",
            "timestamp": _tracksolid_current_date(),
            "sign_method": "md5",
            "format": "json",
            "method": "jimi.oauth.token.refresh",
            "access_token": self._access_token,
            "refresh_token": self._refresh_token,
            "expires_in": "7200",
        }
        sign = _tracksolid_generate_sign(param_map, self.app_secret)
        param_map["sign"] = sign
        resp = self._send_post(param_map)
        if resp.get("code") == 0:
            self._update_token(resp["result"])
        else:
            # Refresh falló: limpiar y hacer auth completa
            self._refresh_token = None
            self._get_access_token()

    def _update_token(self, result):
        self._access_token = result["accessToken"]
        self._refresh_token = result.get("refreshToken", self._refresh_token)
        expires_raw = result.get("expiresIn", 7200)
        expires_val = int(expires_raw)
        # Si viene en milisegundos (>100000), convertir a segundos
        if expires_val > 100000:
            expires_val = expires_val // 1000
        self._token_expires_in = expires_val
        self._token_time = _time.time()

    def _force_full_reauth(self):
        """Limpia tokens y fuerza autenticación completa desde cero."""
        with self._token_lock:
            self._access_token = None
            self._refresh_token = None
            self._token_time = None
            self._get_access_token()

    def _throttle(self):
        """Espera lo necesario para respetar el intervalo mínimo entre llamadas."""
        now = _time.time()
        elapsed = now - self._last_api_call
        if elapsed < self._min_api_interval:
            _time.sleep(self._min_api_interval - elapsed)
        self._last_api_call = _time.time()

    def _api_call(self, build_params_fn):
        self._ensure_valid_token()
        self._throttle()
        resp = build_params_fn()
        code = resp.get("code")
        # Token inválido/expirado: refrescar y reintentar UNA vez
        if code == 1004:
            with self._token_lock:
                if self._refresh_token:
                    try:
                        self._refresh_access_token()
                    except Exception:
                        self._access_token = None
                        self._refresh_token = None
                        self._token_time = None
                        self._get_access_token()
                else:
                    self._access_token = None
                    self._token_time = None
                    self._get_access_token()
            self._throttle()
            resp = build_params_fn()
        # Rate limit: esperar con backoff, reintentar SIN re-autenticar
        elif code == 1006:
            for attempt in range(3):
                wait = 3 * (attempt + 1)  # 3s, 6s, 9s
                _time.sleep(wait)
                self._throttle()
                resp = build_params_fn()
                if resp.get("code") != 1006:
                    break
        return resp

    def fetch_child_list(self, use_cache=True):
        # Retornar caché si está vigente
        if use_cache and self._child_list_cache is not None and self._child_list_cache_time:
            age = _time.time() - self._child_list_cache_time
            if age < self._child_list_cache_ttl:
                return self._child_list_cache

        def _do():
            params = {
                "app_key": self.app_key, "v": "1.0",
                "timestamp": _tracksolid_current_date(), "sign_method": "md5",
                "format": "json", "method": "jimi.user.child.list",
                "access_token": self._access_token, "target": self.account,
            }
            params["sign"] = _tracksolid_generate_sign(params, self.app_secret)
            return self._send_post(params)
        resp = self._api_call(_do)
        if resp.get("code") == 0:
            self._child_list_cache = resp
            self._child_list_cache_time = _time.time()
        return resp

    def fetch_device_list(self, target_account):
        # Cache por cuenta
        cached = self._device_list_cache.get(target_account)
        if cached and (_time.time() - cached["time"]) < self._device_list_cache_ttl:
            return cached["resp"]

        def _do():
            params = {
                "app_key": self.app_key, "v": "1.0",
                "timestamp": _tracksolid_current_date(), "sign_method": "md5",
                "format": "json", "method": "jimi.user.device.list",
                "access_token": self._access_token, "target": target_account,
            }
            params["sign"] = _tracksolid_generate_sign(params, self.app_secret)
            return self._send_post(params)
        resp = self._api_call(_do)
        if resp.get("code") == 0:
            self._device_list_cache[target_account] = {"resp": resp, "time": _time.time()}
        return resp

    def fetch_device_detail(self, imei_val):
        def _do():
            params = {
                "app_key": self.app_key, "v": "1.0",
                "timestamp": _tracksolid_current_date(), "sign_method": "md5",
                "format": "json", "method": "jimi.track.device.detail",
                "access_token": self._access_token, "imei": imei_val,
            }
            params["sign"] = _tracksolid_generate_sign(params, self.app_secret)
            return self._send_post(params)
        return self._api_call(_do)

    # --- Caché de dispositivos ---
    _device_cache = {}     # {imei: {device_info + _account + _accountName}}
    _cache_building = False
    _cache_built_at = None

    def build_device_cache(self):
        """Itera TODAS las sub-cuentas y construye un índice IMEI → device."""
        if self._cache_building:
            return {"status": "already_building"}
        TrackSolidClient._cache_building = True
        try:
            self._ensure_valid_token()
            child_resp = self.fetch_child_list()
            if child_resp.get("code") != 0:
                return {"status": "error", "message": f"child_list failed: {child_resp.get('message')}"}
            sub_accounts = child_resp.get("result", [])
            cache = {}
            errores = 0
            for i, sub in enumerate(sub_accounts):
                acc = sub.get("account", "")
                name = sub.get("name", acc)
                try:
                    dev_resp = self.fetch_device_list(acc)
                    if dev_resp.get("code") != 0:
                        errores += 1
                        continue
                    devices = dev_resp.get("result", [])
                    if not isinstance(devices, list):
                        continue
                    for dev in devices:
                        imei = str(dev.get("imei", ""))
                        if imei:
                            dev["_account"] = acc
                            dev["_accountName"] = name
                            cache[imei] = dev
                except Exception:
                    errores += 1
                # Rate limit: pausa cada 3 cuentas
                if i % 3 == 2:
                    _time.sleep(1.0)
            TrackSolidClient._device_cache = cache
            TrackSolidClient._cache_built_at = _time.time()
            return {"status": "ok", "total_devices": len(cache), "total_accounts": len(sub_accounts), "errores": errores}
        finally:
            TrackSolidClient._cache_building = False

    def search_devices(self, query: str):
        """
        Búsqueda en Tracksolid:
        1. Cache de búsquedas recientes (instantáneo)
        2. Si hay caché de dispositivos, buscar ahí (instantáneo)
        3. Sin caché: buscar por cuenta en child_list, luego listar dispositivos
        """
        q_stripped = query.strip()
        q = query.lower().strip()

        # 0. Cache de búsquedas recientes
        cached_search = self._search_cache.get(q)
        if cached_search and (_time.time() - cached_search["time"]) < self._search_cache_ttl:
            return cached_search["result"]

        results = []

        # 1. Si hay caché global de dispositivos, buscar ahí
        if self._device_cache:
            # Match exacto por IMEI
            if q_stripped in self._device_cache:
                return [self._device_cache[q_stripped]]
            # Match parcial
            for imei, dev in self._device_cache.items():
                dev_name = str(dev.get("deviceName", "")).lower()
                acc = str(dev.get("_account", "")).lower()
                acc_name = str(dev.get("_accountName", "")).lower()
                if q in imei or q in dev_name or q in acc or q in acc_name:
                    results.append(dev)
                    if len(results) >= 20:
                        break
            self._search_cache[q] = {"result": results, "time": _time.time()}
            return results

        # 2. Sin caché: buscar por cuenta en child_list
        child_resp = self.fetch_child_list()
        if child_resp.get("code") != 0:
            return results
        sub_accounts = child_resp.get("result", [])

        # Filtrar sub-cuentas cuyo nombre/account coincida con la búsqueda
        matched = [
            sub for sub in sub_accounts
            if q in sub.get("account", "").lower() or q in sub.get("name", "").lower()
        ]
        # Si no matcheó por nombre pero es dígito, probar las primeras 10
        if not matched and q_stripped.isdigit():
            matched = sub_accounts[:10]

        for i, sub in enumerate(matched[:5]):
            acc_name = sub.get("account", "")
            acc_display = sub.get("name", acc_name)
            dev_resp = self.fetch_device_list(acc_name)
            if dev_resp.get("code") == 1006:
                break  # Rate limited, dejar de iterar
            if dev_resp.get("code") != 0:
                continue
            devices = dev_resp.get("result", [])
            if not isinstance(devices, list):
                continue
            for dev in devices:
                dev_imei = str(dev.get("imei", ""))
                dev_name = str(dev.get("deviceName", "")).lower()
                if q in dev_imei or q in dev_name or q in acc_name.lower() or q in acc_display.lower():
                    dev["_account"] = acc_name
                    dev["_accountName"] = acc_display
                    results.append(dev)
        self._search_cache[q] = {"result": results, "time": _time.time()}
        return results


# ---------- Singleton de TrackSolid para reusar token ----------
_tracksolid_client = None
def _get_tracksolid_client():
    global _tracksolid_client
    if _tracksolid_client is None:
        _tracksolid_client = TrackSolidClient()
    return _tracksolid_client

# ---------- Endpoints de búsqueda en plataformas ----------

@app.get("/api/plataformas/buscar")
def buscar_en_plataforma(q: str = Query(..., min_length=2), plataforma: str = Query(...)):
    """
    Busca dispositivos en IOP o Tracksolid.
    Retorna el response RAW de la API en un array para que el frontend
    pueda mostrarlos en un dropdown y el usuario seleccione.
    """
    plat = plataforma.lower().strip()
    try:
        if plat == "iop":
            if not os.getenv("IOPGPS_APPID"):
                raise HTTPException(status_code=400, detail="Credenciales IOP no configuradas en .env")
            client = IOPGPSClient()
            devices = client.search_devices(q)
            return {"plataforma": "iop", "total": len(devices), "resultados": devices}
        elif plat in ("tracksolid", "track"):
            if not os.getenv("TRACKSOLID_APP_KEY"):
                raise HTTPException(status_code=400, detail="Credenciales Tracksolid no configuradas en .env")
            client = _get_tracksolid_client()
            devices = client.search_devices(q)
            cache_info = {
                "cache_size": len(client._device_cache),
                "cache_built": client._cache_built_at is not None,
                "cache_building": client._cache_building,
            }
            return {"plataforma": "tracksolid", "total": len(devices), "resultados": devices, "_cache": cache_info}
        else:
            raise HTTPException(status_code=400, detail=f"Plataforma no soportada: {plataforma}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/plataformas/debug")
def debug_plataformas():
    """Endpoint temporal para diagnosticar credenciales."""
    import traceback as _tb
    ts_key = os.getenv("TRACKSOLID_APP_KEY", "").strip()
    ts_account = os.getenv("TRACKSOLID_ACCOUNT", "").strip()
    ts_url = os.getenv("TRACKSOLID_OPENAPI_URL", "").strip()
    ts_secret = os.getenv("TRACKSOLID_APP_SECRET", "").strip()
    ts_pwd = os.getenv("TRACKSOLID_PASSWORD_MD5", "").strip()
    iop_appid = os.getenv("IOPGPS_APPID", "").strip()
    iop_base = os.getenv("IOPGPS_BASE_URL", "").strip()

    result = {
        "env": {
            "tracksolid": {
                "url": ts_url,
                "app_key_len": len(ts_key),
                "app_key_first4": ts_key[:4] if ts_key else "(vacío)",
                "app_secret_len": len(ts_secret),
                "account": ts_account,
                "account_repr": repr(ts_account),
                "password_md5_len": len(ts_pwd),
                "password_md5_first6": ts_pwd[:6] if ts_pwd else "(vacío)",
            },
            "iop": {
                "appid": iop_appid,
                "base_url": iop_base,
            }
        },
    }

    # Intentar auth de Tracksolid con logging detallado
    if ts_key and ts_secret and ts_account and ts_pwd:
        try:
            ts = _tracksolid_current_date()
            param_map = {
                "app_key": ts_key,
                "v": "1.0",
                "timestamp": ts,
                "sign_method": "md5",
                "format": "json",
                "method": "jimi.oauth.token.get",
                "user_id": ts_account,
                "user_pwd_md5": ts_pwd,
                "expires_in": "7200",
            }
            sign = _tracksolid_generate_sign(param_map, ts_secret)
            param_map["sign"] = sign
            result["tracksolid_auth_request"] = {
                "url": ts_url,
                "timestamp_used": ts,
                "sign_generated": sign,
                "params_keys": list(param_map.keys()),
            }
            resp = _requests.post(
                ts_url,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data=param_map,
                timeout=15,
            )
            result["tracksolid_auth_response"] = resp.json()
        except Exception as e:
            result["tracksolid_auth_error"] = f"{type(e).__name__}: {e}\n{_tb.format_exc()}"

    return result


@app.post("/api/plataformas/tracksolid/rebuild-cache")
def rebuild_tracksolid_cache():
    """Construye el caché de dispositivos de TODAS las sub-cuentas de Tracksolid.
    Tarda varios minutos la primera vez (~3000 sub-cuentas)."""
    if not os.getenv("TRACKSOLID_APP_KEY"):
        raise HTTPException(status_code=400, detail="Credenciales Tracksolid no configuradas")
    client = _get_tracksolid_client()
    if client._cache_building:
        return {"status": "already_building", "cache_size": len(client._device_cache)}
    result = client.build_device_cache()
    return result


@app.get("/api/plataformas/tracksolid/cache-status")
def tracksolid_cache_status():
    """Muestra el estado del caché de Tracksolid."""
    client = _get_tracksolid_client()
    age = None
    if client._cache_built_at:
        age = int(_time.time() - client._cache_built_at)
    return {
        "cache_size": len(client._device_cache),
        "cache_building": client._cache_building,
        "cache_age_seconds": age,
    }


@app.get("/api/plataformas/dispositivo/{imei_val}")
def detalle_dispositivo_plataforma(imei_val: str, plataforma: str = Query(...)):
    """Obtiene el detalle completo de un dispositivo por IMEI (consulta directa)."""
    plat = plataforma.lower().strip()
    try:
        if plat == "iop":
            if not os.getenv("IOPGPS_APPID"):
                raise HTTPException(status_code=400, detail="Credenciales IOP no configuradas en .env")
            client = IOPGPSClient()
            # Consulta directa por IMEI
            detail = client.get_device_detail(imei_val)
            if detail.get("code") == 0 and detail.get("data"):
                return {"plataforma": "iop", "dispositivo": detail["data"]}
            # Fallback: device/info
            info = client.get_device_info(imei_val=imei_val)
            if info.get("code") == 0 and info.get("data"):
                data = info["data"]
                return {"plataforma": "iop", "dispositivo": data[0] if isinstance(data, list) else data}
            raise HTTPException(status_code=404, detail="Dispositivo no encontrado en IOP")
        elif plat in ("tracksolid", "track"):
            if not os.getenv("TRACKSOLID_APP_KEY"):
                raise HTTPException(status_code=400, detail="Credenciales Tracksolid no configuradas en .env")
            client = _get_tracksolid_client()
            detail = client.fetch_device_detail(imei_val)
            if detail.get("code") == 0 and detail.get("result"):
                return {"plataforma": "tracksolid", "dispositivo": detail["result"]}
            raise HTTPException(status_code=404, detail="Dispositivo no encontrado en Tracksolid")
        else:
            raise HTTPException(status_code=400, detail=f"Plataforma no soportada: {plataforma}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class UtilidadesConsultaRequest(BaseModel):
    imei: str
    plataforma: str


def _normalize_plataforma_utilidades(plataforma: str) -> str:
    p = str(plataforma or "").strip().lower()
    if p in ("iop", "iopsgps"):
        return "iop"
    if p in ("tracksolid", "tracksolidpro", "track"):
        return "tracksolid"
    return p


def _extract_digits(value: str) -> str:
    return "".join(ch for ch in str(value or "") if ch.isdigit())


def _extract_sim_and_account(dispositivo: dict, plataforma: str) -> tuple[str, str, str]:
    cuenta = ""
    cliente = ""
    sim = ""

    if plataforma == "tracksolid":
        cuenta = str(dispositivo.get("account") or dispositivo.get("_account") or "")
        cliente = str(dispositivo.get("customerName") or dispositivo.get("userName") or "")
        sim = _extract_digits(dispositivo.get("sim") or dispositivo.get("simNum") or "")
    else:
        account = dispositivo.get("account") if isinstance(dispositivo.get("account"), dict) else {}
        brief = dispositivo.get("deviceBrief") if isinstance(dispositivo.get("deviceBrief"), dict) else {}
        cuenta = str(account.get("accountName") or dispositivo.get("account") or dispositivo.get("accountId") or "")
        cliente = str(account.get("userName") or dispositivo.get("customerName") or "")
        sim = _extract_digits(brief.get("deviceMobile") or dispositivo.get("sim") or dispositivo.get("simNum") or "")

    return cuenta, cliente, sim


def _extract_campos_utilidades(dispositivo: dict, plataforma: str) -> dict:
    if plataforma == "tracksolid":
        account_val = str(dispositivo.get("account") or "")
        customer_val = str(dispositivo.get("customerName") or "")
        sim_val = _extract_digits(dispositivo.get("sim") or dispositivo.get("simNum") or "")
        return {
            "deaccount": account_val,
            "accountName": customer_val,
            "userName": customer_val,
            "deviceMobile": sim_val,
        }

    account = dispositivo.get("account") if isinstance(dispositivo.get("account"), dict) else {}
    brief = dispositivo.get("deviceBrief") if isinstance(dispositivo.get("deviceBrief"), dict) else {}
    account_name = str(account.get("accountName") or "")
    user_name = str(account.get("userName") or "")
    mobile = _extract_digits(brief.get("deviceMobile") or dispositivo.get("sim") or dispositivo.get("simNum") or "")

    return {
        "deaccount": account_name,
        "accountName": account_name,
        "userName": user_name,
        "deviceMobile": mobile,
    }


@app.get("/api/utilidades/plataformas")
def utilidades_plataformas():
    return {
        "plataformas": [
            {"label": "IOP", "value": "IOP"},
            {"label": "Tracksolid", "value": "TRACKSOLID"},
        ]
    }


@app.get("/api/utilidades/sims/details")
def utilidades_sims_details(identifiers: str = Query(..., min_length=6)):
    identifier = _extract_digits(identifiers)
    if len(identifier) < 6:
        raise HTTPException(status_code=400, detail="Identificador de SIM invalido")

    sim_api_client = os.getenv("SIMPRO_API_CLIENT", "").strip()
    sim_api_key = os.getenv("SIMPRO_API_KEY", "").strip()
    sim_base = os.getenv("SIMPRO_BASE_URL", "https://simpro4.wirelesslogic.com").strip().rstrip("/")

    if not sim_api_client or not sim_api_key:
        raise HTTPException(status_code=400, detail="Faltan credenciales SIMPRO_API_CLIENT y SIMPRO_API_KEY en el entorno")

    try:
        sim_url = f"{sim_base}/api/v3/sims/details"
        sim_resp = _requests.get(
            sim_url,
            params={"identifiers": identifier},
            headers={
                "x-api-client": sim_api_client,
                "x-api-key": sim_api_key,
            },
            timeout=20,
        )
        if not sim_resp.ok:
            raise HTTPException(status_code=sim_resp.status_code, detail=f"SIM details HTTP {sim_resp.status_code}")

        payload = sim_resp.json()
        first = payload[0] if isinstance(payload, list) and payload else {}
        active_connection = first.get("active_connection") if isinstance(first, dict) and isinstance(first.get("active_connection"), dict) else {}

        return {
            "identifiers": identifier,
            "items": payload if isinstance(payload, list) else [],
            "iccid": str(first.get("iccid") or "") if isinstance(first, dict) else "",
            "activation_date": str(active_connection.get("activation_date") or ""),
            "contract_end_date": str(active_connection.get("contract_end_date") or ""),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"No se pudo consultar SIM details: {e}")


def _simpro_creds() -> tuple[str, dict]:
    sim_api_client = os.getenv("SIMPRO_API_CLIENT", "").strip()
    sim_api_key = os.getenv("SIMPRO_API_KEY", "").strip()
    sim_base = os.getenv("SIMPRO_BASE_URL", "https://simpro4.wirelesslogic.com").strip().rstrip("/")
    if not sim_api_client or not sim_api_key:
        raise HTTPException(status_code=400, detail="Faltan credenciales SIMPRO_API_CLIENT y SIMPRO_API_KEY en el entorno")
    return sim_base, {"x-api-client": sim_api_client, "x-api-key": sim_api_key}


def _simpro_get(path: str, params: dict):
    sim_base, headers = _simpro_creds()
    resp = _requests.get(f"{sim_base}{path}", params=params, headers=headers, timeout=30)
    if not resp.ok:
        raise HTTPException(status_code=resp.status_code, detail=f"SIMPRO {path} HTTP {resp.status_code}")
    return resp.json()


def _chunked(seq: list, size: int):
    for i in range(0, len(seq), size):
        yield seq[i:i + size]


@app.post("/api/utilidades/sims/importar")
def importar_sims_simpro():
    """Carga inicial: trae TODOS los SIMs de SIMPRO y los inserta como borrador en
    consultas_sim (campos que SIMPRO no conoce, como plataforma IOP/Tracksolid,
    quedan vacios a proposito para que el usuario los complete). Es re-ejecutable:
    lo que ya existe (por device_mobile o iccid) se omite, no duplica."""
    todos = []
    page = 1
    limit = 2000
    while True:
        data = _simpro_get("/api/v3/sims", {"page": page, "limit": limit})
        items = data.get("sims") if isinstance(data, dict) else None
        items = items if isinstance(items, list) else []
        todos.extend(items)
        if len(items) < limit or page > 50:
            break
        page += 1

    identificadores = []
    vistos = set()
    for item in todos:
        if not isinstance(item, dict):
            continue
        ident = str(item.get("iccid") or "").strip() or _extract_digits(item.get("msisdn") or "")
        if ident and ident not in vistos:
            vistos.add(ident)
            identificadores.append(ident)

    if not identificadores:
        return {"importados": 0, "omitidos": 0, "total_simpro": len(todos)}

    detalles = []
    for lote in _chunked(identificadores, 30):
        data = _simpro_get("/api/v3/sims/details", {"identifiers": ",".join(lote)})
        if isinstance(data, list):
            detalles.extend(data)

    db = _get_db()
    cursor = db.cursor()

    importados = 0
    omitidos = 0

    for det in detalles:
        if not isinstance(det, dict):
            continue

        iccid = str(det.get("iccid") or "").strip()
        imei = _extract_digits(det.get("imei") or "")
        active_conn = det.get("active_connection") if isinstance(det.get("active_connection"), dict) else {}
        device_mobile = _extract_digits(active_conn.get("msisdn") or "")
        if not device_mobile:
            origen = next((m for m in todos if str(m.get("iccid") or "") == iccid), None)
            device_mobile = _extract_digits((origen or {}).get("msisdn") or "")

        if not device_mobile and not iccid:
            continue

        cursor.execute(
            "SELECT id FROM consultas_sim WHERE (device_mobile=%s AND device_mobile<>'') OR (iccid=%s AND iccid<>'') LIMIT 1",
            (device_mobile, iccid)
        )
        if cursor.fetchone():
            omitidos += 1
            continue

        billing_account = det.get("billing_account") if isinstance(det.get("billing_account"), dict) else {}
        deaccount = str(det.get("custom_field1") or "").strip()
        account_name = str(billing_account.get("name") or "").strip()
        activation_date = str(active_conn.get("activation_date") or "")
        vigencia_sim = str(active_conn.get("contract_end_date") or "")

        cursor.execute(
            """INSERT INTO consultas_sim
               (tipo, activation_date, deaccount, account_name, plataforma,
                imei, iccid, device_mobile, vigencia_sim)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            ("activacion", activation_date, deaccount, account_name, "",
             imei, iccid, device_mobile, vigencia_sim)
        )
        importados += 1

    db.commit()
    cursor.close()
    db.close()

    return {"importados": importados, "omitidos": omitidos, "total_simpro": len(todos)}


@app.post("/api/utilidades/consulta-imei")
def utilidades_consulta_imei(payload: UtilidadesConsultaRequest):
    imei = _extract_digits(payload.imei)
    plataforma = _normalize_plataforma_utilidades(payload.plataforma)

    if len(imei) < 6:
        raise HTTPException(status_code=400, detail="IMEI invalido")
    if plataforma not in ("iop", "tracksolid"):
        raise HTTPException(status_code=400, detail="Plataforma no soportada. Usa IOP o TRACKSOLID.")

    base_detail = detalle_dispositivo_plataforma(imei, plataforma=plataforma)
    dispositivo = base_detail.get("dispositivo")
    if isinstance(dispositivo, list):
        dispositivo = dispositivo[0] if dispositivo else {}
    if not isinstance(dispositivo, dict):
        dispositivo = {}

    campos = _extract_campos_utilidades(dispositivo, plataforma)
    cuenta = campos.get("deaccount") or ""
    cliente = campos.get("accountName") or ""
    user_name = campos.get("userName") or ""
    sim = campos.get("deviceMobile") or ""

    sim_error = None
    sim_payload = None
    iccid = ""
    activation_date = ""

    sim_api_client = os.getenv("SIMPRO_API_CLIENT", "").strip()
    sim_api_key = os.getenv("SIMPRO_API_KEY", "").strip()
    sim_base = os.getenv("SIMPRO_BASE_URL", "https://simpro4.wirelesslogic.com").strip().rstrip("/")

    if sim:
        if sim_api_client and sim_api_key:
            try:
                sim_url = f"{sim_base}/api/v3/sims/details"
                sim_resp = _requests.get(
                    sim_url,
                    params={"identifiers": sim},
                    headers={
                        "x-api-client": sim_api_client,
                        "x-api-key": sim_api_key,
                    },
                    timeout=20,
                )
                if not sim_resp.ok:
                    raise Exception(f"HTTP {sim_resp.status_code}")
                sim_payload = sim_resp.json()
                first = sim_payload[0] if isinstance(sim_payload, list) and sim_payload else {}
                if isinstance(first, dict):
                    iccid = str(first.get("iccid") or "")
                    active_connection = first.get("active_connection") if isinstance(first.get("active_connection"), dict) else {}
                    activation_date = str(active_connection.get("activation_date") or "")
            except Exception as e:
                sim_error = f"No se pudo consultar SIM details: {e}"
        else:
            sim_error = "Faltan credenciales SIMPRO_API_CLIENT y SIMPRO_API_KEY en el entorno"

    return {
        "imei": imei,
        "plataforma": "TRACKSOLID" if plataforma == "tracksolid" else "IOP",
        "deaccount": cuenta,
        "accountName": cliente,
        "userName": user_name,
        "deviceMobile": sim,
        "cuenta_plataforma": cuenta,
        "nombre_cliente": cliente,
        "sim": sim,
        "iccid": iccid,
        "activation_date": activation_date,
        "dispositivo": dispositivo,
        "sim_details": sim_payload,
        "plataforma_error": None,
        "sim_error": sim_error,
    }


# ── consultas_sim ────────────────────────────────────────────────────────────

class ConsultaSimRecord(BaseModel):
    tipo: str = "activacion"
    activation_date: str = ""
    deaccount: str = ""
    account_name: str = ""
    plataforma: str = ""
    imei: str = ""
    iccid: str = ""
    device_mobile: str = ""
    vigencia_sim: str = ""


def _get_db():
    return mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )


def _consultas_sim_imei_exists(cursor, imei: str, exclude_id: int | None = None):
    imei_clean = str(imei or "").strip()
    if not imei_clean:
        return None

    query = "SELECT id FROM consultas_sim WHERE imei=%s"
    params = [imei_clean]
    if exclude_id is not None:
        query += " AND id<>%s"
        params.append(exclude_id)
    query += " LIMIT 1"
    cursor.execute(query, params)
    return cursor.fetchone()


@app.get("/api/utilidades/consultas-sim")
def list_consultas_sim(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    tipo: str | None = Query(None),
    activation_date: str | None = Query(None),
    deaccount: str | None = Query(None),
    account_name: str | None = Query(None),
    plataforma: str | None = Query(None),
    imei: str | None = Query(None),
    iccid: str | None = Query(None),
    device_mobile: str | None = Query(None),
    vigencia_sim: str | None = Query(None),
):
    db = _get_db()
    cursor = db.cursor(dictionary=True)
    offset = (page - 1) * size
    conditions = []
    values = []

    def add_like(column: str, value: str | None):
        if value is None:
            return
        cleaned = str(value).strip()
        if not cleaned:
            return
        conditions.append(f"{column} LIKE %s")
        values.append(f"%{cleaned}%")

    def add_vigencia_sim_range(value: str | None):
        cleaned = str(value or "").strip()
        if cleaned != "vencidos_7_dias":
            return False
        limite = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        conditions.append("vigencia_sim <> '' AND LEFT(vigencia_sim, 10) <= %s")
        values.append(limite)
        return True

    if tipo:
        cleaned_tipo = str(tipo).strip()
        if cleaned_tipo:
            conditions.append("tipo = %s")
            values.append(cleaned_tipo)

    add_like("activation_date", activation_date)
    add_like("deaccount", deaccount)
    add_like("account_name", account_name)
    add_like("plataforma", plataforma)
    add_like("imei", imei)
    add_like("iccid", iccid)
    add_like("device_mobile", device_mobile)
    if not add_vigencia_sim_range(vigencia_sim):
        add_like("vigencia_sim", vigencia_sim)

    where_sql = f" WHERE {' AND '.join(conditions)}" if conditions else ""

    cursor.execute(f"SELECT COUNT(*) AS total FROM consultas_sim{where_sql}", values)
    total = cursor.fetchone()["total"]

    query_values = list(values) + [size, offset]
    cursor.execute(
        f"SELECT * FROM consultas_sim{where_sql} ORDER BY activation_date DESC, creado_en DESC LIMIT %s OFFSET %s",
        query_values
    )
    rows = cursor.fetchall()
    cursor.close()
    db.close()
    for row in rows:
        if row.get("creado_en") and hasattr(row["creado_en"], "isoformat"):
            row["creado_en"] = row["creado_en"].isoformat()
    return {"total": total, "page": page, "size": size, "items": rows}


@app.post("/api/utilidades/consultas-sim", status_code=201)
def save_consulta_sim(record: ConsultaSimRecord):
    required = {
        "tipo": record.tipo,
        "activation_date": record.activation_date,
        "deaccount": record.deaccount,
        "account_name": record.account_name,
        "plataforma": record.plataforma,
        "iccid": record.iccid,
        "vigencia_sim": record.vigencia_sim,
    }
    missing = [k for k, v in required.items() if not str(v or "").strip()]
    if missing:
        raise HTTPException(status_code=400, detail=f"Datos incompletos: {', '.join(missing)}")

    imei_clean = str(record.imei or "").strip()
    sim_clean = str(record.device_mobile or "").strip()
    if not imei_clean and not sim_clean:
        raise HTTPException(status_code=400, detail="Debes proporcionar IMEI o SIM ESPAÑOL")

    db = _get_db()
    cursor = db.cursor()
    if _consultas_sim_imei_exists(cursor, imei_clean):
        cursor.close()
        db.close()
        raise HTTPException(status_code=409, detail="Ya existe un registro con ese IMEI")
    cursor.execute(
        """INSERT INTO consultas_sim
           (tipo, activation_date, deaccount, account_name, plataforma,
            imei, iccid, device_mobile, vigencia_sim)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        (
            record.tipo,
            record.activation_date,
            record.deaccount,
            record.account_name,
            record.plataforma,
            imei_clean,
            record.iccid,
            sim_clean,
            record.vigencia_sim,
        )
    )
    new_id = cursor.lastrowid
    db.commit()
    cursor.close()
    db.close()
    return {"id": new_id, "message": "Guardado"}


@app.put("/api/utilidades/consultas-sim/{record_id}")
def update_consulta_sim(record_id: int, record: ConsultaSimRecord):
    required = {
        "tipo": record.tipo,
        "activation_date": record.activation_date,
        "deaccount": record.deaccount,
        "account_name": record.account_name,
        "plataforma": record.plataforma,
        "iccid": record.iccid,
        "vigencia_sim": record.vigencia_sim,
    }
    missing = [k for k, v in required.items() if not str(v or "").strip()]
    if missing:
        raise HTTPException(status_code=400, detail=f"Datos incompletos: {', '.join(missing)}")

    imei_clean = str(record.imei or "").strip()
    sim_clean = str(record.device_mobile or "").strip()
    if not imei_clean and not sim_clean:
        raise HTTPException(status_code=400, detail="Debes proporcionar IMEI o SIM ESPAÑOL")

    db = _get_db()
    cursor = db.cursor()
    if _consultas_sim_imei_exists(cursor, imei_clean, exclude_id=record_id):
        cursor.close()
        db.close()
        raise HTTPException(status_code=409, detail="Ya existe otro registro con ese IMEI")
    cursor.execute(
        """UPDATE consultas_sim
           SET tipo=%s, activation_date=%s, deaccount=%s, account_name=%s, plataforma=%s,
               imei=%s, iccid=%s, device_mobile=%s, vigencia_sim=%s
           WHERE id=%s""",
        (
            record.tipo,
            record.activation_date,
            record.deaccount,
            record.account_name,
            record.plataforma,
            imei_clean,
            record.iccid,
            sim_clean,
            record.vigencia_sim,
            record_id,
        )
    )
    db.commit()
    changed = cursor.rowcount
    cursor.close()
    db.close()
    if changed == 0:
        raise HTTPException(status_code=404, detail="Registro no encontrado")
    return {"id": record_id, "message": "Actualizado"}


@app.delete("/api/utilidades/consultas-sim/{record_id}")
def delete_consulta_sim(record_id: int):
    db = _get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM consultas_sim WHERE id=%s", (record_id,))
    db.commit()
    changed = cursor.rowcount
    cursor.close()
    db.close()
    if changed == 0:
        raise HTTPException(status_code=404, detail="Registro no encontrado")
    return {"id": record_id, "message": "Eliminado"}
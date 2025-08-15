from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
import base64
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Puedes restringir a ["http://localhost:5173"] si prefieres
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
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
    CERT_PATH = os.getenv("CSD_CERT_PATH")
    KEY_PATH = os.getenv("CSD_KEY_PATH")
    KEY_PASS = os.getenv("CSD_KEY_PASS").encode() if os.getenv("CSD_KEY_PASS") else b""

    try:
        if not KEY_PATH or not os.path.exists(KEY_PATH):
            raise Exception(f"No se encontró la llave privada en la ruta: {KEY_PATH}")
        with open(KEY_PATH, "rb") as key_file:
            private_key = serialization.load_der_private_key(
                key_file.read(),
                password=KEY_PASS,
                backend=default_backend()
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cargando llave: {str(e)}")

    # Generar XML CFDI (simplificado)
    conceptos_xml = "".join([
        f'<cfdi:Concepto ClaveProdServ="{p.ClaveProdServ}" Cantidad="{p.Cantidad}" ClaveUnidad="{p.ClaveUnidad}" Unidad="{p.Unidad}" Descripcion="{p.Descripcion}" ValorUnitario="{p.ValorUnitario}" Importe="{p.Importe}"/>'
        for p in data.productos
    ])
    cfdi_xml = f'''<cfdi:Comprobante xmlns:cfdi="http://www.sat.gob.mx/cfd/4" Version="4.0" Serie="A" Folio="1" Fecha="2025-08-15T12:00:00" FormaPago="{data.forma_pago}" SubTotal="{data.total}" Moneda="MXN" Total="{data.total}" TipoDeComprobante="I" MetodoPago="{data.metodo_pago}" LugarExpedicion="64000">
  <cfdi:Emisor Rfc="{os.getenv('CSD_RFC','RAQÑ7701212M3')}" Nombre="Empresa de Pruebas" RegimenFiscal="601"/>
  <cfdi:Receptor Rfc="{data.rfc_cliente}" Nombre="{data.nombre_cliente}" DomicilioFiscalReceptor="64000" RegimenFiscalReceptor="601" UsoCFDI="{data.uso_cfdi}"/>
  <cfdi:Conceptos>
    {conceptos_xml}
  </cfdi:Conceptos>
  <cfdi:Impuestos TotalImpuestosTrasladados="16.00">
    <cfdi:Traslados>
      <cfdi:Traslado Base="100.00" Impuesto="002" TipoFactor="Tasa" TasaOCuota="0.160000" Importe="16.00"/>
    </cfdi:Traslados>
  </cfdi:Impuestos>
</cfdi:Comprobante>'''

    # Generar string original (simplificado)
    string_original = f"||4.0|A|1|2025-08-15T12:00:00|{data.forma_pago}|{data.total}|0|MXN|{data.total}|I|{data.metodo_pago}|64000|{os.getenv('CSD_RFC','RAQÑ7701212M3')}|601|{data.rfc_cliente}|{data.uso_cfdi}|{data.productos[0].Descripcion}|{data.productos[0].Importe}|16.00||"

    # Firmar el string original
    try:
        signature = private_key.sign(
            string_original.encode(),
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        sello = base64.b64encode(signature).decode()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error firmando CFDI: {str(e)}")

    return {
        "cfdi_xml": cfdi_xml,
        "sello": sello
    }

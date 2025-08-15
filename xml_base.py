from lxml import etree
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
import base64

CERT_PATH = "RAQÑ7701212M3_20230509115720/CSD_RAQÑ7701212M3_20230509131040/CSD_Sucursal_1_RAQÑ7701212M3_20230509_131034.cer"  # Certificado Sucursal 1
KEY_PATH = "RAQÑ7701212M3_20230509115720/CSD_RAQÑ7701212M3_20230509131040/CSD_Sucursal_1_RAQÑ7701212M3_20230509_131034.key"   # Llave privada Sucursal 1
KEY_PASS = b"12345678a"

cfdi_xml = '''<cfdi:Comprobante xmlns:cfdi="http://www.sat.gob.mx/cfd/4" Version="4.0" Serie="A" Folio="1" Fecha="2025-08-15T12:00:00" FormaPago="01" SubTotal="100.00" Moneda="MXN" Total="116.00" TipoDeComprobante="I" MetodoPago="PUE" LugarExpedicion="64000">
  <cfdi:Emisor Rfc="RAQÑ7701212M3" Nombre="Empresa de Pruebas" RegimenFiscal="601"/>
  <cfdi:Receptor Rfc="XAXX010101000" Nombre="Publico en General" DomicilioFiscalReceptor="64000" RegimenFiscalReceptor="601" UsoCFDI="G03"/>
  <cfdi:Conceptos>
    <cfdi:Concepto ClaveProdServ="01010101" Cantidad="1" ClaveUnidad="ACT" Unidad="Actividad" Descripcion="Servicio de prueba" ValorUnitario="100.00" Importe="100.00"/>
  </cfdi:Conceptos>
  <cfdi:Impuestos TotalImpuestosTrasladados="16.00">
    <cfdi:Traslados>
      <cfdi:Traslado Base="100.00" Impuesto="002" TipoFactor="Tasa" TasaOCuota="0.160000" Importe="16.00"/>
    </cfdi:Traslados>
  </cfdi:Impuestos>
</cfdi:Comprobante>'''

with open(KEY_PATH, "rb") as key_file:
    private_key = serialization.load_der_private_key(
        key_file.read(),
        password=KEY_PASS,
        backend=default_backend()
    )

string_original = "||4.0|A|1|2025-08-15T12:00:00|01|100.00|0|MXN|116.00|I|PUE|64000|RAQÑ7701212M3|601|XAXX010101000|G03|Servicio de prueba|100.00|16.00||"
signature = private_key.sign(
    string_original.encode(),
    padding.PKCS1v15(),
    hashes.SHA256()
)

sello = base64.b64encode(signature).decode()

print("XML CFDI:")
print(cfdi_xml)
print("\nSello digital (base64):")
print(sello)


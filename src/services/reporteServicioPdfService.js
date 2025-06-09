import pdfMake from "pdfmake/build/pdfmake";
import pdfFonts from "pdfmake/build/vfs_fonts";


export async function generarReporteServicioPDF({ reporte, venta, cliente, empresa }) {
  const logo = ''; // <-- Pega aquí tu cadena base64

  const folio = venta?.folio || venta?.id || '---';
  const fecha = reporte?.fecha || new Date().toLocaleDateString('es-MX');

  const empresaData = empresa || {
    nombre: 'GPSubicacion.com',
    direccion: 'Guadalajara',
    rfc: 'RFC123456',
    regimen: '',
    telefono: '',
    correo: '',
    web: ''
  };

  function tablaDatos(datos) {
    return {
      table: {
        widths: [120, '*'],
        body: Object.entries(datos).map(([k, v]) => [
          { text: k, style: 'tableHeader' },
          { text: v, style: 'tableCell' }
        ])
      },
      layout: {
        fillColor: function (rowIndex) {
          return rowIndex === 0 ? '#f3f3f3' : (rowIndex % 2 === 0 ? '#f9f9f9' : null);
        }
      },
      margin: [0, 0, 0, 10]
    };
  }

  const docDefinition = {
    content: [
      {
        columns: [
          [
            logo ? { image: logo, width: 120, alignment: 'left', margin: [0, 0, 0, 10] } : {},
            { text: empresaData.nombre, style: 'empresaHeader', alignment: 'left' },
            { text: empresaData.direccion, style: 'empresaSubheader', alignment: 'left' },
            { text: `RFC: ${empresaData.rfc}`, style: 'empresaSubheader', alignment: 'left' },
            empresaData.regimen ? { text: `Régimen fiscal: ${empresaData.regimen}`, style: 'empresaSubheader', alignment: 'left' } : {},
            empresaData.telefono ? { text: empresaData.telefono, style: 'empresaSubheader', alignment: 'left' } : {},
            empresaData.correo ? { text: empresaData.correo, style: 'empresaSubheader', alignment: 'left' } : {},
            empresaData.web ? { text: empresaData.web, style: 'empresaSubheader', alignment: 'left' } : {},
            { text: `Fecha: ${fecha}`, alignment: 'left', margin: [0, 10, 0, 0], style: 'empresaSubheader' }
          ],
          [
            { text: `Reporte de servicio - ${folio}`, style: 'title', alignment: 'right', margin: [0, 0, 0, 10] }
          ]
        ]
      },

      // DATOS PRINCIPALES EN DOS COLUMNAS
      {
        columns: [
          [
            { text: 'Datos del cliente', style: 'sectionHeaderCentered', margin: [0, 10, 0, 0] },
            tablaDatos({
              'Cliente': cliente?.nombre || '',
              'Teléfono': cliente?.telefonos?.join(', ') || '',
              'RFC': cliente?.rfc || '',
              'Dirección': cliente?.direccion || ''
            }),
            { text: 'Datos del equipo', style: 'sectionHeaderCentered', margin: [0, 10, 0, 0] },
            tablaDatos({
              'Equipo/Plan': reporte?.equipo_plan || '',
              'IMEI': reporte?.imei || '',
              'Serie': reporte?.serie || '',
              'Accesorios': reporte?.accesorios || ''
            }),
            { text: 'Datos SIM', style: 'sectionHeaderCentered', margin: [0, 10, 0, 0] },
            tablaDatos({
              'Proveedor': reporte?.sim_proveedor || '',
              'Serie': reporte?.sim_serie || '',
              'Instalador': reporte?.sim_instalador || '',
              'Teléfono': reporte?.sim_telefono || ''
            }),
            { text: 'Plataforma y usuario', style: 'sectionHeaderCentered', margin: [0, 10, 0, 0] },
            tablaDatos({
              'Plataforma': reporte?.plataforma || '',
              'Usuario': reporte?.usuario || ''
            }),
            { text: 'Venta y pago', style: 'sectionHeaderCentered', margin: [0, 10, 0, 0] },
            tablaDatos({
              'Subtotal': reporte?.subtotal ? `$${reporte.subtotal}` : '',
              'Total': reporte?.total ? `$${reporte.total}` : '',
              'Forma de pago': reporte?.forma_pago || '',
              'Pagado': reporte?.pagado ? 'Sí' : 'No'
            })
          ],
          [
            { text: 'Datos del vehículo', style: 'sectionHeaderCentered', margin: [0, 10, 0, 0] },
            tablaDatos({
              'Marca': reporte?.marca || '',
              'Submarca': reporte?.submarca || '',
              'Modelo': reporte?.modelo || '',
              'Placas': reporte?.placas || '',
              'Color': reporte?.color || '',
              'Número económico': reporte?.numero_economico || ''
            }),
            { text: 'Conexión y corte', style: 'sectionHeaderCentered', margin: [0, 10, 0, 0] },
            tablaDatos({
              'Batería': reporte?.bateria || '',
              'Ignición': reporte?.ignicion || '',
              'Corte': reporte?.corte || '',
              'Ubicación corte': reporte?.ubicacion_corte || ''
            }),
            { text: 'Técnico', style: 'sectionHeaderCentered', margin: [0, 10, 0, 0] },
            tablaDatos({
              'Técnico': reporte?.nombre_instalador || ''
            })
          ]
        ],
        columnGap: 30
      },

      { text: 'Observaciones', style: 'sectionHeaderCentered', margin: [0, 10, 0, 0] },
      {
        table: {
          widths: ['*'],
          body: [
            [
              { text: reporte?.observaciones || 'Sin observaciones', style: 'tableCell' }
            ]
          ]
        }
      },
      { text: 'Firmas', style: 'sectionHeaderCentered', margin: [0, 10, 0, 0] },
      {
        table: {
          widths: ['*', '*'],
          body: [
            [
              { text: 'Cliente', style: 'tableHeader' },
              { text: 'Instalador', style: 'tableHeader' }
            ],
            [
              { text: reporte?.firma_cliente || '', style: 'tableCell' },
              { text: reporte?.firma_instalador || '', style: 'tableCell' }
            ]
          ]
        },
        layout: {
          fillColor: function (rowIndex) {
            return rowIndex === 0 ? '#666' : null;
          }
        }
      }
    ],
    styles: {
      empresaHeader: { fontSize: 14, bold: true, color: '#444' },
      empresaSubheader: { fontSize: 9, color: '#666' },
      title: { fontSize: 16, bold: true, color: '#222', margin: [0, 10, 0, 10] },
      sectionHeaderCentered: { fontSize: 13, bold: true, color: '#fff', fillColor: '#666', alignment: 'center', margin: [0, 16, 0, 4], decoration: 'underline', letterSpacing: 1, lineHeight: 1.2, background: '#666' },
      tableHeader: { bold: true, fillColor: '#666', color: '#fff', fontSize: 10, alignment: 'left' },
      tableCell: { fontSize: 10, color: '#222', margin: [0, 2, 0, 2] }
    },
    defaultStyle: {
      fontSize: 9
    }
  };

  pdfMake.createPdf(docDefinition).open();
}
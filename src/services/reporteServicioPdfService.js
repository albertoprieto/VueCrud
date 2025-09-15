import pdfMake from "pdfmake/build/pdfmake";
import pdfFonts from "pdfmake/build/vfs_fonts";

export async function generarReporteServicioPDF({ reporte, venta, cliente, empresa }) {
  const folio = venta?.folio || venta?.id || '---';
  const fecha = reporte?.fecha || new Date().toLocaleDateString('es-MX');
  const empresaData = {
    nombre: 'COMERCIALIZADORA TECNOLOGICA DEL RIO',
    direccion: 'Fresno 1441 44910 Guadalajara, Jalisco, México',
    rfc: 'CTR1905206K5',
    regimen: '626 - Régimen Simplificado de Confianza',
    telefono: '3325373183',
    correo: 'gpsvector@gmail.com',
    web: 'gpsubicacion.com'
  };

  // Bloques horizontales agrupados SIN ICONOS, mejor alineación y colores
  function block(title, fields) {
    return [
      { text: title, style: 'sectionTitle', margin: [0, 16, 0, 6] },
      {
        table: {
          widths: ['35%', '65%'],
          body: Object.entries(fields).map(([k, v]) => [
            { text: k, style: 'fieldLabel' },
            { text: v || '-', style: 'fieldValue' }
          ])
        },
        layout: {
          fillColor: function (rowIndex) {
            return rowIndex % 2 === 0 ? '#f4f6fa' : '#fff';
          },
          hLineWidth: () => 0,
          vLineWidth: () => 0
        },
        margin: [0, 0, 0, 0]
      }
    ];
  }

  // Agrupa los bloques en pares para mostrarlos en dos columnas
  function blocksInColumns(blocksArr) {
    const columnsArr = [];
    for (let i = 0; i < blocksArr.length; i += 2) {
      if (i + 1 < blocksArr.length) {
        columnsArr.push({ columns: [ { stack: blocksArr[i] }, { stack: blocksArr[i+1] } ], columnGap: 24, margin: [0,0,0,0] });
      } else {
        columnsArr.push({ columns: [ { stack: blocksArr[i] }, { text: '' } ], columnGap: 24, margin: [0,0,0,0] });
      }
    }
    return columnsArr;
  }

  const blocksList = [
    block('Cliente', {
      'Nombre': reporte?.nombre_cliente || cliente?.nombre || '-',
      'Teléfono': cliente?.telefonos?.join(', ') || '-',
      'Dirección': cliente?.direccion || '-'
    }),
    block('Técnico', {
      'Técnico': reporte?.nombre_instalador || '-'
    }),
    block('Vehículo', {
      'Marca': reporte?.marca || '-',
      'Submarca': reporte?.submarca || '-',
      'Modelo': reporte?.modelo || '-',
      'Placas': reporte?.placas || '-',
      'Color': reporte?.color || '-',
      'Número económico': reporte?.numero_economico || '-'
    }),
    block('GPS', {
      'Modelo GPS': reporte?.modelo_gps || '-',
      'IMEI': reporte?.imei || '-',
      'Serie': reporte?.serie || '-',
      'Accesorios': reporte?.accesorios || '-',
      'Ubicación GPS': reporte?.ubicacion_gps || '-',
      'Ubicación Bloqueo': reporte?.ubicacion_bloqueo || '-'
    }),
    block('SIM', {
      'Serie SIM': reporte?.sim_serie || '-'
    }),
    block('Pago', {
      'Subtotal': reporte?.subtotal ? `$${reporte.subtotal}` : '-',
      'Total': reporte?.total ? `$${reporte.total}` : '-',
      'Forma de pago': reporte?.forma_pago || '-',
      'Monto técnico': reporte?.monto_tecnico ? `$${reporte.monto_tecnico}` : '-',
      'Viáticos': reporte?.viaticos ? `$${reporte.viaticos}` : '-',
      'Pagado': reporte?.pagado ? 'Sí' : 'No'
    })
  ];

  const docDefinition = {
    content: [
      { text: empresaData.nombre, style: 'empresaTitle', margin: [0, 0, 0, 2] },
      { text: empresaData.direccion, style: 'empresaSub' },
      { text: `RFC: ${empresaData.rfc}   |   ${empresaData.regimen}`, style: 'empresaSub' },
      { text: empresaData.telefono + '   |   ' + empresaData.correo + '   |   ' + empresaData.web, style: 'empresaSub', margin: [0, 0, 0, 10] },
      { canvas: [ { type: 'line', x1: 0, y1: 0, x2: 520, y2: 0, lineWidth: 1.5, lineColor: '#1a237e' } ], margin: [0, 8, 0, 8] },
      {
        columns: [
          { text: `Reporte de servicio`, style: 'mainTitle', alignment: 'left' },
          { text: `Folio: ${folio}`, style: 'folio', alignment: 'right' },
          { text: `Fecha: ${fecha}`, style: 'folio', alignment: 'right' }
        ],
        columnGap: 10,
        margin: [0, 0, 0, 10]
      },
      ...blocksInColumns(blocksList),
      { text: 'Observaciones', style: 'sectionTitle', margin: [0, 18, 0, 4] },
      {
        table: {
          widths: ['*'],
          body: [ [ { text: reporte?.observaciones || 'Sin observaciones', style: 'fieldValue' } ] ]
        },
        layout: 'noBorders',
        margin: [0, 0, 0, 8]
      }
    ],
    styles: {
      empresaTitle: { fontSize: 20, bold: true, color: '#1a237e', alignment: 'left' },
      empresaSub: { fontSize: 11, color: '#555', alignment: 'left' },
      mainTitle: { fontSize: 18, bold: true, color: '#222', alignment: 'left', margin: [0, 0, 0, 0] },
      folio: { fontSize: 12, color: '#1a237e', alignment: 'right', margin: [0, 0, 0, 0] },
      sectionTitle: { fontSize: 15, bold: true, color: '#fff', fillColor: '#1a237e', alignment: 'left', margin: [0, 10, 0, 4], letterSpacing: 1 },
      fieldLabel: { fontSize: 12, color: '#1a237e', bold: true, margin: [0, 2, 0, 2] },
      fieldValue: { fontSize: 12, color: '#222', margin: [0, 2, 0, 2] }
    },
    defaultStyle: {
      fontSize: 11
    }
  };

  pdfMake.createPdf(docDefinition).open();
}
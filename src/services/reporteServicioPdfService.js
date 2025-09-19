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

  function pickSimForIndex(li, baseSimSeries) {
    try {
      if (Array.isArray(li?.sims) && li.sims.length) {
        const val = li.sims[0];
        if (val) return String(val);
      }
      if (Array.isArray(baseSimSeries) && baseSimSeries.length) {
        return String(baseSimSeries[0]);
      }
      if (li && li.sim_serie) return String(li.sim_serie);
    } catch(_) { /* noop */ }
    return '';
  }

  const subtotalCalc = Number(reporte?.subtotal ?? 0) || 0;
  const descuentoPct = Number(reporte?.descuento ?? venta?.descuento ?? 0) || 0;
  const descuentoCalc = subtotalCalc * (descuentoPct / 100);
  const baseCalc = Math.max(0, subtotalCalc - descuentoCalc);
  const requiereFactura = Boolean(venta?.requiereFactura ?? reporte?.requiereFactura);
  const ivaCalc = requiereFactura ? baseCalc * 0.16 : 0;
  const totalCalc = Number(reporte?.total ?? 0) || (baseCalc + ivaCalc);

  const blocksList = [
    block('Cliente', {
      'Nombre': reporte?.nombre_cliente || cliente?.nombre || '-',
      'Teléfono': cliente?.telefonos?.join(', ') || '-',
      'Dirección': cliente?.direccion || '-'
    }),
    block('Técnico', {
      'Técnico': reporte?.nombre_instalador || '-'
    }),
    block('Pago', {
      'Subtotal': subtotalCalc ? `$${subtotalCalc.toFixed(2)}` : '-',
      'Descuento (%)': `${descuentoPct}%`,
      'IVA (16%)': `$${ivaCalc.toFixed(2)}`,
      'Total': `$${totalCalc.toFixed(2)}`,
      'Forma de pago': reporte?.forma_pago || '-',
      'Monto técnico': reporte?.monto_tecnico ? `$${Number(reporte.monto_tecnico).toFixed(2)}` : '-',
      'Viáticos': reporte?.viaticos ? `$${Number(reporte.viaticos).toFixed(2)}` : '-',
      'Pagado': reporte?.pagado ? 'Sí' : 'No'
    })
  ];

  // Secciones por instalación
  const instalacionesBlocks = [];
  const imeiLines = Array.isArray(reporte?.imeis_articulos) ? reporte.imeis_articulos : [];
  const simSeries = Array.isArray(reporte?.sim_series) ? reporte.sim_series : [];
  if (imeiLines.length > 0) {
    let simIdx = 0;
    let contador = 1;
    for (const li of imeiLines) {
      const imeis = Array.isArray(li.imeis) ? li.imeis.filter(Boolean) : [];
      const simsLinea = Array.isArray(li.sims) ? li.sims : [];
      for (let i = 0; i < imeis.length; i++) {
        const imei = imeis[i];
        const sim = simsLinea[i] || simSeries[simIdx] || (reporte?.sim_serie || '-');
        if (!simsLinea[i] && simSeries[simIdx]) simIdx += 1;
        instalacionesBlocks.push(
          block(`Servicio de Instalación #${contador}`,[
            ['Marca', li.marca || reporte?.marca || '-'],
            ['Submarca', li.submarca || reporte?.submarca || '-'],
            ['Modelo', li.modelo || reporte?.modelo || '-'],
            ['Placas', li.placas || reporte?.placas || '-'],
            ['Color', li.color || reporte?.color || '-'],
            ['Número económico', li.numero_economico || reporte?.numero_economico || '-'],
            ['Modelo GPS', li.modelo_gps || reporte?.modelo_gps || '-'],
            ['IMEI', imei || '-'],
            ['Serie SIM', sim || '-'],
            ['Ubicación GPS', li.ubicacion_gps || reporte?.ubicacion_gps || '-'],
            ['Ubicación Bloqueo', li.ubicacion_bloqueo || reporte?.ubicacion_bloqueo || '-']
          ].reduce((acc,[k,v])=>{ acc[k]=v; return acc; }, {}))
        );
        contador += 1;
      }
    }
  } else {
    // Push as a grouped block
    instalacionesBlocks.push(
      block('Servicio de Instalación', {
        'Marca': reporte?.marca || '-',
        'Submarca': reporte?.submarca || '-',
        'Modelo': reporte?.modelo || '-',
        'Placas': reporte?.placas || '-',
        'Color': reporte?.color || '-',
        'Número económico': reporte?.numero_economico || '-',
        'Modelo GPS': reporte?.modelo_gps || '-',
        'IMEI': reporte?.imei || '-',
        'Serie SIM': reporte?.sim_serie || '-',
        'Ubicación GPS': reporte?.ubicacion_gps || '-',
        'Ubicación Bloqueo': reporte?.ubicacion_bloqueo || '-'
      })
    );
  }

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
      { text: 'Servicios de Instalación', style: 'sectionTitle', margin: [0, 18, 0, 4] },
      ...blocksInColumns(instalacionesBlocks),
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
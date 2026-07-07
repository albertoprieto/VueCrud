import pdfMake from "pdfmake/build/pdfmake";
import pdfFonts from "pdfmake/build/vfs_fonts";

pdfMake.vfs = pdfFonts.pdfMake ? pdfFonts.pdfMake.vfs : pdfFonts;

const LOGO = 'data:image/svg+xml;base64,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';

export async function generarNotaServicioPDF({ notaId, cliente, total, ordenes, reportes, abrirEnLinea = false }) {
  pdfMake.vfs = pdfFonts.pdfMake ? pdfFonts.pdfMake.vfs : pdfFonts;

  const folio = `NV-${String(notaId || 0).padStart(6, '0')}`;
  const fechaStr = new Date().toLocaleDateString('es-MX', { day: '2-digit', month: '2-digit', year: 'numeric' });
  const _total = Number(total || 0);

  // Build dispositivos from report rows
  const dispositivos = (reportes || []).map(r => ({
    equipo:  r.tipo_servicio || '-',
    imei:    r.imei || '-',
    sim:     r.sim_serie || '-',
    modelo:  r.modelo_gps || '-',
  }));

  // Derive shared service / metodo
  const servicios = [...new Set((reportes || []).map(r => r.tipo_servicio).filter(Boolean))].join(', ') || '-';
  const metodo    = (reportes || []).map(r => r.forma_pago).find(Boolean) || '-';
  const folioList = (ordenes || []).join(', ') || '-';

  const tableBody = [
    [
      { text: '#',         style: 'th' },
      { text: 'Artículo',  style: 'th' },
      { text: 'IMEI',      style: 'th' },
      { text: 'SIM Serie', style: 'th' },
      { text: 'Modelo',    style: 'th' },
    ],
    ...dispositivos.map((d, i) => [
      { text: i + 1, alignment: 'center' },
      { text: d.equipo || '-' },
      { text: d.imei   || '-', fontSize: 7 },
      { text: d.sim    || '-', fontSize: 7 },
      { text: d.modelo || '-' },
    ]),
  ];

  const infoRows = [
    ['Cliente',          cliente    || '-'],
    ['Servicio',         servicios],
    ['Método de pago',   metodo],
    ['Órdenes',          folioList],
  ];

  const docDefinition = {
    pageMargins: [40, 40, 40, 40],
    content: [
      {
        columns: [
          { image: LOGO, width: 160, alignment: 'left' },
          {
            stack: [
              { text: 'NOTA DE VENTA',      style: 'title' },
              { text: folio,                style: 'folio' },
              { text: `Fecha: ${fechaStr}`, style: 'folioSub' },
              { text: 'Estatus: pagado',    style: 'folioSub' },
            ],
            alignment: 'right',
            width: '*',
          },
        ],
        margin: [0, 0, 0, 6],
      },
      {
        stack: [
          { text: 'COMERCIALIZADORA TECNOLOGICA DEL RIO', style: 'empresa' },
          { text: 'Fresno 1441  ·  44910 Guadalajara, Jalisco  ·  RFC: CTR1905206K5', style: 'sub' },
          { text: 'Tel: 3325373183  ·  gpsvector@gmail.com  ·  gpsubicacion.com',      style: 'sub' },
        ],
        margin: [0, 0, 0, 10],
      },
      { canvas: [{ type: 'line', x1: 0, y1: 0, x2: 515, y2: 0, lineWidth: 1, lineColor: '#334155' }], margin: [0, 0, 0, 10] },
      {
        columns: [
          {
            width: '*',
            table: {
              widths: [90, '*'],
              body: infoRows.map(([k, v]) => [
                { text: k, style: 'infoKey' },
                { text: v, style: 'infoVal' },
              ]),
            },
            layout: 'noBorders',
            margin: [0, 0, 20, 0],
          },
          {
            width: 'auto',
            stack: [
              { text: 'Total',                                                                                          style: 'totalLabel' },
              { text: `${_total.toLocaleString('es-MX', { minimumFractionDigits: 2 })} MXN`, style: 'totalValue' },
              { text: `${dispositivos.length} artículo${dispositivos.length !== 1 ? 's' : ''}`, style: 'totalSub' },
            ],
            alignment: 'right',
          },
        ],
        margin: [0, 0, 0, 12],
      },
      { text: 'Artículos', style: 'sectionTitle', margin: [0, 0, 0, 4] },
      dispositivos.length > 0
        ? {
            table: {
              headerRows: 1,
              widths: [18, 100, 105, 80, 80],
              body: tableBody,
            },
            layout: {
              fillColor: r => r === 0 ? '#334155' : r % 2 === 0 ? '#f1f5f9' : null,
              hLineWidth: () => 0.5,
              vLineWidth: () => 0.5,
              hLineColor: () => '#cbd5e1',
              vLineColor: () => '#cbd5e1',
            },
          }
        : { text: 'Sin artículos.', italics: true, color: '#64748b' },
      { canvas: [{ type: 'line', x1: 0, y1: 0, x2: 515, y2: 0, lineWidth: 0.5, lineColor: '#cbd5e1' }], margin: [0, 14, 0, 6] },
      { text: 'Condiciones', style: 'sectionTitle', margin: [0, 0, 0, 4] },
      {
        ul: [
          'Si requiere factura, el pago sería más IVA.',
          'Si adquiriste el GPS con recarga mensual, recarga 50 RECARGA SALDO TELCEL — no paquete.',
        ],
        style: 'nota',
      },
    ],
    styles: {
      empresa:      { fontSize: 10, bold: true, color: '#1e293b' },
      sub:          { fontSize: 7.5, color: '#64748b', margin: [0, 1, 0, 0] },
      title:        { fontSize: 18, bold: true, color: '#1e293b' },
      folio:        { fontSize: 11, color: '#334155', margin: [0, 2, 0, 0] },
      folioSub:     { fontSize: 8.5, color: '#64748b', margin: [0, 1, 0, 0] },
      sectionTitle: { fontSize: 10, bold: true, color: '#334155' },
      infoKey:      { fontSize: 9, bold: true, color: '#475569', margin: [0, 2, 8, 2] },
      infoVal:      { fontSize: 9, color: '#1e293b', margin: [0, 2, 0, 2] },
      totalLabel:   { fontSize: 10, bold: true, color: '#475569', margin: [0, 0, 0, 2] },
      totalValue:   { fontSize: 16, bold: true, color: '#1e293b', margin: [0, 0, 0, 2] },
      totalSub:     { fontSize: 8, color: '#64748b' },
      th:           { bold: true, color: '#ffffff', fontSize: 8.5, alignment: 'center' },
      nota:         { fontSize: 8, color: '#64748b', margin: [0, 2, 0, 2] },
    },
    defaultStyle: { fontSize: 9 },
  };

  if (abrirEnLinea) {
    pdfMake.createPdf(docDefinition).open();
  } else {
    pdfMake.createPdf(docDefinition).download(`${folio}.pdf`);
  }
}

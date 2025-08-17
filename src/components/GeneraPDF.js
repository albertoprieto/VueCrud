import pdfMake from "pdfmake/build/pdfmake";
import pdfFonts from "pdfmake/build/vfs_fonts";

async function getLogoBase64() {
  const res = await fetch('/src/assets/logoBase64.txt');
  return await res.text();
}

export class NotaVentaPdfService {
  static async generarPDF({ venta, cliente, articulos, empresa }) {
    if (!venta || !cliente || !articulos || articulos.length === 0) {
      window.toast && window.toast.add({ severity: 'error', summary: 'Datos incompletos', detail: 'No se puede generar el PDF porque faltan datos de la venta, cliente o artículos.', life: 5000 });
      return;
    }
    // Validación de campos clave
    const camposObligatorios = [
      venta.cliente_id,
      venta.vendedor,
      venta.fecha,
      venta.total,
      venta.subtotal,
      cliente.nombre,
      cliente.rfc
    ];
    if (camposObligatorios.some(c => !c)) {
      window.toast && window.toast.add({ severity: 'error', summary: 'Datos obligatorios faltantes', detail: 'Verifica que todos los campos obligatorios estén completos antes de generar el PDF.', life: 5000 });
      return;
    }
    // Validación de artículos
    for (const art of articulos) {
      if (!art.nombre || !art.cantidad || !art.precio_unitario) {
        window.toast && window.toast.add({ severity: 'error', summary: 'Artículo incompleto', detail: 'Todos los artículos deben tener nombre, cantidad y precio unitario.', life: 5000 });
        return;
      }
    }

    const logo = await getLogoBase64();

    const vendedor = venta.vendedor || '';
    const fechaOrden = venta.fecha || new Date().toLocaleDateString('es-MX');
    const folio = venta.folio || venta.id || '---';

    const body = [
      [
        { text: '#', style: 'tableHeader' },
        { text: 'Artículo & Descripción', style: 'tableHeader' },
        { text: 'Código del artículo', style: 'tableHeader' },
        { text: 'Código de unidad', style: 'tableHeader' },
        { text: 'Cant.', style: 'tableHeader' },
        { text: 'Tarifa', style: 'tableHeader' },
        { text: 'Importe', style: 'tableHeader' }
      ],
      ...articulos.map((a, idx) => [
        idx + 1,
        `${a.nombre || ''}${a.descripcion ? '\n' + a.descripcion : ''}`,
        a.sku || '',
        a.codigoUnidadSat || '',
        `${a.cantidad} ${a.unidad || ''}`,
        `$${Number(a.precio_unitario).toFixed(2)}`,
        `$${(Number(a.cantidad) * Number(a.precio_unitario)).toFixed(2)}`
      ])
    ];

    const subtotal = articulos.reduce((sum, a) => sum + (Number(a.cantidad) * Number(a.precio_unitario)), 0);
    const iva = 0;
    const total = subtotal + iva;

    const docDefinition = {
      content: [
        {
          columns: [
            [
              { image: logo, width: 225, alignment: 'left', margin: [0, 0, 0, 10] }
            ],
            []
          ]
        },
        {
          columns: [
            [
              { text: empresa.nombre, style: 'empresaHeader', alignment: 'left' },
              { text: empresa.direccion, style: 'empresaSubheader', alignment: 'left' },
              { text: `IVA ${empresa.rfc}`, style: 'empresaSubheader', alignment: 'left' },
              { text: `Régimen fiscal: ${empresa.regimen}`, style: 'empresaSubheader', alignment: 'left' },
              { text: empresa.telefono, style: 'empresaSubheader', alignment: 'left' },
              { text: empresa.correo, style: 'empresaSubheader', alignment: 'left' },
              { text: empresa.web, style: 'empresaSubheader', alignment: 'left' }
            ]
          ]
        },
        { text: '\n' },
        { text: 'Orden de servicio', style: 'title', alignment: 'center' },
        { text: `Orden de servicio nº ${folio}`, style: 'folio', alignment: 'center' },
        { text: '\n' },
        {
          columns: [
            [
              { text: 'Facturar a', style: 'sectionHeader' },
              { text: cliente.nombre || '', style: 'clienteLabel' },
              { text: cliente.direccion || '', style: 'clienteLabel' },
              { text: `RFC del receptor ${cliente.rfc || ''}`, style: 'clienteLabel' },
              { text: `Régimen fiscal: ${cliente.regimen_fiscal || ''}`, style: 'clienteLabel' }
            ],
            [
              { text: `Fecha del pedido : ${fechaOrden}`, style: 'clienteLabel', alignment: 'right' },
              { text: `Vendedor : ${vendedor}`, style: 'clienteLabel', alignment: 'right' }
            ]
          ]
        },
        { text: '\n' },
        {
          table: {
            headerRows: 1,
            widths: [18, 120, 60, 60, 40, 50, 60],
            body
          },
          layout: {
            fillColor: function (rowIndex) {
              return rowIndex === 0 ? '#ff4081' : (rowIndex % 2 === 0 ? '#f9f9f9' : null);
            }
          }
        },
        { text: '\n' },
        {
          columns: [
            { width: '*', text: '' },
            {
              width: 'auto',
              table: {
                body: [
                  [ { text: 'Subtotal', style: 'totalLabel' }, { text: `$${subtotal.toFixed(2)}`, style: 'totalValue' } ],
                  [ { text: 'Total', style: 'totalLabel' }, { text: `MXN$${total.toFixed(2)}`, style: 'totalValue' } ]
                ]
              },
              layout: 'noBorders'
            }
          ]
        },
        { text: '\n' },
        { text: 'Notas', style: 'sectionHeader' },
        { text: venta.notas_cliente || 'Si necesita factura el pago sería más IVA.', style: 'notas' },
        { text: '\n' },
        { text: 'Términos y condiciones', style: 'sectionHeader' },
        { text: venta.terminos_condiciones || 'Si el técnico acudió al domicilio o va de camino y se cancela el servicio se cobrará la vuelta en falso del técnico. El tiempo de traslado en el envió de los paquetes depende de la paquetería.', style: 'notas' }
      ],
      styles: {
        empresaHeader: { fontSize: 14, bold: true, color: '#444' },
        empresaSubheader: { fontSize: 9, color: '#666' },
        title: { fontSize: 16, bold: true, color: '#222', margin: [0, 10, 0, 10] },
        folio: { fontSize: 12, color: '#222', margin: [0, 2, 0, 2] },
        sectionHeader: { fontSize: 11, bold: true, color: '#444', margin: [0, 8, 0, 2] },
        clienteLabel: { fontSize: 10, color: '#333', margin: [0, 2, 0, 2] },
        tableHeader: { bold: true, fillColor: '#666', color: '#fff', fontSize: 10, alignment: 'center' },
        totalLabel: { bold: true, fontSize: 11, alignment: 'right', color: '#333' },
        totalValue: { bold: true, fontSize: 11, alignment: 'right', color: '#444' },
        notas: { fontSize: 9, color: '#444', margin: [0, 2, 0, 2] }
      },
      defaultStyle: {
        fontSize: 9
      }
    };

    pdfMake.createPdf(docDefinition).open();
  }
}
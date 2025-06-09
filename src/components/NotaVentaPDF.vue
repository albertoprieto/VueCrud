<template>
  <Button
    v-if="ventaRegistrada"
    label="PDF"
    icon="pi pi-file-pdf"
    @click="generarPDF"
    class="p-button-success mb-2"
  />
</template>

<script setup>
import { computed } from 'vue';
import Button from 'primevue/button';
import pdfMake from "pdfmake/build/pdfmake";
import pdfFonts from "pdfmake/build/vfs_fonts";

// Props
const props = defineProps({
  venta: { type: Object, required: true },
  cliente: { type: Object, required: true },
  articulos: { type: Array, required: true },
  empresa: { type: Object, default: () => ({}) },
  ventaRegistrada: { type: Boolean, default: false }
});

const fecha = computed(() => {
  if (!props.venta.fecha) return new Date().toLocaleDateString('es-MX');
  // Si viene con hora o con 'T', corta solo la fecha
  if (typeof props.venta.fecha === 'string' && (props.venta.fecha.includes(' ') || props.venta.fecha.includes('T')))
    return props.venta.fecha.split(/[ T]/)[0];
  // Si es Date, formatea
  if (props.venta.fecha instanceof Date) return props.venta.fecha.toISOString().slice(0, 10);
  return props.venta.fecha;
});

async function getLogoBase64() {
  const res = await fetch('/logoBase64.txt');
  return await res.text();
}


async function generarPDF() {

  // Logo SVG como base64 (puedes usar un loader o util para base64 si lo necesitas)
  // Aquí solo se referencia la ruta relativa, pdfMake requiere base64 para imágenes SVG
  // Puedes usar un loader o convertir el SVG a base64 y pegarlo aquí si lo deseas
  // Ejemplo: const logo = 'data:image/svg+xml;base64,...';
  const logo = await getLogoBase64();
      
  // Empresa
  const empresa = {
    nombre: 'COMERCIALIZADORA TECNOLOGICA DEL RIO',
    direccion: 'Mezquite 1272\n44900 Guadalajara Jalisco\nMexico',
    rfc: 'CTR1905206K5',
    regimen: '626 - Régimen Simplificado de Confianza',
    telefono: '3325373183',
    correo: 'gpsvector@gmail.com',
    web: 'gpsubicacion.com'
  };

  // Cliente
  const cliente = props.cliente || {};
  const vendedor = props.venta.vendedor || '';
  const fechaOrden = fecha.value;
  const folio = props.venta.folio
  ? props.venta.folio
  : props.venta.id
    ? `SO-${String(props.venta.id).padStart(5, '0')}`
    : 'SO-00000';

  // Tabla de artículos
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
    ...props.articulos.map((a, idx) => [
      idx + 1,
      `${a.nombre || ''}${a.descripcion ? '\n' + a.descripcion : ''}`,
      a.sku || '',
      a.codigoUnidadSat || '',
      `${a.cantidad} ${a.unidad || ''}`,
      `$${Number(a.precio_unitario).toFixed(2)}`,
      `$${(Number(a.cantidad) * Number(a.precio_unitario)).toFixed(2)}`
    ])
  ];

  // Totales
  const subtotal = props.articulos.reduce((sum, a) => sum + (Number(a.cantidad) * Number(a.precio_unitario)), 0);
  const iva = 0; // Zero Rate (0%)
  const total = subtotal + iva;

  const docDefinition = {
    content: [
      {
        columns: [
          [
            { image: logo, width: 225, alignment: 'left', margin: [0, 0, 0, 10] } // 2.5x más grande (90*2.5=225)
          ],
          [
            // Datos de empresa ahora van a la izquierda, así que esta columna queda vacía
          ]
        ]
      },
      {
        // Nueva fila: datos de empresa a la izquierda
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
      { text: 'Orden de venta', style: 'title', alignment: 'center' },
      { text: `${folio}`, style: 'folio', alignment: 'center' },
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
      { text: props.venta.notas_cliente || 'Si necesita factura el pago sería más IVA.', style: 'notas' },
      { text: '\n' },
      { text: 'Términos y condiciones', style: 'sectionHeader' },
      { text: props.venta.terminos_condiciones || 'Si el técnico acudió al domicilio o va de camino y se cancela el servicio se cobrará la vuelta en falso del técnico. El tiempo de traslado en el envió de los paquetes depende de la paquetería.', style: 'notas' }
    ],
    styles: {
      empresaHeader: { fontSize: 14, bold: true, color: '#444' }, // gris oscuro
      empresaSubheader: { fontSize: 9, color: '#666' }, // gris medio
      title: { fontSize: 16, bold: true, color: '#222', margin: [0, 10, 0, 10] }, // gris muy oscuro
      folio: { fontSize: 12, color: '#222', margin: [0, 2, 0, 2] },
      sectionHeader: { fontSize: 11, bold: true, color: '#444', margin: [0, 8, 0, 2] }, // gris oscuro
      clienteLabel: { fontSize: 10, color: '#333', margin: [0, 2, 0, 2] },
      tableHeader: { bold: true, fillColor: '#666', color: '#fff', fontSize: 10, alignment: 'center' }, // gris medio
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
</script>
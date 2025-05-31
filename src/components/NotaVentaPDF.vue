<template>
  <Button
    v-if="ventaRegistrada"
    label="Descargar Nota de Venta (PDF)"
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

const props = defineProps({
  venta: { type: Object, required: true },
  cliente: { type: Object, required: true },
  articulos: { type: Array, required: true },
  empresa: { type: Object, default: () => ({}) },
  ventaRegistrada: { type: Boolean, default: false }
});

const fecha = computed(() => {
  return props.venta.fecha ? props.venta.fecha.split('T')[0] : new Date().toLocaleDateString();
});

// Calcula el total real sumando subtotales de los artículos
const totalCalculado = computed(() =>
  props.articulos.reduce((sum, a) => sum + (Number(a.cantidad) * Number(a.precio_unitario)), 0)
);

// Extrae info adicional del cliente
const telefonos = Array.isArray(props.cliente.telefonos) ? props.cliente.telefonos.join(', ') : (props.cliente.telefono || '');
const correo = props.cliente.correo || '';
const plataformas = Array.isArray(props.cliente.plataformas) ? props.cliente.plataformas.join(', ') : (props.cliente.plataforma || '');
const usuarios = Array.isArray(props.cliente.usuarios) ? props.cliente.usuarios.join(', ') : (props.cliente.usuario || '');

function generarPDF() {
  const body = [
    [
      { text: 'SKU', style: 'tableHeader' },
      { text: 'Cantidad', style: 'tableHeader' },
      { text: 'Precio Unitario', style: 'tableHeader' },
      { text: 'Subtotal', style: 'tableHeader' },
      { text: 'IMEI', style: 'tableHeader' }
    ],
    ...props.articulos.map(a => [
      a.sku || '',
      a.cantidad,
      `$${Number(a.precio_unitario).toFixed(2)}`,
      `$${(Number(a.cantidad) * Number(a.precio_unitario)).toFixed(2)}`,
      a.imei || ''
    ])
  ];

  const docDefinition = {
    content: [
      {
        columns: [
          [
            { text: props.empresa.nombre || 'Mi Empresa S.A. de C.V.', style: 'header' },
            { text: props.empresa.direccion || 'Dirección de la empresa', style: 'subheader' },
            { text: props.empresa.rfc ? `RFC: ${props.empresa.rfc}` : '', style: 'subheader' }
          ],
          [
            // { image: 'https://i.imgur.com/4M7IWwP.png', width: 80, alignment: 'right', margin: [0, 0, 0, 10] } // Logo opcional
          ]
        ]
      },
      { canvas: [ { type: 'line', x1: 0, y1: 0, x2: 515, y2: 0, lineWidth: 1, lineColor: '#ff4081' } ] },
      { text: 'NOTA DE VENTA', style: 'title', margin: [0, 10, 0, 10] },
      {
        columns: [
          [
            { text: `Folio: ${props.venta.id || '---'}`, style: 'folio' },
            { text: `Fecha: ${fecha.value}`, style: 'folio' }
          ],
          [
            { text: `Observaciones: ${props.venta.observaciones || '-'}`, style: 'observaciones', alignment: 'right' }
          ]
        ]
      },
      { text: '\n' },
      {
        style: 'clienteBox',
        table: {
          widths: ['*', '*', '*', '*'],
          body: [
            [
              { text: `Cliente: ${props.cliente.nombre || ''}`, style: 'clienteLabel' },
              { text: `Teléfonos: ${telefonos}`, style: 'clienteLabel' },
              { text: `Correo: ${correo}`, style: 'clienteLabel' },
              { text: `Plataformas: ${plataformas}`, style: 'clienteLabel' }
            ],
            [
              { text: `Usuarios: ${usuarios}`, style: 'clienteLabel', colSpan: 4 }, {}, {}, {}
            ]
          ]
        },
        layout: 'noBorders'
      },
      { text: '\n' },
      {
        table: {
          headerRows: 1,
          widths: [70, 40, 70, 70, '*'],
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
                [
                  { text: 'Total:', style: 'totalLabel' },
                  { text: `$${Number(totalCalculado.value).toFixed(2)}`, style: 'totalValue' }
                ]
              ]
            },
            layout: 'noBorders'
          }
        ]
      },
      { text: '\n' },
      { text: 'Gracias por su compra.', style: 'footer' }
    ],
    styles: {
      header: { fontSize: 20, bold: true, color: '#ff4081', alignment: 'left', margin: [0, 0, 0, 2] },
      subheader: { fontSize: 10, alignment: 'left', color: '#888', margin: [0, 0, 0, 2] },
      title: { fontSize: 16, bold: true, alignment: 'center', color: '#333', margin: [0, 10, 0, 10] },
      tableHeader: { bold: true, fillColor: '#ff4081', color: '#fff', fontSize: 11, alignment: 'center' },
      clienteBox: { margin: [0, 0, 0, 10] },
      clienteLabel: { fontSize: 10, color: '#333', margin: [0, 2, 0, 2] },
      folio: { fontSize: 11, color: '#333', margin: [0, 2, 0, 2] },
      observaciones: { fontSize: 10, italics: true, color: '#666', margin: [0, 2, 0, 2] },
      totalLabel: { bold: true, fontSize: 13, alignment: 'right', color: '#333' },
      totalValue: { bold: true, fontSize: 13, alignment: 'right', color: '#ff4081' },
      footer: { italics: true, alignment: 'center', margin: [0, 20, 0, 0], color: '#888' }
    },
    defaultStyle: {
      fontSize: 10
    }
  };

  pdfMake.createPdf(docDefinition).open();
}
</script>
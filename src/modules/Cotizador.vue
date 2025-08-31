<script setup>
import { ref, computed, watch, onMounted } from 'vue';
import InputText from 'primevue/inputtext';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import Dropdown from 'primevue/dropdown';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import { useVentas } from '@/composables/useVentas.js';
import { addQuotation, enviarCotizacionWhatsapp } from '@/services/quotationService';
import { useToast } from 'primevue/usetoast';
import { useRouter } from 'vue-router';
import { getTodosArticulos } from '@/services/articulosService';
import { getUsuarios } from '@/services/usuariosService';
import { getLogoBase64 } from '@/components/GeneraPDF.js';

const toast = useToast();
const showDialog = ref(false);
const showNuevoClienteDialog = ref(false);
const showSendDialog = ref(false);
const showConfirmSendDialog = ref(false);
const cotizacionGeneradaNumero = ref(null);
const router = useRouter();
const cotizacion = ref({
  id: null,
  cliente_id: null,
  cliente: '',
  fecha: new Date().toISOString().slice(0, 10),
  vendedor: null,
  descuento: 0,
  observaciones: '',
  articulos: [],
  monto: 0,
  status: 'Pendiente'
});
const {
  clientes,
  onArticuloChange,
  validateCantidad,
} = useVentas();

const articulos = ref([]);
const vendedores = ref([]);

onMounted(async () => {
  articulos.value = await getTodosArticulos();
  const usuarios = await getUsuarios();
  vendedores.value = usuarios.filter(u => u.perfil === 'Vendedor');
});

// Paso 1: Agregar artículo vacío y permitir selección
const addArticuloCotizacion = () => {
  cotizacion.value.articulos.push({
    articulo_id: null,
    cantidad: 1,
    precio_unitario: 0
  });
};

// Paso 2: Cuando se selecciona un artículo, autocompletar precio_unitario
function handleArticuloChange(articulo_id, row) {
  const articulo = articulos.value.find(a => a.id === articulo_id);
  if (articulo) {
    row.precio_unitario = Number(articulo.precioVenta) || 0;
    row.cantidad = 1;
  }
}

// Paso 3: Validar cantidad (si quieres lógica extra, usa validateCantidad)
// Nota: En cotizaciones NO se valida stock, solo se asegura que la cantidad sea un entero >= 1
function handleCantidadInput(row) {
  if (!row.cantidad || isNaN(row.cantidad) || row.cantidad < 1) {
    row.cantidad = 1;
  } else {
    row.cantidad = Math.floor(Number(row.cantidad));
  }
}

// Paso 4: Eliminar artículo
const removeArticuloCotizacion = (idx) => {
  cotizacion.value.articulos.splice(idx, 1);
};

const subtotal = computed(() =>
  cotizacion.value.articulos.reduce((sum, a) => sum + ((Number(a.cantidad) || 0) * (Number(a.precio_unitario) || 0)), 0)
);
const descuentoMonto = computed(() =>
  subtotal.value * ((Number(cotizacion.value.descuento) || 0) / 100)
);
const ivaMonto = computed(() =>
  subtotal.value * 0.16
);
const total = computed(() =>
  subtotal.value - descuentoMonto.value + ivaMonto.value
);

watch(
  () => [cotizacion.value.articulos, cotizacion.value.descuento],
  () => {
    cotizacion.value.monto = total.value;
  },
  { deep: true }
);

const showPDFDialog = ref(false);
const pdfDocDefinition = ref(null);

// Validación de campos obligatorios
const cotizacionInvalida = computed(() => {
  if (!cotizacion.value.cliente_id || !cotizacion.value.vendedor || !cotizacion.value.fecha) return true;
  if (!cotizacion.value.articulos.length) return true;
  // Algún artículo sin seleccionar o cantidad inválida
  return cotizacion.value.articulos.some(a => !a.articulo_id || !a.cantidad || a.cantidad < 1);
});

const guardarCotizacion = async () => {
  if (!cotizacion.value.cliente_id || cotizacion.value.articulos.length === 0) {
    toast.add({ severity: 'warn', summary: 'Campos obligatorios', detail: 'Selecciona cliente y al menos un artículo.', life: 4000 });
    return;
  }
  try {
    const logo = await getLogoBase64();
    const empresa = {
      nombre: 'COMERCIALIZADORA TECNOLOGICA DEL RIO',
      direccion: 'Fresno 1441 44910 Guadalajara, Jalisco, México',
      rfc: 'CTR1905206K5',
      regimen: '626 - Régimen Simplificado de Confianza',
      telefono: '3325373183',
      correo: 'gpsvector@gmail.com',
      web: 'gpsubicacion.com'
    };

    const articulosObj = {};
    cotizacion.value.articulos.forEach((a, idx) => {
      articulosObj[idx] = a;
    });
    const clienteObj = clientes.value.find(c => c.id === cotizacion.value.cliente_id);
    const cotizacionCreada = await addQuotation({
      ...cotizacion.value,
      cliente: clienteObj ? clienteObj.nombre : '',
      articulos: articulosObj,
      descripcion: cotizacion.value.descripcion || '',
      status: 'Pendiente'
    });

    const articulosPDF = cotizacion.value.articulos.map((a, idx) => {
      const art = articulos.value.find(x => x.id === a.articulo_id) || {};
      return {
        ...a,
        nombre: art.nombre,
        descripcion: art.descripcion,
        unidad: art.unidad
      };
    });
    const body = [
      [
        { text: '#', style: 'tableHeader' },
        { text: 'Artículo', style: 'tableHeader' },
        { text: 'Descripción', style: 'tableHeader' },
        { text: 'Cant.', style: 'tableHeader' },
        { text: 'Tarifa', style: 'tableHeader' },
        { text: 'Importe', style: 'tableHeader' }
      ],
      ...articulosPDF.map((a, idx) => [
        idx + 1,
        `${a.nombre || ''}`,
        a.descripcion || '',
        `${a.cantidad} ${a.unidad || ''}`,
        `$${Number(a.precio_unitario).toFixed(2)}`,
        `$${(Number(a.cantidad) * Number(a.precio_unitario)).toFixed(2)}`
      ])
    ];
    const subtotal = articulosPDF.reduce((sum, a) => sum + (Number(a.cantidad) * Number(a.precio_unitario)), 0);
    const descuentoMonto = subtotal * ((Number(cotizacion.value.descuento) || 0) / 100);
    const iva = subtotal * 0.16;
    const total = subtotal - descuentoMonto + iva;
    const folio = cotizacionCreada.folio
      ? cotizacionCreada.folio
      : cotizacionCreada.id
        ? `COTIZACION-${String(cotizacionCreada.id).padStart(5, '0')}`
        : 'COTIZACION-00000';
    const docDefinition = {
      content: [
        ...((logo && typeof logo === 'string' && logo.length > 0)
          ? [{ columns: [[{ image: logo, width: 225, alignment: 'left', margin: [0, 0, 0, 10] }], []] }]
          : []),
        {
          columns: [
            [
              { text: empresa.nombre, style: 'empresaHeader', alignment: 'left' },
              { text: empresa.direccion, style: 'empresaSubheader', alignment: 'left' },
              { text: empresa.rfc, style: 'empresaSubheader', alignment: 'left' },
              { text: `Régimen fiscal: ${empresa.regimen}`, style: 'empresaSubheader', alignment: 'left' },
              { text: empresa.telefono, style: 'empresaSubheader', alignment: 'left' },
              { text: empresa.correo, style: 'empresaSubheader', alignment: 'left' },
              { text: empresa.web, style: 'empresaSubheader', alignment: 'left' }
            ]
          ]
        },
        { text: '\n' },
        { text: 'Cotización', style: 'title', alignment: 'center' },
        { text: '\n' },
        {
          columns: [
            [
              { text: 'Facturar a', style: 'sectionHeader' },
              { text: clienteObj.nombre || '', style: 'clienteLabel' },
              { text: clienteObj.direccion || '', style: 'clienteLabel' },
              { text: `RFC del receptor ${clienteObj.rfc || ''}`, style: 'clienteLabel' },
              { text: `Régimen fiscal: ${clienteObj.regimen_fiscal || ''}`, style: 'clienteLabel' }
            ],
            [
              { text: `Fecha : ${cotizacion.value.fecha}`, style: 'clienteLabel', alignment: 'right' },
              { text: `Vendedor : ${cotizacion.value.vendedor || ''}`, style: 'clienteLabel', alignment: 'right' }
            ]
          ]
        },
        { text: '\n' },
        {
          table: {
            headerRows: 1,
            widths: [18, 120, 120, 40, 50, 60],
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
                  [ { text: 'IVA (16%)', style: 'totalLabel' }, { text: `$${iva.toFixed(2)}`, style: 'totalValue' } ],
                  [ { text: 'Total', style: 'totalLabel' }, { text: `MXN$${total.toFixed(2)}`, style: 'totalValue' } ]
                ]
              },
              layout: 'noBorders'
            }
          ]
        },
        { text: '\n' },
        { text: 'Notas', style: 'sectionHeader' },
        { text: 'Si no necesitas factura y tu pago es mediante transferencia podemos descontar el IVA.', style: 'notas' },
        { text: '\n' },
        { text: 'Términos y condiciones', style: 'sectionHeader' },
        { text: 'Si el técnico acudió al domicilio o va de camino y se cancela el servicio se cobrará la vuelta en falso del técnico. El tiempo de traslado en el envió de los paquetes depende de la paquetería.', style: 'notas' }
      ],
      styles: {
        empresaHeader: { fontSize: 14, bold: true, color: '#444' },
        empresaSubheader: { fontSize: 9, color: '#666' },
        title: { fontSize: 16, bold: true, color: '#222', margin: [0, 10, 0, 10] },
        sectionHeader: { fontSize: 11, bold: true, color: '#444', margin: [0, 8, 0, 2] },
        clienteLabel: { fontSize: 10, color: '#333', margin: [0, 2, 0, 2] },
        tableHeader: { bold: true, fillColor: '#666', color: '#fff', fontSize: 10, alignment: 'center' },
        totalLabel: { bold: true, fontSize: 11, alignment: 'right', color: '#333' },
        totalValue: { bold: true, fontSize: 11, alignment: 'right', color: '#444' },
        notas: { fontSize: 9, color: '#444', margin: [0, 2, 0, 2] },
        folio: { fontSize: 13, bold: true, color: '#222', margin: [0, 0, 0, 10] }
      },
      defaultStyle: {
        fontSize: 9
      }
    };
    pdfDocDefinition.value = docDefinition;
    showPDFDialog.value = true;
    cotizacion.value = {
      id: null,
      cliente_id: null,
      cliente: '',
      fecha: new Date().toISOString().slice(0, 10),
      vendedor: null,
      descuento: 0,
      observaciones: '',
      articulos: [],
      monto: 0,
      status: 'Pendiente'
    };
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Error al registrar la cotización', life: 4000 });
  }
};

const descargarPDFCotizacion = async () => {
  if (!pdfDocDefinition.value) return;
  let pdfMake;
  if (window.pdfMake) {
    pdfMake = window.pdfMake;
  } else {
    pdfMake = (await import('pdfmake/build/pdfmake')).default;
    await import('pdfmake/build/vfs_fonts');
  }
  pdfMake.createPdf(pdfDocDefinition.value).download(`${cotizacionGeneradaNumero.value}.pdf`);
  showPDFDialog.value = false;
};

const closeDialog = () => {
  showDialog.value = false;
};

// --- Correos de cliente ("Emiliano Zapata") ---
const cotizacionEmail = ref('');
const clienteEmails = computed(() => {
  const cliente = clientes.value.find(c => c.id === cotizacion.value.cliente_id);
  return cliente && cliente.correo ? cliente.correo : '';
});
watch(
  () => cotizacion.value.cliente_id,
  () => {
    cotizacionEmail.value = clienteEmails.value || '';
  }
);

// --- Teléfonos de cliente ---
const cotizacionTelefono = ref('');
const clienteTelefonos = computed(() => {
  const cliente = clientes.value.find(c => c.id === cotizacion.value.cliente_id);
  return cliente && cliente.telefonos ? cliente.telefonos : [];
});
watch(
  () => cotizacion.value.cliente_id,
  () => {
    cotizacionTelefono.value = clienteTelefonos.value[0] || '';
  }
);

const generarPDFCotizacion = async () => {
  if (!cotizacion.value.cliente_id || cotizacion.value.articulos.length === 0) {
    toast.add({ severity: 'warn', summary: 'Campos obligatorios', detail: 'Selecciona cliente y al menos un artículo.', life: 4000 });
    return;
  }
  const clienteObj = clientes.value.find(c => c.id === cotizacion.value.cliente_id) || {};

  const articulosPDF = cotizacion.value.articulos.map((a, idx) => {
    const art = articulos.value.find(x => x.id === a.articulo_id) || {};
    return {
      ...a,
      nombre: art.nombre,
      descripcion: art.descripcion,
      unidad: art.unidad
    };
  });

  const body = [
    [
      { text: '#', style: 'tableHeader' },
      { text: 'Artículo', style: 'tableHeader' },
      { text: 'Descripción', style: 'tableHeader' },
      { text: 'Cant.', style: 'tableHeader' },
      { text: 'Tarifa', style: 'tableHeader' },
      { text: 'Importe', style: 'tableHeader' }
    ],
    ...articulosPDF.map((a, idx) => [
      idx + 1,
      `${a.nombre || ''}`,
      a.descripcion || '',
      `${a.cantidad} ${a.unidad || ''}`,
      `$${Number(a.precio_unitario).toFixed(2)}`,
      `$${(Number(a.cantidad) * Number(a.precio_unitario)).toFixed(2)}`
    ])
  ];

  const subtotal = articulosPDF.reduce((sum, a) => sum + (Number(a.cantidad) * Number(a.precio_unitario)), 0);
  const descuentoMonto = subtotal * ((Number(cotizacion.value.descuento) || 0) / 100);
  const iva = subtotal * 0.16;
  const total = subtotal - descuentoMonto + iva;

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
            { text: 'COMERCIALIZADORA TECNOLOGICA DEL RIO', style: 'empresaHeader', alignment: 'left' },
            { text: 'Fresno 1441 44910 Guadalajara, Jalisco, México', style: 'empresaSubheader', alignment: 'left' },
            { text: 'IVA CTR1905206K5', style: 'empresaSubheader', alignment: 'left' },
            { text: 'Régimen fiscal: 626 - Régimen Simplificado de Confianza', style: 'empresaSubheader', alignment: 'left' },
            { text: '3325373183', style: 'empresaSubheader', alignment: 'left' },
            { text: 'gpsvector@gmail.com', style: 'empresaSubheader', alignment: 'left' },
            { text: 'gpsubicacion.com', style: 'empresaSubheader', alignment: 'left' }
          ]
        ]
      },
      { text: '\n' },
      { text: 'Cotización', style: 'title', alignment: 'center' },
      { text: '\n' },
      {
        columns: [
          [
            { text: 'Facturar a', style: 'sectionHeader' },
            { text: clienteObj.nombre || '', style: 'clienteLabel' },
            { text: clienteObj.direccion || '', style: 'clienteLabel' },
            { text: `RFC del receptor ${clienteObj.rfc || ''}`, style: 'clienteLabel' },
            { text: `Régimen fiscal: ${clienteObj.regimen_fiscal || ''}`, style: 'clienteLabel' }
          ],
          [
            { text: `Fecha : ${cotizacion.value.fecha}`, style: 'clienteLabel', alignment: 'right' },
            { text: `Vendedor : ${cotizacion.value.vendedor || ''}`, style: 'clienteLabel', alignment: 'right' }
          ]
        ]
      },
      { text: '\n' },
      {
        table: {
          headerRows: 1,
          widths: [18, 120, 120, 40, 50, 60],
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
                [ { text: 'IVA (16%)', style: 'totalLabel' }, { text: `$${iva.toFixed(2)}`, style: 'totalValue' } ],
                [ { text: 'Total', style: 'totalLabel' }, { text: `MXN$${total.toFixed(2)}`, style: 'totalValue' } ]
              ]
            },
            layout: 'noBorders'
          }
        ]
      },
      { text: '\n' },
      { text: 'Notas', style: 'sectionHeader' },
      { text: 'Si no necesitas factura y tu pago es mediante transferencia podemos descontar el IVA.', style: 'notas' },
      { text: '\n' },
      { text: 'Términos y condiciones', style: 'sectionHeader' },
      { text: 'Si el técnico acudió al domicilio o va de camino y se cancela el servicio se cobrará la vuelta en falso del técnico. El tiempo de traslado en el envió de los paquetes depende de la paquetería.', style: 'notas' }
    ],
    styles: {
      empresaHeader: { fontSize: 14, bold: true, color: '#444' },
      empresaSubheader: { fontSize: 9, color: '#666' },
      title: { fontSize: 16, bold: true, color: '#222', margin: [0, 10, 0, 10] },
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

  if (window.pdfMake) {
    window.pdfMake.createPdf(docDefinition).open();
  } else {
    const pdfMake = (await import("pdfmake/build/pdfmake")).default;
    await import("pdfmake/build/vfs_fonts");
    pdfMake.createPdf(docDefinition).open();
  }

  cotizacionGeneradaNumero.value = cotizacion.value.folio || cotizacion.value.id || 'N/A';
  showSendDialog.value = true;
};

const sendingWhatsapp = ref(false);

const enviarCotizacionAlCliente = async () => {
  sendingWhatsapp.value = true;
  try {
    const clienteObj = clientes.value.find(c => c.id === cotizacion.value.cliente_id) || {};
    const articulosTexto = cotizacion.value.articulos.map((a, idx) => {
      const art = articulos.value.find(x => x.id === a.articulo_id) || {};
      return `${idx + 1}. ${art.nombre || ''} x${a.cantidad} - $${Number(a.precio_unitario).toFixed(2)}`;
    }).join('\n');

    const mensaje = 
      `*Cotización #${cotizacionGeneradaNumero.value}*\n` +
      `Cliente: ${clienteObj.nombre}\n` +
      `Fecha: ${cotizacion.value.fecha}\n` +
      `Vendedor: ${cotizacion.value.vendedor || ''}\n\n` +
      `*Artículos:*\n${articulosTexto}\n\n` +
      `Subtotal: $${subtotal.value.toFixed(2)}\n` +
      `Descuento: ${cotizacion.value.descuento || 0}% ($${descuentoMonto.value.toFixed(2)})\n` +
      `IVA (16%): $${ivaMonto.value.toFixed(2)}\n` +
      `Total: $${total.value.toFixed(2)}\n\n` +
      `Observaciones: ${cotizacion.value.observaciones || '-'}`;

    await enviarCotizacionWhatsapp({
      cotizacion_id: cotizacion.value.id,
      cliente_id: cotizacion.value.cliente_id,
      telefono: cotizacionTelefono.value,
      mensaje
    });

    toast.add({ severity: 'success', summary: 'Cotización enviada', detail: 'La cotización fue registrada como enviada por WhatsApp.', life: 4000 });
    showSendDialog.value = false;
    showConfirmSendDialog.value = true;
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo registrar el envío de la cotización.', life: 4000 });
    showSendDialog.value = false;
  } finally {
    sendingWhatsapp.value = false;
  }
};

const closeConfirmSendDialog = () => {
  showConfirmSendDialog.value = false;
};

const irAClientes = () => {
  router.push('/clientes');
};
</script>

<template>
  <div class="cotizador-container">
    <h2 class="cotizador-title">Cotizador</h2>
    <div class="cotizador-card">
      <form @submit.prevent="guardarCotizacion">
        <div class="form-row">
          <div class="form-group">
            <label>Cliente</label>
            <Dropdown v-model="cotizacion.cliente_id" :options="clientes" optionLabel="nombre" optionValue="id" 
              placeholder="Selecciona un cliente" class="w-full" :class="{'p-invalid': !cotizacion.cliente_id}" />
          </div>
          <div class="form-group">
            <label>Nuevo</label>
            <Button label="Nuevo Cliente" icon="pi pi-plus" class="w-full p-button-secondary" 
              @click="showNuevoClienteDialog = true" />
          </div>
          <Dialog v-model:visible="showNuevoClienteDialog" header="Agregar Cliente" :modal="true" class="mobile-dialog">
            <p>¿Deseas agregar un nuevo cliente? Serás redirigido a la pantalla de clientes.</p>
            <template #footer>
              <Button label="Cancelar" class="mobile-button" @click="showNuevoClienteDialog = false" />
              <Button label="Aceptar" class="p-button-success mobile-button" @click="irAClientes" />
            </template>
          </Dialog>
          <div class="form-group">
            <label>Email</label>
            <InputText v-model="cotizacionEmail" class="w-full mobile-input" disabled />
          </div>
          <div class="form-group">
            <label>Fecha</label>
            <InputText v-model="cotizacion.fecha" type="date" class="w-full mobile-input" :class="{'p-invalid': !cotizacion.fecha}" />
          </div>
        </div>
        
        <div class="form-row">
          <div class="form-group">
            <label>Vendedor</label>
            <Dropdown v-model="cotizacion.vendedor" :options="vendedores" optionLabel="username" optionValue="username" 
              placeholder="Selecciona vendedor" class="w-full mobile-dropdown" :class="{'p-invalid': !cotizacion.vendedor}" />
          </div>
          <div class="form-group">
            <label>Descuento (%)</label>
            <InputText v-model.number="cotizacion.descuento" type="number" min="0" max="100" 
              class="w-full mobile-input" :class="{'p-invalid': cotizacion.descuento === null || cotizacion.descuento === undefined}" />
          </div>
        </div>
        
        <h3 class="section-title">Artículos</h3>
        <div class="table-wrapper">
          <DataTable :value="cotizacion.articulos" class="mb-2 mobile-table" scrollable scrollDirection="horizontal">
            <Column field="articulo_id" header="Artículo" :style="{ minWidth: '150px' }">
              <template #body="slotProps">
                <Dropdown
                  v-model="slotProps.data.articulo_id"
                  :options="articulos"
                  optionLabel="sku"
                  optionValue="id"
                  placeholder="Seleccione SKU"
                  class="w-full mobile-dropdown"
                  filter
                  showClear
                  @change="handleArticuloChange(slotProps.data.articulo_id, slotProps.data)"
                  :class="{'p-invalid': !slotProps.data.articulo_id}"
                />
              </template>
            </Column>
            <Column field="cantidad" header="Cantidad" :style="{ minWidth: '100px' }">
              <template #body="slotProps">
                <InputText
                  type="number"
                  v-model.number="slotProps.data.cantidad"
                  min="1"
                  class="w-full mobile-input"
                  :disabled="!slotProps.data.articulo_id"
                  @input="handleCantidadInput(slotProps.data)"
                  :class="{'p-invalid': !slotProps.data.cantidad || slotProps.data.cantidad < 1}"
                />
              </template>
            </Column>
            <Column field="precio_unitario" header="P. Unitario" :style="{ minWidth: '120px' }">
              <template #body="slotProps">
                <InputText
                  type="number"
                  v-model.number="slotProps.data.precio_unitario"
                  min="0"
                  step="0.01"
                  class="w-full mobile-input"
                  :disabled="true"
                />
              </template>
            </Column>
            <Column header="Subtotal" :style="{ minWidth: '100px' }">
              <template #body="slotProps">
                <span class="mobile-text">
                  {{ (Number(slotProps.data.cantidad) || 0) * (Number(slotProps.data.precio_unitario) || 0).toFixed(2) }}
                </span>
              </template>
            </Column>
            <Column header="Acciones" :style="{ minWidth: '80px' }">
              <template #body="slotProps">
                <Button icon="pi pi-trash" class="p-button-danger p-button-sm mobile-icon-button" 
                  @click="removeArticuloCotizacion(slotProps.index)" :disabled="!slotProps.data.articulo_id" />
              </template>
            </Column>
          </DataTable>
        </div>
        
        <Button label="Agregar Artículo" icon="pi pi-plus" class="mb-2 mobile-button full-width-button" 
          @click="addArticuloCotizacion" />

        <div class="mb-2 acciones-footer mobile-summary">
          <div>
            <div><strong>Subtotal:</strong> ${{ subtotal.toFixed(2) }}</div>
            <div><strong>Descuento:</strong> {{ cotizacion.descuento || 0 }}% (${{ descuentoMonto.toFixed(2) }})</div>
            <div><strong>IVA (16%):</strong> ${{ ivaMonto.toFixed(2) }}</div>
            <div><strong>Total:</strong> ${{ total.toFixed(2) }}</div>
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label>Observaciones</label>
            <InputText v-model="cotizacion.observaciones" class="w-full mobile-input" />
          </div>
        </div>

        <div class="actions-right mobile-actions">
          <Button
            label="Guardar Cotización"
            icon="pi pi-save"
            class="p-button-success mobile-button full-width-button"
            type="submit"
            :disabled="cotizacionInvalida"
          />
        </div>
      </form>
      
      <Dialog v-model:visible="showDialog" header="Cotización Guardada" :modal="true" class="mobile-dialog">
        <p>La cotización ha sido guardada exitosamente.</p>
        <Button label="Aceptar" icon="pi pi-check" class="mobile-button" @click="closeDialog" />
      </Dialog>
      
      <Dialog v-model:visible="showSendDialog" header="Enviar Cotización" :modal="true" class="mobile-dialog">
        <p>La cotización con folio <strong>{{ cotizacionGeneradaNumero }}</strong> ha sido generada.</p>
        <p>¿Deseas enviar esta cotización al cliente por WhatsApp?</p>
        <p><strong>WhatsApp:</strong> {{ cotizacionTelefono }}</p>
        <template #footer>
          <Button label="Cancelar" class="mobile-button" 
            @click="() => { showSendDialog = false; router.push('/dashboard'); }" />
          <Button label="Enviar WhatsApp" class="p-button-success mobile-button" 
            @click="enviarCotizacionAlCliente" :loading="sendingWhatsapp" />
        </template>
      </Dialog>
      
      <Dialog v-model:visible="sendingWhatsapp" header="Enviando WhatsApp" :modal="true" :closable="false" 
        class="mobile-dialog">
        <div class="dialog-content">
          <span>Enviando cotización por WhatsApp...</span>
        </div>
      </Dialog>
      
      <Dialog v-model:visible="showConfirmSendDialog" header="Envío exitoso" :modal="true" class="mobile-dialog">
        <p>La cotización fue enviada correctamente al cliente.</p>
        <Button label="Aceptar" icon="pi pi-check" class="mobile-button" @click="closeConfirmSendDialog" />
      </Dialog>

      <Dialog v-model:visible="showPDFDialog" header="Cotización Guardada" :modal="true" class="mobile-dialog">
        <p>La cotización ha sido guardada exitosamente.</p>
        <p>¿Deseas descargar el PDF generado?</p>
        <template #footer>
          <Button label="Cancelar" class="mobile-button" @click="showPDFDialog = false" />
          <Button label="Descargar PDF" class="p-button-success mobile-button" @click="descargarPDFCotizacion" />
        </template>
      </Dialog>

      <Dialog v-model:visible="showPDFDialog" header="Cotización generada" :modal="true" class="mobile-dialog">
        <p>La cotización fue generada correctamente.</p>
        <Button label="Descargar PDF" icon="pi pi-file-pdf" class="p-button-success mobile-button" @click="descargarPDFCotizacion" />
      </Dialog>
    </div>
  </div>
</template>


<style scoped>
.cotizador-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem;
  width: 100%;
  box-sizing: border-box;
}

.cotizador-title {
  font-size: 1.5rem;
  margin-bottom: 1rem;
}

.cotizador-card {
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.form-row {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1rem;
}

.form-group {
  flex: 1;
  min-width: 200px;
}

.section-title {
  margin: 1.5rem 0 1rem;
  font-size: 1.2rem;
}

.table-wrapper {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  margin-bottom: 1rem;
}

.acciones-footer {
  padding: 1rem;
  border-radius: 6px;
}

.actions-right {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}

.full-width-button {
  width: 100%;
}

/* Estilos para móviles */
@media (max-width: 768px) {
  .cotizador-container {
    padding: 0.5rem;
  }
  
  .cotizador-card {
    padding: 1rem;
  }
  
  .cotizador-title {
    font-size: 1.3rem;
  }
  
  .section-title {
    font-size: 1.1rem;
  }
  
  .form-group {
    min-width: 100%;
  }
  
  .mobile-dropdown {
    font-size: 0.9rem;
  }
  
  .mobile-input {
    font-size: 0.9rem;
    padding: 0.5rem;
  }
  
  .mobile-button {
    font-size: 0.9rem;
    padding: 0.5rem;
  }
  
  .mobile-button-group {
    align-self: center;
  }
  
  .mobile-icon-button {
    padding: 0.3rem;
  }
  
  .mobile-text {
    font-size: 0.9rem;
  }
  
  .mobile-table {
    font-size: 0.85rem;
  }
  
  .mobile-summary div {
    font-size: 0.9rem;
  }
  
  .mobile-actions {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .mobile-dialog {
    width: 95vw;
    max-width: 95vw;
  }
  
  .dialog-content {
    padding: 1rem;
    text-align: center;
  }
}

@media (max-width: 480px) {
  .cotizador-title {
    font-size: 1.2rem;
  }
  
  .section-title {
    font-size: 1rem;
  }
  
  .mobile-dropdown, 
  .mobile-input, 
  .mobile-button, 
  .mobile-text {
    font-size: 0.8rem;
  }
  
  .mobile-table {
    font-size: 0.75rem;
  }
}
</style>
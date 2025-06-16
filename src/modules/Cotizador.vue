<script setup>
import { ref, computed, watch, onMounted } from 'vue';
import InputText from 'primevue/inputtext';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import Dropdown from 'primevue/dropdown';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import { useVentas } from '@/composables/useVentas.js';
import { addQuotation } from '@/services/quotationService';
import { useToast } from 'primevue/usetoast';
import { useRouter } from 'vue-router';
import { getTodosArticulos } from '@/services/articulosService';
import { getUsuarios } from '@/services/usuariosService';
import { NotaVentaPdfService } from '@/components/GeneraPDF.js';
import { CotizacionMailService } from '@/services/cotizacionMailService.js';

const toast = useToast();
const showDialog = ref(false);
const showNuevoClienteDialog = ref(false);
const showSendDialog = ref(false);
const cotizacionGeneradaNumero = ref(null);
const router = useRouter();
const cotizacion = ref({
  cliente_id: null,
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
const total = computed(() =>
  subtotal.value - descuentoMonto.value
);

const articulosConSubtotal = computed(() =>
  cotizacion.value.articulos.map(a => ({
    ...a,
    subtotal: (Number(a.cantidad) || 0) * (Number(a.precio_unitario) || 0)
  }))
);

watch(
  () => [cotizacion.value.articulos, cotizacion.value.descuento],
  () => {
    cotizacion.value.monto = total.value;
  },
  { deep: true }
);

const guardarCotizacion = async () => {
  if (!cotizacion.value.cliente_id || cotizacion.value.articulos.length === 0) {
    toast.add({ severity: 'warn', summary: 'Campos obligatorios', detail: 'Selecciona cliente y al menos un artículo.', life: 4000 });
    return;
  }
  try {
    await addQuotation({
      ...cotizacion.value,
      articulos: cotizacion.value.articulos,
      status: 'Pendiente'
    });
    showDialog.value = true;
    cotizacion.value = {
      cliente_id: null,
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

const generarPDFCotizacion = async () => {
  if (!cotizacion.value.cliente_id || cotizacion.value.articulos.length === 0) {
    toast.add({ severity: 'warn', summary: 'Campos obligatorios', detail: 'Selecciona cliente y al menos un artículo.', life: 4000 });
    return;
  }
  const clienteObj = clientes.value.find(c => c.id === cotizacion.value.cliente_id) || {};
  const logo = ""; // Pega aquí tu base64

  // Prepara los artículos para el PDF (nombre para cliente, sku para control)
  const articulosPDF = cotizacion.value.articulos.map((a, idx) => {
    const art = articulos.value.find(x => x.id === a.articulo_id) || {};
    return {
      ...a,
      sku: art.sku,
      nombre: art.nombre,
      descripcion: art.descripcion,
      unidad: art.unidad,
      codigoUnidadSat: art.codigoUnidadSat
    };
  });

  // Tabla de artículos
  const body = [
    [
      { text: '#', style: 'tableHeader' },
      { text: 'Artículo', style: 'tableHeader' },
      { text: 'Código del artículo', style: 'tableHeader' },
      { text: 'Código de unidad', style: 'tableHeader' },
      { text: 'Cant.', style: 'tableHeader' },
      { text: 'Tarifa', style: 'tableHeader' },
      { text: 'Importe', style: 'tableHeader' }
    ],
    ...articulosPDF.map((a, idx) => [
      idx + 1,
      `${a.nombre || ''}`,
      a.sku || '',
      a.codigoUnidadSat || '',
      `${a.cantidad} ${a.unidad || ''}`,
      `$${Number(a.precio_unitario).toFixed(2)}`,
      `$${(Number(a.cantidad) * Number(a.precio_unitario)).toFixed(2)}`
    ])
  ];

  const subtotal = articulosPDF.reduce((sum, a) => sum + (Number(a.cantidad) * Number(a.precio_unitario)), 0);
  const descuentoMonto = subtotal * ((Number(cotizacion.value.descuento) || 0) / 100);
  const total = subtotal - descuentoMonto;

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
            { text: 'Mezquite 1272\n44900 Guadalajara Jalisco\nMexico', style: 'empresaSubheader', alignment: 'left' },
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
      { text: cotizacion.value.observaciones || 'Si necesita factura el pago sería más IVA.', style: 'notas' },
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

  // @ts-ignore
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

const enviarCotizacionAlCliente = async () => {
  try {
    await CotizacionMailService.enviarCotizacion({
      ...cotizacion.value,
      cliente_email: cotizacionEmail.value
    });
    toast.add({ severity: 'success', summary: 'Correo enviado', detail: 'La cotización fue enviada al cliente.', life: 4000 });
    showSendDialog.value = false;
    router.push('/dashboard');
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo enviar la cotización.', life: 4000 });
    showSendDialog.value = false;
    router.push('/dashboard');
  }
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
            <Dropdown v-model="cotizacion.cliente_id" :options="clientes" optionLabel="nombre" optionValue="id" placeholder="Selecciona un cliente" class="w-full" />
          </div>
          <div class="form-group" style="align-self: end;">
            <Button label="Nuevo Cliente" icon="pi pi-plus" class="p-button-success" @click="showNuevoClienteDialog = true" />
          </div>
          <Dialog v-model:visible="showNuevoClienteDialog" header="Agregar Cliente" :modal="true">
            <p>¿Deseas agregar un nuevo cliente? Serás redirigido a la pantalla de clientes.</p>
            <template #footer>
              <Button label="Cancelar" @click="showNuevoClienteDialog = false" />
              <Button label="Aceptar" class="p-button-success" @click="irAClientes" />
            </template>
          </Dialog>
          <div class="form-group">
            <label>Email</label>
            <InputText v-model="cotizacionEmail" class="w-full" disabled />
          </div>
          <div class="form-group">
            <label>Fecha</label>
            <InputText v-model="cotizacion.fecha" type="date" class="w-full" />
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>Vendedor</label>
            <Dropdown v-model="cotizacion.vendedor" :options="vendedores" optionLabel="username" optionValue="username" placeholder="Selecciona vendedor" class="w-full" />
          </div>
          <div class="form-group">
            <label>Descuento (%)</label>
            <InputText v-model.number="cotizacion.descuento" type="number" min="0" max="100" class="w-full" />
          </div>
        </div>
        <h3>Artículos</h3>
        <DataTable :value="cotizacion.articulos" class="mb-2">
          <Column field="articulo_id" header="Artículo">
            <template #body="slotProps">
              <Dropdown
                v-model="slotProps.data.articulo_id"
                :options="articulos"
                optionLabel="sku"
                optionValue="id"
                placeholder="Seleccione SKU"
                class="w-full"
                filter
                showClear
                @change="handleArticuloChange(slotProps.data.articulo_id, slotProps.data)"
              />
            </template>
          </Column>
          <Column field="cantidad" header="Cantidad">
            <template #body="slotProps">
              <InputText
                type="number"
                v-model.number="slotProps.data.cantidad"
                min="1"
                class="w-full"
                :disabled="!slotProps.data.articulo_id"
                @input="handleCantidadInput(slotProps.data)"
              />
            </template>
          </Column>
          <Column field="precio_unitario" header="Precio Unitario">
            <template #body="slotProps">
              <InputText
                type="number"
                v-model.number="slotProps.data.precio_unitario"
                min="0"
                step="0.01"
                class="w-full"
                :disabled="true"
              />
            </template>
          </Column>
          <Column header="Subtotal">
            <template #body="slotProps">
              <span>
                {{ ((Number(slotProps.data.cantidad) || 0) * (Number(slotProps.data.precio_unitario) || 0)).toFixed(2) }}
              </span>
            </template>
          </Column>
          <Column header="Acciones">
            <template #body="slotProps">
              <Button icon="pi pi-trash" class="p-button-danger p-button-sm" @click="removeArticuloCotizacion(slotProps.index)" :disabled="!slotProps.data.articulo_id" />
            </template>
          </Column>
        </DataTable>
        <Button label="Agregar Artículo" icon="pi pi-plus" class="mb-2" @click="addArticuloCotizacion" />

        <div class="mb-2 acciones-footer">
          <div>
            <div><strong>Subtotal:</strong> ${{ subtotal.toFixed(2) }}</div>
            <div><strong>Descuento:</strong> {{ cotizacion.descuento || 0 }}% (${{ descuentoMonto.toFixed(2) }})</div>
            <div><strong>Total:</strong> ${{ total.toFixed(2) }}</div>
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label>Observaciones</label>
            <InputText v-model="cotizacion.observaciones" class="w-full" />
          </div>
        </div>

        <div class="actions-right">
          <Button label="Guardar Cotización" icon="pi pi-save" type="submit" />
          <Button
            label="Generar PDF"
            icon="pi pi-file-pdf"
            class="ml-2"
            :style="{ background: '#f8bbd0', borderColor: '#f8bbd0', color: '#6d214f' }"
            @click="generarPDFCotizacion"
          />
        </div>
      </form>
      <Dialog v-model:visible="showDialog" header="Cotización Guardada" :closable="false" :modal="true">
        <p>La cotización ha sido guardada exitosamente.</p>
        <Button label="Aceptar" icon="pi pi-check" @click="closeDialog" />
      </Dialog>
      <Dialog v-model:visible="showSendDialog" header="Enviar Cotización" :closable="false" :modal="true">
        <p>La cotización con folio <strong>{{ cotizacionGeneradaNumero }}</strong> ha sido generada.</p>
        <p>¿Deseas enviar esta cotización al cliente por correo electrónico?</p>
        <p><strong>Email:</strong> {{ cotizacionEmail }}</p>
        <template #footer>
          <Button label="Cancelar" @click="() => { showSendDialog = false; router.push('/dashboard'); }" />
          <Button label="Enviar" class="p-button-success" @click="enviarCotizacionAlCliente" />
        </template>
      </Dialog>
    </div>
  </div>
</template>
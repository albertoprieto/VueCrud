<template>
  <div class="consultar-cotizaciones">
    <h2 class="consultar-cotizaciones-title">Consultar Cotizaciones</h2>
    <div class="consultar-cotizaciones-card">
      <!-- Toolbar de filtros avanzados -->
      <div class="filters-advanced">
        <div class="filters-row">
          <InputText v-model="globalQuery" placeholder="Buscar: cliente, folio, teléfono, vendedor, observaciones…" class="w-full" />
        </div>
        <div class="filters-row grid-2">
          <div class="filters-field">
            <label>Desde</label>
            <Calendar v-model="dateFrom" dateFormat="yy-mm-dd" showIcon iconDisplay="input" placeholder="YYYY-MM-DD" />
          </div>
          <div class="filters-field">
            <label>Hasta</label>
            <Calendar v-model="dateTo" dateFormat="yy-mm-dd" showIcon iconDisplay="input" placeholder="YYYY-MM-DD" />
          </div>
        </div>
        <div class="filters-row grid-3">
          <div class="filters-field">
            <label>Estado</label>
            <MultiSelect v-model="statusSelected" :options="statusOptions" placeholder="Todos" class="w-full" />
          </div>
          <div class="filters-field">
            <label>Vendedor</label>
            <Dropdown v-model="vendedorSelected" :options="vendedores" optionLabel="username" optionValue="username" placeholder="Todos" class="w-full" />
          </div>
          <div class="filters-field">
            <label>Monto (min - max)</label>
            <div class="range-inline">
              <InputNumber v-model="montoMin" mode="currency" currency="MXN" locale="es-MX" :min="0" inputClass="w-8" />
              <span class="range-sep">—</span>
              <InputNumber v-model="montoMax" mode="currency" currency="MXN" locale="es-MX" :min="0" inputClass="w-8" />
            </div>
          </div>
        </div>
        <div class="filters-actions">
          <div class="left">
            <Button :label="viewGrouped ? 'Vista agrupada' : 'Vista lista'" icon="pi pi-table" class="p-button-text" />
            <Button :label="viewGrouped ? 'Cambiar a lista' : 'Cambiar a agrupada'" icon="pi pi-exchange" class="p-button-text" @click="viewGrouped = !viewGrouped" />
          </div>
          <div class="right">
            <span class="results">{{ resultadosCount }} resultados</span>
            <Button label="Limpiar" icon="pi pi-filter-slash" class="p-button-text" @click="clearFilters" />
          </div>
        </div>
      </div>

      <!-- Vista lista plana -->
      <DataTable v-if="!viewGrouped" :value="filteredQuotationsList" responsiveLayout="scroll" :paginator="true" :rows="10" :rowsPerPageOptions="[10,20,50]" dataKey="id" :sortField="'fecha'" :sortOrder="-1">
        <Column field="folio" header="Folio" sortable />
        <Column field="fecha" header="Fecha" sortable />
        <Column field="cliente" header="Cliente" sortable />
        <Column field="vendedor" header="Vendedor" sortable />
        <Column field="status" header="Estado">
          <template #body="row">
            <span class="chip" :class="{
              'chip-pendiente': row.data.status === 'Pendiente',
              'chip-agendado': row.data.status === 'Agendado',
              'chip-autorizada': row.data.status === 'Autorizada'
            }">{{ row.data.status }}</span>
          </template>
        </Column>
        <Column field="monto" header="Monto" sortable>
          <template #body="row">${{ Number(row.data.monto).toLocaleString('es-MX', { minimumFractionDigits: 2 }) }}</template>
        </Column>
        <Column header="Acciones">
          <template #body="row">
            <Button label="Teléfonos" icon="pi pi-phone" class="p-button-text"
              @click="showTelefonosDialog(row.data.telefonos)"
              :disabled="!row.data.telefonos || !row.data.telefonos.length" />
            <Button label="Detalle" icon="pi pi-eye" class="p-button-text" @click="showDetalleDialog(row.data)" />
            <Button label="Editar" icon="pi pi-pencil" class="p-button-text" @click="showEditarDialog(row.data)" />
            <Button label="PDF" icon="pi pi-file-pdf" class="p-button-text" @click="generatePDF(row.data)" />
          </template>
        </Column>
      </DataTable>

      <!-- Vista agrupada por cliente (original) -->
      <DataTable v-else :value="cotizacionesFiltradas" dataKey="cliente_id" rowExpansion v-model:expandedRows="expandedRows" responsiveLayout="scroll">
        <Column type="expander" style="width: 3em" />
        <Column field="cliente" header="Cliente" />
        <Column header="Teléfonos">
          <template #body="slotProps">
            <Button label="Teléfonos" icon="pi pi-phone" class="p-button-text"
              @click="showTelefonosDialog(slotProps.data.telefonos)"
              :disabled="!slotProps.data.telefonos || !slotProps.data.telefonos.length" />
          </template>
        </Column>
        <Column header="N° Cotizaciones">
          <template #body="slotProps">{{ slotProps.data.cotizaciones.length }}</template>
        </Column>
        <Column header="Acciones">
          <template #body="slotProps">
            <Button label="Ver Cotizaciones" icon="pi pi-list" class="p-button-text" @click="showCotizacionesDialogForCliente(slotProps.data)" />
          </template>
        </Column>
      </DataTable>
    </div>


    <!-- Dialog para mostrar los teléfonos -->
    <Dialog v-model:visible="telefonosDialogVisible" header="Teléfonos del Cliente" :modal="true" :closable="true">
      <ul v-if="telefonosDialogList && telefonosDialogList.length">
        <li v-for="(tel, idx) in telefonosDialogList" :key="idx">
          Teléfono {{ idx + 1 }}: {{ tel }}
        </li>
      </ul>
      <span v-else>No hay teléfonos disponibles.</span>
    </Dialog>

    <!-- Dialogo para ver todas las cotizaciones del cliente -->
    <Dialog :visible="cotizacionesDialogVisible" header="Cotizaciones del Cliente" :modal="true" :closable="false">
      <DataTable :value="cotizacionesDelCliente" responsiveLayout="scroll">
        <Column field="fecha" header="Fecha" />
        <Column field="monto" header="Monto">
          <template #body="row">
            ${{ Number(row.data.monto).toLocaleString('es-MX', { minimumFractionDigits: 2 }) }}
          </template>
        </Column>
        <Column field="status" header="Estado">
          <template #body="row">
            <span class="chip" :class="{
              'chip-pendiente': row.data.status === 'Pendiente',
              'chip-agendado': row.data.status === 'Agendado',
              'chip-autorizada': row.data.status === 'Autorizada'
            }">
              {{ row.data.status }}
            </span>
          </template>
        </Column>
        <Column header="Acciones">
          <template #body="row">
            <Button label="Ver Detalle" icon="pi pi-eye" class="p-button-text" @click="showDetalleDialog(row.data)" />
            <Button label="Editar" icon="pi pi-pencil" class="p-button-text" @click="showEditarDialog(row.data)" />
            <Button label="PDF" icon="pi pi-file-pdf" class="p-button-text" @click="generatePDF(row.data)" />
          </template>
        </Column>
      </DataTable>
      <Button label="Cerrar" class="mt-3" @click="closeCotizacionesDialog" />
    </Dialog>

    <!-- Modal para detalle de cotización -->
    <Dialog :visible="detalleDialogVisible" header="Detalle de Cotización" :modal="true" :closable="false"
      class="detalle-cotizacion-dialog">
      <div v-if="selectedCotizacion">
        <div class="detalle-cotizacion-info">
          <div><strong>Cliente:</strong> {{ selectedCotizacion.cliente }}</div>
          <div><strong>Fecha:</strong> {{ selectedCotizacion.fecha }}</div>
          <div><strong>Vendedor:</strong> {{ selectedCotizacion.vendedor || '-' }}</div>
          <div><strong>Descuento:</strong> {{ selectedCotizacion.descuento || 0 }}%</div>
          <div><strong>Monto:</strong> ${{ Number(selectedCotizacion.monto).toLocaleString('es-MX', {
            minimumFractionDigits:
            2 }) }}</div>
          <div><strong>Status:</strong> {{ selectedCotizacion.status }}</div>
          <div><strong>Observaciones:</strong> {{ selectedCotizacion.observaciones || '-' }}</div>
        </div>
        <h4>Artículos</h4>
        <table class="detalle-cotizacion-table">
          <thead>
            <tr>
              <th>#</th>
              <th>Artículo</th>
              <th>Cantidad</th>
              <th>Precio Unitario</th>
              <th>Subtotal</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(art, idx) in articulosCotizacion" :key="idx">
              <td>{{ idx + 1 }}</td>
              <td>{{ art.nombre || art.articulo_id }}</td>
              <td>{{ art.cantidad }}</td>
              <td>${{ Number(art.precio_unitario).toFixed(2) }}</td>
              <td>${{ (Number(art.cantidad) * Number(art.precio_unitario)).toFixed(2) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <Button label="Cerrar" class="mt-3" @click="closeDetalleDialog" />
    </Dialog>

    <!-- Modal para editar cotización -->
    <Dialog v-model:visible="editarDialogVisible" header="Editar Cotización" :modal="true" :closable="false">
      <form @submit.prevent="confirmUpdate">
        <div class="form-row">
          <div class="form-group">
            <label>Cliente</label>
            <Dropdown v-model="selectedCotizacion.cliente_id" :options="clientes" optionLabel="nombre" optionValue="id"
              placeholder="Selecciona un cliente" class="w-full" :disabled="true" />
          </div>
          <div class="form-group">
            <label>Fecha</label>
            <InputText v-model="selectedCotizacion.fecha" type="date" class="w-full" />
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>Vendedor</label>
            <Dropdown v-model="selectedCotizacion.vendedor" :options="vendedores" optionLabel="username"
              optionValue="username" placeholder="Selecciona vendedor" class="w-full" />
          </div>
          <div class="form-group">
            <label>Descuento (%)</label>
            <InputText v-model.number="selectedCotizacion.descuento" type="number" min="0" max="100" class="w-full" />
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>Observaciones</label>
            <InputText v-model="selectedCotizacion.observaciones" class="w-full" />
          </div>
        </div>
        <h4>Artículos</h4>
        <DataTable :value="selectedCotizacion.articulos" class="mb-2">
          <Column field="articulo_id" header="Artículo">
            <template #body="slotProps">
              <Dropdown v-model="slotProps.data.articulo_id" :options="articulos" optionLabel="sku" optionValue="id"
                placeholder="Seleccione SKU" class="w-full" filter showClear
                @change="handleArticuloChange(slotProps.data.articulo_id, slotProps.data)" />
            </template>
          </Column>
          <Column field="cantidad" header="Cantidad">
            <template #body="slotProps">
              <InputText type="number" v-model.number="slotProps.data.cantidad" min="1" class="w-full"
                @input="handleCantidadInput(slotProps.data)" />
            </template>
          </Column>
          <Column field="precio_unitario" header="Precio Unitario">
            <template #body="slotProps">
              <InputText type="number" v-model.number="slotProps.data.precio_unitario" min="0" step="0.01"
                class="w-full" :disabled="true" />
            </template>
          </Column>
          <Column header="Acciones">
            <template #body="slotProps">
              <Button icon="pi pi-trash" class="p-button-danger p-button-sm"
                @click="removeArticuloEdit(slotProps.index)" />
            </template>
          </Column>
        </DataTable>
        <div class="form-row">
          <div class="form-group">
            <label>Monto total</label>
            <InputText
              :value="Number(selectedCotizacion?.monto || 0).toLocaleString('es-MX', { minimumFractionDigits: 2 })"
              class="w-full" disabled />
          </div>
        </div>
        <Button label="Agregar Artículo" icon="pi pi-plus" class="mb-2" @click="addArticuloEdit" />
        <Button label="Guardar Cambios" icon="pi pi-save" class="mt-2" type="submit" />
      </form>
      <Button label="Cerrar" class="mt-3" @click="editarDialogVisible = false" />
    </Dialog>

    <!-- Dialogo de confirmación de actualización -->
    <Dialog v-model:visible="showConfirmUpdateDialog" header="Confirmar actualización" :modal="true" :closable="false">
      <div style="padding:1.5rem; text-align:center;">
        <span>¿Deseas guardar los cambios de la cotización?</span>
      </div>
      <div class="modal-actions">
        <Button label="Cancelar" icon="pi pi-times" class="p-button-secondary"
          @click="showConfirmUpdateDialog = false" />
        <Button label="Guardar" icon="pi pi-save" class="p-button-success" @click="saveEditCotizacion" />
      </div>
    </Dialog>

    <!-- Dialogo de éxito tras actualizar -->
    <Dialog v-model:visible="showSuccessDialog" header="Éxito" :modal="true" :closable="false">
      <div style="padding:1.5rem; text-align:center;">
        <span>La cotización fue actualizada correctamente.</span>
      </div>
      <Button label="Aceptar" icon="pi pi-check" @click="closeSuccessDialog" class="mt-3" />
    </Dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue';
import { getQuotations, updateQuotation } from '@/services/quotationService';
import { getClientes } from '@/services/clientesService';
import { getTodosArticulos } from '@/services/articulosService';
import { getUsuarios } from '@/services/usuariosService';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import Dropdown from 'primevue/dropdown';
import Calendar from 'primevue/calendar';
import MultiSelect from 'primevue/multiselect';
import InputNumber from 'primevue/inputnumber';
import { useToast } from 'primevue/usetoast';

const toast = useToast();

const quotations = ref([]);
const clientes = ref([]);
const vendedores = ref([]);
const groupedQuotations = ref([]);
const expandedRows = ref([]);
const articulos = ref([]);
const cotizacionesDelCliente = ref([]);
const cotizacionesDialogVisible = ref(false);
const detalleDialogVisible = ref(false);
const editarDialogVisible = ref(false);
const selectedCotizacion = ref(null);
const articulosCotizacion = ref([]);
const showConfirmUpdateDialog = ref(false);
const showSuccessDialog = ref(false);

// Estado filtros avanzados
const viewGrouped = ref(false);
const globalQuery = ref('');
const dateFrom = ref(null);
const dateTo = ref(null);
const statusOptions = ['Pendiente', 'Agendado', 'Autorizada'];
const statusSelected = ref([]);
const vendedorSelected = ref(null);
const montoMin = ref(null);
const montoMax = ref(null);

// Filtros anteriores mantenidos para la vista agrupada
const filtroNombre = ref('');
const filtroTelefono = ref('');
const filtroCotizacion = ref('');
const cotizacionesFiltradas = computed(() => {
  return groupedQuotations.value.filter(q => {
    const nombreOk = !filtroNombre.value || q.cliente.toLowerCase().includes(filtroNombre.value.toLowerCase());
    const telefonoOk = !filtroTelefono.value || (q.telefonos && q.telefonos.some(tel => tel.includes(filtroTelefono.value)));
    const cotizacionOk = !filtroCotizacion.value || (q.cotizaciones && q.cotizaciones.some(c => String(c.id).includes(filtroCotizacion.value)));
    return nombreOk && telefonoOk && cotizacionOk;
  });
});

async function reloadQuotations() {
  const [cotizaciones, clientesList, articulosList, usuarios] = await Promise.all([
    getQuotations(),
    getClientes(),
    getTodosArticulos(),
    getUsuarios()
  ]);
  clientes.value = clientesList;
  articulos.value = articulosList;
  vendedores.value = usuarios.filter(u => u.perfil === 'Vendedor');
  const map = {};
  cotizaciones.forEach(c => {
    const clienteObj = clientesList.find(cl => cl.id === c.cliente_id);
    const nombre = clienteObj ? clienteObj.nombre : `ID:${c.cliente_id}`;
    const telefonos = clienteObj?.telefonos || [];
    if (!map[c.cliente_id]) {
      map[c.cliente_id] = {
        cliente_id: c.cliente_id,
        cliente: nombre,
        telefonos,
        cotizaciones: []
      };
    }
    map[c.cliente_id].cotizaciones.push({
      ...c,
    cliente: nombre,
    telefonos
    });
  });
  groupedQuotations.value = Object.values(map);
  quotations.value = groupedQuotations.value.flatMap(g => g.cotizaciones);
}

onMounted(reloadQuotations);

function showCotizacionesDialogForCliente(clienteGroup) {
  cotizacionesDelCliente.value = clienteGroup.cotizaciones;
  cotizacionesDialogVisible.value = true;
}
function closeCotizacionesDialog() {
  cotizacionesDialogVisible.value = false;
}

function showDetalleDialog(cotizacion) {
  console.log(cotizacion);

  selectedCotizacion.value = cotizacion;
  try {
    const articulosObj = typeof cotizacion.articulos === 'string'
      ? JSON.parse(cotizacion.articulos)
      : cotizacion.articulos;
    articulosCotizacion.value = Object.values(articulosObj).map(a => ({
      ...a,
      nombre: articulos.value.find(art => art.id === a.articulo_id)?.nombre || a.articulo_id
    }));
  } catch {
    articulosCotizacion.value = [];
  }
  detalleDialogVisible.value = true;
  cotizacionesDialogVisible.value = false;
}
function closeDetalleDialog() {
  detalleDialogVisible.value = false;
}

function showEditarDialog(cotizacion) {
  selectedCotizacion.value = { ...cotizacion };
  if (typeof selectedCotizacion.value.articulos === 'string') {
    try {
      selectedCotizacion.value.articulos = Object.values(JSON.parse(selectedCotizacion.value.articulos));
    } catch {
      selectedCotizacion.value.articulos = [];
    }
  }
  editarDialogVisible.value = true;
  cotizacionesDialogVisible.value = false;
}

function handleArticuloChange(articulo_id, row) {
  const articulo = articulos.value.find(a => a.id === articulo_id);
  if (articulo) {
    row.precio_unitario = Number(articulo.precioVenta) || 0;
    row.cantidad = 1;
  }
}

function handleCantidadInput(row) {
  if (!row.cantidad || isNaN(row.cantidad) || row.cantidad < 1) {
    row.cantidad = 1;
  } else {
    row.cantidad = Math.floor(Number(row.cantidad));
  }
}

function addArticuloEdit() {
  if (!selectedCotizacion.value.articulos) selectedCotizacion.value.articulos = [];
  selectedCotizacion.value.articulos.push({
    articulo_id: null,
    cantidad: 1,
    precio_unitario: 0
  });
}

function removeArticuloEdit(idx) {
  selectedCotizacion.value.articulos.splice(idx, 1);
}

function confirmUpdate() {
  showConfirmUpdateDialog.value = true;
}
const telefonosDialogVisible = ref(false);
const telefonosDialogList = ref([]);
function showTelefonosDialog(telefonos) {
  telefonosDialogList.value = telefonos || [];
  telefonosDialogVisible.value = true;
}
async function saveEditCotizacion() {
  showConfirmUpdateDialog.value = false;
  let articulosObj = {};
  (selectedCotizacion.value.articulos || []).forEach((a, idx) => {
    articulosObj[idx] = a;
  });
  try {
    await updateQuotation(selectedCotizacion.value.id, {
      ...selectedCotizacion.value,
      articulos: articulosObj
    });
    toast.add({ severity: 'success', summary: 'Cotización actualizada', detail: 'Los cambios fueron guardados.', life: 3000 });
    showSuccessDialog.value = true;
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo actualizar la cotización.', life: 4000 });
  }
}

function closeSuccessDialog() {
  showSuccessDialog.value = false;
  editarDialogVisible.value = false;
  reloadQuotations();
}

function generatePDF(cotizacion) {
  let articulosArr = [];
  try {
    const articulosObj = typeof cotizacion.articulos === 'string'
      ? JSON.parse(cotizacion.articulos)
      : cotizacion.articulos;
    articulosArr = Object.values(articulosObj).map(a => {
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
  } catch {
    articulosArr = [];
  }

  const clienteObj = clientes.value.find(c => c.id === cotizacion.cliente_id) || {};

  const empresa = {
    nombre: 'COMERCIALIZADORA TECNOLOGICA DEL RIO',
    direccion: 'Fresno 1441 44910 Guadalajara, Jalisco, México',
    rfc: 'CTR1905206K5',
    regimen: '626 - Régimen Simplificado de Confianza',
    telefono: '3325373183',
    correo: 'gpsvector@gmail.com',
    web: 'gpsubicacion.com'
  };

  const logo = '';

  // Folio/número de cotización igual que en Cotizador.vue
  const folio = cotizacion.folio
    ? cotizacion.folio
    : cotizacion.id
      ? `COTIZACION-${String(cotizacion.id).padStart(5, '0')}`
      : 'COTIZACION-00000';

  // Calcular subtotal y total antes de usar en docDefinition
  const subtotal = articulosArr.reduce((sum, a) => sum + (Number(a.cantidad) * Number(a.precio_unitario)), 0);
  const descuentoMonto = subtotal * ((Number(cotizacion.descuento) || 0) / 100);
  const iva = subtotal * 0.16;
  const total = subtotal - descuentoMonto + iva;

  // body debe estar definido antes de usarlo en docDefinition
  const body = [
    [
      { text: '#', style: 'tableHeader' },
      { text: 'Artículo & Descripción', style: 'tableHeader' },
      { text: 'Cant.', style: 'tableHeader' },
      { text: 'Tarifa', style: 'tableHeader' },
      { text: 'Importe', style: 'tableHeader' }
    ],
    ...articulosArr.map((a, idx) => [
      idx + 1,
      `${a.nombre || ''}\n${a.descripcion || ''}`,
      `${a.cantidad}`,
      `$${Number(a.precio_unitario).toFixed(2)}`,
      `$${(Number(a.cantidad) * Number(a.precio_unitario)).toFixed(2)}`
    ])
  ];

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
            { text: `${empresa.rfc}`, style: 'empresaSubheader', alignment: 'left' },
            { text: `Régimen fiscal: ${empresa.regimen}`, style: 'empresaSubheader', alignment: 'left' },
            { text: empresa.telefono, style: 'empresaSubheader', alignment: 'left' },
            { text: empresa.correo, style: 'empresaSubheader', alignment: 'left' },
            { text: empresa.web, style: 'empresaSubheader', alignment: 'left' }
          ]
        ]
      },
      { text: '\n' },
      { text: 'Cotización', style: 'title', alignment: 'center' },
      { text: folio, style: 'folio', alignment: 'center' },
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
            { text: `Fecha : ${cotizacion.fecha}`, style: 'clienteLabel', alignment: 'right' },
            { text: `Vendedor : ${cotizacion.vendedor || ''}`, style: 'clienteLabel', alignment: 'right' },
            { text: `Teléfono cliente: ${clienteObj.telefonos && clienteObj.telefonos.length ? clienteObj.telefonos[0] : '-'}` , style: 'clienteLabel', alignment: 'right' }
          ]
        ]
      },
      { text: '\n' },
      {
        table: {
          headerRows: 1,
          widths: [18, '*', 40, 50, 60],
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
                [{ text: 'Subtotal', style: 'totalLabel' }, { text: `$${subtotal.toFixed(2)}`, style: 'totalValue' }],
                [{ text: 'Descuento', style: 'totalLabel' }, { text: `$${descuentoMonto.toFixed(2)}`, style: 'totalValue' }],
                [{ text: 'IVA (16%)', style: 'totalLabel' }, { text: `$${iva.toFixed(2)}`, style: 'totalValue' }],
                [{ text: 'Total', style: 'totalLabel' }, { text: `MXN$${total.toFixed(2)}`, style: 'totalValue' }]
              ]
            },
            layout: 'noBorders'
          }
        ]
      },
      { text: '\n' },
      { text: 'Notas', style: 'sectionHeader' },
      { text: cotizacion.observaciones , style: 'notas' },
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

  // @ts-ignore
  if (window.pdfMake) {
    window.pdfMake.createPdf(docDefinition).open();
  } else {
    import("pdfmake/build/pdfmake").then(pdfMakeModule => {
      import("pdfmake/build/vfs_fonts").then(() => {
        pdfMakeModule.default.createPdf(docDefinition).open();
      });
    });
  }
}

// Vista lista: filtros combinados
const filteredQuotationsList = computed(() => {
  const q = (globalQuery.value || '').toLowerCase().trim();
  const from = dateFrom.value ? new Date(dateFrom.value) : null;
  const to = dateTo.value ? new Date(dateTo.value) : null;
  const min = montoMin.value != null ? Number(montoMin.value) : null;
  const max = montoMax.value != null ? Number(montoMax.value) : null;
  return (quotations.value || []).filter(c => {
    // Texto global: cliente, vendedor, observaciones, folio, id
    const folio = c.folio ? String(c.folio) : `COTIZACION-${String(c.id).padStart(5, '0')}`;
    const text = [c.cliente, c.vendedor, c.observaciones, folio, String(c.id)]
      .filter(Boolean)
      .join(' ') 
      .toLowerCase();
    const phones = (c.telefonos || []).join(' ').toLowerCase();
    const matchText = !q || text.includes(q) || phones.includes(q);

    // Fecha (asumimos c.fecha en formato YYYY-MM-DD o ISO)
    const d = c.fecha ? new Date(c.fecha) : null;
    const matchFrom = !from || (d && d >= normalizeDate(from));
    const matchTo = !to || (d && d <= normalizeDateEnd(to));

    // Estado
    const matchStatus = !statusSelected.value?.length || statusSelected.value.includes(c.status);

    // Vendedor
    const matchVend = !vendedorSelected.value || c.vendedor === vendedorSelected.value;

    // Monto
    const monto = Number(c.monto || 0);
    const matchMontoMin = min === null || monto >= min;
    const matchMontoMax = max === null || monto <= max;

    return matchText && matchFrom && matchTo && matchStatus && matchVend && matchMontoMin && matchMontoMax;
  }).map(c => ({
    ...c,
    folio: c.folio ? c.folio : c.id ? `COTIZACION-${String(c.id).padStart(5,'0')}` : 'COTIZACION-00000'
  }));
});

const resultadosCount = computed(() => viewGrouped.value ? cotizacionesFiltradas.value.length : filteredQuotationsList.value.length);

function normalizeDate(d) {
  const nd = new Date(d);
  nd.setHours(0,0,0,0);
  return nd;
}
function normalizeDateEnd(d) {
  const nd = new Date(d);
  nd.setHours(23,59,59,999);
  return nd;
}

function clearFilters() {
  globalQuery.value = '';
  dateFrom.value = null;
  dateTo.value = null;
  statusSelected.value = [];
  vendedorSelected.value = null;
  montoMin.value = null;
  montoMax.value = null;
  filtroNombre.value = '';
  filtroTelefono.value = '';
  filtroCotizacion.value = '';
}

watch(
  () => selectedCotizacion.value?.articulos,
  (articulos) => {
    if (!articulos) return;
    let articulosArr = [];
    if (Array.isArray(articulos)) {
      articulosArr = articulos;
    } else if (typeof articulos === 'string') {
      try {
        articulosArr = Object.values(JSON.parse(articulos));
      } catch {
        articulosArr = [];
      }
    } else if (typeof articulos === 'object') {
      articulosArr = Object.values(articulos);
    }
    if (!Array.isArray(articulos.value)) return;
    articulosArr.forEach((a) => {
      // Solo ejecuta si articulos.value es un array
      const articulo = Array.isArray(articulos.value)
        ? articulos.value.find(x => x.id === a.articulo_id)
        : undefined;
      if (articulo && a.precio_unitario !== Number(articulo.precioVenta)) {
        a.precio_unitario = Number(articulo.precioVenta) || 0;
      }
    });
  },
  { deep: true }
);

watch(
  () => [selectedCotizacion.value?.articulos, selectedCotizacion.value?.descuento],
  () => {
    if (!selectedCotizacion.value || !selectedCotizacion.value.articulos) return;
    let articulosArr = [];
    const articulosRaw = selectedCotizacion.value.articulos;
    if (Array.isArray(articulosRaw)) {
      articulosArr = articulosRaw;
    } else if (typeof articulosRaw === 'string') {
      try {
        articulosArr = Object.values(JSON.parse(articulosRaw));
      } catch {
        articulosArr = [];
      }
    } else if (typeof articulosRaw === 'object' && articulosRaw !== null) {
      articulosArr = Object.values(articulosRaw);
    }
    if (!Array.isArray(articulosArr)) return;
    const subtotal = articulosArr.reduce(
      (sum, a) => sum + ((Number(a.cantidad) || 0) * (Number(a.precio_unitario) || 0)),
      0
    );
    const descuentoMonto = subtotal * ((Number(selectedCotizacion.value.descuento) || 0) / 100);
    selectedCotizacion.value.monto = subtotal - descuentoMonto;
  },
  { deep: true }
);
</script>

<style scoped>
.consultar-cotizaciones {
  /* max-width: 900px; */
  margin: 2rem auto;
  text-align: center;
  background: var(--color-bg);
  color: var(--color-text);
  border-radius: 12px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.10);
  padding: 2rem 1.5rem;
}

.consultar-cotizaciones-title {
  margin-bottom: 2rem;
  color: var(--color-title);
}

.consultar-cotizaciones-card {
  background: var(--color-card);
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  margin-bottom: 2rem;
}

.filters-advanced { display: flex; flex-direction: column; gap: .75rem; margin-bottom: 1rem; text-align: left; }
.filters-row { display: flex; gap: .75rem; align-items: center; }
.filters-row.grid-2 > * { flex: 1; }
.filters-row.grid-3 > * { flex: 1; }
.filters-field label { display:block; font-size:.85rem; color: var(--color-title); margin-bottom:.25rem; }
.range-inline { display:flex; align-items:center; gap:.5rem; }
.range-sep { color: #888; }
.filters-actions { display:flex; justify-content: space-between; align-items:center; margin-top:.25rem; }
.filters-actions .results { color:#666; font-size:.9rem; }

.filters {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.text-center {
  text-align: center;
}

.form-group {
  margin-bottom: 1rem;
  text-align: left;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: bold;
  color: var(--color-title);
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1rem;
}

.error-text {
  color: #d32f2f;
  font-size: 0.85rem;
  margin-top: 0.25rem;
}

.chip {
  display: inline-block;
  padding: 0.2em 0.7em;
  border-radius: 12px;
  font-size: 0.95em;
  font-weight: 500;
  margin-right: 0.2em;
}

.chip-pendiente {
  background: #ffe082;
  color: #795548;
}

.chip-agendado {
  background: #b2ebf2;
  color: #00695c;
}

.chip-autorizada {
  background: #c8e6c9;
  color: #388e3c;
}

.detalle-cotizacion-dialog .p-dialog-content {
  background: var(--color-card, #fff);
  border-radius: 12px;
  padding: 1.5rem 1rem;
}

.detalle-cotizacion-info {
  display: flex;
  flex-wrap: wrap;
  gap: 1.2rem 2.5rem;
  margin-bottom: 1.5rem;
  font-size: 1.05em;
  text-align: left;
}

.detalle-cotizacion-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 1rem;
  background: var(--color-card, #f9f9f9);
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  color: var(--color-text, #222);
}

.detalle-cotizacion-table th,
.detalle-cotizacion-table td {
  padding: 0.7em 1em;
  text-align: left;
  border-bottom: 1px solid #e0e0e0;
}

.detalle-cotizacion-table th {
  background: var(--color-bg, #f5f5f5);
  color: var(--color-title, #ff4081);
  font-weight: 600;
}

.detalle-cotizacion-table tr:last-child td {
  border-bottom: none;
}

@media (max-width: 700px) {
  .consultar-cotizaciones {
    padding: 1rem 0.2rem;
  }

  .consultar-cotizaciones-card {
    padding: 0.5rem;
  }

  .filters-row { flex-direction: column; align-items: stretch; }
  .range-inline { justify-content: space-between; }

  .modal-actions {
    flex-direction: column;
    gap: 0.5rem;
  }
}
</style>
``` 
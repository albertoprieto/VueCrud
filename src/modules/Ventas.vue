<template>
  <div class="ventas-card">
    <div class="p-4">
      <h2>Registrar Nota de Venta</h2>
      <div class="ventas-form-header">
        <div class="ventas-form-col">
          <label class="mb-2">Cliente</label>
          <Dropdown v-model="venta.cliente_id" :options="clientes" optionLabel="nombre" optionValue="id" placeholder="Selecciona un cliente" class="w-full" />
        </div>

        
        <div class="ventas-form-col justify-center">
          <label >Fecha</label>
          <InputText v-model="venta.fecha" :value="today" readonly class="fecha-input" />
        </div>
      </div>

      <h3>Artículos</h3>
      <DataTable :value="venta.articulos" responsiveLayout="scroll" class="venta-articulos-table">
        <Column header="Artículo">
          <template #body="slotProps">
            <Dropdown
              v-model="slotProps.data.articulo_id"
              :options="articulosConStock(slotProps.data)"
              optionLabel="nombre"
              optionValue="id"
              placeholder="Selecciona artículo"
              class="w-full"
              @change="onArticuloChange(slotProps.data.articulo_id, slotProps.data)"
              :disabled="articulosConStock(slotProps.data).length === 0"
            />
          </template>
        </Column>
        <Column header="Stock">
          <template #body="slotProps">
            {{ getStockDisponible(slotProps.data.articulo_id, slotProps.data) }}
          </template>
        </Column>
        <Column field="cantidad" header="Cantidad">
          <template #body="slotProps">
            <InputText
              type="number"
              v-model.number="slotProps.data.cantidad"
              :min="1"
              :max="mostrarColumnaIMEI(slotProps.data.articulo_id) ? 1 : getStockDisponible(slotProps.data.articulo_id, slotProps.data)"
              class="w-full"
              :disabled="!slotProps.data.articulo_id || mostrarColumnaIMEI(slotProps.data.articulo_id)"
              @input="validateCantidad(slotProps.data)"
            />
            <small v-if="slotProps.data.cantidad > getStockDisponible(slotProps.data.articulo_id, slotProps.data)" class="error-text">
              Máx: {{ getStockDisponible(slotProps.data.articulo_id, slotProps.data) }}
            </small>
            <small v-if="mostrarColumnaIMEI(slotProps.data.articulo_id)" class="info-text">
              Solo puedes vender un equipo por fila si requiere IMEI.
            </small>
          </template>
        </Column>
        <Column field="precio_unitario" header="Precio">
          <template #body="slotProps">
            <span>{{ slotProps.data.precio_unitario.toFixed(2) }}</span>
          </template>
        </Column>
        <Column field="subtotal" header="Subtotal">
          <template #body="slotProps">
            {{ (slotProps.data.cantidad * slotProps.data.precio_unitario).toFixed(2) }}
          </template>
        </Column>
        <Column header="Acciones">
          <template #body="slotProps">
            <Button icon="pi pi-trash" class="p-button-danger p-button-sm" @click="removeArticulo(slotProps.index)" />
          </template>
        </Column>
        <Column header="IMEI">
          <template #body="slotProps">
            <div class="imei-cell">
              <Dropdown
                v-if="mostrarColumnaIMEI(slotProps.data.articulo_id)"
                v-model="slotProps.data.imei"
                :options="imeisDisponiblesPorArticulo(slotProps.data.articulo_id, slotProps.data)"
                optionLabel="imei"
                optionValue="imei"
                placeholder="Selecciona IMEI"
                class="w-full imei-dropdown"
                :disabled="!slotProps.data.articulo_id"
              />
              <div v-if="slotProps.data.imei" class="imei-seleccionado">
                <span>IMEI seleccionado:</span>
                <span class="imei-value">{{ slotProps.data.imei }}</span>
              </div>
            </div>
          </template>
        </Column>
      </DataTable>
      <Button
        label="Agregar Artículo"
        icon="pi pi-plus"
        class="p-mt-2"
        @click="addArticulo"
        :disabled="articulosConStock().length === 0"
      />

      <div class="p-mt-4">
        <label>Observaciones</label>
        <Textarea v-model="venta.observaciones" rows="2" />
      </div>

      <div class="p-mt-4">
        <strong>Total: ${{ totalVenta.toFixed(2) }}</strong>
      </div>

      <Button label="Guardar Venta" class="p-mt-4" @click="guardarVenta" :disabled="!venta.cliente_id || venta.articulos.length === 0" />

      <h2 class="p-mt-6">Ventas Registradas</h2>
      <DataTable :value="ventas" selectionMode="single" v-model:selection="ventaSeleccionada" @rowSelect="cargarDetalleVenta">
        <Column field="id" header="ID" />
        <Column field="cliente_nombre" header="Cliente" />
        <Column field="fecha" header="Fecha" />
        <Column field="total" header="Total" />
      </DataTable>

      <div v-if="detalleVenta.length > 0" class="p-mt-4">
        <h3>Detalle de Venta #{{ ventaSeleccionada.id }}</h3>
        <DataTable :value="detalleVenta">
          <Column field="articulo_nombre" header="Artículo" />
          <Column field="cantidad" header="Cantidad" />
          <Column field="precio_unitario" header="Precio" />
          <Column field="subtotal" header="Subtotal" />
          <Column field="imei" header="IMEI" />
        </DataTable>
      </div>

      <Dialog v-model:visible="showDialog" header="Venta registrada" :closable="false" :modal="true">
        <p>La nota de venta se registró correctamente.</p>
        <Button label="Aceptar" icon="pi pi-check" @click="showDialog = false" autofocus />
      </Dialog>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';
import { getClientes } from '@/services/clientesService';
import { getVentas, addVenta, getDetalleVenta } from '@/services/ventasService';
import { getIMEIs } from '@/services/imeiService';
import Dropdown from 'primevue/dropdown';
import InputText from 'primevue/inputtext';
import Textarea from 'primevue/textarea';
import Button from 'primevue/button';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Dialog from 'primevue/dialog';

const toast = useToast();
const today = new Date().toISOString().slice(0, 10);

const clientes = ref([]);
const articulosDisponibles = ref([]);
const ventas = ref([]);
const ventaSeleccionada = ref(null);
const detalleVenta = ref([]);
const imeis = ref([]);
const showDialog = ref(false);

const venta = reactive({
  cliente_id: null,
  fecha: today,
  observaciones: '',
  articulos: []
});

const totalVenta = computed(() =>
  venta.articulos.reduce((sum, a) => sum + (a.cantidad * a.precio_unitario), 0)
);

const articulosAgrupados = computed(() => {
  const grupos = {};
  imeis.value.forEach(i => {
    if (!grupos[i.articulo_nombre]) {
      grupos[i.articulo_nombre] = [];
    }
    grupos[i.articulo_nombre].push(i);
  });
  return Object.entries(grupos).map(([articulo_nombre, imeisArr]) => ({
    articulo_nombre,
    cantidad: imeisArr.length,
    imeis: imeisArr
  }));
});

function getStockDisponible(articulo_id, row = null) {
  const articulo = articulosDisponibles.value.find(a => a.id === articulo_id);
  if (!articulo) return 0;
  const grupo = articulosAgrupados.value.find(g => g.articulo_nombre === articulo.nombre);
  const totalStock = grupo ? grupo.cantidad : 0;
  const enVenta = venta.articulos
    .filter(a => a.articulo_id === articulo_id && (!row || a !== row))
    .reduce((sum, a) => sum + a.cantidad, 0);
  return totalStock - enVenta;
}

function articulosConStock(row = null) {
  return articulosDisponibles.value.filter(art => {
    const stock = getStockDisponible(art.id, row);
    if (row && row.articulo_id === art.id) return true;
    return stock > 0;
  });
}

function imeisDisponiblesPorArticulo(articulo_id, currentRow = null) {
  const articulo = articulosDisponibles.value.find(a => a.id === articulo_id);
  if (!articulo) return [];
  const imeisSeleccionados = venta.articulos
    .filter(a => a.articulo_id === articulo_id && a.imei && a !== currentRow)
    .map(a => a.imei);
  return imeis.value.filter(i =>
    i.articulo_nombre === articulo.nombre &&
    i.status === 'Disponible' &&
    !imeisSeleccionados.includes(i.imei)
  );
}

function mostrarColumnaIMEI(articulo_id) {
  return imeisDisponiblesPorArticulo(articulo_id).length > 0;
}

function addArticulo() {
  venta.articulos.push({ articulo_id: null, cantidad: 1, precio_unitario: 0, imei: null });
}
function removeArticulo(index) {
  venta.articulos.splice(index, 1);
}

function validateCantidad(row) {
  if (mostrarColumnaIMEI(row.articulo_id)) {
    row.cantidad = 1;
  } else {
    const stock = getStockDisponible(row.articulo_id, row);
    if (row.cantidad > stock) {
      row.cantidad = stock;
    }
    if (row.cantidad < 1) {
      row.cantidad = 1;
    }
  }
}

function onArticuloChange(articulo_id, row) {
  const articulo = articulosDisponibles.value.find(a => a.id === articulo_id);
  if (articulo) {
    row.precio_unitario = Number(articulo.precioVenta) || 0;
    row.cantidad = mostrarColumnaIMEI(articulo_id) ? 1 : 1;
    row.imei = null;
  }
}

async function cargarClientes() {
  clientes.value = await getClientes();
}
async function cargarArticulos() {
  const res = await fetch('https://64.227.15.111/articulos/todos');
  articulosDisponibles.value = await res.json();
}
async function cargarIMEIs() {
  imeis.value = await getIMEIs();
}
async function cargarVentas() {
  ventas.value = await getVentas();
}

async function guardarVenta() {
  const clienteExiste = clientes.value.some(c => c.id === venta.cliente_id);
  if (!clienteExiste) {
    toast.add({ severity: 'error', summary: 'Cliente inválido', detail: 'Selecciona un cliente válido.', life: 4000 });
    return;
  }
  for (const art of venta.articulos) {
    const articulo = articulosDisponibles.value.find(a => a.id === art.articulo_id);
    if (!articulo) {
      toast.add({ severity: 'error', summary: 'Artículo inválido', detail: 'Selecciona un artículo válido.', life: 4000 });
      return;
    }
    if (art.cantidad > getStockDisponible(art.articulo_id, art)) {
      toast.add({ severity: 'error', summary: 'Stock insuficiente', detail: `No hay suficiente stock para el artículo seleccionado.`, life: 4000 });
      return;
    }
    if (mostrarColumnaIMEI(art.articulo_id)) {
      if (!art.imei) {
        toast.add({ severity: 'error', summary: 'IMEI requerido', detail: 'Selecciona un IMEI para este artículo.', life: 4000 });
        return;
      }
      const todosImeis = venta.articulos.filter(a => a.imei).map(a => a.imei);
      if (new Set(todosImeis).size !== todosImeis.length) {
        toast.add({ severity: 'error', summary: 'IMEI duplicado', detail: 'No puedes vender el mismo IMEI dos veces.', life: 4000 });
        return;
      }
    }
  }
  try {
    const articulosParaEnviar = venta.articulos.map(art => {
      if (mostrarColumnaIMEI(art.articulo_id)) {
        return {
          articulo_id: art.articulo_id,
          cantidad: 1,
          precio_unitario: art.precio_unitario,
          imei: art.imei
        };
      } else {
        return {
          articulo_id: art.articulo_id,
          cantidad: art.cantidad,
          precio_unitario: art.precio_unitario
        };
      }
    });

    await addVenta({
      ...venta,
      total: totalVenta.value,
      articulos: articulosParaEnviar
    });
    showDialog.value = true;
    toast.add({ severity: 'success', summary: 'Venta registrada', life: 3000 });
    venta.cliente_id = null;
    venta.observaciones = '';
    venta.articulos = [];
    await cargarIMEIs();
    await cargarArticulos();
    await cargarVentas();
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error al guardar', detail: e.message, life: 4000 });
  }
}

async function cargarDetalleVenta(event) {
  const id = event.data?.id || ventaSeleccionada.value?.id;
  if (!id) return;
  detalleVenta.value = await getDetalleVenta(id);
}

onMounted(() => {
  cargarClientes();
  cargarArticulos();
  cargarIMEIs();
  cargarVentas();
});
</script>

<style scoped>
.ventas-card {
  max-width: 900px;
  margin: 2rem auto;
  background: var(--color-bg);
  color: var(--color-text);
  border-radius: 12px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.10);
  padding: 2rem 1.5rem;
}

h2, h3 {
  color: var(--color-title);
  margin-bottom: 1.5rem;
  text-align: center;
}

.p-formgrid {
  margin-bottom: 1.5rem;
}

.p-field label {
  color: var(--color-title);
  font-weight: 500;
}

.p-button {
  border-radius: 6px;
  font-weight: 500;
}

.p-mt-2, .p-mt-4, .p-mt-6 {
  margin-top: 1.5rem !important;
}

textarea, .p-inputtext, .p-dropdown {
  background: var(--color-bg-light);
  color: var(--color-text);
  border: 1px solid var(--color-border);
  border-radius: 6px;
  padding: 0.5rem;
}

.venta-articulos-table {
  margin-bottom: 2rem;
  background: var(--color-card);
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  padding: 1.5rem;
}

.imei-seleccionado {
  background: var(--color-bg-light);
  color: var(--color-primary);
  border-radius: 4px;
  padding: 0.15rem 0.5rem;
  margin-top: 0.15rem;
  font-size: 0.95em;
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.error-text {
  color: var(--color-error);
  font-size: 0.85em;
  margin-top: 0.1rem;
  display: block;
}

.info-text {
  color: var(--color-primary);
  font-size: 0.85em;
  margin-top: 0.1rem;
  display: block;
}

.ventas-form-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 1.5rem;
}

.ventas-form-col {
  flex: 1;
  margin-right: 1rem;
}

.ventas-form-col-fecha {
  /* display: table-column; */
  /* flex-direction: column; */
  align-items: flex-end;
  justify-content: flex-end;
  margin-right: 0;
}

.fecha-input {
  width: 100%;
}

@media (max-width: 700px) {
  .ventas-card {
    padding: 1rem 0.5rem;
  }
  .venta-articulos-table {
    font-size: 0.95em;
    padding: 0.5rem;
  }
}
</style>
<template>
  <div class="ventas-container">
    <h2 class="ventas-title">Registrar Orden de Servicio</h2>
    <div class="ventas-card">
      <!-- Fila 1: Cliente, Cotización, Folio, Fecha -->
      <div class="ventas-form-header">
        <div class="ventas-form-col">
          <label>Cliente</label>
          <Dropdown v-model="venta.cliente_id" :options="clientes" optionLabel="nombre" optionValue="id" placeholder="Selecciona un cliente" class="w-full" />
        </div>
        <div class="ventas-form-col">
          <label>Cotización</label>
          <Dropdown
            v-model="cotizacionSeleccionada"
            :options="cotizacionesCliente"
            optionLabel="label"
            optionValue="id"
            placeholder="Selecciona cotización"
            class="w-full"
            @change="cargarCotizacionEnVenta(cotizacionesCliente.find(c => c.id === cotizacionSeleccionada))"
          />
        </div>
        <div class="ventas-form-col">
          <label>Orden de servicio nº</label>
          <InputText :value="folioAsignado || 'Se asignará automáticamente'" disabled class="w-full" />
        </div>
        <div class="ventas-form-col">
          <label>Fecha</label>
          <Calendar v-model="venta.fecha" dateFormat="yy-mm-dd" class="w-full" />
        </div>
      </div>

      <!-- Fila 2: Referencia, Vendedor, Descuento -->
      <div class="ventas-form-header">
        <!-- <div class="ventas-form-col">
          <label>N.º de cotización</label>
          <InputText v-model="venta.referencia" class="w-full" />
        </div> -->
        <div class="ventas-form-col">
          <label>Vendedor</label>
          <Dropdown
            v-model="venta.vendedor"
            :options="vendedores"
            optionLabel="username"
            optionValue="username"
            placeholder="Selecciona vendedor"
            class="w-full"
          />
        </div>
        <div class="ventas-form-col">
          <label>Descuento (%)</label>
          <InputText v-model.number="venta.descuento" type="number" min="0" max="100" class="w-full" :disabled="esVentaDeCotizacion" />
        </div>
      </div>

      <!-- Fila 3: Ubicación -->
      <div class="ventas-form-header">
        <div class="ventas-form-col">
          <label>Ubicación</label>
          <Dropdown
            v-model="venta.ubicacion_id"
            :options="ubicaciones"
            optionLabel="nombre"
            optionValue="id"
            placeholder="Selecciona ubicación"
            class="w-full"
          />
        </div>
      </div>

      <!-- Artículos -->
      <!-- <h3>Artículos</h3>
      <div class="mb-2">
        <Button
          label="Agregar Artículo"
          icon="pi pi-plus"
          class="mb-2"
          @click="addArticulo"
          :disabled="!venta.ubicacion_id"
        />
      </div> -->

      <!-- Tabla de artículos -->
      <DataTable
        :value="venta.articulos"
        responsiveLayout="scroll"
        class="venta-articulos-table"
        :disabled="esVentaDeCotizacion"
      >
        <Column header="Artículo">
          <template #body="slotProps">
            <template v-if="!slotProps.data.articulo_id">
              <Dropdown
                v-model="slotProps.data.articulo_id"
                :options="articulosConStockUbicacion(slotProps.data)"
                optionLabel="sku"
                optionValue="id"
                placeholder="Selecciona artículo"
                class="w-full"
                @change="onArticuloChange(slotProps.data.articulo_id, slotProps.data)"
                :disabled="articulosConStockUbicacion(slotProps.data).length === 0"
              />
            </template>
            <template v-else>
              <span>
                {{ getArticuloNombreAsync(slotProps.data.articulo_id, slotProps.data) }}
              </span>
            </template>
          </template>
        </Column>
        <Column header="Stock">
          <template #body="slotProps">
            <span v-if="esServicio(slotProps.data.articulo_id)">NA</span>
            <span v-else>
              <Chip
                :label="getStockDisponible(slotProps.data.articulo_id, slotProps.data)"
                class="stock-chip"
                style="background:#bdbdbd;color:#222;"
              />
            </span>
          </template>
        </Column>
        <Column field="cantidad" header="Cantidad">
          <template #body="slotProps">
            <InputText
              type="number"
              v-model.number="slotProps.data.cantidad"
              :min="1"
              :max="!esServicio(slotProps.data.articulo_id) ? getStockDisponible(slotProps.data.articulo_id, slotProps.data) : null"
              class="w-full"
              :disabled="true"
              @input="validateCantidad(slotProps.data)"
            />
            <small v-if="!esServicio(slotProps.data.articulo_id) && slotProps.data.cantidad > getStockDisponible(slotProps.data.articulo_id, slotProps.data)" class="error-text">
              Máx: {{ getStockDisponible(slotProps.data.articulo_id, slotProps.data) }}
            </small>
          </template>
        </Column>
        <Column field="precio_unitario" header="C/U">
          <template #body="slotProps">
            <span>{{ (slotProps.data.precio_unitario ?? 0).toFixed(2) }}</span>
          </template>
        </Column>
        <Column field="subtotal" header="Importe">
          <template #body="slotProps">
            {{ ((slotProps.data.cantidad ?? 0) * (slotProps.data.precio_unitario ?? 0)).toFixed(2) }}
          </template>
        </Column>
      </DataTable>
      <!-- IMEI eliminado completamente -->

      <div class="mb-2">
        <label>Observaciones</label>
        <InputText v-model="venta.observaciones" class="w-full" />
      </div>

      <div class="mb-2">
        <label>Método de pago <span style="color:red">*</span></label>
        <Dropdown
          v-model="venta.terminos_pago"
          :options="metodoPagoOptions"
          optionLabel="label"
          optionValue="value"
          placeholder="Selecciona método de pago"
          class="w-full"
          :class="{'p-invalid': !venta.terminos_pago}"
        />
        <small v-if="!venta.terminos_pago" class="error-text">Selecciona un método de pago</small>
      </div>


      <!-- Mensaje de advertencia si falta stock -->
      <div v-if="stockInsuficiente" class="error-text mb-2">
        No hay suficiente stock para uno o más artículos en la ubicación seleccionada.
      </div>

      <div class="mb-2 acciones-footer">
        <div>
          <div><strong>Subtotal:</strong> ${{ subtotalVenta.toFixed(2) }}</div>
          <div><strong>Descuento:</strong> {{ venta.descuento || 0 }}% (${{ descuentoMonto.toFixed(2) }})</div>
          <div><strong>Total (MXN):</strong> ${{ totalVenta.toFixed(2) }}</div>
        </div>
        <Button
          label="Generar orden"
          class="mb-2"
          @click="guardarVentaConLoading"
          :disabled="!venta.cliente_id || !cotizacionSeleccionada || venta.articulos.length === 0 || loadingGuardar || stockInsuficiente"
        />
      </div>

      <div class="mb-2">
        <label>Si necesita factura el pago sería más IVA.</label>
      </div>
      <div class="mb-2">
        <label>Términos y condiciones:</label>
        <small class="info-text">Si el técnico acudió al domicilio o va de camino y se cancela el servicio se cobrará la vuelta en falso del técnico. 
El tiempo de traslado en el envió de los paquetes depende de la paquetería.</small>
      </div>

      <Dialog v-model:visible="ventaRegistrada" header="Orden de Servicio" :closable="false" :modal="true" class="ventas-dialog">
        <p>{{ mensajeExito }}</p>
        <Button label="Aceptar" icon="pi pi-check" @click="cerrarDialogoVenta" autofocus />
      </Dialog>
    </div>
  </div>
</template>

<script setup>
import { useVentas } from '@/composables/useVentas.js';
import { generarNotaVentaPDF } from '@/services/NotaVentaPdfService.js';
import { getDetalleVenta } from '@/services/ventasService';
import { getClientes } from '@/services/clientesService';
import { getTodosArticulos } from '@/services/articulosService';
import { getUbicaciones } from '@/services/ubicacionesService';
import { getUsuarios } from '@/services/usuariosService';
import Dropdown from 'primevue/dropdown';
import InputText from 'primevue/inputtext';
import Button from 'primevue/button';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Dialog from 'primevue/dialog';
import Calendar from 'primevue/calendar';
import { ref, reactive, computed, onMounted, watch } from 'vue';
import { useToast } from 'primevue/usetoast';
import { getArticulosStockPorUbicacion } from '@/services/articulosService';
import { useRouter } from 'vue-router';
import { registrarMovimiento } from '@/services/inventarioService';
import { getQuotations, updateQuotation } from '@/services/quotationService';
import Chip from 'primevue/chip';

const venta = reactive({
  cliente_id: null,
  fecha: new Date().toISOString().slice(0, 10),
  referencia: '',
  fecha_envio: '',
  terminos_pago: '',
  metodo_entrega: '',
  vendedor: '',
  descuento: 0,
  ubicacion_id: null,
  articulos: [],
  observaciones: '',
  notas_cliente: '',
  terminos_condiciones: '',
  total: 0,
  almacen: ''
});
const toast = useToast();
const router = useRouter();

const {
  getVentas
} = useVentas();

const ventaRegistrada = ref(false);
const mensajeExito = ref('La orden de servicio se registró correctamente.');
const detalleVentaPDF = ref([]);
const clientePDF = ref({});
const articulosPDF = ref([]);
const showDetalleDialog = ref(false);
const loadingGuardar = ref(false);
const ubicaciones = ref([]);
const vendedores = ref([]);
const cotizacionesCliente = ref([]);
const cotizacionSeleccionada = ref(null);
const esVentaDeCotizacion = computed(() => !!cotizacionSeleccionada.value);
const articulosDisponibles = ref([]);
const folioAsignado = ref('');

function irAEditarCotizacion() {
  if (cotizacionSeleccionada.value) {
    router.push(`/cotizaciones/editar/${cotizacionSeleccionada.value}`);
  }
}

const terminosPagoOptions = [
  { label: 'Neto 15', value: 'Neto 15' },
  { label: 'Neto 30', value: 'Neto 30' },
  { label: 'Neto 45', value: 'Neto 45' },
  { label: 'Neto 60', value: 'Neto 60' },
  { label: 'Pago Contra Entrega', value: 'Pago Contra Entrega' }
];

const metodoPagoOptions = [
  { label: 'Depósito', value: 'Depósito' },
  { label: 'Transferencia', value: 'Transferencia' }
];

const clientes = ref([]);
const todasCotizaciones = ref([]); // Guarda todas las cotizaciones para filtrar clientes

onMounted(async () => {
  // 1. Cargar todas las cotizaciones
  todasCotizaciones.value = await getQuotations();

  // 2. Cargar todos los clientes
  const todosClientes = await getClientes();

  // 3. Filtrar solo los clientes con cotizaciones pendientes
  const clientesConPendientes = todosClientes.filter(cliente =>
    todasCotizaciones.value.some(
      c => String(c.cliente_id) === String(cliente.id) && c.status === 'Pendiente'
    )
  );
  clientes.value = clientesConPendientes;

  // 4. Cargar ubicaciones, ventas, usuarios
  ubicaciones.value = await getUbicaciones();
  const ventas = await getVentas();
  // folioPropuesto.value = generarFolioConsecutivo(ventas);
  // venta.folio = folioPropuesto.value;
  const usuarios = await getUsuarios();
  vendedores.value = usuarios.filter(u => u.perfil === 'Vendedor');
});

watch(
  () => venta.ubicacion_id,
  async (nuevaUbicacion, anteriorUbicacion) => {
    if (nuevaUbicacion !== anteriorUbicacion) {
      if (nuevaUbicacion) {
        const articulosUbicacion = await getArticulosStockPorUbicacion(nuevaUbicacion);
        const todos = await getTodosArticulos();
        const servicios = todos.filter(a => a.tipo && a.tipo.toLowerCase() === 'servicio');
        servicios.forEach(serv => {
          if (!articulosUbicacion.some(a => a.id === serv.id)) {
            articulosUbicacion.push(serv);
          }
        });
        articulosDisponibles.value = articulosUbicacion;

        // Imprime el stock de los artículos disponibles en consola
        console.log('Stock en ubicación seleccionada:', articulosUbicacion.map(a => ({
          id: a.id,
          nombre: a.nombre,
          stock: a.stock
        })));

        // Valida stock de los artículos ya cargados
        venta.articulos.forEach(a => {
          const stock = articulosUbicacion.find(art => art.id === a.articulo_id)?.stock ?? 0;
          if (!esServicio(a.articulo_id) && a.cantidad > stock) {
            a.cantidad = stock; // Ajusta cantidad si es mayor al stock
          }
        });
      } else {
        articulosDisponibles.value = [];
      }
    }
  }
);

watch(
  () => venta.cliente_id,
  async (nuevoClienteId) => {
    if (nuevoClienteId) {
      const todas = await getQuotations();
      cotizacionesCliente.value = todas
        .filter(
          c => String(c.cliente_id) === String(nuevoClienteId) && c.status !== 'Autorizada'
        )
        .map(c => ({
          ...c,
          label: `COTIZACION-${String(c.id).padStart(5, '0')}`
        }));
      console.log('Cotizaciones del cliente seleccionado:', cotizacionesCliente.value);
    } else {
      cotizacionesCliente.value = [];
    }
    cotizacionSeleccionada.value = null;
  }
);

async function guardarVentaConLoading() {
  loadingGuardar.value = true;
  try {
    if (!venta.terminos_pago) {
      toast.add({ severity: 'error', summary: 'Error', detail: 'Debes seleccionar un método de pago.', life: 4000 });
      loadingGuardar.value = false;
      return;
    }
    // Prepara los datos de la venta
    const { addVenta } = await import('@/services/ventasService');
    const ubicacionObj = ubicaciones.value.find(u => u.id === venta.ubicacion_id);
    venta.almacen = ubicacionObj ? ubicacionObj.nombre : '';

    // Prepara los artículos SIN imeis
    const articulosLimpios = venta.articulos.map(a => ({
      articulo_id: a.articulo_id,
      cantidad: a.cantidad,
      precio_unitario: a.precio_unitario,
        imeis: []
    }));

    // Guarda la venta
    const response = await addVenta({
      cliente_id: venta.cliente_id,
      fecha: venta.fecha,
      referencia: venta.referencia ? String(venta.referencia) : '',
      fecha_envio: venta.fecha_envio ? venta.fecha_envio : null,
      terminos_pago: venta.terminos_pago,
      metodo_entrega: venta.metodo_entrega,
      vendedor: venta.vendedor,
      almacen: venta.almacen,
      descuento: venta.descuento,
      notas_cliente: venta.notas_cliente,
      terminos_condiciones: venta.terminos_condiciones,
      total: totalVenta.value,
      observaciones: venta.observaciones,
      articulos: articulosLimpios
    });

    folioAsignado.value = response.folio || '';

    // Si la venta proviene de una cotización, autoriza la cotización
    if (cotizacionSeleccionada.value) {
      const cotizacion = cotizacionesCliente.value.find(c => c.id === cotizacionSeleccionada.value);
      if (cotizacion) {
        // Convierte el array de artículos a objeto si es necesario
        let articulosObj = {};
        if (Array.isArray(venta.articulos)) {
          venta.articulos.forEach((a, idx) => {
            articulosObj[idx] = {
              cantidad: a.cantidad,
              articulo_id: a.articulo_id,
              precio_unitario: a.precio_unitario
            };
          });
        } else {
          articulosObj = venta.articulos;
        }

        await updateQuotation(cotizacion.id, {
          ...cotizacion,
          status: 'Autorizada',
          autorizada: true,
          fecha_autorizacion: new Date().toISOString().slice(0, 10),
          articulos: articulosObj // <-- Aquí va como objeto, NO como string
        });
      }
    }

    // Genera PDF y muestra éxito
    const ventasActualizadas = await getVentas();
    const ultimaVenta = ventasActualizadas[ventasActualizadas.length - 1];
    const detalle = await getDetalleVenta(ultimaVenta.id);
    detalleVentaPDF.value = detalle;

    const clientes = await getClientes();
    clientePDF.value = clientes.find(c => c.id === ultimaVenta.cliente_id) || {};

    const articulos = await getTodosArticulos();
    articulosPDF.value = detalle.map(item => {
      const art = articulos.find(a => a.id === item.articulo_id) || {};
      return {
        ...item,
        sku: art.sku,
        nombre: art.nombre
      };
    });

    await generarNotaVentaPDF({
      venta: ultimaVenta,
      cliente: clientePDF.value,
      articulos: articulosPDF.value,
      empresa: { nombre: 'GPSubicacion.com', direccion: 'Guadalajara', rfc: 'RFC123456' }
    });

    ventaRegistrada.value = true;
    mensajeExito.value = `La orden de servicio se registró correctamente.\nFolio asignado: ${folioAsignado.value}`;
    toast.add({ severity: 'success', summary: 'Orden de servicio registrada', detail: mensajeExito.value, life: 3000 });
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo registrar la orden.', life: 4000 });
  } finally {
    loadingGuardar.value = false;
  }
}

function cerrarDialogoVenta() {
  ventaRegistrada.value = false;
  router.push('/dashboard');
}

const esServicio = (articulo_id) => {
  const art = articulosDisponibles.value.find(a => a.id === articulo_id);
  return art && String(art.tipo).toLocaleLowerCase() === 'servicio';
};

const subtotalVenta = computed(() =>
  venta.articulos.reduce((sum, a) => sum + (a.cantidad * a.precio_unitario), 0)
);
const descuentoMonto = computed(() =>
  subtotalVenta.value * ((venta.descuento || 0) / 100)
);
const totalVenta = computed(() =>
  subtotalVenta.value - descuentoMonto.value
);

// Computed para validar stock insuficiente por ubicación
const stockInsuficiente = computed(() => {
  if (!venta.ubicacion_id) return false;
  return venta.articulos.some(a => {
    // No valida servicios
    if (esServicio(a.articulo_id)) return false;
    const stock = getStockDisponible(a.articulo_id, a);
    return a.cantidad > stock;
  });
});

function articulosConStockUbicacion(row = null) {
  if (!venta.ubicacion_id) return [];
  // Solo muestra artículos con stock > 0 o servicios
  return articulosDisponibles.value.filter(art => {
    if (art.tipo && art.tipo.toLowerCase() === 'servicio') return true;
    return art.stock > 0;
  });
}

function cargarCotizacionEnVenta(cotizacion) {
  if (!cotizacion) return;
  console.log('Cotización seleccionada:', cotizacion);

  // Parsear articulos si es string
  let articulos = [];
  if (typeof cotizacion.articulos === 'string') {
    try {
      const parsed = JSON.parse(cotizacion.articulos);
      articulos = Object.values(parsed);
    } catch (e) {
      articulos = [];
    }
  } else if (Array.isArray(cotizacion.articulos)) {
    articulos = cotizacion.articulos;
  } else if (typeof cotizacion.articulos === 'object') {
    articulos = Object.values(cotizacion.articulos);
  }

  venta.referencia = cotizacion.id;
  venta.descuento = cotizacion.descuento || 0;
  venta.observaciones = cotizacion.observaciones || '';
  venta.articulos = articulos;
  venta.fecha = cotizacion.fecha || venta.fecha;
  venta.vendedor = cotizacion.vendedor || '';
  venta.ubicacion_id = cotizacion.ubicacion_id || null;
  venta.notas_cliente = cotizacion.notas_cliente || '';
  venta.terminos_condiciones = cotizacion.terminos_condiciones || '';
}

// Agrega esta función para evitar el error en la tabla
function getStockDisponible(articulo_id, row) {
  // Devuelve un número de stock simulado o real según tu lógica
  const articulo = articulosDisponibles.value.find(a => a.id === articulo_id);
  if (!articulo) return 0;
  // Si tienes stock en el objeto, usa eso, si no, retorna un valor por defecto
  return articulo.stock ?? 0;
}

function mostrarColumnaIMEI(articulo_id) {
  // Eliminada la lógica de IMEI
  return false;
}

const articulosNombreCache = {};
async function fetchArticuloNombre(articulo_id) {
  if (articulosNombreCache[articulo_id]) return articulosNombreCache[articulo_id];
  try {
    const todos = await getTodosArticulos();
    const art = todos.find(a => a.id === articulo_id);
    if (art) {
      articulosNombreCache[articulo_id] = art.nombre;
      return art.nombre;
    }
  } catch (e) {}
  return articulo_id;
}

function getArticuloNombre(articulo_id) {
  const articulos = Array.isArray(articulosDisponibles.value) ? articulosDisponibles.value : [];
  const art = articulos.find(a => a.id === articulo_id);
  return art ? art.nombre : '';
}

function getArticuloNombreAsync(articulo_id, row) {
  // Si ya está en la lista, mostrarlo
  const nombre = getArticuloNombre(articulo_id);
  if (nombre) return nombre;
  // Si ya está en cache, mostrarlo
  if (articulosNombreCache[articulo_id]) return articulosNombreCache[articulo_id];
  // Si no, buscarlo y actualizar el row
  fetchArticuloNombre(articulo_id).then(nombre => {
    if (row && nombre && nombre !== articulo_id) {
      row._articulo_nombre = nombre;
    }
  });
  // Si ya se guardó en el row, mostrarlo
  if (row && row._articulo_nombre) return row._articulo_nombre;
  // Mientras, mostrar el id
  return articulo_id;
}
</script>

<style scoped>
.ventas-container {
  max-width: 900px;
  margin: 2rem auto;
  padding: 2rem;
  background: var(--color-bg);
  color: var(--color-text);
  border-radius: 12px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.10);
}
.ventas-title {
  margin-bottom: 2rem;
  color: var(--color-title);
  text-align: center;
}
.ventas-card {
  background: var(--color-card);
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  margin-bottom: 2rem;
}
.ventas-form-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 1.5rem;
  gap: 1rem;
}
.ventas-form-col {
  flex: 1;
}
.mb-2 {
  margin-bottom: 1rem;
}
.w-full {
  width: 100%;
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
.ventas-dialog :deep(.p-dialog-content) {
  background: var(--color-card);
  padding: 1.5rem 1rem;
  border-radius: 12px;
  color: var(--color-text);
}
.ventas-dialog :deep(.p-dialog-header) {
  background: var(--color-bg);
  color: var(--color-title);
  border-bottom: 1px solid var(--color-border);
  border-radius: 12px 12px 0 0;
  font-size: 1.2rem;
  font-weight: bold;
  padding: 1rem 1.5rem;
}
.detalle-venta-dialog {
  padding: 0.5rem 0;
}
.detalle-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 1rem;
  background: var(--color-card);
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  color: var(--color-text);
}
.detalle-table th, .detalle-table td {
  padding: 0.7em 1em;
  text-align: left;
  border-bottom: 1px solid var(--color-border);
}
.detalle-table th {
  background: var(--color-bg);
  color: var(--color-title);
  font-weight: 600;
}
.detalle-table tr:last-child td {
  border-bottom: none;
}
.detalle-venta-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 2rem;
  margin-top: 1rem;
  font-size: 1.05em;
  color: var(--color-text);
}
.detalle-total {
  color: var(--color-title);
  font-size: 1.15em;
  font-weight: bold;
}
.detalle-cerrar-btn {
  margin-top: 1.5rem;
  float: right;
}
.acciones-footer {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 2rem;
  margin-bottom: 1rem;
}
.acciones-footer strong {
  font-size: 1.1em;
}
.stock-chips {
  display: flex;
  gap: 0.5em;
  align-items: center;
}
.stock-chip, .requerido-chip {
  font-size: 0.95em;
  font-weight: bold;
  border-radius: 8px;
}
@media (max-width: 700px) {
  .ventas-container {
    padding: 1rem 0.2rem;
  }
  .ventas-card {
    padding: 0.5rem;
  }
  .ventas-form-header {
    flex-direction: column;
    gap: 0.5rem;
  }
  .venta-articulos-table {
    font-size: 0.95em;
    padding: 0.5rem;
  }
}
</style>
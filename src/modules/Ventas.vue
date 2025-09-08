<template>
  <div class="ventas-container">
    <h2 class="ventas-title">Registrar Orden de Servicio</h2>
    <div class="ventas-card">
      <!-- Fila 1: Cliente, Cotización, Folio, Fecha -->
      <div class="ventas-form-header">
        <div class="ventas-form-col">
          <label>Cliente</label>
          <Dropdown
            v-model="venta.cliente_id"
            :options="clientes"
            optionLabel="nombre"
            optionValue="id"
            placeholder="Selecciona un cliente"
            class="w-full"
            filter
            filterPlaceholder="Buscar cliente..."
            :filterBy="'nombre'"
            showClear
            :virtualScrollerOptions="{ itemSize: 38 }"
          />
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
            filter
            filterPlaceholder="Buscar cotización..."
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
        <div class="ventas-form-col">
          <label>Vendedor</label>
          <Dropdown
            v-model="venta.vendedor"
            :options="vendedores"
            optionLabel="username"
            optionValue="username"
            placeholder="Selecciona vendedor"
            class="w-full"
            filter
            filterPlaceholder="Buscar vendedor..."
            showClear
          />
        </div>
        <div class="ventas-form-col">
          <label>Descuento (%)</label>
          <InputText v-model.number="venta.descuento" type="number" min="0" max="100" class="w-full" :disabled="esVentaDeCotizacion" />
        </div>
      </div>

    <!-- Fila 3: Ubicación o Técnico -->
      <div class="ventas-form-header">
        <div class="ventas-form-col">
      <label>Ubicación o Técnico</label>
          <Dropdown
            v-model="venta.ubicacion_id"
            :options="ubicaciones"
            optionLabel="nombre"
            optionValue="id"
            placeholder="Selecciona ubicación"
            class="w-full"
            filter
            filterPlaceholder="Buscar ubicación..."
            :filterBy="'nombre'"
            @change="onSeleccionarUbicacion(venta.ubicacion_id)"
          />
          <span v-if="venta.ubicacion_id" class="info-text">Ubicación seleccionada: {{ ubicaciones.find(u => u.id === venta.ubicacion_id)?.nombre }}</span>
        </div>
      </div>

      <!-- Fila: Atendido / Facturación -->
      <div class="ventas-form-header form-grid-4">
        <div class="ventas-form-col">
          <label>Atendido por</label>
          <InputText :value="usuarioActual" class="w-full" disabled />
        </div>
        <div class="ventas-form-col">
          <label>Requiere factura</label>
          <div class="inline-control">
            <Checkbox v-model="requiereFactura" binary />
          </div>
        </div>
        <div class="ventas-form-col">
          <label>RFC</label>
          <InputText v-model="rfc" :disabled="!requiereFactura" placeholder="RFC" class="w-full" />
        </div>
        <div class="ventas-form-col">
          <label>Constancia fiscal</label>
          <input type="file" class="file-input" @change="e => archivoConstancia.value = e.target.files[0]" :disabled="!requiereFactura" />
        </div>
      </div>

      <!-- Tabla de artículos -->
      <DataTable
        :value="venta.articulos"
        responsiveLayout="scroll"
        class="venta-articulos-table"
        :disabled="!ubicacionValida || esVentaDeCotizacion"
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
              <div class="stock-chips">
                <Chip
                  :label="'Disp: ' + getStockDisponible(slotProps.data.articulo_id, slotProps.data)"
                  class="stock-chip"
                  :style="{ background: 'var(--color-muted-bg)', color: 'var(--color-on-muted)' }"
                />
                <Chip
                  v-if="(slotProps.data.cantidad ?? 0) > getStockDisponible(slotProps.data.articulo_id, slotProps.data)"
                  :label="'Faltan ' + Math.max(0, (slotProps.data.cantidad ?? 0) - getStockDisponible(slotProps.data.articulo_id, slotProps.data))"
                  class="requerido-chip faltan-chip"
                />
              </div>
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
      <div v-if="stockInsuficiente" class="alerta-stock">
        <div class="alerta-header">
          <span class="alerta-titulo">Stock insuficiente en la ubicación seleccionada</span>
          <div class="alerta-acciones">
            <Button label="Ajustar a stock" class="p-button-text" @click="ajustarACapacidad" />
            <Button label="Cambiar ubicación" class="p-button-text" @click="abrirSelectorUbicacion" />
            <Button v-if="esAdmin" label="Transferir IMEIs" class="p-button-text" @click="irATransferirImeis" />
          </div>
        </div>
        <div class="alerta-tabla">
          <table>
            <thead>
              <tr>
                <th>SKU</th>
                <th>Artículo</th>
                <th>Requiere</th>
                <th>Hay</th>
                <th>Faltan</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="d in detalleFaltantes" :key="d.articulo_id">
                <td>{{ d.sku }}</td>
                <td>{{ d.nombre }}</td>
                <td>{{ d.requerido }}</td>
                <td>{{ d.stock }}</td>
                <td class="faltan">{{ d.faltan }}</td>
              </tr>
            </tbody>
          </table>
        </div>
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
          :title="stockInsuficiente ? 'Completa stock o ajusta cantidades para continuar' : null"
          v-tooltip.top="stockInsuficiente ? 'Completa stock o ajusta cantidades para continuar' : ''"
          :disabled="!venta.cliente_id || !cotizacionSeleccionada || venta.articulos.length === 0 || loadingGuardar || stockInsuficiente || !ubicacionValida || !venta.terminos_pago"
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
      <Dialog v-model:visible="dialogoSinStock" header="Stock insuficiente" :modal="true" :closable="true" class="ventas-dialog">
        <p style="color: red; font-weight: bold;">{{ mensajeSinStock }}</p>
        <Button label="Aceptar" icon="pi pi-check" @click="dialogoSinStock = false; venta.ubicacion_id = null;" autofocus />
      </Dialog>
    </div>
  </div>
</template>

<script setup>
import { useVentas } from '@/composables/useVentas.js';
import { getDetalleVenta } from '@/services/ventasService';
import { getClientes } from '@/services/clientesService';
import { getTodosArticulos } from '@/services/articulosService';
import { getUbicaciones, getImeisPorUbicacion } from '@/services/ubicacionesService';
import { getUsuarios } from '@/services/usuariosService';
import Dropdown from 'primevue/dropdown';
import InputText from 'primevue/inputtext';
import Button from 'primevue/button';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Dialog from 'primevue/dialog';
import Calendar from 'primevue/calendar';
import Checkbox from 'primevue/checkbox';
import { ref, reactive, computed, onMounted, watch } from 'vue';
import { useToast } from 'primevue/usetoast';
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
const clientes = ref([]);
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
const dialogoSinStock = ref(false);
const mensajeSinStock = ref('');
const ubicacionInvalida = ref(false);

const todasCotizaciones = ref([]);
const articulosCatalog = ref([]);

const mostrarDialogoUbicacion = ref(false);
const ubicacionSeleccionada = ref(null);
const ubicacionesDialog = ref([]);
const articulosStockDialog = ref([]);
const ubicacionValidaDialog = computed(() => {
  if (!ubicacionSeleccionada.value) return false;
  if (venta.articulos.length === 0) return true;
  return !venta.articulos.some(a => {
    if (a.articulo_id == null) return false;
    const stock = articulosStockDialog.value.find(art => art.id === a.articulo_id)?.stock ?? 0;
    return a.cantidad > stock && stock !== 'NA';
  });
});

import { useLoginStore } from '@/stores/loginStore';
const loginStore = useLoginStore();
const usuarioActual = computed(() => loginStore.user.username.toUpperCase() || '');
const esAdmin = computed(() => (loginStore.user?.perfil || '').toLowerCase() === 'admin');

const requiereFactura = ref(false);
const rfc = ref('XAXX010101000');
const archivoConstancia = ref(null);

async function onSeleccionarUbicacion(id) {
  // Usar IMEIs como fuente canonical y mapear a stock por artículo
  let articulosUbicacion = [];
  try {
    const imeis = await getImeisPorUbicacion(id);
    articulosUbicacion = agruparStockDesdeImeis(imeis);

    console.info('[Ubicación] Stock calculado a partir de IMEIs (fuente canonical).');
  } catch (_) {
    // si falla IMEIs deja la lista vacía (se añade instalación abajo)
    articulosUbicacion = [];
  }
  // Agrega el objeto de instalación a la ubicación seleccionada
  const instalacionObj = {
    cantidad: 1,
    id: 5,
    stock: 1,
    articulo_id: 5,
    precio_unitario: 650,
  nombre: 'Instalacion a Domicilio GDL',
  tipo: 'Servicio'
  };
  articulosUbicacion.push(instalacionObj);
  articulosDisponibles.value = articulosUbicacion;
  // Log enfocado: coincidencias entre cotización y ubicacion
  logCoincidenciasCotizacionUbicacion();
  // Log adicional: artículos por SKU en la ubicación seleccionada
  try {
    console.groupCollapsed('[Ubicación] Artículos por SKU');
    const items = (Array.isArray(articulosDisponibles.value) ? articulosDisponibles.value : []).map(art => ({
      sku: getArticuloSkuById(art.id ?? art.articulo_id),
      id: art.id ?? art.articulo_id,
      nombre: art.nombre ?? '',
      stock: art.stock ?? 0,
      tipo: art.tipo ?? ''
    }));
    console.table(items);
    console.groupEnd();
  } catch (_) {}
}

function logCoincidenciasCotizacionUbicacion() {
  try {
    const cotizacionArts = Array.isArray(venta.articulos) ? venta.articulos : [];
    const ubicacionArts = Array.isArray(articulosDisponibles.value) ? articulosDisponibles.value : [];
    const detalle = cotizacionArts.map(a => {
      const artU = ubicacionArts.find(art => art.id === a.articulo_id || art.articulo_id === a.articulo_id);
      const servicio = esServicio(a.articulo_id);
      const stock = servicio ? 'NA' : (artU?.stock ?? 0);
      const requerido = a.cantidad ?? 0;
      const existe = servicio || !!artU;
      const stockOK = servicio || (Number(stock) >= Number(requerido));
      return {
  sku: getArticuloSkuById(a.articulo_id),
        articulo_id: a.articulo_id,
        requerido,
        stock_disponible: stock,
        existe_en_ubicacion: existe,
        stock_suficiente: stockOK
      };
    });
    const totales = {
      total_articulos_cotizacion: detalle.length,
      coinciden_en_ubicacion: detalle.filter(d => d.existe_en_ubicacion).length,
      con_stock_suficiente: detalle.filter(d => d.stock_suficiente).length,
      ubicacion_valida: ubicacionValida.value && !stockInsuficiente.value
    };
    console.groupCollapsed('[Orden Servicio] Coincidencias cotización vs ubicación');
    console.table(detalle);
    console.log('Resumen:', totales);
    console.groupEnd();
  } catch (_) {
    // silencio: este log es solo de depuración
  }
}

onMounted(async () => {
  // Catálogo de artículos para resolver SKU/nombres en logs
  try {
    articulosCatalog.value = await getTodosArticulos();
  } catch (_) { articulosCatalog.value = []; }
  todasCotizaciones.value = await getQuotations();
  const todosClientes = await getClientes();
  const clientesConPendientes = todosClientes.filter(cliente =>
    todasCotizaciones.value.some(
      c => String(c.cliente_id) === String(cliente.id) && c.status === 'Pendiente'
    )
  );
  clientes.value = clientesConPendientes;
  ubicaciones.value = await getUbicaciones();
  const ventas = await getVentas();
  const usuarios = await getUsuarios();
  vendedores.value = usuarios.filter(u => u.perfil === 'Vendedor');

  // Usuario actual viene del store de login (usuarioActual es computed)
});

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
    const { addVenta } = await import('@/services/ventasService');
    const ubicacionObj = ubicaciones.value.find(u => u.id === venta.ubicacion_id);
    venta.almacen = ubicacionObj ? ubicacionObj.nombre : '';
    const articulosLimpios = venta.articulos.map(a => ({
      articulo_id: a.articulo_id,
      cantidad: a.cantidad,
      precio_unitario: a.precio_unitario,
        imeis: []
    }));
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

    if (cotizacionSeleccionada.value) {
      const cotizacion = cotizacionesCliente.value.find(c => c.id === cotizacionSeleccionada.value);
      if (cotizacion) {
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
          articulos: articulosObj
        });
      }
    }

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
  const art = articulosDisponibles.value.find(a => a.id === articulo_id || a.articulo_id === articulo_id);
  if (!art) return false;
  const tipo = String(art.tipo).toLocaleLowerCase();
  return tipo === 'servicio' || tipo === 'servicio' || tipo === 'servicios';
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

const stockInsuficiente = computed(() => {
  if (!venta.ubicacion_id) return false;
  return venta.articulos.some(a => {
    if (esServicio(a.articulo_id)) return false;
    // Buscar el artículo en la ubicación por id o articulo_id
    const artUbicacion = articulosDisponibles.value.find(art => art.id === a.articulo_id || art.articulo_id === a.articulo_id);
    const stock = artUbicacion ? artUbicacion.stock ?? 0 : 0;
    return a.cantidad > stock;
  });
});

const detalleFaltantes = computed(() => {
  if (!venta.ubicacion_id) return [];
  const detalles = [];
  for (const a of venta.articulos) {
    if (esServicio(a.articulo_id)) continue;
    const artU = articulosDisponibles.value.find(art => art.id === a.articulo_id || art.articulo_id === a.articulo_id);
    const stock = artU ? (artU.stock ?? 0) : 0;
    const requerido = a.cantidad ?? 0;
    if (requerido > stock) {
      detalles.push({
        articulo_id: a.articulo_id,
        sku: getArticuloSkuById(a.articulo_id),
        nombre: getArticuloNombre(a.articulo_id) || (artU?.nombre ?? ''),
        requerido,
        stock,
        faltan: Math.max(0, requerido - stock)
      });
    }
  }
  return detalles;
});

function ajustarACapacidad() {
  // Ajusta cantidades a lo disponible en la ubicación
  venta.articulos = venta.articulos.map(a => {
    if (esServicio(a.articulo_id)) return a;
    const artU = articulosDisponibles.value.find(art => art.id === a.articulo_id || art.articulo_id === a.articulo_id);
    const stock = artU ? (artU.stock ?? 0) : 0;
    return { ...a, cantidad: Math.min(a.cantidad ?? 0, stock) };
  });
}

function abrirSelectorUbicacion() {
  // simple: enfocarse al dropdown de ubicación
  toast.add({ severity: 'info', summary: 'Selecciona otra ubicación', detail: 'Abre el selector “Ubicación o Técnico”.', life: 2500 });
}

function irATransferirImeis() {
  router.push({ name: 'transferir-imeis' });
}

const ubicacionValida = computed(() => {
  if (!venta.ubicacion_id) return false;
  if (venta.articulos.length === 0) return true;
  const articulosUbicacion = articulosDisponibles.value;
  return !venta.articulos.some(a => {
    if (esServicio(a.articulo_id)) return false;
    const artUbicacion = articulosUbicacion.find(art => art.id === a.articulo_id || art.articulo_id === a.articulo_id);
    const stock = artUbicacion ? artUbicacion.stock ?? 0 : 0;
    return a.cantidad > stock;
  });
});

function articulosConStockUbicacion(row = null) {
  if (!venta.ubicacion_id) return [];
  return articulosDisponibles.value.filter(art => {
    if (art.tipo && art.tipo.toLowerCase() === 'servicio') return true;
    return art.stock > 0;
  });
}

function cargarCotizacionEnVenta(cotizacion) {
  if (!cotizacion) return;

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
  // Log enfocado cuando ya hay ubicación cargada
  if (venta.ubicacion_id) {
    logCoincidenciasCotizacionUbicacion();
  }
}

function getStockDisponible(articulo_id, row) {
  const articulo = articulosDisponibles.value.find(a => a.id === articulo_id || a.articulo_id === articulo_id);
  if (!articulo) return 0;
  return articulo.stock ?? 0;
}

function mostrarColumnaIMEI(articulo_id) {
  return false;
}

const articulosNombreCache = {};
async function fetchArticuloNombre(articulo_id) {
  if (articulosNombreCache[articulo_id]) return articulosNombreCache[articulo_id];
  try {
  const todos = articulosCatalog.value?.length ? articulosCatalog.value : await getTodosArticulos();
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
  const art = articulos.find(a => a.id === articulo_id || a.articulo_id === articulo_id);
  return art ? art.nombre : '';
}

function getArticuloNombreAsync(articulo_id, row) {
  const nombre = getArticuloNombre(articulo_id);
  if (nombre) return nombre;
  if (articulosNombreCache[articulo_id]) return articulosNombreCache[articulo_id];
  fetchArticuloNombre(articulo_id).then(nombre => {
    if (row && nombre && nombre !== articulo_id) {
      row._articulo_nombre = nombre;
    }
  });
  if (row && row._articulo_nombre) return row._articulo_nombre;
  return articulo_id;
}

function getArticuloSkuById(articulo_id) {
  if (!articulo_id && articulo_id !== 0) return '';
  // Primero intenta desde los artículos de la ubicación (si lo traen)
  const artU = (Array.isArray(articulosDisponibles.value) ? articulosDisponibles.value : [])
    .find(a => a.id === articulo_id || a.articulo_id === articulo_id);
  if (artU && artU.sku) return String(artU.sku);
  // Luego intenta desde el catálogo general
  const artC = (Array.isArray(articulosCatalog.value) ? articulosCatalog.value : [])
    .find(a => a.id === articulo_id);
  return artC && artC.sku ? String(artC.sku) : '-';
}

function normalize(str) {
  return String(str ?? '').trim().toUpperCase();
}

function findArticuloInCatalogBySkuOrNombre(sku, nombre) {
  const catalog = Array.isArray(articulosCatalog.value) ? articulosCatalog.value : [];
  const nSku = normalize(sku);
  const nNom = normalize(nombre);
  let art = null;
  if (nSku) {
    art = catalog.find(a => normalize(a.sku) === nSku);
    if (art) return art;
  }
  if (nNom) {
    art = catalog.find(a => normalize(a.nombre) === nNom);
    if (art) return art;
  }
  return null;
}

function agruparStockDesdeImeis(imeis = []) {
  const mapa = new Map();
  let noResueltos = [];
  (Array.isArray(imeis) ? imeis : []).forEach(i => {
    const est = (i.status || i.estado || '').toString();
    if (est && est.toLowerCase() !== 'disponible') return; // contar solo disponibles

    // Resolver artículo por id directo o por SKU / nombre del IMEI contra el catálogo
    const resolved = findArticuloInCatalogBySkuOrNombre(i.sku, i.articulo_nombre || i.articuloNombre);
    const artId = (i.articulo_id ?? i.articuloId ?? i.articuloID) || (resolved ? resolved.id : null);
    const nombre = (i.articulo_nombre || i.articuloNombre || (resolved ? resolved.nombre : '')) || '';
    const sku = (i.sku || (resolved ? resolved.sku : '')) || '';

    // Evitar contar servicios aquí; se agrega instalación aparte
    const isServicioByNombre = normalize(nombre).includes('INSTALACION');
    if (!artId || isServicioByNombre) {
      noResueltos.push({ sku: i.sku || '', nombre, imei: i.imei, ubicacion_id: i.ubicacion_id });
      return;
    }

    if (!mapa.has(artId)) {
      mapa.set(artId, {
        id: artId,
        articulo_id: artId,
        nombre,
        sku,
        stock: 0,
        tipo: 'Producto'
      });
    }
    mapa.get(artId).stock += 1;
  });
  const lista = Array.from(mapa.values()).map(item => {
    // Enriquecer nombre/sku desde catálogo si falta
    if (!item.nombre || !item.sku) {
      const cat = (Array.isArray(articulosCatalog.value) ? articulosCatalog.value : []).find(a => a.id === item.articulo_id);
      if (cat) {
        item.nombre = item.nombre || cat.nombre;
        item.sku = item.sku || cat.sku;
      }
    }
    return item;
  });
  if (noResueltos.length) {
    try {
      console.groupCollapsed('[IMEIs] No mapeados al catálogo (revisar SKU/nombre en catálogo)');
      console.table(noResueltos);
      console.groupEnd();
    } catch (_) {}
  }
  return lista;
}

const metodoPagoOptions = [
  { label: 'Transferencia', value: 'transferencia' },
  { label: 'Depósito', value: 'deposito' }
];
</script>

<style scoped>
.ventas-container {
  /* max-width: 900px; */
  margin: 2rem auto;
  padding: 3rem;
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
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
  margin-bottom: 1.25rem;
}
.form-grid-4 { grid-template-columns: repeat(4, 1fr); }
.ventas-form-col { width: 100%; }
.ventas-form-col label { display:block; font-weight:600; margin: 0 0 .35rem 0; color: var(--color-title); }
.inline-control { display:flex; align-items:center; height: 2.5rem; }
.file-input { width: 100%; }
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
  display: grid;
  grid-template-columns: 1fr auto;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}
.acciones-footer strong { font-size: 1.05em; }
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
.faltan-chip {
  background: rgba(255, 87, 87, 0.15);
  color: #ff5757;
}
.alerta-stock {
  border: 1px solid var(--color-border);
  background: rgba(255, 87, 87, 0.08);
  border-left: 4px solid #ff5757;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  margin: 0.5rem 0 1rem;
}
.alerta-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}
.alerta-titulo {
  color: #ff5757;
  font-weight: 700;
}
.alerta-acciones {
  display: flex;
  gap: 0.5rem;
}
.alerta-tabla table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 0.5rem;
}
.alerta-tabla th, .alerta-tabla td {
  padding: 0.4rem 0.6rem;
  border-bottom: 1px solid var(--color-border);
}
.alerta-tabla .faltan {
  color: #ff5757;
  font-weight: 700;
}
@media (max-width: 1000px) {
  .ventas-form-header, .form-grid-4 { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 700px) {
  .ventas-container {
    padding: 1rem 0.2rem;
  }
  .ventas-card {
    padding: 0.5rem;
  }
  .ventas-form-header, .form-grid-4 { grid-template-columns: 1fr; gap: 0.5rem; }
  .venta-articulos-table {
    font-size: 0.95em;
    padding: 0.5rem;
  }
}
</style>
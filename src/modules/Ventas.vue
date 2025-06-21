<template>
  <div class="ventas-container">
    <h2 class="ventas-title">Registrar Orden de Venta</h2>
    <div class="ventas-card">
      <!-- Encabezado: Cliente, Folio, Fecha -->
      <div class="ventas-form-header">
        <div class="ventas-form-col">
          <label class="mb-2">Cliente</label>
          <Dropdown v-model="venta.cliente_id" :options="clientes" optionLabel="nombre" optionValue="id" placeholder="Selecciona un cliente" class="w-full" />
        </div>
        <div class="ventas-form-col">
          <label>Orden de venta nº</label>
          <InputText :value="folioPropuesto" disabled class="w-full" />
        </div>
        <div class="ventas-form-col">
          <label>Fecha de orden de venta</label>
          <Calendar v-model="venta.fecha" dateFormat="yy-mm-dd" class="w-full" />
        </div>
      </div>

      <div class="ventas-form-header">
        <div class="ventas-form-col">
          <label>N.º de cotización</label>
          <InputText v-model="venta.referencia" class="w-full" />
        </div>
        <!--
        <div class="ventas-form-col">
          <label>Fecha de envío esperada</label>
          <InputText v-model="venta.fecha_envio" type="date" class="w-full" />
        </div>
        <div class="ventas-form-col">
          <label>Términos de pago</label>
          <Dropdown
            v-model="venta.terminos_pago"
            :options="terminosPagoOptions"
            optionLabel="label"
            optionValue="value"
            placeholder="Selecciona términos de pago"
            class="w-full"
          />
        </div>
        <div class="ventas-form-col">
          <label>Método de entrega</label>
          <InputText v-model="venta.metodo_entrega" class="w-full" />
        </div>
        -->
      </div>

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
          />
        </div>
        <div class="ventas-form-col">
          <label>Descuento (%)</label>
          <InputText v-model.number="venta.descuento" type="number" min="0" max="100" class="w-full" />
        </div>
      </div>

      <h3>Artículos</h3>
      <!-- Selector de ubicación -->
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

      <!-- Selector de artículos por ubicación -->
      <div class="mb-2">
        <Button
          label="Agregar Artículo"
          icon="pi pi-plus"
          class="mb-2"
          @click="addArticulo"
          :disabled="!venta.ubicacion_id"
        />
      </div>

      <!-- Tabla de artículos -->
      <DataTable
        :value="venta.articulos"
        responsiveLayout="scroll"
        class="venta-articulos-table"
        :disabled="!venta.ubicacion_id"
      >
        <Column header="Artículo">
          <template #body="slotProps">
            <Dropdown
              v-model="slotProps.data.articulo_id"
              :options="articulosConStockUbicacion(slotProps.data)"
              optionLabel="nombre"
              optionValue="id"
              placeholder="Selecciona artículo"
              class="w-full"
              @change="onArticuloChange(slotProps.data.articulo_id, slotProps.data)"
              :disabled="articulosConStockUbicacion(slotProps.data).length === 0"
            />
          </template>
        </Column>
        <Column header="Stock">
          <template #body="slotProps">
            <span v-if="esServicio(slotProps.data.articulo_id)">NA</span>
            <span v-else>
              {{ getStockDisponible(slotProps.data.articulo_id, slotProps.data) }}
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
              :disabled="!slotProps.data.articulo_id"
              @input="validateCantidad(slotProps.data)"
            />
            <small v-if="!esServicio(slotProps.data.articulo_id) && slotProps.data.cantidad > getStockDisponible(slotProps.data.articulo_id, slotProps.data)" class="error-text">
              Máx: {{ getStockDisponible(slotProps.data.articulo_id, slotProps.data) }}
            </small>
          </template>
        </Column>
        <Column field="precio_unitario" header="Tarifa">
          <template #body="slotProps">
            <span>{{ (slotProps.data.precio_unitario ?? 0).toFixed(2) }}</span>
          </template>
        </Column>
        <Column field="subtotal" header="Importe">
          <template #body="slotProps">
            {{ ((slotProps.data.cantidad ?? 0) * (slotProps.data.precio_unitario ?? 0)).toFixed(2) }}
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
              <template v-if="esServicio(slotProps.data.articulo_id)">
                <span>NA</span>
              </template>
              <template v-else-if="mostrarColumnaIMEI(slotProps.data.articulo_id)">
                <div v-for="idx in slotProps.data.cantidad" :key="idx" style="margin-bottom: 0.2em;">
                  <Dropdown
                    v-model="slotProps.data.imeis[idx - 1]"
                    :options="imeisDisponiblesPorArticulo(slotProps.data.articulo_id, slotProps.data, idx - 1)"
                    optionLabel="imei"
                    optionValue="imei"
                    placeholder="Selecciona IMEI"
                    class="w-full imei-dropdown"
                    :disabled="!slotProps.data.articulo_id"
                    filter
                  />
                </div>
                <div v-if="slotProps.data.imeis && slotProps.data.imeis.length">
                  <span v-for="(imei, idx) in slotProps.data.imeis" :key="imei" class="imei-seleccionado" v-if="imei">
                    IMEI {{ idx + 1 }}: <span class="imei-value">{{ imei }}</span>
                  </span>
                </div>
              </template>
            </div>
          </template>
        </Column>
      </DataTable>

      <div class="mb-2">
        <label>Observaciones</label>
        <InputText v-model="venta.observaciones" class="w-full" />
      </div>

      <div class="mb-2 acciones-footer">
        <div>
          <div><strong>Subtotal:</strong> ${{ subtotalVenta.toFixed(2) }}</div>
          <div><strong>Descuento:</strong> {{ venta.descuento || 0 }}% (${{ descuentoMonto.toFixed(2) }})</div>
          <div><strong>Total (MXN):</strong> ${{ totalVenta.toFixed(2) }}</div>
        </div>
        <Button
          label="Guardar Venta"
          class="mb-2"
          @click="guardarVentaConLoading"
          :disabled="!venta.cliente_id || venta.articulos.length === 0 || loadingGuardar"
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

      <Dialog v-model:visible="ventaRegistrada" header="Venta registrada" :closable="false" :modal="true" class="ventas-dialog">
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
import Textarea from 'primevue/textarea';
import Button from 'primevue/button';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Dialog from 'primevue/dialog';
import Calendar from 'primevue/calendar';
import { ref, reactive, computed, onMounted, watch } from 'vue';
import { useToast } from 'primevue/usetoast';
import { getArticulosStockPorUbicacion } from '@/services/articulosService';
import { getImeisPorUbicacion } from '@/services/ubicacionesService';
import { useRouter } from 'vue-router';
import { registrarMovimiento } from '@/services/inventarioService';

const toast = useToast();
const router = useRouter();

const {
  today,
  clientes,
  articulosDisponibles,
  ventas,
  ventaSeleccionada,
  detalleVenta,
  imeis,
  showDialog,
  venta,
  guardarVenta,
  cargarDetalleVenta,
  articulosConStock,
  addArticulo,
  getStockDisponible,
  mostrarColumnaIMEI,
  onArticuloChange,
  removeArticulo,
  validateCantidad,
  totalVenta: totalVentaProp,
  imeisDisponiblesPorArticulo,
  getVentas
} = useVentas();

const ventaRegistrada = ref(false);
const mensajeExito = ref('La orden de venta se registró correctamente.');
const detalleVentaPDF = ref([]);
const clientePDF = ref({});
const articulosPDF = ref([]);
const showDetalleDialog = ref(false);
const loadingGuardar = ref(false);
const folioPropuesto = ref('');
const ubicaciones = ref([]);
const vendedores = ref([]);

const terminosPagoOptions = [
  { label: 'Neto 15', value: 'Neto 15' },
  { label: 'Neto 30', value: 'Neto 30' },
  { label: 'Neto 45', value: 'Neto 45' },
  { label: 'Neto 60', value: 'Neto 60' },
  { label: 'Pago Contra Entrega', value: 'Pago Contra Entrega' }
];

function generarFolioConsecutivo(ventas) {
  // Busca el mayor número de folio existente con formato SO-XXXXX
  const max = ventas
    .map(v => {
      const match = typeof v.folio === 'string' && v.folio.match(/^SO-(\d+)$/);
      return match ? parseInt(match[1], 10) : 0;
    })
    .reduce((a, b) => Math.max(a, b), 0);
  // Siguiente consecutivo
  const siguiente = max + 1;
  return `SO-${siguiente.toString().padStart(5, '0')}`;
}

onMounted(async () => {
  ubicaciones.value = await getUbicaciones();
  const ventas = await getVentas();
  folioPropuesto.value = generarFolioConsecutivo(ventas);
  venta.folio = folioPropuesto.value;

  // Cargar vendedores
  const usuarios = await getUsuarios();
  vendedores.value = usuarios.filter(u => u.perfil === 'Vendedor');
});

watch(
  () => venta.ubicacion_id,
  async (nuevaUbicacion, anteriorUbicacion) => {
    if (nuevaUbicacion !== anteriorUbicacion) {
      venta.articulos = [];
      if (nuevaUbicacion) {
        // Trae los artículos de la ubicación
        const articulosUbicacion = await getArticulosStockPorUbicacion(nuevaUbicacion);
        // Trae todos los artículos
        const todos = await getTodosArticulos();
        // Filtra solo los servicios
        const servicios = todos.filter(a => a.tipo && a.tipo.toLowerCase() === 'servicio');
        // Agrega los servicios al array de la ubicación (sin duplicar)
        servicios.forEach(serv => {
          if (!articulosUbicacion.some(a => a.id === serv.id)) {
            articulosUbicacion.push(serv);
          }
        });
        articulosDisponibles.value = articulosUbicacion;
        // Carga los IMEIs solo de esa ubicación
        imeis.value = await getImeisPorUbicacion(nuevaUbicacion);
      } else {
        articulosDisponibles.value = [];
        imeis.value = [];
      }
    }
  }
);

async function guardarVentaConLoading() {
  loadingGuardar.value = true;
  try {
    const ventas = await getVentas();
    venta.folio = generarFolioConsecutivo(ventas);

    venta.fecha = venta.fecha || new Date().toISOString().slice(0, 10);
    venta.referencia = venta.referencia || null;
    venta.fecha_envio = venta.fecha_envio || null;
    venta.terminos_pago = venta.terminos_pago || null;
    venta.metodo_entrega = venta.metodo_entrega || null;
    venta.referencia = venta.referencia || null;
    venta.vendedor = venta.vendedor || '';
    venta.almacen = venta.ubicacion_id || '';
    venta.descuento = venta.descuento || 0;
    venta.notas_cliente = venta.notas_cliente || '';
    venta.terminos_condiciones = venta.terminos_condiciones || '';
    venta.total = totalVenta.value;
    venta.observaciones = venta.observaciones || '';

    // --- MODIFICACIÓN: Forzar POST directo para asegurar guardado ---
    const { addVenta } = await import('@/services/ventasService');
    // Busca el nombre de la ubicación seleccionada
    const ubicacionObj = ubicaciones.value.find(u => u.id === venta.ubicacion_id);
    venta.almacen = ubicacionObj ? ubicacionObj.nombre : '';

    // Limpia los artículos para quitar campos no válidos y ajusta IMEIs
    const articulosLimpios = venta.articulos.flatMap(a => {
      const articulo = articulosDisponibles.value.find(art => art.id === a.articulo_id);
      if (articulo && articulo.tipo && articulo.tipo.toLowerCase() === 'servicio') {
        // Servicio: no lleva imei
        return [{
          articulo_id: a.articulo_id,
          cantidad: a.cantidad,
          precio_unitario: a.precio_unitario
        }];
      }
      // Si tiene arreglo de imeis, genera un objeto por cada imei
      if (Array.isArray(a.imeis) && a.imeis.length > 0) {
        return a.imeis
          .filter(imei => imei)
          .map(imei => ({
            articulo_id: a.articulo_id,
            cantidad: 1,
            precio_unitario: a.precio_unitario,
            imei
          }));
      }
      // Si tiene un solo imei
      if (a.imei) {
        return [{
          articulo_id: a.articulo_id,
          cantidad: 1,
          precio_unitario: a.precio_unitario,
          imei: a.imei
        }];
      }
      // Artículo normal sin imei
      return [{
        articulo_id: a.articulo_id,
        cantidad: a.cantidad,
        precio_unitario: a.precio_unitario
      }];
    });

    await addVenta({
      cliente_id: venta.cliente_id,
      fecha: venta.fecha,
      folio: venta.folio,
      referencia: venta.referencia,
      fecha_envio: venta.fecha_envio,
      terminos_pago: venta.terminos_pago,
      metodo_entrega: venta.metodo_entrega,
      vendedor: venta.vendedor,
      almacen: venta.almacen,
      descuento: venta.descuento,
      notas_cliente: venta.notas_cliente,
      terminos_condiciones: venta.terminos_condiciones,
      total: venta.total,
      observaciones: venta.observaciones,
      articulos: articulosLimpios
    });

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
    // Mostrar modal de éxito después de abrir el PDF
    ventaRegistrada.value = true;
    mensajeExito.value = 'La orden de venta se registró correctamente.';
    toast.add({ severity: 'success', summary: 'Orden de Venta registrada', detail: mensajeExito.value, life: 3000 });

    // Registrar movimientos de inventario por cada artículo con IMEI
    for (const art of venta.articulos) {
      if (art.imei) {
        await registrarMovimiento({
          usuario: 'sistema',
          evento: 'venta',
          articulo_id: art.articulo_id,
          articulo_nombre: getArticuloNombre(art.imei),
          imei: art.imei,
          ubicacion_origen: venta.almacen,
          ubicacion_destino: null,
          motivo: 'Venta de IMEI'
        });
      }
    }
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

function articulosConStockUbicacion(row = null) {
  if (!venta.ubicacion_id) return [];
  return articulosDisponibles.value.filter(art => {
    if (art.tipo && art.tipo.toLowerCase() === 'servicio') return true;
    return imeis.value.some(i =>
      i.articulo_id === art.id &&
      i.ubicacion_id === venta.ubicacion_id &&
      (i.status === 'Disponible' || i.status === 'Devuelto')
    );
  });
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
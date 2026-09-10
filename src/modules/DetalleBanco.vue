<template>
  <div class="detalle-banco-container">
    <Button icon="pi pi-arrow-left" label="Volver a Bancos" class="p-button-text mb-3" @click="router.push('/bancos')" />

    <div v-if="loading" style="text-align:center;padding:3rem;">
      <i class="pi pi-spin pi-spinner" style="font-size:2rem;"></i>
    </div>

    <template v-else>
      <div class="saldo-card">
        <span class="saldo-banco">{{ nombre }}</span>
        <span class="saldo-valor" :class="{ negativo: saldo.saldo < 0 }">{{ formatTotal(saldo.saldo) }}</span>
        <div class="saldo-desglose">
          <span class="saldo-desglose-linea">
            {{ filtroMes === 'todos' ? 'Saldo inicial' : 'Saldo inicial del mes' }}
            <b>{{ formatTotal(saldo.saldoInicial) }}</b>
            <small v-if="saldo.arrastre">(arranque {{ formatTotal(saldo.saldoInicialBase) }} + meses previos {{ formatTotal(saldo.arrastre) }})</small>
            <Button v-if="esAdmin" icon="pi pi-pencil" class="p-button-text p-button-sm" style="padding:0.15rem;" title="Editar saldo de arranque" @click="abrirSaldoInicialDialog" />
          </span>
          <span class="saldo-desglose-linea">
            + Entradas netas <b>{{ formatTotal(saldo.entradasNetas) }}</b>
            <small v-if="saldo.comision">(bruto {{ formatTotal(saldo.entradasBrutas) }} − 1% {{ formatTotal(saldo.comision) }})</small>
          </span>
          <span v-if="saldo.egresos" class="saldo-desglose-linea">− Egresos <b>{{ formatTotal(saldo.egresos) }}</b></span>
          <span v-if="saldo.retiros" class="saldo-desglose-linea">− Retiros <b>{{ formatTotal(saldo.retiros) }}</b></span>
        </div>
        <span v-if="porValidarResumen.count" class="saldo-pendiente">
          {{ porValidarResumen.count }} por validar en esta vista ({{ formatTotal(porValidarResumen.monto) }}) — no suman hasta aprobarse
        </span>
        <span v-if="saldo.pendientesCount" class="saldo-pendiente">
          En revisión: -{{ formatTotal(saldo.pendiente) }} ({{ saldo.pendientesCount }} retiro{{ saldo.pendientesCount === 1 ? '' : 's' }} por aprobar)
        </span>
        <div class="saldo-acciones">
          <Button label="Nuevo movimiento" icon="pi pi-plus" class="p-button-sm p-button-secondary" @click="abrirNuevoMovimiento" />
          <Button label="Registrar retiro" icon="pi pi-upload" class="p-button-sm p-button-danger" @click="abrirRetiroDialog" />
        </div>
      </div>

      <div class="toolbar">
        <InputText v-model="busqueda" placeholder="Buscar por nombre, usuario o IMEI..." class="toolbar-buscador" />
        <Dropdown v-model="filtroMes" :options="opcionesFiltroMes" optionLabel="label" optionValue="value" placeholder="Mes" class="toolbar-filtro" />
        <Dropdown v-model="filtroTipo" :options="opcionesFiltroTipo" optionLabel="label" optionValue="value" placeholder="Tipo" class="toolbar-filtro" />
        <Dropdown v-model="filtroValidacion" :options="opcionesFiltroValidacion" optionLabel="label" optionValue="value" placeholder="Validación" class="toolbar-filtro" />
      </div>

      <div class="movimientos-card">
        <DataTable
          :value="filasFiltradas" responsiveLayout="scroll" :paginator="filasFiltradas.length > 30" :rows="30" dataKey="key"
          :reorderableRows="!filtrosActivos" @row-reorder="onRowReorder"
        >
          <Column rowReorder headerStyle="width:3rem" :reorderableColumn="false" :title="filtrosActivos ? 'Quita los filtros para poder reordenar' : 'Arrastra para reordenar'" />
          <Column field="tipo" header="Tipo" style="width:100px">
            <template #body="{ data }"><span :class="'badge badge-' + badgeClaseTipo(data.tipo)">{{ data.tipo }}</span></template>
          </Column>
          <Column field="fecha" header="Fecha de whatsapp">
            <template #body="{ data }">
              <Calendar v-if="editando === data.key" v-model="edicion.fecha" dateFormat="dd/mm/yy" showIcon iconDisplay="input" class="edit-input" />
              <span v-else>{{ formatFecha(data.fecha) }}</span>
            </template>
          </Column>
          <Column field="nombre" header="Nombre">
            <template #body="{ data }">
              <InputText v-if="editando === data.key && data.tipo !== 'Ingreso banco'" v-model="edicion.nombre" class="edit-input" />
              <span v-else>{{ data.nombre || '—' }}</span>
            </template>
          </Column>
          <Column field="usuario" header="Usuario">
            <template #body="{ data }">
              <InputText v-if="editando === data.key && ['Ingreso banco', 'Ingreso', 'Egreso', 'Retiro'].includes(data.tipo)" v-model="edicion.usuario" class="edit-input" />
              <span v-else>{{ data.usuario || '—' }}</span>
            </template>
          </Column>
          <Column field="imeis" header="IMEIs">
            <template #body="{ data }">
              <InputText v-if="editando === data.key && data.tipo === 'Ingreso banco'" v-model="edicion.imeis" class="edit-input" />
              <span v-else>{{ data.imeis || '—' }}</span>
            </template>
          </Column>
          <Column field="fecha_real" header="Fecha de la transacción">
            <template #body="{ data }">
              <span v-if="data.tipo !== 'Ingreso banco'" class="celda-vacia">No aplica</span>
              <Calendar v-else-if="editando === data.key" v-model="edicion.fecha_real" dateFormat="dd/mm/yy" showIcon iconDisplay="input" showButtonBar class="edit-input" />
              <span v-else>{{ data.fecha_real ? formatFecha(data.fecha_real) : '—' }}</span>
            </template>
          </Column>
          <Column field="monto" header="Monto">
            <template #body="{ data }">
              <InputNumber v-if="editando === data.key" v-model="edicion.monto" mode="currency" currency="MXN" locale="es-MX" class="edit-input" />
              <span v-else :class="data.monto < 0 ? 'monto-negativo' : 'monto-positivo'">
                {{ data.monto >= 0 ? '+' : '' }}{{ formatTotal(data.monto) }}
              </span>
            </template>
          </Column>
          <Column header="Estatus">
            <template #body="{ data }">
              <span v-if="data.estatus" :class="'badge badge-' + badgeClaseEstatus(data.estatus)">{{ data.estatus }}</span>
              <span v-else class="celda-vacia">—</span>
              <i
                v-if="data.tipo === 'Ingreso banco' && data.raw.tiene_justificacion"
                class="pi pi-exclamation-triangle icono-justificacion"
                v-tooltip.top="textoJustificaciones(data.raw)"
              />
            </template>
          </Column>
          <Column header="Comprobante">
            <template #body="{ data }">
              <span v-if="!data.comprobantes.length" class="celda-vacia">—</span>
              <div v-else class="comprobantes-links">
                <span v-for="(url, i) in data.comprobantes" :key="i" class="comprobante-item">
                  <a :href="url" target="_blank" rel="noopener noreferrer" class="link-comprobante" :title="'Ver comprobante ' + (i + 1)">
                    <i class="pi pi-file" /> {{ data.comprobantes.length > 1 ? i + 1 : '' }}
                  </a>
                  <Button
                    v-if="(data.tipo === 'Ingreso' || data.tipo === 'Egreso')"
                    icon="pi pi-trash" class="p-button-sm p-button-text p-button-danger" style="padding:0.1rem;"
                    :loading="eliminandoComprobanteKey === data.key"
                    title="Eliminar comprobante"
                    @click="eliminarComprobanteMovimiento(data)"
                  />
                </span>
              </div>
            </template>
          </Column>
          <Column header="Validado" style="width:150px">
            <template #body="{ data }">
              <Dropdown
                :modelValue="data.estatusValidacion"
                :options="opcionesEstatusValidacion"
                optionLabel="label" optionValue="value"
                :class="'estatus-dropdown estatus-' + data.estatusValidacion"
                :disabled="validandoKey === data.key"
                @update:modelValue="v => cambiarEstadoValidacion(data, v)"
              />
            </template>
          </Column>
          <Column header="Acciones" style="width:220px">
            <template #body="{ data }">
              <div style="display:flex;gap:0.4rem;flex-wrap:wrap;align-items:center;">
                <template v-if="editando === data.key">
                  <Button icon="pi pi-check" class="p-button-sm p-button-success" :loading="guardando" @click="guardarEdicion(data)" />
                  <Button icon="pi pi-times" class="p-button-sm p-button-secondary" @click="editando = null" />
                </template>
                <template v-else>
                  <Button v-if="esEditable(data)" icon="pi pi-pencil" class="p-button-sm p-button-text" @click="iniciarEdicion(data)" />
                  <Button
                    v-if="data.tipo === 'Retiro'"
                    icon="pi pi-trash" class="p-button-sm p-button-text p-button-danger"
                    :loading="procesandoId === data.id" @click="eliminarRetiroFila(data)"
                  />
                  <Button
                    v-if="data.tipo === 'Ingreso' || data.tipo === 'Egreso'"
                    icon="pi pi-trash" class="p-button-sm p-button-text p-button-danger"
                    :loading="eliminandoMovimientoKey === data.key" @click="eliminarMovimientoFila(data)"
                  />
                  <Button
                    v-if="data.tipo === 'Ingreso banco'"
                    icon="pi pi-trash" class="p-button-sm p-button-text p-button-danger"
                    title="Eliminar ingreso"
                    :loading="eliminandoIngresoId === data.id" @click="eliminarIngresoFila(data)"
                  />
                  <router-link v-if="data.tipo === 'Nota'" :to="{ name: 'detalle-pago', params: { tipo: 'nota', id: data.id } }" class="p-button p-button-sm p-button-text p-button-icon-only"><i class="pi pi-eye" /></router-link>
                  <router-link v-else-if="data.tipo === 'Factura'" :to="{ name: 'detalle-factura', params: { id: data.id } }" class="p-button p-button-sm p-button-text p-button-icon-only"><i class="pi pi-eye" /></router-link>
                  <router-link v-else-if="data.tipo === 'Pago nota'" :to="{ name: 'detalle-pago', params: { tipo: 'nota', id: data.raw.nota_id } }" class="p-button p-button-sm p-button-text p-button-icon-only" v-tooltip.top="'Ver nota'"><i class="pi pi-eye" /></router-link>
                  <router-link
                    v-else-if="data.tipo === 'Ingreso banco' && data.raw.links?.[0]?.factura_id"
                    :to="{ name: 'detalle-factura', params: { id: data.raw.links[0].factura_id } }"
                    class="p-button p-button-sm p-button-text p-button-icon-only" v-tooltip.top="'Ver factura ligada'"
                  ><i class="pi pi-eye" /></router-link>
                  <router-link
                    v-else-if="data.tipo === 'Ingreso banco' && data.raw.links?.[0]?.nota_id"
                    :to="{ name: 'detalle-pago', params: { tipo: 'nota', id: data.raw.links[0].nota_id } }"
                    class="p-button p-button-sm p-button-text p-button-icon-only" v-tooltip.top="'Ver nota ligada'"
                  ><i class="pi pi-eye" /></router-link>
                </template>
              </div>
            </template>
          </Column>
        </DataTable>
      </div>
    </template>

    <!-- Dialog: nuevo movimiento manual -->
    <Dialog v-model:visible="movimientoDialogVisible" header="Nuevo movimiento" :modal="true" :style="{ width: '420px', maxWidth: '95vw' }" :draggable="false">
      <div class="form-group">
        <label>Tipo</label>
        <Dropdown v-model="nuevoMovimiento.tipo" :options="['Ingreso', 'Egreso']" class="w-full" />
      </div>
      <div class="form-group">
        <label>Concepto</label>
        <InputText v-model="nuevoMovimiento.concepto" class="w-full" placeholder="Ej: Pago a proveedor" />
      </div>
      <div class="form-group">
        <label>Fecha</label>
        <Calendar v-model="nuevoMovimientoFecha" dateFormat="dd/mm/yy" showIcon iconDisplay="input" class="w-full" />
      </div>
      <div class="form-group">
        <label>Monto</label>
        <InputNumber v-model="nuevoMovimiento.monto" mode="currency" currency="MXN" locale="es-MX" class="w-full" />
      </div>
      <div class="form-group">
        <label>Usuario (opcional)</label>
        <InputText v-model="nuevoMovimiento.usuario" class="w-full" />
      </div>
      <div class="form-group">
        <label>Referencia (opcional)</label>
        <InputText v-model="nuevoMovimiento.referencia" class="w-full" />
      </div>
      <div class="form-group">
        <label>Comprobante (opcional)</label>
        <input type="file" accept="application/pdf,image/*" @change="onMovimientoFileChange" />
      </div>
      <div class="modal-actions">
        <Button label="Registrar" icon="pi pi-check" :loading="guardandoMovimiento" @click="confirmarNuevoMovimiento" />
        <Button label="Cancelar" class="p-button-secondary" @click="movimientoDialogVisible = false" />
      </div>
    </Dialog>

    <!-- Dialog: registrar retiro -->
    <Dialog v-model:visible="retiroDialogVisible" header="Registrar retiro" :modal="true" :style="{ width: '450px', maxWidth: '95vw' }" :draggable="false">
      <div class="retiro-form">
        <div class="retiro-field">
          <label>Monto a retirar</label>
          <InputNumber v-model="retiroForm.monto" mode="currency" currency="MXN" locale="es-MX" class="w-full" />
        </div>
        <div class="retiro-field">
          <label>Motivo (opcional)</label>
          <InputText v-model="retiroForm.motivo" placeholder="Ej: Pago a proveedor" class="w-full" />
        </div>
        <div class="retiro-field">
          <label>Usuario (opcional)</label>
          <InputText v-model="retiroForm.usuario" class="w-full" />
        </div>
        <div class="retiro-field">
          <label>Fecha</label>
          <Calendar v-model="retiroFecha" dateFormat="dd/mm/yy" showIcon iconDisplay="input" class="w-full" />
        </div>
        <div class="retiro-field">
          <label>Comprobante</label>
          <input type="file" accept="application/pdf,image/*" @change="onFileChange" />
        </div>
      </div>
      <div style="display:flex;justify-content:flex-end;gap:0.75rem;margin-top:1.25rem;">
        <Button label="Cancelar" class="p-button-text" @click="retiroDialogVisible = false" />
        <Button
          label="Registrar"
          icon="pi pi-upload"
          class="p-button-danger"
          :disabled="!retiroForm.monto || !retiroArchivo"
          :loading="guardandoRetiro"
          @click="confirmarRetiro"
        />
      </div>
    </Dialog>

    <!-- Dialog: saldo inicial -->
    <Dialog v-model:visible="saldoInicialDialogVisible" header="Saldo inicial" :modal="true" :style="{ width: '400px', maxWidth: '95vw' }" :draggable="false">
      <p style="margin-top:0;font-size:0.85rem;color:var(--color-text);opacity:0.75;">
        Número de arranque de {{ nombre }}. Todo movimiento validado del banco se suma o resta encima de este valor.
      </p>
      <div class="form-group">
        <label>Saldo inicial</label>
        <InputNumber v-model="saldoInicialForm" mode="currency" currency="MXN" locale="es-MX" class="w-full" />
      </div>
      <div class="modal-actions">
        <Button label="Guardar" icon="pi pi-check" :loading="guardandoSaldoInicial" @click="confirmarSaldoInicial" />
        <Button label="Cancelar" class="p-button-secondary" @click="saldoInicialDialogVisible = false" />
      </div>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import InputNumber from 'primevue/inputnumber';
import Dropdown from 'primevue/dropdown';
import Calendar from 'primevue/calendar';
import { useToast } from 'primevue/usetoast';
import { useLoginStore } from '@/stores/loginStore';
import {
  actualizarCamposNota, actualizarValidadoNota,
  actualizarCamposFactura, actualizarValidadoFactura,
  actualizarValidadoPagoNota,
} from '@/services/pagosService';
import {
  crearRetiro, aprobarRetiro, rechazarRetiro, marcarPendienteRetiro, reordenarBancos,
  editarRetiro, eliminarRetiro, setSaldoInicial,
} from '@/services/bancosService';
import { registrarAbonoDinero, actualizarMovimientoDinero, eliminarComprobanteMovimientoDinero, eliminarMovimientoDinero } from '@/services/dineroService';
import { editarIngresoBanco, eliminarIngresoBanco } from '@/services/ingresosBancoService';
import { fetchBancosRaw, buildFilas, calcularSaldoBanco, mesKey } from '@/composables/useBancosData';

const props = defineProps({ nombre: { type: String, required: true } });
const route = useRoute();
const router = useRouter();
const toast = useToast();
const loginStore = useLoginStore();

const nombre = computed(() => props.nombre || route.params.nombre);
const esAdmin = computed(() => (loginStore.user?.perfil || '').toLowerCase() === 'admin');

const loading = ref(true);
const filasRaw = ref([]);
const procesandoId = ref(null);

const formatoMoneda = new Intl.NumberFormat('es-MX', {
  style: 'currency', currency: 'MXN', minimumFractionDigits: 2, maximumFractionDigits: 2,
});
function formatTotal(value) { return formatoMoneda.format(Number(value) || 0); }
function formatFecha(f) {
  if (!f) return '';
  const [y, m, d] = String(f).slice(0, 10).split('-');
  return `${d}/${m}/${y}`;
}
function badgeClaseTipo(tipo) {
  if (tipo === 'Nota' || tipo === 'Factura' || tipo === 'Ingreso' || tipo === 'Pago nota') return 'success';
  if (tipo === 'Egreso' || tipo === 'Retiro') return 'danger';
  return 'info';
}
function badgeClaseEstatus(estatus) {
  if (estatus === 'aprobado' || estatus === 'asignado') return 'success';
  if (estatus === 'rechazado' || estatus === 'Cancelado' || estatus === 'cancelado') return 'danger';
  if (estatus === 'parcial' || estatus === 'sin_asignar') return 'warning';
  return 'warning';
}
// Tooltip del ⚠️ de conciliación: junta las justificaciones de todas las
// notas ligadas a este ingreso cuyo monto no cuadró exacto (ver
// requiere_justificacion en ingreso_banco_notas, backend main.py).
function textoJustificaciones(ingresoRaw) {
  return (ingresoRaw.links || [])
    .filter(l => l.requiere_justificacion)
    .map(l => `${l.factura_id ? `Factura #${l.factura_id}` : `Nota #${l.nota_id}`} (dif. $${Number(l.diferencia).toFixed(2)}): ${(l.conceptos || []).map(c => `${c.concepto} $${Number(c.monto).toFixed(2)}`).join(', ') || 'sin conceptos'}`)
    .join('\n') || 'Requiere justificación';
}

const filasBanco = computed(() => filasRaw.value.filter(f => f.banco === nombre.value));
const saldosIncialesPorBanco = ref({});
const nombresMes = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];
function labelMes(key) {
  const [y, m] = key.split('-');
  return `${nombresMes[Number(m) - 1]} ${y}`;
}

const busqueda = ref('');
const filtroMes = ref(mesKey(new Date()));  // arranca en el mes en curso
const filtroTipo = ref('todos');
const opcionesFiltroTipo = [
  { label: 'Todos', value: 'todos' },
  { label: 'Nota', value: 'Nota' },
  { label: 'Factura', value: 'Factura' },
  { label: 'Ingreso', value: 'Ingreso' },
  { label: 'Egreso', value: 'Egreso' },
  { label: 'Retiro', value: 'Retiro' },
  { label: 'Pago nota', value: 'Pago nota' },
  { label: 'Ingreso banco', value: 'Ingreso banco' },
];
const filtroValidacion = ref('todos');
const opcionesFiltroValidacion = [
  { label: 'Todas', value: 'todos' },
  { label: 'Por validar', value: 'pendiente' },
  { label: 'Validadas', value: 'aprobado' },
  { label: 'Rechazadas', value: 'rechazado' },
];

const saldo = computed(() => calcularSaldoBanco(
  filasRaw.value, nombre.value, saldosIncialesPorBanco.value,
  filtroMes.value === 'todos' ? null : filtroMes.value,
));
const opcionesFiltroMes = computed(() => {
  // Siempre incluye el mes en curso aunque no tenga movimientos todavía —
  // es el valor por defecto y el dropdown debe poder mostrarlo.
  const keys = [...new Set([mesKey(new Date()), ...filasBanco.value.map(f => mesKey(f.fecha))].filter(Boolean))].sort().reverse();
  return [{ label: 'Todos los meses', value: 'todos' }, ...keys.map(k => ({ label: labelMes(k), value: k }))];
});

// Orden manual (flechas subir/bajar), igual que la tabla combinada de antes:
// orden_manual null (fila nunca reordenada, incluye las recién llegadas) va
// antes que las ya ordenadas, así lo nuevo aparece arriba sin enterrarse.
const filasOrdenadas = computed(() => {
  const arr = [...filasBanco.value];
  arr.sort((a, b) => {
    const oa = a.orden_manual, ob = b.orden_manual;
    if (oa != null && ob != null) return oa - ob;
    if (oa != null) return 1;
    if (ob != null) return -1;
    return new Date(b.fecha) - new Date(a.fecha);
  });
  return arr;
});

// filtroMes NO cuenta aquí: el reordenamiento opera sobre filasOrdenadas
// completa (sin filtrar por mes), así que reordenar con mes puesto es seguro.
const filtrosActivos = computed(() => !!(
  busqueda.value.trim() || filtroTipo.value !== 'todos' || filtroValidacion.value !== 'todos'
));

const filasFiltradas = computed(() => {
  const q = busqueda.value.trim().toLowerCase();
  return filasOrdenadas.value.filter(f => {
    if (q && !(
      String(f.nombre || '').toLowerCase().includes(q) ||
      String(f.usuario || '').toLowerCase().includes(q) ||
      String(f.imeis || '').toLowerCase().includes(q)
    )) return false;
    if (filtroMes.value !== 'todos' && mesKey(f.fecha) !== filtroMes.value) return false;
    if (filtroTipo.value !== 'todos' && f.tipo !== filtroTipo.value) return false;
    if (filtroValidacion.value !== 'todos' && f.estatusValidacion !== filtroValidacion.value) return false;
    return true;
  });
});

// Resumen "por validar" acotado a lo que se ve en la tabla (respeta búsqueda,
// mes y tipo). Todas cuentan para el saldo al aprobarse — ya no hay corte.
const porValidarResumen = computed(() => {
  const noCancelada = (f) =>
    !(f.tipo === 'Nota' && f.raw?.status === 'cancelado') &&
    !(f.tipo === 'Factura' && f.raw?.status === 'Cancelado');
  const pend = filasFiltradas.value.filter(f => f.estatusValidacion === 'pendiente' && noCancelada(f));
  return {
    count: pend.length,
    monto: pend.reduce((s, f) => s + Math.abs(f.monto), 0),
  };
});

// Reordenar arrastrando filas (PrimeVue rowReorder) — reemplaza las flechas
// subir/bajar, permite mover una fila varios lugares de un solo jalón.
// Deshabilitado con filtros activos (event.value vendría de la lista filtrada,
// no de filasOrdenadas completa, y desalinearía los índices).
async function onRowReorder(event) {
  const orden = event.value.map((f, i) => ({ key: f.key, orden: i }));
  try {
    await reordenarBancos(orden);
    toast.add({ severity: 'success', summary: 'Orden actualizado', detail: 'Fila movida.', life: 2000 });
    await cargar(false);
  } catch {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo reordenar.', life: 3500 });
  }
}

// ── Edición inline (nombre, monto) ──
const editando = ref(null);
const edicion = ref({ nombre: '', monto: 0, fecha: null, usuario: '', imeis: '', fecha_real: null });
const guardando = ref(false);

function esEditable(fila) {
  if (fila.tipo === 'Retiro') return fila.estatus === 'pendiente';
  return ['Nota', 'Factura', 'Ingreso', 'Egreso', 'Ingreso banco'].includes(fila.tipo);
}
function iniciarEdicion(fila) {
  editando.value = fila.key;
  // El monto de un retiro se guarda negativo en la fila (para sumar/restar
  // directo al saldo) — al editar se muestra en positivo, como lo capturó el usuario.
  edicion.value = {
    nombre: fila.nombre,
    monto: fila.tipo === 'Retiro' ? -fila.monto : fila.monto,
    fecha: fila.fecha ? fechaLocal(fila.fecha) : new Date(),
    usuario: fila.usuario || '',
    imeis: fila.imeis || '',
    fecha_real: fila.fecha_real ? fechaLocal(fila.fecha_real) : null,
  };
}

async function guardarEdicion(fila) {
  guardando.value = true;
  try {
    const fecha = fechaISO(edicion.value.fecha);
    if (fila.tipo === 'Nota') {
      await actualizarCamposNota(fila.id, { cliente: edicion.value.nombre, total: edicion.value.monto, fecha });
    } else if (fila.tipo === 'Factura') {
      await actualizarCamposFactura(fila.id, { cliente: edicion.value.nombre, total: edicion.value.monto, fecha });
    } else if (fila.tipo === 'Ingreso' || fila.tipo === 'Egreso') {
      await actualizarMovimientoDinero(fila.id, { banco: nombre.value, concepto: edicion.value.nombre, monto: Number(edicion.value.monto) || 0, usuario: edicion.value.usuario || null, fecha });
    } else if (fila.tipo === 'Retiro') {
      await editarRetiro(fila.id, { monto: Number(edicion.value.monto) || 0, motivo: edicion.value.nombre, usuario: edicion.value.usuario || null, fecha });
    } else if (fila.tipo === 'Ingreso banco') {
      await editarIngresoBanco(fila.id, {
        monto: Number(edicion.value.monto) || 0,
        imeis: String(edicion.value.imeis || '').split(',').map(s => s.trim()).filter(Boolean),
        usuario: edicion.value.usuario || null,
        fecha_transaccion: fecha,
        fecha_transaccion_real: edicion.value.fecha_real ? fechaISO(edicion.value.fecha_real) : null,
      });
    }
    toast.add({ severity: 'success', summary: 'Guardado', detail: 'Cambios guardados.', life: 2500 });
    editando.value = null;
    await cargar(false);
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: e?.response?.data?.detail || 'No se pudo guardar.', life: 4000 });
  }
  guardando.value = false;
}

const eliminandoMovimientoKey = ref(null);
async function eliminarMovimientoFila(fila) {
  eliminandoMovimientoKey.value = fila.key;
  try {
    await eliminarMovimientoDinero(fila.id);
    toast.add({ severity: 'success', summary: 'Eliminado', detail: 'Movimiento eliminado.', life: 2500 });
    await cargar(false);
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: e?.response?.data?.detail || 'No se pudo eliminar el movimiento.', life: 4000 });
  }
  eliminandoMovimientoKey.value = null;
}

async function eliminarRetiroFila(fila) {
  procesandoId.value = fila.id;
  try {
    await eliminarRetiro(fila.id);
    toast.add({ severity: 'success', summary: 'Eliminado', detail: 'Retiro eliminado.', life: 2500 });
    await cargar(false);
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: e?.response?.data?.detail || 'No se pudo eliminar el retiro.', life: 4000 });
  }
  procesandoId.value = null;
}

// Un solo selector con 3 estados (pendiente/validado/rechazado) para toda fila
// — reemplaza el toggle booleano de Validado y los botones separados de
// Aprobar/Rechazar de Retiro. Cualquier usuario logueado puede moverlo, no
// solo Admin. cargar(false) para no tapar la tabla con el spinner de carga
// inicial en cada cambio, solo refresca los datos en su lugar.
const opcionesEstatusValidacion = [
  { label: 'Pendiente', value: 'pendiente' },
  { label: 'Validado', value: 'aprobado' },
  { label: 'Rechazado', value: 'rechazado' },
];
const CODIGO_POR_ESTADO = { pendiente: 0, aprobado: 1, rechazado: 2 };
const validandoKey = ref(null);
async function cambiarEstadoValidacion(fila, nuevoEstado) {
  if (nuevoEstado === fila.estatusValidacion) return;
  validandoKey.value = fila.key;
  try {
    if (fila.tipo === 'Retiro') {
      if (nuevoEstado === 'aprobado') await aprobarRetiro(fila.id);
      else if (nuevoEstado === 'rechazado') await rechazarRetiro(fila.id);
      else await marcarPendienteRetiro(fila.id);
    } else if (fila.tipo === 'Nota') {
      await actualizarValidadoNota(fila.id, nuevoEstado);
    } else if (fila.tipo === 'Factura') {
      await actualizarValidadoFactura(fila.id, nuevoEstado);
    } else if (fila.tipo === 'Pago nota') {
      await actualizarValidadoPagoNota(fila.raw.nota_id, fila.id, nuevoEstado);
    } else if (fila.tipo === 'Ingreso banco') {
      await editarIngresoBanco(fila.id, { validado: CODIGO_POR_ESTADO[nuevoEstado] });
    } else {
      await actualizarMovimientoDinero(fila.id, { validado: CODIGO_POR_ESTADO[nuevoEstado] });
    }
    const etiqueta = opcionesEstatusValidacion.find(o => o.value === nuevoEstado)?.label || nuevoEstado;
    toast.add({ severity: 'success', summary: 'Estatus actualizado', detail: `Marcado como ${etiqueta}.`, life: 2000 });
    await cargar(false);
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: e?.response?.data?.detail || 'No se pudo actualizar el estatus.', life: 4000 });
  }
  validandoKey.value = null;
}

// ── Nuevo movimiento manual (banco fijo = este) ──
const movimientoDialogVisible = ref(false);
const nuevoMovimiento = ref({ tipo: 'Ingreso', concepto: '', monto: 0, referencia: '', usuario: '' });
const nuevoMovimientoFecha = ref(new Date());
const nuevoMovimientoArchivo = ref(null);
const guardandoMovimiento = ref(false);

function abrirNuevoMovimiento() {
  nuevoMovimiento.value = { tipo: 'Ingreso', concepto: '', monto: 0, referencia: '', usuario: '' };
  nuevoMovimientoFecha.value = new Date();
  nuevoMovimientoArchivo.value = null;
  movimientoDialogVisible.value = true;
}
function onMovimientoFileChange(event) {
  const files = event?.target?.files;
  nuevoMovimientoArchivo.value = files && files.length ? files[0] : null;
}
async function confirmarNuevoMovimiento() {
  if (!nuevoMovimiento.value.concepto || !nuevoMovimiento.value.monto) {
    toast.add({ severity: 'warn', summary: 'Faltan datos', detail: 'Concepto y monto son obligatorios.', life: 3000 });
    return;
  }
  guardandoMovimiento.value = true;
  try {
    await registrarAbonoDinero({
      fecha: fechaISO(nuevoMovimientoFecha.value),
      tipo: nuevoMovimiento.value.tipo,
      concepto: nuevoMovimiento.value.concepto,
      monto: Number(nuevoMovimiento.value.monto),
      referencia: nuevoMovimiento.value.referencia,
      usuario: nuevoMovimiento.value.usuario || undefined,
      banco: nombre.value,
      archivo: nuevoMovimientoArchivo.value,
    });
    toast.add({ severity: 'success', summary: 'Registrado', detail: 'Movimiento registrado.', life: 2500 });
    movimientoDialogVisible.value = false;
    await cargar(false);
  } catch {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo registrar el movimiento.', life: 4000 });
  }
  guardandoMovimiento.value = false;
}

const eliminandoComprobanteKey = ref(null);
async function eliminarComprobanteMovimiento(fila) {
  eliminandoComprobanteKey.value = fila.key;
  try {
    await eliminarComprobanteMovimientoDinero(fila.id);
    toast.add({ severity: 'success', summary: 'Eliminado', detail: 'Comprobante eliminado.', life: 2500 });
    await cargar(false);
  } catch {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo eliminar el comprobante.', life: 4000 });
  }
  eliminandoComprobanteKey.value = null;
}

// ── Eliminar ingreso bancario (editar es inline en la tabla, ver
// guardarEdicion; crearlo vive un paso antes en Bancos.vue, donde se elige
// el banco de destino). Ver ingresosBancoService.js y el bloque "Ingresos
// bancarios" en main.py para el flujo de conciliación con nota. ──
const eliminandoIngresoId = ref(null);

// fecha_transaccion es DATE puro ("2026-09-05", sin hora) — new Date() de un
// string así lo interpreta como UTC y lo corre un día al mostrarlo en horario
// local negativo (México). Se arma en local con año/mes/día para evitar el corrimiento.
function fechaLocal(f) {
  const [y, m, d] = String(f).slice(0, 10).split('-').map(Number);
  return new Date(y, m - 1, d);
}
function fechaISO(d) {
  const dt = d instanceof Date ? d : new Date(d);
  return `${dt.getFullYear()}-${String(dt.getMonth() + 1).padStart(2, '0')}-${String(dt.getDate()).padStart(2, '0')}`;
}
// Si ya está ligado a nota(s), el backend rechaza el borrado a menos que se
// mande forzar=true — confirmamos con el usuario mostrando cuáles notas se
// desligarían antes de reintentar con forzar.
async function eliminarIngresoFila(fila) {
  eliminandoIngresoId.value = fila.id;
  try {
    await eliminarIngresoBanco(fila.id);
    toast.add({ severity: 'success', summary: 'Eliminado', detail: 'Ingreso eliminado.', life: 2500 });
    await cargar(false);
  } catch (e) {
    const detail = e?.response?.data?.detail || '';
    if (detail.includes('Ligado a nota')) {
      if (confirm(`${detail}\n\n¿Eliminar de todas formas? Esto desliga el ingreso de esa(s) nota(s).`)) {
        try {
          await eliminarIngresoBanco(fila.id, true);
          toast.add({ severity: 'success', summary: 'Eliminado', detail: 'Ingreso eliminado y desligado.', life: 2500 });
          await cargar(false);
        } catch (e2) {
          toast.add({ severity: 'error', summary: 'Error', detail: e2?.response?.data?.detail || 'No se pudo eliminar el ingreso.', life: 4000 });
        }
      }
    } else {
      toast.add({ severity: 'error', summary: 'Error', detail: detail || 'No se pudo eliminar el ingreso.', life: 4000 });
    }
  }
  eliminandoIngresoId.value = null;
}

// ── Registrar retiro (banco fijo = este) ──
const retiroDialogVisible = ref(false);
const retiroForm = ref({ monto: null, motivo: '', usuario: '' });
const retiroFecha = ref(new Date());
const retiroArchivo = ref(null);
const guardandoRetiro = ref(false);

function abrirRetiroDialog() {
  retiroForm.value = { monto: null, motivo: '', usuario: '' };
  retiroFecha.value = new Date();
  retiroArchivo.value = null;
  retiroDialogVisible.value = true;
}
function onFileChange(event) {
  const files = event?.target?.files;
  retiroArchivo.value = files && files.length ? files[0] : null;
}
async function confirmarRetiro() {
  if (!retiroForm.value.monto || !retiroArchivo.value) return;
  guardandoRetiro.value = true;
  try {
    await crearRetiro({
      banco: nombre.value,
      monto: retiroForm.value.monto,
      motivo: retiroForm.value.motivo,
      usuario: retiroForm.value.usuario,
      fecha: fechaISO(retiroFecha.value),
      archivo: retiroArchivo.value,
    });
    toast.add({ severity: 'success', summary: 'Registrado', detail: 'Retiro registrado, pendiente de aprobación.', life: 3000 });
    retiroDialogVisible.value = false;
    await cargar(false);
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: e?.response?.data?.detail || 'No se pudo registrar el retiro.', life: 4000 });
  }
  guardandoRetiro.value = false;
}

async function cargar(resetLoading = true) {
  if (resetLoading) loading.value = true;
  try {
    const raw = await fetchBancosRaw();
    filasRaw.value = buildFilas(raw);
    saldosIncialesPorBanco.value = raw.saldosIncialesPorBanco;
  } catch {
    filasRaw.value = [];
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo cargar el estado de cuenta.', life: 4000 });
  }
  loading.value = false;
}

// ── Saldo inicial (admin) — número de arranque; los movimientos validados
// se suman/restan encima. Sin cierre de mes ni fecha de corte. ──
const saldoInicialDialogVisible = ref(false);
const saldoInicialForm = ref(0);
const guardandoSaldoInicial = ref(false);

function abrirSaldoInicialDialog() {
  saldoInicialForm.value = saldo.value.saldoInicialBase;
  saldoInicialDialogVisible.value = true;
}
async function confirmarSaldoInicial() {
  guardandoSaldoInicial.value = true;
  try {
    await setSaldoInicial(nombre.value, Number(saldoInicialForm.value) || 0);
    toast.add({ severity: 'success', summary: 'Guardado', detail: 'Saldo inicial actualizado.', life: 2500 });
    saldoInicialDialogVisible.value = false;
    await cargar(false);
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: e?.response?.data?.detail || 'No se pudo guardar el saldo inicial.', life: 4000 });
  }
  guardandoSaldoInicial.value = false;
}

onMounted(cargar);
</script>

<style scoped>
.detalle-banco-container {
  margin: 2rem auto;
  padding: 2rem 1.5rem;
}
.mb-3 { margin-bottom: 1rem; }
.saldo-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.35rem;
  padding: 2rem;
  margin-bottom: 1.5rem;
  border-radius: 16px;
  background: var(--color-card);
  border: 1px solid var(--color-border);
}
.saldo-banco {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--color-title);
}
.saldo-valor {
  font-size: 2.6rem;
  font-weight: 800;
  color: var(--color-success);
}
.saldo-valor.negativo {
  color: var(--color-error);
}
.saldo-inicial-info {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.8rem;
  color: var(--color-text);
  opacity: 0.7;
}
.saldo-desglose {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.15rem;
  margin-top: 0.25rem;
  font-size: 0.82rem;
  color: var(--color-text);
  opacity: 0.85;
}
.saldo-desglose-linea {
  display: flex;
  align-items: center;
  gap: 0.35rem;
}
.saldo-desglose-linea b { font-weight: 700; }
.saldo-desglose-linea small { opacity: 0.7; }
.saldo-pendiente {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--color-warning);
}
.saldo-acciones {
  display: flex;
  gap: 0.75rem;
  margin-top: 1rem;
}

.toolbar {
  display: flex; flex-wrap: wrap; gap: 0.75rem; align-items: center;
  margin-bottom: 1.25rem; padding: 1rem 1.1rem; border-radius: 16px;
  background: var(--color-card); border: 1px solid var(--color-border);
}
.toolbar-buscador { flex: 1; min-width: 220px; }
.toolbar-filtro { min-width: 180px; }

.movimientos-card {
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  border-radius: 14px;
  background: var(--color-card);
  border: 1px solid var(--color-border);
}
.monto-positivo { color: var(--color-success); font-weight: 700; }
.monto-negativo { color: var(--color-error); font-weight: 700; }
.comprobantes-links { display: flex; gap: 0.4rem; flex-wrap: wrap; }
.comprobante-item { display: flex; align-items: center; gap: 0.1rem; }
.link-comprobante { color: var(--color-primary); font-weight: 600; text-decoration: none; }
.celda-vacia { color: var(--color-border); }
.edit-input { width: 100%; min-width: 130px; }
.form-group { margin-bottom: 1rem; }
.form-group label { display: block; font-weight: 600; margin-bottom: 0.4rem; font-size: 0.85rem; }
.modal-actions { display: flex; gap: 1rem; justify-content: flex-end; padding-top: 0.5rem; }
.badge {
  display: inline-flex; align-items: center; padding: 0.25rem 0.75rem;
  border-radius: 1rem; font-size: 0.78rem; font-weight: 700;
}
.badge-success { background: color-mix(in srgb, var(--color-success) 22%, transparent); color: var(--color-success); }
.badge-warning { background: color-mix(in srgb, var(--color-warning) 25%, transparent); color: var(--color-warning); }
.badge-danger  { background: color-mix(in srgb, var(--color-error) 20%, transparent); color: var(--color-error); }
.badge-info { background: color-mix(in srgb, var(--color-primary) 18%, transparent); color: var(--color-primary); }
.icono-justificacion { color: var(--color-warning); margin-left: 0.4rem; cursor: help; }
.retiro-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.retiro-field label {
  display: block;
  font-weight: 600;
  margin-bottom: 0.35rem;
  font-size: 0.85rem;
}
.w-full { width: 100%; }
.estatus-dropdown { width: 100%; }
.estatus-dropdown.estatus-aprobado :deep(.p-dropdown-label) { color: var(--color-success); font-weight: 700; }
.estatus-dropdown.estatus-rechazado :deep(.p-dropdown-label) { color: var(--color-error); font-weight: 700; }
.estatus-dropdown.estatus-pendiente :deep(.p-dropdown-label) { color: var(--color-warning); font-weight: 700; }

@media (max-width: 768px) {
  .detalle-banco-container {
    margin: 1rem auto;
    padding: 1rem 0.75rem;
  }
  .saldo-card { padding: 1.25rem; }
}
</style>

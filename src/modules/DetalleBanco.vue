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
        <span class="saldo-inicial-info">
          Saldo inicial: {{ formatTotal(saldo.saldoInicial) }}
          <Button v-if="esAdmin" icon="pi pi-pencil" class="p-button-text p-button-sm" style="padding:0.15rem;" @click="abrirSaldoInicialDialog" />
        </span>
        <span v-if="saldo.pendientesCount" class="saldo-pendiente">
          En revisión: -{{ formatTotal(saldo.pendiente) }} ({{ saldo.pendientesCount }} retiro{{ saldo.pendientesCount === 1 ? '' : 's' }} por aprobar)
        </span>
        <div class="saldo-acciones">
          <Button label="Nuevo movimiento" icon="pi pi-plus" class="p-button-sm p-button-secondary" @click="abrirNuevoMovimiento" />
          <Button label="Registrar retiro" icon="pi pi-upload" class="p-button-sm p-button-danger" @click="abrirRetiroDialog" />
          <Button v-if="esAdmin" label="Cerrar mes" icon="pi pi-lock" class="p-button-sm p-button-outlined" @click="abrirCerrarMes" />
        </div>
      </div>

      <div class="toolbar">
        <InputText v-model="busqueda" placeholder="Buscar por nombre, usuario o IMEI..." class="toolbar-buscador" />
        <Dropdown v-model="filtroMes" :options="opcionesFiltroMes" optionLabel="label" optionValue="value" placeholder="Mes" class="toolbar-filtro" />
        <Dropdown v-model="filtroTipo" :options="opcionesFiltroTipo" optionLabel="label" optionValue="value" placeholder="Tipo" class="toolbar-filtro" />
      </div>

      <div class="movimientos-card">
        <DataTable :value="filasFiltradas" responsiveLayout="scroll" :paginator="filasFiltradas.length > 30" :rows="30" dataKey="key">
          <Column header="Orden" headerStyle="width:3.5rem" style="text-align:center;">
            <template #body="{ data }">
              <div style="display:flex;flex-direction:column;gap:0.1rem;" :title="filtrosActivos ? 'Quita los filtros para poder reordenar' : ''">
                <Button
                  icon="pi pi-chevron-up" class="p-button-sm p-button-text"
                  style="padding:0.15rem;width:1.8rem;height:1.4rem;"
                  :disabled="filtrosActivos || esPrimeraFila(data) || moviendoKey !== null"
                  :loading="moviendoKey === data.key"
                  @click="moverFila(data, -1)"
                />
                <Button
                  icon="pi pi-chevron-down" class="p-button-sm p-button-text"
                  style="padding:0.15rem;width:1.8rem;height:1.4rem;"
                  :disabled="filtrosActivos || esUltimaFila(data) || moviendoKey !== null"
                  @click="moverFila(data, 1)"
                />
              </div>
            </template>
          </Column>
          <Column field="tipo" header="Tipo" style="width:100px">
            <template #body="{ data }"><span :class="'badge badge-' + badgeClaseTipo(data.tipo)">{{ data.tipo }}</span></template>
          </Column>
          <Column field="fecha" header="Fecha">
            <template #body="{ data }">{{ formatFecha(data.fecha) }}</template>
          </Column>
          <Column field="nombre" header="Nombre">
            <template #body="{ data }">
              <InputText v-if="editando === data.key" v-model="edicion.nombre" class="edit-input" />
              <span v-else>{{ data.nombre || '—' }}</span>
            </template>
          </Column>
          <Column field="usuario" header="Usuario">
            <template #body="{ data }">{{ data.usuario || '—' }}</template>
          </Column>
          <Column field="imeis" header="IMEIs">
            <template #body="{ data }">{{ data.imeis || '—' }}</template>
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
            </template>
          </Column>
          <Column header="Comprobante">
            <template #body="{ data }">
              <span v-if="!data.comprobantes.length" class="celda-vacia">—</span>
              <div v-else class="comprobantes-links">
                <a v-for="(url, i) in data.comprobantes" :key="i" :href="url" target="_blank" rel="noopener noreferrer" class="link-comprobante" :title="'Ver comprobante ' + (i + 1)">
                  <i class="pi pi-file" /> {{ data.comprobantes.length > 1 ? i + 1 : '' }}
                </a>
              </div>
            </template>
          </Column>
          <Column header="Validado" style="width:110px">
            <template #body="{ data }">
              <Button
                :icon="data.validado ? 'pi pi-check-circle' : 'pi pi-circle'"
                :label="data.validado ? 'Validado' : 'Validar'"
                :class="'p-button-sm ' + (data.validado ? 'p-button-success' : 'p-button-outlined p-button-secondary')"
                :loading="validando === data.key"
                @click="toggleValidado(data)"
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
                    v-if="data.tipo === 'Retiro' && data.estatus === 'pendiente'"
                    icon="pi pi-trash" class="p-button-sm p-button-text p-button-danger"
                    :loading="procesandoId === data.id" @click="eliminarRetiroFila(data)"
                  />
                  <Button
                    v-if="data.tipo === 'Retiro' && data.estatus === 'pendiente' && esAdmin"
                    icon="pi pi-check" label="Aprobar" class="p-button-sm p-button-success"
                    :loading="procesandoId === data.id" @click="aprobar(data.id)"
                  />
                  <Button
                    v-if="data.tipo === 'Retiro' && data.estatus === 'pendiente' && esAdmin"
                    icon="pi pi-times" label="Rechazar" class="p-button-sm p-button-danger p-button-outlined"
                    :loading="procesandoId === data.id" @click="rechazar(data.id)"
                  />
                  <router-link v-if="data.tipo === 'Nota'" :to="{ name: 'detalle-pago', params: { tipo: 'nota', id: data.id } }" class="p-button p-button-sm p-button-text p-button-icon-only"><i class="pi pi-eye" /></router-link>
                  <router-link v-else-if="data.tipo === 'Factura'" :to="{ name: 'detalle-factura', params: { id: data.id } }" class="p-button p-button-sm p-button-text p-button-icon-only"><i class="pi pi-eye" /></router-link>
                  <router-link v-else-if="data.tipo === 'Pago nota'" :to="{ name: 'detalle-pago', params: { tipo: 'nota', id: data.raw.nota_id } }" class="p-button p-button-sm p-button-text p-button-icon-only" v-tooltip.top="'Ver nota'"><i class="pi pi-eye" /></router-link>
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
        <label>Monto</label>
        <InputNumber v-model="nuevoMovimiento.monto" mode="currency" currency="MXN" locale="es-MX" class="w-full" />
      </div>
      <div class="form-group">
        <label>Referencia (opcional)</label>
        <InputText v-model="nuevoMovimiento.referencia" class="w-full" />
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

    <!-- Dialog: saldo inicial / cerrar mes (mismo mecanismo: fija saldo + fecha de corte) -->
    <Dialog v-model:visible="saldoInicialDialogVisible" :header="modoCierre ? 'Cerrar mes' : 'Saldo inicial'" :modal="true" :style="{ width: '400px', maxWidth: '95vw' }" :draggable="false">
      <p style="margin-top:0;font-size:0.85rem;color:var(--color-text);opacity:0.75;">
        <template v-if="modoCierre">
          Fija el saldo actual de {{ nombre }} como punto de partida — los movimientos de hoy hacia atrás quedan
          "horneados" en este número y no se vuelven a sumar. Los retiros pendientes se siguen mostrando igual.
        </template>
        <template v-else>
          Saldo con el que arranca {{ nombre }} al pasar a producción. Se suma a los movimientos posteriores a hoy.
        </template>
      </p>
      <div class="form-group">
        <label>{{ modoCierre ? 'Saldo a fijar' : 'Saldo inicial' }}</label>
        <InputNumber v-model="saldoInicialForm" mode="currency" currency="MXN" locale="es-MX" class="w-full" />
      </div>
      <div class="modal-actions">
        <Button :label="modoCierre ? 'Confirmar cierre' : 'Guardar'" icon="pi pi-check" :loading="guardandoSaldoInicial" @click="confirmarSaldoInicial" />
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
import { useToast } from 'primevue/usetoast';
import { useLoginStore } from '@/stores/loginStore';
import {
  actualizarCamposNota, actualizarValidadoNota,
  actualizarCamposFactura, actualizarValidadoFactura,
  actualizarValidadoPagoNota,
} from '@/services/pagosService';
import {
  crearRetiro, aprobarRetiro, rechazarRetiro, actualizarValidadoRetiro, reordenarBancos,
  editarRetiro, eliminarRetiro, setSaldoInicial,
} from '@/services/bancosService';
import { registrarAbonoDinero, actualizarMovimientoDinero } from '@/services/dineroService';
import { fetchBancosRaw, buildFilas, calcularSaldoBanco } from '@/composables/useBancosData';

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
  const d = new Date(f);
  return `${String(d.getDate()).padStart(2, '0')}/${String(d.getMonth() + 1).padStart(2, '0')}/${d.getFullYear()}`;
}
function badgeClaseTipo(tipo) {
  if (tipo === 'Nota' || tipo === 'Factura' || tipo === 'Ingreso' || tipo === 'Pago nota') return 'success';
  if (tipo === 'Egreso' || tipo === 'Retiro') return 'danger';
  return 'info';
}
function badgeClaseEstatus(estatus) {
  if (estatus === 'aprobado') return 'success';
  if (estatus === 'rechazado' || estatus === 'Cancelado' || estatus === 'cancelado') return 'danger';
  return 'warning';
}

const filasBanco = computed(() => filasRaw.value.filter(f => f.banco === nombre.value));
const saldosIncialesPorBanco = ref({});
const saldo = computed(() => calcularSaldoBanco(filasRaw.value, nombre.value, saldosIncialesPorBanco.value));

function mesKey(fecha) {
  if (!fecha) return null;
  const d = new Date(fecha);
  if (isNaN(d)) return null;
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`;
}
const nombresMes = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];
function labelMes(key) {
  const [y, m] = key.split('-');
  return `${nombresMes[Number(m) - 1]} ${y}`;
}

const busqueda = ref('');
const filtroMes = ref('todos');
const filtroTipo = ref('todos');
const opcionesFiltroTipo = [
  { label: 'Todos', value: 'todos' },
  { label: 'Nota', value: 'Nota' },
  { label: 'Factura', value: 'Factura' },
  { label: 'Ingreso', value: 'Ingreso' },
  { label: 'Egreso', value: 'Egreso' },
  { label: 'Retiro', value: 'Retiro' },
  { label: 'Pago nota', value: 'Pago nota' },
];
const opcionesFiltroMes = computed(() => {
  const keys = [...new Set(filasBanco.value.map(f => mesKey(f.fecha)).filter(Boolean))].sort().reverse();
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
  busqueda.value.trim() || filtroTipo.value !== 'todos'
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
    return true;
  });
});

// Mover una fila un lugar arriba/abajo (adyacente en filasOrdenadas, sin
// filtros — mover con filtros puestos intercambiaría con una fila que ni se ve).
const moviendoKey = ref(null);
function esPrimeraFila(fila) {
  return filasOrdenadas.value[0]?.key === fila.key;
}
function esUltimaFila(fila) {
  const lista = filasOrdenadas.value;
  return lista[lista.length - 1]?.key === fila.key;
}
async function moverFila(fila, direccion) {
  const lista = [...filasOrdenadas.value];
  const idx = lista.findIndex(f => f.key === fila.key);
  const destino = idx + direccion;
  if (idx === -1 || destino < 0 || destino >= lista.length) return;
  [lista[idx], lista[destino]] = [lista[destino], lista[idx]];

  moviendoKey.value = fila.key;
  try {
    const orden = lista.map((f, i) => ({ key: f.key, orden: i }));
    await reordenarBancos(orden);
    await cargar(false);
  } catch {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo mover la fila.', life: 3500 });
  }
  moviendoKey.value = null;
}

// ── Edición inline (nombre, monto) ──
const editando = ref(null);
const edicion = ref({ nombre: '', monto: 0 });
const guardando = ref(false);

function esEditable(fila) {
  if (fila.tipo === 'Retiro') return fila.estatus === 'pendiente';
  return fila.tipo === 'Nota' || fila.tipo === 'Factura' || fila.tipo === 'Ingreso' || fila.tipo === 'Egreso';
}
function iniciarEdicion(fila) {
  editando.value = fila.key;
  // El monto de un retiro se guarda negativo en la fila (para sumar/restar
  // directo al saldo) — al editar se muestra en positivo, como lo capturó el usuario.
  edicion.value = { nombre: fila.nombre, monto: fila.tipo === 'Retiro' ? -fila.monto : fila.monto };
}

async function guardarEdicion(fila) {
  guardando.value = true;
  try {
    if (fila.tipo === 'Nota') {
      await actualizarCamposNota(fila.id, { cliente: edicion.value.nombre, total: edicion.value.monto });
    } else if (fila.tipo === 'Factura') {
      await actualizarCamposFactura(fila.id, { cliente: edicion.value.nombre, total: edicion.value.monto });
    } else if (fila.tipo === 'Ingreso' || fila.tipo === 'Egreso') {
      await actualizarMovimientoDinero(fila.id, { banco: nombre.value, concepto: edicion.value.nombre, monto: Number(edicion.value.monto) || 0 });
    } else if (fila.tipo === 'Retiro') {
      await editarRetiro(fila.id, { monto: Number(edicion.value.monto) || 0, motivo: edicion.value.nombre });
    }
    toast.add({ severity: 'success', summary: 'Guardado', detail: 'Cambios guardados.', life: 2500 });
    editando.value = null;
    await cargar();
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: e?.response?.data?.detail || 'No se pudo guardar.', life: 4000 });
  }
  guardando.value = false;
}

async function eliminarRetiroFila(fila) {
  procesandoId.value = fila.id;
  try {
    await eliminarRetiro(fila.id);
    toast.add({ severity: 'success', summary: 'Eliminado', detail: 'Retiro eliminado.', life: 2500 });
    await cargar();
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: e?.response?.data?.detail || 'No se pudo eliminar el retiro.', life: 4000 });
  }
  procesandoId.value = null;
}

const validando = ref(null);
async function toggleValidado(fila) {
  validando.value = fila.key;
  try {
    const nuevoValor = !fila.validado;
    if (fila.tipo === 'Nota') await actualizarValidadoNota(fila.id, nuevoValor);
    else if (fila.tipo === 'Factura') await actualizarValidadoFactura(fila.id, nuevoValor);
    else if (fila.tipo === 'Retiro') await actualizarValidadoRetiro(fila.id, nuevoValor);
    else if (fila.tipo === 'Pago nota') await actualizarValidadoPagoNota(fila.raw.nota_id, fila.id, nuevoValor);
    else await actualizarMovimientoDinero(fila.id, { validado: nuevoValor });
    await cargar();
  } catch {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo actualizar validado.', life: 4000 });
  }
  validando.value = null;
}

// ── Nuevo movimiento manual (banco fijo = este) ──
const movimientoDialogVisible = ref(false);
const nuevoMovimiento = ref({ tipo: 'Ingreso', concepto: '', monto: 0, referencia: '' });
const guardandoMovimiento = ref(false);

function abrirNuevoMovimiento() {
  nuevoMovimiento.value = { tipo: 'Ingreso', concepto: '', monto: 0, referencia: '' };
  movimientoDialogVisible.value = true;
}
async function confirmarNuevoMovimiento() {
  if (!nuevoMovimiento.value.concepto || !nuevoMovimiento.value.monto) {
    toast.add({ severity: 'warn', summary: 'Faltan datos', detail: 'Concepto y monto son obligatorios.', life: 3000 });
    return;
  }
  guardandoMovimiento.value = true;
  try {
    await registrarAbonoDinero({
      fecha: new Date().toISOString().slice(0, 10),
      tipo: nuevoMovimiento.value.tipo,
      concepto: nuevoMovimiento.value.concepto,
      monto: Number(nuevoMovimiento.value.monto),
      referencia: nuevoMovimiento.value.referencia,
      banco: nombre.value,
    });
    toast.add({ severity: 'success', summary: 'Registrado', detail: 'Movimiento registrado.', life: 2500 });
    movimientoDialogVisible.value = false;
    await cargar();
  } catch {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo registrar el movimiento.', life: 4000 });
  }
  guardandoMovimiento.value = false;
}

// ── Registrar retiro (banco fijo = este) ──
const retiroDialogVisible = ref(false);
const retiroForm = ref({ monto: null, motivo: '' });
const retiroArchivo = ref(null);
const guardandoRetiro = ref(false);

function abrirRetiroDialog() {
  retiroForm.value = { monto: null, motivo: '' };
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
      archivo: retiroArchivo.value,
    });
    toast.add({ severity: 'success', summary: 'Registrado', detail: 'Retiro registrado, pendiente de aprobación.', life: 3000 });
    retiroDialogVisible.value = false;
    await cargar();
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: e?.response?.data?.detail || 'No se pudo registrar el retiro.', life: 4000 });
  }
  guardandoRetiro.value = false;
}

async function aprobar(id) {
  procesandoId.value = id;
  try {
    await aprobarRetiro(id);
    toast.add({ severity: 'success', summary: 'Aprobado', detail: 'Retiro aprobado correctamente.', life: 3000 });
    await cargar();
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: e?.response?.data?.detail || 'No se pudo aprobar el retiro.', life: 4000 });
  }
  procesandoId.value = null;
}
async function rechazar(id) {
  procesandoId.value = id;
  try {
    await rechazarRetiro(id);
    toast.add({ severity: 'success', summary: 'Rechazado', detail: 'Retiro rechazado.', life: 3000 });
    await cargar();
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: e?.response?.data?.detail || 'No se pudo rechazar el retiro.', life: 4000 });
  }
  procesandoId.value = null;
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

// ── Saldo inicial / cerrar mes (admin) — mismo endpoint, distinto valor
// prefijado: "editar saldo inicial" parte del valor guardado, "cerrar mes"
// parte del saldo actual ya calculado con todos los movimientos a hoy. ──
const saldoInicialDialogVisible = ref(false);
const saldoInicialForm = ref(0);
const guardandoSaldoInicial = ref(false);
const modoCierre = ref(false);

function abrirSaldoInicialDialog() {
  modoCierre.value = false;
  saldoInicialForm.value = saldo.value.saldoInicial;
  saldoInicialDialogVisible.value = true;
}
function abrirCerrarMes() {
  modoCierre.value = true;
  saldoInicialForm.value = saldo.value.saldo;
  saldoInicialDialogVisible.value = true;
}
async function confirmarSaldoInicial() {
  guardandoSaldoInicial.value = true;
  try {
    await setSaldoInicial(nombre.value, Number(saldoInicialForm.value) || 0);
    toast.add({ severity: 'success', summary: 'Guardado', detail: 'Saldo inicial actualizado.', life: 2500 });
    saldoInicialDialogVisible.value = false;
    await cargar();
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

@media (max-width: 768px) {
  .detalle-banco-container {
    margin: 1rem auto;
    padding: 1rem 0.75rem;
  }
  .saldo-card { padding: 1.25rem; }
}
</style>

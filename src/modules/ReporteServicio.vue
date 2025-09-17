<template>
  <div class="reporte-servicio-container">
    <h2 class="reporte-title">Reporte de Servicio</h2>
    <form class="reporte-form" @submit.prevent="guardar">
      <div class="responsive-grid">
        <div class="col-block">
          <div class="form-group">
            <label class="required-label">Tipo de servicio</label>
            <Dropdown v-model="form.tipo_servicio" :options="tiposServicio" placeholder="Selecciona" class="w-full" :class="{'p-invalid': isCampoInvalido('tipo_servicio')}" />
            <small v-if="isCampoInvalido('tipo_servicio')" class="error-msg">Requerido</small>
          </div>
          <div class="form-group">
            <label>Lugar / Centro de instalación</label>
            <InputText v-model="form.lugar_instalacion" class="w-full" placeholder="Opcional" />
          </div>
          <h4 class="section-title">Datos del vehículo</h4>
          <div class="form-group">
            <InputText v-model="form.marca" placeholder="Marca" class="w-full mb-2" :class="{'p-invalid': isCampoInvalido('marca')}" />
            <InputText v-model="form.submarca" placeholder="Submarca" class="w-full mb-2" :class="{'p-invalid': isCampoInvalido('submarca')}" />
            <InputText v-model="form.modelo" placeholder="Modelo" class="w-full mb-2" :class="{'p-invalid': isCampoInvalido('modelo')}" />
            <InputText v-model="form.placas" placeholder="Placa" class="w-full mb-2" :class="{'p-invalid': isCampoInvalido('placas')}" />
            <InputText v-model="form.color" placeholder="Color" class="w-full mb-2" :class="{'p-invalid': isCampoInvalido('color')}" />
            <InputText v-model="form.numero_economico" placeholder="Número económico" class="w-full mb-2" :class="{'p-invalid': isCampoInvalido('numero_economico')}" />
          </div>
        </div>
        <div class="col-block">
          <h4 class="section-title">Datos del dispositivo (opcionales)</h4>
          <div class="form-group">
            <InputText v-model="form.modelo_gps" placeholder="Modelo GPS" class="w-full mb-2" />
            <InputText v-model="form.accesorios" placeholder="Accesorios adicionales (Botón/Micro/Etc.)" class="w-full mb-2" />
            <InputText v-model="form.ubicacion_gps" placeholder="Ubicación del GPS" class="w-full mb-2" />
            <InputText v-model="form.ubicacion_bloqueo" placeholder="Ubicación del Bloqueo (Bomba/Switch/Ignición/Etc.)" class="w-full mb-2" />
          </div>
          <h4 class="section-title">Datos del cobro</h4>
          <div class="form-group">
            <label class="required-label">Subtotal (orden de servicio)</label>
            <InputText v-model="form.subtotal" placeholder="Subtotal" class="w-full mb-2" :disabled="true" :class="{'p-invalid': isCampoInvalido('subtotal')}" />
          </div>
            <div class="form-group">
            <label class="required-label">Total a cobrar</label>
            <InputNumber v-model="form.total" placeholder="Total a cobrar" class="w-full mb-2" :class="{'p-invalid': isCampoInvalido('total')}" />
            <small>El instalador puede modificar este valor si hay algún ajuste.</small>
          </div>
          <div class="form-group monto-tecnico-group">
            <label>Monto cobrado por el técnico</label>
            <div class="monto-tecnico-row">
              <InputNumber v-model="form.monto_tecnico" placeholder="Monto técnico" class="w-full mb-2" :disabled="usarTotalMontoTecnico" />
              <div class="checkbox-inline">
                <Checkbox v-model="usarTotalMontoTecnico" :binary="true" inputId="chkUsarTotal" />
                <label for="chkUsarTotal" class="inline-label">Total</label>
              </div>
            </div>
          </div>
          <div class="form-group">
            <label>Método de pago</label>
            <InputText v-model="form.forma_pago" placeholder="Método de pago" class="w-full mb-2" :disabled="true" />
          </div>
          <div class="form-group">
            <label>Viáticos</label>
            <InputText v-model="form.viaticos" type="number" class="w-full mb-2" />
          </div>
        </div>

        <!-- NUEVA SECCION: Asignación múltiple de IMEIs por artículo (incluye SIM) -->
        <div class="col-block full-width" v-if="lineItems.length > 0 || simSerieOptions.length">
          <h4 class="section-title">Asignación de IMEIs y SIM</h4>
          <div class="line-item-block sim-block" v-if="simSerieOptions.length">
            <div class="line-header">
              <strong>SIM</strong>
              <Button size="small" type="button" icon="pi pi-plus" class="p-button-text p-button-sm" @click="agregarSimSlot" />
            </div>
            <div class="slots-grid">
              <div v-for="(simSel, sIdx) in simSelecciones" :key="'sim-slot-'+sIdx" class="slot-item">
                <Dropdown
                  v-model="simSelecciones[sIdx]"
                  :options="simOpcionesVisibles(sIdx)"
                  optionLabel="label"
                  optionValue="value"
                  placeholder="SIM (stock)"
                  :filter="true"
                  class="w-full"
                />
                <div class="sim-slot-actions" v-if="simSelecciones.length > 1">
                  <Button icon="pi pi-times" class="p-button-text p-button-danger p-button-sm" type="button" @click="eliminarSimSlot(sIdx)" />
                </div>
              </div>
            </div>
          </div>
          <div v-if="lineItems.length" class="multi-imei-wrapper">
            <div v-for="linea in lineItems" :key="`line-${linea.lineaId}`" class="line-item-block">
              <div class="line-header">
                <strong>{{ linea.articulo_nombre || ('Artículo #' + linea.lineaId) }}</strong>
                <span class="badge" :class="{ complete: linea.seleccionesCompletas, incomplete: !linea.seleccionesCompletas }">
                  {{ linea.selecciones.filter(Boolean).length }} / {{ linea.selecciones.length }}
                </span>
                <Button v-if="linea.selecciones.some(s => s)" size="small" type="button" label="Limpiar" class="p-button-text p-button-sm" @click="limpiarLinea(linea)" />
              </div>
              <div class="slots-grid">
                <div v-for="(sel, idx) in linea.selecciones" :key="`line-${linea.lineaId}-slot-${idx}`" class="slot-item">
                  <Dropdown
                    v-model="linea.selecciones[idx]"
                    :options="opcionesVisibles(linea, idx)"
                    :disabled="opcionesVisibles(linea, idx).length === 0"
                    optionLabel="label"
                    optionValue="value"
                    placeholder="IMEI"
                    :filter="true"
                    class="w-full"
                    :class="{'p-invalid imei-slot-invalid': attemptedSubmit && !linea.selecciones[idx]}"
                  />
                  <small v-if="attemptedSubmit && !linea.selecciones[idx]" class="error-msg">Requerido</small>
                  <small v-else-if="opcionesVisibles(linea, idx).length === 0" class="warn-text">Sin IMEIs disponibles</small>
                </div>
              </div>
            </div>
            <div v-if="stockInsuficiente.length" class="warning-block">
              <p><strong>Advertencia:</strong> Stock insuficiente para:</p>
              <ul>
                <li v-for="s in stockInsuficiente" :key="'warn-'+s.lineaId">{{ s.articulo_nombre }} (slots {{ s.requerido }}, disponibles {{ s.disponibles }})</li>
              </ul>
            </div>
          </div>
        </div>
        <!-- FIN NUEVA SECCION -->

        <div class="col-block full-width">
          <div class="form-group">
            <label>Observaciones</label>
            <Textarea v-model="form.observaciones" rows="2" class="w-full" />
          </div>
        </div>
      </div>
      <div class="modal-actions full-width">
        <Button label="Guardar" icon="pi pi-save" type="submit" :disabled="!formCompleto" :class="{ 'btn-disabled-force': !formCompleto }" />
        <Button label="Cancelar" icon="pi pi-times" class="p-button-secondary" type="button" @click="cerrar" />
      </div>
    </form>
    <Dialog v-model:visible="showResultDialog" header="Resultado" :modal="true" :closable="false">
      <div style="padding:1.5rem; text-align:center;">
        <span>{{ resultMessage }}</span>
      </div>
      <Button label="Aceptar" icon="pi pi-check" @click="onDialogAccept" class="mt-3" />
    </Dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch, nextTick } from 'vue';
import Textarea from 'primevue/textarea';
import InputText from 'primevue/inputtext';
import Dropdown from 'primevue/dropdown';
import Button from 'primevue/button';
import Checkbox from 'primevue/checkbox';
import Dialog from 'primevue/dialog';
import { addReporteServicio, getReportePorAsignacion } from '@/services/reportesServicio';
import { getDetalleVenta } from '@/services/ventasService';
import { useRoute, useRouter } from 'vue-router';
import { getAsignacionesTecnicos } from '@/services/asignacionesService';
import { getUsuarios } from '@/services/usuariosService';
import { getVentas } from '@/services/ventasService';
import InputNumber from 'primevue/inputnumber';
import { getImeisPorUbicacion, getUbicaciones } from '@/services/ubicacionesService';
import { getTodosArticulos } from '@/services/articulosService';

const emit = defineEmits(['close', 'saved']);

const route = useRoute();
const router = useRouter();
const asignacionIdValido = computed(() => Number.isInteger(Number(route.params.asignacionId)) && Number(route.params.asignacionId) > 0);
const asignacionIdCentral = computed(() => asignacionIdValido.value ? Number(route.params.asignacionId) : null);
const asignacion = ref(null);

const tiposServicio = ['Instalación', 'Reinstalación', 'Revisión', 'Desinstalación', 'Búsqueda'];
const formasPago = ['Efectivo Entregado al tecnico', 'Transferencia', 'Depósito', ];

const tecnicoNombre = ref('');
const tecnicoTelefono = ref('');
const proveedoresSim = [ { label: 'TELCEL', value: 'TELCEL' }, { label: 'ESPAÑOL', value: 'ESPAÑOL' } ];
const imeiOptions = ref([]); // Para IMEI (filtrado por artículos de la orden)
const simSerieOptions = ref([]); // Para Serie (stock de la ubicación filtrado)
const simSelecciones = ref([null]); // NUEVO: múltiples SIM seleccionadas

const ubicacionId = ref(null); // Ubicación (almacén) asociada a la venta/asignación
const allowedArticuloIds = ref(new Set()); // Set de ids de artículos presentes en el detalle (puede usarse en futuras reglas)
const allowedArticuloNames = ref(new Set()); // Set de nombres normalizados de artículos
const ALLOW_AUTO_UBICACION_DEDUCCION = false; // Deshabilitado por defecto (evita deducir ubicación automáticamente)

function buildImeiOptions(){
  imeiOptions.value = imeisStockRaw.value
    .filter(r => !esSimArticuloNombre(r.articulo_nombre))
    .map(r => ({ label: `${r.imei} — ${r.articulo_nombre}`, value: String(r.imei) }));
}

function normalizeTexto(v){
  return String(v||'').toLowerCase().normalize('NFD').replace(/\p{Diacritic}/gu,'').trim();
}

function esSimArticuloNombre(nombre){
  return /\bsim\b/.test(normalizeTexto(nombre));
}

const form = ref({
  tipo_servicio: '',
  lugar_instalacion: '',
  marca: '',
  submarca: '',
  modelo: '',
  placas: '',
  color: '',
  numero_economico: '',
  equipo_plan: '',
  imei: '',
  serie: '',
  accesorios: '',
  sim_proveedor: '',
  sim_serie: '',
  sim_instalador: '',
  sim_telefono: '',
  bateria: '',
  ignicion: '',
  corte: '',
  ubicacion_corte: '',
  observaciones: '',
  plataforma: '',
  usuario: '',
  subtotal: '',
  forma_pago: '',
  pagado: false,
  nombre_cliente: '',
  firma_cliente: '',
  nombre_instalador: '',
  firma_instalador: '',
  asignacion_id: undefined, // Se setea en onMounted
  monto_tecnico: 0,
  viaticos: 0
});

const loading = ref(false);
const showResultDialog = ref(false);
const resultMessage = ref('');
const saveSuccess = ref(false);
const imeiUpdateError = ref(false);

const clienteUsuariosOptions = ref([]);
const clientePlataformasOptions = ref([]);
const pagos = ref([]);
const imeisStockRaw = ref([]);
const articulosIndex = ref({}); // Nuevo índice de artículos por id

const attemptedSubmit = ref(false);
const usarTotalMontoTecnico = ref(false);

async function cargarArticulos(){
  try {
    const arts = await getTodosArticulos();
    if (Array.isArray(arts)) {
      articulosIndex.value = Object.fromEntries(arts.map(a => [a.id, a]));
    }
  } catch (e) {
    console.error('Error cargando articulos:', e);
  }
}

async function cargarImeisDeUbicacion(id){
  console.log('cargarImeisDeUbicacion llamado con id:', id);
  
  try {
    const res = await fetch(`${import.meta.env.VITE_API_URL}/imeis`);
    const todos = await res.json();
    console.log('Todos los IMEIs cargados:', todos);
    
    const imeisUbicacion = Array.isArray(todos) ? todos.filter(i => Number(i.ubicacion_id) === Number(id)) : [];
    console.log('IMEIs ubicacion (raw) antes de filtrar status:', imeisUbicacion);
    imeisStockRaw.value = imeisUbicacion.filter(i => ['Disponible','Devuelto'].includes(i.status));
    buildSimSerieOptions();
    buildLineItems();
  } catch(e){ console.error('Error cargando IMEIs:', e); }
}

watch(ubicacionId, (val) => {
  if(val && !imeisStockRaw.value.length){
    cargarImeisDeUbicacion(val).then(()=>{ buildImeiOptions(); buildLineItems(); });
  }
});

function buildSimSerieOptions(){
  const sims = imeisStockRaw.value.filter(r => esSimArticuloNombre(r.articulo_nombre));
  simSerieOptions.value = sims.map(i => ({ label: `${i.imei} — ${i.articulo_nombre}`, value: String(i.imei) }));
}

function buildLineItems(){
  if(!detalleVentaRaw.value.length || !imeisStockRaw.value.length) { lineItems.value = []; return; }
  const resultado = [];
  for(const d of detalleVentaRaw.value){
    if(esSimArticuloNombre(d.articulo_nombre)) continue;
    if(/instalacion/.test(normalizeTexto(d.articulo_nombre||''))) continue;
    const cantidad = Number(d.cantidad || d.cantidad_articulos || 1) || 1;
    const nombreDetNorm = normalizeTexto(d.articulo_nombre || d.descripcion || '');
    const imeisPosibles = imeisStockRaw.value
      .filter(r => {
        if(esSimArticuloNombre(r.articulo_nombre)) return false;
        const sameId = r.articulo_id && d.articulo_id && Number(r.articulo_id) === Number(d.articulo_id);
        const sameName = nombreDetNorm && normalizeTexto(r.articulo_nombre) === nombreDetNorm;
        return sameId || sameName;
      })
      .map(r => ({ label:`${r.imei} — ${r.articulo_nombre}`, value:String(r.imei) }));
    resultado.push({
      lineaId: d.id || d.detalle_id || `${d.articulo_id}-${Math.random().toString(36).slice(2,7)}`,
      articulo_id: d.articulo_id || null,
      articulo_nombre: d.articulo_nombre || d.descripcion || 'Artículo',
      imeisPosibles,
      selecciones: Array(cantidad).fill(null),
      get seleccionesCompletas(){ return this.selecciones.every(v=>!!v); }
    });
  }
  lineItems.value = resultado;
}

async function cargarPagos() {
  pagos.value = [];
}

async function cargarDatosTecnico() {
  try {
    if (!asignacion.value) return;
    let usuarios = await getUsuarios();
    let tecnico = usuarios.find(u => 
      u.username?.toLowerCase() === asignacion.value.tecnico?.toLowerCase() ||
      u.nombre?.toLowerCase() === asignacion.value.tecnico?.toLowerCase()
    );
    if (tecnico) {
      tecnicoNombre.value = tecnico.username || tecnico.nombre || '';
      tecnicoTelefono.value = tecnico.telefono || '';
      form.value.sim_instalador = tecnicoNombre.value;
      form.value.sim_telefono = tecnicoTelefono.value;
      form.value.nombre_instalador = tecnicoNombre.value;
    } else if (asignacion.value.tecnico) {
      tecnicoNombre.value = asignacion.value.tecnico;
      tecnicoTelefono.value = '';
      form.value.sim_instalador = asignacion.value.tecnico;
      form.value.nombre_instalador = asignacion.value.tecnico;
    }
  } catch (e) {
    console.error('Error en cargarDatosTecnico:', e);
  }
}

const detalleVentaRaw = ref([]);
const lineItems = ref([]); // [{ lineaId, articulo_id, articulo_nombre, cantidad, imeisPosibles:[{label,value}], selecciones:[...], seleccionesCompletas:false }]

const selectedImeisGlobal = computed(() => {
  const s = new Set();
  for (const sim of simSelecciones.value) if (sim) s.add(sim);
  for (const li of lineItems.value) {
    for (const val of li.selecciones) if (val) s.add(val);
  }
  return s;
});

function esArticuloServicio(d){
  const art = d?.articulo_id ? articulosIndex.value[d.articulo_id] : null;
  const tipo = String(art?.tipo || d?.tipo || '').toLowerCase();
  return tipo === 'servicio';
}

function opcionesVisibles(linea, slotIdx){
  const current = linea.selecciones[slotIdx];
  return linea.imeisPosibles.filter(opt => !selectedImeisGlobal.value.has(opt.value) || opt.value === current);
}

function agregarSimSlot(){
  simSelecciones.value.push(null);
}
function eliminarSimSlot(idx){
  if (simSelecciones.value.length === 1) { simSelecciones.value[0] = null; return; }
  simSelecciones.value.splice(idx,1);
  if (!simSelecciones.value[0]) form.value.sim_serie = '';
}
function simOpcionesVisibles(idx){
  const current = simSelecciones.value[idx];
  return simSerieOptions.value.filter(opt => !selectedImeisGlobal.value.has(opt.value) || opt.value === current);
}

function limpiarLinea(linea) {
  linea.selecciones.splice(0, linea.selecciones.length, ...Array(linea.selecciones.length).fill(null));
}

const stockInsuficiente = computed(() => {
  const arr = [];
  for (const li of lineItems.value) {
    const requerido = li.selecciones.length;
    const disponibles = li.imeisPosibles.length;
    if (disponibles < requerido) arr.push({ lineaId: li.lineaId, articulo_nombre: li.articulo_nombre, requerido, disponibles });
  }
  return arr;
});

watch(simSelecciones, (arr) => {
  const first = arr.find(v => !!v) || '';
  form.value.sim_serie = first;
}, { deep: true });

watch(selectedImeisGlobal, (setVal) => {
  if (!form.value.imei) {
    const first = Array.from(setVal).find(v => v !== form.value.sim_serie);
    if (first) form.value.imei = first;
  }
});

function validarAsignacionesImeis() {
  if (!lineItems.value.length) return true;
  const allSelected = [];
  for (const li of lineItems.value) allSelected.push(...li.selecciones.filter(Boolean));
  if (new Set(allSelected).size !== allSelected.length) {
    resultMessage.value = 'Hay IMEIs duplicados en las asignaciones de artículos.';
    showResultDialog.value = true;
    return false;
  }
  const incompletos = lineItems.value.filter(li => li.imeisPosibles.length >= li.selecciones.length && !li.selecciones.every(v => !!v));
  if (incompletos.length) {
    resultMessage.value = 'Debes completar todos los slots de IMEI o eliminar los sobrantes.';
    showResultDialog.value = true;
    return false;
  }
  return true;
}

async function cargarDatosCliente() {
  try {
    if (!asignacion.value) return;
    const { getClientes } = await import('@/services/clientesService');
    const clientes = await getClientes();
    const cliente = clientes.find(c => c.id == asignacion.value.cliente_id);
    if (cliente) {
      form.value.nombre_cliente = cliente.nombre || '';
      form.value.telefono_cliente = cliente.telefonos?.join(', ') || '';
      clienteUsuariosOptions.value = Array.isArray(cliente.usuarios)
        ? cliente.usuarios.map(u => ({ label: u, value: u }))
        : [];
      clientePlataformasOptions.value = Array.isArray(cliente.plataformas)
        ? cliente.plataformas.map(p => ({ label: p, value: p }))
        : [];
    }
    if (asignacion.value.venta_id) {
      const ventas = await getVentas();
      const venta = ventas.find(v => v.id == asignacion.value.venta_id);
      if (venta) {
        form.value.subtotal = venta.total || '';
        form.value.total = venta.total || '';
        form.value.forma_pago = venta.terminos_pago || '';
        try {
          const detalle = await getDetalleVenta(venta.id);
          if (Array.isArray(detalle) && detalle.length > 0) {
            detalleVentaRaw.value = detalle; // NUEVO
            const art = detalle[0];
            form.value.modelo = art.modelo || art.modelo_gps || '';
            form.value.imei = art.imei || '';
            form.value.serie = art.serie || '';
            form.value.equipo_plan =  '';
            form.value.placas = art.placas || '';
            form.value.color = art.color || '';
            form.value.numero_economico = art.numero_economico || '';
            form.value.accesorios = art.accesorios || '';
          }
          try {
            const ids = new Set();
            const names = new Set();
            for (const d of detalle || []) {
              if (d.articulo_id) ids.add(Number(d.articulo_id));
              if (d.articulo_nombre) names.add(String(d.articulo_nombre).toLowerCase());
            }
            allowedArticuloIds.value = ids;
            allowedArticuloNames.value = names;
          } catch (_) {}
        } catch (e) {
          console.error('Error en getDetalleVenta:', e);
        }
        try {
          const ubicaciones = await getUbicaciones();

          
          const uMatch = ubicaciones.find(u => String(u.nombre || '').toLowerCase() === String(venta.almacen || '').toLowerCase());
          if (uMatch?.id) {
            ubicacionId.value = uMatch.id;
          }
        } catch (e) {}
        if (!ubicacionId.value) {
          ubicacionId.value = venta.ubicacion_id || null;
        }
        if (ubicacionId.value) {
          await cargarImeisDeUbicacion(ubicacionId.value);
          buildImeiOptions();
          buildLineItems(); // NUEVO
        } else if (ALLOW_AUTO_UBICACION_DEDUCCION) { // ahora condicionado
          const imeiBase = form.value.imei;
          if (imeiBase) {
            try {
              const res = await fetch(`${import.meta.env.VITE_API_URL}/buscar-imei?digitos=${encodeURIComponent(String(imeiBase))}`);
              const resultados = await res.json();
              const ubicacionNombre = Array.isArray(resultados) && resultados[0]?.ubicacion ? resultados[0].ubicacion : null;
              if (ubicacionNombre) {
                const ubicaciones = await getUbicaciones();
                const ubic = ubicaciones.find(u => (u.nombre || '').toLowerCase() === String(ubicacionNombre).toLowerCase());
                if (ubic?.id) {
                  ubicacionId.value = ubic.id;
                  await cargarImeisDeUbicacion(ubicacionId.value);
                  buildImeiOptions();
                  buildLineItems();
                }
              }
            } catch (e) {
              console.error('No se pudo deducir la ubicación desde IMEI:', e);
            }
          }
        }
      }
    }
  } catch (e) {
    console.error('Error en cargarDatosCliente:', e);
  }
}

onMounted(async () => {
  loading.value = true;
  try {
    await cargarArticulos(); // cargar catálogo primero para saber tipo Bien/Servicio
    const asignaciones = await getAsignacionesTecnicos();
    asignacion.value = asignaciones.find(a => String(a.id) === String(asignacionIdCentral.value) || String(a.venta_id) === String(asignacionIdCentral.value));
    if (!asignacion.value) {
      loading.value = false;
      resultMessage.value = 'No se encontró la asignación para el ID proporcionado.';
      showResultDialog.value = true;
      return;
    }
    form.value.asignacion_id = asignacion.value.id;
    await cargarDatosTecnico();
    await cargarDatosCliente();
    try {
      await cargarPagos();
    } catch (e) {
      console.error('Error en cargarPagos:', e);
    }
    loading.value = false;
  } catch (e) {
    console.error('Error en onMounted:', e);
    loading.value = false;
  }
});

function cerrar() {
  emit('close');
  router.push('/');
}

async function guardar() {
  attemptedSubmit.value = true;
  if (!asignacionIdValido.value) {
    resultMessage.value = 'ID de asignación inválido. No se puede guardar el reporte.';
    showResultDialog.value = true;
    scrollFocusFirstIssue();
    return;
  }
  if(!formCompleto.value){
    scrollFocusFirstIssue();
  }
  if (!validarAsignacionesImeis()) { scrollFocusFirstIssue(); return; }
  loading.value = true;
  try {
    saveSuccess.value = false;
    imeiUpdateError.value = false;
    let asignaciones = await getAsignacionesTecnicos();
    const asignacion = asignaciones.find(a => String(a.id) === String(asignacionIdCentral.value) || String(a.venta_id) === String(asignacionIdCentral.value));
    if (!asignacion || !asignacion.venta_id) {
      resultMessage.value = 'No se puede guardar el reporte: falta asignación o venta asociada.';
      loading.value = false;
      showResultDialog.value = true;
      return;
    }
    const imeisArticulosPayload = lineItems.value.map(li => ({
      articulo_id: li.articulo_id,
      linea_id: li.lineaId,
      imeis: [...li.selecciones]
    }));
    if (!form.value.sim_serie && simSelecciones.value.some(s=>s)) {
      form.value.sim_serie = simSelecciones.value.find(s=>s) || '';
    }
    if (!form.value.imei && selectedImeisGlobal.value.size) {
      const firstImei = Array.from(selectedImeisGlobal.value).find(v => v !== form.value.sim_serie);
      if (firstImei) form.value.imei = firstImei;
    }
    const payload = {
      asignacion_id: asignacion.id,
      tipo_servicio: form.value.tipo_servicio || '',
      lugar_instalacion: form.value.lugar_instalacion || '',
      marca: form.value.marca || '',
      submarca: form.value.submarca || '',
      modelo: form.value.modelo || '',
      placas: form.value.placas || '',
      color: form.value.color || '',
      numero_economico: form.value.numero_economico || '',
      equipo_plan: form.value.equipo_plan || '',
      imei: form.value.imei || '',
      serie: form.value.serie || '',
      accesorios: form.value.accesorios || '',
      sim_proveedor: form.value.sim_proveedor || '',
      sim_serie: form.value.sim_serie || '',
      sim_instalador: form.value.sim_instalador || '',
      sim_telefono: form.value.sim_telefono || '',
      bateria: form.value.bateria || '',
      ignicion: form.value.ignicion || '',
      corte: form.value.corte || '',
      ubicacion_corte: form.value.ubicacion_corte || '',
      observaciones: form.value.observaciones || '',
      plataforma: form.value.plataforma || '',
      usuario: form.value.usuario || '',
      subtotal: String(form.value.subtotal ?? ''),
      forma_pago: form.value.forma_pago || '',
      pagado: !!form.value.pagado,
      nombre_cliente: form.value.nombre_cliente || '',
      firma_cliente: form.value.firma_cliente || '',
      nombre_instalador: form.value.nombre_instalador || '',
      firma_instalador: form.value.firma_instalador || '',
      total: Number(form.value.total) || 0,
      monto_tecnico: Number(form.value.monto_tecnico) || 0,
      viaticos: Number(form.value.viaticos) || 0,
      modelo_gps: form.value.modelo_gps || '',
      ubicacion_gps: form.value.ubicacion_gps || '',
      ubicacion_bloqueo: form.value.ubicacion_bloqueo || '',
      imeis_articulos: imeisArticulosPayload // NUEVO
    };
    const resp = await addReporteServicio(payload);
    const baseMessage = (resp && typeof resp === 'object' && 'message' in resp)
      ? String(resp.message)
      : 'Reporte de servicio creado exitosamente';
    {
      const setImeis = new Set();
      if (payload.imei) setImeis.add(payload.imei);
      for (const sim of simSelecciones.value.filter(Boolean)) setImeis.add(sim);
      for (const li of imeisArticulosPayload) {
        for (const im of li.imeis.filter(Boolean)) setImeis.add(im);
      }
      try {
        for (const imei of Array.from(setImeis)) {
          await fetch(`${import.meta.env.VITE_API_URL}/imeis/${encodeURIComponent(imei)}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status: 'Vendido' })
          });
        }
      } catch (e) {
        console.error('Error marcando IMEIs como vendidos:', e);
        imeiUpdateError.value = true;
      }
    }
    if (!imeiUpdateError.value) {
      resultMessage.value = `${baseMessage}. Al aceptar te llevaré al inicio.`;
      saveSuccess.value = true;
    } else {
      resultMessage.value = `${baseMessage}, pero hubo un problema actualizando los IMEIs. Puedes revisar el estado en Inventario.`;
      saveSuccess.value = false;
    }
    emit('saved');
  } catch (e) {
    console.error('Error en guardar:', e);
    resultMessage.value = 'Error al guardar el reporte de servicio.';
    saveSuccess.value = false;
  } finally {
    loading.value = false;
    showResultDialog.value = true;
  }
}

function onDialogAccept() {
  showResultDialog.value = false;
  if (saveSuccess.value) {
    router.push('/');
  }
}

function formatearFecha(fecha) {
  if (!fecha) return '';
  const d = new Date(fecha);
  const dia = String(d.getDate()).padStart(2, '0');
  const mes = String(d.getMonth() + 1).padStart(2, '0');
  const anio = d.getFullYear();
  return `${dia}/${mes}/${anio}`;
}

function formatoMoneda(valor) {
  if (isNaN(valor)) return '$0.00';
  return valor.toLocaleString('es-MX', { style: 'currency', currency: 'MXN', minimumFractionDigits: 2 });
}

const baseObligatorios = ['tipo_servicio','marca','submarca','modelo','placas','color','numero_economico','subtotal','total'];
function isCampoObligatorio(c){
  if((c === 'placas' || c === 'numero_economico') && ['Revisión','Búsqueda'].includes(form.value.tipo_servicio)) return false;
  return baseObligatorios.includes(c);
}
function isCampoInvalido(c){
  if(!isCampoObligatorio(c)) return false;
  const val = form.value[c];
  if(c === 'total') return val === null || val === undefined || val === '' || isNaN(val);
  return !String(val ?? '').trim();
}
const formCompleto = computed(() => baseObligatorios.filter(isCampoObligatorio).every(c => !isCampoInvalido(c)));

watch(usarTotalMontoTecnico, val => {
  if (val) {
    form.value.monto_tecnico = Number(form.value.total) || 0;
  }
});
watch(() => form.value.total, val => {
  if (usarTotalMontoTecnico.value) {
    form.value.monto_tecnico = Number(val) || 0;
  }
});

function scrollFocusFirstIssue(){
  nextTick(() => {
    const container = document.querySelector('.reporte-form');
    if(!container) return;
    const firstInvalid = container.querySelector('.p-invalid');
    if(firstInvalid){
      firstInvalid.scrollIntoView({behavior:'smooth', block:'center'});
      const focusable = firstInvalid.querySelector('input,textarea,.p-dropdown');
      if(focusable && 'focus' in focusable) focusable.focus();
    }
  });
}
</script>

<style scoped>
@import '@/assets/main.css';
.reporte-servicio-container {
  max-width: 900px;
  margin: 2rem auto;
  background: var(--color-card);
  color: var(--color-text);
  border-radius: 10px;
  box-shadow: var(--shadow-1);
  padding: 2rem 1rem;
}
.reporte-title {
  color: var(--color-title);
  text-align: center;
  margin-bottom: 2rem;
  font-size: 1.5rem;
  font-weight: bold;
}
.reporte-form {
  width: 100%;
}
.form-row {
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
  margin-bottom: 1.2rem;
}
.form-col {
  flex: 1 1 0;
  min-width: 0;
  display: flex;
  flex-direction: column;
}
.section-title {
  color: var(--color-title);
  margin-top: 1.5rem;
  margin-bottom: 1rem;
  font-size: 1rem;
  font-weight: 600;
}
.form-group {
  margin-bottom: 1rem;
}
label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: bold;
  color: var(--color-title);
}
.w-full {
  width: 100%;
}
.mb-2 {
  margin-bottom: 0.7rem;
}
.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 2rem;
}
.reporte-form .responsive-grid {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}
.col-block { background: transparent; }
.full-width { width: 100%; }
@media (min-width: 880px) {
  .reporte-form .responsive-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.5rem 2rem;
    align-items: start;
  }
  .reporte-form .responsive-grid .full-width { grid-column: 1 / -1; }
}
@media (max-width: 700px) {
  .reporte-servicio-container {
    padding: 1rem 0.5rem;
    max-width: 100vw;
  }
}
.multi-imei-wrapper { display: flex; flex-direction: column; gap: 1.2rem; }
.line-item-block { padding: 0.9rem 0.9rem 1rem; border: 1px solid var(--p-gray-400,#ccc); border-radius: 8px; background: var(--color-bg-alt,rgba(255,255,255,0.02)); }
.line-header { display: flex; flex-wrap: wrap; gap: .75rem; align-items: center; margin-bottom: .75rem; }
.line-header .badge { font-size: .75rem; padding: .25rem .5rem; border-radius: 12px; background: #999; color:#fff; }
.line-header .badge.complete { background: #2e7d32; }
.line-header .badge.incomplete { background: #d32f2f; }
.line-header .p-button-sm { padding: 0 .4rem; }
.slots-grid { display: grid; gap: .75rem; grid-template-columns: repeat(auto-fill,minmax(160px,1fr)); }
.slot-item { display:flex; flex-direction: column; }
.warn-text { color: #d32f2f; font-size: .65rem; margin-top: .25rem; }
.warning-block { background: #fff4e5; border:1px solid #ffb74d; padding: .75rem 1rem; border-radius:6px; font-size:.8rem; }
.sim-block { margin-bottom: 1rem; }
.sim-slot-actions { margin-top: .25rem; display:flex; justify-content:flex-end; }
.btn-disabled-force { opacity:.45 !important; pointer-events:none !important; filter:grayscale(1); }
.required-label::after { content: ' *'; color: #d32f2f; }
.error-msg { color:#d32f2f; font-size:0.7rem; margin-top:-0.25rem; display:block; }
.monto-tecnico-row { display:flex; gap:.75rem; align-items:flex-start; }
.checkbox-inline { display:flex; align-items:center; gap:.35rem; margin-top:.25rem; }
.inline-label { font-weight:normal; margin:0; }
.imei-slot-invalid :deep(.p-dropdown) { border:1px solid #d32f2f !important; }
.info-block { background:#e8f4fd; border:1px solid #90caf9; padding:.65rem .8rem; border-radius:6px; font-size:.75rem; margin-top: .75rem; }
</style>
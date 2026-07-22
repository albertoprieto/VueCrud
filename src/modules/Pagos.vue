<template>
  <div class="pagos-container">
    <h2 class="pagos-title">
      <i :class="['pi', tab === 'notas' ? 'pi-file' : 'pi-receipt']"></i>
      {{ tab === 'notas' ? 'Notas' : 'Facturas' }} — Histórico
    </h2>

    <!-- Tabs: Notas / Facturas -->
    <div class="pagos-tabs">
      <Button
        :class="['tab-btn', tab === 'notas' ? 'tab-active' : 'tab-inactive']"
        label="Notas"
        icon="pi pi-file"
        @click="tab = 'notas'"
      />
      <Button
        :class="['tab-btn', tab === 'facturas' ? 'tab-active' : 'tab-inactive']"
        label="Facturas"
        icon="pi pi-receipt"
        @click="tab = 'facturas'"
      />
    </div>

    <!-- ════════ FILTROS ════════ -->
    <button
      v-if="isMobile"
      type="button"
      class="filtros-toggle"
      @click="filtrosAbiertos = !filtrosAbiertos"
    >
      <span><i class="pi pi-filter" /> Filtros<span v-if="filtrosActivos" class="filtros-badge">{{ filtrosActivos }}</span></span>
      <i :class="['pi', filtrosAbiertos ? 'pi-chevron-up' : 'pi-chevron-down']" />
    </button>

    <div class="pagos-filtros" v-if="!isMobile || filtrosAbiertos">
      <div class="filtro-item">
        <label>Cliente</label>
        <InputText v-model="filtroCliente" placeholder="Buscar por cliente..." class="w-full" />
      </div>
      <div class="filtro-item">
        <label>Nº Orden</label>
        <InputText v-model="filtroOrden" placeholder="Buscar por orden..." class="w-full" />
      </div>
      <div class="filtro-item">
        <label>IMEI (últimos 6 dígitos)</label>
        <InputText v-model="filtroImei" placeholder="Ej: 123456" maxlength="6" class="w-full" />
      </div>
      <div class="filtro-item">
        <label>Instalador</label>
        <InputText v-model="filtroInstalador" placeholder="Buscar por instalador..." class="w-full" />
      </div>
      <div class="filtro-item">
        <label>Vendedor</label>
        <InputText v-model="filtroVendedor" placeholder="Buscar por vendedor..." class="w-full" />
      </div>
      <div class="filtro-item">
        <label>Pagado en</label>
        <Dropdown
          v-model="filtroLugarPago"
          :options="lugaresPago"
          placeholder="Todos"
          showClear
          class="w-full"
        />
      </div>
    </div>

    <!-- ════════ BANCOS — Resumen de Dinero ════════ -->
    <div class="bancos-resumen">
      <div class="bancos-header">
        <h3>Bancos</h3>
        <span class="bancos-total-general">Total: {{ formatTotal(resumenBancos.totalGeneral) }}</span>
      </div>
      <div class="bancos-grid">
        <button
          v-for="banco in resumenBancos.bancos"
          :key="banco.nombre"
          type="button"
          :class="['banco-card', banco.activo ? 'banco-card-activo' : '']"
          :style="{ '--serie-color': bancoColor(banco.nombre) }"
          @click="toggleFiltroBanco(banco.nombre)"
        >
          <span class="banco-nombre"><span class="banco-dot"></span>{{ banco.nombre }}</span>
          <span class="banco-total">{{ formatTotal(banco.total) }}</span>
          <span class="banco-pct">{{ pctBanco(banco.total) }}</span>
          <span class="banco-count">{{ banco.count }} documento{{ banco.count === 1 ? '' : 's' }}</span>
        </button>
        <div v-if="resumenBancos.sinEspecificar.count" class="banco-card banco-card-sin" :style="{ '--serie-color': bancoColor(null) }">
          <span class="banco-nombre"><span class="banco-dot"></span>Sin especificar</span>
          <span class="banco-total">{{ formatTotal(resumenBancos.sinEspecificar.total) }}</span>
          <span class="banco-pct">{{ pctBanco(resumenBancos.sinEspecificar.total) }}</span>
          <span class="banco-count">{{ resumenBancos.sinEspecificar.count }} documento{{ resumenBancos.sinEspecificar.count === 1 ? '' : 's' }}</span>
        </div>
      </div>
    </div>

    <!-- ════════ NOTAS ════════ -->
    <div v-if="tab === 'notas'" class="tabla-seccion seccion-notas">
      <DataTable
        v-if="!isMobile"
        :value="notasFiltradas"
        responsiveLayout="scroll"
        :loading="loadingNotas"
        :paginator="true"
        :rows="15"
        :rowsPerPageOptions="[15, 30, 50]"
      >
        <template #loading>
          <DataTableLoader text="Cargando notas..." />
        </template>
        <Column field="id" header="ID" style="width: 60px" />
        <Column header="Órdenes">
          <template #body="{ data }">
            {{ (data.ordenes || []).join(', ') }}
          </template>
        </Column>
        <Column field="cliente" header="Cliente" />
        <Column header="IMEIs">
          <template #body="{ data }">
            <div v-if="getImeisUnicos(data).length" class="imeis-cell">
              <div v-for="(imei, idx) in getImeisUnicos(data)" :key="idx">{{ imei }}</div>
            </div>
            <span v-else style="color:var(--color-border);">—</span>
          </template>
        </Column>
        <Column field="total" header="Total">
          <template #body="{ data }">
            {{ formatTotal(data.total) }}
          </template>
        </Column>
        <Column field="lugar_pago" header="Pagado en">
          <template #body="{ data }">
            <span v-if="data.lugar_pago" class="badge-lugar">{{ data.lugar_pago }}</span>
            <span v-else style="color:var(--color-border);">—</span>
          </template>
        </Column>
        <Column field="instalador" header="Instalador" />
        <Column field="vendedor" header="Vendedor" />
        <Column field="status" header="Estatus">
          <template #body="{ data }">
            <span :class="'badge badge-' + badgeClassNota(data.status)">{{ data.status }}</span>
          </template>
        </Column>
        <Column field="fecha" header="Fecha">
          <template #body="{ data }">{{ formatFecha(data.fecha) }}</template>
        </Column>
        <Column header="Acciones" style="width: 320px">
          <template #body="{ data }">
            <div style="display: flex; gap: 0.5rem;">
              <Button icon="pi pi-eye" class="p-button-sm p-button-info" label="Detalle"
                @click="irDetalle('nota', data.id)" />
              <Button icon="pi pi-download" class="p-button-sm p-button-success" label="PDF"
                :loading="descargandoId === `nota-${data.id}`"
                @click="descargarPDF('nota', data)" />
              <Button icon="pi pi-file" class="p-button-sm p-button-info p-button-outlined" label="Comprobante"
                :disabled="!parseComprobantes(data).length"
                @click="verComprobante(data)" />
              <Button icon="pi pi-trash" class="p-button-sm p-button-danger" label="Eliminar"
                @click="confirmarEliminar('nota', data)" />
            </div>
          </template>
        </Column>
      </DataTable>

      <div v-else class="mobile-list-wrap">
        <div v-if="loadingNotas" class="mobile-loader-wrap">
          <DataTableLoader text="Cargando notas..." />
        </div>
        <div v-else-if="!notasFiltradas.length" class="mobile-empty">
          No hay notas para mostrar.
        </div>
        <div v-else class="mobile-cards">
          <article
            v-for="item in notasFiltradas"
            :key="`nota-mobile-${item.id}`"
            class="mobile-card"
          >
            <header class="mobile-card-header">
              <div>
                <p class="mobile-card-id">Nota #{{ item.id }}</p>
                <p class="mobile-card-cliente">{{ item.cliente || 'Sin cliente' }}</p>
              </div>
              <span :class="'badge badge-' + badgeClassNota(item.status)">{{ item.status }}</span>
            </header>

            <div class="mobile-card-grid">
              <div class="mobile-field">
                <span class="mobile-label">Total</span>
                <span class="mobile-value">{{ formatTotal(item.total) }}</span>
              </div>
              <div class="mobile-field">
                <span class="mobile-label">Fecha</span>
                <span class="mobile-value">{{ formatFecha(item.fecha) }}</span>
              </div>
              <div class="mobile-field">
                <span class="mobile-label">Ordenes</span>
                <span class="mobile-value">{{ (item.ordenes || []).join(', ') || '—' }}</span>
              </div>
              <div class="mobile-field">
                <span class="mobile-label">Pagado en</span>
                <span class="mobile-value">{{ item.lugar_pago || '—' }}</span>
              </div>
              <div class="mobile-field">
                <span class="mobile-label">Instalador</span>
                <span class="mobile-value">{{ item.instalador || '—' }}</span>
              </div>
              <div class="mobile-field">
                <span class="mobile-label">Vendedor</span>
                <span class="mobile-value">{{ item.vendedor || '—' }}</span>
              </div>
              <div class="mobile-field mobile-field-full">
                <span class="mobile-label">IMEIs</span>
                <span class="mobile-value">{{ getImeisUnicos(item).join(', ') || '—' }}</span>
              </div>
            </div>

            <div class="mobile-actions">
              <Button icon="pi pi-eye" class="p-button-sm p-button-info" label="Detalle"
                @click="irDetalle('nota', item.id)" />
              <Button icon="pi pi-download" class="p-button-sm p-button-success" label="PDF"
                :loading="descargandoId === `nota-${item.id}`"
                @click="descargarPDF('nota', item)" />
              <Button icon="pi pi-file" class="p-button-sm p-button-info p-button-outlined" label="Comprobante"
                :disabled="!parseComprobantes(item).length"
                @click="verComprobante(item)" />
              <Button icon="pi pi-trash" class="p-button-sm p-button-danger" label="Eliminar"
                @click="confirmarEliminar('nota', item)" />
            </div>
          </article>
        </div>
      </div>
    </div>

    <!-- ════════ FACTURAS ════════ -->
    <div v-if="tab === 'facturas'" class="tabla-seccion seccion-facturas">
      <DataTable
        v-if="!isMobile"
        :value="facturasFiltradas"
        responsiveLayout="scroll"
        :loading="loadingFacturas"
        :paginator="true"
        :rows="15"
        :rowsPerPageOptions="[15, 30, 50]"
      >
        <template #loading>
          <DataTableLoader text="Cargando facturas..." />
        </template>
        <Column field="id" header="ID" style="width: 60px" />
        <Column header="Órdenes">
          <template #body="{ data }">
            {{ (data.ordenes || []).join(', ') }}
          </template>
        </Column>
        <Column field="cliente" header="Cliente" />
        <Column header="IMEIs">
          <template #body="{ data }">
            <div v-if="getImeisUnicos(data).length" class="imeis-cell">
              <div v-for="(imei, idx) in getImeisUnicos(data)" :key="idx">{{ imei }}</div>
            </div>
            <span v-else style="color:var(--color-border);">—</span>
          </template>
        </Column>
        <Column field="total" header="Total">
          <template #body="{ data }">
            {{ formatTotal(data.total) }}
          </template>
        </Column>
        <Column field="lugar_pago" header="Pagado en">
          <template #body="{ data }">
            <span v-if="data.lugar_pago" class="badge-lugar">{{ data.lugar_pago }}</span>
            <span v-else style="color:var(--color-border);">—</span>
          </template>
        </Column>
        <Column field="instalador" header="Instalador" />
        <Column field="vendedor" header="Vendedor" />
        <Column field="status" header="Estatus">
          <template #body="{ data }">
            <span :class="'badge badge-' + badgeClassFactura(data.status)">{{ data.status }}</span>
          </template>
        </Column>
        <Column field="fecha" header="Fecha">
          <template #body="{ data }">{{ formatFecha(data.fecha) }}</template>
        </Column>
        <Column header="Acciones" style="width: 320px">
          <template #body="{ data }">
            <div style="display: flex; gap: 0.5rem;">
              <Button icon="pi pi-eye" class="p-button-sm p-button-info" label="Detalle"
                @click="irDetalle('factura', data.id)" />
              <Button icon="pi pi-download" class="p-button-sm p-button-success" label="PDF"
                :loading="descargandoId === `factura-${data.id}`"
                @click="descargarPDF('factura', data)" />
              <Button icon="pi pi-file" class="p-button-sm p-button-info p-button-outlined" label="Comprobante"
                :disabled="!parseComprobantes(data).length"
                @click="verComprobante(data)" />
              <Button icon="pi pi-code" class="p-button-sm p-button-help p-button"
                :disabled="!data.cfdi_xml_path"
                @click="abrirArchivoCfdi(data.cfdi_xml_path)" />
              <Button icon="pi pi-file-pdf" class="p-button-sm p-button-help p-button"
                :disabled="!data.cfdi_pdf_path"
                @click="abrirArchivoCfdi(data.cfdi_pdf_path)" />
              <Button icon="pi pi-trash" class="p-button-sm p-button-danger"
                @click="confirmarEliminar('factura', data)" />
            </div>
          </template>
        </Column>
      </DataTable>

      <div v-else class="mobile-list-wrap">
        <div v-if="loadingFacturas" class="mobile-loader-wrap">
          <DataTableLoader text="Cargando facturas..." />
        </div>
        <div v-else-if="!facturasFiltradas.length" class="mobile-empty">
          No hay facturas para mostrar.
        </div>
        <div v-else class="mobile-cards">
          <article
            v-for="item in facturasFiltradas"
            :key="`factura-mobile-${item.id}`"
            class="mobile-card"
          >
            <header class="mobile-card-header">
              <div>
                <p class="mobile-card-id">Factura #{{ item.id }}</p>
                <p class="mobile-card-cliente">{{ item.cliente || 'Sin cliente' }}</p>
              </div>
              <span :class="'badge badge-' + badgeClassFactura(item.status)">{{ item.status }}</span>
            </header>

            <div class="mobile-card-grid">
              <div class="mobile-field">
                <span class="mobile-label">Total</span>
                <span class="mobile-value">{{ formatTotal(item.total) }}</span>
              </div>
              <div class="mobile-field">
                <span class="mobile-label">Fecha</span>
                <span class="mobile-value">{{ formatFecha(item.fecha) }}</span>
              </div>
              <div class="mobile-field">
                <span class="mobile-label">Ordenes</span>
                <span class="mobile-value">{{ (item.ordenes || []).join(', ') || '—' }}</span>
              </div>
              <div class="mobile-field">
                <span class="mobile-label">Pagado en</span>
                <span class="mobile-value">{{ item.lugar_pago || '—' }}</span>
              </div>
              <div class="mobile-field">
                <span class="mobile-label">Instalador</span>
                <span class="mobile-value">{{ item.instalador || '—' }}</span>
              </div>
              <div class="mobile-field">
                <span class="mobile-label">Vendedor</span>
                <span class="mobile-value">{{ item.vendedor || '—' }}</span>
              </div>
              <div class="mobile-field mobile-field-full">
                <span class="mobile-label">IMEIs</span>
                <span class="mobile-value">{{ getImeisUnicos(item).join(', ') || '—' }}</span>
              </div>
            </div>

            <div class="mobile-actions">
              <Button icon="pi pi-eye" class="p-button-sm p-button-info" label="Detalle"
                @click="irDetalle('factura', item.id)" />
              <Button icon="pi pi-download" class="p-button-sm p-button-success" label="PDF"
                :loading="descargandoId === `factura-${item.id}`"
                @click="descargarPDF('factura', item)" />
              <Button icon="pi pi-file" class="p-button-sm p-button-info p-button" label="Comprobante"
                :disabled="!parseComprobantes(item).length"
                @click="verComprobante(item)" />
              <Button icon="pi pi-code" class="p-button-sm p-button-help p-button" label="XML"
                :disabled="!item.cfdi_xml_path"
                @click="abrirArchivoCfdi(item.cfdi_xml_path)" />
              <Button icon="pi pi-file-pdf" class="p-button-sm p-button-help p-button" label="PDF Timbre"
                :disabled="!item.cfdi_pdf_path"
                @click="abrirArchivoCfdi(item.cfdi_pdf_path)" />
              <Button icon="pi pi-trash" class="p-button-sm p-button-danger" label="Eliminar"
                @click="confirmarEliminar('factura', item)" />
            </div>
          </article>
        </div>
      </div>
    </div>

    <!-- Dialogo Confirmar Eliminación -->
    <Dialog v-model:visible="showConfirmDelete" header="Confirmar Eliminación" :modal="true" :closable="false">
      <div style="padding:1.5rem; text-align:center;">
        <span>¿Seguro que deseas eliminar esta {{ eliminarTipo === 'nota' ? 'nota' : 'factura' }}?</span>
        <br />
        <small>Los reportes de servicio asociados quedarán liberados y podrán asignarse nuevamente.</small>
      </div>
      <div style="display:flex;gap:1rem;justify-content:center;padding-bottom:1rem;">
        <Button label="Eliminar" icon="pi pi-trash" class="p-button-danger" @click="ejecutarEliminar" :loading="eliminando" />
        <Button label="Cancelar" icon="pi pi-times" class="p-button-secondary" @click="showConfirmDelete = false" />
      </div>
    </Dialog>

    <!-- Dialogo Comprobantes -->
    <Dialog v-model:visible="showComprobantes" header="Comprobantes de pago" :modal="true" :style="{ width: '420px', maxWidth: '95vw' }" :draggable="false">
      <div v-if="!comprobantesActivos.length" style="text-align:center;color:var(--color-border);padding:1rem;">
        Sin comprobantes cargados.
      </div>
      <div v-else class="comprobantes-lista">
        <div v-for="(comp, idx) in comprobantesActivos" :key="idx" class="comprobante-item">
          <i class="pi pi-file" style="color:var(--color-primary);margin-right:0.5rem;"></i>
          <a :href="urlComprobante(comp)" target="_blank" rel="noopener noreferrer" class="comprobante-link">
            {{ nombreArchivoComprobante(comp) }}
          </a>
        </div>
      </div>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue';
import { useRouter } from 'vue-router';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import Dropdown from 'primevue/dropdown';
import DataTableLoader from '@/components/DataTableLoader.vue';
import { getNotas, getFacturas, getNotaById, getFacturaById, eliminarNota, eliminarFactura } from '@/services/pagosService';
import { generarPagoPDF } from '@/services/PagoPdfService';
import { useToast } from 'primevue/usetoast';

const router = useRouter();
const toast = useToast();

const tab = ref('notas');
const notas = ref([]);
const facturas = ref([]);
const loadingNotas = ref(false);
const loadingFacturas = ref(false);
const isMobile = ref(false);

// Filtros
const filtroCliente = ref('');
const filtroOrden = ref('');
const filtroImei = ref('');
const filtroInstalador = ref('');
const filtroVendedor = ref('');
const filtroLugarPago = ref('');
const filtrosAbiertos = ref(false);

const filtrosActivos = computed(() => {
  return [filtroCliente.value, filtroOrden.value, filtroImei.value, filtroInstalador.value, filtroVendedor.value, filtroLugarPago.value]
    .filter(v => (v || '').trim()).length;
});

const lugaresPago = [
  // 'ASP Vianey',
 'ASP Renovaciones', 
 'Comercializadora', 
 'BBVA PAU', 
 'Tecnico', 
 'Oficina', 
 'Mercadopago'
];

function parseImeis(value) {
  if (Array.isArray(value)) return value;
  if (typeof value !== 'string') return [];

  const raw = value.trim();
  if (!raw) return [];

  try {
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return raw.includes(',') ? raw.split(',') : [];
  }
}

function getImeisUnicos(row) {
  const arr = parseImeis(row?.imeis)
    .map(v => String(v).trim())
    .filter(Boolean);

  return Array.from(new Set(arr));
}

function filtrarRegistros(rows, { aplicarLugarPago = true } = {}) {
  let result = rows;
  const cl = filtroCliente.value.trim().toLowerCase();
  const ord = filtroOrden.value.trim().toLowerCase();
  const imei6 = filtroImei.value.trim();
  const inst = filtroInstalador.value.trim().toLowerCase();
  const vend = filtroVendedor.value.trim().toLowerCase();
  if (cl) {
    result = result.filter(r => (r.cliente || '').toLowerCase().includes(cl));
  }
  if (ord) {
    result = result.filter(r => (r.ordenes || []).some(o => String(o).toLowerCase().includes(ord)));
  }
  if (imei6) {
    result = result.filter(r => getImeisUnicos(r).some(im => String(im).endsWith(imei6)));
  }
  if (inst) {
    result = result.filter(r => (r.instalador || '').toLowerCase().includes(inst));
  }
  if (vend) {
    result = result.filter(r => (r.vendedor || '').toLowerCase().includes(vend));
  }
  if (aplicarLugarPago && filtroLugarPago.value) {
    result = result.filter(r => (r.lugar_pago || '') === filtroLugarPago.value);
  }
  return result;
}

const notasFiltradas = computed(() => filtrarRegistros(notas.value));
const facturasFiltradas = computed(() => filtrarRegistros(facturas.value));

// Resumen "Bancos": dinero por lugar de pago, combinando notas + facturas
// (excluye canceladas — dinero que no llegó al banco), ignora el filtro de
// "Pagado en" para mostrar siempre la distribución completa; los demás
// filtros (cliente, orden, imei, instalador, vendedor) sí aplican.
const resumenBancos = computed(() => {
  const notasBase = filtrarRegistros(notas.value, { aplicarLugarPago: false })
    .filter(r => r.status !== 'cancelado');
  const facturasBase = filtrarRegistros(facturas.value, { aplicarLugarPago: false })
    .filter(r => r.status !== 'Cancelado');
  const todas = [...notasBase, ...facturasBase];

  const mapa = new Map();
  const sinEspecificar = { count: 0, total: 0 };
  let totalGeneral = 0;

  for (const row of todas) {
    const monto = Number(row.total) || 0;
    totalGeneral += monto;
    const lugar = row.lugar_pago;
    if (!lugar) {
      sinEspecificar.count++;
      sinEspecificar.total += monto;
      continue;
    }
    if (!mapa.has(lugar)) mapa.set(lugar, { count: 0, total: 0 });
    const entry = mapa.get(lugar);
    entry.count++;
    entry.total += monto;
  }

  const bancos = lugaresPago.map(nombre => ({
    nombre,
    count: mapa.get(nombre)?.count || 0,
    total: mapa.get(nombre)?.total || 0,
    activo: filtroLugarPago.value === nombre,
  }));

  return { bancos, sinEspecificar, totalGeneral };
});

// Paleta categórica (identidad fija por banco, no ciclada)
const BANCO_COLORES = {
  'ASP Vianey': '#2a78d6',
  'ASP Renovaciones': '#1baf7a',
  'Comercializadora': '#eda100',
  'BBVA PAU': '#008300',
  'Tecnico': '#4a3aa7',
  'Oficina': '#e34948',
  'Mercadopago': '#e87ba4',
};

function bancoColor(nombre) {
  return BANCO_COLORES[nombre] || '#898781';
}

function pctBanco(total) {
  const totalGeneral = resumenBancos.value.totalGeneral;
  if (!totalGeneral) return '0%';
  return `${((Number(total) || 0) / totalGeneral * 100).toFixed(1)}%`;
}

function toggleFiltroBanco(nombre) {
  filtroLugarPago.value = filtroLugarPago.value === nombre ? '' : nombre;
}

const descargandoId = ref(null);
const showConfirmDelete = ref(false);
const eliminarTipo = ref('nota');
const eliminarItem = ref(null);
const eliminando = ref(false);

const API_URL = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '');
const showComprobantes = ref(false);
const comprobantesActivos = ref([]);

function parseComprobantes(row) {
  const raw = row?.comprobantes;
  if (Array.isArray(raw)) return raw;
  if (typeof raw !== 'string' || !raw.trim()) return [];
  try {
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function urlComprobante(path) {
  if (!path) return '';
  const p = path.startsWith('/') ? path : `/${path}`;
  return `${API_URL}${p}`;
}

function nombreArchivoComprobante(path) {
  if (!path) return 'comprobante';
  return path.split('/').pop();
}

function abrirArchivoCfdi(path) {
  if (!path) return;
  window.open(urlComprobante(path), '_blank', 'noopener');
}

function verComprobante(row) {
  const comps = parseComprobantes(row);
  if (!comps.length) return;
  if (comps.length === 1) {
    window.open(urlComprobante(comps[0]), '_blank', 'noopener');
    return;
  }
  comprobantesActivos.value = comps;
  showComprobantes.value = true;
}

function formatFecha(f) {
  if (!f) return '';
  const d = new Date(f);
  return `${String(d.getDate()).padStart(2, '0')}/${String(d.getMonth() + 1).padStart(2, '0')}/${d.getFullYear()}`;
}

const formatoMoneda = new Intl.NumberFormat('es-MX', {
  style: 'currency',
  currency: 'MXN',
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

function formatTotal(value) {
  return value != null ? formatoMoneda.format(Number(value)) : '-';
}

function setViewportMode() {
  isMobile.value = window.innerWidth <= 768;
}

function badgeClassNota(status) {
  if (status === 'pagado') return 'success';
  if (status === 'cancelado') return 'danger';
  return 'warning'; // pendiente de pago
}

function badgeClassFactura(status) {
  if (status === 'Timbrado') return 'success';
  if (status === 'Cancelado') return 'danger';
  return 'warning'; // Pendiente timbre
}

function irDetalle(tipo, id) {
  router.push({ name: 'detalle-pago', params: { tipo, id } });
}

function confirmarEliminar(tipo, item) {
  eliminarTipo.value = tipo;
  eliminarItem.value = item;
  showConfirmDelete.value = true;
}

async function ejecutarEliminar() {
  if (!eliminarItem.value) return;
  eliminando.value = true;
  try {
    if (eliminarTipo.value === 'nota') {
      await eliminarNota(eliminarItem.value.id);
      toast.add({ severity: 'success', summary: 'Eliminada', detail: 'Nota eliminada correctamente.', life: 3000 });
      await cargarNotas();
    } else {
      await eliminarFactura(eliminarItem.value.id);
      toast.add({ severity: 'success', summary: 'Eliminada', detail: 'Factura eliminada correctamente.', life: 3000 });
      await cargarFacturas();
    }
    showConfirmDelete.value = false;
  } catch {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo eliminar.', life: 4000 });
  }
  eliminando.value = false;
}

async function descargarPDF(tipo, data) {
  const key = `${tipo}-${data.id}`;
  descargandoId.value = key;
  try {
    const detalle = tipo === 'nota'
      ? await getNotaById(data.id)
      : await getFacturaById(data.id);
    // El endpoint de detalle puede no devolver imeis completos, instalador ni vendedor;
    // esos campos vienen del listado (data). Se fusionan tomando el listado como fuente.
    const pdfData = {
      ...detalle,
      imeis:      getImeisUnicos(data).length ? getImeisUnicos(data) : getImeisUnicos(detalle),
      instalador: data.instalador         || detalle.instalador || '',
      vendedor:   data.vendedor           || detalle.vendedor   || '',
    };
    generarPagoPDF(tipo, pdfData);
  } catch {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo generar el PDF.', life: 4000 });
  }
  descargandoId.value = null;
}

async function cargarNotas() {
  loadingNotas.value = true;
  try {
    notas.value = await getNotas();
  } catch {
    notas.value = [];
    toast.add({ severity: 'error', summary: 'Error', detail: 'Error al cargar notas.', life: 4000 });
  }
  loadingNotas.value = false;
}

async function cargarFacturas() {
  loadingFacturas.value = true;
  try {
    facturas.value = await getFacturas();
  } catch {
    facturas.value = [];
    toast.add({ severity: 'error', summary: 'Error', detail: 'Error al cargar facturas.', life: 4000 });
  }
  loadingFacturas.value = false;
}

onMounted(() => {
  setViewportMode();
  window.addEventListener('resize', setViewportMode);
  cargarNotas();
  cargarFacturas();
});

onBeforeUnmount(() => {
  window.removeEventListener('resize', setViewportMode);
});
</script>

<style scoped>
.pagos-container {
  margin: 2rem auto;
  padding: 2rem 1.5rem;
}
.pagos-title {
  text-align: center;
  margin-bottom: 1.5rem;
  color: var(--color-title);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}
.tabla-seccion {
  border-top: 3px solid var(--accent-seccion);
  padding-top: 1rem;
}
.seccion-notas {
  --accent-seccion: #2a78d6;
}
.seccion-facturas {
  --accent-seccion: #eda100;
}
.pagos-tabs {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-bottom: 1.5rem;
}
.tab-btn {
  min-width: 140px;
}
.tab-active {
  background: var(--color-title) !important;
  color: var(--color-bg) !important;
  border: none !important;
}
.tab-inactive {
  background: transparent !important;
  color: var(--color-title) !important;
  border: 2px solid var(--color-title) !important;
}
.badge {
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.85rem;
  font-weight: bold;
}
.badge-success { background: color-mix(in srgb, var(--color-success) 22%, transparent); color: var(--color-success); }
.badge-warning { background: color-mix(in srgb, var(--color-warning) 25%, transparent); color: var(--color-warning); }
.badge-danger  { background: color-mix(in srgb, var(--color-error) 20%, transparent); color: var(--color-error); }
.badge-lugar {
  background: color-mix(in srgb, var(--color-primary) 20%, transparent);
  color: var(--color-primary);
  padding: 0.2rem 0.6rem;
  border-radius: 0.75rem;
  font-size: 0.82rem;
  font-weight: 600;
}
.filtros-toggle {
  display: none;
}
.pagos-filtros {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}
.filtro-item {
  flex: 1;
  min-width: 180px;
}
.filtro-item label {
  display: block;
  font-weight: 600;
  margin-bottom: 0.3rem;
  font-size: 0.85rem;
}
.comprobantes-lista {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}
.comprobante-item {
  display: flex;
  align-items: center;
  padding: 0.4rem 0;
  border-bottom: 1px solid var(--color-border);
}
.comprobante-item:last-child {
  border-bottom: none;
}
.comprobante-link {
  color: var(--color-primary);
  font-weight: 600;
  text-decoration: none;
}
.imeis-cell {
  display: flex;
  flex-direction: column;
  gap: 2px;
  font-size: 0.85rem;
}

.bancos-resumen {
  margin-bottom: 1.5rem;
  padding: 1.25rem 1.5rem;
  border: 1px solid var(--color-border);
  background: var(--color-bg-light);
  border-radius: 14px;
  box-shadow: var(--shadow-1, 0 1px 4px rgba(0, 0, 0, 0.05));
}
.bancos-header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1.1rem;
}
.bancos-header h3 {
  margin: 0;
  font-size: 0.85rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--color-text);
  opacity: 0.7;
}
.bancos-total-general {
  font-weight: 800;
  font-size: 1.3rem;
  color: var(--color-title);
}
.bancos-grid {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 1rem;
}
.banco-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.3rem;
  flex: 1 1 200px;
  max-width: 240px;
  padding: 1.1rem 1.25rem;
  border-radius: 12px;
  border: 1px solid var(--color-border);
  border-top: 3px solid color-mix(in srgb, var(--serie-color, var(--color-border)) 65%, transparent);
  background: var(--color-card);
  cursor: pointer;
  text-align: center;
  box-shadow: var(--shadow-1, 0 1px 3px rgba(0, 0, 0, 0.05));
  transition: transform 0.15s, box-shadow 0.15s, border-color 0.15s;
}
.banco-card:hover {
  border-top-color: var(--serie-color, var(--color-primary));
  box-shadow: var(--shadow-2, 0 8px 20px rgba(0, 0, 0, 0.09));
  transform: translateY(-3px);
}
.banco-card-activo {
  border-top-color: var(--serie-color, var(--color-primary));
  background: color-mix(in srgb, var(--serie-color, var(--color-primary)) 7%, var(--color-card));
  box-shadow: 0 0 0 2px color-mix(in srgb, var(--serie-color, var(--color-primary)) 30%, transparent), var(--shadow-2, 0 8px 20px rgba(0, 0, 0, 0.09));
}
.banco-card-sin {
  cursor: default;
  background: var(--color-bg-light);
}
.banco-card-sin:hover {
  transform: none;
  box-shadow: var(--shadow-1, 0 1px 3px rgba(0, 0, 0, 0.05));
}
.banco-nombre {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-weight: 700;
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--color-text);
  opacity: 0.75;
}
.banco-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--serie-color, var(--color-border));
  flex-shrink: 0;
}
.banco-total {
  font-weight: 800;
  font-size: 1.55rem;
  color: var(--color-title);
}
.banco-pct {
  font-size: 0.78rem;
  font-weight: 700;
  padding: 0.15rem 0.6rem;
  border-radius: 999px;
  background: color-mix(in srgb, var(--serie-color, var(--color-text)) 16%, transparent);
  color: var(--serie-color, var(--color-text));
}
.banco-count {
  font-size: 0.74rem;
  color: var(--color-text);
  opacity: 0.6;
}

.mobile-list-wrap {
  margin-top: 0.5rem;
}

.mobile-loader-wrap,
.mobile-empty {
  background: var(--color-card);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 1rem;
}

.mobile-empty {
  text-align: center;
  color: var(--color-text);
}

.mobile-cards {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.mobile-card {
  border: 1px solid var(--color-border);
  background: var(--color-card);
  border-radius: 12px;
  padding: 0.9rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.mobile-card-header {
  display: flex;
  justify-content: space-between;
  gap: 0.8rem;
  align-items: flex-start;
  margin-bottom: 0.75rem;
}

.mobile-card-id {
  margin: 0;
  font-size: 0.78rem;
  color: var(--color-text);
  font-weight: 600;
}

.mobile-card-cliente {
  margin: 0.2rem 0 0;
  font-weight: 700;
  color: var(--color-title);
}

.mobile-card-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.6rem;
  margin-bottom: 0.8rem;
}

.mobile-field {
  min-width: 0;
}

.mobile-field-full {
  grid-column: 1 / -1;
}

.mobile-label {
  display: block;
  font-size: 0.72rem;
  color: var(--color-text);
  margin-bottom: 0.15rem;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.mobile-value {
  display: block;
  font-size: 0.88rem;
  color: var(--color-text);
  word-break: break-word;
}

.mobile-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

@media (max-width: 768px) {
  .pagos-container {
    margin: 1rem auto;
    padding: 1rem 0.75rem;
  }

  .pagos-tabs {
    gap: 0.5rem;
  }

  .tab-btn {
    min-width: 0;
    flex: 1;
  }

  .filtros-toggle {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;
    padding: 0.75rem 1rem;
    margin-bottom: 1rem;
    border: 1px solid var(--color-border);
    border-radius: 10px;
    background: var(--color-card);
    color: var(--color-title);
    font-weight: 600;
    font-size: 0.95rem;
  }
  .filtros-toggle span {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
  .filtros-badge {
    background: var(--color-primary);
    color: var(--color-on-primary, #fff);
    font-size: 0.72rem;
    font-weight: 700;
    border-radius: 999px;
    min-width: 1.3rem;
    height: 1.3rem;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 0 0.3rem;
  }

  .pagos-filtros {
    gap: 0.75rem;
    padding: 0.9rem;
    margin-top: -0.5rem;
    border: 1px solid var(--color-border);
    border-radius: 10px;
    background: var(--color-bg-light);
  }

  .filtro-item {
    min-width: 100%;
  }

  .bancos-resumen {
    padding: 1rem;
  }

  .bancos-grid {
    flex-wrap: nowrap;
    justify-content: flex-start;
    overflow-x: auto;
    scroll-snap-type: x mandatory;
    padding-bottom: 0.4rem;
    margin: 0 -0.25rem;
    padding-left: 0.25rem;
    padding-right: 0.25rem;
  }

  .banco-card {
    flex: 0 0 155px;
    max-width: none;
    scroll-snap-align: start;
  }
}
</style>

<template>
  <div class="np-page">
    <div class="np-header">
      <Button icon="pi pi-arrow-left" label="Facturación" class="p-button-text" @click="router.push({ name: 'facturacion' })" />
      <h2 class="np-title"><i class="pi pi-file-plus" /> Nueva prefactura</h2>
    </div>

    <div class="np-grid">
      <!-- ═══ Columna principal ═══ -->
      <div class="np-main">
        <!-- Cliente -->
        <section class="np-card">
          <h3 class="np-card-title"><i class="pi pi-user" /> Cliente</h3>

          <div v-if="clienteSeleccionado" class="np-cliente-elegido">
            <span class="np-cliente-avatar">{{ inicialesDe(clienteSeleccionado.nombre) }}</span>
            <div class="np-cliente-info">
              <strong>{{ clienteSeleccionado.nombre }}</strong>
              <span class="np-cliente-correo">{{ clienteSeleccionado.correo || 'Sin correo capturado' }}</span>
            </div>
            <span class="np-fiscal-badge" :class="fiscalBadge(clienteSeleccionado).claseCss">
              <i :class="fiscalBadge(clienteSeleccionado).icono" /> {{ fiscalBadge(clienteSeleccionado).texto }}
            </span>
            <Button icon="pi pi-times" class="p-button-text p-button-sm" title="Cambiar cliente" @click="quitarClienteSeleccionado" />
          </div>

          <template v-else>
            <AutoComplete
              v-model="clienteBusqueda"
              :suggestions="clienteSugerencias"
              @complete="buscarCliente"
              @item-select="e => seleccionarCliente(e.value)"
              optionLabel="nombre"
              placeholder="Buscar cliente por nombre..."
              class="w-full"
              :dropdown="true"
            >
              <template #option="{ option }">
                <div class="np-opcion-cliente">
                  <span>{{ option.nombre }}</span>
                  <i :class="[fiscalBadge(option).icono, fiscalBadge(option).claseCss]" :title="fiscalBadge(option).texto"></i>
                </div>
              </template>
            </AutoComplete>

            <div v-if="clienteEsNuevo" class="np-cliente-nuevo">
              <p><i class="pi pi-info-circle" /> No existe un cliente llamado "<strong>{{ clienteBusquedaTexto }}</strong>".</p>
              <Button
                v-if="!mostrarCrearCliente" label="Crear cliente nuevo" icon="pi pi-user-plus"
                class="p-button-sm p-button-outlined" @click="abrirCrearCliente"
              />
              <div v-else class="np-crear-cliente-form">
                <div class="np-crear-cliente-grid">
                  <div class="np-field">
                    <label>Nombre</label>
                    <InputText v-model="nuevoClienteForm.nombre" class="w-full" />
                  </div>
                  <div class="np-field">
                    <label>Correo (recomendado, para el CFDI)</label>
                    <InputText v-model="nuevoClienteForm.correo" placeholder="cliente@correo.com" class="w-full" />
                  </div>
                </div>
                <div style="display:flex;gap:0.5rem;">
                  <Button label="Guardar y continuar" icon="pi pi-check" class="p-button-sm" :loading="creandoCliente" @click="confirmarCrearCliente" />
                  <Button label="Cancelar" class="p-button-sm p-button-text" @click="mostrarCrearCliente = false" />
                </div>
                <small class="np-hint">Solo lo esencial — RFC, régimen y demás se completan después desde Clientes o al timbrar.</small>
              </div>
            </div>
          </template>

          <router-link to="/clientes" class="np-link-admin" target="_blank">
            <i class="pi pi-external-link" /> Administrar clientes
          </router-link>
        </section>

        <!-- Conceptos manuales -->
        <section class="np-card">
          <h3 class="np-card-title"><i class="pi pi-list" /> Conceptos manuales</h3>
          <p class="np-card-subtitle">Requerido si no hay artículos ligados arriba.</p>

          <div v-for="(prod, idx) in productosManuales" :key="idx" class="np-producto-card">
            <div class="np-producto-header">
              <span class="np-producto-numero">#{{ idx + 1 }}</span>
              <Button
                icon="pi pi-trash" class="p-button-sm p-button-danger p-button-text"
                @click="quitarProductoManual(idx)" v-if="productosManuales.length > 1"
              />
            </div>
            <div class="np-field np-producto-desc-field">
              <label>Descripción</label>
              <InputText v-model="prod.Descripcion" placeholder="Descripción del concepto" class="w-full" />
            </div>
            <div class="np-producto-grid">
              <div class="np-field">
                <label>Precio unitario</label>
                <InputNumber v-model="prod.ValorUnitario" placeholder="$0.00" mode="currency" currency="MXN" locale="es-MX" class="w-full" />
              </div>
              <div class="np-field">
                <label>Cantidad</label>
                <InputNumber v-model="prod.Cantidad" placeholder="1" :min="1" class="w-full" />
              </div>
              <div class="np-field np-producto-clave-field">
                <label>Clave SAT</label>
                <InputText v-model="prod.ClaveProdServ" placeholder="Ej. 81112501" class="w-full" />
              </div>
            </div>
          </div>
          <Button icon="pi pi-plus" label="Agregar concepto" class="p-button-sm p-button-text" @click="agregarProductoManual" />
        </section>
      </div>

      <!-- ═══ Resumen (sidebar) ═══ -->
      <aside class="np-sidebar">
        <div class="np-card np-resumen">
          <h3 class="np-card-title"><i class="pi pi-receipt" /> Resumen</h3>

          <div class="np-resumen-cliente">
            <span class="np-label">Cliente</span>
            <strong>{{ nombreClienteFinal || 'Sin elegir' }}</strong>
          </div>

          <div v-if="conceptosPreview.length" class="np-resumen-conceptos">
            <div v-for="(c, idx) in conceptosPreview" :key="idx" class="np-resumen-concepto">
              <span>{{ c.Descripcion }}</span>
              <span>{{ formatTotal(c.ValorUnitario * (c.Cantidad || 1)) }}</span>
            </div>
          </div>

          <div class="np-field">
            <label>Total</label>
            <InputNumber v-model="nuevaTotal" class="w-full" mode="currency" currency="MXN" locale="es-MX" />
          </div>

          <label class="np-pagada-toggle">
            <input type="checkbox" v-model="nuevaPagada" />
            Ya está pagada
          </label>
          <small class="np-hint">Si no la marcas, queda como "Pendiente pago" — independiente de si ya está timbrada.</small>

          <Button
            label="Generar prefactura" icon="pi pi-check" class="np-generar-btn"
            :loading="creandoFactura" :disabled="!listoParaGenerar" @click="confirmarNuevaFactura"
          />
          <small v-if="!listoParaGenerar" class="np-hint np-hint-warn">
            <i class="pi pi-exclamation-circle" /> Falta cliente, o al menos un concepto/artículo con total mayor a cero.
          </small>
        </div>
      </aside>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import InputNumber from 'primevue/inputnumber';
import AutoComplete from 'primevue/autocomplete';
import { useToast } from 'primevue/usetoast';
import { crearFactura } from '@/services/pagosService';
import { getClientes, addCliente } from '@/services/clientesService';

const router = useRouter();
const toast = useToast();

const formatoMoneda = new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN', minimumFractionDigits: 2, maximumFractionDigits: 2 });
function formatTotal(v) { return v != null ? formatoMoneda.format(Number(v)) : '-'; }
function inicialesDe(nombre) {
  const partes = (nombre || '').trim().split(/\s+/).filter(Boolean);
  if (!partes.length) return '?';
  return (partes[0][0] + (partes[1]?.[0] || '')).toUpperCase();
}

// ── Cliente: buscar existente o crear uno nuevo sin salir de la página ──
const RFC_PUBLICO_GENERAL = 'XAXX010101000';
const clientesTodos = ref([]);
const clienteBusqueda = ref('');
const clienteSugerencias = ref([]);
const clienteSeleccionado = ref(null);
const mostrarCrearCliente = ref(false);
const nuevoClienteForm = ref({ nombre: '', correo: '' });
const creandoCliente = ref(false);

const clienteBusquedaTexto = computed(() => (typeof clienteBusqueda.value === 'string' ? clienteBusqueda.value : clienteBusqueda.value?.nombre || '').trim());
const clienteEsNuevo = computed(() => {
  if (clienteSeleccionado.value || !clienteBusquedaTexto.value) return false;
  return !clientesTodos.value.some(c => (c.nombre || '').trim().toLowerCase() === clienteBusquedaTexto.value.toLowerCase());
});
const nombreClienteFinal = computed(() => clienteSeleccionado.value?.nombre || clienteBusquedaTexto.value);

function buscarCliente(event) {
  const q = (event.query || '').toLowerCase();
  clienteSugerencias.value = clientesTodos.value.filter(c => (c.nombre || '').toLowerCase().includes(q));
}
function seleccionarCliente(cliente) {
  clienteSeleccionado.value = cliente;
  mostrarCrearCliente.value = false;
}
function quitarClienteSeleccionado() {
  clienteSeleccionado.value = null;
  clienteBusqueda.value = '';
}
function fiscalBadge(cliente) {
  if (cliente?.facturapi_validado) return { texto: 'Validado SAT', icono: 'pi pi-verified', claseCss: 'np-badge-validado' };
  if (cliente?.facturapi_customer_id) return { texto: 'Sincronizado', icono: 'pi pi-sync', claseCss: 'np-badge-sincronizado' };
  if (cliente?.rfc && cliente.rfc !== RFC_PUBLICO_GENERAL && cliente.codigo_postal && cliente.regimen_fiscal) {
    return { texto: 'Datos capturados', icono: 'pi pi-check-circle', claseCss: 'np-badge-capturado' };
  }
  return { texto: 'Sin datos fiscales', icono: 'pi pi-user', claseCss: 'np-badge-generico' };
}

function abrirCrearCliente() {
  nuevoClienteForm.value = { nombre: clienteBusquedaTexto.value, correo: '' };
  mostrarCrearCliente.value = true;
}
async function confirmarCrearCliente() {
  const nombre = nuevoClienteForm.value.nombre.trim();
  if (!nombre) {
    toast.add({ severity: 'warn', summary: 'Falta el nombre', detail: 'Escribe el nombre del cliente.', life: 3500 });
    return;
  }
  creandoCliente.value = true;
  try {
    const res = await addCliente({ nombre, correo: nuevoClienteForm.value.correo.trim() });
    const nuevo = { id: res.id, nombre, correo: nuevoClienteForm.value.correo.trim(), facturapi_customer_id: res.facturapi_customer_id };
    clientesTodos.value = [...clientesTodos.value, nuevo];
    seleccionarCliente(nuevo);
    toast.add({ severity: 'success', summary: 'Cliente creado', detail: `${nombre} se agregó correctamente.`, life: 3000 });
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: e?.response?.data?.detail || 'No se pudo crear el cliente.', life: 4500 });
  }
  creandoCliente.value = false;
}

// ── Conceptos manuales ──
const productosManuales = ref([{ Descripcion: '', ValorUnitario: 0, Cantidad: 1, ClaveProdServ: '' }]);
function agregarProductoManual() {
  productosManuales.value.push({ Descripcion: '', ValorUnitario: 0, Cantidad: 1, ClaveProdServ: '' });
}
function quitarProductoManual(idx) {
  productosManuales.value.splice(idx, 1);
}

const conceptosPreview = computed(() =>
  productosManuales.value.filter(p => p.Descripcion?.trim() && Number(p.ValorUnitario) > 0)
);

// ── Resumen / total / envío ──
const nuevaTotal = ref(0);
const nuevaPagada = ref(false);
const creandoFactura = ref(false);

const listoParaGenerar = computed(() => !!nombreClienteFinal.value && conceptosPreview.value.length > 0 && Number(nuevaTotal.value) > 0);

async function confirmarNuevaFactura() {
  if (!listoParaGenerar.value) return;

  const conceptosManuales = productosManuales.value
    .filter(p => p.Descripcion?.trim() && Number(p.ValorUnitario) > 0)
    .map(p => ({
      Descripcion: p.Descripcion.trim(),
      ValorUnitario: Number(p.ValorUnitario),
      Cantidad: Number(p.Cantidad) || 1,
      ClaveProdServ: p.ClaveProdServ?.trim() || undefined
    }));

  creandoFactura.value = true;
  try {
    const res = await crearFactura({
      ordenes: [],
      cliente: nombreClienteFinal.value,
      cliente_id: clienteSeleccionado.value?.id || null,
      total: Number(nuevaTotal.value) || 0,
      status: 'Pendiente timbre',
      reporte_ids: [],
      productos_manual: conceptosManuales.length ? conceptosManuales : null,
      pagado: nuevaPagada.value
    });

    toast.add({ severity: 'success', summary: 'Prefactura creada', detail: 'Ya puedes completar sus datos fiscales y timbrarla.', life: 3500 });
    router.push({ name: 'detalle-factura', params: { id: res.id } });
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: e?.response?.data?.detail || 'No se pudo crear la prefactura.', life: 4000 });
  }
  creandoFactura.value = false;
}

onMounted(async () => {
  try {
    clientesTodos.value = await getClientes();
  } catch {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudieron cargar los clientes.', life: 4000 });
  }
});
</script>

<style scoped>
.np-page { max-width: 1160px; margin: 2rem auto; padding: 0 1.5rem 3rem; }
.np-header { display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1.5rem; flex-wrap: wrap; }
.np-title {
  display: flex; align-items: center; gap: 0.6rem; margin: 0;
  color: var(--color-title); font-size: 1.5rem; font-weight: 800; letter-spacing: -0.02em;
}
.np-title .pi { color: var(--color-primary); }

.np-grid { display: grid; grid-template-columns: 1fr 340px; gap: 1.5rem; align-items: start; }

.np-card {
  background: var(--color-card); border: 1px solid var(--color-border); border-radius: 16px;
  padding: 1.4rem 1.5rem; margin-bottom: 1.5rem;
  box-shadow: var(--shadow-1, 0 1px 4px rgba(0, 0, 0, 0.04));
}
.np-card-title {
  display: flex; align-items: center; gap: 0.5rem; margin: 0 0 0.3rem;
  color: var(--color-title); font-size: 1.02rem; font-weight: 700;
}
.np-card-title .pi { color: var(--color-primary); }
.np-card-subtitle { margin: 0 0 0.9rem; font-size: 0.83rem; color: var(--color-text); opacity: 0.7; }

.np-cliente-elegido {
  display: flex; align-items: center; gap: 0.75rem;
  padding: 0.8rem 1rem; border-radius: 12px;
  background: color-mix(in srgb, var(--color-primary) 6%, transparent);
  border: 1px solid color-mix(in srgb, var(--color-primary) 20%, transparent);
}
.np-cliente-avatar {
  display: inline-flex; align-items: center; justify-content: center;
  width: 2.4rem; height: 2.4rem; flex-shrink: 0; border-radius: 50%;
  background: color-mix(in srgb, var(--color-primary) 18%, transparent);
  color: var(--color-primary); font-size: 0.9rem; font-weight: 700;
}
.np-cliente-info { display: flex; flex-direction: column; gap: 0.1rem; flex: 1; min-width: 0; }
.np-cliente-info strong { color: var(--color-title); }
.np-cliente-correo { font-size: 0.8rem; color: var(--color-text); opacity: 0.7; }

.np-fiscal-badge {
  display: inline-flex; align-items: center; gap: 0.3rem;
  padding: 0.2rem 0.6rem; border-radius: 999px; font-size: 0.72rem; font-weight: 700; white-space: nowrap;
}
.np-badge-validado { background: color-mix(in srgb, var(--color-success) 18%, transparent); color: var(--color-success); }
.np-badge-sincronizado { background: color-mix(in srgb, var(--color-primary) 14%, transparent); color: var(--color-primary); }
.np-badge-capturado { background: color-mix(in srgb, var(--color-warning) 18%, transparent); color: var(--color-warning); }
.np-badge-generico { background: var(--color-bg-light, transparent); color: var(--color-text); opacity: 0.6; }

.np-opcion-cliente { display: flex; align-items: center; justify-content: space-between; gap: 0.6rem; }

.np-cliente-nuevo {
  margin-top: 0.8rem; padding: 0.9rem 1rem; border-radius: 12px;
  background: color-mix(in srgb, var(--color-warning) 8%, transparent);
  border: 1px solid color-mix(in srgb, var(--color-warning) 25%, transparent);
}
.np-cliente-nuevo p { margin: 0 0 0.6rem; font-size: 0.85rem; display: flex; align-items: center; gap: 0.4rem; }
.np-crear-cliente-form { display: flex; flex-direction: column; gap: 0.7rem; margin-top: 0.5rem; }
.np-crear-cliente-grid { display: flex; gap: 0.75rem; flex-wrap: wrap; }
.np-crear-cliente-grid .np-field { flex: 1; min-width: 200px; }

.np-link-admin {
  display: inline-flex; align-items: center; gap: 0.35rem; margin-top: 0.9rem;
  font-size: 0.8rem; color: var(--color-primary); text-decoration: none;
}
.np-link-admin:hover { text-decoration: underline; }

.np-field { margin-bottom: 0.2rem; }
.np-field label { display: block; font-weight: 600; margin-bottom: 0.35rem; font-size: 0.85rem; }
.np-hint { display: block; margin-top: 0.4rem; font-size: 0.78rem; color: var(--color-text); opacity: 0.65; }
.np-hint-warn { display: flex; align-items: center; gap: 0.3rem; color: var(--color-warning); opacity: 1; margin-top: 0.6rem; }

.np-producto-card {
  padding: 0.9rem 1rem; margin-bottom: 0.9rem; border-radius: 12px;
  background: var(--color-bg-light, transparent); border: 1px solid var(--color-border);
}
.np-producto-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.5rem; }
.np-producto-numero { font-size: 0.75rem; font-weight: 700; color: var(--color-text); opacity: 0.55; text-transform: uppercase; letter-spacing: 0.03em; }
.np-producto-desc-field { margin-bottom: 0.7rem; }
.np-producto-grid { display: grid; grid-template-columns: 1fr 1fr 1.4fr; gap: 0.7rem; }
@media (max-width: 560px) {
  .np-producto-grid { grid-template-columns: 1fr 1fr; }
  .np-producto-clave-field { grid-column: 1 / -1; }
}

.np-sidebar { position: sticky; top: 1.5rem; }
.np-resumen .np-card-title { margin-bottom: 1rem; }
.np-resumen-cliente {
  display: flex; flex-direction: column; gap: 0.15rem; margin-bottom: 1rem;
  padding-bottom: 0.9rem; border-bottom: 1px solid var(--color-border);
}
.np-label { font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.03em; color: var(--color-text); opacity: 0.6; }
.np-resumen-cliente strong { color: var(--color-title); font-size: 1rem; }

.np-resumen-conceptos { margin-bottom: 1rem; display: flex; flex-direction: column; gap: 0.4rem; }
.np-resumen-concepto {
  display: flex; justify-content: space-between; gap: 0.5rem;
  font-size: 0.82rem; color: var(--color-text);
}

.np-pagada-toggle { display: flex !important; align-items: center; gap: 0.5rem; cursor: pointer; margin-top: 1rem; font-size: 0.88rem; font-weight: 600; }

.np-generar-btn { width: 100%; margin-top: 1.25rem; }

@media (max-width: 900px) {
  .np-grid { grid-template-columns: 1fr; }
  .np-sidebar { position: static; }
}
@media (max-width: 600px) {
  .np-page { padding: 0 0.85rem 2rem; margin: 1rem auto; }
  .np-card { padding: 1.1rem; }
}
</style>

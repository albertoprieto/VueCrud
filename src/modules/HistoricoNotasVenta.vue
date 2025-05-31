<template>
  <div class="historico-notas-container">
    <h2 class="historico-title">Histórico de Notas de Venta</h2>
    <DataTable
      :value="ventas"
      :loading="loading"
      responsiveLayout="scroll"
      class="historico-table"
    >
      <Column
        field="id"
        header="Folio"
      />
      <Column
        field="cliente_nombre"
        header="Cliente"
      />
      <Column
        field="tecnicoNombre"
        header="Asignado a"
      >
        <template #body="slotProps">
          <span v-if="slotProps.data.tecnicoNombre" class="chip chip-asignado">
            {{ slotProps.data.tecnicoNombre }}
          </span>
          <span v-else class="chip chip-sinasignar">Sin asignar</span>
        </template>
      </Column>
      <Column
        field="status"
        header="Status"
      >
        <template #body="slotProps">
          <span
            class="chip"
            :class="{
              'chip-asignado': slotProps.data.tecnicoNombre,
              'chip-sinasignar': !slotProps.data.tecnicoNombre
            }"
          >
            {{ slotProps.data.tecnicoNombre ? 'Asignado' : 'Sin asignar' }}
          </span>
        </template>
      </Column>
      <Column header="Acciones">
        <template #body="slotProps">
          <Button
            icon="pi pi-file-pdf"
            label="PDF"
            class="p-button-sm p-button-success"
            @click="descargarPDF(slotProps.data)"
          />
          <Button
            :icon="slotProps.data.tecnicoNombre ? 'pi pi-user-edit' : 'pi pi-user-plus'"
            :label="slotProps.data.tecnicoNombre ? 'Cambiar técnico' : 'Asignar técnico'"
            class="p-button-sm p-button-info ml-2"
            @click="abrirAsignarTecnico(slotProps.data)"
          />
          <Button
            v-if="slotProps.data.tecnicoNombre"
            icon="pi pi-trash"
            label="Eliminar asignación"
            class="p-button-sm p-button-danger ml-2"
            @click="eliminarAsignacion(slotProps.data)"
          />
        </template>
      </Column>
    </DataTable>
    <Dialog v-model:visible="showDialog" header="Nota de Venta" :modal="true" class="historico-dialog">
      <NotaVentaPDF
        v-if="ventaSeleccionada && clienteSeleccionado && articulosSeleccionados.length"
        :venta="ventaSeleccionada"
        :cliente="clienteSeleccionado"
        :articulos="articulosSeleccionados"
        :empresa="empresa"
        :venta-registrada="true"
      />
      <Button label="Cerrar" icon="pi pi-times" @click="showDialog = false" class="mt-3" />
    </Dialog>
    <Dialog v-model:visible="showAsignarDialog" header="Asignar Técnico" :modal="true">
      <Dropdown
        v-model="tecnicoSeleccionado"
        :options="tecnicos"
        optionLabel="nombre"
        optionValue="id"
        placeholder="Selecciona técnico"
        class="w-full mb-3"
      />
      <Button label="Asignar" icon="pi pi-check" @click="asignarTecnico" :disabled="!tecnicoSeleccionado" />
      <Button label="Cancelar" icon="pi pi-times" @click="showAsignarDialog = false" class="p-button-secondary ml-2" />
    </Dialog>
    <Dialog v-model:visible="showResponseDialog" header="Resultado" :modal="true">
      <div style="padding:1.5rem; text-align:center;">
        <span>{{ responseMessage }}</span>
      </div>
      <Button label="Aceptar" icon="pi pi-check" @click="showResponseDialog = false" class="mt-3" />
    </Dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import DataTable from 'primevue/datatable';
import Dropdown from 'primevue/dropdown';
import Column from 'primevue/column';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import NotaVentaPDF from '@/components/NotaVentaPDF.vue';
import { getVentas, getDetalleVenta, asignarTecnicoVenta, getTecnicoVenta, deleteAsignacionTecnico } from '@/services/ventasService';
import { getClientes } from '@/services/clientesService';
import { getTodosArticulos } from '@/services/articulosService';
import { getUsuarios } from '@/services/usuariosService';

const ventas = ref([]);
const loading = ref(true);
const showDialog = ref(false);
const ventaSeleccionada = ref(null);
const clienteSeleccionado = ref(null);
const articulosSeleccionados = ref([]);
const empresa = {
  nombre: 'GPSubicacion.com',
  direccion: 'Guadalajara',
  rfc: 'RFC123456'
};
const showAsignarDialog = ref(false);
const ventaParaAsignar = ref(null);
const tecnicos = ref([]);
const tecnicoSeleccionado = ref(null);
const showResponseDialog = ref(false);
const responseMessage = ref('');

// Cargar ventas y técnicos asignados
onMounted(async () => {
  loading.value = true;
  const ventasRaw = await getVentas();
  // Para cada venta, consulta el técnico asignado
  const ventasConTecnico = await Promise.all(
    ventasRaw.map(async v => {
      const tecnico = await getTecnicoVenta(v.id);
      return {
        ...v,
        cliente_nombre: String(v.cliente_nombre ?? ''),
        tecnicoNombre: tecnico ? String(tecnico.username) : '',
        status: tecnico ? 'Asignado' : 'Sin asignar'
      };
    })
  );
  ventas.value = ventasConTecnico;
  loading.value = false;
});

async function descargarPDF(venta) {
  loading.value = true;
  ventaSeleccionada.value = venta;
  const detalle = await getDetalleVenta(venta.id);
  const clientes = await getClientes();
  clienteSeleccionado.value = clientes.find(c => c.id === venta.cliente_id) || {};
  const articulos = await getTodosArticulos();
  articulosSeleccionados.value = detalle.map(item => {
    const art = articulos.find(a => a.id === item.articulo_id) || {};
    return {
      ...item,
      sku: art.sku,
      nombre: art.nombre
    };
  });
  showDialog.value = true;
  loading.value = false;
}

async function abrirAsignarTecnico(venta) {
  ventaParaAsignar.value = venta;
  const usuarios = await getUsuarios();
  tecnicos.value = usuarios.map(u => ({
    nombre: u.username,
    id: u.id,
    perfil: u.perfil
  }));
  tecnicoSeleccionado.value = venta.tecnicoAsignado ?? null;
  showAsignarDialog.value = true;
}

async function asignarTecnico() {
  if (!ventaParaAsignar.value || !tecnicoSeleccionado.value) return;
  const res = await asignarTecnicoVenta(ventaParaAsignar.value.id, tecnicoSeleccionado.value);
  const tecnico = tecnicos.value.find(t => t.id === tecnicoSeleccionado.value);
  const idx = ventas.value.findIndex(v => v.id === ventaParaAsignar.value.id);
  if (idx !== -1 && tecnico) {
    const nuevasVentas = [...ventas.value];
    nuevasVentas[idx] = { ...nuevasVentas[idx], tecnicoAsignado: tecnico.id, tecnicoNombre: tecnico.nombre, status: 'Asignado' };
    ventas.value = nuevasVentas;
  }
  showAsignarDialog.value = false;
  responseMessage.value = res?.message || 'Técnico asignado';
  showResponseDialog.value = true;
}

async function eliminarAsignacion(venta) {
  if (!venta.id) return;
  await deleteAsignacionTecnico(venta.id);
  const idx = ventas.value.findIndex(v => v.id === venta.id);
  if (idx !== -1) {
    const nuevasVentas = [...ventas.value];
    nuevasVentas[idx] = { ...nuevasVentas[idx], tecnicoAsignado: null, tecnicoNombre: null, status: 'Sin asignar' };
    ventas.value = nuevasVentas;
  }
  responseMessage.value = 'Asignación eliminada';
  showResponseDialog.value = true;
}
</script>

<style scoped>
.historico-notas-container {
  max-width: 1000px;
  margin: 2rem auto;
  background: var(--color-bg);
  border-radius: 12px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.10);
  padding: 2rem 1.5rem;
  color: var(--color-text);
}
.historico-title {
  color: var(--color-title, #ff4081);
  text-align: center;
  margin-bottom: 2rem;
  font-size: 2rem;
  font-weight: bold;
}
.historico-table {
  margin-bottom: 2rem;
  background: var(--color-card);
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  padding: 1.5rem;
}
.historico-dialog :deep(.p-dialog-content) {
  background: var(--color-card);
  padding: 1.5rem 1rem;
  border-radius: 12px;
  color: var(--color-text);
}
.chip {
  display: inline-block;
  padding: 0.2em 0.8em;
  border-radius: 12px;
  font-size: 0.95em;
  font-weight: 500;
  margin-right: 0.2em;
  margin-bottom: 0.1em;
  vertical-align: middle;
}
.chip-asignado {
  background: var(--color-bg, #e0f7fa);
  color: var(--color-title, #00695c);
  border: 1px solid var(--color-title, #00695c);
}
.chip-sinasignar {
  background: var(--color-card, #ffe082);
  color: var(--color-text, #795548);
  border: 1px solid var(--color-text, #795548);
}
</style>
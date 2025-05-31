<template>
  <div class="historico-notas-container">
    <h2 class="historico-title">Histórico de Notas de Venta</h2>
    <DataTable :value="ventas" :loading="loading" responsiveLayout="scroll" class="historico-table">
      <Column field="id" header="Folio" />
      <Column field="cliente_nombre" header="Cliente" />
      <Column field="fecha" header="Fecha">
        <template #body="slotProps">
          {{ slotProps.data.fecha?.split('T')[0] || slotProps.data.fecha || '' }}
        </template>
      </Column>
      <Column field="total" header="Total">
        <template #body="slotProps">
          ${{ Number(slotProps.data.total).toFixed(2) }}
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
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import NotaVentaPDF from '@/components/NotaVentaPDF.vue';
import { getVentas, getDetalleVenta } from '@/services/ventasService';
import { getClientes } from '@/services/clientesService';
import { getTodosArticulos } from '@/services/articulosService';

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

onMounted(async () => {
  loading.value = true;
  ventas.value = await getVentas();
  loading.value = false;
});

async function descargarPDF(venta) {
  loading.value = true;
  ventaSeleccionada.value = venta;
  // Obtener detalle de la venta
  const detalle = await getDetalleVenta(venta.id);
  // Obtener cliente
  const clientes = await getClientes();
  clienteSeleccionado.value = clientes.find(c => c.id === venta.cliente_id) || {};
  // Obtener artículos para SKU y nombre formal
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
</style>
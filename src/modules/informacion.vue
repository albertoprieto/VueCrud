<template>
  <div class="informacion">
    <h1>Panel de Inicio</h1>
    <div class="grid-container">
      <div class="info-card" @click="showDetalle('disponibles')">
        <h2>IMEIs Disponibles</h2>
        <p class="info-value">{{ imeisDisponibles }}</p>
        <p class="info-desc">Ver resumen por ubicación y artículo</p>
      </div>
      <div class="info-card" @click="showDetalle('vendidos')">
        <h2>IMEIs Vendidos</h2>
        <p class="info-value">{{ imeisVendidos }}</p>
        <p class="info-desc">Ver resumen por ubicación y artículo</p>
      </div>
      <div class="info-card" @click="showDetalle('articulos')">
        <h2>Artículos en Inventario</h2>
        <p class="info-value">{{ totalArticulos }}</p>
        <p class="info-desc">Ver total por artículo (todas las ubicaciones)</p>
      </div>
    </div>

    <Dialog v-model:visible="showDialog" :header="dialogTitle" :modal="true" class="detalle-dialog">
      <DataTable :value="detalleDialogRows" responsiveLayout="scroll">
        <Column field="ubicacion" header="Ubicación" />
        <Column field="nombre" header="Artículo" />
        <Column field="stock" :header="dialogType === 'vendidos' ? 'Vendidos' : 'Disponibles'" />
      </DataTable>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import Dialog from 'primevue/dialog';
import { getIMEIs } from '@/services/imeiService';
import { getTodosArticulos } from '@/services/articulosService';
import { getUbicaciones } from '@/services/ubicacionesService';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';

const imeis = ref([]);
const articulos = ref([]);
const ubicaciones = ref([]);
const imeisDisponibles = computed(() => {
  // Solo IMEIs disponibles, con artículo válido (no servicio)
  return imeis.value.filter(i =>
    i.status === 'Disponible' &&
    articulos.value.some(a => a.nombre === i.articulo_nombre && a.tipo && a.tipo.toLowerCase() !== 'servicio')
  ).length;
});
const imeisVendidos = ref(0);
const totalArticulos = ref(0);

const showDialog = ref(false);
const dialogType = ref('');
const dialogTitle = ref('');
const detalleDialogRows = computed(() => {
  if (dialogType.value === 'disponibles') {
    return resumenDisponibles.value.flatMap(g =>
      g.articulos.map(a => ({ ubicacion: g.ubicacion, nombre: a.nombre, stock: a.stock }))
    );
  }
  if (dialogType.value === 'vendidos') {
    return resumenVendidos.value.flatMap(g =>
      g.articulos.map(a => ({ ubicacion: g.ubicacion, nombre: a.nombre, stock: a.stock }))
    );
  }
  if (dialogType.value === 'articulos') {
    return resumenArticulos.value.map(a => ({
      ubicacion: 'Todas',
      nombre: a.nombre,
      stock: a.stock
    }));
  }
  return [];
});

const resumenDisponibles = computed(() => {
  const grupos = [];
  ubicaciones.value.forEach(u => {
    const imeisUbic = imeis.value.filter(i => i.status === 'Disponible' && i.ubicacion_id === u.id);
    const articulosEnUbic = [];
    articulos.value.forEach(a => {
      if (a.tipo && a.tipo.toLowerCase() === 'servicio') return;
      const stock = imeisUbic.filter(i => i.articulo_nombre === a.nombre).length;
      if (stock > 0) {
        articulosEnUbic.push({ nombre: a.nombre, stock });
      }
    });
    if (articulosEnUbic.length > 0) {
      grupos.push({ ubicacion: u.nombre, articulos: articulosEnUbic });
    }
  });
  return grupos;
});

const resumenVendidos = computed(() => {
  const grupos = [];
  ubicaciones.value.forEach(u => {
    const imeisUbic = imeis.value.filter(i => i.status === 'Vendido' && i.ubicacion_id === u.id);
    const articulosEnUbic = [];
    articulos.value.forEach(a => {
      if (a.tipo && a.tipo.toLowerCase() === 'servicio') return;
      const stock = imeisUbic.filter(i => i.articulo_nombre === a.nombre).length;
      if (stock > 0) {
        articulosEnUbic.push({ nombre: a.nombre, stock });
      }
    });
    if (articulosEnUbic.length > 0) {
      grupos.push({ ubicacion: u.nombre, articulos: articulosEnUbic });
    }
  });
  return grupos;
});

const resumenArticulos = computed(() => {
  // Total por artículo en todas las ubicaciones (solo disponibles)
  return articulos.value
    .filter(a => a.tipo && a.tipo.toLowerCase() !== 'servicio')
    .map(a => {
      const stock = imeis.value.filter(i => i.status === 'Disponible' && i.articulo_nombre === a.nombre).length;
      return { nombre: a.nombre, stock };
    })
    .filter(a => a.stock > 0);
});

function showDetalle(tipo) {
  dialogType.value = tipo;
  if (tipo === 'disponibles') dialogTitle.value = 'Resumen de IMEIs Disponibles';
  else if (tipo === 'vendidos') dialogTitle.value = 'Resumen de IMEIs Vendidos';
  else if (tipo === 'articulos') dialogTitle.value = 'Artículos en Inventario';
  showDialog.value = true;
}

onMounted(async () => {
  imeis.value = await getIMEIs();
  articulos.value = await getTodosArticulos();
  ubicaciones.value = await getUbicaciones();
  imeisVendidos.value = imeis.value.filter(i => i.status === 'Vendido').length;
  totalArticulos.value = articulos.value.filter(a => a.tipo && a.tipo.toLowerCase() !== 'servicio').length;
});
</script>

<style scoped>
.informacion {
  text-align: center;
  margin: 20px;
}
.grid-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 32px;
  margin-top: 32px;
}
.info-card {
  background: var(--color-card);
  color: var(--color-text);
  border-radius: 14px;
  box-shadow: 0 4px 24px rgba(25, 118, 210, 0.10);
  padding: 2.2rem 1.5rem 1.5rem 1.5rem;
  cursor: pointer;
  transition: transform 0.18s, box-shadow 0.18s, background 0.18s;
  position: relative;
  min-height: 140px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.info-card:hover {
  transform: translateY(-8px) scale(1.03);
  box-shadow: 0 8px 32px rgba(25, 118, 210, 0.18);
  background: var(--color-bg);
}
.info-card h2 {
  color: var(--color-title);
}
.info-value {
  color: var(--color-title);
}
.info-desc {
  color: var(--color-text);
}
.detalle-dialog {
  min-width: 350px;
  max-width: 600px;
  background: var(--color-bg);
  border-radius: 12px;
  padding: 1.5rem 1rem;
}
.detalle-grupo-resumen {
  margin-bottom: 1.2rem;
  text-align: left;
  background: var(--color-card);
  border-radius: 8px;
  padding: 0.7rem 1rem;
  color: var(--color-text);
  box-shadow: 0 2px 8px rgba(25, 118, 210, 0.05);
}
.articulo-nombre {
  font-weight: 600;
  color: var(--color-title);
}
.stock-label {
  font-weight: 500;
  color: var(--color-text);
}
.detalle-grupo-resumen ul {
  margin: 0.2rem 0 0 1.2rem;
  padding: 0;
}
@media (max-width: 700px) {
  .grid-container {
    grid-template-columns: 1fr;
    gap: 18px;
  }
  .info-card {
    padding: 1.2rem 0.7rem;
    min-height: 100px;
  }
}
</style>
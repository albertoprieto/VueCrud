<template>
  <div class="articulos-con-imeis">
    <h2>Historico</h2>
    <div class="table-actions">
      <InputText v-model="filtroNombre" placeholder="Filtrar por artículo..." class="p-inputtext-sm" style="max-width:250px;" />
      <Button
        icon="pi pi-file-excel"
        class="p-button-success p-button-sm"
        label="Exportar Excel"
        style="margin-left: 1rem"
        @click="exportarInventario"
      />
    </div>
    <div class="articulos-imeis-card">
      <DataTable
        :value="historicoFiltrado"
        :sortField="sortField"
        :sortOrder="sortOrder"
        responsiveLayout="scroll"
        @sort="onSort"
        :loading="loadingImeis"
      >
        <Column field="articulo_nombre" header="Artículo" sortable />
        <Column field="precio_unitario" header="Precio unitario" sortable />
        <Column field="cantidad_total" header="Total IMEIs" sortable />
        <Column field="cantidad_disponible" header="Disponibles" sortable />
        <Column field="cantidad_vendidos" header="Vendidos" sortable />
        <Column field="total_disponible" header="Total disponibles (MXN)" sortable />
        <Column field="total_vendido" header="Total vendidos (MXN)" sortable />
        <Column field="ubicacion_nombre" header="Ubicación" sortable />
      </DataTable>
    </div>

    <!-- Resumen de totales -->
    <div class="resumen-totales">
      <div class="total-disponible">Total disponibles: <span>{{ totalDisponiblesMXN }}</span></div>
      <div class="total-vendido">Total vendidos: <span>{{ totalVendidosMXN }}</span></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { getIMEIs } from '@/services/imeiService';
import { getTodosArticulos } from '@/services/articulosService';
import { getUbicaciones } from '@/services/ubicacionesService';
import Button from 'primevue/button';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import * as XLSX from 'xlsx';
import { saveAs } from 'file-saver';

const imeis = ref([]);
const articulos = ref([]);
const ubicaciones = ref([]);
const loadingImeis = ref(true);
const showImeisDialog = ref(false);
const imeisSeleccionados = ref([]);
const filtroNombre = ref('');
const sortField = ref('articulo_nombre');
const sortOrder = ref(1);
const mostrarVendidos = ref(false);
const mostrarDisponibles = ref(false);

const articulosAgrupados = computed(() => {
  const grupos = {};
  imeis.value.forEach(i => {
    if (!grupos[i.articulo_nombre]) {
      grupos[i.articulo_nombre] = [];
    }
    grupos[i.articulo_nombre].push(i);
  });
  return Object.entries(grupos).map(([articulo_nombre, imeisArr]) => ({
    articulo_nombre,
    cantidad: imeisArr.length,
    imeis: imeisArr
  }));
});

const articulosFiltrados = computed(() => {
  if (!filtroNombre.value) return articulosAgrupados.value;
  return articulosAgrupados.value.filter(a =>
    a.articulo_nombre?.toLowerCase().includes(filtroNombre.value.toLowerCase())
  );
});

const imeisFiltrados = computed(() => {
  if (mostrarVendidos.value) {
    return imeisSeleccionados.value.filter(i => i.status === 'Vendido');
  }
  if (mostrarDisponibles.value) {
    return imeisSeleccionados.value.filter(i => i.status === 'Disponible');
  }
  return imeisSeleccionados.value;
});

const mxn = new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN' });

const historicoArticulos = computed(() => {
  const grupos = {};
  imeis.value.forEach(i => {
    if (!grupos[i.articulo_nombre]) grupos[i.articulo_nombre] = [];
    grupos[i.articulo_nombre].push(i);
  });
  return Object.entries(grupos).map(([articulo_nombre, imeisArr]) => {
    const cantidad_total = imeisArr.length;
    const cantidad_disponible = imeisArr.filter(i => i.status === 'Disponible').length;
    const cantidad_vendidos = imeisArr.filter(i => i.status === 'Vendido').length;
    const articulo = articulos.value.find(a => a.nombre === articulo_nombre);
    const precio = Number(articulo?.precioVenta) || 0;
    const ubicacion_id = imeisArr[0]?.ubicacion_id;
    const ubicacion_nombre = ubicaciones.value.find(u => u.id === ubicacion_id)?.nombre || '';
    return {
      articulo_nombre,
      precio_unitario: mxn.format(precio),
      cantidad_total,
      cantidad_disponible,
      cantidad_vendidos,
      total_disponible: mxn.format(cantidad_disponible * precio),
      total_vendido: mxn.format(cantidad_vendidos * precio),
      ubicacion_nombre,
    };
  });
});

const historicoFiltrado = computed(() => {
  if (!filtroNombre.value) return historicoArticulos.value;
  return historicoArticulos.value.filter(a =>
    a.articulo_nombre?.toLowerCase().includes(filtroNombre.value.toLowerCase())
  );
});

const totalDisponiblesMXN = computed(() =>
  mxn.format(historicoArticulos.value.reduce((acc, art) => acc + Number(art.total_disponible.replace(/[^0-9.-]+/g,"")), 0))
);

const totalVendidosMXN = computed(() =>
  mxn.format(historicoArticulos.value.reduce((acc, art) => acc + Number(art.total_vendido.replace(/[^0-9.-]+/g,"")), 0))
);

const verImeis = (articulo_nombre) => {
  const grupo = articulosAgrupados.value.find(a => a.articulo_nombre === articulo_nombre);
  imeisSeleccionados.value = grupo ? grupo.imeis : [];
  showImeisDialog.value = true;
};

const onSort = (event) => {
  sortField.value = event.sortField;
  sortOrder.value = event.sortOrder;
};

const loadIMEIs = async () => {
  loadingImeis.value = true;
  try {
    const disponibles = await getIMEIs();
    const vendidos = await fetch('https://64.227.15.111/imeis-vendidos').then(r => r.json());
    imeis.value = [...disponibles, ...vendidos];
    articulos.value = await getTodosArticulos();
    ubicaciones.value = await getUbicaciones();
  } finally {
    loadingImeis.value = false;
  }
};

// --- Exportar a Excel ---
const exportarInventario = () => {
  const grupos = {};
  imeis.value.forEach(i => {
    if (!grupos[i.articulo_nombre]) grupos[i.articulo_nombre] = [];
    grupos[i.articulo_nombre].push(i);
  });

  const mxn = new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN' });

  const data = articulos.value.map(art => {
    const stock = grupos[art.nombre]?.length || 0;
    const precio = Number(art.precioVenta) || 0;
    return {
      'Artículo': art.nombre,
      'SKU': art.sku,
      'Tipo': art.tipo,
      'Unidad': art.unidad,
      'Precio unitario': mxn.format(precio),
      'Cantidad en stock': stock,
      'Total inventario': mxn.format(precio * stock),
      'Descripción': art.descripcion,
      'Impuesto': art.impuesto,
    };
  });

  const ws = XLSX.utils.json_to_sheet(data);
  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, ws, 'Inventario');
  const excelBuffer = XLSX.write(wb, { bookType: 'xlsx', type: 'array' });
  saveAs(new Blob([excelBuffer], { type: 'application/octet-stream' }), 'inventario.xlsx');
};

const rowClass = (data) => {
  if (data.status === 'Vendido') return 'imei-vendido';
  if (data.status === 'Disponible') return 'imei-disponible';
  return '';
};

onMounted(loadIMEIs);
</script>

<style scoped>
.articulos-con-imeis {
  max-width: 900px;
  margin: 2rem auto;
  text-align: center;
  background: var(--color-bg);
  color: var(--color-text);
  border-radius: 12px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.10);
  padding: 2rem 1.5rem;
}
h2 {
  margin-bottom: 2rem;
  color: var(--color-title); /* rosa opaco llamativo */
}
.table-actions {
  margin-bottom: 1rem;
  display: flex;
  justify-content: flex-end;
}
.articulos-imeis-card {
  background: var(--color-card);
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  margin-bottom: 2rem;
}
.dialog-content {
  padding: 1rem 0.5rem;
}
.imei-vendido {
  background: linear-gradient(90deg, #ffdde1 0%, #ee9ca7 100%);
  color: #b71c1c;
  font-weight: bold;
}
.imei-disponible {
  background: linear-gradient(90deg, #e0f7fa 0%, #b2ebf2 100%);
  color: #00695c;
  font-weight: bold;
}
:root {
  --color-title: #e91e63;
  --color-card: #fff;
  --color-bg: #f7f7fa;
  --color-text: #222;
}
body.dark,
html.dark {
  --color-title: #ff80ab;
  --color-card: #23232b;
  --color-bg: #181820;
  --color-text: #eee;
}
@media (max-width: 700px) {
  .articulos-con-imeis {
    padding: 1rem 0.2rem;
  }
  .articulos-imeis-card {
    padding: 0.5rem;
  }
}
.imeis-dialog-actions {
  display: flex;
  justify-content: flex-end;
}
.vendido-label {
  background: linear-gradient(90deg, #ffdde1 0%, #ee9ca7 100%);
  color: #b71c1c;
  font-weight: bold;
  border-radius: 6px;
  padding: 0.2em 0.7em;
  display: inline-block;
}
.disponible-label {
  background: linear-gradient(90deg, #e0f7fa 0%, #b2ebf2 100%);
  color: #00695c;
  font-weight: bold;
  border-radius: 6px;
  padding: 0.2em 0.7em;
  display: inline-block;
}
.origen-vendido {
  background: #ffe0e6;
  color: #c62828;
  border-radius: 6px;
  padding: 0.15em 0.5em;
  font-size: 0.95em;
}
.origen-disponible {
  background: #e0f7fa;
  color: #00695c;
  border-radius: 6px;
  padding: 0.15em 0.5em;
  font-size: 0.95em;
}
.resumen-totales {
  display: flex;
  justify-content: center;
  gap: 2rem;
  margin-top: 1.5rem;
}
.total-disponible {
  background: #e0f7fa;
  color: #00695c;
  font-weight: bold;
  padding: 0.7em 1.5em;
  border-radius: 8px;
}
.total-vendido {
  background: #ffdde1;
  color: #b71c1c;
  font-weight: bold;
  padding: 0.7em 1.5em;
  border-radius: 8px;
}
</style>
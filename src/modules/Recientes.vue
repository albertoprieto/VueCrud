<template>
  <div class="recientes-container">
    <h2 class="recientes-title">Activaciones Recientes</h2>
    
    <!-- Zona de carga de archivo -->
    <div class="upload-section">
      <div class="upload-box" @click="triggerFileInput" @dragover.prevent @drop.prevent="handleDrop">
        <input
          ref="fileInput"
          type="file"
          accept=".xlsx,.xls"
          style="display: none"
          @change="handleFileSelect"
        />
        <span class="pi pi-cloud-upload upload-icon"></span>
        <p class="upload-text">
          Arrastra un archivo Excel, o haz clic para seleccionar
        </p>
        <p class="upload-hint">Archivos .xlsx, .xls</p>
      </div>
      
      <div v-if="fileName" class="file-info">
        <span class="pi pi-file"></span>
        <span>{{ fileName }}</span>
        <Button icon="pi pi-times" class="p-button-text p-button-danger" @click="clearFile" />
      </div>

      <div class="config-row">
        <label for="dias">Filtrar últimos:</label>
        <InputNumber id="dias" v-model="diasFiltro" :min="1" :max="365" suffix=" días" />
        <Button 
          label="Procesar" 
          icon="pi pi-cog" 
          :disabled="!selectedFile" 
          :loading="processing"
          @click="procesarArchivo" 
        />
      </div>
    </div>

    <!-- Información de procesamiento -->
    <div v-if="resultado" class="resultado-info">
      <div class="info-card-mini">
        <span class="pi pi-database"></span>
        <div>
          <strong>{{ resultado.totalRegistros }}</strong>
          <small>Total en archivo</small>
        </div>
      </div>
      <div class="info-card-mini">
        <span class="pi pi-filter"></span>
        <div>
          <strong>{{ resultado.registrosFiltrados }}</strong>
          <small>Últimos {{ diasFiltro }} días</small>
        </div>
      </div>
      <div class="info-card-mini success">
        <span class="pi pi-check-circle"></span>
        <div>
          <strong>{{ totales.conReporte }}</strong>
          <small>Con reporte</small>
        </div>
      </div>
      <div class="info-card-mini warning">
        <span class="pi pi-exclamation-triangle"></span>
        <div>
          <strong>{{ totales.sinReporte }}</strong>
          <small>Sin reporte</small>
        </div>
      </div>
    </div>

    <!-- Error -->
    <Message v-if="error" severity="error" :closable="true" @close="error = null">
      {{ error }}
    </Message>

    <!-- Tabla de datos -->
    <DataTable
      v-if="dataEnriquecida.length"
      :value="dataEnriquecida"
      :paginator="false"
      responsiveLayout="scroll"
      class="recientes-table"
      :loading="processing"
      stripedRows
      scrollable
      scrollHeight="500px"
      :rowClass="rowClass"
    >
      <template #header>
        <div class="table-header">
          <span>Activaciones - Ordenadas por fecha (más reciente primero)</span>
          <Button 
            icon="pi pi-file-excel" 
            label="Exportar sin reporte (.xlsx)" 
            class="p-button-outlined p-button-sm p-button-success"
            @click="exportarSinReporte"
            :disabled="!dataEnriquecida.length"
          />
        </div>
      </template>

      <!-- Columnas dinámicas del CSV -->
      <Column 
        v-for="col in columnasVisibles" 
        :key="col" 
        :field="col" 
        :header="col"
        :sortable="true"
        :style="getColumnStyle(col)"
      >
        <template #body="slotProps">
          <span :class="getCellClass(col)">
            {{ formatCell(slotProps.data[col], col) }}
          </span>
        </template>
      </Column>

      <!-- Columna de estado de reporte -->
      <Column header="Reporte" :style="{ minWidth: '180px' }">
        <template #body="slotProps">
          <div class="reporte-status">
            <Tag 
              v-if="slotProps.data._tieneReporte" 
              severity="success" 
              icon="pi pi-check"
            >
              Tiene Reporte
            </Tag>
            <div v-else class="sin-reporte-actions">
              <Tag severity="warning" icon="pi pi-exclamation-triangle">
                Sin Reporte
              </Tag>
              <Button
                icon="pi pi-plus"
                label="Crear"
                class="p-button-sm p-button-success mt-1"
                @click="irACrearReporte(slotProps.data)"
              />
            </div>
          </div>
        </template>
      </Column>

      <template #footer>
        <div class="table-footer">
          Total: <strong>{{ dataEnriquecida.length }}</strong> registros
        </div>
      </template>
    </DataTable>

    <!-- Estado vacío -->
    <div v-else-if="resultado && !processing" class="empty-state">
      <span class="pi pi-inbox empty-icon"></span>
      <p>No se encontraron registros en los últimos {{ diasFiltro }} días</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useToast } from 'primevue/usetoast';
import { useLoginStore } from '@/stores/loginStore';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import InputNumber from 'primevue/inputnumber';
import Message from 'primevue/message';
import Tag from 'primevue/tag';
import * as XLSX from 'xlsx';

import {
  processCSVFile,
  enrichWithReportesInfo,
  calculateTotals,
  parseDate
} from '@/services/recientesService';

const router = useRouter();
const toast = useToast();
const loginStore = useLoginStore();

// Verificar si es admin
const esAdmin = computed(() => (loginStore.user?.perfil || '').toLowerCase() === 'admin');

// Redirigir si no es admin
onMounted(() => {
  if (!esAdmin.value) {
    toast.add({
      severity: 'error',
      summary: 'Acceso denegado',
      detail: 'Solo los administradores pueden acceder a esta pantalla',
      life: 4000
    });
    router.push('/');
  }
});

// Estado
const fileInput = ref(null);
const selectedFile = ref(null);
const fileName = ref('');
const diasFiltro = ref(30);
const processing = ref(false);
const error = ref(null);
const resultado = ref(null);
const dataEnriquecida = ref([]);
const totales = ref({ totalRegistros: 0, conReporte: 0, sinReporte: 0, sinIMEI: 0 });
const imeiColumn = ref(null);
const activationColumn = ref(null);

// Columnas que se mostrarán en la tabla (solo estas, en este orden)
const COLUMNAS_VISIBLES = [
  'Cuenta',
  'Número de dispositivo',
  'Nombre del dispositivo',
  'Modelo de dispositivo',
  'Número de tarjeta SIM',
  'Hora de activación'
];

// Columnas visibles (solo las definidas que existan en los datos)
const columnasVisibles = computed(() => {
  if (!dataEnriquecida.value.length) return [];
  const allCols = Object.keys(dataEnriquecida.value[0]);
  // Filtrar solo las columnas definidas que existan en los datos
  return COLUMNAS_VISIBLES.filter(col => allCols.includes(col));
});

// Métodos
const triggerFileInput = () => {
  fileInput.value?.click();
};

const handleFileSelect = (event) => {
  const file = event.target.files?.[0];
  if (file) {
    setFile(file);
  }
};

const handleDrop = (event) => {
  const file = event.dataTransfer?.files?.[0];
  if (file) {
    setFile(file);
  }
};

const setFile = (file) => {
  if (!file.name.match(/\.(csv|xlsx|xls)$/i)) {
    toast.add({
      severity: 'error',
      summary: 'Archivo inválido',
      detail: 'Solo se aceptan archivos Excel (.xlsx, .xls) o CSV (.csv)',
      life: 4000
    });
    return;
  }
  selectedFile.value = file;
  fileName.value = file.name;
  error.value = null;
};

const clearFile = () => {
  selectedFile.value = null;
  fileName.value = '';
  resultado.value = null;
  dataEnriquecida.value = [];
  if (fileInput.value) fileInput.value.value = '';
};

const procesarArchivo = async () => {
  if (!selectedFile.value) return;

  processing.value = true;
  error.value = null;

  try {
    // Procesar el archivo (CSV o Excel)
    const res = await processCSVFile(selectedFile.value, diasFiltro.value);

    if (!res.success) {
      error.value = res.error;
      resultado.value = null;
      dataEnriquecida.value = [];
      return;
    }

    resultado.value = res;
    imeiColumn.value = res.imeiColumn;
    activationColumn.value = res.activationColumn;

    // Enriquecer con información de reportes
    const enriched = await enrichWithReportesInfo(res.data, res.imeiColumn);
    dataEnriquecida.value = enriched;

    // Calcular totales
    totales.value = calculateTotals(enriched);

    toast.add({
      severity: 'success',
      summary: 'Archivo procesado',
      detail: `${res.registrosFiltrados} registros encontrados`,
      life: 3000
    });
  } catch (err) {
    console.error('Error procesando archivo:', err);
    error.value = err.message || 'Error al procesar el archivo';
  } finally {
    processing.value = false;
  }
};

const isDateColumn = (col) => {
  const colLower = col.toLowerCase();
  return colLower.includes('fecha') || colLower.includes('hora') || colLower.includes('date') || colLower.includes('vencimiento');
};

const isNumericIdColumn = (col) => {
  const colLower = col.toLowerCase();
  return colLower.includes('dispositivo') || colLower.includes('imei') || 
         colLower.includes('sim') || colLower.includes('tarjeta') || colLower.includes('número');
};

const getColumnStyle = (col) => {
  const colLower = col.toLowerCase();
  if (colLower.includes('dispositivo') || colLower.includes('imei')) {
    return { minWidth: '160px' };
  }
  if (isDateColumn(col)) {
    return { minWidth: '150px' };
  }
  if (colLower.includes('cuenta')) {
    return { minWidth: '120px' };
  }
  if (colLower.includes('nombre')) {
    return { minWidth: '180px' };
  }
  return { minWidth: '100px' };
};

const getCellClass = (col) => {
  return {
    'fecha-col': isDateColumn(col),
    'numeric-col': isNumericIdColumn(col),
    'text-col': !isDateColumn(col) && !isNumericIdColumn(col)
  };
};

const formatCell = (value, col) => {
  if (!value || value === 'NaN' || value === 'undefined') return '-';
  
  // Formatear fechas
  if (isDateColumn(col)) {
    const date = parseDate(value);
    if (date && !isNaN(date.getTime())) {
      return date.toLocaleString('es-MX', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      });
    }
  }
  
  // Formatear números de dispositivo/IMEI - mostrar completo sin notación científica
  if (isNumericIdColumn(col)) {
    // Si es un número muy largo, convertir a string para evitar notación científica
    const strValue = String(value);
    // Remover decimales si los hay (ej: 8.67E+14 -> 867144060421094)
    if (strValue.includes('E') || strValue.includes('e')) {
      try {
        const num = Number(value);
        if (!isNaN(num)) {
          return num.toLocaleString('fullwide', { useGrouping: false });
        }
      } catch {
        return strValue;
      }
    }
    return strValue;
  }
  
  return String(value);
};

const rowClass = (data) => {
  if (data._tieneReporte) return 'row-con-reporte';
  return 'row-sin-reporte';
};

const irACrearReporte = (rowData) => {
  // Navegar a crear reporte con el IMEI precargado si existe
  const imei = imeiColumn.value ? rowData[imeiColumn.value] : null;
  router.push({
    name: 'nuevo-reporte-servicio',
    query: imei ? { imei } : {}
  });
};

const exportarSinReporte = () => {
  const sinReporte = dataEnriquecida.value.filter(row => !row._tieneReporte);
  
  if (!sinReporte.length) {
    toast.add({
      severity: 'info',
      summary: 'Sin datos',
      detail: 'Todos los registros ya tienen reporte',
      life: 3000
    });
    return;
  }

  // Preparar datos para Excel
  const cols = columnasVisibles.value;
  
  // Crear datos con formato correcto
  const excelData = sinReporte.map(row => {
    const formattedRow = {};
    cols.forEach(col => {
      let value = row[col];
      
      // Formatear números de dispositivo/IMEI como texto para evitar notación científica
      if (col.toLowerCase().includes('dispositivo') || 
          col.toLowerCase().includes('imei') || 
          col.toLowerCase().includes('sim') ||
          col.toLowerCase().includes('tarjeta')) {
        formattedRow[col] = value ? String(value) : '';
      }
      // Formatear fechas
      else if (col.toLowerCase().includes('hora') || col.toLowerCase().includes('fecha') || col.toLowerCase().includes('vencimiento')) {
        if (value) {
          const date = parseDate(value);
          if (date) {
            formattedRow[col] = date.toLocaleString('es-MX', {
              year: 'numeric',
              month: '2-digit',
              day: '2-digit',
              hour: '2-digit',
              minute: '2-digit',
              second: '2-digit'
            });
          } else {
            formattedRow[col] = value;
          }
        } else {
          formattedRow[col] = '';
        }
      }
      else {
        formattedRow[col] = value || '';
      }
    });
    return formattedRow;
  });

  // Crear worksheet
  const ws = XLSX.utils.json_to_sheet(excelData);
  
  // Calcular ancho de columnas basado en contenido
  const colWidths = cols.map(col => {
    // Ancho mínimo basado en el header
    let maxWidth = col.length;
    
    // Revisar el contenido de cada fila
    excelData.forEach(row => {
      const cellValue = String(row[col] || '');
      if (cellValue.length > maxWidth) {
        maxWidth = cellValue.length;
      }
    });
    
    // Limitar ancho máximo y agregar padding
    return { wch: Math.min(maxWidth + 2, 40) };
  });
  
  ws['!cols'] = colWidths;
  
  // Crear workbook
  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, ws, 'Sin Reporte');
  
  // Agregar hoja de resumen
  const resumenData = [
    { Concepto: 'Total registros sin reporte', Valor: sinReporte.length },
    { Concepto: 'Fecha de exportación', Valor: new Date().toLocaleString('es-MX') },
    { Concepto: 'Filtro aplicado', Valor: `Últimos ${diasFiltro.value} días` }
  ];
  const wsResumen = XLSX.utils.json_to_sheet(resumenData);
  wsResumen['!cols'] = [{ wch: 30 }, { wch: 25 }];
  XLSX.utils.book_append_sheet(wb, wsResumen, 'Resumen');
  
  // Exportar
  const fileName = `sin_reporte_${new Date().toISOString().slice(0, 10)}.xlsx`;
  XLSX.writeFile(wb, fileName);

  toast.add({
    severity: 'success',
    summary: 'Exportado',
    detail: `${sinReporte.length} registros exportados a Excel`,
    life: 3000
  });
};
</script>

<style scoped>
.recientes-container {
  padding: 1.5rem;
  max-width: 1400px;
  margin: 0 auto;
}

.recientes-title {
  text-align: center;
  font-size: 2rem;
  font-weight: 800;
  color: var(--color-title);
  margin-bottom: 2rem;
}

.upload-section {
  background: var(--color-card);
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  border: 2px solid var(--color-border);
}

.upload-box {
  border: 2px dashed var(--color-border);
  border-radius: 8px;
  padding: 2rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
  background: var(--color-bg);
}

.upload-box:hover {
  border-color: var(--color-title);
  background: var(--color-card);
}

.upload-icon {
  font-size: 3rem;
  color: var(--color-title);
  display: block;
  margin-bottom: 1rem;
}

.upload-text {
  font-size: 1.1rem;
  color: var(--color-text);
  margin-bottom: 0.5rem;
}

.upload-hint {
  font-size: 0.85rem;
  color: var(--color-text);
  opacity: 0.7;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 1rem;
  padding: 0.75rem;
  background: var(--color-bg);
  border-radius: 6px;
}

.file-info .pi-file {
  color: var(--color-title);
}

.config-row {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-top: 1.5rem;
  flex-wrap: wrap;
}

.config-row label {
  font-weight: 600;
  color: var(--color-text);
}

.resultado-info {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  margin-bottom: 1.5rem;
}

.info-card-mini {
  background: var(--color-card);
  border-radius: 10px;
  padding: 1rem 1.5rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  border: 2px solid var(--color-border);
  flex: 1;
  min-width: 140px;
}

.info-card-mini .pi {
  font-size: 1.5rem;
  color: var(--color-title);
}

.info-card-mini div {
  display: flex;
  flex-direction: column;
}

.info-card-mini strong {
  font-size: 1.4rem;
  color: var(--color-title);
}

.info-card-mini small {
  font-size: 0.8rem;
  color: var(--color-text);
  opacity: 0.8;
}

.info-card-mini.success {
  border-color: #4caf50;
}

.info-card-mini.success .pi {
  color: #4caf50;
}

.info-card-mini.warning {
  border-color: #ff9800;
}

.info-card-mini.warning .pi {
  color: #ff9800;
}

.recientes-table {
  background: var(--color-card);
  border-radius: 10px;
  overflow: hidden;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.table-footer {
  text-align: right;
  padding: 0.5rem;
}

.fecha-col {
  white-space: nowrap;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 0.9em;
}

.numeric-col {
  white-space: nowrap;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 0.9em;
  letter-spacing: 0.5px;
}

.text-col {
  word-break: break-word;
}

.reporte-status {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.25rem;
}

.sin-reporte-actions {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

:deep(.row-con-reporte) {
  background-color: rgba(76, 175, 80, 0.08) !important;
}

:deep(.row-sin-reporte) {
  background-color: rgba(255, 152, 0, 0.08) !important;
}

.empty-state {
  text-align: center;
  padding: 3rem;
  color: var(--color-text);
}

.empty-icon {
  font-size: 4rem;
  color: var(--color-border);
  display: block;
  margin-bottom: 1rem;
}

@media (max-width: 768px) {
  .recientes-container {
    padding: 1rem;
  }

  .config-row {
    flex-direction: column;
    align-items: stretch;
  }

  .resultado-info {
    flex-direction: column;
  }

  .info-card-mini {
    min-width: 100%;
  }
}
</style>

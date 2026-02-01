<template>
  <div class="recientes-container">
    <h2 class="recientes-title">Dispositivos Recientes</h2>
    
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
          Arrastra un archivo Excel para agregar nuevos dispositivos o haz clic para seleccionar uno
        </p>
      </div>
      
      <div v-if="fileName" class="file-info">
        <span class="pi pi-file"></span>
        <span>{{ fileName }}</span>
        <Button icon="pi pi-times" class="p-button-text p-button-danger" @click="clearFile" />
        <Button 
          label="Cargar Registros" 
          icon="pi pi-upload" 
          class="p-button-success"
          :disabled="!selectedFile" 
          :loading="processing"
          @click="procesarYGuardar" 
        />
      </div>
    </div>

    <!-- Información de procesamiento -->
    <div v-if="dataEnriquecida.length" class="resultado-info">
      <div class="info-card-mini">
        <span class="pi pi-list"></span>
        <div>
          <strong>{{ dataEnriquecida.length }}</strong>
          <small>Total activaciones</small>
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
      <div class="info-card-mini envio">
        <span class="pi pi-truck"></span>
        <div>
          <strong>{{ totales.esEnvio }}</strong>
          <small>Es envío</small>
        </div>
      </div>
      <div class="info-card-mini no-requiere">
        <span class="pi pi-minus-circle"></span>
        <div>
          <strong>{{ totales.noRequiere }}</strong>
          <small>No requiere</small>
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
          <div class="header-left">
            <span class="pi pi-calendar"></span>
            <span class="header-label">Últimos</span>
            <InputNumber 
              v-model="diasFiltro" 
              :min="1" 
              :max="365" 
              suffix=" días" 
              class="dias-input"
              @input="recargarDatos" 
            />
          </div>
          <Button 
            icon="pi pi-file-excel" 
            label="Exportar sin reporte" 
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
      <Column header="Reporte" :style="{ minWidth: '220px' }">
        <template #body="slotProps">
          <div class="reporte-status">
            <!-- Tiene reporte -->
            <Tag 
              v-if="slotProps.data._tieneReporte" 
              severity="success" 
              icon="pi pi-check"
            >
              Tiene Reporte
            </Tag>
            
            <!-- Cualquier otro estado -->
            <div v-else class="sin-reporte-actions">
              <!-- Tag del estado actual -->
              <Tag 
                v-if="slotProps.data._status === 'es_envio'"
                severity="warning" 
                icon="pi pi-truck"
              >
                Es envío
              </Tag>
              <Tag 
                v-else-if="slotProps.data._status === 'no_requiere'"
                severity="warning" 
                icon="pi pi-minus-circle"
              >
                No requiere
              </Tag>
              <Tag 
                v-else
                severity="danger" 
                icon="pi pi-exclamation-triangle"
              >
                Sin Reporte
              </Tag>
              
              <!-- Botones siempre visibles -->
              <div class="status-buttons">
                <Button
                  icon="pi pi-plus"
                  title="Crear Reporte"
                  class="p-button-sm p-button-success p-button-outlined"
                  @click="irACrearReporte(slotProps.data)"
                />
                <Button
                  v-if="slotProps.data._status !== 'es_envio'"
                  icon="pi pi-truck"
                  class="p-button-sm p-button-warning p-button-outlined"
                  title="Marcar como envío"
                  @click="marcarStatus(slotProps.data, 'es_envio')"
                />
                <Button
                  v-if="slotProps.data._status !== 'no_requiere'"
                  icon="pi pi-minus-circle"
                  class="p-button-sm p-button-warning p-button-outlined"
                  title="No requiere reporte"
                  @click="marcarStatus(slotProps.data, 'no_requiere')"
                />
                <Button
                  v-if="slotProps.data._status === 'es_envio' || slotProps.data._status === 'no_requiere'"
                  icon="pi pi-exclamation-triangle"
                  class="p-button-sm p-button-danger p-button-outlined"
                  title="Marcar como sin reporte"
                  @click="marcarStatus(slotProps.data, 'sin_reporte')"
                />
              </div>
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
    <div v-else-if="!processing && !dataEnriquecida.length" class="empty-state">
      <span class="pi pi-inbox empty-icon"></span>
      <p>No hay activaciones en los últimos {{ diasFiltro }} días</p>
      <p class="empty-hint">Carga un archivo Excel para agregar activaciones</p>
    </div>
    
    <!-- Cargando inicial -->
    <div v-if="processing && !dataEnriquecida.length" class="loading-state">
      <i class="pi pi-spin pi-spinner" style="font-size: 2rem"></i>
      <p>Cargando activaciones...</p>
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
  parseDate
} from '@/services/recientesService';

import {
  guardarActivacionesBulk,
  getActivacionesRecientes
} from '@/services/activacionesService';

const router = useRouter();
const toast = useToast();
const loginStore = useLoginStore();

// Verificar si es admin
const esAdmin = computed(() => (loginStore.user?.perfil || '').toLowerCase() === 'admin');

// Redirigir si no es admin, o cargar datos
onMounted(async () => {
  if (!esAdmin.value) {
    toast.add({
      severity: 'error',
      summary: 'Acceso denegado',
      detail: 'Solo los administradores pueden acceder a esta pantalla',
      life: 4000
    });
    router.push('/');
    return;
  }
  
  // Cargar datos automáticamente al entrar
  await cargarDatos();
});

// Estado
const fileInput = ref(null);
const selectedFile = ref(null);
const fileName = ref('');
const diasFiltro = ref(30);
const processing = ref(false);
const error = ref(null);
const dataEnriquecida = ref([]);
const totales = ref({ totalRegistros: 0, conReporte: 0, sinReporte: 0, esEnvio: 0, noRequiere: 0 });
const imeiColumn = ref('Número de dispositivo');

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
  if (fileInput.value) fileInput.value.value = '';
};

// Cargar datos desde la BD
const cargarDatos = async () => {
  processing.value = true;
  error.value = null;
  
  try {
    const response = await getActivacionesRecientes({
      dias: diasFiltro.value,
      limit: 2000
    });
    
    // Mapear datos de BD al formato de la tabla
    const datosMapeados = response.activaciones.map(a => ({
      _id: a.id,
      'Cuenta': a.cuenta,
      'Número de dispositivo': a.numero_dispositivo,
      'Nombre del dispositivo': a.nombre_dispositivo,
      'Modelo de dispositivo': a.modelo_dispositivo,
      'Número de tarjeta SIM': a.numero_tarjeta_sim,
      'Hora de activación': a.hora_activacion,
      _tieneReporte: a.status === 'con_reporte',
      _status: a.status,
      _reporteId: a.reporte_servicio_id,
      _folioReporte: a.folio_reporte
    }));
    
    dataEnriquecida.value = datosMapeados;
    actualizarTotales();
    
  } catch (err) {
    console.error('Error cargando datos:', err);
    // Si falla, solo mostrar tabla vacía (no es error crítico)
    dataEnriquecida.value = [];
  } finally {
    processing.value = false;
  }
};

// Recargar cuando cambia el filtro de días
let recargarTimeout = null;
const recargarDatos = () => {
  clearTimeout(recargarTimeout);
  recargarTimeout = setTimeout(() => {
    cargarDatos();
  }, 500);
};

// Procesar archivo y guardar automáticamente
const procesarYGuardar = async () => {
  if (!selectedFile.value) return;

  processing.value = true;
  error.value = null;

  try {
    // 1. Procesar el archivo Excel
    const res = await processCSVFile(selectedFile.value, diasFiltro.value);

    if (!res.success) {
      error.value = res.error;
      toast.add({
        severity: 'error',
        summary: 'Error en archivo',
        detail: res.error,
        life: 5000
      });
      return;
    }

    // 2. Guardar automáticamente en la BD
    const usuario = loginStore.user?.username || 'sistema';
    const resultadoGuardado = await guardarActivacionesBulk(res.data, usuario);
    
    toast.add({
      severity: 'success',
      summary: 'Activaciones cargadas',
      detail: `${resultadoGuardado.insertados} nuevas, ${resultadoGuardado.actualizados} actualizadas`,
      life: 4000
    });
    
    // 3. Limpiar archivo y recargar datos de la BD
    clearFile();
    await cargarDatos();
    
  } catch (err) {
    console.error('Error procesando archivo:', err);
    error.value = err.message || 'Error al procesar el archivo';
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: err.message || 'Error al procesar el archivo',
      life: 5000
    });
  } finally {
    processing.value = false;
  }
};

// Actualizar totales
const actualizarTotales = () => {
  const conReporte = dataEnriquecida.value.filter(d => d._tieneReporte).length;
  const esEnvio = dataEnriquecida.value.filter(d => d._status === 'es_envio').length;
  const noRequiere = dataEnriquecida.value.filter(d => d._status === 'no_requiere').length;
  const sinReporte = dataEnriquecida.value.filter(d => !d._tieneReporte && d._status !== 'es_envio' && d._status !== 'no_requiere').length;
  
  totales.value = {
    totalRegistros: dataEnriquecida.value.length,
    conReporte,
    sinReporte,
    esEnvio,
    noRequiere
  };
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
    return { minWidth: '100px' };
  }
  if (colLower.includes('nombre')) {
    return { minWidth: '150px', maxWidth: '200px' };
  }
  return { minWidth: '100px' };
};

const getCellClass = (col) => {
  const colLower = col.toLowerCase();
  return {
    'fecha-col': isDateColumn(col),
    'numeric-col': isNumericIdColumn(col),
    'nombre-col': colLower.includes('nombre'),
    'text-col': !isDateColumn(col) && !isNumericIdColumn(col) && !colLower.includes('nombre')
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
  if (data._status === 'es_envio') return 'row-es-envio';
  if (data._status === 'no_requiere') return 'row-no-requiere';
  return 'row-sin-reporte';
};

const irACrearReporte = (rowData) => {
  // Navegar a crear reporte con el IMEI precargado si existe
  const imei = rowData['Número de dispositivo'] || '';
  router.push({
    name: 'nuevo-reporte-servicio',
    query: imei ? { imei } : {}
  });
};

// Marcar activación con un status especial (es_envio, no_requiere)
const marcarStatus = async (rowData, nuevoStatus) => {
  try {
    const { actualizarStatusActivacion } = await import('@/services/activacionesService');
    
    // Buscar el ID de la activación (necesitamos agregarlo al mapeo)
    const activacionId = rowData._id;
    
    if (!activacionId) {
      // Si no tiene ID, necesitamos buscarlo por cuenta + numero_dispositivo
      const cuenta = rowData['Cuenta'];
      const numeroDispositivo = rowData['Número de dispositivo'];
      
      // Actualizar via endpoint especial
      const { actualizarStatusPorDispositivo } = await import('@/services/activacionesService');
      await actualizarStatusPorDispositivo(cuenta, numeroDispositivo, nuevoStatus);
    } else {
      await actualizarStatusActivacion(activacionId, nuevoStatus);
    }
    
    // Actualizar localmente
    rowData._status = nuevoStatus;
    
    // Actualizar totales reactivamente
    actualizarTotales();
    
    toast.add({
      severity: 'success',
      summary: 'Estado actualizado',
      detail: nuevoStatus === 'es_envio' ? 'Marcado como envío' : 
              nuevoStatus === 'no_requiere' ? 'Marcado como no requiere reporte' :
              'Marcado como sin reporte',
      life: 3000
    });
  } catch (err) {
    console.error('Error actualizando status:', err);
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'No se pudo actualizar el estado',
      life: 4000
    });
  }
};

const exportarSinReporte = () => {
  // Filtrar registros que NO tienen reporte (incluye sin_reporte, es_envio, no_requiere)
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

  // Preparar datos para Excel - incluir columna Status
  const cols = [...columnasVisibles.value, 'Status'];
  
  // Mapeo de status a texto legible
  const statusLabels = {
    'sin_reporte': 'Sin reporte',
    'es_envio': 'Es envío',
    'no_requiere': 'No requiere',
    'pendiente': 'Sin reporte'
  };
  
  // Crear datos con formato correcto
  const excelData = sinReporte.map(row => {
    const formattedRow = {};
    columnasVisibles.value.forEach(col => {
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
    
    // Agregar columna Status
    formattedRow['Status'] = statusLabels[row._status] || 'Sin reporte';
    
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
  
  // Agregar hoja de resumen con desglose por status
  const cantSinReporte = sinReporte.filter(r => r._status === 'sin_reporte' || r._status === 'pendiente' || !r._status).length;
  const cantEsEnvio = sinReporte.filter(r => r._status === 'es_envio').length;
  const cantNoRequiere = sinReporte.filter(r => r._status === 'no_requiere').length;
  
  const resumenData = [
    { Concepto: 'Total registros sin reporte', Valor: sinReporte.length },
    { Concepto: '  - Sin reporte (pendientes)', Valor: cantSinReporte },
    { Concepto: '  - Es envío', Valor: cantEsEnvio },
    { Concepto: '  - No requiere reporte', Valor: cantNoRequiere },
    { Concepto: '', Valor: '' },
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
  border-color: #f44336;
}

.info-card-mini.warning .pi {
  color: #f44336;
}

.info-card-mini.envio {
  border-color: #2196f3;
}

.info-card-mini.envio .pi {
  color: #2196f3;
}

.info-card-mini.no-requiere {
  border-color: #ff9800;
}

.info-card-mini.no-requiere .pi {
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

.header-left {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.header-left .pi-calendar {
  font-size: 1.1rem;
  color: var(--primary-color, #3b82f6);
}

.header-label {
  font-weight: 500;
  color: var(--color-text);
}

.dias-input {
  width: 120px;
}

.dias-input :deep(.p-inputnumber-input) {
  padding: 0.4rem 0.6rem;
  font-size: 0.9rem;
  text-align: center;
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

.nombre-col {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 200px;
  line-height: 1.3;
  word-break: break-word;
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
  gap: 0.5rem;
}

.status-buttons {
  display: flex;
  gap: 0.25rem;
  flex-wrap: wrap;
}

.estado-especial {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

:deep(.row-con-reporte) {
  background-color: rgba(76, 175, 80, 0.25) !important; /* Verde - tiene reporte */
  border-left: 4px solid #4caf50 !important;
}

:deep(.row-sin-reporte) {
  background-color: rgba(244, 67, 54, 0.25) !important; /* Rojo - sin reporte */
  border-left: 4px solid #f44336 !important;
}

:deep(.row-es-envio) {
  background-color: rgba(33, 150, 243, 0.28) !important; /* Azul - es envío */
  border-left: 4px solid #2196f3 !important;
}

:deep(.row-no-requiere) {
  background-color: rgba(255, 152, 0, 0.28) !important; /* Naranja - no requiere reporte */
  border-left: 4px solid #ff9800 !important;
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

.empty-hint {
  font-size: 0.9rem;
  opacity: 0.7;
  margin-top: 0.5rem;
}

.loading-state {
  text-align: center;
  padding: 3rem;
  color: var(--color-text);
}

.loading-state p {
  margin-top: 1rem;
}

@media (max-width: 768px) {
  .recientes-container {
    padding: 1rem;
  }

  .table-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .header-left {
    width: 100%;
    justify-content: flex-start;
  }

  .dias-input {
    flex: 1;
    max-width: 140px;
  }

  .resultado-info {
    flex-direction: column;
  }

  .info-card-mini {
    min-width: 100%;
  }
  
  .file-info {
    flex-direction: column;
    gap: 0.5rem;
  }
}
</style>

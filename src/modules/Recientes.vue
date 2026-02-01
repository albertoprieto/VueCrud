<template>
  <div class="recientes-container">
    <h2 class="recientes-title">Dispositivos Recientes</h2>
    
    <!-- Zona de carga de archivo con selector de formato integrado -->
    <div class="upload-section">
      <!-- Tabs de plataforma -->
      <div class="plataforma-tabs">
        <button 
          :class="['plataforma-tab', { 'tab-activo': formatoSeleccionado === 'iop' }]"
          @click="formatoSeleccionado = 'iop'"
        >
          <span class="pi pi-server"></span>
          <span>IOP</span>
        </button>
        <button 
          :class="['plataforma-tab', { 'tab-activo': formatoSeleccionado === 'tracksolid' }]"
          @click="formatoSeleccionado = 'tracksolid'"
        >
          <span class="pi pi-map-marker"></span>
          <span>Tracksolid</span>
        </button>
      </div>
      
      <!-- Zona de drop -->
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
          Arrastra tu archivo Excel de <strong>{{ formatoSeleccionado === 'iop' ? 'IOP' : 'Tracksolid' }}</strong>
        </p>
        <p class="upload-hint">o haz clic para seleccionar</p>
      </div>
      
      <!-- Archivo seleccionado -->
      <div v-if="fileName" class="file-info">
        <div class="file-details">
          <span class="pi pi-file-excel file-icon"></span>
          <div class="file-name-wrapper">
            <span class="file-name">{{ fileName }}</span>
            <Tag :value="formatoSeleccionado === 'iop' ? 'IOP' : 'Tracksolid'" 
                 :severity="formatoSeleccionado === 'iop' ? 'info' : 'success'" 
                 class="file-tag" />
          </div>
        </div>
        <div class="file-actions">
          <Button icon="pi pi-times" class="p-button-text p-button-danger p-button-sm" @click="clearFile" title="Quitar archivo" />
          <Button 
            label="Cargar" 
            icon="pi pi-upload"
            class="p-button-success p-button-sm"
            :disabled="!selectedFile" 
            :loading="processing"
            @click="procesarYGuardar" 
          />
        </div>
      </div>
    </div>

    <!-- Información de procesamiento con gráfica -->
    <div v-if="dataEnriquecida.length" class="stats-section">
      <!-- Gráfica circular minimalista -->
      <div class="stats-chart">
        <svg viewBox="0 0 36 36" class="circular-chart">
          <!-- Fondo gris -->
          <circle class="circle-bg" cx="18" cy="18" r="15.9155" />
          <!-- Con reporte (verde) -->
          <circle 
            class="circle-progress success" 
            cx="18" cy="18" r="15.9155"
            :stroke-dasharray="`${porcentajes.conReporte} 100`"
            stroke-dashoffset="0"
          />
          <!-- Sin reporte (rojo) - continúa después del verde -->
          <circle 
            class="circle-progress danger" 
            cx="18" cy="18" r="15.9155"
            :stroke-dasharray="`${porcentajes.sinReporte} 100`"
            :stroke-dashoffset="`${-porcentajes.conReporte}`"
          />
          <!-- Es envío (azul) -->
          <circle 
            class="circle-progress info" 
            cx="18" cy="18" r="15.9155"
            :stroke-dasharray="`${porcentajes.esEnvio} 100`"
            :stroke-dashoffset="`${-(porcentajes.conReporte + porcentajes.sinReporte)}`"
          />
          <!-- No requiere (naranja) -->
          <circle 
            class="circle-progress warning" 
            cx="18" cy="18" r="15.9155"
            :stroke-dasharray="`${porcentajes.noRequiere} 100`"
            :stroke-dashoffset="`${-(porcentajes.conReporte + porcentajes.sinReporte + porcentajes.esEnvio)}`"
          />
        </svg>
        <div class="chart-center">
          <strong>{{ dataEnriquecida.length }}</strong>
          <small>Total</small>
        </div>
      </div>
      
      <!-- Cards con porcentajes -->
      <div class="resultado-info">
        <div class="info-card-mini success">
          <div class="card-icon">
            <span class="pi pi-check-circle"></span>
          </div>
          <div class="card-content">
            <div class="card-numbers">
              <strong>{{ totales.conReporte }}</strong>
              <span class="percentage">{{ porcentajes.conReporte.toFixed(1) }}%</span>
            </div>
            <small>Con reporte</small>
            <div class="mini-bar">
              <div class="mini-bar-fill success" :style="{ width: porcentajes.conReporte + '%' }"></div>
            </div>
          </div>
        </div>
        <div class="info-card-mini warning">
          <div class="card-icon">
            <span class="pi pi-exclamation-triangle"></span>
          </div>
          <div class="card-content">
            <div class="card-numbers">
              <strong>{{ totales.sinReporte }}</strong>
              <span class="percentage">{{ porcentajes.sinReporte.toFixed(1) }}%</span>
            </div>
            <small>Sin reporte</small>
            <div class="mini-bar">
              <div class="mini-bar-fill danger" :style="{ width: porcentajes.sinReporte + '%' }"></div>
            </div>
          </div>
        </div>
        <div class="info-card-mini envio">
          <div class="card-icon">
            <span class="pi pi-truck"></span>
          </div>
          <div class="card-content">
            <div class="card-numbers">
              <strong>{{ totales.esEnvio }}</strong>
              <span class="percentage">{{ porcentajes.esEnvio.toFixed(1) }}%</span>
            </div>
            <small>Es envío</small>
            <div class="mini-bar">
              <div class="mini-bar-fill info" :style="{ width: porcentajes.esEnvio + '%' }"></div>
            </div>
          </div>
        </div>
        <div class="info-card-mini no-requiere">
          <div class="card-icon">
            <span class="pi pi-minus-circle"></span>
          </div>
          <div class="card-content">
            <div class="card-numbers">
              <strong>{{ totales.noRequiere }}</strong>
              <span class="percentage">{{ porcentajes.noRequiere.toFixed(1) }}%</span>
            </div>
            <small>No requiere</small>
            <div class="mini-bar">
              <div class="mini-bar-fill warning" :style="{ width: porcentajes.noRequiere + '%' }"></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Error -->
    <Message v-if="error" severity="error" :closable="true" @close="error = null">
      {{ error }}
    </Message>

    <!-- Tabla de datos con paginación -->
    <DataTable
      v-if="dataEnriquecida.length"
      :value="dataEnriquecida"
      :paginator="true"
      :rows="50"
      :rowsPerPageOptions="[25, 50, 100, 200]"
      paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink RowsPerPageDropdown CurrentPageReport"
      currentPageReportTemplate="Mostrando {first} a {last} de {totalRecords}"
      responsiveLayout="scroll"
      class="recientes-table"
      :loading="processing"
      stripedRows
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
      <p>No hay dispositivos activos en los últimos {{ diasFiltro }} días</p>
      <p class="empty-hint">Carga un archivo Excel para agregar dispositivos</p>
    </div>
    
    <!-- Cargando inicial -->
    <div v-if="processing && !dataEnriquecida.length" class="loading-state">
      <i class="pi pi-spin pi-spinner" style="font-size: 2rem"></i>
      <p>Cargando dispositivos activos...</p>
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
const formatoSeleccionado = ref('iop'); // 'iop' o 'tracksolid'

// Columnas que se mostrarán en la tabla (homogéneas para ambos formatos)
const COLUMNAS_VISIBLES = [
  'Plataforma',
  'Cuenta',
  'Número de dispositivo',
  'Nombre del dispositivo',
  'Modelo de dispositivo',
  'Hora de activación'
];

// Mapeo de columnas Tracksolid -> IOP
const MAPEO_TRACKSOLID = {
  'Account': 'Cuenta',
  'IMEI': 'Número de dispositivo',
  'Device Name': 'Nombre del dispositivo',
  'Model': 'Modelo de dispositivo',
  'Activated Date': 'Hora de activación'
};

// Columnas visibles (solo las definidas que existan en los datos)
const columnasVisibles = computed(() => {
  if (!dataEnriquecida.value.length) return [];
  const allCols = Object.keys(dataEnriquecida.value[0]);
  // Filtrar solo las columnas definidas que existan en los datos
  return COLUMNAS_VISIBLES.filter(col => allCols.includes(col));
});

// Porcentajes para las gráficas
const porcentajes = computed(() => {
  const total = dataEnriquecida.value.length || 1; // Evitar división por cero
  return {
    conReporte: (totales.value.conReporte / total) * 100,
    sinReporte: (totales.value.sinReporte / total) * 100,
    esEnvio: (totales.value.esEnvio / total) * 100,
    noRequiere: (totales.value.noRequiere / total) * 100
  };
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
  
  // Procesar automáticamente al seleccionar
  procesarYGuardar();
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
      'Plataforma': a.plataforma || 'IOP',
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

// Detectar formato del archivo basándose en las columnas
const detectarFormatoArchivo = async (file) => {
  return new Promise((resolve) => {
    const reader = new FileReader();
    
    reader.onload = (e) => {
      try {
        const data = new Uint8Array(e.target.result);
        const workbook = XLSX.read(data, { type: 'array' });
        const firstSheet = workbook.Sheets[workbook.SheetNames[0]];
        const jsonData = XLSX.utils.sheet_to_json(firstSheet, { header: 1 });
        
        if (jsonData.length < 1) {
          resolve({ formato: null, error: 'Archivo vacío' });
          return;
        }
        
        // Obtener headers de las primeras 3 filas (por si hay filas vacías o títulos)
        const primeraFila = jsonData[0]?.map(h => String(h || '').toLowerCase().trim()) || [];
        const segundaFila = jsonData[1]?.map(h => String(h || '').toLowerCase().trim()) || [];
        const terceraFila = jsonData[2]?.map(h => String(h || '').toLowerCase().trim()) || [];
        
        // Combinar todas las filas para búsqueda flexible
        const todasLasFilas = [...primeraFila, ...segundaFila, ...terceraFila].join(' ');
        
        console.log('Detección - Primera fila:', primeraFila.slice(0, 8));
        console.log('Detección - Segunda fila:', segundaFila.slice(0, 8));
        
        // === DETECTAR TRACKSOLID ===
        // Los headers de Tracksolid pueden ser: Account, IMEI, Device Name, Model, Activated Date, etc.
        // Buscar en primera fila (donde normalmente están)
        const tieneImei = primeraFila.some(h => h === 'imei' || h.includes('imei'));
        const tieneAccount = primeraFila.some(h => h === 'account' || h.includes('account'));
        const tieneDeviceName = primeraFila.some(h => h === 'device name' || h.includes('device name'));
        const tieneActivatedDate = primeraFila.some(h => h.includes('activated') || h.includes('activation'));
        const tieneModel = primeraFila.some(h => h === 'model' || h === 'modelo');
        
        // Tracksolid tiene IMEI como columna principal (no "Número de dispositivo")
        const esTracksolid = tieneImei || (tieneAccount && tieneDeviceName) || (tieneAccount && tieneActivatedDate);
        
        // === DETECTAR IOP ===
        // Los headers de IOP están típicamente en la fila 2 (índice 1)
        // Columnas: Cuenta, Número de dispositivo, Nombre del dispositivo, Hora de activación del servicio
        const tieneCuenta = segundaFila.some(h => h === 'cuenta');
        const tieneNumeroDispositivo = segundaFila.some(h => 
          h.includes('número de dispositivo') || h.includes('numero de dispositivo') || h === 'dispositivo'
        );
        const tieneHoraActivacion = segundaFila.some(h => 
          h.includes('hora de activación') || h.includes('hora de activacion') || h.includes('activación del servicio')
        );
        
        // IOP tiene "Cuenta" y "Número de dispositivo" (no IMEI)
        const esIOP = (tieneCuenta && tieneNumeroDispositivo) || (tieneCuenta && tieneHoraActivacion);
        
        console.log('Detección resultado:', { 
          esTracksolid, esIOP,
          tracksolid: { tieneImei, tieneAccount, tieneDeviceName, tieneActivatedDate, tieneModel },
          iop: { tieneCuenta, tieneNumeroDispositivo, tieneHoraActivacion }
        });
        
        // Determinar formato final
        if (esTracksolid && !esIOP) {
          resolve({ formato: 'tracksolid' });
        } else if (esIOP && !esTracksolid) {
          resolve({ formato: 'iop' });
        } else if (esTracksolid && esIOP) {
          // Si ambos detectados, priorizar por la columna más distintiva
          // IMEI es exclusivo de Tracksolid, "Cuenta" en segunda fila es de IOP
          resolve({ formato: tieneImei ? 'tracksolid' : 'iop' });
        } else {
          // Intento de detección por contenido de texto general
          if (todasLasFilas.includes('imei')) {
            resolve({ formato: 'tracksolid' });
          } else if (todasLasFilas.includes('cuenta') && todasLasFilas.includes('dispositivo')) {
            resolve({ formato: 'iop' });
          } else {
            resolve({ formato: null, error: 'No se pudo determinar el formato del archivo. Verifica que sea un archivo válido de IOP o Tracksolid.' });
          }
        }
        
      } catch (err) {
        console.error('Error detectando formato:', err);
        resolve({ formato: null, error: 'Error al leer el archivo' });
      }
    };
    
    reader.onerror = () => {
      resolve({ formato: null, error: 'Error al leer el archivo' });
    };
    
    reader.readAsArrayBuffer(file);
  });
};

// Procesar archivo y guardar automáticamente
const procesarYGuardar = async () => {
  if (!selectedFile.value) return;

  processing.value = true;
  error.value = null;

  try {
    // Detectar el formato real del archivo
    const deteccion = await detectarFormatoArchivo(selectedFile.value);
    
    if (deteccion.error) {
      error.value = deteccion.error;
      toast.add({
        severity: 'error',
        summary: 'Error en archivo',
        detail: deteccion.error,
        life: 5000
      });
      processing.value = false;
      return;
    }
    
    // Validar que el formato del archivo coincida con el seleccionado
    if (deteccion.formato !== formatoSeleccionado.value) {
      const formatoDetectado = deteccion.formato === 'iop' ? 'IOP' : 'Tracksolid';
      const formatoEsperado = formatoSeleccionado.value === 'iop' ? 'IOP' : 'Tracksolid';
      
      error.value = `El archivo es de ${formatoDetectado}, pero seleccionaste ${formatoEsperado}`;
      toast.add({
        severity: 'error',
        summary: 'Formato incorrecto',
        detail: `El archivo parece ser de ${formatoDetectado}. Cambia la selección o usa el archivo correcto.`,
        life: 6000
      });
      processing.value = false;
      return;
    }
    
    // Determinar la plataforma basada en el formato seleccionado
    const plataforma = formatoSeleccionado.value === 'iop' ? 'IOP' : 'Tracksolid';
    
    if (formatoSeleccionado.value === 'iop') {
      // === FORMATO IOP: Procesar y guardar en BD ===
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

      // Guardar automáticamente en la BD
      const usuario = loginStore.user?.username || 'sistema';
      const resultadoGuardado = await guardarActivacionesBulk(res.data, usuario, plataforma);
      
      toast.add({
        severity: 'success',
        summary: 'Activaciones IOP cargadas',
        detail: `${resultadoGuardado.insertados} nuevas, ${resultadoGuardado.actualizados} actualizadas`,
        life: 4000
      });
      
      // Limpiar archivo y recargar datos de la BD
      clearFile();
      await cargarDatos();
      
    } else if (formatoSeleccionado.value === 'tracksolid') {
      // === FORMATO TRACKSOLID ===
      const res = await procesarArchivoTracksolid(selectedFile.value);

      if (!res.success) {
        error.value = res.error;
        toast.add({
          severity: 'error',
          summary: 'Error en archivo Tracksolid',
          detail: res.error,
          life: 5000
        });
        return;
      }

      // Guardar en BD igual que IOP
      const usuario = loginStore.user?.username || 'sistema';
      console.log('Guardando Tracksolid con plataforma:', plataforma, '- Registros:', res.data.length);
      const resultadoGuardado = await guardarActivacionesBulk(res.data, usuario, plataforma);
      
      const statsMsg = res.stats 
        ? `(${res.stats.filtrados} filtrados de ${res.stats.totalLeidos})` 
        : '';
      
      toast.add({
        severity: 'success',
        summary: 'Tracksolid cargado',
        detail: `${resultadoGuardado.insertados} nuevas, ${resultadoGuardado.actualizados} actualizadas ${statsMsg}`,
        life: 5000
      });
      
      // Limpiar archivo y recargar datos de la BD
      clearFile();
      await cargarDatos();
    }
    
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

// Procesar archivo Tracksolid (modo prueba - solo lectura)
const procesarArchivoTracksolid = async (file) => {
  return new Promise((resolve) => {
    const reader = new FileReader();
    
    reader.onload = (e) => {
      try {
        const data = new Uint8Array(e.target.result);
        const workbook = XLSX.read(data, { type: 'array' });
        const firstSheet = workbook.Sheets[workbook.SheetNames[0]];
        
        // Leer datos con header en fila 1
        const jsonData = XLSX.utils.sheet_to_json(firstSheet, { header: 1 });
        
        if (jsonData.length < 2) {
          resolve({ success: false, error: 'El archivo está vacío o no tiene datos' });
          return;
        }
        
        // Primera fila como headers
        const headers = jsonData[0].map(h => String(h || '').trim());
        
        // Encontrar índice de columna de fecha para filtrar
        const dateColIndex = headers.findIndex(h => 
          h.toLowerCase().includes('activated') || 
          h.toLowerCase().includes('date') || 
          h.toLowerCase().includes('fecha')
        );
        
        // Calcular fecha límite según diasFiltro
        const fechaLimite = new Date();
        fechaLimite.setDate(fechaLimite.getDate() - diasFiltro.value);
        fechaLimite.setHours(0, 0, 0, 0);
        
        // Convertir filas a objetos (filtrando por fecha)
        const registros = [];
        let totalLeidos = 0;
        let filtrados = 0;
        
        for (let i = 1; i < jsonData.length; i++) {
          const row = jsonData[i];
          if (!row || row.length === 0) continue;
          
          totalLeidos++;
          
          // Filtrar por fecha si encontramos columna de fecha
          if (dateColIndex >= 0) {
            const valorFecha = row[dateColIndex];
            
            // Filtrar registros sin fecha válida (Inactive, vacío, etc.)
            if (!valorFecha || String(valorFecha).toLowerCase().includes('inactive') || String(valorFecha).trim() === '') {
              filtrados++;
              continue; // Saltar registros inválidos
            }
            
            const fechaRegistro = parseTracksolidDate(valorFecha);
            
            // Si no se pudo parsear la fecha, filtrar
            if (!fechaRegistro) {
              filtrados++;
              continue;
            }
            
            // Filtrar por rango de días
            if (fechaRegistro < fechaLimite) {
              filtrados++;
              continue; // Saltar registros fuera del rango
            }
          }
          
          // Crear registro mapeando columnas de Tracksolid a IOP
          const registro = {};
          headers.forEach((header, idx) => {
            const nombreColumna = MAPEO_TRACKSOLID[header] || header;
            registro[nombreColumna] = row[idx] !== undefined ? row[idx] : '';
          });
          
          // Agregar campos internos para compatibilidad con la tabla
          registro._tieneReporte = false;
          registro._status = 'pendiente';
          registro._formatoOrigen = 'tracksolid';
          
          registros.push(registro);
        }
        
        console.log(`Tracksolid: ${totalLeidos} leídos, ${filtrados} filtrados por fecha, ${registros.length} mostrados`);
        
        resolve({ success: true, data: registros, stats: { totalLeidos, filtrados } });
        
      } catch (err) {
        console.error('Error parseando Tracksolid:', err);
        resolve({ success: false, error: 'Error al leer el archivo: ' + err.message });
      }
    };
    
    reader.onerror = () => {
      resolve({ success: false, error: 'Error al leer el archivo' });
    };
    
    reader.readAsArrayBuffer(file);
  });
};

// Parsear fecha de Tracksolid (formato: 2025-11-11 o similar)
const parseTracksolidDate = (value) => {
  if (!value) return null;
  
  // Si es número de Excel (serial date)
  if (typeof value === 'number') {
    const excelEpoch = new Date(1899, 11, 30);
    return new Date(excelEpoch.getTime() + value * 86400000);
  }
  
  // Si es string, intentar parsear
  const str = String(value).trim();
  const parsed = new Date(str);
  return isNaN(parsed.getTime()) ? null : parsed;
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

/* Selector de formato */
.formato-selector {
  background: var(--color-card);
  border-radius: 12px;
  padding: 1rem 1.5rem;
  margin-bottom: 1rem;
  border: 2px solid var(--color-border);
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.formato-label {
  font-weight: 600;
  color: var(--color-text);
}

.formato-buttons {
  display: flex;
  gap: 0.5rem;
}

.formato-btn {
  transition: all 0.2s;
}

.formato-btn:not(.formato-activo) {
  opacity: 0.6;
  background: transparent !important;
  border-color: var(--color-border) !important;
  color: var(--color-text) !important;
}

.formato-activo {
  opacity: 1;
  box-shadow: 0 0 0 2px var(--primary-color, #3b82f6);
}

.upload-section {
  background: var(--color-card);
  border-radius: 12px;
  padding: 0;
  margin-bottom: 1.5rem;
  border: 2px solid var(--color-border);
  overflow: hidden;
}

/* Tabs de plataforma */
.plataforma-tabs {
  display: flex;
  border-bottom: 2px solid var(--color-border);
}

.plataforma-tab {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.875rem 1rem;
  border: none;
  background: var(--color-bg);
  color: var(--color-text);
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  opacity: 0.6;
}

.plataforma-tab:first-child {
  border-right: 1px solid var(--color-border);
}

.plataforma-tab:hover {
  opacity: 0.8;
  background: var(--color-card);
}

.plataforma-tab.tab-activo {
  opacity: 1;
  background: var(--color-card);
  color: var(--primary-color, #3b82f6);
  border-bottom: 3px solid var(--primary-color, #3b82f6);
  margin-bottom: -2px;
}

.plataforma-tab .pi {
  font-size: 1.1rem;
}

.upload-box {
  margin: 1rem;
  padding: 2rem;
  border: 2px dashed var(--color-border);
  border-radius: 8px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
  background: var(--color-bg);
}

.upload-box:hover {
  border-color: var(--primary-color, #3b82f6);
  background: rgba(59, 130, 246, 0.05);
}

.upload-icon {
  font-size: 2.5rem;
  color: var(--primary-color, #3b82f6);
  display: block;
  margin-bottom: 0.75rem;
  opacity: 0.8;
}

.upload-text {
  font-size: 1rem;
  color: var(--color-text);
  margin-bottom: 0.25rem;
}

.upload-hint {
  font-size: 0.8rem;
  color: var(--color-text);
  opacity: 0.5;
}

.file-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin: 0 1rem 1rem 1rem;
  padding: 0.75rem 1rem;
  background: rgba(76, 175, 80, 0.1);
  border: 1px solid rgba(76, 175, 80, 0.3);
  border-radius: 8px;
}

.file-details {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex: 1;
  min-width: 0;
}

.file-icon {
  font-size: 1.5rem;
  color: #4caf50;
}

.file-name-wrapper {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex: 1;
  min-width: 0;
}

.file-name {
  font-weight: 500;
  color: var(--color-text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.file-tag {
  flex-shrink: 0;
}

.file-actions {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  flex-shrink: 0;
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

/* Stats Section con gráfica */
.stats-section {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 1.5rem;
  align-items: flex-start;
}

.stats-chart {
  position: relative;
  width: 120px;
  height: 120px;
  flex-shrink: 0;
}

.circular-chart {
  width: 100%;
  height: 100%;
  transform: rotate(-90deg);
}

.circle-bg {
  fill: none;
  stroke: var(--color-border);
  stroke-width: 2.5;
}

.circle-progress {
  fill: none;
  stroke-width: 2.5;
  stroke-linecap: round;
  transition: stroke-dasharray 0.5s ease;
}

.circle-progress.success { stroke: #4caf50; }
.circle-progress.danger { stroke: #f44336; }
.circle-progress.info { stroke: #2196f3; }
.circle-progress.warning { stroke: #ff9800; }

.chart-center {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}

.chart-center strong {
  display: block;
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-title);
  line-height: 1;
}

.chart-center small {
  font-size: 0.7rem;
  color: var(--color-text);
  opacity: 0.7;
}

.resultado-info {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
  flex: 1;
}

.info-card-mini {
  background: var(--color-card);
  border-radius: 10px;
  padding: 0.875rem 1rem;
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  border: 2px solid var(--color-border);
  flex: 1;
  min-width: 150px;
  max-width: 200px;
}

.card-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.info-card-mini.success .card-icon {
  background: rgba(76, 175, 80, 0.15);
}

.info-card-mini.warning .card-icon {
  background: rgba(244, 67, 54, 0.15);
}

.info-card-mini.envio .card-icon {
  background: rgba(33, 150, 243, 0.15);
}

.info-card-mini.no-requiere .card-icon {
  background: rgba(255, 152, 0, 0.15);
}

.info-card-mini .pi {
  font-size: 1.1rem;
  color: var(--color-title);
}

.card-content {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-width: 0;
}

.card-numbers {
  display: flex;
  align-items: baseline;
  gap: 0.5rem;
}

.card-numbers strong {
  font-size: 1.3rem;
  color: var(--color-title);
  line-height: 1;
}

.card-numbers .percentage {
  font-size: 0.75rem;
  font-weight: 600;
  opacity: 0.7;
}

.info-card-mini small {
  font-size: 0.75rem;
  color: var(--color-text);
  opacity: 0.7;
  margin-top: 0.125rem;
}

.mini-bar {
  height: 4px;
  background: var(--color-border);
  border-radius: 2px;
  margin-top: 0.5rem;
  overflow: hidden;
}

.mini-bar-fill {
  height: 100%;
  border-radius: 2px;
  transition: width 0.5s ease;
}

.mini-bar-fill.success { background: #4caf50; }
.mini-bar-fill.danger { background: #f44336; }
.mini-bar-fill.info { background: #2196f3; }
.mini-bar-fill.warning { background: #ff9800; }

.info-card-mini.success {
  border-color: #4caf50;
}

.info-card-mini.success .pi {
  color: #4caf50;
}

.info-card-mini.success .percentage {
  color: #4caf50;
}

.info-card-mini.warning {
  border-color: #f44336;
}

.info-card-mini.warning .pi {
  color: #f44336;
}

.info-card-mini.warning .percentage {
  color: #f44336;
}

.info-card-mini.envio {
  border-color: #2196f3;
}

.info-card-mini.envio .pi {
  color: #2196f3;
}

.info-card-mini.envio .percentage {
  color: #2196f3;
}

.info-card-mini.no-requiere {
  border-color: #ff9800;
}

.info-card-mini.no-requiere .pi {
  color: #ff9800;
}

.info-card-mini.no-requiere .percentage {
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

  .stats-section {
    flex-direction: column;
    align-items: center;
  }

  .stats-chart {
    width: 100px;
    height: 100px;
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
    width: 100%;
  }

  .info-card-mini {
    min-width: 100%;
    max-width: 100%;
  }
  
  .file-info {
    flex-direction: column;
    gap: 0.5rem;
  }
}
</style>

// =====================================================
// Servicio para Activaciones Recientes
// Maneja la comunicación con los endpoints de la API
// =====================================================
import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL;

/**
 * Obtiene las activaciones recientes desde la base de datos
 * @param {Object} filtros - Filtros opcionales
 * @param {string} filtros.status - 'pendiente' | 'con_reporte' | 'sin_reporte'
 * @param {number} filtros.dias - Días de antigüedad (default: 30)
 * @param {string} filtros.cuenta - Filtrar por cuenta
 * @param {number} filtros.limit - Límite de registros
 * @returns {Promise<{total: number, activaciones: Array}>}
 */
export async function getActivacionesRecientes(filtros = {}) {
  try {
    const params = new URLSearchParams();
    
    if (filtros.status) params.append("status", filtros.status);
    if (filtros.dias) params.append("dias", filtros.dias);
    if (filtros.cuenta) params.append("cuenta", filtros.cuenta);
    if (filtros.limit) params.append("limit", filtros.limit);
    
    const response = await axios.get(`${API_URL}/activaciones-recientes`, { params });
    return response.data;
  } catch (error) {
    console.error("Error al obtener activaciones:", error);
    throw error;
  }
}

/**
 * Guarda múltiples activaciones en la base de datos (UPSERT)
 * @param {Array} activaciones - Array de activaciones a guardar
 * @param {string} cargadoPor - Usuario que carga los datos
 * @param {string} plataforma - Plataforma de origen: 'IOP' o 'Tracksolid'
 * @returns {Promise<{insertados: number, actualizados: number, errores: Array}>}
 */
export async function guardarActivacionesBulk(activaciones, cargadoPor = "sistema", plataforma = "IOP") {
  try {
    console.log('guardarActivacionesBulk - Plataforma recibida:', plataforma, '- Total registros:', activaciones.length);
    
    // Mapear los datos del Excel al formato esperado por la API
    const activacionesMapeadas = activaciones.map(a => ({
      cuenta: String(a["Cuenta"] || a.cuenta || ""),
      numero_dispositivo: String(a["Número de dispositivo"] || a.numero_dispositivo || ""),
      nombre_dispositivo: String(a["Nombre del dispositivo"] || a.nombre_dispositivo || ""),
      modelo_dispositivo: String(a["Modelo de dispositivo"] || a.modelo_dispositivo || ""),
      numero_tarjeta_sim: String(a["Número de tarjeta SIM"] || a.numero_tarjeta_sim || ""),
      hora_activacion: a["Hora de activación del servicio"] || a["Hora de activación"] || a.hora_activacion || null,
      plataforma: plataforma
    }));
    
    // Debug: ver primer registro mapeado
    console.log('Primer registro a enviar:', JSON.stringify(activacionesMapeadas[0]));
    
    const response = await axios.post(`${API_URL}/activaciones-recientes/bulk`, {
      activaciones: activacionesMapeadas,
      cargado_por: cargadoPor
    });
    
    return response.data;
  } catch (error) {
    console.error("Error al guardar activaciones:", error);
    throw error;
  }
}

/**
 * Verifica y actualiza el status de reportes para todas las activaciones
 * @returns {Promise<{actualizados_por_imei: number, actualizados_por_json: number, conteos: Object}>}
 */
export async function verificarReportesActivaciones() {
  try {
    const response = await axios.get(`${API_URL}/activaciones-recientes/verificar-reportes`);
    return response.data;
  } catch (error) {
    console.error("Error al verificar reportes:", error);
    throw error;
  }
}

/**
 * Actualiza el status de una activación específica
 * @param {number} id - ID de la activación
 * @param {string} status - Nuevo status
 * @param {number|null} reporteServicioId - ID del reporte asociado (opcional)
 * @returns {Promise<Object>}
 */
export async function actualizarStatusActivacion(id, status, reporteServicioId = null) {
  try {
    const response = await axios.put(`${API_URL}/activaciones-recientes/${id}/status`, {
      status,
      reporte_servicio_id: reporteServicioId
    });
    return response.data;
  } catch (error) {
    console.error("Error al actualizar status:", error);
    throw error;
  }
}

/**
 * Obtiene estadísticas de las activaciones
 * @returns {Promise<{por_status: Object, por_modelo: Array, ultimos_7_dias: Array}>}
 */
export async function getEstadisticasActivaciones() {
  try {
    const response = await axios.get(`${API_URL}/activaciones-recientes/stats`);
    return response.data;
  } catch (error) {
    console.error("Error al obtener estadísticas:", error);
    throw error;
  }
}

/**
 * Elimina activaciones antiguas
 * @param {number} diasAntiguedad - Eliminar registros más antiguos que X días
 * @returns {Promise<{eliminados: number}>}
 */
export async function limpiarActivacionesAntiguas(diasAntiguedad = 90) {
  try {
    const response = await axios.delete(`${API_URL}/activaciones-recientes`, {
      params: { dias_antiguedad: diasAntiguedad }
    });
    return response.data;
  } catch (error) {
    console.error("Error al limpiar activaciones:", error);
    throw error;
  }
}

/**
 * Exporta activaciones a Excel (solo las sin reporte)
 * Nota: Esta función se ejecuta del lado del cliente usando SheetJS
 * @param {Array} activaciones - Activaciones a exportar
 * @returns {Blob} - Archivo Excel
 */
export function exportarActivacionesSinReporte(activaciones) {
  // Esta función se implementa en el componente ya que usa SheetJS
  // Solo retornamos las activaciones filtradas
  return activaciones.filter(a => a.status === 'sin_reporte' || !a.tieneReporte);
}

export default {
  getActivacionesRecientes,
  guardarActivacionesBulk,
  verificarReportesActivaciones,
  actualizarStatusActivacion,
  getEstadisticasActivaciones,
  limpiarActivacionesAntiguas,
  exportarActivacionesSinReporte
};

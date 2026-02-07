// =====================================================
// Servicio para Renovaciones Recientes
// Maneja la comunicación con los endpoints de la API
// =====================================================
import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL;

/**
 * Obtiene las renovaciones recientes desde la base de datos
 * @param {Object} filtros - Filtros opcionales
 * @param {string} filtros.status - 'pendiente' | 'con_reporte' | 'sin_reporte'
 * @param {number} filtros.dias - Días de antigüedad (default: 30)
 * @param {string} filtros.cuenta - Filtrar por cuenta
 * @param {number} filtros.limit - Límite de registros
 * @returns {Promise<{total: number, renovaciones: Array}>}
 */
export async function getRenovacionesRecientes(filtros = {}) {
  try {
    const params = new URLSearchParams();
    
    if (filtros.status) params.append("status", filtros.status);
    if (filtros.dias) params.append("dias", filtros.dias);
    if (filtros.cuenta) params.append("cuenta", filtros.cuenta);
    if (filtros.limit) params.append("limit", filtros.limit);
    
    const response = await axios.get(`${API_URL}/renovaciones-recientes`, { params });
    return response.data;
  } catch (error) {
    console.error("Error al obtener renovaciones:", error);
    throw error;
  }
}

/**
 * Guarda múltiples renovaciones en la base de datos (UPSERT)
 * @param {Array} renovaciones - Array de renovaciones a guardar
 * @param {string} cargadoPor - Usuario que carga los datos
 * @param {string} plataforma - Plataforma de origen: 'IOP' o 'Tracksolid'
 * @returns {Promise<{insertados: number, actualizados: number, errores: Array}>}
 */
export async function guardarRenovacionesBulk(renovaciones, cargadoPor = "sistema", plataforma = "IOP") {
  try {
    console.log('guardarRenovacionesBulk - Plataforma recibida:', plataforma, '- Total registros:', renovaciones.length);
    
    // Mapear los datos del Excel al formato esperado por la API
    const renovacionesMapeadas = renovaciones.map(r => ({
      cuenta: String(r["Cuenta propia"] || r.cuenta || "SIN_CUENTA"),
      numero_dispositivo: String(r["Número de dispositivo"] || r.numero_dispositivo || ""),
      nombre_dispositivo: String(r["Nombre del dispositivo"] || r.nombre_dispositivo || ""),
      modelo_dispositivo: String(r["Modelo de dispositivo"] || r.modelo_dispositivo || ""),
      numero_tarjeta_sim: String(r["Número de tarjeta SIM"] || r.numero_tarjeta_sim || ""),
      hora_activacion: r["Tiempo de operación"] || r["Hora de activación"] || r.hora_activacion || null,
      periodo_de_renovacion: String(r["Período de renovación"] || r.periodo_de_renovacion || ""),
      tiempo_vencimiento_plataforma: r["Tiempo de vencimiento de la plataforma"] || r.tiempo_vencimiento_plataforma || null,
      hora_vencimiento_usuario: r["Hora de vencimiento del usuario"] || r.hora_vencimiento_usuario || null,
      fecha_renovacion: r["Fecha de renovación"] || r.fecha_renovacion || null,
      status: r._status || r.status || 'pendiente',
      plataforma: plataforma
    }));
    
    // Debug: ver primer registro mapeado
    console.log('Primer registro a enviar:', JSON.stringify(renovacionesMapeadas[0]));
    
    const response = await axios.post(`${API_URL}/renovaciones-recientes/bulk`, {
      renovaciones: renovacionesMapeadas,
      cargado_por: cargadoPor
    });
    
    return response.data;
  } catch (error) {
    console.error("Error al guardar renovaciones:", error);
    throw error;
  }
}

/**
 * Verifica y actualiza el status de reportes para todas las renovaciones
 * @returns {Promise<{actualizados_por_imei: number, conteos: Object}>}
 */
export async function verificarReportesRenovaciones() {
  try {
    const response = await axios.get(`${API_URL}/renovaciones-recientes/verificar-reportes`);
    return response.data;
  } catch (error) {
    console.error("Error al verificar reportes de renovaciones:", error);
    throw error;
  }
}

/**
 * Actualiza el status de una renovación específica
 * @param {number} id - ID de la renovación
 * @param {string} status - Nuevo status
 * @param {number|null} reporteServicioId - ID del reporte asociado (opcional)
 * @returns {Promise<Object>}
 */
export async function actualizarStatusRenovacion(id, status, reporteServicioId = null) {
  try {
    const response = await axios.put(`${API_URL}/renovaciones-recientes/${id}/status`, {
      status,
      reporte_servicio_id: reporteServicioId
    });
    return response.data;
  } catch (error) {
    console.error("Error al actualizar status de renovación:", error);
    throw error;
  }
}

/**
 * Actualiza el status de una renovación por número de dispositivo (IMEI)
 * @param {string} cuenta - Cuenta del dispositivo
 * @param {string} numeroDispositivo - IMEI del dispositivo
 * @param {string} status - Nuevo status
 * @returns {Promise<Object>}
 */
export async function actualizarStatusRenovacionPorDispositivo(cuenta, numeroDispositivo, status) {
  try {
    const response = await axios.put(`${API_URL}/renovaciones-recientes/por-dispositivo/status`, {
      cuenta,
      numero_dispositivo: numeroDispositivo,
      status
    });
    return response.data;
  } catch (error) {
    console.error("Error al actualizar status por dispositivo:", error);
    throw error;
  }
}

/**
 * Marca una renovación como sin reporte usando solo el IMEI
 * @param {string} imei - IMEI del dispositivo
 * @returns {Promise<Object>}
 */
export async function marcarRenovacionSinReportePorImei(imei) {
  try {
    const response = await axios.put(`${API_URL}/renovaciones-recientes/por-imei/sin-reporte`, {
      imei: String(imei).trim()
    });
    return response.data;
  } catch (error) {
    console.error("Error al marcar renovación sin reporte por IMEI:", error);
    throw error;
  }
}

/**
 * Obtiene estadísticas de las renovaciones
 * @returns {Promise<{por_status: Object, por_periodo: Array, ultimos_7_dias: Array}>}
 */
export async function getEstadisticasRenovaciones() {
  try {
    const response = await axios.get(`${API_URL}/renovaciones-recientes/stats`);
    return response.data;
  } catch (error) {
    console.error("Error al obtener estadísticas de renovaciones:", error);
    throw error;
  }
}

/**
 * Elimina renovaciones antiguas
 * @param {number} diasAntiguedad - Eliminar registros más antiguos que X días
 * @returns {Promise<{eliminados: number}>}
 */
export async function limpiarRenovacionesAntiguas(diasAntiguedad = 90) {
  try {
    const response = await axios.delete(`${API_URL}/renovaciones-recientes`, {
      params: { dias_antiguedad: diasAntiguedad }
    });
    return response.data;
  } catch (error) {
    console.error("Error al limpiar renovaciones:", error);
    throw error;
  }
}

export default {
  getRenovacionesRecientes,
  guardarRenovacionesBulk,
  verificarReportesRenovaciones,
  actualizarStatusRenovacion,
  actualizarStatusRenovacionPorDispositivo,
  marcarRenovacionSinReportePorImei,
  getEstadisticasRenovaciones,
  limpiarRenovacionesAntiguas
};

import axios from 'axios';

const API_URL = `${import.meta.env.VITE_API_URL}/reportes-servicio`;

export const addReporteServicio = async (data) => {
  try {
    const response = await axios.post(API_URL, data);
    return response.data;
  } catch (error) {
    // Re-lanzar el error para que sea manejado por el componente
    throw error;
  }
};

export const getReportePorAsignacion = async (asignacion_id) => {
  try {
    const res = await axios.get(`${API_URL}?asignacion_id=${asignacion_id}`);
    return res.data;
  } catch (error) {
    // Si es 404, no existe el reporte, devolver null
    if (error.response && error.response.status === 404) {
      return null;
    }
    // Para otros errores, re-lanzar
    throw error;
  }
};

// Nuevo: obtener todos los reportes (incluye campos de comprobante)
export const getTodosReportes = async () => {
  const res = await axios.get(`${API_URL}-todos`);
  return res.data || [];
};
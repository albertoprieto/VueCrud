import axios from 'axios';

const API_URL = 'https://api.gpsubicacionapi.com/reportes';

export const addReporte = async (reporteData) => {
  const response = await axios.post(API_URL, reporteData);
  return response.data;
};

export const getReportesByEvento = async (eventoId) => {
  const response = await axios.get(`${API_URL}?eventoId=${eventoId}`);
  return response.data;
};

// Obtener todos los reportes de servicio
export const getReportesServicioTodos = async () => {
  const response = await axios.get('https://api.gpsubicacionapi.com/reportes-servicio-todos');
  return response.data;
};

// Badge: contar reportes no pagados
export async function getReportesNuevos() {
  const reportes = await getReportesServicioTodos();
  return Array.isArray(reportes)
    ? reportes.filter(r => !r.pagado).length
    : 0;
}

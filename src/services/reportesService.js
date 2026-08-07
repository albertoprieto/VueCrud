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

// Excusa temporal para que un reporte no cuente como "pendiente" en
// comisiones (ver utils/comisiones.js) — tipo: 'tecnico' | 'cliente'.
export const marcarPermisoPendiente = async (reporteId, { tipo, fecha_compromiso, usuario }) => {
  const response = await axios.put(
    `https://api.gpsubicacionapi.com/reportes-servicio/${reporteId}/permiso-pendiente`,
    { tipo, fecha_compromiso, usuario }
  );
  return response.data;
};

export const quitarPermisoPendiente = async (reporteId) => {
  const response = await axios.delete(`https://api.gpsubicacionapi.com/reportes-servicio/${reporteId}/permiso-pendiente`);
  return response.data;
};

// Reasignar el vendedor/responsable de un reporte (ej. transferir un
// pendiente de comprobante a otro vendedor) — no deja rastro del vendedor
// original, el reporte pasa completo al nuevo.
export const transferirVendedor = async (reporteId, vendedor) => {
  const response = await axios.put(`https://api.gpsubicacionapi.com/reportes-servicio/${reporteId}`, { vendedor });
  return response.data;
};

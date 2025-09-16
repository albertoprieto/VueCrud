import axios from 'axios';

const API_URL = `${import.meta.env.VITE_API_URL}/reportes-servicio`;

export const addReporteServicio = async (data) => {
  return await axios.post(API_URL, data);
};

export const getReportePorAsignacion = async (asignacion_id) => {
  const res = await axios.get(`${API_URL}?asignacion_id=${asignacion_id}`);
  return res.data;
};

// Nuevo: obtener todos los reportes (incluye campos de comprobante)
export const getTodosReportes = async () => {
  const res = await axios.get(`${API_URL}-todos`);
  return res.data || [];
};
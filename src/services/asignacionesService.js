import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL;

export const getAsignacionesTecnicos = async () => {
  const res = await axios.get(`${API_URL}/asignaciones-tecnicos`);
  return res.data;
};

export const getAsignacionVenta = async (ventaId) => {
  // GET /ventas/:id/asignacion
  const res = await axios.get(`${API_URL}/ventas/${ventaId}/asignacion`);
  return res.data;
};
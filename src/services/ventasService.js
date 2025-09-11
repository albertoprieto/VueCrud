import axios from 'axios';

const API_URL = `${import.meta.env.VITE_API_URL}/ventas`;

export const getVentas = async () => {
  const res = await axios.get(API_URL);
  return res.data;
};

export const addVenta = async (venta) => {
  const res = await axios.post(API_URL, venta);
  return res.data;
};

export const getDetalleVenta = async (ventaId) => {
  const res = await axios.get(`${API_URL}/${ventaId}/detalle`);
  return res.data;
};

export const asignarTecnicoVenta = async (ventaId, tecnicoId, fecha_servicio, extraPayload = null) => {
  const base = { tecnico_id: tecnicoId, fecha_servicio };
  // Aseguramos que base no pise campos extra y permitimos override si extraPayload redefine tecnico_id / fecha_servicio
  const body = extraPayload ? { ...base, ...extraPayload } : base;
  console.log('[ventasService] POST asignar-tecnico body ->', body);
  return await axios.post(`${API_URL}/${ventaId}/asignar-tecnico`, body);
};

export const getTecnicoVenta = async (ventaId) => {
  const res = await axios.get(`${API_URL}/${ventaId}/tecnico`);
  return res.data;
};

export const deleteAsignacionTecnico = async (ventaId) => {
  return await axios.delete(`${API_URL}/${ventaId}/asignar-tecnico`);
};
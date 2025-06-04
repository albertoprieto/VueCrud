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

export const asignarTecnicoVenta = async (ventaId, tecnicoId, fecha_servicio) => {
  return await axios.post(`${API_URL}/${ventaId}/asignar-tecnico`, {
    tecnico_id: tecnicoId,
    fecha_servicio
  });
};

export const getTecnicoVenta = async (ventaId) => {
  const res = await axios.get(`${API_URL}/${ventaId}/tecnico`);
  return res.data;
};

export const deleteAsignacionTecnico = async (ventaId) => {
  return await axios.delete(`${API_URL}/${ventaId}/asignar-tecnico`);
};
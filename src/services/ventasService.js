import axios from 'axios';

const API_URL = 'https://64.227.15.111/ventas';

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
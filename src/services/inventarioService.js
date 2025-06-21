import axios from 'axios';

export const getMovimientosInventario = async () => {
  const res = await axios.get(`${import.meta.env.VITE_API_URL}/movimientos-inventario`);
  return res.data;
};

export const registrarMovimiento = async (movimiento) => {
  return axios.post(`${import.meta.env.VITE_API_URL}/movimientos-inventario`, movimiento);
};
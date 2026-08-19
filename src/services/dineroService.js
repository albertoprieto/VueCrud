import axios from 'axios';

export const getMovimientosDineroPorReferencia = async (referencia) => {
  const apiUrl = import.meta.env.VITE_API_URL || '';
  const res = await axios.get(`${apiUrl}/movimientos-dinero`);
  // Filtra por referencia exacta o que contenga la referencia
  return res.data.filter(mov => mov.referencia && mov.referencia.includes(referencia));
};

export const registrarAbonoDinero = async ({ archivo, ...movimiento }) => {
  const apiUrl = import.meta.env.VITE_API_URL || '';
  const fd = new FormData();
  Object.entries(movimiento).forEach(([k, v]) => { if (v !== undefined && v !== null) fd.append(k, v); });
  if (archivo) fd.append('archivo', archivo);
  return axios.post(`${apiUrl}/movimientos-dinero`, fd, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

export const eliminarComprobanteMovimientoDinero = async (id) => {
  const apiUrl = import.meta.env.VITE_API_URL || '';
  const res = await axios.delete(`${apiUrl}/movimientos-dinero/${id}/comprobante`);
  return res.data;
};

export const getMovimientosDinero = async () => {
  const apiUrl = import.meta.env.VITE_API_URL || '';
  const res = await axios.get(`${apiUrl}/movimientos-dinero`);
  return res.data;
};

export const actualizarMovimientoDinero = async (id, data) => {
  const apiUrl = import.meta.env.VITE_API_URL || '';
  const res = await axios.put(`${apiUrl}/movimientos-dinero/${id}`, data);
  return res.data;
};

export const eliminarMovimientoDinero = async (id) => {
  const apiUrl = import.meta.env.VITE_API_URL || '';
  const res = await axios.delete(`${apiUrl}/movimientos-dinero/${id}`);
  return res.data;
};

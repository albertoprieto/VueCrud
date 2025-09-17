import axios from 'axios';

const API_URL = `${import.meta.env.VITE_API_URL}/clientes`;

export const getClientes = async () => {
  const res = await axios.get(API_URL);
  return res.data;
};

export const addCliente = async (cliente) => {
  const res = await axios.post(API_URL, cliente);
  return res.data;
};

export const updateCliente = async (id, cliente) => {
  const res = await axios.put(`${API_URL}/${id}`, cliente);
  return res.data;
};

export const deleteCliente = async (id) => {
  const res = await axios.delete(`${API_URL}/${id}`);
  return res.data;
};

export const getConstanciaVentaReciente = async (clienteId) => {
  const res = await axios.get(`${API_URL}/${clienteId}/constancia-venta-reciente`);
  return res.data; // { hasConstancia, venta_id, folio, rfc, fecha, constancia_url }
};

// Nuevo: eliminar constancia de una venta específica (si se usa desde clientes)
export const deleteConstanciaVenta = async (ventaId) => {
  const API_VENTAS = `${import.meta.env.VITE_API_URL}/ventas`;
  const res = await axios.delete(`${API_VENTAS}/${ventaId}/constancia`);
  return res.data;
};
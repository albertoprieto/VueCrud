import axios from 'axios';

const API_URL = `${import.meta.env.VITE_API_URL}/articulos`;

export const getArticulos = async () => {
  const res = await axios.get(API_URL);
  return res.data;
};

export const getTodosArticulos = async () => {
  const res = await axios.get(`${API_URL}/todos`);
  return res.data;
};

export const getArticulosStockPorUbicacion = async (ubicacionId) => {
  const res = await axios.get(`${import.meta.env.VITE_API_URL}/ubicaciones/${ubicacionId}/articulos-stock`);
  return res.data;
};

export const addArticulo = async (articulo) => {
  const res = await axios.post(API_URL, articulo);
  return res.data;
};

export const updateArticulo = async (articulo) => {
  const res = await axios.put(`${API_URL}/${articulo.id}`, articulo);
  return res.data;
};

export const deleteArticulo = async (id) => {
  const res = await axios.delete(`${API_URL}/${id}`);
  return res.data;
};

export const sincronizarStockArticulos = async () => {
  return await axios.post(`${API_URL}/sincronizar-stock-imeis`);
};
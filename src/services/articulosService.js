import axios from 'axios';

const API_URL = 'https://64.227.15.111/articulos';

export const getArticulos = async () => {
  const res = await axios.get(API_URL);
  return res.data;
};

export const getTodosArticulos = async () => {
  const res = await axios.get(`${API_URL}/todos`);
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
  return await axios.post('https://64.227.15.111/articulos/sincronizar-stock-imeis');
};
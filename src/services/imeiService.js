import axios from 'axios';

const API_URL = `${import.meta.env.VITE_API_URL}/imeis`;

export const addIMEI = async (imeiData) => {
  const response = await axios.post(API_URL, imeiData);
  return response.data;
};

export const getIMEIs = async () => {
  const res = await axios.get(API_URL);
  return res.data;
};

export const updateIMEI = async (imei, data) => {
  const response = await axios.put(`${API_URL}/${imei}`, data);
  return response.data;
};

export const asignarIMEIsAArticulo = async (articuloId, imeis) => {
  return await axios.post(`${import.meta.env.VITE_API_URL}/articulos/${articuloId}/asignar-imeis`, imeis);
};

export const registrarYAsignarIMEIs = async (articuloId, imeis, registeredBy = "Sistema") => {
  return await axios.post(
    `${import.meta.env.VITE_API_URL}/articulos/${articuloId}/registrar-y-asignar-imeis`,
    { imeis, registeredBy }
  );
};

export const registrarYAsignarIMEIsPorNombre = async (articuloNombre, imeis, registeredBy = "Sistema") => {
  return await axios.post(
    `${import.meta.env.VITE_API_URL}/articulos/nombre/${encodeURIComponent(articuloNombre)}/registrar-y-asignar-imeis`,
    { imeis, registeredBy }
  );
};

export const getIMEIsByArticuloNombre = async (articuloNombre) => {
  const response = await axios.get(`${API_URL}?articulo_nombre=${encodeURIComponent(articuloNombre)}`);
  return response.data;
};

export const getIMEIsByArticulo = async (articuloId) => {
  const response = await axios.get(`${API_URL}?articulo_id=${articuloId}`);
  return response.data;
};

export const getStockByArticuloId = async (articuloId) => {
  const response = await axios.get(`${import.meta.env.VITE_API_URL}/articulos/${articuloId}/stock`);
  return response.data.stock;
};

export const getStockByArticuloNombre = async (articuloNombre) => {
  const response = await axios.get(`${import.meta.env.VITE_API_URL}/articulos/nombre/${encodeURIComponent(articuloNombre)}/stock`);
  return response.data.stock;
};

export const devolverIMEI = async (imei) => {
  const res = await axios.post(`${API_URL}/${imei}/devolver`);
  return res.data;
};

export const deleteIMEI = async (imei) => {
  const res = await axios.delete(`${API_URL}/${imei}`);
  return res.data;
};

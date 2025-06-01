import axios from 'axios';

const API_URL = 'https://api.gpsubicacionapi.com/imeis';

export const addIMEI = async (imeiData) => {
  const response = await axios.post(API_URL, imeiData);
  return response.data;
};

export const getIMEIs = async () => {
  const res = await axios.get(API_URL);
  return res.data;
};

export const updateIMEI = async (imei, data) => {
  const response = await axios.put(`https://api.gpsubicacionapi.com/imeis/${imei}`, data);
  return response.data;
};

export const asignarIMEIsAArticulo = async (articuloId, imeis) => {
  return await axios.post(`https://api.gpsubicacionapi.com/articulos/${articuloId}/asignar-imeis`, imeis);
};

export const registrarYAsignarIMEIs = async (articuloId, imeis, registeredBy = "Sistema") => {
  return await axios.post(
    `https://api.gpsubicacionapi.com/articulos/${articuloId}/registrar-y-asignar-imeis`,
    { imeis, registeredBy }
  );
};

export const registrarYAsignarIMEIsPorNombre = async (articuloNombre, imeis, registeredBy = "Sistema") => {
  return await axios.post(
    `https://api.gpsubicacionapi.com/articulos/nombre/${encodeURIComponent(articuloNombre)}/registrar-y-asignar-imeis`,
    { imeis, registeredBy }
  );
};

export const getIMEIsByArticuloNombre = async (articuloNombre) => {
  const response = await axios.get(`https://api.gpsubicacionapi.com/imeis?articulo_nombre=${encodeURIComponent(articuloNombre)}`);
  return response.data;
};

export const getIMEIsByArticulo = async (articuloId) => {
  const response = await axios.get(`https://api.gpsubicacionapi.com/imeis?articulo_id=${articuloId}`);
  return response.data;
};

export const getStockByArticuloId = async (articuloId) => {
  const response = await axios.get(`https://api.gpsubicacionapi.com/articulos/${articuloId}/stock`);
  return response.data.stock;
};

export const getStockByArticuloNombre = async (articuloNombre) => {
  const response = await axios.get(`https://api.gpsubicacionapi.com/articulos/nombre/${encodeURIComponent(articuloNombre)}/stock`);
  return response.data.stock;
};

export const devolverIMEI = async (imei) => {
  const res = await axios.post(`https://api.gpsubicacionapi.com/imeis/${imei}/devolver`);
  return res.data;
};

export const deleteIMEI = async (imei) => {
  const res = await axios.delete(`https://api.gpsubicacionapi.com/imeis/${imei}`);
  return res.data;
};

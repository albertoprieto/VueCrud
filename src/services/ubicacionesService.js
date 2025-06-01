import axios from 'axios';

const API_URL = 'https://api.gpsubicacionapi.com/ubicaciones';

export const getUbicaciones = async () => {
  const res = await axios.get(API_URL);
  return res.data;
};

export const getImeisPorUbicacion = async (ubicacionId) => {
  const res = await axios.get(`${API_URL}/${ubicacionId}/imeis`);
  return res.data;
};

export const asignarImeisUbicacion = async (ubicacionId, imeis) => {
  const res = await axios.post(`${API_URL}/${ubicacionId}/asignar-imeis`, { imeis, ubicacion_id: ubicacionId });
  return res.data;
};

export const addUbicacion = async (ubicacion) => {
  const res = await axios.post(API_URL, ubicacion);
  return res.data;
};

export const updateUbicacion = async (id, ubicacion) => {
  const res = await axios.put(`${API_URL}/${id}`, ubicacion);
  return res.data;
};

export const deleteUbicacion = async (id) => {
  const res = await axios.delete(`${API_URL}/${id}`);
  return res.data;
};
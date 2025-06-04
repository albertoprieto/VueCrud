import axios from 'axios';

const API_URL = `${import.meta.env.VITE_API_URL}/eventos`;

export const getEventos = async () => {
  const response = await axios.get(API_URL);
  return response.data;
};

export const updateEventoStatus = async (id, status) => {
  const response = await axios.patch(`${API_URL}/${id}`, { status });
  return response.data;
};

export const addEvento = async (eventoData) => {
  const response = await axios.post(`${API_URL}`, eventoData);
  return response.data;
};
import axios from 'axios';

const API_URL = 'http://64.227.15.111/eventos';

export const getEventos = async () => {
  const response = await axios.get(API_URL);
  return response.data;
};

// Si necesitas actualizar el estado de un evento:
export const updateEventoStatus = async (id, status) => {
  const response = await axios.patch(`${API_URL}/${id}`, { status });
  return response.data;
};

export const addEvento = async (eventoData) => {
  const response = await axios.post('http://64.227.15.111/eventos', eventoData);
  return response.data;
};
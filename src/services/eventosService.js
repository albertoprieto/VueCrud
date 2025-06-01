import axios from 'axios';

const API_URL = 'https://api.gpsubicacionapi.com/eventos';

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
  const response = await axios.post('https://api.gpsubicacionapi.com/eventos', eventoData);
  return response.data;
};

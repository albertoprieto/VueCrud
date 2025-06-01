import axios from 'axios';

const API_URL = 'https://api.gpsubicacionapi.com/reportes';

export const addReporte = async (reporteData) => {
  const response = await axios.post(API_URL, reporteData);
  return response.data;
};

export const getReportesByEvento = async (eventoId) => {
  const response = await axios.get(`${API_URL}?eventoId=${eventoId}`);
  return response.data;
};

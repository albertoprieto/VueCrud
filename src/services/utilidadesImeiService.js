import axios from 'axios';

const API_URL = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '');

export async function getUtilidadesPlataformas() {
  const response = await axios.get(`${API_URL}/api/utilidades/plataformas`);
  return response.data;
}

export async function getDispositivoPorPlataforma(imei, plataforma) {
  const response = await axios.get(`${API_URL}/api/plataformas/dispositivo/${encodeURIComponent(imei)}`, {
    params: { plataforma }
  });
  return response.data;
}

export async function getSimDetails(identifier) {
  const response = await axios.get(`${API_URL}/api/utilidades/sims/details`, {
    params: { identifiers: identifier }
  });
  return response.data;
}

export async function consultarImeiFlujo(payload) {
  const response = await axios.post(`${API_URL}/api/utilidades/consulta-imei`, payload);
  return response.data;
}

export async function getConsultasSim(page = 1, size = 10, filters = {}) {
  const response = await axios.get(`${API_URL}/api/utilidades/consultas-sim`, {
    params: {
      page,
      size,
      ...filters
    }
  });
  return response.data;
}

export async function saveConsultaSim(record) {
  const response = await axios.post(`${API_URL}/api/utilidades/consultas-sim`, record);
  return response.data;
}

export async function updateConsultaSim(id, record) {
  const response = await axios.put(`${API_URL}/api/utilidades/consultas-sim/${id}`, record);
  return response.data;
}

export async function deleteConsultaSim(id) {
  const response = await axios.delete(`${API_URL}/api/utilidades/consultas-sim/${id}`);
  return response.data;
}

export async function importarSimsSimpro() {
  const response = await axios.post(`${API_URL}/api/utilidades/sims/importar`);
  return response.data;
}

export default {
  getUtilidadesPlataformas,
  getDispositivoPorPlataforma,
  getSimDetails,
  consultarImeiFlujo,
  getConsultasSim,
  saveConsultaSim,
  updateConsultaSim,
  deleteConsultaSim,
  importarSimsSimpro
};

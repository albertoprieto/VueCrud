import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL;

export async function getCasos({ estado, categoria } = {}) {
  const params = {};
  if (estado) params.estado = estado;
  if (categoria) params.categoria = categoria;
  const res = await axios.get(`${API_URL}/whatsapp-casos`, { params });
  return res.data;
}

export async function getCasoDetalle(id) {
  const res = await axios.get(`${API_URL}/whatsapp-casos/${id}`);
  return res.data;
}

export async function actualizarEstadoCaso(id, estado) {
  const res = await axios.put(`${API_URL}/whatsapp-casos/${id}/estado`, { estado });
  return res.data;
}

export async function actualizarCategoriaCaso(id, categoria) {
  const res = await axios.put(`${API_URL}/whatsapp-casos/${id}/categoria`, { categoria });
  return res.data;
}

export async function asignarCaso(id, atendido_por) {
  const res = await axios.put(`${API_URL}/whatsapp-casos/${id}/asignar`, { atendido_por });
  return res.data;
}

export async function renombrarContacto(id, nombre_contacto) {
  const res = await axios.put(`${API_URL}/whatsapp-casos/${id}/nombre-contacto`, { nombre_contacto });
  return res.data;
}

export async function responderComoHumano(id, texto) {
  const res = await axios.post(`${API_URL}/whatsapp-casos/${id}/responder`, { texto });
  return res.data;
}

export async function reactivarIA(id) {
  const res = await axios.put(`${API_URL}/whatsapp-casos/${id}/reactivar-ia`);
  return res.data;
}

import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL;

export async function getRetiros(banco) {
  const res = await axios.get(`${API_URL}/retiros-banco`, { params: banco ? { banco } : {} });
  return res.data;
}

export async function crearRetiro({ banco, monto, motivo, archivo }) {
  const fd = new FormData();
  fd.append('banco', banco);
  fd.append('monto', monto);
  if (motivo) fd.append('motivo', motivo);
  fd.append('archivo', archivo);
  const res = await axios.post(`${API_URL}/retiros-banco`, fd, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return res.data;
}

export async function aprobarRetiro(id) {
  const res = await axios.put(`${API_URL}/retiros-banco/${id}/aprobar`);
  return res.data;
}

export async function rechazarRetiro(id) {
  const res = await axios.put(`${API_URL}/retiros-banco/${id}/rechazar`);
  return res.data;
}

export async function eliminarRetiro(id) {
  const res = await axios.delete(`${API_URL}/retiros-banco/${id}`);
  return res.data;
}

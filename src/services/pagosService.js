import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL;

// ── Notas ──
export async function getNotas() {
  const res = await axios.get(`${API_URL}/notas-pago`);
  return res.data;
}

export async function getNotaById(id) {
  const res = await axios.get(`${API_URL}/notas-pago/${id}`);
  return res.data;
}

export async function crearNota(payload) {
  const res = await axios.post(`${API_URL}/notas-pago`, payload);
  return res.data;
}

export async function actualizarStatusNota(id, status) {
  const res = await axios.put(`${API_URL}/notas-pago/${id}/status`, { status });
  return res.data;
}

export async function eliminarNota(id) {
  const res = await axios.delete(`${API_URL}/notas-pago/${id}`);
  return res.data;
}

export async function subirComprobanteNota(id, archivo) {
  const fd = new FormData();
  fd.append('archivo', archivo);
  const res = await axios.post(`${API_URL}/notas-pago/${id}/comprobante`, fd, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return res.data;
}

// ── Facturas ──
export async function getFacturas() {
  const res = await axios.get(`${API_URL}/facturas-pago`);
  return res.data;
}

export async function getFacturaById(id) {
  const res = await axios.get(`${API_URL}/facturas-pago/${id}`);
  return res.data;
}

export async function crearFactura(payload) {
  const res = await axios.post(`${API_URL}/facturas-pago`, payload);
  return res.data;
}

export async function actualizarStatusFactura(id, status) {
  const res = await axios.put(`${API_URL}/facturas-pago/${id}/status`, { status });
  return res.data;
}

export async function eliminarFactura(id) {
  const res = await axios.delete(`${API_URL}/facturas-pago/${id}`);
  return res.data;
}

export async function subirComprobanteFactura(id, archivo) {
  const fd = new FormData();
  fd.append('archivo', archivo);
  const res = await axios.post(`${API_URL}/facturas-pago/${id}/comprobante`, fd, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return res.data;
}

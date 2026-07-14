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

export async function actualizarLugarPagoNota(id, lugar_pago) {
  const res = await axios.put(`${API_URL}/notas-pago/${id}/lugar-pago`, { lugar_pago });
  return res.data;
}

export async function actualizarObservacionesNota(id, observaciones) {
  const res = await axios.put(`${API_URL}/notas-pago/${id}/observaciones`, { observaciones });
  return res.data;
}

export async function actualizarDatosPagoNota(id, payload) {
  const res = await axios.put(`${API_URL}/notas-pago/${id}/datos-pago`, payload);
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

export async function eliminarComprobanteNota(id, path) {
  const res = await axios.delete(`${API_URL}/notas-pago/${id}/comprobante`, {
    data: { path }
  });
  return res.data;
}

export async function agregarReportesNota(id, reporte_ids) {
  const res = await axios.put(`${API_URL}/notas-pago/${id}/agregar-reportes`, { reporte_ids });
  return res.data;
}

export async function quitarReportesNota(id, reporte_ids) {
  const res = await axios.put(`${API_URL}/notas-pago/${id}/quitar-reportes`, { reporte_ids });
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

export async function actualizarLugarPagoFactura(id, lugar_pago) {
  const res = await axios.put(`${API_URL}/facturas-pago/${id}/lugar-pago`, { lugar_pago });
  return res.data;
}

export async function actualizarObservacionesFactura(id, observaciones) {
  const res = await axios.put(`${API_URL}/facturas-pago/${id}/observaciones`, { observaciones });
  return res.data;
}

export async function actualizarDatosPagoFactura(id, payload) {
  const res = await axios.put(`${API_URL}/facturas-pago/${id}/datos-pago`, payload);
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

export async function eliminarComprobanteFactura(id, path) {
  const res = await axios.delete(`${API_URL}/facturas-pago/${id}/comprobante`, {
    data: { path }
  });
  return res.data;
}

export async function agregarReportesFactura(id, reporte_ids) {
  const res = await axios.put(`${API_URL}/facturas-pago/${id}/agregar-reportes`, { reporte_ids });
  return res.data;
}

export async function quitarReportesFactura(id, reporte_ids) {
  const res = await axios.put(`${API_URL}/facturas-pago/${id}/quitar-reportes`, { reporte_ids });
  return res.data;
}

export async function timbrarFactura(id, payload) {
  const res = await axios.post(`${API_URL}/facturas-pago/${id}/timbrar`, payload);
  return res.data;
}

export async function cancelarFactura(id, payload) {
  const res = await axios.post(`${API_URL}/facturas-pago/${id}/cancelar`, payload);
  return res.data;
}

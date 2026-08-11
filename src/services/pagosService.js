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

export async function actualizarCamposNota(id, campos) {
  const res = await axios.put(`${API_URL}/notas-pago/${id}/editar-campos`, campos);
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

export async function actualizarPagadoFactura(id, pagado) {
  const res = await axios.put(`${API_URL}/facturas-pago/${id}/pagado`, { pagado });
  return res.data;
}

export async function actualizarCamposFactura(id, campos) {
  const res = await axios.put(`${API_URL}/facturas-pago/${id}/editar-campos`, campos);
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

export async function sincronizarComprobantesFactura(id) {
  const res = await axios.post(`${API_URL}/facturas-pago/${id}/sincronizar-comprobantes`);
  return res.data;
}

export async function sincronizarComprobantesTodas() {
  const res = await axios.post(`${API_URL}/facturas-pago/sincronizar-comprobantes`);
  return res.data;
}

export async function limpiarComprobantesDuplicados() {
  const res = await axios.post(`${API_URL}/facturas-pago/limpiar-comprobantes-duplicados`);
  return res.data;
}

export async function marcarPagadasConComprobante() {
  const res = await axios.post(`${API_URL}/facturas-pago/marcar-pagadas-con-comprobante`);
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

export async function generarPrefacturaFactura(id, payload) {
  const res = await axios.post(`${API_URL}/facturas-pago/${id}/generar-prefactura`, payload);
  return res.data;
}

export async function getPrefacturaPdfUrl(id) {
  return `${API_URL}/facturas-pago/${id}/prefactura-pdf`;
}

export async function timbrarFactura(id, payload) {
  const res = await axios.post(`${API_URL}/facturas-pago/${id}/timbrar`, payload);
  return res.data;
}

export async function cancelarFactura(id, payload) {
  const res = await axios.post(`${API_URL}/facturas-pago/${id}/cancelar`, payload);
  return res.data;
}

export async function verificarCancelacionFactura(id) {
  const res = await axios.post(`${API_URL}/facturas-pago/${id}/verificar-cancelacion`);
  return res.data;
}

export async function enviarCfdiFactura(id, correo) {
  const res = await axios.post(`${API_URL}/facturas-pago/${id}/enviar-cfdi`, { correo });
  return res.data;
}

// ── Complementos de pago (REP) — facturas PPD ──
export async function getPagosPpd(facturaId) {
  const res = await axios.get(`${API_URL}/facturas-pago/${facturaId}/pagos-ppd`);
  return res.data;
}

export async function registrarPagoPpd(facturaId, payload) {
  const res = await axios.post(`${API_URL}/facturas-pago/${facturaId}/pagos-ppd`, payload);
  return res.data;
}

export async function cancelarPagoPpd(facturaId, pagoId, motivo, folioSustitucion) {
  const res = await axios.post(`${API_URL}/facturas-pago/${facturaId}/pagos-ppd/${pagoId}/cancelar`, { motivo, folio_sustitucion: folioSustitucion || undefined });
  return res.data;
}

export async function verificarCancelacionPagoPpd(facturaId, pagoId) {
  const res = await axios.post(`${API_URL}/facturas-pago/${facturaId}/pagos-ppd/${pagoId}/verificar-cancelacion`);
  return res.data;
}

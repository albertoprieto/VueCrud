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

export async function getConsultasSim(page = 1, size = 10, filters = {}, sort = {}) {
  const response = await axios.get(`${API_URL}/api/utilidades/consultas-sim`, {
    params: {
      page,
      size,
      ...filters,
      ...(sort.field ? { sort_field: sort.field, sort_order: sort.order } : {})
    }
  });
  return response.data;
}

export async function saveConsultaSim(record) {
  const response = await axios.post(`${API_URL}/api/utilidades/consultas-sim`, record);
  return response.data;
}

export async function getConsultaSim(id) {
  const response = await axios.get(`${API_URL}/api/utilidades/consultas-sim/${id}`);
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

// ── Acciones SIMPRO sobre un registro de consultas_sim ──
export async function verificarEstadoSim(id) {
  const response = await axios.post(`${API_URL}/api/utilidades/consultas-sim/${id}/verificar-estado`);
  return response.data;
}

export async function suspenderSim(id, { pausarFacturacion = false, hasta } = {}) {
  const response = await axios.post(`${API_URL}/api/utilidades/consultas-sim/${id}/suspender`, {
    pausar_facturacion: pausarFacturacion,
    ...(hasta ? { hasta } : {})
  });
  return response.data;
}

export async function reactivarSim(id) {
  const response = await axios.post(`${API_URL}/api/utilidades/consultas-sim/${id}/reactivar`);
  return response.data;
}

export async function cancelarSim(id, { cancellationDate } = {}) {
  const response = await axios.post(`${API_URL}/api/utilidades/consultas-sim/${id}/cancelar`, {
    ...(cancellationDate ? { cancellation_date: cancellationDate } : {})
  });
  return response.data;
}

export async function detenerCancelacionSim(id) {
  const response = await axios.post(`${API_URL}/api/utilidades/consultas-sim/${id}/detener-cancelacion`);
  return response.data;
}

export async function verificarConsumoSim(id) {
  const response = await axios.post(`${API_URL}/api/utilidades/consultas-sim/${id}/verificar-consumo`);
  return response.data;
}

export async function syncSimARepositorioSimpro(id) {
  const response = await axios.post(`${API_URL}/api/utilidades/consultas-sim/${id}/sync-simpro`);
  return response.data;
}

export async function completarDatosSims(maxRegistros) {
  const response = await axios.post(`${API_URL}/api/utilidades/consultas-sim/completar-datos`, {
    ...(maxRegistros ? { max_registros: maxRegistros } : {})
  });
  return response.data;
}

export async function refrescarSimproSims(maxRegistros) {
  const response = await axios.post(`${API_URL}/api/utilidades/consultas-sim/refrescar-simpro`, {
    ...(maxRegistros ? { max_registros: maxRegistros } : {})
  });
  return response.data;
}

// ── Administración SIMPRO ──
export async function imeiLockSim(id, activar) {
  const r = await axios.post(`${API_URL}/api/utilidades/consultas-sim/${id}/imei-lock`, { activar });
  return r.data;
}

export async function refrescarRedSim(id) {
  const r = await axios.post(`${API_URL}/api/utilidades/consultas-sim/${id}/refrescar-red`);
  return r.data;
}

export async function cambiarSolucionSim(id, customerSolution) {
  const r = await axios.post(`${API_URL}/api/utilidades/consultas-sim/${id}/cambiar-solucion`, { customer_solution: customerSolution });
  return r.data;
}

export async function cotizarCancelacionSim(id, cancellationDate) {
  const r = await axios.post(`${API_URL}/api/utilidades/consultas-sim/${id}/cotizar-cancelacion`, {
    ...(cancellationDate ? { cancellation_date: cancellationDate } : {})
  });
  return r.data;
}

export async function historialConsumoSim(id, meses = 3) {
  const r = await axios.get(`${API_URL}/api/utilidades/consultas-sim/${id}/historial-consumo`, { params: { meses } });
  return r.data;
}

export async function swapIccidSim(id, newIccid) {
  const r = await axios.post(`${API_URL}/api/utilidades/consultas-sim/${id}/swap-iccid`, { new_iccid: newIccid });
  return r.data;
}

export async function reasignarSim(id, { nuevoImei, nuevoUsuario, nuevoCliente }) {
  const r = await axios.post(`${API_URL}/api/utilidades/consultas-sim/${id}/reasignar`, {
    nuevo_imei: nuevoImei,
    ...(nuevoUsuario ? { nuevo_usuario: nuevoUsuario } : {}),
    ...(nuevoCliente ? { nuevo_cliente: nuevoCliente } : {})
  });
  return r.data;
}

export async function getCustomerSolutions(billingAccount) {
  const r = await axios.get(`${API_URL}/api/utilidades/simpro/customer-solutions`, {
    params: billingAccount ? { billing_account: billingAccount } : {}
  });
  return r.data;
}

export async function getBillingAccounts() {
  const r = await axios.get(`${API_URL}/api/utilidades/simpro/billing-accounts`);
  return r.data;
}

export async function activarSimsSimpro({ iccids, customerSolution, billingAccountNumber }) {
  const r = await axios.post(`${API_URL}/api/utilidades/simpro/activar-sims`, {
    iccids,
    customer_solution: customerSolution,
    ...(billingAccountNumber ? { billing_account_number: billingAccountNumber } : {})
  });
  return r.data;
}

export async function getAlertasConsumoSimpro() {
  const r = await axios.get(`${API_URL}/api/utilidades/simpro/alertas-consumo`);
  return r.data;
}

export async function getFacturasSimpro(billingAccount) {
  const r = await axios.get(`${API_URL}/api/utilidades/simpro/facturas`, {
    params: billingAccount ? { billing_account: billingAccount } : {}
  });
  return r.data;
}

export default {
  getUtilidadesPlataformas,
  getDispositivoPorPlataforma,
  getSimDetails,
  consultarImeiFlujo,
  getConsultasSim,
  getConsultaSim,
  saveConsultaSim,
  updateConsultaSim,
  deleteConsultaSim,
  importarSimsSimpro,
  verificarEstadoSim,
  suspenderSim,
  reactivarSim,
  cancelarSim,
  detenerCancelacionSim,
  verificarConsumoSim,
  syncSimARepositorioSimpro,
  completarDatosSims,
  refrescarSimproSims,
  imeiLockSim,
  refrescarRedSim,
  cambiarSolucionSim,
  cotizarCancelacionSim,
  historialConsumoSim,
  swapIccidSim,
  reasignarSim,
  getCustomerSolutions,
  getBillingAccounts,
  activarSimsSimpro,
  getAlertasConsumoSimpro,
  getFacturasSimpro
};

import axios from 'axios';

// Ingresos bancarios "comprobante primero": se suben desde Bancos sin nota
// aún, y se ligan después desde el detalle de la nota (ver DetalleBanco.vue
// y DetallePago.vue). Backend: bloque "Ingresos bancarios" en main.py.
const API_URL = import.meta.env.VITE_API_URL;

export async function getIngresosBanco() {
  const res = await axios.get(`${API_URL}/ingresos-banco`);
  return res.data;
}

export async function crearIngresoBanco({
  banco, monto, imeis, fecha_transaccion, usuario,
  cuenta_origen, referencia_comprobante, clave_rastreo, comprobante,
}) {
  const fd = new FormData();
  fd.append('banco', banco);
  fd.append('monto', monto);
  fd.append('imeis', imeis);
  fd.append('fecha_transaccion', fecha_transaccion);
  if (usuario) fd.append('usuario', usuario);
  if (cuenta_origen) fd.append('cuenta_origen', cuenta_origen);
  if (referencia_comprobante) fd.append('referencia_comprobante', referencia_comprobante);
  if (clave_rastreo) fd.append('clave_rastreo', clave_rastreo);
  fd.append('comprobante', comprobante);
  const res = await axios.post(`${API_URL}/ingresos-banco`, fd, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return res.data;
}

export async function editarIngresoBanco(id, campos) {
  const res = await axios.put(`${API_URL}/ingresos-banco/${id}`, campos);
  return res.data;
}

export async function eliminarIngresoBanco(id, forzar = false) {
  const res = await axios.delete(`${API_URL}/ingresos-banco/${id}`, { params: forzar ? { forzar: true } : {} });
  return res.data;
}

// Liga (total o parcial) un ingreso a una nota. Si el monto no cubre exacto
// el saldo pendiente de la nota (tolerancia $1 MXN), el backend responde 400
// pidiendo `justificacion` — reintentar mandándola resuelve la conciliación.
export async function asignarIngresoANota(ingresoId, { nota_id, monto_aplicado, justificacion, marcar_pagada }) {
  const res = await axios.post(`${API_URL}/ingresos-banco/${ingresoId}/asignar-nota`, {
    nota_id, monto_aplicado, justificacion, marcar_pagada,
  });
  return res.data;
}

export async function desligarIngresoNota(linkId) {
  const res = await axios.delete(`${API_URL}/ingreso-banco-notas/${linkId}`);
  return res.data;
}

export async function getIngresosLigadosANota(notaId) {
  const res = await axios.get(`${API_URL}/notas-pago/${notaId}/ingresos-banco`);
  return res.data;
}

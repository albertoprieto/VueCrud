import { getNotas, getFacturas, getPagosNotaTodos } from '@/services/pagosService';
import { getRetiros, getSaldosIniciales } from '@/services/bancosService';
import { getMovimientosDinero } from '@/services/dineroService';
import { getIngresosBanco } from '@/services/ingresosBancoService';

export const LUGARES_VALIDOS = [
  'ASP Vianey', 'ASP Renovaciones', 'Comercializadora', 'BBVA PAU',
  'Mercadopago Victor', 'Mercadopago Eliseo', 'Efectivo oficina', 'Efectivo tecnico',
];

const API_URL = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '');

export function urlComprobante(path) {
  if (!path) return '';
  const p = path.startsWith('/') ? path : `/${path}`;
  return `${API_URL}${p}`;
}

// Tri-estado de validación (pendiente/aprobado/rechazado) — para Retiro viene
// directo del campo `estatus`; para el resto se guarda como código 0/1/2 en
// la columna `validado` (0=pendiente, 1=aprobado, 2=rechazado).
const ESTADO_POR_CODIGO_VALIDACION = ['pendiente', 'aprobado', 'rechazado'];
export function estadoValidacion(codigo) {
  return ESTADO_POR_CODIGO_VALIDACION[Number(codigo) || 0] || 'pendiente';
}

export function parseComprobantes(raw) {
  if (Array.isArray(raw)) return raw;
  if (typeof raw === 'string') {
    try { return JSON.parse(raw) || []; } catch { return []; }
  }
  return [];
}

// Trae las fuentes que alimentan el estado de cuenta de un banco: notas,
// facturas, movimientos manuales, retiros, pagos adicionales de nota,
// ingresos bancarios "comprobante primero" y el saldo inicial (con el que
// arrancó el banco al pasar a producción).
export async function fetchBancosRaw() {
  const [notas, facturas, movimientos, retiros, pagosNota, ingresosBanco, saldosIniciales] = await Promise.all([
    getNotas(), getFacturas(), getMovimientosDinero(), getRetiros(), getPagosNotaTodos(), getIngresosBanco(), getSaldosIniciales(),
  ]);
  const saldosIncialesPorBanco = {};
  for (const s of saldosIniciales) saldosIncialesPorBanco[s.banco] = s;
  return { notas, facturas, movimientos, retiros, pagosNota, ingresosBanco, saldosIncialesPorBanco };
}

// Unifica las 6 fuentes en una sola lista de filas, cada una con su campo
// "banco" — mismo shape que usaba la tabla combinada de Bancos.vue.
export function buildFilas({ notas, facturas, movimientos, retiros, pagosNota, ingresosBanco }) {
  const out = [];
  for (const n of notas || []) {
    out.push({
      key: `nota-${n.id}`, id: n.id, tipo: 'Nota',
      fecha: n.fecha, banco: n.lugar_pago || null,
      nombre: n.cliente || '', usuario: n.usuario || '',
      imeis: (n.imeis || []).join(', '),
      monto: Number(n.total) || 0,
      comprobantes: parseComprobantes(n.comprobantes).map(urlComprobante),
      estatus: n.status,
      validado: !!n.validado,
      estatusValidacion: estadoValidacion(n.validado),
      orden_manual: n.orden_manual,
      raw: n,
    });
  }
  for (const f of facturas || []) {
    const comprobantes = parseComprobantes(f.comprobantes).map(urlComprobante);
    if (f.cfdi_pdf_path) comprobantes.push(urlComprobante(f.cfdi_pdf_path));
    out.push({
      key: `factura-${f.id}`, id: f.id, tipo: 'Factura',
      fecha: f.fecha, banco: f.lugar_pago || null,
      nombre: f.cliente || '', usuario: f.usuario || '',
      imeis: (f.imeis || []).join(', '),
      monto: Number(f.total) || 0,
      comprobantes,
      estatus: f.status,
      validado: !!f.validado,
      estatusValidacion: estadoValidacion(f.validado),
      orden_manual: f.orden_manual,
      raw: f,
    });
  }
  for (const m of movimientos || []) {
    out.push({
      key: `mov-${m.id}`, id: m.id, tipo: m.tipo === 'Egreso' ? 'Egreso' : 'Ingreso',
      fecha: m.fecha, banco: m.banco || null,
      nombre: m.concepto || '', usuario: '',
      imeis: '',
      monto: Number(m.monto) || 0,
      comprobantes: m.comprobante_url ? [m.comprobante_url] : [],
      estatus: '',
      validado: !!m.validado,
      estatusValidacion: estadoValidacion(m.validado),
      orden_manual: m.orden_manual,
      raw: m,
    });
  }
  for (const r of retiros || []) {
    out.push({
      key: `retiro-${r.id}`, id: r.id, tipo: 'Retiro',
      fecha: r.creado_fecha, banco: r.banco || null,
      nombre: r.motivo || 'Retiro de banco', usuario: '',
      imeis: '',
      monto: -(Number(r.monto) || 0),
      comprobantes: r.comprobante_url ? [r.comprobante_url] : [],
      estatus: r.estatus,
      validado: !!r.validado,
      estatusValidacion: r.estatus || 'pendiente',
      orden_manual: r.orden_manual,
      raw: r,
    });
  }
  for (const p of pagosNota || []) {
    out.push({
      key: `pagonota-${p.id}`, id: p.id, tipo: 'Pago nota',
      fecha: p.creado_fecha, banco: p.banco || null,
      nombre: p.nota_cliente || '', usuario: p.nota_usuario || '',
      imeis: (p.nota_imeis || []).join(', '),
      monto: Number(p.monto) || 0,
      comprobantes: p.comprobante_url ? [p.comprobante_url] : [],
      estatus: '',
      validado: !!p.validado,
      estatusValidacion: estadoValidacion(p.validado),
      orden_manual: p.orden_manual,
      raw: p,
    });
  }
  // Ingreso bancario "comprobante primero" — puede estar sin asignar, ligado
  // parcialmente (varios IMEIs, una nota cubierta y otras pendientes) o
  // asignado por completo. `estatus` refleja eso; `raw.tiene_justificacion`
  // dice si alguna liga se conciliÓ con diferencia (ver DetalleBanco.vue,
  // que pinta el ⚠️ cuando esto es true).
  for (const g of ingresosBanco || []) {
    const notasLigadas = [...new Set((g.links || []).map(l => l.nota_cliente).filter(Boolean))];
    out.push({
      key: `ingreso-${g.id}`, id: g.id, tipo: 'Ingreso banco',
      fecha: g.fecha_transaccion, banco: g.banco || null,
      nombre: notasLigadas.length ? `Ligado: ${notasLigadas.join(', ')}` : 'Sin asignar',
      usuario: g.usuario || '',
      imeis: (g.imeis || []).join(', '),
      monto: Number(g.monto) || 0,
      comprobantes: g.comprobante_url ? [g.comprobante_url] : [],
      estatus: g.estado_asignacion,
      validado: !!g.validado,
      estatusValidacion: estadoValidacion(g.validado),
      orden_manual: g.orden_manual,
      raw: g,
    });
  }
  return out;
}

// Saldo de un banco: saldo inicial + ingresos de notas/facturas/movimientos
// no cancelados, menos retiros ya aprobados. Los retiros pendientes se
// reportan aparte ("en revisión") sin restarlos todavía del saldo.
//
// "Cerrar mes" fija el saldo actual como saldo_inicial y guarda la fecha en
// actualizado_fecha (mismo mecanismo que editar el saldo inicial a mano) —
// esa fecha actúa como corte: los movimientos anteriores ya quedaron
// "horneados" dentro del nuevo saldo_inicial y no se vuelven a sumar.
// Los retiros pendientes SÍ se siguen mostrando aunque sean de antes del
// corte — un retiro sin resolver sigue necesitando acción sin importar el mes.
export function calcularSaldoBanco(filas, banco, saldosIncialesPorBanco = {}) {
  const delBanco = filas.filter(f => f.banco === banco);
  const info = saldosIncialesPorBanco[banco];
  const saldoInicial = Number(info?.saldo_inicial) || 0;
  const corte = info?.actualizado_fecha ? new Date(info.actualizado_fecha) : null;

  let saldo = saldoInicial;
  let pendiente = 0;
  let pendientesCount = 0;
  let ultimaFecha = null;
  for (const f of delBanco) {
    if (f.tipo === 'Nota' && f.raw.status === 'cancelado') continue;
    if (f.tipo === 'Factura' && f.raw.status === 'Cancelado') continue;
    if (f.tipo === 'Retiro') {
      if (f.estatus === 'pendiente') {
        pendiente += -f.monto;
        pendientesCount++;
      } else if (f.estatus === 'aprobado' && !(corte && f.fecha && new Date(f.fecha) <= corte)) {
        saldo += f.monto;
        if (f.fecha && (!ultimaFecha || new Date(f.fecha) > new Date(ultimaFecha))) ultimaFecha = f.fecha;
      }
      // rechazado: no cuenta para nada
      continue;
    }
    if (corte && f.fecha && new Date(f.fecha) <= corte) continue;
    saldo += f.monto;
    if (f.fecha && (!ultimaFecha || new Date(f.fecha) > new Date(ultimaFecha))) ultimaFecha = f.fecha;
  }
  return { saldo, saldoInicial, corte, pendiente, pendientesCount, ultimaFecha, totalMovimientos: delBanco.length };
}

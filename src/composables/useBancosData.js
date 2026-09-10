import { getNotas, getFacturas, getPagosNotaTodos } from '@/services/pagosService';
import { getRetiros, getSaldosIniciales } from '@/services/bancosService';
import { getMovimientosDinero } from '@/services/dineroService';
import { getIngresosBanco } from '@/services/ingresosBancoService';

export const LUGARES_VALIDOS = [
  'ASP Vianey', 'ASP Renovaciones', 'Comercializadora', 'BBVA PAU',
  'Mercadopago Victor', 'Mercadopago Eliseo', 'Efectivo oficina', 'Efectivo tecnico',
];

// El 1% de comisión por recibir dinero solo lo cobran los bancos ASP
// (ASP Vianey, ASP Renovaciones). El resto entra a valor pleno.
export const cobraComisionBanco = (banco) => String(banco || '').startsWith('ASP');
export const COMISION_ENTRADA = 0.01;

// Tipos de fila que son "entrada de dinero" y por tanto sujetos al 1%. El
// resto (Egreso, Retiro) mueve a valor pleno.
const TIPOS_ENTRADA = new Set(['Nota', 'Factura', 'Ingreso', 'Pago nota', 'Ingreso banco']);

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

// Unifica las fuentes en una sola lista de filas, cada una con su campo
// "banco" — mismo shape que usaba la tabla combinada de Bancos.vue.
export function buildFilas({ notas, facturas, movimientos, retiros, pagosNota, ingresosBanco }) {
  const out = [];

  // Una nota/factura cuyo pago se registró de forma granular (uno o varios
  // `pagos_nota`, o ligada a `ingresos_banco`) ya está representada por esas
  // filas — cada una con su propio banco. Emitir además la nota/factura
  // completa en su `lugar_pago` duplicaría el dinero. Las notas legacy
  // (pagadas sin ningún registro granular) sí se emiten como fila `Nota`.
  const notasConPagoGranular = new Set();
  const facturasConIngreso = new Set();
  for (const p of pagosNota || []) {
    if (p.nota_id != null) notasConPagoGranular.add(p.nota_id);
  }
  for (const g of ingresosBanco || []) {
    for (const l of (g.links || [])) {
      if (l.nota_id != null) notasConPagoGranular.add(l.nota_id);
      if (l.factura_id != null) facturasConIngreso.add(l.factura_id);
    }
  }

  for (const n of notas || []) {
    if (notasConPagoGranular.has(n.id)) continue;
    // Sin pagar todavía → no toca ningún banco. Cancelada sí se emite: la
    // regla del 1% necesita saber si fue aprobada y luego cancelada.
    if (n.status !== 'pagado' && n.status !== 'cancelado') continue;
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
    if (facturasConIngreso.has(f.id)) continue;  // representada por su fila `Ingreso banco`
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
    const esEgreso = m.tipo === 'Egreso';
    out.push({
      key: `mov-${m.id}`, id: m.id, tipo: esEgreso ? 'Egreso' : 'Ingreso',
      fecha: m.fecha, banco: m.banco || null,
      nombre: m.concepto || '', usuario: m.usuario || '',
      imeis: '',
      // Egreso resta: se guarda con signo negativo (igual que Retiro).
      monto: (Number(m.monto) || 0) * (esEgreso ? -1 : 1),
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
      nombre: r.motivo || 'Retiro de banco', usuario: r.usuario || '',
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
      // `fecha` es la que manda para mes/saldo/orden: la fecha real de la
      // transacción si se capturó, si no la de whatsapp. `fecha_whatsapp` y
      // `fecha_real` quedan aparte para sus columnas.
      fecha: g.fecha_transaccion_real || g.fecha_transaccion,
      fecha_whatsapp: g.fecha_transaccion,
      fecha_real: g.fecha_transaccion_real || null,
      banco: g.banco || null,
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

// Saldo de un banco:
// Mes de una fecha como 'YYYY-MM'. Corta el string directo cuando puede —
// new Date('2026-09-01') es UTC y en México (UTC-6) getMonth() la corre al
// mes anterior.
export function mesKey(fecha) {
  if (!fecha) return null;
  const m = String(fecha).match(/^(\d{4})-(\d{2})/);
  if (m) return `${m[1]}-${m[2]}`;
  const d = new Date(fecha);
  if (isNaN(d)) return null;
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`;
}

// Saldo de un banco. Sin `mes` → acumulado de toda la historia. Con `mes`
// ('YYYY-MM') → vista mensual: el saldo inicial del mes es el saldo con el
// que se cerró el mes anterior (base + arrastre de meses previos), y las
// entradas/egresos/comisión/sin-validar son solo de ese mes. Así el saldo
// final de un mes = saldo inicial del siguiente, sin botón ni corte guardado.
//
//   saldo = saldo_inicial_del_mes
//         + Σ entradas netas    (aprobadas del mes)   [importe − 1% si el banco cobra comisión]
//         − Σ egresos           (aprobados del mes)
//         − Σ retiros           (aprobados del mes)
//
// Solo cuentan movimientos con validación `aprobado` (Retiro: `estatus`).
// Pendiente/rechazado no suman — se reportan en `sinValidar`. Los retiros
// pendientes se muestran ("en revisión") sin restarlos aún.
export function calcularSaldoBanco(filas, banco, saldosIncialesPorBanco = {}, mes = null) {
  const delBanco = filas.filter(f => f.banco === banco);
  const saldoInicialBase = Number(saldosIncialesPorBanco[banco]?.saldo_inicial) || 0;
  const cobraComision = cobraComisionBanco(banco);

  const esCancelado = (f) =>
    (f.tipo === 'Nota' && f.raw?.status === 'cancelado') ||
    (f.tipo === 'Factura' && f.raw?.status === 'Cancelado');

  // Efecto neto de un movimiento validado sobre el saldo (con signo, ya con
  // el 1% descontado). Cancelado aprobado: solo la pérdida de comisión.
  const efectoValidado = (f) => {
    if (f.tipo === 'Retiro') return f.estatus === 'aprobado' ? f.monto : 0; // f.monto negativo
    const esEntrada = TIPOS_ENTRADA.has(f.tipo);
    const com = (esEntrada && cobraComision) ? Math.abs(f.monto) * COMISION_ENTRADA : 0;
    if (esCancelado(f)) return f.estatusValidacion === 'aprobado' ? -com : 0;
    if (f.estatusValidacion !== 'aprobado') return 0;
    if (esEntrada) return Math.abs(f.monto) - com;
    if (f.tipo === 'Egreso') return -Math.abs(f.monto);
    return 0;
  };

  // Arrastre: efecto de todo lo validado en meses ANTERIORES al pedido.
  let arrastre = 0;
  if (mes) {
    for (const f of delBanco) {
      const k = mesKey(f.fecha);
      if (k && k < mes) arrastre += efectoValidado(f);
    }
  }
  const saldoInicial = saldoInicialBase + arrastre;

  let entradasBrutas = 0;
  let comision = 0;
  let egresos = 0;
  let retiros = 0;
  let pendiente = 0;        // magnitud de retiros pendientes de aprobar
  let pendientesCount = 0;
  let sinValidar = 0;       // magnitud de movimientos sin aprobar (no suman al saldo)
  let sinValidarCount = 0;
  let ultimaFecha = null;

  const enElMes = (f) => !mes || mesKey(f.fecha) === mes || !f.fecha;
  const marcarFecha = (f) => {
    if (f.fecha && (!ultimaFecha || new Date(f.fecha) > new Date(ultimaFecha))) ultimaFecha = f.fecha;
  };

  for (const f of delBanco) {
    if (!enElMes(f)) continue;

    // ── Retiros: su validación vive en `estatus`, no en `validado` ──
    if (f.tipo === 'Retiro') {
      if (f.estatus === 'pendiente') {
        pendiente += -f.monto;          // f.monto es negativo
        pendientesCount++;
      } else if (f.estatus === 'aprobado') {
        retiros += -f.monto;
        marcarFecha(f);
      }
      continue;
    }

    const esEntrada = TIPOS_ENTRADA.has(f.tipo);
    const comisionFila = (esEntrada && cobraComision) ? Math.abs(f.monto) * COMISION_ENTRADA : 0;
    const fueAprobada = f.estatusValidacion === 'aprobado';

    if (esCancelado(f)) {
      if (comisionFila && fueAprobada) comision += comisionFila;
      continue;
    }

    if (!fueAprobada) {
      sinValidar += Math.abs(f.monto);
      sinValidarCount++;
      continue;
    }

    if (esEntrada) {
      entradasBrutas += Math.abs(f.monto);
      comision += comisionFila;
    } else if (f.tipo === 'Egreso') {
      egresos += Math.abs(f.monto);
    }
    marcarFecha(f);
  }

  const entradasNetas = entradasBrutas - comision;
  const saldo = saldoInicial + entradasNetas - egresos - retiros;

  return {
    saldo, saldoInicial, saldoInicialBase, arrastre,
    entradasBrutas, comision, entradasNetas, egresos, retiros,
    pendiente, pendientesCount,
    sinValidar, sinValidarCount,
    ultimaFecha,
    totalMovimientos: mes ? delBanco.filter(enElMes).length : delBanco.length,
  };
}

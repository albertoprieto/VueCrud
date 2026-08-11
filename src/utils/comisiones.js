// Lógica compartida entre Comisiones.vue y DetalleComision.vue.
//
// Modelo: un reporte de servicio queda "cerrado" para la empresa cuando la
// nota de pago (renovaciones/instalaciones) o la factura (Comercializadora)
// que lo agrupa tiene un comprobante subido. Los vendedores son los
// responsables de subir esos comprobantes, así que lo que hay que poder ver
// rápido es: ¿ya subió el comprobante o no? — no el status interno de la nota.
//
// - Técnico: su comisión exacta vive en reporte.monto_tecnico.
// - Vendedor/Responsable: no hay % de comisión en el modelo — lo relevante de
//   ellos es el $ vendido y cuántos comprobantes les falta subir.

export const ESTADOS = {
  SIN_NOTA: 'sin_nota',
  SIN_COMPROBANTE: 'sin_comprobante',
  CON_COMPROBANTE: 'con_comprobante',
  CANCELADO: 'cancelado',
  PERMISO_PENDIENTE: 'permiso_pendiente',
};

const LABELS_ESTADO = {
  [ESTADOS.SIN_NOTA]: 'Sin nota/factura',
  [ESTADOS.SIN_COMPROBANTE]: 'Sin comprobante',
  [ESTADOS.CON_COMPROBANTE]: 'Con comprobante',
  [ESTADOS.CANCELADO]: 'Cancelado',
  [ESTADOS.PERMISO_PENDIENTE]: 'Permiso (pendiente excusado)',
};

// ── Permiso de pendiente: excusa temporal (Técnico/Cliente) para que un
// reporte no cuente como pendiente real hasta su fecha_compromiso — ver
// PUT /reportes-servicio/{id}/permiso-pendiente en main.py. Solo se puede
// solicitar hasta el día 25 de cada mes; al llegar la fecha_compromiso el
// reporte vuelve solo (sin cron) a contar como pendiente, marcado como vencido.
function hoyLocal() {
  const d = new Date();
  d.setHours(0, 0, 0, 0);
  return d;
}

// Día 25 del mes en curso — tope tanto para pedir el permiso como para la
// fecha_compromiso elegida.
export function limitePermisoPendiente() {
  const d = hoyLocal();
  return new Date(d.getFullYear(), d.getMonth(), 25);
}

// false en los últimos días del mes (26+) — ahí ya no se aceptan permisos
// nuevos, solo se resuelven los pendientes reales para cerrar el mes.
export function ventanaPermisoPendienteAbierta() {
  return hoyLocal().getDate() <= 25;
}

function permisoVigente(reporte) {
  if (!reporte?.permiso_pendiente_fecha) return false;
  const fc = new Date(reporte.permiso_pendiente_fecha);
  if (isNaN(fc)) return false;
  fc.setHours(0, 0, 0, 0);
  return fc >= hoyLocal();
}

// true si el reporte tuvo un permiso marcado pero ya venció (informativo,
// el reporte ya volvió a contar como pendiente normal).
export function permisoVencido(reporte) {
  return !!(reporte?.permiso_pendiente_tipo && reporte?.permiso_pendiente_fecha && !permisoVigente(reporte));
}

export function labelEstado(estado) {
  return LABELS_ESTADO[estado] || estado;
}

function parseComprobantes(raw) {
  if (!raw) return [];
  if (Array.isArray(raw)) return raw;
  try {
    const arr = JSON.parse(raw);
    return Array.isArray(arr) ? arr : [];
  } catch {
    return [];
  }
}

// Mapa reporte_id -> { tipo, id, status, lugarPago, comprobantes, estado }
// El listado (GET /notas-pago, /facturas-pago) ya trae "comprobantes" y
// "lugar_pago" — no hace falta pedir el detalle de cada nota/factura.
export function indexarNotasFacturas(notas, facturas) {
  const indice = new Map();

  for (const nota of notas || []) {
    const comprobantes = parseComprobantes(nota.comprobantes);
    const estado = nota.status === 'cancelado'
      ? ESTADOS.CANCELADO
      : (comprobantes.length ? ESTADOS.CON_COMPROBANTE : ESTADOS.SIN_COMPROBANTE);
    for (const rid of (nota.reporte_ids || [])) {
      indice.set(rid, { tipo: 'nota', id: nota.id, status: nota.status, lugarPago: nota.lugar_pago || null, comprobantes, estado });
    }
  }

  for (const factura of facturas || []) {
    const comprobantes = parseComprobantes(factura.comprobantes);
    const estado = factura.status === 'Cancelado'
      ? ESTADOS.CANCELADO
      : (comprobantes.length ? ESTADOS.CON_COMPROBANTE : ESTADOS.SIN_COMPROBANTE);
    for (const rid of (factura.reporte_ids || [])) {
      if (!indice.has(rid)) {
        indice.set(rid, { tipo: 'factura', id: factura.id, status: factura.status, lugarPago: factura.lugar_pago || null, comprobantes, estado });
      }
    }
  }

  return indice;
}

export function estadoDeReporte(reporte, indice) {
  const match = indice.get(reporte.id);
  const base = !match
    ? { estado: ESTADOS.SIN_NOTA, referencia: null }
    : { estado: match.estado, referencia: match };
  // Un reporte con comprobante o cancelado no necesita excusa — el permiso
  // solo aplica a lo que de otro modo contaría como pendiente real.
  if (base.estado !== ESTADOS.CON_COMPROBANTE && base.estado !== ESTADOS.CANCELADO && permisoVigente(reporte)) {
    return { ...base, estado: ESTADOS.PERMISO_PENDIENTE };
  }
  return base;
}

// Las renovaciones se procesan en bloque, sin técnico/vendedor real asignado
// (por eso llevan los placeholders "Ventas Mostrador"/"Marye" de abajo) — no
// tiene sentido rastrear comprobantes de renovación en esta pantalla, así
// que se excluyen por completo, sin importar qué nombre traigan.
export function esRenovacion(reporte) {
  return /renovaci[oó]n|migraci[oó]n/i.test(reporte?.tipo_servicio || '');
}

// Placeholders que el bot mete en nombre_instalador/vendedor para
// renovaciones sin técnico o responsable real asignado (ver
// buildPayloadMulti/buildPayloadSingle en el bot) — no son personas, no
// deben aparecer en las listas de técnicos/vendedores.
const NO_ES_PERSONA = {
  nombre_instalador: new Set(['ventas mostrador']),
  vendedor: new Set(['marye']),
};

// Mismo vendedor/técnico capturado con variantes distintas del nombre (ej.
// "Victor" vs "Victor Ortiz") — se unifican bajo el nombre canónico (la
// clave). Agregar aquí nuevos casos conforme aparezcan.
const ALIAS_PERSONA = {
  vendedor: {
    'Victor': ['victor ortiz', 'victor'],
    'Carlos': ['carlos lopez', 'carlosl', 'Carlos Lopez Estavillo'],
    'Eliseo': ['eliseo', 'eliseo 2'],
    'Ricardo': ['Ricardoa', 'Ricardo Arteaga Gomez'],
    'Braulio': ['Braulio Ávila (CDMX)', 'Braulior', 'BRAULIO'],
    'Paulina Rivas': ['paulina']
  },
  nombre_instalador: {
    'Carlos': ['carlos lopez', 'carlosl'],
    'Eliseo': ['eliseo', 'eliseo 2'],
  },
};

function resolverNombre(campo, nombreRaw) {
  const nombre = (nombreRaw || '').trim();
  if (!nombre) return '';
  const norm = nombre.toLowerCase();
  const alias = ALIAS_PERSONA[campo];
  if (alias) {
    for (const canonico of Object.keys(alias)) {
      // Comparación insensible a mayúsculas — no importa cómo se haya
      // escrito la variante en la lista de arriba.
      if (alias[canonico].some(variante => variante.trim().toLowerCase() === norm)) return canonico;
    }
  }
  return nombre;
}

// campo: 'nombre_instalador' (técnico) | 'vendedor' (responsable)
export function agruparPorPersona(reportes, indice, campo) {
  const grupos = new Map();
  const excluidos = NO_ES_PERSONA[campo];

  for (const reporte of reportes || []) {
    if (esRenovacion(reporte)) continue;
    const nombre = resolverNombre(campo, reporte[campo]);
    if (!nombre || excluidos?.has(nombre.toLowerCase())) continue;

    if (!grupos.has(nombre)) {
      grupos.set(nombre, {
        nombre,
        totalReportes: 0,
        totalVendido: 0,
        totalConComprobante: 0,
        totalSinComprobante: 0,
        totalSinNota: 0,
        reportesConComprobante: 0,
        reportesSinComprobante: 0,
        reportesSinNota: 0,
        reportesConPermiso: 0,
        totalConPermiso: 0,
        comisionConComprobante: 0,
        comisionSinComprobante: 0,
      });
    }

    const g = grupos.get(nombre);
    const total = Number(reporte.total) || 0;
    const montoTecnico = Number(reporte.monto_tecnico) || 0;
    const { estado } = estadoDeReporte(reporte, indice);

    g.totalReportes += 1;
    g.totalVendido += total;

    if (estado === ESTADOS.CON_COMPROBANTE) {
      g.totalConComprobante += total;
      g.reportesConComprobante += 1;
      g.comisionConComprobante += montoTecnico;
    } else if (estado === ESTADOS.SIN_COMPROBANTE) {
      g.totalSinComprobante += total;
      g.reportesSinComprobante += 1;
      g.comisionSinComprobante += montoTecnico;
    } else if (estado === ESTADOS.SIN_NOTA) {
      g.totalSinNota += total;
      g.reportesSinNota += 1;
      g.comisionSinComprobante += montoTecnico;
    } else if (estado === ESTADOS.PERMISO_PENDIENTE) {
      g.totalConPermiso += total;
      g.reportesConPermiso += 1;
    }
    // CANCELADO no suma a ningún total — no es venta viva.
  }

  return [...grupos.values()];
}

export function reportesDePersona(reportes, indice, campo, nombre) {
  const norm = (nombre || '').trim().toLowerCase();
  return (reportes || [])
    .filter(r => !esRenovacion(r) && resolverNombre(campo, r[campo]).toLowerCase() === norm)
    .map(r => {
      const { estado, referencia } = estadoDeReporte(r, indice);
      return { ...r, estado, referencia, permisoVencido: permisoVencido(r) };
    })
    .sort((a, b) => new Date(b.fecha) - new Date(a.fecha));
}

// Lista de meses (YYYY-MM) presentes en los reportes, más recientes primero.
export function mesesDisponibles(reportes) {
  const set = new Set();
  for (const r of reportes || []) {
    if (!r.fecha) continue;
    const d = new Date(r.fecha);
    if (isNaN(d)) continue;
    set.add(`${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`);
  }
  const MESES = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'];
  return [...set].sort().reverse().map(value => {
    const [anio, mes] = value.split('-');
    return { value, label: `${MESES[Number(mes) - 1]} ${anio}` };
  });
}

// 'YYYY-MM' del mes en curso — default del filtro de mes en todas las pantallas.
export function mesActual() {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`;
}

// mes: 'YYYY-MM' o null/undefined/'todos' para no filtrar.
export function filtrarPorMes(reportes, mes) {
  if (!mes || mes === 'todos') return reportes || [];
  return (reportes || []).filter(r => {
    if (!r.fecha) return false;
    const d = new Date(r.fecha);
    if (isNaN(d)) return false;
    const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`;
    return key === mes;
  });
}

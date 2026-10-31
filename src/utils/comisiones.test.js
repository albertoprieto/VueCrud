// node src/utils/comisiones.test.js
import assert from 'node:assert/strict';
import { ESTADOS, estadoDeReporte, indexarNotasFacturas, reportesDePersona } from './comisiones.js';

const vencido = { permiso_pendiente_tipo: 'cliente', permiso_pendiente_fecha: '2020-01-01' };
const base = { id: 1, vendedor: 'Ana', fecha: '2026-10-01', ...vencido };
const nota = (extra = {}) => ({ id: 9, status: 'pendiente de pago', reporte_ids: [1], ...extra });
const fila = (reporte, notas) =>
  reportesDePersona([reporte], indexarNotasFacturas(notas, []), 'vendedor', 'Ana')[0];

// Permiso vencido sin pago: sigue marcado.
assert.equal(fila(base, []).permisoVencido, true);
assert.equal(fila(base, [nota()]).permisoVencido, true);

// Se le asignó pago (comprobante directo o de ingreso ligado): se quita.
assert.equal(fila(base, [nota({ comprobantes: ['a.pdf'] })]).permisoVencido, false);
assert.equal(fila(base, [nota({ comprobantes_extra: ['b.pdf'] })]).permisoVencido, false);

// Pagado en el pasado: sale de pendientes, con o sin nota, y sin bandera.
const pasado = { ...base, pagado_pasado_fecha: '2026-10-30T10:00:00' };
assert.equal(estadoDeReporte(pasado, new Map()).estado, ESTADOS.PAGADO_PASADO);
assert.equal(fila(pasado, [nota()]).estado, ESTADOS.PAGADO_PASADO);
assert.equal(fila(pasado, [nota()]).permisoVencido, false);

// Si después llega comprobante, manda el comprobante.
assert.equal(fila(pasado, [nota({ comprobantes: ['a.pdf'] })]).estado, ESTADOS.CON_COMPROBANTE);

console.log('ok');

import { calcularSaldoBanco, mesKey } from './useBancosData.js';

// Helpers para armar filas con el shape que produce buildFilas().
const entrada = (banco, monto, estatusValidacion = 'aprobado', extra = {}) => ({
  banco, tipo: 'Nota', monto, fecha: '2026-06-01',
  estatus: 'pagado', estatusValidacion, raw: { status: 'pagado' }, ...extra,
});
const egreso = (banco, monto, estatusValidacion = 'aprobado') => ({
  banco, tipo: 'Egreso', monto: -Math.abs(monto), fecha: '2026-06-01',
  estatus: '', estatusValidacion, raw: {},
});
const retiro = (banco, monto, estatus = 'aprobado') => ({
  banco, tipo: 'Retiro', monto: -Math.abs(monto), fecha: '2026-06-01',
  estatus, estatusValidacion: estatus, raw: {},
});
const ini = (saldo_inicial) => ({ BBVA: { saldo_inicial } });

describe('calcularSaldoBanco', () => {
  it('sin movimientos, saldo = saldo inicial', () => {
    const r = calcularSaldoBanco([], 'BBVA', ini(1000));
    expect(r.saldo).toBe(1000);
  });

  it('entrada aprobada en banco real: suma importe − 1%', () => {
    const r = calcularSaldoBanco([entrada('BBVA', 1000)], 'BBVA', ini(0));
    expect(r.comision).toBeCloseTo(10);
    expect(r.entradasNetas).toBeCloseTo(990);
    expect(r.saldo).toBeCloseTo(990);
  });

  it('entrada aprobada en Efectivo: sin comisión', () => {
    const r = calcularSaldoBanco(
      [entrada('Efectivo oficina', 1000)], 'Efectivo oficina',
      { 'Efectivo oficina': { saldo_inicial: 0, actualizado_fecha: null } },
    );
    expect(r.comision).toBe(0);
    expect(r.saldo).toBeCloseTo(1000);
  });

  it('entrada sin validar no suma, se reporta en sinValidar', () => {
    const r = calcularSaldoBanco([entrada('BBVA', 1000, 'pendiente')], 'BBVA', ini(500));
    expect(r.saldo).toBe(500);
    expect(r.sinValidarCount).toBe(1);
    expect(r.sinValidar).toBeCloseTo(1000);
  });

  it('egreso aprobado resta a valor pleno', () => {
    const r = calcularSaldoBanco([egreso('BBVA', 300)], 'BBVA', ini(1000));
    expect(r.egresos).toBeCloseTo(300);
    expect(r.saldo).toBeCloseTo(700);
  });

  it('retiro aprobado resta; pendiente va a bucket sin restar', () => {
    const r = calcularSaldoBanco(
      [retiro('BBVA', 200, 'aprobado'), retiro('BBVA', 50, 'pendiente')],
      'BBVA', ini(1000),
    );
    expect(r.saldo).toBeCloseTo(800);
    expect(r.pendiente).toBeCloseTo(50);
    expect(r.pendientesCount).toBe(1);
  });

  it('todo movimiento validado cuenta, sin importar la fecha (no hay corte)', () => {
    const r = calcularSaldoBanco(
      [entrada('BBVA', 1000, 'aprobado', { fecha: '2020-01-01' })],
      'BBVA', ini(5000),
    );
    expect(r.saldo).toBeCloseTo(5990);
  });

  it('entrada aprobada y luego cancelada: importe fuera, 1% queda como pérdida', () => {
    const fila = entrada('BBVA', 1000, 'aprobado', {
      estatus: 'cancelado', raw: { status: 'cancelado' },
    });
    const r = calcularSaldoBanco([fila], 'BBVA', ini(2000));
    expect(r.entradasBrutas).toBe(0);
    expect(r.comision).toBeCloseTo(10);
    expect(r.saldo).toBeCloseTo(1990);
  });

  it('sinValidar acumula todas las pendientes; solo las aprobadas suman al saldo', () => {
    const filas = [
      entrada('BBVA', 1000, 'pendiente'),
      entrada('BBVA', 1000, 'pendiente'),
      entrada('BBVA', 1000, 'pendiente'),
      entrada('BBVA', 1000, 'aprobado'),
    ];
    const r = calcularSaldoBanco(filas, 'BBVA', ini(5000));
    expect(r.sinValidarCount).toBe(3);
    expect(r.sinValidar).toBeCloseTo(3000);
    expect(r.saldo).toBeCloseTo(5990);
  });

  it('mesKey no corre la fecha por timezone', () => {
    expect(mesKey('2026-09-01')).toBe('2026-09');
    expect(mesKey('2026-09-01T05:00:00Z')).toBe('2026-09');
  });

  it('vista mensual: el saldo final de un mes es el inicial del siguiente', () => {
    const filas = [
      entrada('BBVA', 1000, 'aprobado', { fecha: '2026-08-10' }),
      entrada('BBVA', 500, 'aprobado', { fecha: '2026-09-05' }),
      entrada('BBVA', 200, 'pendiente', { fecha: '2026-09-06' }),
    ];
    const ago = calcularSaldoBanco(filas, 'BBVA', ini(1000), '2026-08');
    const sep = calcularSaldoBanco(filas, 'BBVA', ini(1000), '2026-09');
    expect(ago.saldo).toBeCloseTo(1990);          // 1000 + (1000 − 1%)
    expect(sep.saldoInicial).toBeCloseTo(1990);   // hereda el cierre de agosto
    expect(sep.saldoInicialBase).toBe(1000);      // el arranque no cambia
    expect(sep.entradasNetas).toBeCloseTo(495);   // solo la entrada de septiembre
    expect(sep.saldo).toBeCloseTo(2485);
    expect(sep.sinValidarCount).toBe(1);
  });

  it('nota cancelada que nunca se aprobó: no afecta nada', () => {
    const fila = entrada('BBVA', 1000, 'pendiente', {
      estatus: 'cancelado', raw: { status: 'cancelado' },
    });
    const r = calcularSaldoBanco([fila], 'BBVA', ini(2000));
    expect(r.comision).toBe(0);
    expect(r.saldo).toBe(2000);
  });
});

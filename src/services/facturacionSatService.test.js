import { emitirFacturaPrueba } from './facturacionSatService.js';

describe('emitirFacturaPrueba', () => {
  it('debe emitir factura correctamente con datos mínimos', async () => {
    const reporte = {
      nombre_cliente: 'Juan Pérez',
      total: 1234.56
    };
    const resultado = await emitirFacturaPrueba(reporte);
    expect(resultado.exito).toBe(true);
    expect(resultado.uuid).toBeDefined();
    expect(resultado.mensaje).toMatch(/Factura emitida/);
  });

  it('debe fallar si falta el nombre del cliente', async () => {
    const reporte = {
      total: 1234.56
    };
    const resultado = await emitirFacturaPrueba(reporte);
    expect(resultado.exito).toBe(false);
    expect(resultado.mensaje).toMatch(/Faltan datos/);
  });

  it('debe fallar si falta el total', async () => {
    const reporte = {
      nombre_cliente: 'Juan Pérez'
    };
    const resultado = await emitirFacturaPrueba(reporte);
    expect(resultado.exito).toBe(false);
    expect(resultado.mensaje).toMatch(/Faltan datos/);
  });
});

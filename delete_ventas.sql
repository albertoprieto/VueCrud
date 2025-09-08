-- Elimina todo lo operativo y relativo a ventas y agenda, pero NO usuarios ni clientes

-- Borra detalle de ventas (debe ir antes que ventas)
DELETE FROM detalle_venta;

-- Borra asignaciones de técnicos a ventas
DELETE FROM venta_tecnico;

-- Borra reportes de servicio
DELETE FROM reportes_servicio;

-- Borra reportes (si usas la tabla reportes para agenda/servicio)
DELETE FROM reportes;

-- Borra ventas
DELETE FROM ventas;

UPDATE imeis SET status = 'Disponible';
SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE cotizaciones_enviadas;
TRUNCATE detalle_venta;
TRUNCATE movimientos_dinero;
TRUNCATE reportes;
TRUNCATE reportes_servicio;
TRUNCATE cotizaciones;
TRUNCATE ventas;
SET FOREIGN_KEY_CHECKS = 1;

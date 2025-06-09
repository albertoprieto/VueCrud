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

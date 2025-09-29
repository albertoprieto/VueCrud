-- ATENCIÓN: Esto eliminará TODOS los datos existentes
-- Solo ejecuta si estás seguro de querer reiniciar todo

-- 1. Eliminar reportes de servicio (dependen de asignaciones)
DELETE FROM reportes_servicio;

-- 2. Eliminar asignaciones de técnicos (dependen de ventas)
DELETE FROM venta_tecnico;

-- 3. Eliminar ventas
DELETE FROM ventas;

-- 4. Resetear contadores AUTO_INCREMENT (opcional)
ALTER TABLE ventas AUTO_INCREMENT = 1;
ALTER TABLE venta_tecnico AUTO_INCREMENT = 1;
ALTER TABLE reportes_servicio AUTO_INCREMENT = 1;
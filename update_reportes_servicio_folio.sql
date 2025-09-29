-- Actualizar folios de reportes de servicio existentes
-- para que coincidan con el folio de su orden de servicio
UPDATE reportes_servicio rs
JOIN venta_tecnico vt ON rs.asignacion_id = vt.id
JOIN ventas v ON vt.venta_id = v.id
SET rs.folio = v.folio
WHERE rs.folio IS NULL OR rs.folio = '';
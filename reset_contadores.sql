-- Opción más segura: Solo resetear los contadores sin eliminar datos
-- Los folios seguirán la secuencia correcta pero empezarán desde 00001

-- Resetear contadores AUTO_INCREMENT
ALTER TABLE ventas AUTO_INCREMENT = 1;
ALTER TABLE venta_tecnico AUTO_INCREMENT = 1;
ALTER TABLE reportes_servicio AUTO_INCREMENT = 1;

-- Para que el próximo folio sea SERVICIO-00001, también puedes:
-- (Esto forzará que el próximo folio sea 00001)
-- Nota: Esto solo afecta futuras inserciones
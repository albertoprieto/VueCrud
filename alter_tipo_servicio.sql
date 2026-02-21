-- Agrega columna tipo_de_servicio solo para renovaciones Tracksolid
ALTER TABLE renovaciones_recientes ADD COLUMN tipo_de_servicio VARCHAR(100) NULL AFTER modelo_dispositivo;
-- Si solo quieres llenarla para Tracksolid, puedes dejarla NULL para IOP.

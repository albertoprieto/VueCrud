-- Agrega columnas para manejo de comprobantes en reportes_servicio
ALTER TABLE `reportes_servicio`
  ADD COLUMN `comprobante_path` VARCHAR(255) NULL AFTER `viaticos`,
  ADD COLUMN `comprobante_estado` ENUM('pendiente','aprobado','rechazado') NULL AFTER `comprobante_path`,
  ADD COLUMN `aprobado_por` VARCHAR(100) NULL AFTER `comprobante_estado`,
  ADD COLUMN `aprobado_fecha` DATETIME NULL AFTER `aprobado_por`;

-- Opcional: índice para búsquedas por estado de comprobante
CREATE INDEX idx_rep_serv_comprobante_estado ON reportes_servicio (comprobante_estado);

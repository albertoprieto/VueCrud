-- Agrega columna folio a reportes_servicio para usar el mismo folio que la orden de servicio
ALTER TABLE `reportes_servicio`
  ADD COLUMN `folio` VARCHAR(20) NULL AFTER `id`;

-- Opcional: índice para búsquedas por folio
CREATE INDEX idx_rep_serv_folio ON reportes_servicio (folio);
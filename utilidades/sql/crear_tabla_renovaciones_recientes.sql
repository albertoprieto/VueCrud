-- =====================================================
-- Tabla: renovaciones_recientes
-- Descripción: Almacena las renovaciones de tarjeta prepago 
--              cargadas desde el archivo Excel de la plataforma GPS
-- Llaves: cuenta + numero_dispositivo (compuesta)
-- =====================================================

CREATE TABLE IF NOT EXISTS renovaciones_recientes (
    id INT AUTO_INCREMENT,
    
    -- Campos del archivo Excel
    cuenta VARCHAR(100) NOT NULL,
    numero_dispositivo VARCHAR(50) NOT NULL,
    nombre_dispositivo VARCHAR(255) DEFAULT '',
    modelo_dispositivo VARCHAR(100) DEFAULT '',
    numero_tarjeta_sim VARCHAR(100) DEFAULT '',
    hora_activacion DATETIME DEFAULT NULL,
    plataforma VARCHAR(50),  -- 'IOP' o 'Tracksolid'
    
    -- Campo específico de renovaciones
    periodo_de_renovacion VARCHAR(50) DEFAULT '',  -- Ej: "1 Año", "10 Años"
    tiempo_vencimiento_plataforma DATE DEFAULT NULL,
    hora_vencimiento_usuario DATE DEFAULT NULL,
    
    -- Campos de control
    status ENUM('pendiente', 'con_reporte', 'sin_reporte', 'es_envio', 'no_requiere', 'desconocido', 'no_encontrado') DEFAULT 'pendiente',
    reporte_servicio_id INT DEFAULT NULL,
    
    -- Campos de auditoría
    fecha_carga DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    cargado_por VARCHAR(100) DEFAULT NULL,
    
    -- Llaves
    PRIMARY KEY (id),
    UNIQUE KEY idx_cuenta_dispositivo_renovacion (cuenta, numero_dispositivo),
    INDEX idx_status (status),
    INDEX idx_hora_activacion (hora_activacion),
    INDEX idx_numero_dispositivo (numero_dispositivo),
    INDEX idx_plataforma (plataforma),
    INDEX idx_periodo_renovacion (periodo_de_renovacion),
    INDEX idx_vencimiento_plataforma (tiempo_vencimiento_plataforma),
    
    -- Foreign key opcional al reporte de servicio
    CONSTRAINT fk_renovacion_reporte 
        FOREIGN KEY (reporte_servicio_id) 
        REFERENCES reportes_servicio(id) 
        ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- =====================================================
-- Índice para búsquedas rápidas por IMEI (numero_dispositivo)
-- =====================================================
CREATE INDEX idx_renovacion_imei ON renovaciones_recientes(numero_dispositivo);

-- =====================================================
-- Trigger para actualizar status cuando se asocia un reporte
-- =====================================================
DELIMITER //
CREATE TRIGGER trg_renovacion_status_update
BEFORE UPDATE ON renovaciones_recientes
FOR EACH ROW
BEGIN
    IF NEW.reporte_servicio_id IS NOT NULL AND OLD.reporte_servicio_id IS NULL THEN
        SET NEW.status = 'con_reporte';
    ELSEIF NEW.reporte_servicio_id IS NULL AND OLD.reporte_servicio_id IS NOT NULL THEN
        SET NEW.status = 'sin_reporte';
    END IF;
END//
DELIMITER ;

-- =====================================================
-- Vista para consulta rápida con información del reporte
-- =====================================================
CREATE OR REPLACE VIEW v_renovaciones_con_reporte AS
SELECT 
    rr.*,
    rs.folio AS folio_reporte,
    rs.tipo_servicio,
    rs.nombre_instalador AS tecnico,
    rs.fecha AS fecha_reporte
FROM renovaciones_recientes rr
LEFT JOIN reportes_servicio rs ON rr.reporte_servicio_id = rs.id;

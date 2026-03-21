-- ═══════════════════════════════════════════════════════════════
-- Tabla: notas_pago
-- Status posibles: 'pendiente de pago', 'pagado', 'cancelado'
-- ═══════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS notas_pago (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    ordenes     JSON          NOT NULL COMMENT 'Array de folios de orden seleccionados',
    cliente     VARCHAR(255)  NOT NULL,
    total       DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    status      VARCHAR(50)   NOT NULL DEFAULT 'pendiente de pago',
    reporte_ids JSON          NULL     COMMENT 'Array de IDs de reportes_servicio asociados',
    fecha       DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_notas_status (status),
    INDEX idx_notas_fecha  (fecha)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ═══════════════════════════════════════════════════════════════
-- Tabla: facturas_pago
-- Status posibles: 'Timbrado', 'Pendiente timbre', 'Cancelado'
-- ═══════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS facturas_pago (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    ordenes     JSON          NOT NULL COMMENT 'Array de folios de orden seleccionados',
    cliente     VARCHAR(255)  NOT NULL,
    total       DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    status      VARCHAR(50)   NOT NULL DEFAULT 'Pendiente timbre',
    reporte_ids JSON          NULL     COMMENT 'Array de IDs de reportes_servicio asociados',
    fecha       DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_facturas_status (status),
    INDEX idx_facturas_fecha  (fecha)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

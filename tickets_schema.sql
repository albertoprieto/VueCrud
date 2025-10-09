-- DDL básico para Tickets

CREATE TABLE IF NOT EXISTS tickets (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  reporte_id INT NOT NULL,
  titulo VARCHAR(200) NOT NULL,
  descripcion TEXT,
  prioridad ENUM('baja','media','alta','crítica') DEFAULT 'media',
  tipo ENUM('soporte','garantía','posventa','otro') DEFAULT 'soporte',
  estado ENUM('nuevo','en_progreso','en_espera','resuelto','cerrado') DEFAULT 'nuevo',
  imeis JSON NULL,
  cliente_id INT NULL,
  cliente_nombre VARCHAR(255) NULL,
  created_by_user_id INT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_tickets_reporte (reporte_id),
  INDEX idx_tickets_estado (estado)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS ticket_comments (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  ticket_id INT NOT NULL,
  text TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_ticket_comments_ticket (ticket_id),
  CONSTRAINT fk_ticket_comments_ticket FOREIGN KEY (ticket_id) REFERENCES tickets(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Vista opcional: contexto desde la cadena Reporte->Venta->Cliente->Cotización + IMEIs
-- Asegúrate de tener las tablas ventas, venta_tecnico, clientes, cotizaciones, detalle_venta y reportes_servicio
CREATE OR REPLACE VIEW v_ticket_context AS
WITH
base AS (
  SELECT
    rs.id AS reporte_id, rs.folio AS folio_reporte, rs.fecha AS fecha_reporte,
    vt.id AS asignacion_id, v.id AS venta_id, v.folio AS folio_venta, v.cliente_id,
    cte.nombre AS cliente_nombre, cte.correo AS cliente_correo,
    cot.id AS cotizacion_id, cot.status AS cotizacion_status,
    cot.autorizada AS cotizacion_autorizada, cot.fecha_autorizacion
  FROM reportes_servicio rs
  JOIN venta_tecnico vt ON vt.id = rs.asignacion_id
  JOIN ventas v ON v.id = vt.venta_id
  LEFT JOIN clientes cte ON cte.id = v.cliente_id
  LEFT JOIN cotizaciones cot ON cot.venta_id = v.id
),
from_json_nested AS (
  SELECT b.reporte_id, jt.imei
  FROM base b
  JOIN reportes_servicio rs ON rs.id = b.reporte_id
  JOIN JSON_TABLE(rs.imeis_articulos, '$[*].imeis[*]' COLUMNS(imei VARCHAR(64) PATH '$')) jt
),
from_json_flat AS (
  SELECT b.reporte_id, jt2.imei
  FROM base b
  JOIN reportes_servicio rs ON rs.id = b.reporte_id
  JOIN JSON_TABLE(rs.imeis_articulos, '$[*]' COLUMNS(imei VARCHAR(64) PATH '$')) jt2
),
from_rs_col AS (
  SELECT b.reporte_id, rs.imei
  FROM base b
  JOIN reportes_servicio rs ON rs.id = b.reporte_id
  WHERE rs.imei IS NOT NULL AND rs.imei <> ''
),
from_detalle_venta AS (
  SELECT b.reporte_id, dv.imei
  FROM base b
  JOIN detalle_venta dv ON dv.venta_id = b.venta_id
  WHERE dv.imei IS NOT NULL AND dv.imei <> ''
),
all_imeis AS (
  SELECT reporte_id, TRIM(imei) AS imei FROM from_json_nested
  UNION ALL
  SELECT reporte_id, TRIM(imei) FROM from_json_flat
  UNION ALL
  SELECT reporte_id, TRIM(imei) FROM from_rs_col
  UNION ALL
  SELECT reporte_id, TRIM(imei) FROM from_detalle_venta
),
filtered AS (
  SELECT reporte_id, imei
  FROM all_imeis
  WHERE imei REGEXP '^[0-9]{10,20}$'
),
agg AS (
  SELECT reporte_id,
         GROUP_CONCAT(DISTINCT imei ORDER BY imei SEPARATOR ',') AS imeis_concat,
         JSON_ARRAYAGG(imei) AS imeis_json
  FROM filtered
  GROUP BY reporte_id
)
SELECT b.*, a.imeis_concat, a.imeis_json
FROM base b
LEFT JOIN agg a ON a.reporte_id = b.reporte_id;

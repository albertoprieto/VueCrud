-- Script para verificar que la corrección de reportes duplicados funciona correctamente

-- 1. Verificar que solo quede un reporte por asignación
SELECT asignacion_id, COUNT(*) as total_reportes 
FROM reportes_servicio 
GROUP BY asignacion_id 
ORDER BY asignacion_id;

-- 2. Verificar que el índice único esté creado
SHOW INDEX FROM reportes_servicio WHERE Key_name = 'idx_unique_asignacion';

-- 3. Ver todos los reportes actuales
SELECT id, asignacion_id, folio, fecha, tipo_servicio, total, pagado 
FROM reportes_servicio 
ORDER BY asignacion_id, id;

-- 4. Probar que no se pueden insertar duplicados (este comando debe fallar)
-- INSERT INTO reportes_servicio (asignacion_id, tipo_servicio, total) 
-- VALUES (3, 'Prueba Duplicado', 100);

-- 5. Verificar estructura de índices
SELECT 
    INDEX_NAME,
    COLUMN_NAME,
    NON_UNIQUE,
    INDEX_TYPE
FROM INFORMATION_SCHEMA.STATISTICS 
WHERE TABLE_NAME = 'reportes_servicio' 
AND TABLE_SCHEMA = DATABASE()
ORDER BY INDEX_NAME, SEQ_IN_INDEX;
# =====================================================
# Endpoints para Activaciones Recientes
# Agregar este código al main.py
# =====================================================

from typing import List, Optional
from pydantic import BaseModel
from fastapi import HTTPException, Query, Body
import mysql.connector
from datetime import datetime

# =====================================================
# MODELO: ActivacionReciente
# =====================================================
class ActivacionReciente(BaseModel):
    cuenta: str
    numero_dispositivo: str
    nombre_dispositivo: str = ""
    modelo_dispositivo: str = ""
    numero_tarjeta_sim: str = ""
    hora_activacion: Optional[str] = None

class ActivacionRecienteResponse(BaseModel):
    id: int
    cuenta: str
    numero_dispositivo: str
    nombre_dispositivo: str
    modelo_dispositivo: str
    numero_tarjeta_sim: str
    hora_activacion: Optional[str]
    status: str
    reporte_servicio_id: Optional[int]
    fecha_carga: Optional[str]
    # Campos del reporte si existe
    folio_reporte: Optional[str] = None
    tipo_servicio: Optional[str] = None
    tecnico: Optional[str] = None

class BulkActivacionesRequest(BaseModel):
    activaciones: List[ActivacionReciente]
    cargado_por: str = "sistema"

# =====================================================
# GET /activaciones-recientes
# Obtener todas las activaciones con filtros opcionales
# =====================================================
@app.get("/activaciones-recientes")
def get_activaciones_recientes(
    status: Optional[str] = Query(None, description="Filtrar por status: pendiente, con_reporte, sin_reporte"),
    dias: Optional[int] = Query(30, description="Filtrar por días de antigüedad"),
    cuenta: Optional[str] = Query(None, description="Filtrar por cuenta"),
    limit: Optional[int] = Query(500, description="Límite de registros")
):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor(dictionary=True)
    
    # Construir query con filtros
    query = """
        SELECT 
            ar.id,
            ar.cuenta,
            ar.numero_dispositivo,
            ar.nombre_dispositivo,
            ar.modelo_dispositivo,
            ar.numero_tarjeta_sim,
            ar.hora_activacion,
            ar.status,
            ar.reporte_servicio_id,
            ar.fecha_carga,
            rs.folio AS folio_reporte,
            rs.tipo_servicio,
            rs.nombre_instalador AS tecnico
        FROM activaciones_recientes ar
        LEFT JOIN reportes_servicio rs ON ar.reporte_servicio_id = rs.id
        WHERE 1=1
    """
    params = []
    
    if status:
        query += " AND ar.status = %s"
        params.append(status)
    
    if dias:
        query += " AND ar.hora_activacion >= DATE_SUB(NOW(), INTERVAL %s DAY)"
        params.append(dias)
    
    if cuenta:
        query += " AND ar.cuenta LIKE %s"
        params.append(f"%{cuenta}%")
    
    query += " ORDER BY ar.hora_activacion DESC"
    
    if limit:
        query += " LIMIT %s"
        params.append(limit)
    
    cursor.execute(query, params)
    activaciones = cursor.fetchall()
    
    # Convertir datetime a string
    for a in activaciones:
        if a.get('hora_activacion'):
            a['hora_activacion'] = a['hora_activacion'].isoformat() if hasattr(a['hora_activacion'], 'isoformat') else str(a['hora_activacion'])
        if a.get('fecha_carga'):
            a['fecha_carga'] = a['fecha_carga'].isoformat() if hasattr(a['fecha_carga'], 'isoformat') else str(a['fecha_carga'])
    
    cursor.close()
    db.close()
    
    return {
        "total": len(activaciones),
        "activaciones": activaciones
    }

# =====================================================
# POST /activaciones-recientes/bulk
# Insertar/actualizar múltiples activaciones (UPSERT)
# =====================================================
@app.post("/activaciones-recientes/bulk")
def bulk_upsert_activaciones(data: BulkActivacionesRequest):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor(dictionary=True)
    
    insertados = 0
    actualizados = 0
    errores = []
    
    for activacion in data.activaciones:
        try:
            # Parsear fecha si viene como string
            hora_activacion = None
            if activacion.hora_activacion:
                try:
                    # Intentar varios formatos
                    for fmt in ['%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S', '%d/%m/%Y %H:%M:%S', '%Y-%m-%dT%H:%M:%S.%fZ']:
                        try:
                            hora_activacion = datetime.strptime(activacion.hora_activacion.replace('Z', ''), fmt.replace('Z', ''))
                            break
                        except:
                            continue
                    if not hora_activacion:
                        hora_activacion = datetime.fromisoformat(activacion.hora_activacion.replace('Z', '+00:00').replace('+00:00', ''))
                except:
                    hora_activacion = None
            
            # UPSERT: INSERT ... ON DUPLICATE KEY UPDATE
            cursor.execute("""
                INSERT INTO activaciones_recientes (
                    cuenta, numero_dispositivo, nombre_dispositivo, 
                    modelo_dispositivo, numero_tarjeta_sim, hora_activacion,
                    cargado_por, status
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, 'pendiente')
                ON DUPLICATE KEY UPDATE
                    nombre_dispositivo = VALUES(nombre_dispositivo),
                    modelo_dispositivo = VALUES(modelo_dispositivo),
                    numero_tarjeta_sim = VALUES(numero_tarjeta_sim),
                    hora_activacion = VALUES(hora_activacion),
                    fecha_actualizacion = CURRENT_TIMESTAMP
            """, (
                activacion.cuenta,
                activacion.numero_dispositivo,
                activacion.nombre_dispositivo,
                activacion.modelo_dispositivo,
                activacion.numero_tarjeta_sim,
                hora_activacion,
                data.cargado_por
            ))
            
            if cursor.rowcount == 1:
                insertados += 1
            elif cursor.rowcount == 2:  # MySQL devuelve 2 en UPDATE
                actualizados += 1
                
        except mysql.connector.Error as e:
            errores.append({
                "dispositivo": activacion.numero_dispositivo,
                "error": str(e)
            })
    
    db.commit()
    
    # Después de insertar, actualizar status basado en reportes existentes
    try:
        cursor.execute("""
            UPDATE activaciones_recientes ar
            INNER JOIN reportes_servicio rs ON ar.numero_dispositivo = rs.imei
            SET ar.status = 'con_reporte', ar.reporte_servicio_id = rs.id
            WHERE ar.status = 'pendiente'
        """)
        
        # También verificar en imeis_articulos (JSON)
        cursor.execute("""
            UPDATE activaciones_recientes ar
            SET ar.status = 'sin_reporte'
            WHERE ar.status = 'pendiente'
            AND ar.reporte_servicio_id IS NULL
        """)
        
        db.commit()
    except Exception as e:
        print(f"Error actualizando status: {e}")
    
    cursor.close()
    db.close()
    
    return {
        "message": "Carga completada",
        "insertados": insertados,
        "actualizados": actualizados,
        "errores": errores,
        "total_procesados": len(data.activaciones)
    }

# =====================================================
# GET /activaciones-recientes/verificar-reportes
# Verificar qué activaciones tienen reporte de servicio
# =====================================================
@app.get("/activaciones-recientes/verificar-reportes")
def verificar_reportes_activaciones():
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor(dictionary=True)
    
    # Actualizar status basándose en reportes existentes
    # Buscar por IMEI en el campo imei de reportes_servicio
    cursor.execute("""
        UPDATE activaciones_recientes ar
        INNER JOIN reportes_servicio rs ON ar.numero_dispositivo = rs.imei
        SET ar.status = 'con_reporte', ar.reporte_servicio_id = rs.id
        WHERE ar.reporte_servicio_id IS NULL
    """)
    actualizados_imei = cursor.rowcount
    
    # También buscar en imeis_articulos (JSON array)
    cursor.execute("""
        SELECT ar.id, ar.numero_dispositivo, rs.id as reporte_id
        FROM activaciones_recientes ar
        CROSS JOIN reportes_servicio rs
        WHERE ar.reporte_servicio_id IS NULL
        AND rs.imeis_articulos IS NOT NULL
        AND JSON_SEARCH(rs.imeis_articulos, 'all', ar.numero_dispositivo) IS NOT NULL
    """)
    matches_json = cursor.fetchall()
    
    for match in matches_json:
        cursor.execute("""
            UPDATE activaciones_recientes 
            SET status = 'con_reporte', reporte_servicio_id = %s
            WHERE id = %s
        """, (match['reporte_id'], match['id']))
    
    actualizados_json = len(matches_json)
    
    # Marcar como sin_reporte los que no tienen reporte
    cursor.execute("""
        UPDATE activaciones_recientes
        SET status = 'sin_reporte'
        WHERE status = 'pendiente'
        AND reporte_servicio_id IS NULL
    """)
    sin_reporte = cursor.rowcount
    
    db.commit()
    
    # Obtener conteos
    cursor.execute("SELECT status, COUNT(*) as cantidad FROM activaciones_recientes GROUP BY status")
    conteos = {row['status']: row['cantidad'] for row in cursor.fetchall()}
    
    cursor.close()
    db.close()
    
    return {
        "message": "Verificación completada",
        "actualizados_por_imei": actualizados_imei,
        "actualizados_por_json": actualizados_json,
        "marcados_sin_reporte": sin_reporte,
        "conteos": conteos
    }

# =====================================================
# PUT /activaciones-recientes/{id}/status
# Actualizar status manualmente
# =====================================================
@app.put("/activaciones-recientes/{activacion_id}/status")
def update_activacion_status(activacion_id: int, data: dict = Body(...)):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor()
    
    status = data.get('status')
    reporte_id = data.get('reporte_servicio_id')
    
    if status not in ['pendiente', 'con_reporte', 'sin_reporte']:
        raise HTTPException(status_code=400, detail="Status inválido")
    
    cursor.execute("""
        UPDATE activaciones_recientes 
        SET status = %s, reporte_servicio_id = %s
        WHERE id = %s
    """, (status, reporte_id, activacion_id))
    
    db.commit()
    affected = cursor.rowcount
    cursor.close()
    db.close()
    
    if affected == 0:
        raise HTTPException(status_code=404, detail="Activación no encontrada")
    
    return {"message": "Status actualizado", "id": activacion_id, "status": status}

# =====================================================
# DELETE /activaciones-recientes
# Eliminar activaciones antiguas (limpieza)
# =====================================================
@app.delete("/activaciones-recientes")
def delete_activaciones_antiguas(dias_antiguedad: int = Query(90, description="Eliminar registros más antiguos que X días")):
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor()
    
    cursor.execute("""
        DELETE FROM activaciones_recientes 
        WHERE fecha_carga < DATE_SUB(NOW(), INTERVAL %s DAY)
    """, (dias_antiguedad,))
    
    eliminados = cursor.rowcount
    db.commit()
    cursor.close()
    db.close()
    
    return {"message": f"Limpieza completada", "eliminados": eliminados}

# =====================================================
# GET /activaciones-recientes/stats
# Estadísticas de activaciones
# =====================================================
@app.get("/activaciones-recientes/stats")
def get_activaciones_stats():
    db = mysql.connector.connect(
        host="localhost",
        user="usuario_vue",
        password="tu_password_segura",
        database="nombre_de_tu_db"
    )
    cursor = db.cursor(dictionary=True)
    
    # Conteo por status
    cursor.execute("""
        SELECT status, COUNT(*) as cantidad 
        FROM activaciones_recientes 
        GROUP BY status
    """)
    por_status = {row['status']: row['cantidad'] for row in cursor.fetchall()}
    
    # Conteo por modelo
    cursor.execute("""
        SELECT modelo_dispositivo, COUNT(*) as cantidad 
        FROM activaciones_recientes 
        GROUP BY modelo_dispositivo 
        ORDER BY cantidad DESC 
        LIMIT 10
    """)
    por_modelo = cursor.fetchall()
    
    # Activaciones últimos 7 días
    cursor.execute("""
        SELECT DATE(hora_activacion) as fecha, COUNT(*) as cantidad 
        FROM activaciones_recientes 
        WHERE hora_activacion >= DATE_SUB(NOW(), INTERVAL 7 DAY)
        GROUP BY DATE(hora_activacion) 
        ORDER BY fecha DESC
    """)
    ultimos_7_dias = cursor.fetchall()
    for row in ultimos_7_dias:
        if row.get('fecha'):
            row['fecha'] = row['fecha'].isoformat() if hasattr(row['fecha'], 'isoformat') else str(row['fecha'])
    
    cursor.close()
    db.close()
    
    return {
        "por_status": por_status,
        "por_modelo": por_modelo,
        "ultimos_7_dias": ultimos_7_dias,
        "total": sum(por_status.values())
    }

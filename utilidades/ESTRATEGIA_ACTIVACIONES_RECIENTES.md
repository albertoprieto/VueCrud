# Estrategia de Persistencia - Activaciones Recientes

## Resumen
Esta estrategia permite cargar archivos Excel de activaciones recientes, almacenarlos en la base de datos MySQL, y verificar automáticamente si cada dispositivo tiene un reporte de servicio asociado.

---

## 1. Estructura de Base de Datos

### Tabla: `activaciones_recientes`
```sql
CREATE TABLE activaciones_recientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cuenta VARCHAR(100) NOT NULL,
    numero_dispositivo VARCHAR(50) NOT NULL,
    nombre_dispositivo VARCHAR(200),
    modelo_dispositivo VARCHAR(200),
    numero_tarjeta_sim VARCHAR(50),
    hora_activacion DATETIME,
    status ENUM('pendiente', 'con_reporte', 'sin_reporte') DEFAULT 'pendiente',
    reporte_servicio_id INT NULL,
    fecha_carga TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    cargado_por VARCHAR(100),
    
    UNIQUE KEY uk_cuenta_dispositivo (cuenta, numero_dispositivo),
    INDEX idx_status (status),
    INDEX idx_hora_activacion (hora_activacion),
    INDEX idx_numero_dispositivo (numero_dispositivo),
    FOREIGN KEY (reporte_servicio_id) REFERENCES reportes_servicio(id) ON DELETE SET NULL
);
```

**Ver archivo completo:** `utilidades/sql/crear_tabla_activaciones_recientes.sql`

---

## 2. Endpoints API (FastAPI)

### Endpoints disponibles:

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/activaciones-recientes` | Obtener activaciones con filtros |
| POST | `/activaciones-recientes/bulk` | Insertar/actualizar múltiples registros |
| GET | `/activaciones-recientes/verificar-reportes` | Sincronizar status de reportes |
| PUT | `/activaciones-recientes/{id}/status` | Actualizar status manual |
| DELETE | `/activaciones-recientes` | Limpiar registros antiguos |
| GET | `/activaciones-recientes/stats` | Estadísticas |

**Ver código completo:** `utilidades/endpoints_activaciones_recientes.py`

### Ejemplo de uso - POST Bulk:
```json
POST /activaciones-recientes/bulk
{
  "activaciones": [
    {
      "cuenta": "123456",
      "numero_dispositivo": "867144060421094",
      "nombre_dispositivo": "GPS Tracker",
      "modelo_dispositivo": "GT06",
      "numero_tarjeta_sim": "8952140066...",
      "hora_activacion": "2024-01-15T10:30:00"
    }
  ],
  "cargado_por": "admin"
}
```

---

## 3. Servicio JavaScript

**Archivo:** `src/services/activacionesService.js`

### Funciones disponibles:
- `getActivacionesRecientes(filtros)` - Obtener activaciones de la BD
- `guardarActivacionesBulk(activaciones, usuario)` - Guardar múltiples registros
- `verificarReportesActivaciones()` - Sincronizar status
- `actualizarStatusActivacion(id, status)` - Actualizar status individual
- `getEstadisticasActivaciones()` - Obtener estadísticas

---

## 4. Flujo de Trabajo

### Flujo al cargar un archivo Excel:
```
1. Usuario carga archivo Excel
2. Sistema procesa archivo (parseExcel)
3. Muestra datos en tabla con status de reportes (API existente)
4. Usuario presiona "Guardar en BD"
5. Sistema hace UPSERT de todos los registros
6. Backend verifica automáticamente reportes existentes
7. Status se actualiza: pendiente → con_reporte / sin_reporte
```

### Flujo de sincronización:
```
1. Usuario presiona "Sincronizar reportes"
2. Backend busca coincidencias por:
   - Campo `imei` en reportes_servicio
   - Campo JSON `imeis_articulos` en reportes_servicio
3. Actualiza status de activaciones
4. Retorna conteo de actualizaciones
```

---

## 5. Estados del Registro

| Status | Descripción | Color |
|--------|-------------|-------|
| `pendiente` | Recién cargado, no verificado | Gris |
| `con_reporte` | Tiene reporte de servicio asociado | Verde |
| `sin_reporte` | Verificado, no tiene reporte | Naranja |

---

## 6. Instalación

### Paso 1: Crear tabla en MySQL
```bash
mysql -u usuario -p nombre_db < utilidades/sql/crear_tabla_activaciones_recientes.sql
```

### Paso 2: Agregar endpoints al main.py
Copiar el contenido de `utilidades/endpoints_activaciones_recientes.py` al archivo `main.py` del backend.

### Paso 3: Configurar conexión BD
Actualizar las credenciales de MySQL en los endpoints:
```python
db = mysql.connector.connect(
    host="tu_host",
    user="tu_usuario",
    password="tu_password",
    database="tu_database"
)
```

---

## 7. Ventajas de esta Estrategia

1. **Persistencia**: Los datos no se pierden al cerrar la aplicación
2. **Velocidad**: El status se consulta desde la BD, no de la API de reportes
3. **Histórico**: Se mantiene registro de todas las cargas
4. **Deduplicación**: El UPSERT evita registros duplicados (cuenta + dispositivo)
5. **Trazabilidad**: Se guarda quién cargó y cuándo
6. **Limpieza**: Endpoint para eliminar registros antiguos

---

## 8. Consideraciones

- La llave única es `(cuenta, numero_dispositivo)` - evita duplicados
- El trigger actualiza automáticamente el status cuando se asigna un reporte
- La vista `v_activaciones_con_reporte` facilita consultas con JOIN
- Se recomienda sincronizar reportes después de crear un nuevo reporte de servicio

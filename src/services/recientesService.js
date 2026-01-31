/**
 * Servicio para procesar activaciones recientes desde un archivo CSV/Excel
 * Equivalente en JS del script de Python proporcionado
 */

import { getTodosReportes } from './reportesServicio';
import * as XLSX from 'xlsx';

/**
 * Parsea un archivo Excel (.xlsx, .xls) y lo convierte en un array de objetos
 * Equivalente a pd.read_excel('datos.xlsx', header=1)
 * @param {File} file - Archivo Excel a parsear
 * @returns {Promise<Object>} - { headers, data }
 */
export const parseExcel = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const data = new Uint8Array(e.target.result);
        const workbook = XLSX.read(data, { type: 'array' });
        
        // Tomar la primera hoja
        const firstSheetName = workbook.SheetNames[0];
        const worksheet = workbook.Sheets[firstSheetName];
        
        // Convertir a array de arrays (todas las filas)
        const allRows = XLSX.utils.sheet_to_json(worksheet, { header: 1, defval: '' });
        
        console.log('Total de filas en el Excel:', allRows.length);
        console.log('Fila 0 (título extraño):', allRows[0]);
        console.log('Fila 1 (headers reales):', allRows[1]);
        
        if (allRows.length < 3) {
          reject(new Error('El archivo Excel no tiene suficientes filas'));
          return;
        }

        // header=1 en Python significa: la fila índice 1 es el header
        // (saltamos la fila 0 que tiene un header extraño)
        const headerIndex = 1;
        
        const headers = allRows[headerIndex].map(h => String(h || '').trim()).filter(h => h);
        console.log('Headers encontrados (fila 1):', headers);
        
        const dataRows = [];
        for (let i = headerIndex + 1; i < allRows.length; i++) {
          const rowValues = allRows[i];
          if (rowValues && rowValues.some(v => v !== '' && v !== null && v !== undefined)) {
            const row = {};
            headers.forEach((header, idx) => {
              let value = rowValues[idx];
              // Manejar fechas de Excel (números seriales)
              if (typeof value === 'number' && value > 40000 && value < 60000) {
                // Probablemente es una fecha de Excel
                try {
                  const excelDate = XLSX.SSF.parse_date_code(value);
                  if (excelDate) {
                    value = new Date(excelDate.y, excelDate.m - 1, excelDate.d, excelDate.H || 0, excelDate.M || 0, excelDate.S || 0).toISOString();
                  }
                } catch {
                  // Mantener el valor original
                }
              } else if (value instanceof Date) {
                value = value.toISOString();
              }
              row[header] = value !== null && value !== undefined ? String(value).trim() : '';
            });
            dataRows.push(row);
          }
        }

        console.log('Total de filas de datos:', dataRows.length);
        if (dataRows.length > 0) {
          console.log('Primera fila de datos:', dataRows[0]);
        }

        resolve({ headers, data: dataRows });
      } catch (err) {
        console.error('Error parseando Excel:', err);
        reject(err);
      }
    };
    reader.onerror = () => reject(new Error('Error al leer el archivo'));
    reader.readAsArrayBuffer(file);
  });
};

/**
 * Busca la fila que contiene los headers en un array de arrays
 */
const findHeaderRowInArray = (rows) => {
  const headerPatterns = [
    /imei/i,
    /activac/i,
    /fecha/i,
    /hora/i,
    /serie/i,
    /modelo/i,
    /cliente/i,
    /numero/i,
    /cuenta/i,
    /dispositivo/i,
    /plataforma/i,
    /vencimiento/i,
    /tarjeta/i,
    /sim/i
  ];

  for (let i = 0; i < Math.min(rows.length, 10); i++) {
    const row = rows[i];
    if (!row || !Array.isArray(row)) continue;
    
    const rowText = row.map(c => String(c || '').toLowerCase()).join(' ');
    let matches = 0;
    
    for (const pattern of headerPatterns) {
      if (pattern.test(rowText)) {
        matches++;
      }
    }
    
    // Si encontramos al menos 2 patrones, probablemente es el header
    if (matches >= 2) {
      return i;
    }
  }
  
  // Si no encontramos un header claro, asumir fila 1 (índice 1) como header=1 en Python
  return rows.length > 1 ? 1 : 0;
};

/**
 * Parsea un archivo CSV y lo convierte en un array de objetos
 * @param {File} file - Archivo CSV a parsear
 * @returns {Promise<Array<Object>>} - Array de objetos con los datos del CSV
 */
export const parseCSV = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const text = e.target.result;
        const lines = text.split(/\r?\n/).filter(line => line.trim());
        
        if (lines.length < 2) {
          reject(new Error('El archivo CSV no tiene suficientes líneas'));
          return;
        }

        // Buscar la fila que contiene los headers reales
        // Similar a pd.read_excel('datos.xlsx', header=1) - saltamos filas extrañas
        let headerIndex = findHeaderRow(lines);
        
        console.log('Header encontrado en línea:', headerIndex);
        console.log('Headers:', lines[headerIndex]);

        const headers = parseCSVLine(lines[headerIndex]);
        const data = [];

        for (let i = headerIndex + 1; i < lines.length; i++) {
          const values = parseCSVLine(lines[i]);
          // Permitir filas con diferente número de columnas (rellenar con vacío)
          if (values.length > 0) {
            const row = {};
            headers.forEach((header, idx) => {
              row[header.trim()] = values[idx]?.trim() || '';
            });
            data.push(row);
          }
        }

        resolve({ headers, data });
      } catch (err) {
        reject(err);
      }
    };
    reader.onerror = () => reject(new Error('Error al leer el archivo'));
    reader.readAsText(file);
  });
};

/**
 * Busca la fila que contiene los headers reales del CSV
 * Busca patrones comunes como IMEI, activación, fecha, etc.
 */
const findHeaderRow = (lines) => {
  const headerPatterns = [
    /imei/i,
    /activac/i,
    /fecha/i,
    /hora/i,
    /serie/i,
    /cuenta/i,
    /dispositivo/i,
    /plataforma/i,
    /vencimiento/i,
    /tarjeta/i,
    /sim/i,
    /modelo/i,
    /cliente/i,
    /numero/i
  ];

  for (let i = 0; i < Math.min(lines.length, 10); i++) {
    const lineLower = lines[i].toLowerCase();
    let matches = 0;
    
    for (const pattern of headerPatterns) {
      if (pattern.test(lineLower)) {
        matches++;
      }
    }
    
    // Si encontramos al menos 2 patrones, probablemente es el header
    if (matches >= 2) {
      return i;
    }
  }
  
  // Si no encontramos un header claro, asumir que es la segunda fila (índice 1)
  // como hace el código Python con header=1
  return lines.length > 1 ? 1 : 0;
};

/**
 * Parsea una línea de CSV manejando comas dentro de comillas
 */
const parseCSVLine = (line) => {
  const result = [];
  let current = '';
  let inQuotes = false;

  for (let i = 0; i < line.length; i++) {
    const char = line[i];
    if (char === '"') {
      inQuotes = !inQuotes;
    } else if (char === ',' && !inQuotes) {
      result.push(current);
      current = '';
    } else {
      current += char;
    }
  }
  result.push(current);
  return result;
};

/**
 * Encuentra la columna de activación en los headers
 * @param {Array<string>} headers - Array de encabezados
 * @returns {string|null} - Nombre de la columna de activación
 */
export const findActivationColumn = (headers) => {
  // Normalizar headers removiendo espacios extra
  const normalizedHeaders = headers.map(h => h.trim());
  
  // Buscar columna que contenga "hora" y "activacion" (prioridad alta)
  for (const col of normalizedHeaders) {
    const colLower = col.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, ''); // Remover acentos
    if (colLower.includes('hora') && colLower.includes('activac')) {
      return col;
    }
  }
  
  // Buscar "Hora de activación" o variantes
  for (const col of normalizedHeaders) {
    const colLower = col.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
    if (colLower.includes('activacion') || colLower.includes('activac')) {
      return col;
    }
  }
  
  // Buscar columnas de fecha/hora
  for (const col of normalizedHeaders) {
    const colLower = col.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
    if (colLower.includes('fecha') || colLower.includes('date') || colLower.includes('time')) {
      return col;
    }
  }
  
  console.log('Columnas disponibles:', normalizedHeaders);
  return null;
};

/**
 * Encuentra la columna de IMEI en los headers
 * @param {Array<string>} headers - Array de encabezados
 * @returns {string|null} - Nombre de la columna de IMEI
 */
export const findIMEIColumn = (headers) => {
  // Buscar "Número de dispositivo" primero (formato del archivo del usuario)
  for (const col of headers) {
    const colLower = col.toLowerCase().trim();
    if (colLower.includes('número de dispositivo') || colLower.includes('numero de dispositivo')) {
      return col;
    }
  }
  
  // Buscar IMEI
  for (const col of headers) {
    const colLower = col.toLowerCase().trim();
    if (colLower === 'imei' || colLower.includes('imei')) {
      return col;
    }
  }
  
  // Buscar columnas que podrían ser IMEI
  for (const col of headers) {
    const colLower = col.toLowerCase().trim();
    if (colLower.includes('serie') || colLower.includes('serial') || colLower.includes('dispositivo')) {
      return col;
    }
  }
  return null;
};

/**
 * Parsea una fecha desde string a Date
 * Soporta múltiples formatos comunes
 */
export const parseDate = (dateStr) => {
  if (!dateStr) return null;
  
  // Intentar parseo directo
  let date = new Date(dateStr);
  if (!isNaN(date.getTime())) return date;

  // Formato DD/MM/YYYY HH:MM:SS
  const match1 = dateStr.match(/(\d{2})\/(\d{2})\/(\d{4})\s*(\d{2})?:?(\d{2})?:?(\d{2})?/);
  if (match1) {
    const [, day, month, year, hour = '0', min = '0', sec = '0'] = match1;
    return new Date(year, month - 1, day, hour, min, sec);
  }

  // Formato YYYY-MM-DD HH:MM:SS
  const match2 = dateStr.match(/(\d{4})-(\d{2})-(\d{2})\s*(\d{2})?:?(\d{2})?:?(\d{2})?/);
  if (match2) {
    const [, year, month, day, hour = '0', min = '0', sec = '0'] = match2;
    return new Date(year, month - 1, day, hour, min, sec);
  }

  return null;
};

/**
 * Filtra los registros de los últimos N días
 * @param {Array<Object>} data - Datos a filtrar
 * @param {string} dateColumn - Nombre de la columna de fecha
 * @param {number} days - Número de días hacia atrás (default: 30)
 * @returns {Array<Object>} - Datos filtrados
 */
export const filterByDays = (data, dateColumn, days = 30) => {
  const now = new Date();
  const limitDate = new Date(now.getTime() - days * 24 * 60 * 60 * 1000);

  return data.filter(row => {
    const date = parseDate(row[dateColumn]);
    return date && date >= limitDate;
  });
};

/**
 * Ordena los datos por fecha de activación (más reciente primero)
 * @param {Array<Object>} data - Datos a ordenar
 * @param {string} dateColumn - Nombre de la columna de fecha
 * @returns {Array<Object>} - Datos ordenados
 */
export const sortByDateDesc = (data, dateColumn) => {
  return [...data].sort((a, b) => {
    const dateA = parseDate(a[dateColumn]);
    const dateB = parseDate(b[dateColumn]);
    if (!dateA && !dateB) return 0;
    if (!dateA) return 1;
    if (!dateB) return -1;
    return dateB.getTime() - dateA.getTime();
  });
};

/**
 * Procesa el archivo CSV o Excel completo
 * @param {File} file - Archivo CSV o Excel
 * @param {number} days - Días hacia atrás para filtrar (default: 30)
 * @returns {Promise<Object>} - Resultado del procesamiento
 */
export const processCSVFile = async (file, days = 30) => {
  // Detectar tipo de archivo por extensión
  const fileName = file.name.toLowerCase();
  const isExcel = fileName.endsWith('.xlsx') || fileName.endsWith('.xls');
  
  console.log('=== PROCESAMIENTO ARCHIVO ===');
  console.log('Nombre:', file.name);
  console.log('Tipo detectado:', isExcel ? 'Excel' : 'CSV');

  // Usar el parser apropiado
  const { headers, data } = isExcel 
    ? await parseExcel(file) 
    : await parseCSV(file);

  console.log('Headers encontrados:', headers);
  console.log('Total de filas de datos:', data.length);
  if (data.length > 0) {
    console.log('Primera fila de ejemplo:', data[0]);
  }

  const activationColumn = findActivationColumn(headers);
  const imeiColumn = findIMEIColumn(headers);

  console.log('Columna de activación detectada:', activationColumn);
  console.log('Columna de IMEI detectada:', imeiColumn);

  if (!activationColumn) {
    return {
      success: false,
      error: `No se encontró una columna de fecha/hora de activación. Columnas disponibles: ${headers.join(', ')}`,
      headers,
      data: data // Devolver datos sin filtrar para debug
    };
  }

  // Filtrar por días
  const filteredData = filterByDays(data, activationColumn, days);
  console.log(`Registros después de filtrar (últimos ${days} días):`, filteredData.length);

  // Ordenar por fecha descendente
  const sortedData = sortByDateDesc(filteredData, activationColumn);

  return {
    success: true,
    headers,
    activationColumn,
    imeiColumn,
    totalRegistros: data.length,
    registrosFiltrados: sortedData.length,
    data: sortedData
  };
};

/**
 * Verifica si un IMEI tiene un reporte de servicio generado
 * @param {string} imei - IMEI a verificar
 * @param {Array<Object>} reportes - Lista de reportes de servicio
 * @returns {Object|null} - Reporte encontrado o null
 */
export const findReporteByIMEI = (imei, reportes) => {
  if (!imei || !reportes || !Array.isArray(reportes)) return null;
  
  const imeiStr = String(imei).trim();
  
  return reportes.find(reporte => {
    // Buscar en el campo imei principal
    if (reporte.imei && String(reporte.imei).trim() === imeiStr) {
      return true;
    }
    // Buscar en imeis_articulos si existe (JSON array)
    if (reporte.imeis_articulos) {
      try {
        const imeisArr = typeof reporte.imeis_articulos === 'string' 
          ? JSON.parse(reporte.imeis_articulos) 
          : reporte.imeis_articulos;
        if (Array.isArray(imeisArr)) {
          for (const item of imeisArr) {
            if (Array.isArray(item?.imeis)) {
              if (item.imeis.some(i => String(i).trim() === imeiStr)) {
                return true;
              }
            }
          }
        }
      } catch {
        // Ignorar errores de parseo
      }
    }
    return false;
  }) || null;
};

/**
 * Enriquece los datos del CSV con información de reportes de servicio
 * @param {Array<Object>} data - Datos del CSV
 * @param {string} imeiColumn - Nombre de la columna de IMEI
 * @returns {Promise<Array<Object>>} - Datos enriquecidos
 */
export const enrichWithReportesInfo = async (data, imeiColumn) => {
  if (!imeiColumn) {
    return data.map(row => ({
      ...row,
      _tieneReporte: false,
      _reporteInfo: null,
      _imeiNoEncontrado: true
    }));
  }

  // Obtener todos los reportes de servicio
  let reportes = [];
  try {
    reportes = await getTodosReportes();
  } catch (error) {
    console.error('Error al obtener reportes:', error);
  }

  return data.map(row => {
    const imei = row[imeiColumn];
    const reporte = findReporteByIMEI(imei, reportes);
    
    return {
      ...row,
      _tieneReporte: !!reporte,
      _reporteInfo: reporte,
      _imeiNoEncontrado: !imei
    };
  });
};

/**
 * Calcula totales de los datos
 * @param {Array<Object>} data - Datos a totalizar
 * @returns {Object} - Totales
 */
export const calculateTotals = (data) => {
  const totals = {
    totalRegistros: data.length,
    conReporte: 0,
    sinReporte: 0,
    sinIMEI: 0
  };

  for (const row of data) {
    if (row._imeiNoEncontrado) {
      totals.sinIMEI++;
    } else if (row._tieneReporte) {
      totals.conReporte++;
    } else {
      totals.sinReporte++;
    }
  }

  return totals;
};

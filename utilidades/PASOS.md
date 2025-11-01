

# PASOS.md

## Flujo completo de la aplicación (VueCrud)

Este documento describe el recorrido funcional de la aplicación, desde el acceso inicial hasta el cierre de procesos, pasando por todos los módulos principales. Se anotan inconsistencias y puntos críticos para facilitar el testeo y la mejora continua.

---


### 1. Acceso y Autenticación

**Componente principal:** `login.vue`

**Estructura y campos:**
- Formulario con dos campos principales:
  - Usuario (input tipo texto)
  - Contraseña (input tipo password)
- Botón de acceso: "Iniciar sesión"
- Feedback visual: loader/spinner durante la petición, toast o mensaje de error si falla.

**Validaciones:**
- Se debe validar que ambos campos no estén vacíos antes de enviar.
- Puede faltar validación de formato de usuario (correo, longitud mínima, etc).

**Flujo:**
1. El usuario accede a la pantalla de login.
2. Ingresa usuario y contraseña.
3. Al hacer clic en "Iniciar sesión":
   - Se envía petición POST al endpoint `/login` (API backend).
   - Si la respuesta es exitosa, se recibe un `access_token` y datos de usuario.
   - Se guarda el token en el store/localStorage y se redirige al dashboard.
   - Si la respuesta es error, se muestra mensaje visual (toast, modal, alerta).

**Endpoints principales:**
- POST `/login` (autenticación)

**Feedback visual:**
- Loader/spinner mientras se espera la respuesta.
- Toast o alerta en caso de error (credenciales incorrectas, usuario inactivo, etc).

**Ejemplo de error frecuente:**
> El usuario ingresa credenciales incorrectas y el sistema muestra un mensaje genérico, sin indicar si el usuario existe o si la contraseña es incorrecta.

---



### 2. Dashboard (Menú principal)

**Componente principal:** `dashboard.vue`

**Estructura y componentes:**
- Panel principal con indicadores (ventas, instalaciones, stock, alertas).
- Menú lateral y superior generado dinámicamente con array de `items`:
  - Cada `item` tiene: `label`, `route`, `icon`, y opcionalmente `badge` (notificaciones).
  - Submenús para módulos agrupados (Inventario, Ventas, Clientes, Técnicos, etc).
- Navegación mediante `<router-link>` y acciones con botones.
- Botón de perfil y cierre de sesión.

**Navegación y flujo:**
1. Al acceder, el usuario ve el dashboard con el menú y los indicadores.
2. Puede navegar a cualquier módulo haciendo clic en el menú.
3. El menú y los indicadores se actualizan según el perfil y los datos del usuario.
4. El usuario puede cerrar sesión desde el botón de perfil.

**Feedback visual:**
- Loader/spinner al cambiar de módulo o cargar datos.
- Badges en el menú para notificaciones (ejemplo: cotizaciones pendientes, reportes nuevos).
- Toasts y alertas en caso de error al cargar datos.

**Validaciones y lógica:**
- El menú debería mostrar solo las opciones permitidas según el perfil (admin, técnico, cliente, etc), pero puede faltar validación en frontend.
- Los indicadores deben actualizarse en tiempo real o con polling, pero pueden quedarse desactualizados si la lógica reactiva falla.
- El menú depende de la estructura de `items`, si se modifica sin control puede romper la navegación.

**Endpoints principales:**
- GET `/dashboard/indicators` (panel de indicadores)
- GET `/notificaciones` (badges y alertas)

**Inconsistencias y observaciones:**
- El menú puede mostrar opciones no permitidas según el perfil (falta validación de permisos en frontend).
- Los indicadores pueden no actualizarse en tiempo real (revisar lógica reactiva y polling).
- El menú depende de la estructura de `items`, si se modifica sin control puede romper la navegación.
- El cierre de sesión puede no limpiar correctamente el estado global.
- Falta confirmación visual al cerrar sesión.

**Ejemplo de error frecuente:**
> El usuario cambia de perfil y el menú no se actualiza, mostrando opciones que no debería ver.

### 3. Inventario

**Componentes principales:**
- `Articulos.vue`: gestión de artículos y stock.
- `AsignarImeis.vue`: asignación de IMEIs a artículos.
- `ArticulosConImeis.vue`: visualización de artículos con IMEIs asignados.
- `TransferirImeis.vue`: transferencia de IMEIs entre ubicaciones.
- `BuscarImei.vue`: búsqueda de IMEI por número.

**Estructura y campos:**
- Listado de artículos en `DataTable` con columnas: código, nombre, SKU, tipo, precio venta, precio compra, stock, ubicación, etc.
- Formularios de alta/edición de artículo con campos obligatorios y dropdowns para tipo, ubicación, etc.
- Botones para agregar, editar, eliminar, exportar a Excel, asignar y transferir IMEIs.
- Modales para confirmación de acciones y edición.

**Validaciones:**
- Validar que los campos obligatorios estén completos antes de guardar.
- Validar que el SKU y código sean únicos.
- Validar que la cantidad de IMEIs asignados no exceda el stock disponible.

**Feedback visual:**
- Loader/spinner al cargar o modificar artículos.
- Toasts y alertas en caso de éxito o error (alta, edición, transferencia, exportación).
- Mensajes de confirmación antes de eliminar o transferir IMEIs.

**Endpoints principales:**
- GET `/articulos` (listado)
- POST `/articulos` (alta)
- PUT `/articulos/:id` (edición)
- DELETE `/articulos/:id` (eliminación)
- POST `/asignar-imei` (asignación)
- POST `/transferir-imei` (transferencia)

**Inconsistencias y observaciones:**
- El stock puede no reflejar movimientos recientes si no hay actualización tras transferencias.
- Falta validación de campos obligatorios en formularios (puede guardar incompleto).
- El manejo de errores en transferencias y asignaciones puede ser insuficiente (no siempre muestra feedback visual).
- Exportar a Excel puede fallar si hay datos corruptos o campos vacíos.
- La búsqueda de IMEI puede no encontrar resultados si el backend no indexa correctamente.

**Ejemplo de error frecuente:**
> El usuario intenta asignar más IMEIs de los que hay en stock y el sistema lo permite, generando inconsistencias en inventario.


### 4. Ventas

**Componentes principales:**
- `Ventas.vue`: registro y edición de ventas/órdenes de servicio.
- `consultarVentas.vue`: consulta de ventas históricas y detalle.

**Estructura y campos:**
- Formulario de venta con campos:
  - Cliente (dropdown)
  - Cotización (opcional, dropdown)
  - Artículos (tabla editable, selección y cantidad)
  - Vendedor (dropdown)
  - Fecha, referencia, ubicación, descuentos, observaciones, términos y condiciones
  - Método de pago (dropdown), total, subtotal
- Botones para agregar artículos, generar orden, descargar PDF, aceptar/cancelar
- Modal de confirmación al guardar

**Validaciones:**
- Validar que todos los campos obligatorios estén completos antes de guardar.
- Validar que el stock de cada artículo sea suficiente antes de registrar la venta.
- Validar formato de fecha y datos numéricos.

**Feedback visual:**
- Loader/spinner al guardar o consultar ventas.
- Toasts y alertas en caso de éxito o error (registro, edición, descarga).
- Mensaje de confirmación al guardar la orden.

**Endpoints principales:**
- GET `/ventas` (listado)
- POST `/ventas` (registro)
- PUT `/ventas/:id` (edición)
- GET `/ventas/:id/pdf` (descarga PDF)

**Inconsistencias y observaciones:**
- El PDF puede no reflejar todos los datos si el modelo de venta está incompleto o hay campos vacíos.


**Ejemplo de error frecuente:**
> El usuario registra una venta con descuento y el total calculado no coincide con el esperado, generando confusión y posibles errores contables.


### 5. Clientes

**Componente principal:** `Clientes.vue`

**Estructura y campos:**
- Listado de clientes en `DataTable` con columnas: nombre, teléfonos, correo, ciudad, usuarios, plataformas.
- Formularios de alta/edición de cliente con campos:
  - Nombre, teléfonos (inputs dinámicos), correo, ciudad
  - Usuarios (inputs dinámicos), plataformas (inputs dinámicos)
- Botones para agregar, editar, eliminar, limpiar filtros
- Modal para edición y confirmación de acciones

**Validaciones:**
- Validar que los campos obligatorios estén completos antes de guardar.
- Validar formato de correo y teléfono.
- Validar que no haya duplicados en usuarios y teléfonos.

**Feedback visual:**
- Loader/spinner al guardar o consultar clientes.
- Toasts y alertas en caso de éxito o error (registro, edición, eliminación).
- Mensaje de confirmación al guardar o eliminar.

**Endpoints principales:**
- GET `/clientes` (listado)
- POST `/clientes` (registro)
- PUT `/clientes/:id` (edición)
- DELETE `/clientes/:id` (eliminación)

**Inconsistencias y observaciones:**
- La edición puede no guardar correctamente los cambios si el backend no responde.
- Falta validación de duplicados en usuarios y teléfonos (puede guardar datos repetidos).
- El feedback visual puede ser insuficiente en errores de guardado o eliminación.
- El filtro de búsqueda puede no funcionar correctamente si hay problemas de indexación.

**Ejemplo de error frecuente:**
> El usuario agrega un cliente con dos teléfonos iguales y el sistema lo permite, generando confusión en futuras consultas.

---


### 6. Cotizaciones

**Componentes principales:**
- `Cotizador.vue`: creación y edición de cotizaciones.
- `ConsultarCotizaciones.vue`: consulta de cotizaciones históricas.
- `CalendarioCotizaciones.vue`: calendarización y seguimiento de cotizaciones.

**Estructura y campos:**
- Formulario de cotización con campos:
  - Cliente (dropdown)
  - Artículos (tabla editable, selección y cantidad)
  - Precios, descuentos, observaciones
  - Fecha, vendedor
- Botones para crear, editar, convertir en venta, calendarizar
- Modal de confirmación al guardar o convertir

**Validaciones:**
- Validar que los campos obligatorios estén completos antes de guardar.
- Validar que los precios y descuentos sean correctos.
- Validar que la conversión a venta conserve todos los datos relevantes.

**Feedback visual:**
- Loader/spinner al guardar, consultar o convertir cotizaciones.
- Toasts y alertas en caso de éxito o error (registro, edición, conversión).
- Mensaje de confirmación al guardar o convertir.

**Endpoints principales:**
- GET `/cotizaciones` (listado)
- POST `/cotizaciones` (registro)
- PUT `/cotizaciones/:id` (edición)
- POST `/cotizaciones/:id/convertir` (convertir en venta)

**Inconsistencias y observaciones:**
- La conversión de cotización a venta puede perder datos si no se valida el modelo.
- El histórico puede no mostrar todas las cotizaciones si hay problemas de paginación o filtros.
- El feedback visual puede ser insuficiente en errores de conversión o edición.
- La calendarización puede no reflejarse correctamente en el calendario si hay problemas de sincronización.

**Ejemplo de error frecuente:**
> El usuario convierte una cotización en venta y algunos artículos o descuentos no se transfieren correctamente, generando diferencias en el total.

---


### 7. Técnicos y Asignaciones

**Componentes principales:**
- `CalendarioAsignaciones.vue`: visualización y gestión de asignaciones.
- `CalendarioTecnicosTablaDual.vue`: vista dual de asignaciones por técnico y fecha.
- `DetalleAsignacion.vue`: detalle de cada asignación y acceso a reportes.

**Estructura y campos:**
- Calendario visual con asignaciones por técnico y fecha.
- Detalle de asignación con campos: técnico, cliente, nota de venta, fecha, descripción, estado.
- Botones para agregar reporte, descargar orden, editar asignación.
- Modal para agregar reporte de servicio.

**Validaciones:**
- Validar que la asignación exista antes de mostrar el detalle.
- Validar que el ID de asignación y el `venta_id` no se confundan.
- Validar que los campos del reporte estén completos antes de guardar.

**Feedback visual:**
- Loader/spinner al cargar asignaciones o detalles.
- Toasts y alertas en caso de error (asignación no encontrada, error al guardar reporte).
- Mensaje de confirmación al agregar reporte o descargar orden.

**Endpoints principales:**
- GET `/asignaciones` (listado)
- GET `/asignaciones/:id` (detalle)
- POST `/reportes-servicio` (agregar reporte)

**Inconsistencias y observaciones:**
- El ID de asignación puede confundirse con el `venta_id` (revisar lógica de búsqueda y documentación).
- Si la asignación no existe, el flujo se detiene con mensaje de error.
- Falta validación visual en la selección de asignaciones (puede seleccionar una inexistente).
- El feedback visual puede ser insuficiente en errores de guardado o descarga.

**Ejemplo de error frecuente:**
> El usuario intenta agregar un reporte a una asignación inexistente y el sistema no muestra un mensaje claro, quedando el flujo bloqueado.


### 8. Reportes de Servicio

**Componentes principales:**
- `ReporteServicio.vue`: registro y edición de reportes de servicio.
- `ConsultarReportes.vue`: consulta y gestión de reportes históricos.
- `Reporte.vue`: vista y edición de reportes individuales.

**Estructura y campos:**
- Formulario de reporte con campos:
  - Técnico, cliente, fecha, nota de venta, descripción, estado
  - Datos del vehículo, equipo, SIM, observaciones, plataformas, usuarios
  - Subtotal, total, método de pago, pagado, firmas
- Botones para guardar, cancelar, descargar PDF/XML, facturar, marcar como pagado, eliminar
- Modal de confirmación para acciones críticas

**Validaciones:**
- Validar que todos los campos obligatorios estén completos antes de guardar.
- Validar que la asignación y venta asociada existan.
- Validar datos fiscales antes de facturar.

**Feedback visual:**
- Loader/spinner al guardar, consultar, descargar o facturar reportes.
- Toasts y alertas en caso de éxito o error (registro, edición, facturación, descarga).
- Mensaje de confirmación al guardar, eliminar o facturar.

**Endpoints principales:**
- GET `/reportes-servicio` (listado)
- POST `/reportes-servicio` (registro)
- PUT `/reportes-servicio/:id` (edición)
- DELETE `/reportes-servicio/:id` (eliminación)
- GET `/reportes-servicio/:id/pdf` (descarga PDF)
- POST `/reportes-servicio/:id/facturar` (facturación)

**Inconsistencias y observaciones:**
- Si el ID recibido no corresponde a una asignación, el formulario no carga y no muestra mensaje claro.
- Si la venta asociada no existe, no se puede guardar el reporte.
- Facturación puede fallar si faltan datos fiscales o si la API no responde.
- El feedback visual puede ser insuficiente en errores de facturación o descarga.
- El marcado como pagado puede no actualizarse correctamente si hay problemas de sincronización.

**Ejemplo de error frecuente:**
> El usuario intenta facturar un reporte sin datos fiscales completos y el sistema no muestra un mensaje claro, quedando el flujo bloqueado.


### 9. Dinero

**Componente principal:** `Dinero.vue`

**Estructura y campos:**
- Tarjetas resumen de ingresos, egresos y saldo.
- Tabla de movimientos con columnas: fecha, tipo, concepto, monto, referencia.
- Botones para exportar movimientos, filtrar por fecha/tipo/concepto.
- Loader/spinner y mensajes de error/estado vacío.

**Validaciones:**
- Validar que los datos de movimientos sean correctos y completos.
- Validar formato de monto y fecha.
- Validar que los filtros funcionen correctamente.

**Feedback visual:**
- Loader/spinner al cargar movimientos.
- Toasts y alertas en caso de error o estado vacío.
- Mensaje de confirmación al exportar movimientos.

**Endpoints principales:**
- GET `/movimientos-dinero` (listado)
- GET `/movimientos-dinero/exportar` (exportar)

**Inconsistencias y observaciones:**
- El saldo puede no coincidir con los movimientos si hay errores en la API o cálculos incorrectos.
- Falta paginación real si hay muchos movimientos (solo paginación visual).
- El feedback visual puede ser insuficiente en errores de carga o exportación.
- Los filtros pueden no funcionar correctamente si hay problemas de indexación.

**Ejemplo de error frecuente:**
> El usuario exporta los movimientos y el archivo generado no coincide con lo mostrado en pantalla, generando confusión contable.

---

### 10. Usuarios
  - Alta, edición, cambio de contraseña, asignación de roles.
  - Los cambios de rol pueden no aplicarse correctamente si el backend no responde.
  - El alta de usuario puede fallar si no se valida el correo.
  - Falta validación visual en formularios.

### 10. Usuarios

**Componente principal:** `Usuarios.vue`

**Estructura y campos:**
- Listado de usuarios en `DataTable` con columnas: nombre, correo, rol, estado, fecha de alta.
- Formularios de alta/edición de usuario con campos:
  - Nombre, correo, contraseña, rol (dropdown), estado (activo/inactivo)
- Botones para agregar, editar, eliminar, cambiar contraseña, asignar roles
- Modal para edición y confirmación de acciones

**Validaciones:**
- Validar que los campos obligatorios estén completos antes de guardar.
- Validar formato de correo y contraseña.
- Validar que el rol seleccionado sea válido.

**Feedback visual:**
- Loader/spinner al guardar o consultar usuarios.
- Toasts y alertas en caso de éxito o error (registro, edición, cambio de rol, eliminación).
- Mensaje de confirmación al guardar o eliminar.

**Endpoints principales:**
- GET `/usuarios` (listado)
- POST `/usuarios` (registro)
- PUT `/usuarios/:id` (edición)
- DELETE `/usuarios/:id` (eliminación)
- POST `/usuarios/:id/cambiar-contraseña` (cambio de contraseña)

**Inconsistencias y observaciones:**
- Los cambios de rol pueden no aplicarse correctamente si el backend no responde.
- El alta de usuario puede fallar si no se valida el correo o la contraseña.
- Falta validación visual en formularios (puede guardar incompleto).
- El filtro de búsqueda puede no funcionar correctamente si hay problemas de indexación.

**Ejemplo de error frecuente:**
> El usuario registra un nuevo usuario con correo inválido y el sistema lo permite, generando problemas de acceso y comunicación.

---

### 11. Panel de Indicadores

### 11. Panel de Indicadores

**Componente principal:** `dashboard.vue`

**Estructura y campos:**
- Tarjetas/resúmenes para KPIs principales: ventas totales, clientes activos, inventario disponible, cotizaciones generadas, reportes de servicio realizados.
- Gráficas y tablas para mostrar tendencias y comparativas (por mes, semana, día).
- Botones para refrescar datos y navegar a módulos relacionados.

**Validaciones:**
- Validar que los datos recibidos del backend tengan formato y valores esperados.
- Validar que los KPIs no sean negativos o inconsistentes.

**Feedback visual:**
- Loader/spinner al cargar indicadores.
- Toasts y alertas en caso de error de conexión o datos incompletos.
- Mensaje de "Sin datos" si el backend responde vacío.

**Endpoints principales:**
- GET `/dashboard/indicators` (KPIs)
- GET `/dashboard/trends` (gráficas)

**Inconsistencias y observaciones:**
- Los indicadores pueden mostrar datos desactualizados si el backend no responde o hay caché.
- Falta feedback visual en caso de error de conexión (puede quedar en blanco).
- Las gráficas pueden no coincidir con los totales si hay desfase en la actualización.

**Ejemplo de error frecuente:**
> El panel muestra ventas totales en cero aunque existen ventas registradas, por error de sincronización o endpoint caído.

---

### 12. Cierre de sesión y navegación
- El usuario puede cerrar sesión o navegar entre módulos.
- Observaciones:
  - El cierre de sesión puede no limpiar correctamente el estado.
  - Falta confirmación visual al cerrar sesión.

---

---

### 3. Inventario
- Visualizar y gestionar artículos, stock, ubicaciones y transferencias de IMEIs.
- Acciones: alta de artículos, asignar IMEIs, transferir IMEIs, buscar IMEI, consultar ubicaciones.
- **Inconsistencias:**
  - El stock puede no reflejar movimientos recientes.
  - Transferencias pueden fallar si no se valida el destino.

---

### 4. Ventas
- Crear, consultar y editar órdenes de servicio (notas de venta).
- Acciones: registrar venta, consultar histórico, descargar PDF, aplicar descuentos.
- **Inconsistencias:**
  - El cálculo de totales y descuentos puede ser incorrecto.
  - El PDF puede no reflejar todos los datos.

---

### 5. Clientes
- Registrar, editar y consultar clientes, teléfonos, plataformas y usuarios asociados.
- **Inconsistencias:**
  - La edición puede no guardar correctamente los cambios.
  - La relación cliente-usuario puede perderse si la API falla.

---

### 6. Cotizaciones
- Generar, consultar y calendarizar cotizaciones.
- Acciones: crear cotización, consultar histórico, convertir cotización en venta.
- **Inconsistencias:**
  - La conversión de cotización a venta puede perder datos.
  - El histórico puede no mostrar todas las cotizaciones.

---

### 7. Técnicos y Asignaciones
- Visualizar calendario de asignaciones, consultar detalles, agregar reportes de servicio.
- Acciones: asignar servicios, consultar reportes, descargar órdenes.
- **Inconsistencias:**
  - El ID de asignación puede confundirse con el `venta_id`.
  - Si la asignación no existe, el flujo se detiene con mensaje de error.

---

### 8. Reportes de Servicio
- Registrar y editar reportes detallados de instalaciones y servicios.
- Acciones: agregar reporte, consultar histórico, descargar PDF, facturar servicio.
- **Inconsistencias:**
  - Si el ID recibido no corresponde a una asignación, el formulario no carga.
  - Si la venta asociada no existe, no se puede guardar el reporte.
  - Facturación puede fallar si faltan datos fiscales.

---

### 9. Dinero
- Visualizar movimientos, ingresos, egresos y saldo.
- Acciones: consultar histórico, exportar movimientos.
- **Inconsistencias:**
  - El saldo puede no coincidir con los movimientos si hay errores en la API.

---

### 10. Usuarios
- Gestionar usuarios, roles y accesos.
- Acciones: alta, edición, cambio de contraseña, asignación de roles.
- **Inconsistencias:**
  - Los cambios de rol pueden no aplicarse correctamente.
  - El alta de usuario puede fallar si no se valida el correo.

---

### 11. Panel de Indicadores
- Visualizar ventas, instalaciones, stock y alertas operativas.
- **Inconsistencias:**
  - Los indicadores pueden no reflejar el estado real si la API no actualiza correctamente.

---

### 12. Cierre de sesión y navegación

**Componentes principales:**
- Botón de logout en barra superior/menu lateral.
- Redirección automática tras cierre de sesión.
- Menú lateral y superior para navegación entre módulos.

**Estructura y acciones:**
- Al hacer clic en logout:
  - Se llama endpoint de cierre de sesión (opcional, según backend).
  - Se elimina token y datos de usuario del localStorage/sessionStorage.
  - Se redirige automáticamente a la pantalla de login.
- Navegación entre módulos mediante router-link/menu.

**Validaciones:**
- Validar que el token se elimine correctamente.
- Validar que la redirección ocurra tras logout.
- Validar que el usuario no pueda acceder a rutas protegidas tras logout.

**Feedback visual:**
- Toast/alerta de "Sesión cerrada correctamente".
- Loader/spinner si el cierre de sesión tarda.
- Mensaje de error si el backend no responde o el token no se elimina.

**Endpoints principales:**
- POST `/logout` (opcional, según backend)

**Inconsistencias y observaciones:**
- Si el backend no responde, el token puede no eliminarse correctamente y el usuario puede quedar "logueado".
- Falta feedback visual en caso de error (puede quedar en blanco o sin redirección).
- El menú puede mostrar opciones no permitidas si el rol no se actualiza tras logout.

**Ejemplo de error frecuente:**
> El usuario cierra sesión pero al volver a la app, sigue accediendo a rutas protegidas porque el token no se eliminó correctamente.

---

## Notas para el tester
- Verifica que cada paso funcione como se describe.
- Marca cualquier inconsistencia, error o comportamiento inesperado.
- Revisa especialmente el manejo de IDs y la relación entre módulos.
- Documenta cualquier mensaje de error que no sea claro o útil.

---

**Este documento se irá actualizando conforme se detecten y corrijan inconsistencias.**

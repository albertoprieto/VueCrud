import { createRouter, createWebHashHistory } from 'vue-router';
import Informacion from '@/modules/informacion.vue';
import Dinero from '@/modules/Dinero.vue';
import Login from '@/modules/login.vue';
import Reporte from '@/modules/Reporte.vue';
import Registrar from '@/modules/Registrar.vue';
import Consultar from '@/modules/Consultar.vue';
import Cotizacion from '@/modules/Cotizacion.vue';
import ConsultarCotizaciones from '@/modules/ConsultarCotizaciones.vue';
import CalendarioCotizaciones from '@/modules/CalendarioCotizaciones.vue';
import SeguimientoEventos from '@/modules/SeguimientoEventos.vue';
import ConsultarReportes from '@/modules/ConsultarReportes.vue';
import CrearEvento from '@/modules/CrearEvento.vue';
import Articulos from '@/modules/Articulos.vue';
import AsignarImeis from '@/modules/AsignarImeis.vue';
import ArticulosConImeis from '@/modules/ArticulosConImeis.vue';
import Clientes from '@/modules/Clientes.vue';
import Ventas from '@/modules/Ventas.vue';
import Ubicaciones from '@/modules/Ubicaciones.vue';
import UbicacionImeis from '@/modules/UbicacionImeis.vue';
import ConsultarVentas from '@/modules/consultarVentas.vue';
import BuscarImei from '@/modules/BuscarImei.vue';
import HistoricoNotasVenta from '@/modules/HistoricoNotasVenta.vue';
import Usuarios from '@/modules/Usuarios.vue';
import CalendarioAsignaciones from '@/modules/CalendarioAsignaciones.vue';
import DetalleAsignacion from '@/modules/DetalleAsignacion.vue';
import ReporteServicio from '@/modules/ReporteServicio.vue';
import TransferirImeis from '@/modules/TransferirImeis.vue';
import Cotizador from '@/modules/Cotizador.vue';
import CalendarioTecnicosTablaDual from '@/components/CalendarioTecnicosTablaDual.vue';
import TicketsList from '@/modules/TicketsList.vue';
import TicketNew from '@/modules/TicketNew.vue';
import TicketDetail from '@/modules/TicketDetail.vue';
import NuevoReporteDeServicio from '@/modules/NuevoReporteDeServicio.vue';
import Recientes from '@/modules/Recientes.vue';
import RenovacionesRecientes from '@/modules/RenovacionesRecientes.vue';

const routes = [
  { path: '/nuevo-reporte-servicio', name: 'nuevo-reporte-servicio', component: NuevoReporteDeServicio },
  { path: '/', name: 'home', component: Informacion },
  { path: '/login', name: 'login', component: Login },
  { path: '/informacion', name: 'informacion', component: Informacion },
  { path: '/registrar', name: 'registrar', component: Registrar },
  { path: '/consultar', name: 'consultar', component: Consultar },
  { path: '/reporte', name: 'reporte', component: Reporte },
  { path: '/Cotizacion', name: 'Cotizacion', component: Cotizacion },
  { path: '/consultar-cotizaciones', name: 'consultar-cotizaciones', component: ConsultarCotizaciones },
  { path: '/calendario-cotizaciones', name: 'calendario-cotizaciones', component: CalendarioCotizaciones },
  { path: '/consultar-reportes', name: 'consultar-reportes', component: ConsultarReportes },
  { path: '/crear-evento', name: 'crear-evento', component: CrearEvento },
  { path: '/seguimiento', name: 'Seguimiento', component: SeguimientoEventos },
  { path: '/alta-articulo', name: 'alta-articulo', component: Articulos },
  { path: '/asignar-imeis', name: 'asignar-imeis', component: AsignarImeis },
  { path: '/articulos-con-imeis', name: 'articulos-con-imeis', component: ArticulosConImeis },
  { path: '/clientes', name: 'clientes', component: Clientes },
  { path: '/ventas', name: 'ventas', component: Ventas },
  { path: '/ubicaciones', name: 'Ubicaciones', component: Ubicaciones },
  { path: '/ubicaciones/:id/imeis', name: 'UbicacionImeis', component: UbicacionImeis, props: true },
  { path: '/consultar-ventas', name: 'consultar-ventas', component: ConsultarVentas },
  { path: '/buscar-imei', component: BuscarImei },
  { path: '/historico-notas', name: 'historico-notas', component: HistoricoNotasVenta },
  { path: '/usuarios', name: 'usuarios', component: Usuarios },
  { path: '/calendario-asignaciones', name: 'calendario-asignaciones', component: CalendarioAsignaciones },
  { path: '/asignacion/:id', name: 'detalle-asignacion', component: DetalleAsignacion },
  { path: '/reporte-servicio/:asignacionId', name: 'reporte-servicio', component: ReporteServicio },
  { path: '/transferir-imeis', name: 'transferir-imeis', component: TransferirImeis },
  { path: '/cotizador', name: 'cotizador', component: Cotizador },
  { path: '/calendario-tecnicos', name: 'calendario-tecnicos', component: CalendarioTecnicosTablaDual }
  ,{ path: '/dinero', name: 'dinero', component: Dinero }
  ,{ path: '/tickets', name: 'tickets', component: TicketsList }
  ,{ path: '/tickets/new', name: 'ticket-new', component: TicketNew }
  ,{ path: '/tickets/:id', name: 'ticket-detail', component: TicketDetail }
  ,{ path: '/recientes', name: 'recientes', component: Recientes }
  ,{ path: '/renovaciones-recientes', name: 'renovaciones-recientes', component: RenovacionesRecientes }
];

const router = createRouter({
  history: createWebHashHistory(),
  routes
});

export default router;

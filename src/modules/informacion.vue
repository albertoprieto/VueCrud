<template>
  <div>
    <div class="informacion">
      <h1 class="panel-title">Panel de Inicio</h1>
      <div v-for="(group, idx) in groupedItems" :key="group.title" class="section-group">
        <div class="section-header">
          <span>{{ group.title }}</span>
          <div class="section-divider"></div>
        </div>
        <div class="grid-container">
          <div
            v-for="item in group.items"
            :key="item.route"
            class="info-card"
            @click="goTo(item.route)"
          >
            <span :class="['info-icon', item.icon]" style="font-size:2rem;margin-bottom:8px;" />
            <h2>{{ item.label }}</h2>
            <p class="info-desc">{{ item.desc }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';

const router = useRouter();
function goTo(route) {
  console.log('Navegando a:', route); // <-- Agrega esto
  router.push(route);
}

const groupedItems = [
  {
    title: 'Inventario',
    items: [
      { label: 'Alta artículos', route: '/alta-articulo', icon: 'pi pi-fw pi-plus-circle', desc: 'Registrar nuevos artículos' },
      { label: 'Asignar IMEIs', route: '/asignar-imeis', icon: 'pi pi-fw pi-barcode', desc: 'Asignar IMEIs a artículos' },
      { label: 'Ubicaciones', route: '/ubicaciones', icon: 'pi pi-fw pi-map-marker', desc: 'Gestionar ubicaciones' },
      { label: 'Buscar IMEI', route: '/buscar-imei', icon: 'pi pi-fw pi-search', desc: 'Buscar IMEI por número' },
      { label: 'Histórico IMEIs', route: '/articulos-con-imeis', icon: 'pi pi-fw pi-history', desc: 'Ver histórico de IMEIs' },
      { label: 'Transferir IMEIs', route: '/transferir-imeis', icon: 'pi pi-fw pi-share-alt', desc: 'Transferir IMEIs entre ubicaciones' }
    ]
  },
  {
    title: 'Ventas',
    items: [
      { label: 'Clientes', route: '/clientes', icon: 'pi pi-fw pi-users', desc: 'Gestión de clientes' },
      { label: 'Crear Orden de Venta', route: '/ventas', icon: 'pi pi-fw pi-file', desc: 'Registrar' },
      { label: 'Consultar Orden de Venta', route: '/historico-notas', icon: 'pi pi-fw pi-calendar', desc: 'Histórico' }
    ]
  },
  {
    title: 'Usuarios',
    items: [
      { label: 'Usuarios', route: '/usuarios', icon: 'pi pi-fw pi-users', desc: 'Gestión de usuarios' }
    ]
  },
  {
    title: 'Técnicos',
    items: [
      { label: 'Asignaciones a Técnicos', route: '/calendario-asignaciones', icon: 'pi pi-fw pi-calendar', desc: 'Ver calendario de asignaciones' },
      { label: 'Reportes de Servicio', route: '/consultar-reportes', icon: 'pi pi-fw pi-file-edit', desc: 'Consultar reportes de servicio' }
    ]
  },
  {
    title: 'Cotizaciones',
    items: [
      { label: 'Cotizador', route: '/cotizador', icon: 'pi pi-fw pi-file-edit', desc: 'Generar cotizaciones' },
      { label: 'Consultar Cotizaciones', route: '/consultar-cotizaciones', icon: 'pi pi-fw pi-list', desc: 'Histórico de cotizaciones' }
    ]
  }
];
</script>

<style scoped>
.info-icon {
  display: block;
}
.informacion {
  text-align: center;
  margin: 20px;
}
.panel-title {
  text-align: center;
  /* font-family: 'Montserrat', 'Segoe UI', Arial, sans-serif; */
  font-size: 2.4rem;
  font-weight: 800;
  letter-spacing: 1.5px;
  color: var(--color-title);
  margin-bottom: 2.5rem;
}
.section-group {
  margin-bottom: 2.5rem;
}
.section-header {
  /* display: flex; */
  color: --color-title;
  align-items: center;
  gap: 1.2rem;
  margin-bottom: 1.2rem;
}
.section-header span {
  font-size: 1.35rem;
  font-weight: 800;
  color: var(--color-title);
  letter-spacing: 1px;
  text-align: center;
  width: 100%;
  display: block;
  position: relative;
  margin-bottom: 0.7rem;
}
.section-header span::after {
  content: "";
  display: block;
  margin: 0.5rem auto 0 auto;
  width: 60px;
  height: 3px;
  border-radius: 2px;
  background: linear-gradient(90deg, var(--color-title) 0%, transparent 100%);
  opacity: 0.35;
}
.section-divider {
  flex: 1;
  height: 2px;
  background: linear-gradient(90deg, var(--color-title) 0%, transparent 100%);
  border-radius: 2px;
  opacity: 0.25;
}
.grid-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 32px;
  margin-top: 12px;
}
.info-card {
  background: var(--color-card);
  color: var(--color-text);
  border-radius: 14px;
  box-shadow: 0 4px 24px rgba(25, 118, 210, 0.10);
  padding: 2.2rem 1.5rem 1.5rem 1.5rem;
  cursor: pointer;
  transition: transform 0.18s, box-shadow 0.18s, background 0.18s;
  position: relative;
  min-height: 140px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border: 2.5px solid var(--color-border); /* relieve marcado */
  box-shadow:
    0 2px 8px var(--color-border, #444),
    0 4px 24px rgba(25, 118, 210, 0.10);
  cursor: pointer;
  user-select: none;
  min-height: 100px;
  min-width: 100px; /* Asegura que el área sea suficientemente grande para el dedo */
}
.info-card:hover {
  transform: translateY(-8px) scale(1.03);
  box-shadow:
    0 6px 24px var(--color-border, #444),
    0 8px 32px rgba(25, 118, 210, 0.18);
  background: var(--color-bg);
}
.info-card h2 {
  color: var(--color-title); /* Título de la tarjeta */
  /* font-family: 'Montserrat', 'Segoe UI', Arial, sans-serif; */
  font-weight: 700;
}
.info-desc {
  color: var(--color-text); /* Texto descriptivo */
}
@media (max-width: 700px) {
  .grid-container {
    grid-template-columns: 1fr;
    gap: 18px;
  }
  .info-card {
    padding: 1.2rem 0.7rem;
    min-height: 100px;
  }
}
</style>
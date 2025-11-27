<template>
  <div class="p-3">
    <h2>Tickets</h2>
    <Loader v-if="store.loading"/>
    <table v-else class="p-datatable">
      <thead>
        <tr>
          <th>ID</th>
          <th>Título</th>
          <th>Estado</th>
          <th>Prioridad</th>
          <!-- <th>Reporte</th> -->
          <th>Cliente</th>
          <th>Autor</th>
          <th>Actualizado</th>
          <th>Acciones</th>
        </tr>
      </thead>
      <tbody>
  <tr v-for="t in store.list" :key="t.id">
          <td :data-label="labels.id">{{ t.id }}</td>
          <td :data-label="labels.titulo">{{ t.titulo || '-' }}</td>
          <td :data-label="labels.estado">{{ t.estado }}</td>
          <td :data-label="labels.prioridad">{{ t.prioridad }}</td>
          <td :data-label="labels.cliente">{{ t.cliente || '-' }}</td>
          <td :data-label="labels.autor">{{ t.autor || '-' }}</td>
          <td :data-label="labels.actualizado">{{ (t.updatedAt || t.createdAt || '').replace('T',' ').slice(0,19) }}</td>
          <td :data-label="labels.acciones">
            <router-link :to="`/tickets/${t.id}`" class="p-button p-button-text p-button-sm">Ver</router-link>
            <button class="p-button p-button-text p-button-sm p-button-danger" @click="confirmDelete(t)">Eliminar</button>
            <button class="estado-edit-btn" @click="openEstadoMenu(t)">
              <i class="pi pi-pencil"></i>
            </button>
            <div v-if="estadoMenuTicket && estadoMenuTicket.id === t.id" class="estado-dropdown" @keydown.esc="closeEstadoMenu" tabindex="0">
              <div class="estado-dropdown-header">Cambiar estado</div>
              <ul>
                <li v-for="estado in estadosPosibles" :key="estado">
                  <button @click="setEstado(t, estado)" :class="{'selected': t.estado === estado}">{{ estado }}</button>
                </li>
              </ul>
              <button class="close-btn" @click="closeEstadoMenu">Cerrar</button>
            </div>
          </td>
        </tr>
      </tbody>
    </table>
    <Toast/>
    <ConfirmDialog/>
  </div>
  
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { updateTicket } from '@/services/ticketsService';
const estadosPosibles = ['Abierto', 'En Proceso', 'Resuelto', 'Cancelado'];
const estadoMenuTicket = ref(null);

function openEstadoMenu(ticket) {
  estadoMenuTicket.value = ticket;
  setTimeout(() => {
    const el = document.querySelector('.estado-dropdown');
    if (el) el.focus();
  }, 50);
  document.addEventListener('mousedown', clickOutsideMenu);
}

function closeEstadoMenu() {
  estadoMenuTicket.value = null;
  document.removeEventListener('mousedown', clickOutsideMenu);
}

function clickOutsideMenu(e) {
  const menu = document.querySelector('.estado-dropdown');
  if (menu && !menu.contains(e.target)) {
    closeEstadoMenu();
  }
}

async function setEstado(ticket, nuevoEstado) {
  if (ticket.estado === nuevoEstado) return;
  try {
    await updateTicket(ticket.id, { estado: nuevoEstado });
    ticket.estado = nuevoEstado;
    toast.add({ severity: 'success', summary: 'Estado actualizado', life: 1200 });
    closeEstadoMenu();
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo cambiar el estado', life: 2500 });
  }
}
import { useTicketsStore } from '@/stores/ticketsStore';
import Loader from '@/components/Loader.vue';
import { useToast } from 'primevue/usetoast';
import { useConfirm } from 'primevue/useconfirm';

const store = useTicketsStore();
const toast = useToast();
const confirm = useConfirm();
const labels = {
  id: 'ID',
  titulo: 'Título',
  estado: 'Estado',
  prioridad: 'Prioridad',
  reporte: 'Reporte',
  cliente: 'Cliente',
  actualizado: 'Actualizado',
  autor: 'Autor',
  acciones: 'Acciones'
};

onMounted(async () => {
  try {
    await store.fetch();
    // Rellenar cliente desde contexto si falta en el ticket
    const work = (store.list || []).slice(0, 25); // limitar para no saturar
    for (const t of work) {
      if (!t.clienteNombre && t.reporteId) {
        try {
          const ctx = await store.getContext(t.reporteId);
          if (ctx?.nombre_cliente || ctx?.cliente_nombre) {
            t._ctx_nombre_cliente = ctx.nombre_cliente || ctx.cliente_nombre;
          }
        } catch {}
      }
    }
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error cargando tickets', life: 2500 });
  }
});

function confirmDelete(t) {
  confirm.require({
    message: `¿Eliminar el ticket #${t.id}? Esta acción no se puede deshacer.`,
    header: 'Eliminar ticket',
    icon: 'pi pi-exclamation-triangle',
    acceptLabel: 'Eliminar',
    rejectLabel: 'Cancelar',
    accept: async () => {
      try {
        await store.remove(t.id);
        toast.add({ severity: 'success', summary: 'Ticket eliminado', life: 2000 });
      } catch (e) {
        toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo eliminar', life: 3000 });
      }
    }
  });
}
</script>

<style scoped>
/* Botón para editar estado */
.estado-edit-btn {
  background: #fff;
  border: 1px solid #1976d2;
  color: #1976d2;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin-left: 6px;
  cursor: pointer;
  transition: box-shadow 0.2s;
  box-shadow: 0 1px 4px rgba(25,118,210,0.08);
}
.estado-edit-btn:hover {
  background: #e3f2fd;
  box-shadow: 0 2px 8px rgba(25,118,210,0.12);
}
.estado-dropdown {
  position: absolute;
  z-index: 10;
  min-width: 160px;
  background: #fff;
  border: 1px solid #1976d2;
  border-radius: 10px;
  box-shadow: 0 4px 16px rgba(25,118,210,0.12);
  padding: 0.5rem 1rem 0.8rem 1rem;
  margin-top: 8px;
  right: 0;
}
.estado-dropdown-header {
  font-weight: 600;
  color: #1976d2;
  margin-bottom: 0.5rem;
}
.estado-dropdown ul {
  list-style: none;
  padding: 0;
  margin: 0 0 0.5rem 0;
}
.estado-dropdown li {
  margin-bottom: 0.3rem;
}
.estado-dropdown button {
  background: none;
  border: none;
  color: #1976d2;
  font-weight: 500;
  padding: 4px 0;
  width: 100%;
  text-align: left;
  cursor: pointer;
  border-radius: 4px;
  transition: background 0.15s;
}
.estado-dropdown button.selected {
  background: #e3f2fd;
  color: #1565c0;
}
.estado-dropdown .close-btn {
  background: #f7fafd;
  border: 1px solid #1976d2;
  color: #1976d2;
  border-radius: 6px;
  padding: 4px 12px;
  font-size: 0.95rem;
  margin-top: 0.5rem;
  cursor: pointer;
}
.p-datatable {
  width: 90%;
  border-collapse: collapse;
}
.p-datatable th, .p-datatable td {
  border-bottom: 1px solid var(--color-border);
  padding: 8px 10px;
  text-align: left;
}
/* Centrar ID y Reporte */
.p-datatable th:nth-child(1), .p-datatable td:nth-child(1),
.p-datatable th:nth-child(5), .p-datatable td:nth-child(5) {
  text-align: center;
  white-space: nowrap;
}
/* Forzar una línea en fecha */
.p-datatable th:nth-child(8), .p-datatable td:nth-child(8) {
  white-space: nowrap;
}
/* Alinear acciones a la derecha */
.p-datatable th:last-child, .p-datatable td:last-child {
  text-align: right;
  white-space: nowrap;
}
@media (max-width: 700px) {
  .p-datatable thead { display: none; }
  .p-datatable, .p-datatable tbody, .p-datatable tr, .p-datatable td { display: block; width: 100%; }
  .p-datatable tr { margin-bottom: 12px; border: 1px solid var(--color-border); border-radius: 8px; overflow: hidden; }
  .p-datatable td { display: flex; justify-content: space-between; align-items: center; padding: 10px 12px; }
  .p-datatable td::before {
    content: attr(data-label);
    font-weight: 600;
    color: var(--color-title);
    margin-right: 10px;
  }
}
</style>

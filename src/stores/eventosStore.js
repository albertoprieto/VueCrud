import { defineStore } from 'pinia';

export const useEventosStore = defineStore('eventosStore', {
  state: () => ({
    eventos: []
  }),
  actions: {
    addEvento(evento) {
      const formattedEvento = {
        id: Date.now(),
        title: evento.titulo,
        start: evento.fecha,
        descripcion: evento.descripcion,
        imei: evento.imei,
        technician: evento.technician,
        status: evento.status || 'Pendiente'
      };
      console.log('Evento formateado:', formattedEvento);
      this.eventos.push(formattedEvento);
    },
    updateEvento(updatedEvento) {
      const index = this.eventos.findIndex(e => e.id === updatedEvento.id);
      if (index !== -1) {
        this.eventos[index] = updatedEvento;
      }
    },
    updateStatus(eventoId, status) {
      const index = this.eventos.findIndex(e => e.id === eventoId);
      if (index !== -1) {
        this.eventos[index].status = status;
      }
    },
    deleteEvento(eventoId) {
      this.eventos = this.eventos.filter(e => e.id !== eventoId);
    }
  },
  getters: {
    getEventos: (state) => state.eventos
  }
});
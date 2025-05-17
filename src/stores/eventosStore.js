import { defineStore } from 'pinia';

export const useEventosStore = defineStore('eventos', {
  state: () => ({
    eventos: JSON.parse(localStorage.getItem('eventos')) || []
  }),
  actions: {
    addEvento(evento) {
      const newId = this.eventos.length ? Math.max(...this.eventos.map(e => e.id)) + 1 : 1;
      const newEvento = { ...evento, id: newId };
      this.eventos.push(newEvento);
      localStorage.setItem('eventos', JSON.stringify(this.eventos));
    },
    getEventos() {
      return this.eventos;
    }
  }
});
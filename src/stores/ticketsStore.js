import { defineStore } from 'pinia';
import { getTickets, createTicket, updateTicket, getTicket, addComment, getTicketContextByReporte, deleteTicket } from '@/services/ticketsService';

export const useTicketsStore = defineStore('tickets', {
  state: () => ({
    list: [],
    current: null,
    loading: false,
    counters: { abiertos: 0 }
  }),
  actions: {
    async fetch(params = {}) {
      this.loading = true;
      try {
        const res = await getTickets(params);
        this.list = Array.isArray(res) ? res : [];
        this.counters.abiertos = this.list.filter(t => ['nuevo','en_progreso','en_espera'].includes(t.estado)).length;
      } finally {
        this.loading = false;
      }
    },
    async fetchOne(id) {
      this.loading = true;
      try {
        this.current = await getTicket(id);
        return this.current;
      } finally {
        this.loading = false;
      }
    },
    async create(data) {
      const t = await createTicket(data);
      await this.fetch();
      return t;
    },
    async patch(id, patch) {
      const t = await updateTicket(id, patch);
      await this.fetch();
      return t;
    },
    async comment(id, text) {
      const t = await addComment(id, text);
      await this.fetchOne(id);
      return t;
    },
    async remove(id) {
      const ok = await deleteTicket(id);
      if (!ok) throw new Error('delete_failed');
      await this.fetch();
    },
    async getContext(reporteId) {
      return await getTicketContextByReporte(reporteId);
    }
  }
});

import { defineStore } from 'pinia';

export const useQuotationStore = defineStore('quotationStore', {
  state: () => ({
    quotations: []
  }),
  actions: {
    addQuotation(quotation) {
      this.quotations.push({ ...quotation, status: 'Pendiente' }); // Estado inicial
    },
    updateQuotation(updatedQuotation) {
      const index = this.quotations.findIndex(q => q.id === updatedQuotation.id);
      if (index !== -1) {
        this.quotations[index] = updatedQuotation;
      }
    },
    cancelQuotation(quotationId) {
      const index = this.quotations.findIndex(q => q.id === quotationId);
      if (index !== -1) {
        this.quotations[index].status = 'Cancelado';
      }
    },
    markInProgress(quotationId) {
      const index = this.quotations.findIndex(q => q.id === quotationId);
      if (index !== -1) {
        this.quotations[index].status = 'En Proceso';
      }
    },
    markCompleted(quotationId) {
      const index = this.quotations.findIndex(q => q.id === quotationId);
      if (index !== -1) {
        this.quotations[index].status = 'Concluido';
      }
    }
  },
  getters: {
    getQuotations: (state) => state.quotations,
    getPendingQuotations: (state) => state.quotations.filter(q => q.status === 'Pendiente'),
    getScheduledQuotations: (state) => state.quotations.filter(q => q.status === 'Agendado'),
    getInProgressQuotations: (state) => state.quotations.filter(q => q.status === 'En Proceso'),
    getCompletedQuotations: (state) => state.quotations.filter(q => q.status === 'Concluido')
  }
});
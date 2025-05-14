import { defineStore } from 'pinia';

export const useQuotationStore = defineStore('quotation', {
  state: () => ({
    quotations: JSON.parse(localStorage.getItem('quotations')) || []
  }),
  actions: {
    addQuotation(quotation) {
      const newId = this.quotations.length ? Math.max(...this.quotations.map(q => q.id)) + 1 : 1;
      const newQuotation = { ...quotation, id: newId };
      this.quotations.push(newQuotation);
      localStorage.setItem('quotations', JSON.stringify(this.quotations));
    },
    getQuotations() {
      return this.quotations;
    },
    getQuotationById(id) {
      return this.quotations.find(quotation => quotation.id === id);
    },
    deleteQuotation(id) {
      this.quotations = this.quotations.filter(quotation => quotation.id !== id);
      localStorage.setItem('quotations', JSON.stringify(this.quotations));
    },
    updateQuotation(updatedQuotation) {
      const index = this.quotations.findIndex((q) => q.id === updatedQuotation.id);
      if (index !== -1) {
        this.quotations[index] = updatedQuotation;
        localStorage.setItem('quotations', JSON.stringify(this.quotations));
      }
    }
  }
});
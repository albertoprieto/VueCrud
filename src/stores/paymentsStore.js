import { defineStore } from 'pinia';

export const usePaymentsStore = defineStore('payments', {
  state: () => ({
    payments: []
  }),
  actions: {
    addPayment(payment) {
      const newId = this.payments.length ? Math.max(...this.payments.map(p => p.id)) + 1 : 1;
      this.payments.push({ ...payment, id: newId, date: new Date().toISOString().split('T')[0] });
    },
    getPayments() {
      return this.payments;
    },
    getPaymentById(id) {
      console.log(id,'id',this.payments)
      return this.payments.find(payment => payment.id === id);
    },
    updateStatus(id, status) {
      const payment = this.getPaymentById(id);
      if (payment) {
        payment.status = status;
      }
    }
  }
});
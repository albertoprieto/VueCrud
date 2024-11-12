import { defineStore } from 'pinia';

export const usePurchasesStore = defineStore('purchases', {
  state: () => ({
    purchases: []
  }),
  actions: {
    addPurchase(purchase) {
      this.purchases.push(purchase);
    },
    getPurchases() {
      return this.purchases;
    },
    getPurchaseById(id) {
      return this.purchases.find(purchase => purchase.id === id);
    },
    updateStatus(id, status) {
      const purchase = this.getPurchaseById(id);
      if (purchase) {
        purchase.status = status;
      }
    }
  }
});
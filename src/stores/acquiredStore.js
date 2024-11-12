import { defineStore } from 'pinia';
import { useLoginStore } from './loginStore';

export const useAcquiredStore = defineStore('acquired', {
  state: () => ({
    acquiredItems: {}
  }),
  actions: {
    addItem(item) {
      const loginStore = useLoginStore();
      const username = loginStore.currentUser;
      if (username) {
        if (!this.acquiredItems[username]) {
          this.acquiredItems[username] = [];
        }
        this.acquiredItems[username].push(item);
      } else {
        console.error('User not authenticated');
      }
    },
    removeItem(itemId) {
      const loginStore = useLoginStore();
      const username = loginStore.currentUser;
      if (username && this.acquiredItems[username]) {
        this.acquiredItems[username] = this.acquiredItems[username].filter(item => item.id !== itemId);
      } else {
        console.error('User not authenticated or item not found');
      }
    },
    getItems() {
      const loginStore = useLoginStore();
      const username = loginStore.currentUser;
      if (username) {
        return this.acquiredItems[username] || [];
      } else {
        console.error('User not authenticated');
        return [];
      }
    }
  }
});
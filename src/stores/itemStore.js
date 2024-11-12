import { defineStore } from 'pinia';

export const useItemsStore = defineStore('items', {
  state: () => ({
    items: JSON.parse(localStorage.getItem('items')) || [
      {
        id: 1,
        name: 'Servicio de Agua',
        description: 'Servicio de agua potable',
        price: 200,
        urlpago: '',
        image: 'https://imgs.search.brave.com/I60rVbqvoc0l1o4vl5jQmxPQYlkuMy-HnuKxZZtYupU/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly9jb25j/ZXB0by5kZS93cC1j/b250ZW50L3VwbG9h/ZHMvMjAxOC8wMi9h/Z3VhLWdvdGEtbWlu/LWUxNTE4NzE5OTky/NjcyLTgwMHg0MjEu/anBlZw'
      }
    ]
  }),
  actions: {
    addItem(item) {
      const newId = this.items.length ? Math.max(...this.items.map(i => i.id)) + 1 : 1;
      this.items.push({ ...item, id: newId });
      localStorage.setItem('items', JSON.stringify(this.items));
    },
    updateItem(updatedItem) {
      const index = this.items.findIndex(item => item.id === updatedItem.id);
      if (index !== -1) {
        this.items[index] = updatedItem;
        localStorage.setItem('items', JSON.stringify(this.items));
      }
    },
    deleteItem(id) {
      this.items = this.items.filter(item => item.id !== id);
      localStorage.setItem('items', JSON.stringify(this.items));
    }
  }
});
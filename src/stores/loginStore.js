// stores/userStore.js
import { defineStore } from 'pinia';

export const useLoginStore = defineStore('user', {
  state: () => ({
	currentUser: null,
  }),
  actions: {
	setUser(userObj) {
	  // userObj debe contener al menos username, perfil, id, etc.
	  this.currentUser = userObj;
	},
	logout() {
	  this.currentUser = null;
	  localStorage.removeItem('access_token');
	},
	isAuthenticated() {
	  return !!this.currentUser;
	},
  },
  getters: {
	user: (state) => state.currentUser,
  },
});


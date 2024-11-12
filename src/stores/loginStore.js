// stores/userStore.js
import { defineStore } from 'pinia';

export const useLoginStore = defineStore('user', {
  state: () => ({
	users: [
	  { username: 'admin', password: 'admin123' },
	  { username: '', password: '' }
	],
	currentUser: null,
  }),
  actions: {
	addUser(username, password) {
	  this.users.push({ username, password });
	},
	authenticate(username, password) {
	  const user = this.users.find(
		(user) => user.username === username && user.password === password
	  );
	  if (user) {
		this.setUser(username);
		return true;
	  }
	  return false;
	},
	setUser(username) {
	  this.currentUser = { username };
	},
	logout() {
	  this.currentUser = null;
	},
	isAuthenticated() {
	  return !!this.currentUser;
	},
  },
});


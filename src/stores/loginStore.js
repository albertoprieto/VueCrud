// stores/userStore.js
import { defineStore } from 'pinia';

// Función para restaurar usuario desde localStorage
const getSavedUser = () => {
  try {
    const saved = localStorage.getItem('currentUser');
    return saved ? JSON.parse(saved) : null;
  } catch {
    return null;
  }
};

export const useLoginStore = defineStore('user', {
  state: () => ({
    currentUser: getSavedUser(),
  }),
  actions: {
    setUser(userObj) {
      // userObj debe contener al menos username, perfil, id, etc.
      this.currentUser = userObj;
      if (userObj) {
        localStorage.setItem('currentUser', JSON.stringify(userObj));
      }
    },
    logout() {
      this.currentUser = null;
      localStorage.removeItem('access_token');
      localStorage.removeItem('currentUser');
    },
    isAuthenticated() {
      return !!this.currentUser && !!localStorage.getItem('access_token');
    },
    // Restaurar sesión al iniciar la app
    restoreSession() {
      const token = localStorage.getItem('access_token');
      const user = getSavedUser();
      if (token && user) {
        this.currentUser = user;
        return true;
      }
      return false;
    },
  },
  getters: {
    user: (state) => state.currentUser,
  },
});


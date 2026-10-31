// stores/userStore.js
import { defineStore } from 'pinia';
import { esVigilado } from '@/config/vigilados';

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
        sessionStorage.setItem('sesionActiva', '1');
      }
    },
    logout() {
      this.currentUser = null;
      sessionStorage.removeItem('sesionActiva');
      localStorage.removeItem('access_token');
      localStorage.removeItem('currentUser');
    },
    isAuthenticated() {
      return !!this.currentUser && !!localStorage.getItem('access_token');
    },
    // Restaurar sesión al iniciar la app.
    // Usuarios vigilados: NO se restaura — deben ingresar con contraseña cada
    // vez (así el registro de "cuándo ingresó" es real, no una sesión vieja).
    // Excepción: recarga (F5) dentro de la misma pestaña — sessionStorage
    // sobrevive al F5 pero no a cerrar la pestaña/navegador.
    restoreSession() {
      const token = localStorage.getItem('access_token');
      const user = getSavedUser();
      if (token && user) {
        const impersonando = sessionStorage.getItem('impersonando') === '1';
        if (impersonando) sessionStorage.removeItem('impersonando');
        const mismaPestana = sessionStorage.getItem('sesionActiva') === '1';
        if (esVigilado(user.username) && !impersonando && !mismaPestana) {
          this.logout();
          return false;
        }
        sessionStorage.setItem('sesionActiva', '1');
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


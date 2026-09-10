import { createApp } from 'vue'
import { createPinia } from 'pinia'

//**primevue */
import PrimeVue from 'primevue/config';
import 'primeicons/primeicons.css';
import './assets/theme.css';
import './assets/datatable-small.css';
import './assets/polish.css';
import Aura from '@primevue/themes/aura';
import { definePreset } from '@primevue/themes';

// Un solo acento sobrio (azul pizarra) para TODA la app — PrimeVue y estilos
// propios comparten el mismo `primary`. Adiós al rosa y a los azules sueltos.
const AppPreset = definePreset(Aura, {
  semantic: {
    primary: {
      50:  '#f2f5f7',
      100: '#dde5ea',
      200: '#bccdd7',
      300: '#95afc0',
      400: '#688aa3',
      500: '#3d5568',
      600: '#344758',
      700: '#2b3a48',
      800: '#232f3a',
      900: '#1b242d',
      950: '#111820',
    },
  },
});
import ToastService from 'primevue/toastservice';
import ConfirmationService from 'primevue/confirmationservice';
import App from './App.vue'
import router from './router'

// Importar componentes de PrimeVue
import Button from 'primevue/button';
import Menubar from 'primevue/menubar';
import Toast from 'primevue/toast';
import ConfirmDialog from 'primevue/confirmdialog';
import axios from 'axios';

const app = createApp(App)
app.use(PrimeVue, {
    // Default theme configuration
    theme: {
        preset: AppPreset,
        options: {
            prefix: 'p',
            darkModeSelector: '[data-theme="dark"]',
            cssLayer: false
        }
    }
 });
app.use(ToastService)
app.use(ConfirmationService)
app.component('Button', Button);
app.component('Menubar', Menubar);
app.component('Toast', Toast);
app.component('ConfirmDialog', ConfirmDialog);
app.use(createPinia())
app.use(router)

axios.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});


axios.interceptors.response.use(
  response => response,
  error => {
    if (error.response && (error.response.status === 401 || error.response.status === 403)) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('currentUser');
      router.push('/login');
    }
    return Promise.reject(error);
  }
);
app.mount('#app')
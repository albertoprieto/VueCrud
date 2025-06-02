import { createApp } from 'vue'
import { createPinia } from 'pinia'

//**primevue */
import PrimeVue from 'primevue/config';
import 'primeicons/primeicons.css';
import Aura from '@primevue/themes/aura';
import ToastService from 'primevue/toastservice';
import App from './App.vue'
import router from './router'

// Importar componentes de PrimeVue
import Button from 'primevue/button';
import Menubar from 'primevue/menubar';
import Toast from 'primevue/toast';
import axios from 'axios';

const app = createApp(App)
app.use(PrimeVue, {
    // Default theme configuration
    theme: {
        preset: Aura,
        options: {
            prefix: 'p',
            darkModeSelector: 'system',
            cssLayer: false
        }
    }
 });
app.use(ToastService)
app.component('Button', Button);
app.component('Menubar', Menubar);
app.component('Toast', Toast);
app.use(createPinia())
app.use(router)

axios.interceptors.response.use(
  response => response,
  error => {
    // Si hay error de autenticación o cualquier otro error
    if (error.response && (error.response.status === 401 || error.response.status === 403)) {
      router.push('/login');
    } else if (!error.response) {
      // Error de red u otro error inesperado
      router.push('/login');
    }
    return Promise.reject(error);
  }
);

app.mount('#app')
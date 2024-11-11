import { createApp } from 'vue';
import { createPinia } from 'pinia';

//**primevue */
import PrimeVue from 'primevue/config';
import 'primeicons/primeicons.css';
import '@primevue/resources/themes/saga-blue/theme.css'; // Asegúrate de que el tema esté importado correctamente
import ToastService from 'primevue/toastservice';
import App from './App.vue';
import router from './router';

// Importar componentes de PrimeVue
import Button from 'primevue/button';
import Menubar from 'primevue/menubar';
import Toast from 'primevue/toast';

// Crear la aplicación Vue
const app = createApp(App);

// Usar PrimeVue y otros servicios
app.use(PrimeVue);
app.use(ToastService);
app.use(router);
app.use(createPinia());

// Registrar componentes globalmente
app.component('Button', Button);
app.component('Menubar', Menubar);
app.component('Toast', Toast);

// Montar la aplicación
app.mount('#app');
<template>
  <div style="display: flex; justify-content: center; align-items: center; min-height: 100vh;">
    <Loader v-if="showLoader" />
    <div v-else style="display: flex; flex-direction: column; align-items: center;">
      <h2 style="text-align: center;">Login</h2>
      <div style="margin-bottom: 1rem;">
        <InputText v-model="username" placeholder="Usuario" @keydown.enter="handleSubmit"/>
      </div>
      <div style="margin-bottom: 1rem;">
        <InputText v-model="password" type="password" placeholder="Contraseña" @keydown.enter="handleSubmit"/>
      </div>
      <Button label="Login" @click="handleSubmit" />
      <div v-if="errorMsg" style="color: red; margin-top: 1rem;">{{ errorMsg }}</div>
    </div>
    <Loader v-if="loading && !showLoader" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import InputText from 'primevue/inputtext';
import Button from 'primevue/button';
import { defineEmits } from 'vue';
import { useRouter } from 'vue-router';
import { loginUsuario } from '@/services/userService';
import { useLoginStore } from '@/stores/loginStore';
import Loader from '@/components/Loader.vue';

const router = useRouter();
const emit = defineEmits(['session']);
const username = ref('');
const password = ref('');
const errorMsg = ref('');
const loading = ref(false);
const showLoader = ref(true);
const loginStore = useLoginStore();

onMounted(() => {
  const n = 2;
  const min = 1000;
  const max = 3500;
  const randomDelay = Math.pow(Math.random(), n) * (max - min) + min;
  setTimeout(() => {
    showLoader.value = false;
  }, randomDelay);
});

const handleSubmit = async () => {
  errorMsg.value = '';
  loading.value = true;
  try {
    const result = await loginUsuario(username.value, password.value);
    if (result.access_token) {
      // Guarda el token en localStorage o Pinia
      localStorage.setItem('access_token', result.access_token);
      // Opcional: guarda el tipo de token si lo necesitas
      // localStorage.setItem('token_type', result.token_type);
      emit('session', true);
      router.push('/dashboard');
    } else {
      errorMsg.value = 'Usuario o contraseña incorrectos';
      emit('session', false);
    }
  } catch (e) {
    errorMsg.value = 'Error de conexión o servidor';
    emit('session', false);
  } finally {
    loading.value = false;
  }
};
</script>
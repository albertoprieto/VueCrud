<template>
  <div style="display: flex; justify-content: center; align-items: center; min-height: 100vh;">
    <div style="display: flex; flex-direction: column; align-items: center;">
      <h2 style="text-align: center;">Login</h2>
      <div style="margin-bottom: 1rem;">
        <InputText v-model="username" placeholder="Usuario" :disabled="isGuest" @keydown.enter="handleSubmit"/>
      </div>
      <div style="margin-bottom: 1rem;">
        <InputText v-model="password" type="password" placeholder="Contraseña" :disabled="isGuest" @keydown.enter="handleSubmit"/>
      </div>
      <div style="margin-bottom: 1rem; display: flex; align-items: center;">
        <input type="checkbox" id="guest" v-model="isGuest" @change="handleGuest"/>
        <label for="guest" style="margin-left: 0.5rem;">Ingresar como invitado</label>
      </div>
      <Button label="Login" @click="handleSubmit" />
      <div v-if="errorMsg" style="color: red; margin-top: 1rem;">{{ errorMsg }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import InputText from 'primevue/inputtext';
import Button from 'primevue/button';
import { defineEmits } from 'vue';
import { useRouter } from 'vue-router';
import { loginUsuario } from '@/services/userService';
import { useLoginStore } from '@/stores/loginStore';

const router = useRouter();
const emit = defineEmits(['session']);
const username = ref('');
const password = ref('');
const errorMsg = ref('');
const isGuest = ref(false);
const loginStore = useLoginStore();

const handleGuest = () => {
  if (isGuest.value) {
    username.value = 'INVITADO';
    password.value = '';
    errorMsg.value = '';
  } else {
    username.value = '';
    password.value = '';
  }
};

const handleSubmit = async () => {
  errorMsg.value = '';
  if (isGuest.value) {
    loginStore.setUser('INVITADO');
    emit('session', true);
    router.push('/dashboard');
    return;
  }
  try {
    const result = await loginUsuario(username.value, password.value);
    if (result.success) {
      loginStore.setUser(result.user.username);
      emit('session', true);
      router.push('/dashboard');
    } else {
      errorMsg.value = 'Usuario o contraseña incorrectos';
      emit('session', false);
    }
  } catch (e) {
    errorMsg.value = 'Error de conexión o servidor';
    emit('session', false);
  }
};
</script>
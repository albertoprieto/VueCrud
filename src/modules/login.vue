<template>
  <div style="display: flex; justify-content: center; align-items: center; min-height: 100vh;">
    <div style="display: flex; flex-direction: column; align-items: center;">
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
const loginStore = useLoginStore();

const handleSubmit = async () => {
  errorMsg.value = '';
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
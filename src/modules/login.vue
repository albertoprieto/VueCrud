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
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import InputText from 'primevue/inputtext';
import Button from 'primevue/button';
import { useLoginStore } from '@/stores/loginStore';
import { defineEmits } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();

const emit = defineEmits(['session']);
const username = ref('');
const password = ref('');

const handleSubmit = () => {
  const loginStore = useLoginStore();
  if (loginStore.authenticate(username.value, password.value)) {
    emit('session', true);
    loginStore.setUser(username.value)
    router.push('/dashboard');
  } else {
    emit('session', false);
  }
};
</script>
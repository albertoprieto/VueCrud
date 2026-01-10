<template>
  <div class="datatable-loader-wrapper">
    <div class="datatable-loader-content">
      <!-- Spinner principal con anillos -->
      <div class="loader-rings">
        <div class="ring ring-1"></div>
        <div class="ring ring-2"></div>
        <div class="ring ring-3"></div>
        <div class="ring-center">
          <i class="pi pi-spin pi-cog"></i>
        </div>
      </div>
      
      <!-- Texto animado -->
      <div class="loader-text">
        <span class="loading-word">
          <span v-for="(letter, index) in loadingText" :key="index" 
                class="letter" 
                :style="{ animationDelay: `${index * 0.1}s` }">
            {{ letter }}
          </span>
        </span>
      </div>
      
      <!-- Barra de progreso animada -->
      <div class="progress-bar-container">
        <div class="progress-bar-track">
          <div class="progress-bar-fill"></div>
        </div>
      </div>
      
      <!-- Puntos flotantes decorativos -->
      <div class="floating-dots">
        <span class="dot" v-for="n in 5" :key="n" :style="{ animationDelay: `${n * 0.2}s` }"></span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  text: {
    type: String,
    default: 'Cargando datos...'
  }
});

const loadingText = computed(() => props.text.split(''));
</script>

<style scoped>
.datatable-loader-wrapper {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(var(--surface-ground-rgb, 255, 255, 255), 0.92);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  border-radius: 8px;
}

.datatable-loader-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
}

/* Anillos giratorios */
.loader-rings {
  position: relative;
  width: 100px;
  height: 100px;
}

.ring {
  position: absolute;
  border-radius: 50%;
  border: 3px solid transparent;
}

.ring-1 {
  width: 100%;
  height: 100%;
  border-top-color: var(--primary-color, #6366f1);
  animation: spin 1.5s linear infinite;
}

.ring-2 {
  width: 75%;
  height: 75%;
  top: 12.5%;
  left: 12.5%;
  border-right-color: var(--primary-color, #6366f1);
  border-bottom-color: var(--primary-color, #6366f1);
  animation: spin-reverse 1.2s linear infinite;
}

.ring-3 {
  width: 50%;
  height: 50%;
  top: 25%;
  left: 25%;
  border-left-color: var(--primary-color, #6366f1);
  animation: spin 0.9s linear infinite;
}

.ring-center {
  position: absolute;
  width: 30%;
  height: 30%;
  top: 35%;
  left: 35%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.ring-center i {
  font-size: 1.5rem;
  color: var(--primary-color, #6366f1);
  animation: pulse-icon 1s ease-in-out infinite;
}

/* Animaciones de rotación */
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes spin-reverse {
  0% { transform: rotate(360deg); }
  100% { transform: rotate(0deg); }
}

@keyframes pulse-icon {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.2); opacity: 0.7; }
}

/* Texto animado letra por letra */
.loader-text {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-color, #374151);
  letter-spacing: 0.5px;
}

.loading-word {
  display: flex;
}

.letter {
  display: inline-block;
  animation: bounce-letter 1.4s ease-in-out infinite;
}

@keyframes bounce-letter {
  0%, 60%, 100% { 
    transform: translateY(0); 
    opacity: 1;
  }
  30% { 
    transform: translateY(-8px); 
    opacity: 0.6;
  }
}

/* Barra de progreso */
.progress-bar-container {
  width: 200px;
}

.progress-bar-track {
  height: 4px;
  background: var(--surface-200, #e5e7eb);
  border-radius: 4px;
  overflow: hidden;
}

.progress-bar-fill {
  height: 100%;
  width: 40%;
  background: linear-gradient(90deg, 
    var(--primary-color, #6366f1), 
    var(--primary-400, #818cf8), 
    var(--primary-color, #6366f1)
  );
  background-size: 200% 100%;
  border-radius: 4px;
  animation: progress-slide 1.5s ease-in-out infinite;
}

@keyframes progress-slide {
  0% {
    transform: translateX(-100%);
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    transform: translateX(350%);
    background-position: 0% 50%;
  }
}

/* Puntos flotantes */
.floating-dots {
  display: flex;
  gap: 8px;
  margin-top: 0.5rem;
}

.dot {
  width: 8px;
  height: 8px;
  background: var(--primary-color, #6366f1);
  border-radius: 50%;
  animation: float-dot 1.6s ease-in-out infinite;
}

@keyframes float-dot {
  0%, 100% {
    transform: translateY(0) scale(1);
    opacity: 0.4;
  }
  50% {
    transform: translateY(-12px) scale(1.2);
    opacity: 1;
  }
}

/* Tema oscuro */
:root[data-theme="dark"] .datatable-loader-wrapper,
.p-dark .datatable-loader-wrapper {
  background: rgba(30, 30, 30, 0.92);
}

:root[data-theme="dark"] .progress-bar-track,
.p-dark .progress-bar-track {
  background: rgba(255, 255, 255, 0.1);
}
</style>

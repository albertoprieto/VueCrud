<template>
  <div class="loader-overlay">
    <div class="loader">
      <div class="line" v-for="n in 5" :key="n" :style="{ animationDelay: (n * 0.15) + 's' }"></div>
    </div>
  </div>
</template>

<style scoped>
.loader-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(20, 22, 30, 0.85);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  transition: background 0.4s;
}

.loader {
  display: flex;
  gap: 10px;
  height: 60px;
}

.line {
  width: 8px;
  height: 100%;
  background: linear-gradient(180deg, #3a3f4b 0%, #6e7a8a 100%);
  border-radius: 8px;
  animation: loader-move 1.2s cubic-bezier(0.4,0,0.2,1) infinite;
  box-shadow: 0 0 16px #2e3440, 0 0 4px #6e7a8a;
  transition: background 0.4s;
}

.line:nth-child(1) { background: linear-gradient(180deg, #2e3440 0%, #434c5e 100%); }
.line:nth-child(2) { background: linear-gradient(180deg, #3b4252 0%, #4c566a 100%); }
.line:nth-child(3) { background: linear-gradient(180deg, #434c5e 0%, #6e7a8a 100%); }
.line:nth-child(4) { background: linear-gradient(180deg, #4c566a 0%, #3a3f4b 100%); }
.line:nth-child(5) { background: linear-gradient(180deg, #2e3440 0%, #434c5e 100%); }

@keyframes loader-move {
  0%, 100% { transform: scaleY(0.5); opacity: 0.7; }
  50% { transform: scaleY(1.3); opacity: 1; }
}
</style>
<template>
  <div class="loader-overlay">
    <div class="loader-card">
      <div class="loader-bars">
        <span v-for="n in 5" :key="n" class="bar" :style="{ animationDelay: (n * 0.12) + 's' }"></span>
      </div>
      <div class="loader-label">{{ text }}</div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  text: { type: String, default: 'Cargando' },
});
</script>

<style scoped>
.loader-overlay {
  position: fixed;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  background: color-mix(in srgb, var(--color-bg, #fff) 78%, transparent);
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
  animation: fade-in 0.25s var(--ease, ease);
}

.loader-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.1rem;
  padding: 2rem 2.4rem;
  border-radius: 18px;
  background: var(--color-card, #f7f7fa);
  border: 1px solid var(--color-border, #e6e6e6);
  box-shadow: var(--elev-3, 0 14px 40px rgba(0, 0, 0, 0.16));
}

.loader-bars {
  display: flex;
  gap: 8px;
  height: 52px;
}

.bar {
  width: 8px;
  height: 100%;
  border-radius: 8px;
  background: linear-gradient(
    180deg,
    var(--color-primary, #3d5568),
    color-mix(in srgb, var(--color-primary, #3d5568) 45%, var(--color-title, var(--color-primary)))
  );
  box-shadow: 0 0 14px color-mix(in srgb, var(--color-primary, #3d5568) 55%, transparent);
  animation: bar-wave 1.1s var(--ease, cubic-bezier(0.4, 0, 0.2, 1)) infinite;
}

.loader-label {
  font-family: var(--font-display, sans-serif);
  font-size: 0.9rem;
  font-weight: 600;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--color-text, #333);
  background: linear-gradient(
    90deg,
    color-mix(in srgb, var(--color-text, #333) 35%, transparent),
    var(--color-text, #333),
    color-mix(in srgb, var(--color-text, #333) 35%, transparent)
  );
  background-size: 200% 100%;
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  animation: label-shimmer 2s linear infinite;
}

@keyframes bar-wave {
  0%, 100% { transform: scaleY(0.4); opacity: 0.55; }
  50% { transform: scaleY(1.25); opacity: 1; }
}
@keyframes label-shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

@media (prefers-reduced-motion: reduce) {
  .bar { animation: none; transform: scaleY(0.85); }
  .loader-label { animation: none; -webkit-text-fill-color: var(--color-text, #333); }
}
</style>

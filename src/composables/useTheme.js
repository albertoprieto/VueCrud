import { ref } from 'vue';

// Tema claro/oscuro global. El valor real vive en <html data-theme> (lo fija
// primero un script inline en index.html para evitar parpadeo) y se persiste
// en localStorage. PrimeVue usa el mismo selector, ver main.js.
const CLAVE = 'app-theme';
const tema = ref(leerActual());

function leerActual() {
  if (typeof document === 'undefined') return 'light';
  return document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
}

function aplicar(valor) {
  const v = valor === 'dark' ? 'dark' : 'light';
  tema.value = v;
  document.documentElement.setAttribute('data-theme', v);
  try { localStorage.setItem(CLAVE, v); } catch { /* modo privado */ }
}

function toggleTheme() {
  aplicar(tema.value === 'dark' ? 'light' : 'dark');
}

// Mientras el usuario NO haya elegido tema, la app sigue al sistema en vivo.
if (typeof window !== 'undefined' && window.matchMedia) {
  const mq = window.matchMedia('(prefers-color-scheme: dark)');
  const onChange = (e) => {
    let elegido = null;
    try { elegido = localStorage.getItem(CLAVE); } catch { /* ignore */ }
    if (elegido !== 'light' && elegido !== 'dark') {
      const v = e.matches ? 'dark' : 'light';
      tema.value = v;
      document.documentElement.setAttribute('data-theme', v);
    }
  };
  mq.addEventListener ? mq.addEventListener('change', onChange) : mq.addListener(onChange);
}

export function useTheme() {
  return { tema, toggleTheme };
}

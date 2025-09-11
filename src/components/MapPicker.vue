<template>
  <div class="map-wrapper">
    <div class="search-bar">
      <input
        v-model="searchQuery"
        @input="onSearchInput"
        type="text"
        placeholder="Buscar dirección, ciudad, CP..."
        class="search-input"
      />
      <ul v-if="showResults" class="results">
        <li v-for="r in searchResults" :key="r.place_id" @click="selectResult(r)">
          {{ r.display_name }}
        </li>
        <li v-if="!searchResults.length && !searchLoading">Sin resultados</li>
        <li v-if="searchLoading">Buscando...</li>
      </ul>
    </div>
    <div ref="mapEl" class="map-picker"></div>
    <div class="map-footer" v-if="lat && lng">
      <small>Lat: {{ lat.toFixed(6) }}, Lng: {{ lng.toFixed(6) }}</small>
      <div class="link-preview" v-if="generatedLink">{{ generatedLink }}</div>
    </div>
    <div v-else class="map-hint"><small>Toca / haz click en el mapa para seleccionar ubicación.</small></div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
let L = null; // Se asignará desde CDN

const props = defineProps({
  modelValue: { type: String, default: '' },
  height: { type: String, default: '260px' }
});
const emit = defineEmits(['update:modelValue', 'coords-change', 'place-selected']);

const mapEl = ref(null);
const mapInstance = ref(null);
const marker = ref(null);
const lat = ref(null);
const lng = ref(null);
const generatedLink = ref('');
// Search state
const searchQuery = ref('');
const searchResults = ref([]);
const searchLoading = ref(false);
const showResults = ref(false);
let searchDebounce = null;
let lastSearchTime = 0;

function setCoords(_lat, _lng) {
  lat.value = _lat;
  lng.value = _lng;
  generatedLink.value = `https://www.google.com/maps?q=${_lat},${_lng}`;
  emit('update:modelValue', generatedLink.value);
  emit('coords-change', { lat: _lat, lng: _lng });
}

function loadLeafletViaCDN() {
  return new Promise((resolve, reject) => {
    if (window.L) {
      L = window.L;
      return resolve(L);
    }
    // CSS
    if (!document.querySelector('link[data-leaflet]')) {
      const link = document.createElement('link');
      link.rel = 'stylesheet';
      link.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
      link.setAttribute('data-leaflet','true');
      document.head.appendChild(link);
    }
    // Script
    const script = document.createElement('script');
    script.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
    script.async = true;
    script.onload = () => { L = window.L; resolve(L); };
    script.onerror = (e) => reject(e);
    document.head.appendChild(script);
  });
}

onMounted(async () => {
  await loadLeafletViaCDN();
  try {
    delete L.Icon.Default.prototype._getIconUrl;
    L.Icon.Default.mergeOptions({
      iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
      iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
      shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png'
    });
  } catch (e) {
    console.warn('No se pudo configurar iconos leaflet', e);
  }

  mapInstance.value = L.map(mapEl.value).setView([20.6736, -103.344], 6);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '© OpenStreetMap'
  }).addTo(mapInstance.value);

  mapInstance.value.on('click', e => {
    const { lat: clat, lng: clng } = e.latlng;
    if (marker.value) {
      marker.value.setLatLng(e.latlng);
    } else {
      marker.value = L.marker(e.latlng).addTo(mapInstance.value);
    }
    setCoords(clat, clng);
  });

  if (props.modelValue) {
    const match = props.modelValue.match(/[-+]?\d+\.\d+[, ]+[-+]?\d+\.\d+/);
    if (match) {
      const [ilat, ilng] = match[0].split(/[, ]+/).map(Number);
      setCoords(ilat, ilng);
      mapInstance.value.setView([ilat, ilng], 14);
    }
  }
});

function onSearchInput() {
  showResults.value = !!searchQuery.value;
  if (searchDebounce) clearTimeout(searchDebounce);
  if (!searchQuery.value) { searchResults.value = []; return; }
  searchDebounce = setTimeout(doSearch, 450);
}

async function doSearch() {
  const q = searchQuery.value.trim();
  if (!q) { searchResults.value = []; return; }
  const now = Date.now();
  if (now - lastSearchTime < 800) { // throttle server-friendly
    return;
  }
  lastSearchTime = now;
  searchLoading.value = true;
  // Primero Nominatim jsonv2
  const nominatimUrl = `https://nominatim.openstreetmap.org/search?format=jsonv2&limit=7&addressdetails=1&extratags=1&namedetails=1&accept-language=es&q=${encodeURIComponent(q)}`;
  try {
    const res = await fetch(nominatimUrl, { headers: { 'Accept': 'application/json' } });
    if (!res.ok) throw new Error('HTTP ' + res.status);
    const data = await res.json();
    if (Array.isArray(data) && data.length) {
      searchResults.value = data;
      return;
    }
    // Fallback a Photon si sin resultados
    await photonFallback(q);
  } catch (e) {
    console.warn('[Geocode] Nominatim fallo o vacío, fallback Photon', e);
    await photonFallback(q);
  } finally {
    searchLoading.value = false;
  }
}

async function photonFallback(q) {
  try {
    const url = `https://photon.komoot.io/api/?q=${encodeURIComponent(q)}&limit=7&lang=es`;
    const res = await fetch(url);
    const data = await res.json();
    if (data && Array.isArray(data.features)) {
      searchResults.value = data.features.map(f => ({
        place_id: f.properties.osm_id + '-photon',
        lat: f.geometry.coordinates[1],
        lon: f.geometry.coordinates[0],
        display_name: f.properties.name + (f.properties.city ? ', ' + f.properties.city : ''),
        address: {
          road: f.properties.street || f.properties.name,
          house_number: f.properties.housenumber,
          city: f.properties.city || f.properties.town || f.properties.village,
          state: f.properties.state,
          postcode: f.properties.postcode
        }
      }));
    } else {
      searchResults.value = [];
    }
  } catch (err) {
    console.warn('[Geocode] Photon también falló', err);
    searchResults.value = [];
  }
}

function selectResult(r) {
  showResults.value = false;
  searchResults.value = [];
  searchQuery.value = r.display_name;
  const ilat = parseFloat(r.lat);
  const ilng = parseFloat(r.lon);
  if (!isNaN(ilat) && !isNaN(ilng)) {
    if (mapInstance.value) {
      if (marker.value) marker.value.setLatLng([ilat, ilng]); else marker.value = L.marker([ilat, ilng]).addTo(mapInstance.value);
      mapInstance.value.setView([ilat, ilng], 16);
    }
    setCoords(ilat, ilng);
    const addr = r.address || {};
    const direccionArmada = [addr.road, addr.house_number, addr.suburb, addr.city || addr.town || addr.village, addr.state].filter(Boolean).join(', ');
    emit('place-selected', {
      lat: ilat,
      lng: ilng,
      displayName: r.display_name,
      postcode: addr.postcode || '',
      address: direccionArmada || r.display_name,
      raw: r
    });
  }
}

watch(() => props.modelValue, (val) => {
  if (!val) return;
  if (generatedLink.value === val) return;
  const match = val.match(/[-+]?\d+\.\d+[, ]+[-+]?\d+\.\d+/);
  if (match) {
    const [ilat, ilng] = match[0].split(/[, ]+/).map(Number);
    setCoords(ilat, ilng);
    if (mapInstance.value) mapInstance.value.setView([ilat, ilng], 14);
  }
});
</script>

<style scoped>
.map-wrapper { width: 100%; }
.map-picker { width: 100%; border: 1px solid var(--color-border, #444); border-radius: 8px; height: v-bind(height); }
.map-footer { margin-top: .5rem; font-size: .7rem; opacity: .85; display: flex; flex-direction: column; gap: .25rem; }
.link-preview { font-size: .65rem; word-break: break-all; opacity: .75; }
.map-hint { margin-top: .35rem; font-size: .65rem; opacity: .6; }
.search-bar { position: relative; margin-bottom: .4rem; }
.search-input { width: 100%; padding: .45rem .65rem; border: 1px solid var(--color-border, #444); border-radius: 6px; background: var(--color-card, #222); color: var(--color-text,#eee); font-size: .8rem; }
.results { position: absolute; z-index: 25; top: 100%; left: 0; right: 0; background: var(--color-card,#1e1e1e); border: 1px solid var(--color-border,#444); border-radius: 6px; margin: .25rem 0 0; padding: .25rem 0; max-height: 210px; overflow-y: auto; list-style: none; }
.results li { padding: .4rem .6rem; font-size: .7rem; cursor: pointer; line-height: 1.15; }
.results li:hover { background: rgba(255,255,255,0.08); }
</style>

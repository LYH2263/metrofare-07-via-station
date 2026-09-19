<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, postJSON } from '../api'
const stations = ref([])
const start = ref('A1')
const end = ref('B2')
const via = ref('')
const out = ref(null)
const err = ref('')
onMounted(async () => { stations.value = (await getJSON('/api/stations')).items })
const run = async () => {
  out.value = null
  err.value = ''
  try {
    out.value = await postJSON('/api/quote', { start: start.value, end: end.value, via: via.value || null, persist: true })
  } catch (e) {
    err.value = e.message
    try { const d = JSON.parse(e.message).detail; err.value = (d && d.message) || d || e.message } catch {}
  }
}
</script>
<template>
  <div class="page"><h1>最短站数票价</h1>
    <div class="panel">
      <select v-model="start"><option v-for="s in stations" :key="s.code" :value="s.code">{{ s.name }}</option></select>
      →
      <select v-model="via">
        <option value="">(无必经站)</option>
        <option v-for="s in stations" :key="s.code" :value="s.code">{{ s.name }}</option>
      </select>
      →
      <select v-model="end"><option v-for="s in stations" :key="s.code" :value="s.code">{{ s.name }}</option></select>
      <button @click="run">试算</button>
    </div>
    <p v-if="err" class="muted">{{ err }}</p>
    <div v-if="out" class="panel">
      <template v-if="out.reachable">
        <p>站数 {{ out.hops }} · 票价 <span class="hero-num">¥{{ out.fare }}</span></p>
        <template v-if="out.via">
          <p>第一段 {{ out.segments[0].from }}→{{ out.segments[0].to }} {{ out.segments[0].hops }} 站 · 第二段 {{ out.segments[1].from }}→{{ out.segments[1].to }} {{ out.segments[1].hops }} 站</p>
          <p>途经：{{ out.path.join(' → ') }}</p>
        </template>
      </template>
      <p v-else class="muted">{{ out.error ? out.error.message : '不可达' }}</p>
    </div>
  </div>
</template>

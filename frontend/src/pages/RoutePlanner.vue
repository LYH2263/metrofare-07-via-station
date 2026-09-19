<script setup>
import { computed, onMounted, ref } from 'vue'
import { getJSON, postJSON } from '../api'
const stations = ref([])
const start = ref('A1')
const end = ref('B2')
const via = ref('')
const out = ref(null)
const errorMsg = ref('')
onMounted(async () => { stations.value = (await getJSON('/api/stations')).items })
const nameOf = (code) => stations.value.find(s => s.code === code)?.name ?? code
const legSummary = computed(() => {
  if (!out.value?.reachable) return ''
  return out.value.legs.map((l, i) => `第${i + 1}段 ${l.hops} 站`).join(' · ')
})
const run = async () => {
  errorMsg.value = ''
  out.value = null
  try {
    out.value = await postJSON('/api/quote', {
      start: start.value,
      end: end.value,
      via: via.value || null,
      persist: true,
    })
  } catch (e) {
    // FastAPI error body: {"detail": {"code": ..., "message": ...}}
    try { errorMsg.value = JSON.parse(e.message).detail.message } catch { errorMsg.value = String(e.message) }
  }
}
</script>
<template>
  <div class="page"><h1>最短站数票价</h1>
    <div class="panel planner-row">
      <select v-model="start"><option v-for="s in stations" :key="s.code" :value="s.code">{{ s.name }}</option></select>
      →
      <select v-model="via">
        <option value="">（无必经站）</option>
        <option v-for="s in stations" :key="s.code" :value="s.code">经 {{ s.name }}</option>
      </select>
      →
      <select v-model="end"><option v-for="s in stations" :key="s.code" :value="s.code">{{ s.name }}</option></select>
      <button @click="run">试算</button>
    </div>
    <p v-if="errorMsg" class="panel error-text">{{ errorMsg }}</p>
    <div v-if="out" class="panel">
      <template v-if="out.reachable">
        <p>
          总站数 {{ out.hops }} · 票价 <span class="hero-num">¥{{ out.fare }}</span>
        </p>
        <p v-if="out.via" class="muted">必经站 {{ nameOf(out.via) }}（{{ out.via }}） · {{ legSummary }}</p>
        <p class="route-path">
          <span v-for="(code, i) in out.path" :key="i" class="path-node">
            <span :class="{ 'path-via': out.via && code === out.via }">{{ nameOf(code) }}</span>
            <span v-if="i < out.path.length - 1" class="path-arrow">→</span>
          </span>
        </p>
      </template>
      <p v-else class="muted">不可达</p>
    </div>
  </div>
</template>
<style scoped>
.planner-row { display: flex; gap: 0.5rem; align-items: center; flex-wrap: wrap; }
.route-path { display: flex; flex-wrap: wrap; gap: 0.25rem; align-items: center; }
.path-arrow { color: var(--muted); margin: 0 0.25rem; }
.path-via { color: var(--accent); font-weight: 700; }
.error-text { color: #ff8080; border: 1px solid #ff808055; }
</style>

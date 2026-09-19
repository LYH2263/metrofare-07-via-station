<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
const items = ref([])
onMounted(async () => {
  const rows = (await getJSON('/api/history')).items
  items.value = rows.map(r => {
    let input = {}, result = {}
    try { input = JSON.parse(r.input_json) } catch { /* legacy row */ }
    try { result = JSON.parse(r.result_json) } catch { /* legacy row */ }
    return { ...r, input, result }
  })
})
</script>
<template>
  <div class="page"><h1>试算记录</h1>
    <table>
      <tr v-for="h in items" :key="h.id">
        <td>#{{ h.id }}</td>
        <td>{{ h.created_at }}</td>
        <td>
          <template v-if="h.result && h.result.reachable">
            {{ h.input.start }}
            <template v-if="h.input.via"> → <span class="via-tag">经 {{ h.input.via }}</span></template>
            → {{ h.input.end }}
            · 共 {{ h.result.hops }} 站 · ¥{{ h.result.fare }}
            <div v-if="Array.isArray(h.result.legs) && h.result.legs.length > 1" class="muted">
              <span v-for="(l, i) in h.result.legs" :key="i">第{{ i + 1 }}段 {{ l.hops }} 站<span v-if="i < h.result.legs.length - 1"> · </span></span>
            </div>
            <div v-if="Array.isArray(h.result.path) && h.result.path.length" class="muted path-line">
              {{ h.result.path.join(' → ') }}
            </div>
          </template>
          <span v-else class="muted">不可达</span>
        </td>
      </tr>
    </table>
  </div>
</template>
<style scoped>
.via-tag { color: var(--accent); font-weight: 700; }
.path-line { font-size: 0.85rem; margin-top: 0.15rem; }
td { vertical-align: top; }
</style>

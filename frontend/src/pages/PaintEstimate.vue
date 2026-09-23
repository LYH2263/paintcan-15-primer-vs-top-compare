<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, postJSON } from '../api'
const room_id = ref(1)
const out = ref(null)
const run = async () => { out.value = await postJSON('/api/estimate', { room_id: room_id.value, persist: true }) }

// 底漆 / 面漆对照：同一净面积，仅涂布率遍数不同
const defaults = ref({ coverage: 8, coats: 2 })
onMounted(async () => {
  const s = await getJSON('/api/settings')
  defaults.value = { coverage: Number(s.coverage) || 8, coats: Number(s.coats) || 2 }
  topCov.value = defaults.value.coverage
  topCoats.value = defaults.value.coats
})
const primerCov = ref(10), primerCoats = ref(1)
const topCov = ref(8), topCoats = ref(2)
const cmp = ref(null)
const err = ref('')
const heavierText = (side) => side === 'primer' ? '底漆更费漆' : side === 'topcoat' ? '面漆更费漆' : '两侧持平'
const compare = async () => {
  err.value = ''; cmp.value = null
  try {
    cmp.value = await postJSON('/api/compare', {
      room_id: room_id.value, persist: true,
      primer: { coverage: Number(primerCov.value), coats: Number(primerCoats.value) },
      topcoat: { coverage: Number(topCov.value), coats: Number(topCoats.value) },
    })
  } catch (e) { err.value = '提交被拒绝：涂布率须为正数、遍数须为正整数（整单不写入记录）' }
}
</script>
<template><div class="page"><h1>估漆工作台</h1>
<label>房间ID <input v-model.number="room_id" /></label>
<button @click="run">估算</button>
<p v-if="out">净 {{ out.net_m2 }} m² · {{ out.liters }} 升 · {{ out.coats }} 遍</p>

<hr />
<h2>底漆 / 面漆用量对照</h2>
<p class="hint">同一房间同一净面积，一次提交两侧涂布率与遍数。</p>
<div class="compare-grid">
  <div class="side"><h3>底漆</h3>
    <label>涂布率 m²/L <input v-model.number="primerCov" /></label>
    <label>遍数 <input v-model.number="primerCoats" /></label>
  </div>
  <div class="side"><h3>面漆</h3>
    <label>涂布率 m²/L <input v-model.number="topCov" /></label>
    <label>遍数 <input v-model.number="topCoats" /></label>
  </div>
</div>
<button @click="compare">对照提交</button>
<p class="err" v-if="err">{{ err }}</p>
<div v-if="cmp" class="cmp-out">
  <p>净面积 {{ cmp.net_m2 }} m²（两侧同一口径）</p>
  <table>
    <tr><th>侧</th><th>涂布率</th><th>遍数</th><th>用量</th></tr>
    <tr><td>底漆</td><td>{{ cmp.primer.coverage }}</td><td>{{ cmp.primer.coats }}</td><td>{{ cmp.primer.liters }} 升</td></tr>
    <tr><td>面漆</td><td>{{ cmp.topcoat.coverage }}</td><td>{{ cmp.topcoat.coats }}</td><td>{{ cmp.topcoat.liters }} 升</td></tr>
    <tr><td>差值</td><td colspan="2"></td><td>{{ cmp.diff_liters }} 升</td></tr>
  </table>
  <p class="hero-num">{{ heavierText(cmp.heavier_side) }}</p>
  <p v-if="cmp.run_id" class="hint">已钉选为记录 #{{ cmp.run_id }}（单条，含两侧升数与差）</p>
</div></div></template>
<style scoped>
.compare-grid { display:flex; gap:1rem; margin:0.5rem 0; }
.side { flex:1; border:1px solid #aacce0; padding:0.75rem; }
.side label { display:block; margin:0.35rem 0; }
.side input { width:6em; margin-left:0.4rem; }
.cmp-out { margin-top:1rem; }
.hint { color:#5a7a8a; font-size:0.9rem; }
.err { color:#b03a2e; }
hr { border:0; border-top:1px dashed #aacce0; margin:1.25rem 0; }
</style>

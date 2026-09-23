<script setup>
import { ref } from 'vue'
import { postJSON } from '../api'
const room_id = ref(1)
const out = ref(null)
const run = async () => { out.value = await postJSON('/api/estimate', { room_id: room_id.value, persist: true }) }

// 底漆/面漆对照：一次提交两侧涂布率与遍数
const pCov = ref(10); const pCoats = ref(1)
const tCov = ref(null); const tCoats = ref(null)
const cmp = ref(null)
const err = ref('')
const heavierText = (h) => ({ primer: '底漆更费漆', top: '面漆更费漆', even: '两侧持平' }[h] || h)
const compare = async () => {
  err.value = ''; cmp.value = null
  const body = {
    room_id: room_id.value, persist: true,
    primer_coverage: Number(pCov.value), primer_coats: Number(pCoats.value),
  }
  if (tCov.value !== null && tCov.value !== '') body.top_coverage = Number(tCov.value)
  if (tCoats.value !== null && tCoats.value !== '') body.top_coats = Number(tCoats.value)
  try {
    cmp.value = await postJSON('/api/estimate/compare', body)
  } catch (e) { err.value = e.message }
}
</script>
<template><div class="page">
  <h1>估漆工作台</h1>
  <label>房间ID <input v-model.number="room_id" /></label>
  <button @click="run">估算</button>
  <p v-if="out">净 {{ out.net_m2 }} m² · {{ out.liters }} 升 · {{ out.coats }} 遍</p>

  <h2>底漆 / 面漆用量对照</h2>
  <p class="hint">同一净面积口径，仅涂布率与遍数不同。面漆参数留空则用系统默认值。</p>
  <table>
    <tr><th></th><th>涂布率 (m²/升)</th><th>遍数</th></tr>
    <tr><td>底漆</td><td><input v-model="pCov" /></td><td><input v-model="pCoats" /></td></tr>
    <tr><td>面漆</td><td><input v-model="tCov" placeholder="默认" /></td><td><input v-model="tCoats" placeholder="默认" /></td></tr>
  </table>
  <button @click="compare">提交对照</button>
  <p v-if="err" class="err">整单拒绝：{{ err }}</p>
  <div v-if="cmp" class="cmp">
    <p>净面积 {{ cmp.net_m2 }} m²（两侧共用）</p>
    <table>
      <tr><th></th><th>涂布率</th><th>遍数</th><th>升数</th></tr>
      <tr><td>底漆</td><td>{{ cmp.primer.coverage }}</td><td>{{ cmp.primer.coats }}</td><td>{{ cmp.primer.liters }} 升</td></tr>
      <tr><td>面漆</td><td>{{ cmp.top.coverage }}</td><td>{{ cmp.top.coats }}</td><td>{{ cmp.top.liters }} 升</td></tr>
    </table>
    <p class="hero-num">合计差 {{ cmp.diff_liters }} 升 · {{ heavierText(cmp.heavier_side) }}</p>
    <p class="hint" v-if="cmp.run_id">已钉选为一条记录 #{{ cmp.run_id }}</p>
  </div>
</div></template>

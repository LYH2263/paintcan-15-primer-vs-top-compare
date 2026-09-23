<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
const items = ref([])
const openId = ref(null)
const detail = ref(null)
const toggle = async (id) => {
  if (openId.value === id) { openId.value = null; detail.value = null; return }
  openId.value = id
  detail.value = await getJSON(`/api/history/${id}`)
}
const heavierText = (h) => ({ primer: '底漆更费漆', top: '面漆更费漆', even: '两侧持平' }[h] || h)
onMounted(async () => { items.value = (await getJSON('/api/history')).items })
</script>
<template><div class="page"><h1>估算记录</h1>
<table>
  <tr v-for="h in items" :key="h.id">
    <td><a href="#" @click.prevent="toggle(h.id)">#{{ h.id }}</a></td>
    <td>{{ h.kind }}</td>
    <td>{{ h.created_at }}</td>
  </tr>
</table>
<div v-if="detail" class="cmp">
  <h2>记录 #{{ detail.id }} 钉选结果</h2>
  <template v-if="detail.kind === 'primer_top_compare'">
    <p>房间 {{ detail.input.room_id }} · 净面积 {{ detail.result.net_m2 }} m²（两侧共用）</p>
    <table>
      <tr><th></th><th>涂布率</th><th>遍数</th><th>升数</th></tr>
      <tr><td>底漆</td><td>{{ detail.result.primer.coverage }}</td><td>{{ detail.result.primer.coats }}</td><td>{{ detail.result.primer.liters }} 升</td></tr>
      <tr><td>面漆</td><td>{{ detail.result.top.coverage }}</td><td>{{ detail.result.top.coats }}</td><td>{{ detail.result.top.liters }} 升</td></tr>
    </table>
    <p class="hero-num">合计差 {{ detail.result.diff_liters }} 升 · {{ heavierText(detail.result.heavier_side) }}</p>
  </template>
  <template v-else>
    <pre>{{ detail.result }}</pre>
  </template>
</div>
</div></template>

<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
const items = ref([])
const current = ref(null)
const parseJSON = (t) => { try { return JSON.parse(t) } catch { return null } }
const open = async (id) => { current.value = await getJSON(`/api/history/${id}`) }
const heavierText = (side) => side === 'primer' ? '底漆更费漆' : side === 'topcoat' ? '面漆更费漆' : '两侧持平'
onMounted(async () => { items.value = (await getJSON('/api/history')).items })
</script>
<template><div class="page"><h1>估算记录</h1>
<table><tr v-for="h in items" :key="h.id" class="row" @click="open(h.id)">
  <td>#{{ h.id }}</td><td>{{ h.kind }}</td><td>{{ h.created_at }}</td><td>点击打开</td>
</tr></table>

<div v-if="current" class="detail">
  <h2>记录 #{{ current.id }}（{{ current.kind }}）</h2>
  <p>{{ current.created_at }} · 房间 {{ current.room_id }}</p>
  <template v-if="current.kind === 'compare'">
    <table>
      <tr><th>侧</th><th>涂布率</th><th>遍数</th><th>用量</th></tr>
      <tr><td>底漆</td><td>{{ parseJSON(current.result_json).primer.coverage }}</td>
          <td>{{ parseJSON(current.result_json).primer.coats }}</td>
          <td>{{ parseJSON(current.result_json).primer.liters }} 升</td></tr>
      <tr><td>面漆</td><td>{{ parseJSON(current.result_json).topcoat.coverage }}</td>
          <td>{{ parseJSON(current.result_json).topcoat.coats }}</td>
          <td>{{ parseJSON(current.result_json).topcoat.liters }} 升</td></tr>
      <tr><td>差值</td><td colspan="2"></td><td>{{ parseJSON(current.result_json).diff_liters }} 升</td></tr>
    </table>
    <p class="hero-num">{{ heavierText(parseJSON(current.result_json).heavier_side) }}</p>
    <p class="hint">升数为提交时钉选，随后修改默认涂布率不会改变本条。</p>
  </template>
  <template v-else>
    <pre>{{ current.result_json }}</pre>
  </template>
</div></div></template>
<style scoped>
.row { cursor:pointer; }
.row:hover { background:#eef6fc; }
.detail { margin-top:1.25rem; border-top:2px dashed #aacce0; padding-top:1rem; }
.hint { color:#5a7a8a; }
</style>

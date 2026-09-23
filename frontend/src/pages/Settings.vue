<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, postJSON } from '../api'
const s = ref({})
const coverage = ref('')
const msg = ref('')
const load = async () => { s.value = await getJSON('/api/settings'); coverage.value = s.value.coverage ?? '' }
const save = async () => {
  msg.value = ''
  try {
    s.value = await postJSON('/api/settings/coverage', { coverage: Number(coverage.value) })
    msg.value = '已保存；仅影响此后新提交，旧记录钉选数不变'
  } catch (e) { msg.value = e.message }
}
onMounted(load)
</script>
<template><div class="page"><h1>设置</h1>
  <table>
    <tr><td>面漆默认涂布率 (m²/升)</td><td><input v-model="coverage" /></td><td><button @click="save">保存</button></td></tr>
    <tr><td>默认遍数</td><td>{{ s.coats }}</td><td>（本页只改面漆涂布率）</td></tr>
  </table>
  <p v-if="msg" class="hint">{{ msg }}</p>
  <pre>{{ s }}</pre>
</div></template>

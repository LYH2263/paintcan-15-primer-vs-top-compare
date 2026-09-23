<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, putJSON } from '../api'
const s = ref({})
const coverage = ref(null)
const msg = ref('')
const load = async () => {
  s.value = await getJSON('/api/settings')
  coverage.value = Number(s.value.coverage)
}
const save = async () => {
  msg.value = ''
  try {
    s.value = await putJSON('/api/settings', { coverage: Number(coverage.value) })
    msg.value = '已更新面漆默认涂布率；历史对照的钉选升数不变。'
  } catch { msg.value = '保存失败：涂布率须为正数。' }
}
onMounted(load)
</script>
<template><div class="page"><h1>设置</h1>
<p>面漆默认涂布率 <input v-model.number="coverage" /> m²/L · 默认 {{ s.coats }} 遍</p>
<button @click="save">保存</button>
<p class="hint">{{ msg }}</p></div></template>
<style scoped>.hint { color:#5a7a8a; }</style>

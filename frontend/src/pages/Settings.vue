<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, putJSON } from '../api'

const s = ref({})
const err = ref('')
const busy = ref(false)
const saved = ref(false)
const padPct = ref(8) // 百分比（%）

onMounted(async () => {
  try {
    s.value = await getJSON('/api/settings')
    if (s.value.pad_pct !== undefined) padPct.value = Math.round(Number(s.value.pad_pct) * 1000) / 10
  } catch (e) {
    err.value = String(e.message || e)
  }
})

async function savePadPct() {
  err.value = ''
  saved.value = false
  if (Number(padPct.value) < 0) {
    err.value = '垫层百分比不能为负'
    return
  }
  busy.value = true
  try {
    const r = await putJSON('/api/settings/pad_pct', { pad_pct: Number(padPct.value) / 100 })
    s.value.pad_pct = String(r.pad_pct)
    padPct.value = Math.round(r.pad_pct * 1000) / 10
    saved.value = true
  } catch (e) {
    err.value = String(e.message || e)
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <div class="page">
    <h1>设置</h1>
    <p class="lede">改默认垫层百分比只影响之后的新测算；已写入用纸档的百分比、顺序与面积钉住不变。</p>
    <p v-if="err" class="bad">{{ err }}</p>
    <ul class="item-list">
      <li>
        <span>折边系数 overlap</span>
        <span class="meta">{{ s.overlap }}</span>
      </li>
      <li>
        <span>系统默认垫层百分比</span>
        <span class="meta">
          <input v-model.number="padPct" type="number" min="0" step="0.5" style="width:6rem" /> %
          <button :disabled="busy" @click="savePadPct" style="margin-left:0.5rem;padding:0.35rem 0.7rem">保存</button>
        </span>
      </li>
    </ul>
    <p v-if="saved" class="stat-line"><span class="pill">已保存</span> 历史用纸档不回改。</p>
  </div>
</template>

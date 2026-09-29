<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, postJSON, padOrderLabel, pctLabel } from '../api'
import BoxUnfold from '../components/BoxUnfold.vue'

const boxes = ref([])
const bid = ref(1)
const padEnabled = ref(false)
const padPct = ref(8) // 百分比（%），发送时换算为小数；留空则取系统默认
const useDefaultPct = ref(true)
const defaultPct = ref(null)
const out = ref(null)
const err = ref('')
const busy = ref(false)

onMounted(async () => {
  try {
    boxes.value = (await getJSON('/api/boxes')).items.filter((b) => b.data_quality === 'clean')
    if (boxes.value.length) bid.value = boxes.value[0].id
    const s = await getJSON('/api/settings')
    defaultPct.value = s.pad_pct !== undefined ? Number(s.pad_pct) : null
    if (defaultPct.value !== null) padPct.value = Math.round(defaultPct.value * 1000) / 10
  } catch (e) {
    err.value = String(e.message || e)
  }
})

function body(save) {
  const b = { box_id: bid.value, save, pad_enabled: padEnabled.value }
  if (padEnabled.value && !useDefaultPct.value && padPct.value !== '' && padPct.value !== null) {
    b.pad_pct = Number(padPct.value) / 100
  }
  return b
}

async function go(save) {
  err.value = ''
  busy.value = true
  try {
    out.value = save
      ? await postJSON('/api/estimate', body(true))
      : await postJSON('/api/estimate', body(false))
  } catch (e) {
    out.value = null
    err.value = String(e.message || e)
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <div class="page">
    <h1>算纸</h1>
    <p class="lede">先试算看面积与展开，确认后再写入用纸档。开启防压垫后面积应高于关闭时同盒结果。</p>
    <div class="row">
      <select v-model.number="bid">
        <option v-for="b in boxes" :key="b.id" :value="b.id">{{ b.name }}</option>
      </select>
      <label class="switch">
        <input type="checkbox" v-model="padEnabled" />
        防压垫加纸
      </label>
      <label v-if="padEnabled" class="pct-field">
        <input type="checkbox" v-model="useDefaultPct" />
        用系统默认
        <span v-if="!useDefaultPct" class="pct-input">
          <input v-model.number="padPct" type="number" min="0" step="0.5" style="min-width:0;width:5.5rem" /> %
        </span>
        <span v-else class="meta">（{{ pctLabel(defaultPct) }}）</span>
      </label>
    </div>
    <div class="row">
      <button :disabled="busy" @click="go(false)">试算</button>
      <button class="ribbon" :disabled="busy" @click="go(true)">写入用纸档</button>
    </div>
    <p v-if="err" class="bad">{{ err }}</p>
    <div v-if="out" class="result-board">
      <div class="figure">{{ out.paper_m2 }}<span>m²</span></div>
      <p class="stat-line">
        <span class="pill" v-if="out.pad_enabled">防压垫 {{ pctLabel(out.pad_pct) }} · {{ padOrderLabel(out.pad_order) }}</span>
        <span v-else class="meta">防压垫关闭</span>
      </p>
      <p class="stat-line" v-if="out.ribbon">
        十字丝带约 {{ out.ribbon.ribbon_m ?? out.ribbon }} m（只跟基础三边）
      </p>
      <BoxUnfold
        :l="out.box.length"
        :w="out.box.width"
        :h="out.box.height"
        :paper-m2="out.paper_m2"
      />
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, postJSON, padOrderLabel, pctLabel } from '../api'

const props = defineProps({ id: String })
const run = ref(null)
const err = ref('')
const check = ref(null) // { busy, paper_m2, match }
const checkErr = ref('')

onMounted(async () => {
  try {
    run.value = await getJSON(`/api/runs/${props.id}`)
  } catch (e) {
    err.value = String(e.message || e)
  }
})

// 用写入时钉住的同参（盒、折边、开关、百分比）再干算一次，与回看面积互证。
async function recompute() {
  checkErr.value = ''
  check.value = { busy: true, paper_m2: null, match: false }
  try {
    const r = run.value
    const fresh = await postJSON('/api/estimate', {
      box_id: r.box_id,
      overlap: r.overlap,
      wrap_style: r.result?.ribbon?.wrap_style ?? 'cross',
      save: false,
      pad_enabled: r.pad_enabled,
      pad_pct: r.pad_pct,
    })
    const pinned = r.paper_m2 ?? r.result?.paper_m2
    check.value = { busy: false, paper_m2: fresh.paper_m2, match: Math.abs(fresh.paper_m2 - pinned) < 1e-9 }
  } catch (e) {
    check.value = { busy: false, paper_m2: null, match: false }
    checkErr.value = String(e.message || e)
  }
}
</script>

<template>
  <div class="page">
    <p v-if="err" class="bad">{{ err }}</p>
    <template v-else-if="run">
      <h1>{{ run.box_name }} <span class="meta">#{{ run.id }}</span></h1>
      <p class="lede">回看为写入时钉住的值，不按当前系统默认百分比或默认顺序重抬。</p>
      <ul class="item-list">
        <li><span>最终用纸面积</span><span class="meta">{{ run.paper_m2 ?? run.result?.paper_m2 }} m²</span></li>
        <li><span>防压垫开关</span><span class="meta">{{ run.pad_enabled ? '开启' : '关闭' }}</span></li>
        <li><span>垫层百分比</span><span class="meta">{{ run.pad_enabled ? pctLabel(run.pad_pct) : '—' }}</span></li>
        <li><span>叠乘顺序</span><span class="meta">{{ run.pad_enabled ? padOrderLabel(run.pad_order) : '—' }}</span></li>
        <li><span>折边系数</span><span class="meta">{{ run.overlap }}</span></li>
        <li v-if="run.result?.ribbon"><span>十字丝带</span><span class="meta">{{ run.result.ribbon.ribbon_m }} m（基础三边）</span></li>
      </ul>

      <div class="row" style="margin-top:1.25rem">
        <button :disabled="check?.busy" @click="recompute">同参再干算</button>
        <router-link class="btn ghost" to="/history">返回用纸档</router-link>
      </div>
      <p v-if="checkErr" class="bad">{{ checkErr }}</p>
      <p v-else-if="check && !check.busy" class="stat-line">
        再干算面积 <strong>{{ check.paper_m2 }}</strong> m²；
        <span class="pill" :class="{ warn: !check.match }">{{ check.match ? '与回看一致，互证通过' : '与回看不一致！' }}</span>
      </p>
    </template>
  </div>
</template>

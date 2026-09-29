<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, padOrderLabel, pctLabel } from '../api'

const items = ref([])
const err = ref('')

onMounted(async () => {
  try {
    items.value = (await getJSON('/api/runs')).items
  } catch (e) {
    err.value = String(e.message || e)
  }
})
</script>

<template>
  <div class="page">
    <h1>用纸档</h1>
    <p class="lede">算纸页「写入用纸档」后的落库结果。百分比、叠乘顺序与面积均按写入时钉住，随后改系统默认不回改。</p>
    <p v-if="err" class="bad">{{ err }}</p>
    <p v-else-if="!items.length" class="empty">还没有写入过。先去算纸试一单。</p>
    <ul v-else class="item-list">
      <li v-for="r in items" :key="r.id">
        <router-link :to="`/runs/${r.id}`">{{ r.box_name }} #{{ r.id }}</router-link>
        <span class="meta">
          <span class="pill" v-if="r.pad_enabled">垫 {{ pctLabel(r.pad_pct) }} · {{ padOrderLabel(r.pad_order) }}</span>
          <span v-else>垫关</span>
          · {{ r.paper_m2 ?? r.result?.paper_m2 ?? '—' }} m²
        </span>
      </li>
    </ul>
  </div>
</template>

export async function getJSON(path) {
  const r = await fetch(path)
  if (!r.ok) throw new Error(await r.text())
  return r.json()
}
export async function postJSON(path, body) {
  const r = await fetch(path, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })
  if (!r.ok) throw new Error(await r.text())
  return r.json()
}
export async function putJSON(path, body) {
  const r = await fetch(path, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })
  if (!r.ok) throw new Error(await r.text())
  return r.json()
}

// 叠乘顺序标记 -> 中文口径（与后端引擎 PAD_ORDER 对应）。
export function padOrderLabel(order) {
  if (order === 'fold_then_pad') return '先折边再垫'
  if (order === 'pad_then_fold') return '先垫再折边'
  return '—'
}

export function pctLabel(pct) {
  if (pct === null || pct === undefined) return '—'
  return `${Math.round(pct * 1000) / 10}%`
}

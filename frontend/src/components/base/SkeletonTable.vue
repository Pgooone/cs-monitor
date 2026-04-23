<template>
  <div class="skeleton-table">
    <div class="skeleton-table__header">
      <div
        v-for="n in columns"
        :key="`h-${n}`"
        class="skeleton-table__cell skeleton-table__cell--header"
      >
        <div class="skeleton-line" :style="{ width: `${40 + Math.random() * 40}%` }" />
      </div>
    </div>
    <div v-for="row in rows" :key="`r-${row}`" class="skeleton-table__row">
      <div
        v-for="n in columns"
        :key="`c-${row}-${n}`"
        class="skeleton-table__cell"
      >
        <div class="skeleton-line" :style="{ width: `${30 + Math.random() * 50}%` }" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  rows?: number
  columns?: number
}>(), {
  rows: 6,
  columns: 5,
})
</script>

<style scoped>
.skeleton-table {
  width: 100%;
  border-radius: 0.5rem;
  overflow: hidden;
  background: var(--n-color, #fff);
}
.skeleton-table__header {
  display: grid;
  grid-template-columns: repeat(var(--columns, 5), 1fr);
  gap: 1rem;
  padding: 0.75rem 1rem;
  background: rgba(0, 0, 0, 0.02);
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}
html.dark .skeleton-table__header {
  background: rgba(255, 255, 255, 0.02);
  border-bottom-color: rgba(255, 255, 255, 0.06);
}
.skeleton-table__row {
  display: grid;
  grid-template-columns: repeat(var(--columns, 5), 1fr);
  gap: 1rem;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid rgba(0, 0, 0, 0.04);
}
html.dark .skeleton-table__row {
  border-bottom-color: rgba(255, 255, 255, 0.04);
}
.skeleton-table__cell {
  display: flex;
  align-items: center;
}
.skeleton-line {
  height: 0.875rem;
  border-radius: 0.25rem;
  background: linear-gradient(
    90deg,
    rgba(0, 0, 0, 0.06) 25%,
    rgba(0, 0, 0, 0.10) 50%,
    rgba(0, 0, 0, 0.06) 75%
  );
  background-size: 200% 100%;
  animation: skeleton-shimmer 1.5s infinite;
}
html.dark .skeleton-line {
  background: linear-gradient(
    90deg,
    rgba(255, 255, 255, 0.08) 25%,
    rgba(255, 255, 255, 0.14) 50%,
    rgba(255, 255, 255, 0.08) 75%
  );
  background-size: 200% 100%;
}
@keyframes skeleton-shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
</style>

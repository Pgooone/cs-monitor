<template>
  <div class="skeleton-card-grid">
    <div
      v-for="n in count"
      :key="n"
      class="skeleton-card"
    >
      <div class="skeleton-card__image" />
      <div class="skeleton-card__body">
        <div class="skeleton-line skeleton-line--title" />
        <div class="skeleton-line skeleton-line--subtitle" />
        <div class="skeleton-card__footer">
          <div class="skeleton-line skeleton-line--price" />
          <div class="skeleton-line skeleton-line--badge" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  count?: number
}>(), {
  count: 4,
})
</script>

<style scoped>
.skeleton-card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 1rem;
}
.skeleton-card {
  border-radius: 0.75rem;
  overflow: hidden;
  background: var(--n-color, #fff);
  border: 1px solid rgba(0, 0, 0, 0.06);
}
html.dark .skeleton-card {
  border-color: rgba(255, 255, 255, 0.06);
}
.skeleton-card__image {
  width: 100%;
  height: 140px;
  background: linear-gradient(
    90deg,
    rgba(0, 0, 0, 0.06) 25%,
    rgba(0, 0, 0, 0.10) 50%,
    rgba(0, 0, 0, 0.06) 75%
  );
  background-size: 200% 100%;
  animation: skeleton-shimmer 1.5s infinite;
}
html.dark .skeleton-card__image {
  background: linear-gradient(
    90deg,
    rgba(255, 255, 255, 0.08) 25%,
    rgba(255, 255, 255, 0.14) 50%,
    rgba(255, 255, 255, 0.08) 75%
  );
  background-size: 200% 100%;
}
.skeleton-card__body {
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
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
.skeleton-line--title {
  width: 70%;
}
.skeleton-line--subtitle {
  width: 50%;
}
.skeleton-card__footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 0.25rem;
}
.skeleton-line--price {
  width: 40%;
}
.skeleton-line--badge {
  width: 20%;
}
@keyframes skeleton-shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
</style>

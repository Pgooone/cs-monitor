<template>
  <div class="empty-state" :class="{ 'empty-state--compact': compact }">
    <div class="empty-state__icon">
      <slot name="icon">
        <span class="empty-state__emoji">{{ emoji }}</span>
      </slot>
    </div>
    <div class="empty-state__title">{{ title }}</div>
    <div v-if="description" class="empty-state__desc">{{ description }}</div>
    <div v-if="$slots.action" class="empty-state__action">
      <slot name="action" />
    </div>
  </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  title: string
  description?: string
  emoji?: string
  compact?: boolean
}>(), {
  emoji: '📭',
  compact: false,
})
</script>

<style scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 1rem;
  text-align: center;
  animation: fade-in 240ms ease;
}
.empty-state--compact {
  padding: 2rem 1rem;
}
.empty-state__icon {
  margin-bottom: 1rem;
}
.empty-state__emoji {
  font-size: 4rem;
  opacity: 0.6;
  line-height: 1;
}
.empty-state__title {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: var(--n-text-color-1);
}
.empty-state__desc {
  font-size: 0.875rem;
  color: var(--n-text-color-3);
  margin-bottom: 1.5rem;
  max-width: 320px;
  line-height: 1.5;
}
.empty-state__action {
  display: flex;
  gap: 0.75rem;
}

@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(4px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>

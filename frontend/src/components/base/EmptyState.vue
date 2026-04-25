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
  animation: empty-fade-in 400ms cubic-bezier(0.25, 1, 0.5, 1);
}

.empty-state--compact {
  padding: 2.5rem 1rem;
}

.empty-state__icon {
  margin-bottom: 1.25rem;
  position: relative;
}

.empty-state__icon::before {
  content: '';
  position: absolute;
  inset: -0.75rem;
  border-radius: 50%;
  background: radial-gradient(circle, var(--cs-brand-primary) 0%, transparent 70%);
  opacity: 0.08;
  filter: blur(12px);
}

.empty-state__emoji {
  font-size: 3.5rem;
  line-height: 1;
  display: block;
  position: relative;
  filter: saturate(0.85);
  transition: filter 300ms ease;
}

.empty-state:hover .empty-state__emoji {
  filter: saturate(1);
}

.empty-state__title {
  font-size: 1.125rem;
  font-weight: 600;
  margin-bottom: 0.375rem;
  color: var(--cs-text-primary);
  letter-spacing: -0.01em;
}

.empty-state__desc {
  font-size: 0.875rem;
  color: var(--cs-text-muted);
  margin-bottom: 1.5rem;
  max-width: 320px;
  line-height: 1.6;
}

.empty-state__action {
  display: flex;
  gap: 0.75rem;
}

@keyframes empty-fade-in {
  from {
    opacity: 0;
    transform: translateY(8px) scale(0.98);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}
</style>

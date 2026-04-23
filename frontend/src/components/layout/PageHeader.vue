<template>
  <div class="page-header">
    <div class="page-header__main">
      <nav v-if="breadcrumbs.length > 0" class="page-header__breadcrumb" aria-label="面包屑导航">
        <span
          v-for="(crumb, idx) in breadcrumbs"
          :key="idx"
          class="page-header__crumb"
        >
          <router-link
            v-if="crumb.routeName"
            :to="{ name: crumb.routeName }"
            class="page-header__crumb-link"
          >
            {{ crumb.label }}
          </router-link>
          <span v-else class="page-header__crumb-text">{{ crumb.label }}</span>
          <span v-if="idx < breadcrumbs.length - 1" class="page-header__crumb-sep">/</span>
        </span>
      </nav>
      <h1 class="page-header__title">{{ title }}</h1>
    </div>
    <div v-if="$slots.actions" class="page-header__actions">
      <slot name="actions" />
    </div>
  </div>
</template>

<script setup lang="ts">
interface Breadcrumb {
  label: string
  routeName?: string
}

withDefaults(defineProps<{
  title?: string
  breadcrumbs?: Breadcrumb[]
}>(), {
  breadcrumbs: () => [],
})
</script>

<style scoped>
.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.page-header__breadcrumb {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.75rem;
  color: var(--n-text-color-3);
  margin-bottom: 0.25rem;
}

.page-header__crumb {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
}

.page-header__crumb-link {
  color: var(--n-text-color-3);
  text-decoration: none;
  transition: color 150ms ease;
}

.page-header__crumb-link:hover {
  color: var(--n-primary-color);
}

.page-header__crumb-text {
  color: var(--n-text-color-1);
  font-weight: 500;
}

.page-header__crumb-sep {
  opacity: 0.5;
  margin-left: 0.125rem;
}

.page-header__title {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 700;
  line-height: 1.3;
  color: var(--n-text-color-1);
}

.page-header__actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
  padding-top: 0.25rem;
}

@media (max-width: 639px) {
  .page-header {
    flex-direction: column;
    gap: 0.75rem;
  }
  .page-header__actions {
    width: 100%;
    justify-content: flex-end;
  }
}
</style>

<template>
  <div class="stats">
    <div class="stats__header">
      <div>
        <h2 class="stats__title">市场趋势分析</h2>
        <p class="stats__desc">深度集成 SteamDT 数据，提供多维度的价值趋势可视化。</p>
      </div>
    </div>

    <div class="glass-card stats__placeholder">
      <div class="stats__icon-wrap">
        <LineChart class="stats__icon" />
        <div class="stats__scan-line" />
      </div>
      <p class="stats__text">正在计算市场热力图与 K 线走势...</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { LineChart } from 'lucide-vue-next'
</script>

<style scoped>
.stats {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  max-width: 80rem;
  margin: 0 auto;
}

.stats__title {
  font-size: 1.75rem;
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: -0.02em;
  color: #ffffff;
  margin: 0;
}

.stats__desc {
  color: #94a3b8;
  font-weight: 500;
  font-size: 0.875rem;
  margin: 0.25rem 0 0 0;
}

.stats__placeholder {
  height: 24rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border: 2px dashed #1f1f23;
  position: relative;
  overflow: hidden;
}

.stats__icon-wrap {
  position: relative;
}

.stats__icon {
  width: 4rem;
  height: 4rem;
  color: #94a3b8;
  opacity: 0.1;
  transition: all 700ms;
}

.stats__placeholder:hover .stats__icon {
  opacity: 0.3;
  transform: scale(1.1);
}

.stats__scan-line {
  position: absolute;
  top: 0;
  left: -50px;
  width: 4px;
  height: 100%;
  background: #6366f1;
  animation: scan 3s infinite;
}

@keyframes scan {
  0% { left: -50px; opacity: 0; }
  25% { opacity: 1; }
  75% { opacity: 1; }
  100% { left: calc(100% + 50px); opacity: 0; }
}

.stats__text {
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  font-size: 0.75rem;
  color: #94a3b8;
  margin-top: 1.5rem;
}

/* 浅色模式 */
html:not(.dark) .stats__title { color: #0f172a; }
html:not(.dark) .stats__desc { color: #64748b; }
html:not(.dark) .stats__placeholder { border-color: #e2e8f0; }
</style>

<template>
  <div class="skeleton-chart">
    <div class="skeleton-chart__header">
      <div class="skeleton-line skeleton-line--title" />
      <div class="skeleton-line skeleton-line--action" />
    </div>
    <div class="skeleton-chart__body">
      <div class="skeleton-chart__y-axis">
        <div v-for="n in 5" :key="`y-${n}`" class="skeleton-line skeleton-line--y" />
      </div>
      <div class="skeleton-chart__area">
        <svg width="100%" height="100%" preserveAspectRatio="none">
          <defs>
            <linearGradient id="skeletonChartGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stop-color="rgba(0,0,0,0.08)" />
              <stop offset="100%" stop-color="rgba(0,0,0,0.02)" />
            </linearGradient>
            <linearGradient id="skeletonChartGradDark" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stop-color="rgba(255,255,255,0.10)" />
              <stop offset="100%" stop-color="rgba(255,255,255,0.03)" />
            </linearGradient>
          </defs>
          <path
            class="skeleton-chart__path"
            d="M0,80 Q50,60 100,70 T200,50 T300,60 T400,40 T500,55 T600,30 T700,45 T800,35 T900,50 T1000,40 V120 H0 Z"
          />
        </svg>
      </div>
    </div>
    <div class="skeleton-chart__x-axis">
      <div v-for="n in 6" :key="`x-${n}`" class="skeleton-line skeleton-line--x" />
    </div>
  </div>
</template>

<style scoped>
.skeleton-chart {
  width: 100%;
  padding: 1rem;
  border-radius: 0.75rem;
  background: var(--n-color, #fff);
  border: 1px solid rgba(0, 0, 0, 0.06);
}
html.dark .skeleton-chart {
  border-color: rgba(255, 255, 255, 0.06);
}
.skeleton-chart__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
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
  width: 30%;
}
.skeleton-line--action {
  width: 15%;
}
.skeleton-chart__body {
  display: flex;
  height: 200px;
  gap: 0.5rem;
}
.skeleton-chart__y-axis {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  width: 40px;
  flex-shrink: 0;
}
.skeleton-line--y {
  height: 0.5rem;
  width: 60%;
}
.skeleton-chart__area {
  flex: 1;
  position: relative;
  border-left: 1px solid rgba(0, 0, 0, 0.06);
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}
html.dark .skeleton-chart__area {
  border-left-color: rgba(255, 255, 255, 0.06);
  border-bottom-color: rgba(255, 255, 255, 0.06);
}
.skeleton-chart__path {
  fill: url(#skeletonChartGrad);
  animation: skeleton-shimmer 1.5s infinite;
}
html.dark .skeleton-chart__path {
  fill: url(#skeletonChartGradDark);
}
.skeleton-chart__x-axis {
  display: flex;
  justify-content: space-between;
  margin-top: 0.5rem;
  padding-left: 48px;
}
.skeleton-line--x {
  height: 0.5rem;
  width: 12%;
}
@keyframes skeleton-shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
</style>

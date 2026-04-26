/**
 * ECharts 自定义主题 — Trading Terminal Pro
 *
 * 注册名为 'cs-monitor' 的 ECharts 主题，包含 light / dark 两套变体。
 * 参考专业交易终端的图表风格：极简网格、精细坐标轴、玻璃拟态 tooltip
 */

import { registerTheme } from 'echarts/core'
import { chartColors, neutral, fontFamily } from '@/styles/tokens'

const csMonitorLight = {
  color: [...chartColors],
  backgroundColor: 'transparent',
  textStyle: {
    fontFamily: fontFamily.mono,
    color: neutral.light[500],
    fontSize: 11,
  },
  title: {
    textStyle: { color: neutral.light[900], fontFamily: fontFamily.sans, fontWeight: 600, fontSize: 14 },
    subtextStyle: { color: neutral.light[400], fontFamily: fontFamily.sans, fontSize: 12 },
  },
  line: {
    smooth: true,
    symbol: 'none',
    lineStyle: { width: 2 },
    areaStyle: { opacity: 0.06 },
  },
  bar: {
    barMaxWidth: 32,
    itemStyle: { borderRadius: [3, 3, 0, 0] },
  },
  categoryAxis: {
    axisLine: { show: true, lineStyle: { color: neutral.light[200], width: 1 } },
    axisTick: { show: false },
    axisLabel: { color: neutral.light[400], fontSize: 11, fontFamily: fontFamily.mono },
    splitLine: { show: false },
  },
  valueAxis: {
    axisLine: { show: false },
    axisTick: { show: false },
    axisLabel: { color: neutral.light[400], fontSize: 11, fontFamily: fontFamily.mono },
    splitLine: { show: true, lineStyle: { color: neutral.light[100], type: [4, 4] } },
  },
  tooltip: {
    backgroundColor: 'rgba(255, 255, 255, 0.95)',
    borderColor: neutral.light[200],
    borderWidth: 1,
    textStyle: { color: neutral.light[800], fontSize: 12, fontFamily: fontFamily.sans },
    extraCssText: 'backdrop-filter: blur(12px) saturate(1.2); box-shadow: 0 8px 32px rgba(0,0,0,0.1); border-radius: 10px; padding: 10px 14px;',
  },
  grid: {
    left: '2%',
    right: '3%',
    bottom: '2%',
    top: '8%',
    containLabel: true,
  },
  legend: {
    textStyle: { color: neutral.light[500], fontSize: 11, fontFamily: fontFamily.sans },
    pageTextStyle: { color: neutral.light[500] },
    itemGap: 16,
    itemWidth: 14,
    itemHeight: 8,
  },
  dataZoom: {
    textStyle: { color: neutral.light[400] },
    handleStyle: { color: '#4a5cf2', borderColor: '#4a5cf2' },
    fillerColor: 'rgba(74, 92, 242, 0.08)',
    borderColor: 'transparent',
    backgroundColor: neutral.light[50],
    dataBackground: {
      lineStyle: { color: neutral.light[300] },
      areaStyle: { color: neutral.light[100] },
    },
  },
  visualMap: {
    textStyle: { color: neutral.light[500] },
  },
}

const csMonitorDark = {
  color: [...chartColors],
  backgroundColor: 'transparent',
  textStyle: {
    fontFamily: fontFamily.mono,
    color: neutral.dark[500],
    fontSize: 11,
  },
  title: {
    textStyle: { color: neutral.dark[900], fontFamily: fontFamily.sans, fontWeight: 600, fontSize: 14 },
    subtextStyle: { color: neutral.dark[400], fontFamily: fontFamily.sans, fontSize: 12 },
  },
  line: {
    smooth: true,
    symbol: 'none',
    lineStyle: { width: 2 },
    areaStyle: { opacity: 0.08 },
  },
  bar: {
    barMaxWidth: 32,
    itemStyle: { borderRadius: [3, 3, 0, 0] },
  },
  categoryAxis: {
    axisLine: { show: true, lineStyle: { color: 'rgba(255,255,255,0.06)', width: 1 } },
    axisTick: { show: false },
    axisLabel: { color: neutral.dark[400], fontSize: 11, fontFamily: fontFamily.mono },
    splitLine: { show: false },
  },
  valueAxis: {
    axisLine: { show: false },
    axisTick: { show: false },
    axisLabel: { color: neutral.dark[400], fontSize: 11, fontFamily: fontFamily.mono },
    splitLine: { show: true, lineStyle: { color: 'rgba(255,255,255,0.04)', type: [4, 4] } },
  },
  tooltip: {
    backgroundColor: 'rgba(13, 19, 32, 0.95)',
    borderColor: 'rgba(255,255,255,0.08)',
    borderWidth: 1,
    textStyle: { color: neutral.dark[800], fontSize: 12, fontFamily: fontFamily.sans },
    extraCssText: 'backdrop-filter: blur(16px) saturate(1.2); box-shadow: 0 8px 32px rgba(0,0,0,0.4); border-radius: 10px; padding: 10px 14px;',
  },
  grid: {
    left: '2%',
    right: '3%',
    bottom: '2%',
    top: '8%',
    containLabel: true,
  },
  legend: {
    textStyle: { color: neutral.dark[500], fontSize: 11, fontFamily: fontFamily.sans },
    pageTextStyle: { color: neutral.dark[500] },
    itemGap: 16,
    itemWidth: 14,
    itemHeight: 8,
  },
  dataZoom: {
    textStyle: { color: neutral.dark[400] },
    handleStyle: { color: '#6b7ff8', borderColor: '#6b7ff8' },
    fillerColor: 'rgba(107, 127, 248, 0.1)',
    borderColor: 'transparent',
    backgroundColor: 'rgba(255,255,255,0.02)',
    dataBackground: {
      lineStyle: { color: 'rgba(255,255,255,0.1)' },
      areaStyle: { color: 'rgba(255,255,255,0.03)' },
    },
  },
  visualMap: {
    textStyle: { color: neutral.dark[500] },
  },
}

export function registerCsMonitorThemes() {
  registerTheme('cs-monitor-light', csMonitorLight)
  registerTheme('cs-monitor-dark', csMonitorDark)
}

export function getChartTheme(isDark: boolean): string {
  return isDark ? 'cs-monitor-dark' : 'cs-monitor-light'
}

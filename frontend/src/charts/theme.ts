/**
 * ECharts 自定义主题注册
 *
 * 注册名为 'cs-monitor' 的 ECharts 主题，包含 light / dark 两套变体。
 * 按需引入 ECharts 时必须先调用 registerTheme。
 */

import { registerTheme } from 'echarts/core'
import { chartColors, brand, neutral, fontFamily } from '@/styles/tokens'

const csMonitorLight = {
  color: [...chartColors],
  backgroundColor: 'transparent',
  textStyle: {
    fontFamily: fontFamily.sans,
    color: neutral.light[700],
  },
  title: {
    textStyle: { color: neutral.light[900] },
    subtextStyle: { color: neutral.light[500] },
  },
  line: {
    smooth: true,
    symbol: 'none',
  },
  categoryAxis: {
    axisLine: { show: true, lineStyle: { color: neutral.light[300] } },
    axisTick: { show: false },
    axisLabel: { color: neutral.light[500] },
    splitLine: { show: true, lineStyle: { color: neutral.light[100], type: 'dashed' } },
  },
  valueAxis: {
    axisLine: { show: false },
    axisTick: { show: false },
    axisLabel: { color: neutral.light[500] },
    splitLine: { show: true, lineStyle: { color: neutral.light[100], type: 'dashed' } },
  },
  tooltip: {
    backgroundColor: 'rgba(255, 255, 255, 0.92)',
    borderColor: neutral.light[200],
    borderWidth: 1,
    textStyle: { color: neutral.light[900] },
    extraCssText: 'backdrop-filter: blur(8px); box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.15); border-radius: 8px;',
    padding: [12, 16],
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    top: '10%',
    containLabel: true,
  },
  legend: {
    textStyle: { color: neutral.light[600] },
    pageTextStyle: { color: neutral.light[600] },
  },
  dataZoom: {
    textStyle: { color: neutral.light[500] },
    handleStyle: { color: brand[500] },
    fillerColor: 'rgba(59, 130, 246, 0.1)',
    borderColor: 'transparent',
    backgroundColor: neutral.light[100],
  },
  visualMap: {
    textStyle: { color: neutral.light[600] },
  },
}

const csMonitorDark = {
  color: [...chartColors],
  backgroundColor: 'transparent',
  textStyle: {
    fontFamily: fontFamily.sans,
    color: neutral.dark[700],
  },
  title: {
    textStyle: { color: neutral.dark[900] },
    subtextStyle: { color: neutral.dark[500] },
  },
  line: {
    smooth: true,
    symbol: 'none',
  },
  categoryAxis: {
    axisLine: { show: true, lineStyle: { color: neutral.dark[300] } },
    axisTick: { show: false },
    axisLabel: { color: neutral.dark[500] },
    splitLine: { show: true, lineStyle: { color: neutral.dark[200], type: 'dashed' } },
  },
  valueAxis: {
    axisLine: { show: false },
    axisTick: { show: false },
    axisLabel: { color: neutral.dark[500] },
    splitLine: { show: true, lineStyle: { color: neutral.dark[200], type: 'dashed' } },
  },
  tooltip: {
    backgroundColor: 'rgba(23, 23, 23, 0.92)',
    borderColor: neutral.dark[300],
    borderWidth: 1,
    textStyle: { color: neutral.dark[900] },
    extraCssText: 'backdrop-filter: blur(8px); box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.35); border-radius: 8px;',
    padding: [12, 16],
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    top: '10%',
    containLabel: true,
  },
  legend: {
    textStyle: { color: neutral.dark[600] },
    pageTextStyle: { color: neutral.dark[600] },
  },
  dataZoom: {
    textStyle: { color: neutral.dark[500] },
    handleStyle: { color: brand[400] },
    fillerColor: 'rgba(96, 165, 250, 0.15)',
    borderColor: 'transparent',
    backgroundColor: neutral.dark[100],
  },
  visualMap: {
    textStyle: { color: neutral.dark[600] },
  },
}

export function registerCsMonitorThemes() {
  registerTheme('cs-monitor-light', csMonitorLight)
  registerTheme('cs-monitor-dark', csMonitorDark)
}

export function getChartTheme(isDark: boolean): string {
  return isDark ? 'cs-monitor-dark' : 'cs-monitor-light'
}

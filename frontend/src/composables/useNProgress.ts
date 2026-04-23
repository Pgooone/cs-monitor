/**
 * useNProgress — 顶部加载条封装
 *
 * 路由切换时自动显隐，支持手动控制。
 */

import NProgress from 'nprogress'
import 'nprogress/nprogress.css'

// 自定义样式覆盖（品牌色 + 细条）
const style = document.createElement('style')
style.textContent = `
  #nprogress .bar {
    background: #3b82f6 !important;
    height: 2px !important;
  }
  #nprogress .peg {
    box-shadow: 0 0 10px #3b82f6, 0 0 5px #3b82f6 !important;
  }
  html.dark #nprogress .bar {
    background: #60a5fa !important;
  }
  html.dark #nprogress .peg {
    box-shadow: 0 0 10px #60a5fa, 0 0 5px #60a5fa !important;
  }
`
document.head.appendChild(style)

NProgress.configure({
  showSpinner: false,
  trickleSpeed: 200,
  minimum: 0.08,
})

export function useNProgress() {
  function start() {
    NProgress.start()
  }

  function done() {
    NProgress.done()
  }

  return { start, done }
}

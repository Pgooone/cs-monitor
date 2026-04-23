/**
 * useToast — 全局消息反馈封装
 *
 * 基于 naive-ui createDiscreteApi，支持在任意位置（包括拦截器、store）调用，
 * 无需 NMessageProvider 包裹。
 */

import { createDiscreteApi } from 'naive-ui'
const { message } = createDiscreteApi(['message'])

export function toastSuccess(content: string, duration = 3000) {
  message.success(content, { duration })
}

export function toastError(content: string, duration = 4000) {
  message.error(content, { duration })
}

export function toastWarning(content: string, duration = 3000) {
  message.warning(content, { duration })
}

export function toastInfo(content: string, duration = 3000) {
  message.info(content, { duration })
}

export function useToast() {
  return {
    success: toastSuccess,
    error: toastError,
    warning: toastWarning,
    info: toastInfo,
  }
}

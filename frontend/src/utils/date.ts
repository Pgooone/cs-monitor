/**
 * 将后端返回的 UTC 时间字符串转换为本地时区显示
 * 后端格式: '2026-04-28 15:48:42'（无时区标记，实际为 UTC）
 */
export function formatUTCToLocal(
  dateStr: string | null | undefined,
  options?: Intl.DateTimeFormatOptions
): string {
  if (!dateStr || dateStr === '-') return '-'

  // 显式将字符串按 UTC 解析（追加 'Z' 后缀）
  const utcDate = new Date(dateStr + 'Z')
  if (isNaN(utcDate.getTime())) return dateStr

  return utcDate.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
    ...options,
  })
}

/** 仅显示日期部分 */
export function formatUTCDate(dateStr: string | null | undefined): string {
  return formatUTCToLocal(dateStr, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: undefined,
    minute: undefined,
    second: undefined,
  })
}

/** 仅显示时间部分 */
export function formatUTCTime(dateStr: string | null | undefined): string {
  return formatUTCToLocal(dateStr, {
    year: undefined,
    month: undefined,
    day: undefined,
    hour: '2-digit',
    minute: '2-digit',
    second: undefined,
  })
}

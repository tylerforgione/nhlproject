import { requestJson } from './client'
import type { CurrentContext } from './types'

export async function getCurrentContext(): Promise<CurrentContext> {
  return requestJson<CurrentContext>('/api/v1/current-context')
}

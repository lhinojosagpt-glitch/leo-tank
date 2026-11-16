export const DISPLAY_TANK_TAG = 'T-160MB'
export const DISPLAY_TANK_NAME = 'Tanque T-160MB'
export const DISPLAY_PROFILE = 'API650_12E_T160MB'

/**
 * Rebrands legacy T-78 identifiers only at the presentation boundary.
 * Calculation/formula IDs remain unchanged for audit compatibility.
 */
export function displayIdentity(value: unknown): string {
  return String(value ?? '')
    .replaceAll('API650_12E_T78', DISPLAY_PROFILE)
    .replaceAll('T78_2019', 'T160MB_2019')
    .replace(/T[- ]?78/gi, DISPLAY_TANK_TAG)
}

export function applyProjectIdentity<T extends Record<string, any>>(source: T): T {
  return {
    ...source,
    project: {
      ...source.project,
      tank_tag: DISPLAY_TANK_TAG,
      name: DISPLAY_TANK_NAME,
    },
  }
}

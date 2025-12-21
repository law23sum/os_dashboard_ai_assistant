/**
 * Compatibility shim for restored pages under `src/pages/**` that import `../types`.
 * The canonical types live elsewhere; for now, keep these pages type-safe enough to compile.
 */

export type JsonValue = null | boolean | number | string | JsonValue[] | { [key: string]: JsonValue }

export type Project = Record<string, unknown>
export type Metric = Record<string, unknown>
export type Artifact = Record<string, unknown>





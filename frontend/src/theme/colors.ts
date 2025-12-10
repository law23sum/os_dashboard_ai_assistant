/**
 * Theme colors inspired by Tkinter GUI palette
 * Exact match from assistant_hub_gui/assistant_hub/gui.py _build_color_palette()
 * These colors ensure visual consistency between Tkinter and React surfaces
 */

export const darkTheme = {
  background: '#030713',      // Deep navy background
  surface: '#0f172a',          // Primary surface (cards, panels)
  surfaceAlt: '#18223d',       // Secondary surface (alternate cards)
  border: 'rgba(79, 172, 254, 0.25)', // Borders and dividers
  text: '#f8fafc',              // Primary text (light)
  muted: '#9fb0d3',             // Secondary text, placeholders
  accent: '#4facfe',            // Primary accent (indigo/teal gradient)
  accentHover: '#2563eb',      // Accent hover state (blue)
  pill: 'rgba(24, 34, 61, 0.85)', // Pill/badge background
  // Additional semantic colors (matching Tkinter bootstyle colors)
  success: '#10b981',          // Success/green (matches bootstyle="success")
  error: '#ef4444',             // Error/red
  warning: '#f59e0b',           // Warning/amber
  info: '#3b82f6',              // Info/blue (matches bootstyle="info")
  // Tkinter-specific colors
  primary: '#4facfe',           // Primary button color
  secondary: '#667eea',         // Secondary button color
} as const

export const lightTheme = {
  background: '#f4f6fb',       // Light background
  surface: '#ffffff',           // White surface
  surfaceAlt: '#f7f9fd',        // Light alternate surface
  border: '#dfe3eb',            // Light border
  text: '#1f2937',              // Dark text
  muted: '#64748b',             // Muted text
  accent: '#6366f1',            // Indigo accent
  accentHover: '#4f46e5',       // Darker indigo on hover
  pill: '#edf2ff',              // Light pill background
  // Additional semantic colors
  success: '#10b981',
  error: '#ef4444',
  warning: '#f59e0b',
  info: '#3b82f6',
  // Tkinter-specific colors
  primary: '#6366f1',
  secondary: '#64748b',
} as const

export type ThemeColors = typeof darkTheme

export const getTheme = (isDark: boolean): ThemeColors => {
  return isDark ? darkTheme : lightTheme
}

// Export theme tokens for CSS variable mapping
export const themeTokens = {
  dark: darkTheme,
  light: lightTheme,
} as const

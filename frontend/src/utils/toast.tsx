/**
 * Simple toast notification system (replacement for react-hot-toast)
 * No external dependencies required
 */

import React from 'react';
import { createRoot, Root } from 'react-dom/client';

export type ToastType = 'success' | 'error' | 'info';

interface ToastOptions {
  duration?: number;
  position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left';
}

let toastContainer: HTMLDivElement | null = null;
let toastRoot: Root | null = null;
let globalPosition: ToastOptions['position'] = 'bottom-right';

function ensureContainer(): HTMLDivElement {
  if (!toastContainer) {
    toastContainer = document.createElement('div');
    toastContainer.id = 'toast-container';
    toastContainer.style.cssText = `
      position: fixed;
      z-index: 10000;
      pointer-events: none;
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
    `;
    document.body.appendChild(toastContainer);
    toastRoot = createRoot(toastContainer);
  }
  return toastContainer;
}

function getPositionStyles(position: ToastOptions['position'] = 'bottom-right'): string {
  const positions = {
    'top-right': 'top: 1rem; right: 1rem;',
    'top-left': 'top: 1rem; left: 1rem;',
    'bottom-right': 'bottom: 1rem; right: 1rem;',
    'bottom-left': 'bottom: 1rem; left: 1rem;',
  };
  return positions[position];
}

function ToastMessage({ message, type, onClose }: { message: string; type: ToastType; onClose: () => void }) {
  const colors = {
    success: '#10b981',
    error: '#ef4444',
    info: '#3b82f6',
  };

  return (
    <div
      style={{
        backgroundColor: '#1e293b',
        color: '#f8fafc',
        padding: '0.75rem 1rem',
        borderRadius: '0.5rem',
        border: `1px solid ${colors[type]}`,
        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.3)',
        pointerEvents: 'auto',
        display: 'flex',
        alignItems: 'center',
        gap: '0.75rem',
        maxWidth: '400px',
        animation: 'slideIn 0.2s ease-out',
      }}
    >
      <div
        style={{
          width: '4px',
          height: '100%',
          backgroundColor: colors[type],
          borderRadius: '2px',
          flexShrink: 0,
        }}
      />
      <span style={{ flex: 1 }}>{message}</span>
      <button
        onClick={onClose}
        style={{
          background: 'none',
          border: 'none',
          color: '#94a3b8',
          cursor: 'pointer',
          padding: '0.25rem',
          fontSize: '1.25rem',
          lineHeight: 1,
        }}
      >
        ×
      </button>
      <style>{`
        @keyframes slideIn {
          from {
            opacity: 0;
            transform: translateY(10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
      `}</style>
    </div>
  );
}

interface ToastInstance {
  id: string;
  message: string;
  type: ToastType;
  timeoutId: number;
}

let toasts: ToastInstance[] = [];

function renderToasts() {
  const container = ensureContainer();
  container.style.cssText += getPositionStyles(globalPosition);

  if (!toastRoot) return;

  toastRoot.render(
    <>
      {toasts.map((toast) => (
        <ToastMessage
          key={toast.id}
          message={toast.message}
          type={toast.type}
          onClose={() => removeToast(toast.id)}
        />
      ))}
    </>
  );
}

function removeToast(id: string) {
  const toast = toasts.find((t) => t.id === id);
  if (toast) {
    clearTimeout(toast.timeoutId);
    toasts = toasts.filter((t) => t.id !== id);
    renderToasts();
  }
}

function showToast(message: string, type: ToastType, options: ToastOptions = {}) {
  const id = Math.random().toString(36).substring(7);
  const duration = options.duration || 3000;
  if (options.position) {
    globalPosition = options.position;
  }

  const timeoutId = window.setTimeout(() => {
    removeToast(id);
  }, duration);

  toasts.push({ id, message, type, timeoutId });
  renderToasts();

  return () => removeToast(id);
}

export const toast = {
  success: (message: string, options?: ToastOptions) => showToast(message, 'success', options),
  error: (message: string, options?: ToastOptions) => showToast(message, 'error', options),
  info: (message: string, options?: ToastOptions) => showToast(message, 'info', options),
};

// Simple Toaster component for React (optional, for compatibility)
export function Toaster({ position: pos = 'bottom-right' }: { position?: ToastOptions['position'] }) {
  // This component ensures the toast container is created and sets the position
  React.useEffect(() => {
    globalPosition = pos;
    ensureContainer();
  }, [pos]);
  return null;
}

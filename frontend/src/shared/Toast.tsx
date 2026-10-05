export type ToastState = { id: number; tone: 'success' | 'error' | 'info'; title: string; detail?: string }

export default function Toast({ toast, onClose }: { toast?: ToastState; onClose: () => void }) {
  if (!toast) return null
  return <div className={`toast ${toast.tone}`} role="status" aria-live="polite">
    <div className="toast-icon">{toast.tone === 'success' ? '✓' : toast.tone === 'error' ? '!' : 'i'}</div>
    <div><strong>{toast.title}</strong>{toast.detail && <span>{toast.detail}</span>}</div>
    <button onClick={onClose} aria-label="Cerrar notificación">×</button>
  </div>
}

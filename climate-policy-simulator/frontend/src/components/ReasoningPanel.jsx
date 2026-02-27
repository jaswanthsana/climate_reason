import { useState } from 'react'

export function ReasoningPanel({ reasoning, title = 'K2 Reasoning Chain', defaultOpen = false }) {
  const [open, setOpen] = useState(defaultOpen)

  if (!reasoning) return null

  return (
    <div className="mt-2 border border-surface-3 rounded overflow-hidden">
      <button
        onClick={() => setOpen(o => !o)}
        className="w-full flex items-center justify-between px-3 py-2
                   bg-surface-2 hover:bg-surface-3 transition-colors text-left"
      >
        <div className="flex items-center gap-2">
          <svg className="w-3.5 h-3.5 text-accent-purple" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M8.25 3v1.5M4.5 8.25H3m18 0h-1.5M4.5 12H3m18 0h-1.5m-15 3.75H3m18 0h-1.5M8.25 19.5V21M12 3v1.5m0 15V21m3.75-18v1.5m0 15V21m-9-1.5h10.5a2.25 2.25 0 002.25-2.25V6.75a2.25 2.25 0 00-2.25-2.25H6.75A2.25 2.25 0 004.5 6.75v10.5a2.25 2.25 0 002.25 2.25zm.75-12h9v9h-9v-9z" />
          </svg>
          <span className="label-mono text-[10px] text-accent-purple/80">{title}</span>
          <span className="text-[10px] text-slate-600 font-mono">
            {reasoning.length.toLocaleString()} chars
          </span>
        </div>
        <svg
          className={`w-3.5 h-3.5 text-slate-500 transition-transform ${open ? 'rotate-180' : ''}`}
          fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}
        >
          <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" />
        </svg>
      </button>

      {open && (
        <div className="max-h-64 overflow-y-auto bg-surface-DEFAULT/50 p-3">
          <pre className="reasoning-text whitespace-pre-wrap break-words text-[11px] leading-relaxed">
            {reasoning}
          </pre>
        </div>
      )}
    </div>
  )
}

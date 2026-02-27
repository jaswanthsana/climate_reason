/**
 * Small colored badge for confidence levels.
 * level: 'high' | 'medium' | 'low'
 * score: optional 0-1 number
 */
export function ConfidenceBadge({ level, score, size = 'sm' }) {
  const config = {
    high:   { label: 'HIGH',   bg: 'bg-emerald-500/15', text: 'text-emerald-400', border: 'border-emerald-500/30', dot: 'bg-emerald-400' },
    medium: { label: 'MEDIUM', bg: 'bg-amber-500/15',   text: 'text-amber-400',   border: 'border-amber-500/30',   dot: 'bg-amber-400' },
    low:    { label: 'LOW',    bg: 'bg-red-500/15',     text: 'text-red-400',     border: 'border-red-500/30',     dot: 'bg-red-400' },
  }

  const c = config[level] || config.medium
  const pct = score !== undefined ? Math.round(score * 100) : null

  return (
    <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded border font-mono
      ${c.bg} ${c.text} ${c.border}
      ${size === 'sm' ? 'text-[10px]' : 'text-xs'}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${c.dot}`} />
      {c.label}
      {pct !== null && <span className="opacity-70">·{pct}%</span>}
    </span>
  )
}

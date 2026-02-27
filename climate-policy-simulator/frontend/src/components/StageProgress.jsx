import { useState } from 'react'
import { ConfidenceBadge } from './ConfidenceBadge'
import { ReasoningPanel } from './ReasoningPanel'

const STAGE_META = {
  1: { icon: '⬡', color: 'text-slate-400',  activeColor: 'text-accent-blue',  doneColor: 'text-emerald-400', hint: 'reasoning_effort: low' },
  2: { icon: '⬡', color: 'text-slate-400',  activeColor: 'text-accent-cyan',  doneColor: 'text-emerald-400', hint: 'reasoning_effort: high' },
  3: { icon: '⬡', color: 'text-slate-400',  activeColor: 'text-accent-cyan',  doneColor: 'text-emerald-400', hint: 'reasoning_effort: high' },
  4: { icon: '⬡', color: 'text-slate-400',  activeColor: 'text-amber-400',    doneColor: 'text-emerald-400', hint: 'reasoning_effort: medium' },
  5: { icon: '⬡', color: 'text-slate-400',  activeColor: 'text-accent-purple',doneColor: 'text-emerald-400', hint: 'reasoning_effort: medium' },
}

function Spinner() {
  return (
    <svg className="spinner w-4 h-4 text-accent-blue" fill="none" viewBox="0 0 24 24">
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
      <path className="opacity-75" fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
    </svg>
  )
}

function StageDetail({ stage, data }) {
  if (!data) return null

  if (stage === 1) {
    return (
      <div className="mt-2 text-xs space-y-1.5">
        <div className="flex items-center gap-2 flex-wrap">
          <span className="label-mono text-[9px]">Type:</span>
          <span className="text-accent-cyan font-mono text-[10px]">{data.policy_type}</span>
        </div>
        <div className="flex items-start gap-2 flex-wrap">
          <span className="label-mono text-[9px]">Sectors:</span>
          <div className="flex gap-1 flex-wrap">
            {(data.sectors_affected || []).map(s => (
              <span key={s} className="px-1.5 py-0.5 rounded bg-surface-3 text-[9px] font-mono text-slate-300 border border-surface-4">
                {s}
              </span>
            ))}
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="label-mono text-[9px]">Timeline:</span>
          <span className="text-slate-300 font-mono text-[10px]">{data.timeline_start} → {data.timeline_end}</span>
        </div>
      </div>
    )
  }

  if (stage === 2) {
    return (
      <div className="mt-2 text-xs">
        <p className="text-slate-400 font-mono text-[10px] mb-1">
          Total reduction: <span className="text-emerald-400">{data.total_emission_reduction_estimate}</span>
        </p>
        <div className="space-y-1">
          {(data.sector_impacts || []).slice(0, 3).map(si => (
            <div key={si.sector} className="flex items-baseline gap-2">
              <span className="w-20 shrink-0 label-mono text-[9px]">{si.sector}</span>
              <span className="text-slate-400 text-[10px] font-mono truncate">{si.magnitude_estimate}</span>
            </div>
          ))}
          {(data.sector_impacts || []).length > 3 && (
            <span className="text-slate-600 text-[9px] font-mono">
              +{data.sector_impacts.length - 3} more sectors
            </span>
          )}
        </div>
      </div>
    )
  }

  if (stage === 3) {
    return (
      <div className="mt-2 text-xs space-y-1">
        <p className="label-mono text-[9px]">
          Cascades: <span className="text-white">{(data.cascade_effects || []).length}</span>
          &nbsp;·&nbsp;
          Feedback loops: <span className="text-white">{(data.feedback_loops || []).length}</span>
        </p>
        <p className="font-mono text-[9px] text-amber-400">
          Leakage risk: {data.carbon_leakage_risk}
        </p>
      </div>
    )
  }

  if (stage === 4) {
    return (
      <div className="mt-2 flex items-center gap-2">
        <span className="label-mono text-[9px]">Overall confidence:</span>
        <ConfidenceBadge level={data.overall_confidence} score={data.overall_confidence_score} />
      </div>
    )
  }

  if (stage === 5) {
    return (
      <div className="mt-2 text-xs">
        <p className="text-slate-300 leading-relaxed text-[10px]">
          {data.net_emission_impact}
        </p>
      </div>
    )
  }

  return null
}

function StageItem({ stageNum, stage, isLast }) {
  const [expanded, setExpanded] = useState(false)
  const meta = STAGE_META[stageNum]
  const isRunning = stage.status === 'running'
  const isComplete = stage.status === 'complete'
  const isError = stage.status === 'error'
  const isWaiting = stage.status === 'waiting'

  const dotColor = isRunning ? 'bg-accent-blue animate-pulse-slow'
    : isComplete ? 'bg-emerald-500'
    : isError ? 'bg-red-500'
    : 'bg-surface-4'

  return (
    <div className="relative">
      {/* Connector line */}
      {!isLast && (
        <div className={`absolute left-3.5 top-8 bottom-0 w-px
          ${isComplete ? 'bg-emerald-500/20' : 'bg-surface-3'}`} />
      )}

      <div className={`relative flex gap-3 p-3 rounded-lg transition-all
        ${isRunning ? 'bg-surface-2 border border-accent-blue/20' : ''}
        ${isComplete && expanded ? 'bg-surface-2/50' : ''}
      `}>
        {/* Status indicator */}
        <div className="shrink-0 flex flex-col items-center gap-1 mt-0.5">
          {isRunning ? (
            <Spinner />
          ) : isComplete ? (
            <div className="w-7 h-7 rounded-full flex items-center justify-center bg-emerald-500/10 border border-emerald-500/30">
              <svg className="w-3.5 h-3.5 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
              </svg>
            </div>
          ) : isError ? (
            <div className="w-7 h-7 rounded-full flex items-center justify-center bg-red-500/10 border border-red-500/30">
              <svg className="w-3.5 h-3.5 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
          ) : (
            <div className="w-7 h-7 rounded-full flex items-center justify-center bg-surface-3 border border-surface-4">
              <span className="text-[10px] font-mono text-slate-500">{stageNum}</span>
            </div>
          )}
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between gap-2">
            <div>
              <p className={`text-sm font-medium leading-tight
                ${isRunning ? 'text-white cursor-blink' : isComplete ? 'text-slate-200' : 'text-slate-500'}`}>
                {stage.label}
              </p>
              <p className="text-[9px] font-mono text-slate-600 mt-0.5">{meta.hint}</p>
            </div>

            {isComplete && (
              <button
                onClick={() => setExpanded(e => !e)}
                className="shrink-0 text-[9px] font-mono text-slate-500 hover:text-slate-300
                           px-1.5 py-0.5 rounded hover:bg-surface-3 transition-all"
              >
                {expanded ? '▲ less' : '▼ more'}
              </button>
            )}
          </div>

          {isRunning && (
            <p className="text-xs text-slate-500 mt-1 font-mono animate-pulse">
              K2 is reasoning…
            </p>
          )}

          {isComplete && (
            <>
              <StageDetail stage={stageNum} data={stage.data} />
              {expanded && stage.reasoning && (
                <ReasoningPanel reasoning={stage.reasoning} />
              )}
            </>
          )}

          {isError && (
            <p className="text-xs text-red-400 mt-1 font-mono">{stage.data?.error}</p>
          )}
        </div>
      </div>
    </div>
  )
}

export function StageProgress({ stages }) {
  return (
    <div className="panel">
      <div className="panel-header">
        <svg className="w-4 h-4 text-accent-cyan" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" />
        </svg>
        <span className="label-mono">Reasoning Pipeline</span>
        <div className="ml-auto flex gap-1">
          {[1, 2, 3, 4, 5].map(n => {
            const s = stages[n]
            const color = s.status === 'complete' ? 'bg-emerald-500'
              : s.status === 'running' ? 'bg-accent-blue animate-pulse'
              : s.status === 'error' ? 'bg-red-500'
              : 'bg-surface-4'
            return <div key={n} className={`w-1.5 h-1.5 rounded-full ${color}`} />
          })}
        </div>
      </div>

      <div className="p-3 space-y-1">
        {[1, 2, 3, 4, 5].map(n => (
          <StageItem
            key={n}
            stageNum={n}
            stage={stages[n]}
            isLast={n === 5}
          />
        ))}
      </div>
    </div>
  )
}

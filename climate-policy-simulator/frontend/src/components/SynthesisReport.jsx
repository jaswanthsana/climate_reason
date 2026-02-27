import { useState } from 'react'
import { ConfidenceBadge } from './ConfidenceBadge'
import { ReasoningPanel } from './ReasoningPanel'

function Section({ title, icon, children }) {
  return (
    <div className="space-y-2">
      <div className="flex items-center gap-2">
        <span className="text-base">{icon}</span>
        <h3 className="text-xs font-semibold text-slate-300 uppercase tracking-wider">{title}</h3>
      </div>
      {children}
    </div>
  )
}

export function SynthesisReport({ data, reasoning }) {
  const [showReasoning, setShowReasoning] = useState(false)

  if (!data) return null

  const {
    executive_summary,
    headline_findings = [],
    net_emission_impact,
    co_benefits = [],
    risks_and_tradeoffs = [],
    recommendations = [],
    implementation_timeline,
    bottom_line,
    monitoring_indicators = [],
  } = data

  return (
    <div className="panel animate-fade-in">
      <div className="panel-header">
        <svg className="w-4 h-4 text-accent-green" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
        </svg>
        <span className="label-mono">Executive Briefing</span>
        <div className="ml-auto flex items-center gap-2">
          <span className="text-[10px] font-mono text-emerald-400">Stage 5 Complete</span>
          <div className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
        </div>
      </div>

      <div className="p-4 space-y-5">
        {/* Bottom line */}
        {bottom_line && (
          <div className="p-3 rounded-lg bg-accent-blue/10 border border-accent-blue/20">
            <p className="text-sm text-white font-medium leading-relaxed">
              {bottom_line}
            </p>
          </div>
        )}

        {/* Net impact */}
        {net_emission_impact && (
          <div className="flex items-start gap-3 p-3 rounded-lg bg-emerald-500/5 border border-emerald-500/20">
            <div className="w-8 h-8 rounded shrink-0 bg-emerald-500/15 border border-emerald-500/20
                           flex items-center justify-center">
              <svg className="w-4 h-4 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 18L9 11.25l4.306 4.307a11.95 11.95 0 015.814-5.519l2.74-1.22m0 0l-5.94-2.28m5.94 2.28l-2.28 5.941" />
              </svg>
            </div>
            <div>
              <p className="label-mono text-[9px] text-emerald-400/70 mb-1">Net Emission Impact</p>
              <p className="text-sm text-emerald-300 font-mono">{net_emission_impact}</p>
            </div>
          </div>
        )}

        {/* Executive summary */}
        {executive_summary && (
          <Section title="Executive Summary" icon="📋">
            <p className="text-sm text-slate-300 leading-relaxed">{executive_summary}</p>
          </Section>
        )}

        {/* Headline findings */}
        {headline_findings.length > 0 && (
          <Section title="Key Findings" icon="🎯">
            <div className="space-y-2">
              {headline_findings.map((f, i) => (
                <div key={i} className="flex items-start gap-3 p-2.5 rounded bg-surface-2 border border-surface-3">
                  <span className="text-[10px] font-mono text-slate-600 mt-0.5 w-4 shrink-0">#{i + 1}</span>
                  <div className="flex-1 min-w-0">
                    <p className="text-xs text-slate-200 leading-relaxed mb-1">{f.finding}</p>
                    {f.supporting_evidence && (
                      <p className="text-[10px] text-slate-500 leading-relaxed">{f.supporting_evidence}</p>
                    )}
                  </div>
                  <ConfidenceBadge level={f.confidence} />
                </div>
              ))}
            </div>
          </Section>
        )}

        {/* Co-benefits and Risks side by side */}
        <div className="grid grid-cols-2 gap-3">
          {co_benefits.length > 0 && (
            <Section title="Co-Benefits" icon="✅">
              <ul className="space-y-1.5">
                {co_benefits.map((b, i) => (
                  <li key={i} className="flex items-start gap-2 text-xs text-slate-300 leading-relaxed">
                    <span className="text-emerald-500 mt-0.5 shrink-0">+</span>
                    {b}
                  </li>
                ))}
              </ul>
            </Section>
          )}

          {risks_and_tradeoffs.length > 0 && (
            <Section title="Risks & Trade-offs" icon="⚠️">
              <ul className="space-y-1.5">
                {risks_and_tradeoffs.map((r, i) => (
                  <li key={i} className="flex items-start gap-2 text-xs text-slate-300 leading-relaxed">
                    <span className="text-amber-500 mt-0.5 shrink-0">!</span>
                    {r}
                  </li>
                ))}
              </ul>
            </Section>
          )}
        </div>

        {/* Recommendations */}
        {recommendations.length > 0 && (
          <Section title="Recommendations" icon="🔧">
            <div className="space-y-2">
              {recommendations.sort((a, b) => a.priority - b.priority).map((r, i) => (
                <div key={i} className="p-2.5 rounded bg-surface-2 border border-surface-3">
                  <div className="flex items-start gap-2 mb-1">
                    <span className="shrink-0 w-5 h-5 rounded bg-accent-blue/20 border border-accent-blue/30
                                   flex items-center justify-center text-[9px] font-mono text-accent-blue">
                      {r.priority}
                    </span>
                    <p className="text-xs font-medium text-slate-200">{r.action}</p>
                  </div>
                  {r.rationale && (
                    <p className="text-[10px] text-slate-500 leading-relaxed ml-7">{r.rationale}</p>
                  )}
                  {r.complementary_policy && (
                    <span className="ml-7 mt-1 inline-block text-[9px] font-mono px-1.5 py-0.5 rounded
                                    bg-accent-purple/10 border border-accent-purple/20 text-accent-purple/80">
                      {r.complementary_policy}
                    </span>
                  )}
                </div>
              ))}
            </div>
          </Section>
        )}

        {/* Timeline */}
        {implementation_timeline && (
          <Section title="Implementation Roadmap" icon="🗓️">
            <p className="text-xs text-slate-400 leading-relaxed font-mono">{implementation_timeline}</p>
          </Section>
        )}

        {/* Monitoring indicators */}
        {monitoring_indicators.length > 0 && (
          <Section title="Key Monitoring Indicators" icon="📊">
            <div className="space-y-1.5">
              {monitoring_indicators.map((m, i) => (
                <div key={i} className="flex items-start gap-2 text-xs">
                  <span className="text-accent-cyan shrink-0 mt-0.5">→</span>
                  <div>
                    <span className="text-slate-200 font-medium">{m.indicator}</span>
                    {m.target && <span className="text-slate-500"> — {m.target}</span>}
                    {m.frequency && <span className="text-slate-600"> [{m.frequency}]</span>}
                  </div>
                </div>
              ))}
            </div>
          </Section>
        )}

        {/* K2 reasoning */}
        {reasoning && (
          <ReasoningPanel reasoning={reasoning} title="Stage 5 Reasoning Chain" />
        )}
      </div>
    </div>
  )
}

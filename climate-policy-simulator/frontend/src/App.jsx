import { useState } from 'react'
import { PolicyInput } from './components/PolicyInput'
import { StageProgress } from './components/StageProgress'
import { CausalGraph } from './components/CausalGraph'
import { SynthesisReport } from './components/SynthesisReport'
import { useSSE } from './hooks/useSSE'

function Header() {
  return (
    <header className="h-14 flex items-center px-6 border-b border-surface-3 bg-surface-1/80 backdrop-blur-sm shrink-0">
      <div className="flex items-center gap-3">
        {/* Logo mark */}
        <div className="w-8 h-8 rounded bg-accent-blue/15 border border-accent-blue/30 flex items-center justify-center">
          <svg className="w-4.5 h-4.5 text-accent-blue" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round"
              d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" />
          </svg>
        </div>
        <div>
          <h1 className="text-base font-semibold tracking-tight text-white leading-none">
            ClimateReason
          </h1>
          <p className="text-[10px] text-slate-500 font-mono leading-none mt-0.5">
            Powered by K2 Think V2
          </p>
        </div>
      </div>

      <div className="ml-8 h-5 w-px bg-surface-3" />

      <div className="ml-6 flex items-center gap-6 text-[10px] font-mono text-slate-600">
        <span>MBZUAI · Build with K2 Think V2 Hackathon</span>
        <span className="flex items-center gap-1.5">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse-slow" />
          K2 Think V2 · 70B
        </span>
      </div>

      <div className="ml-auto flex items-center gap-3 text-[10px] font-mono text-slate-600">
        <span>5-Stage Reasoning Pipeline</span>
        <span>·</span>
        <span>RAG + D3 Graph</span>
        <span>·</span>
        <span>SSE Streaming</span>
      </div>
    </header>
  )
}

function GraphHeader({ nodeCount, edgeCount, stage }) {
  const stageLabel = {
    0: 'Waiting for analysis',
    2: 'Nodes populated',
    3: 'Edges added',
    4: 'Confidence applied',
    5: 'Complete',
  }

  return (
    <div className="panel-header">
      <svg className="w-4 h-4 text-accent-purple" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round"
          d="M7.5 14.25v2.25m3-4.5v4.5m3-6.75v6.75m3-9v9M6 20.25h12A2.25 2.25 0 0020.25 18V6A2.25 2.25 0 0018 3.75H6A2.25 2.25 0 003.75 6v12A2.25 2.25 0 006 20.25z" />
      </svg>
      <span className="label-mono">Causal Impact Graph</span>

      {nodeCount > 0 && (
        <div className="flex items-center gap-3 ml-2">
          <span className="text-[10px] font-mono text-slate-500">
            {nodeCount} nodes · {edgeCount} edges
          </span>
        </div>
      )}

      <div className="ml-auto text-[10px] font-mono text-slate-600">
        D3 force-directed · drag to rearrange
      </div>
    </div>
  )
}

export default function App() {
  const {
    stages, graphNodes, graphEdges,
    isRunning, isDone, error,
    analyze, cancel, reset,
  } = useSSE()

  // Determine which stage of graph rendering we're at
  const graphStage = stages[4]?.status === 'complete' ? 4
    : stages[3]?.status === 'complete' ? 3
    : stages[2]?.status === 'complete' ? 2
    : 0

  const stage5Data = stages[5]?.data
  const stage5Reasoning = stages[5]?.reasoning

  return (
    <div className="h-screen flex flex-col bg-surface-DEFAULT grid-dot overflow-hidden">
      <Header />

      {/* Main layout */}
      <div className="flex-1 flex min-h-0 p-4 gap-4">

        {/* Left panel: Input + Pipeline */}
        <div className="w-[380px] shrink-0 flex flex-col gap-3 overflow-y-auto min-h-0 pr-1">
          <PolicyInput
            onAnalyze={analyze}
            isRunning={isRunning}
            onCancel={cancel}
          />
          <StageProgress stages={stages} />

          {error && (
            <div className="panel p-3 border-red-500/30 bg-red-500/5">
              <p className="text-xs text-red-400 font-mono">{error}</p>
            </div>
          )}
        </div>

        {/* Right panel: Graph + Report */}
        <div className="flex-1 flex flex-col gap-3 min-w-0 min-h-0">

          {/* Graph */}
          <div className="panel flex-1 flex flex-col min-h-0">
            <GraphHeader
              nodeCount={graphNodes.length}
              edgeCount={graphEdges.length}
              stage={graphStage}
            />
            <div className="flex-1 relative">
              <CausalGraph
                nodes={graphNodes}
                edges={graphEdges}
                stage={graphStage}
              />
            </div>
          </div>

          {/* Synthesis report (appears after stage 5) */}
          {stage5Data && (
            <div className="max-h-[45vh] overflow-y-auto">
              <SynthesisReport data={stage5Data} reasoning={stage5Reasoning} />
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

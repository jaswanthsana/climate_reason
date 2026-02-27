/**
 * useSSE — consumes the /api/analyze SSE stream and maintains:
 *   - stages[1..5]: { status, label, data, reasoning }
 *   - graphNodes: accumulated array of GraphNode objects
 *   - graphEdges: accumulated array of GraphEdge objects
 *   - isRunning: boolean
 *   - isDone: boolean
 *   - error: string | null
 */
import { useState, useCallback, useRef } from 'react'

const INITIAL_STAGES = {
  1: { status: 'waiting', label: 'Parse Policy', data: null, reasoning: '' },
  2: { status: 'waiting', label: 'Direct Impact Analysis', data: null, reasoning: '' },
  3: { status: 'waiting', label: 'Cascade & Cross-Sector Effects', data: null, reasoning: '' },
  4: { status: 'waiting', label: 'Validate & Score Confidence', data: null, reasoning: '' },
  5: { status: 'waiting', label: 'Synthesize & Recommend', data: null, reasoning: '' },
}

export function useSSE() {
  const [stages, setStages] = useState(INITIAL_STAGES)
  const [graphNodes, setGraphNodes] = useState([])
  const [graphEdges, setGraphEdges] = useState([])
  const [isRunning, setIsRunning] = useState(false)
  const [isDone, setIsDone] = useState(false)
  const [error, setError] = useState(null)
  const abortRef = useRef(null)

  const reset = useCallback(() => {
    setStages(INITIAL_STAGES)
    setGraphNodes([])
    setGraphEdges([])
    setIsRunning(false)
    setIsDone(false)
    setError(null)
  }, [])

  const analyze = useCallback(async (policyText, country = 'UAE') => {
    // Cancel any in-flight request
    if (abortRef.current) {
      abortRef.current.abort()
    }
    abortRef.current = new AbortController()

    reset()
    setIsRunning(true)

    try {
      const response = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ policy_text: policyText, country }),
        signal: abortRef.current.signal,
      })

      if (!response.ok) {
        const errText = await response.text()
        throw new Error(`API error ${response.status}: ${errText}`)
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })

        // SSE lines are separated by \n\n
        const parts = buffer.split('\n\n')
        buffer = parts.pop() // last potentially incomplete chunk

        for (const part of parts) {
          const line = part.trim()
          if (!line.startsWith('data:')) continue

          const jsonStr = line.slice(5).trim()
          if (!jsonStr) continue

          let event
          try {
            event = JSON.parse(jsonStr)
          } catch {
            console.warn('Failed to parse SSE event:', jsonStr)
            continue
          }

          // Pipeline done signal
          if (event.done) {
            setIsRunning(false)
            setIsDone(true)
            continue
          }

          const { stage, status, label, data, reasoning, graph_nodes, graph_edges } = event

          // Update stage state
          setStages(prev => ({
            ...prev,
            [stage]: { status, label, data: data || null, reasoning: reasoning || '' },
          }))

          // Stage 2 complete → add initial nodes and edges
          if (stage === 2 && status === 'complete') {
            if (graph_nodes?.length) {
              setGraphNodes(graph_nodes)
            }
            if (graph_edges?.length) {
              setGraphEdges(graph_edges)
            }
          }

          // Stage 3 complete → add cross-sector edges
          if (stage === 3 && status === 'complete') {
            if (graph_edges?.length) {
              setGraphEdges(prev => {
                // Deduplicate by source+target
                const existing = new Set(prev.map(e => `${e.source}→${e.target}`))
                const newEdges = graph_edges.filter(
                  e => !existing.has(`${e.source}→${e.target}`)
                )
                return [...prev, ...newEdges]
              })
            }
          }

          // Stage 4 complete → update nodes with confidence scores
          if (stage === 4 && status === 'complete') {
            if (graph_nodes?.length) {
              setGraphNodes(graph_nodes)
            }
          }

          // Handle errors
          if (status === 'error') {
            console.error(`Stage ${stage} error:`, data?.error)
          }
        }
      }
    } catch (err) {
      if (err.name === 'AbortError') return
      console.error('SSE stream error:', err)
      setError(err.message)
      setIsRunning(false)
    }
  }, [reset])

  const cancel = useCallback(() => {
    if (abortRef.current) {
      abortRef.current.abort()
    }
    setIsRunning(false)
  }, [])

  return {
    stages,
    graphNodes,
    graphEdges,
    isRunning,
    isDone,
    error,
    analyze,
    cancel,
    reset,
  }
}

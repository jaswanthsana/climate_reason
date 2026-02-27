import { useEffect, useRef, useState, useCallback } from 'react'
import * as d3 from 'd3'

const SECTOR_COLORS = {
  energy:      '#3b82f6',
  water:       '#06b6d4',
  agriculture: '#10b981',
  transport:   '#f97316',
  industry:    '#94a3b8',
  economy:     '#8b5cf6',
  social:      '#ec4899',
}

const CONFIDENCE_STROKE = (c) => {
  if (c === undefined || c === null) return '#1e2d4a'
  if (c >= 0.7) return '#10b981'
  if (c >= 0.4) return '#f59e0b'
  return '#ef4444'
}

const NODE_RADIUS = (d) => {
  const base = 18
  const mag = d.magnitude ?? 0.5
  return base + mag * 14
}

export function CausalGraph({ nodes, edges, stage }) {
  const svgRef = useRef(null)
  const tooltipRef = useRef(null)
  const simulationRef = useRef(null)
  const [selectedNode, setSelectedNode] = useState(null)

  const getColor = useCallback((sector) => SECTOR_COLORS[sector] || '#64748b', [])

  useEffect(() => {
    if (!nodes.length || !svgRef.current) return

    // Filter edges to only those whose source and target exist in the node set.
    // Stage 3 cross-sector edges sometimes reference sector names instead of
    // specific node IDs; D3 v7 throws "node not found" for missing IDs.
    const nodeIds = new Set(nodes.map(n => n.id))
    const validEdges = edges.filter(e => {
      const src = typeof e.source === 'object' ? e.source?.id : e.source
      const tgt = typeof e.target === 'object' ? e.target?.id : e.target
      return nodeIds.has(src) && nodeIds.has(tgt)
    })

    const container = svgRef.current.parentElement
    const width = container.clientWidth
    const height = container.clientHeight

    const svg = d3.select(svgRef.current)
    svg.attr('width', width).attr('height', height)

    // Clear previous render
    svg.selectAll('*').remove()

    // Defs: arrowheads
    const defs = svg.append('defs')
    const marker = defs.append('marker')
      .attr('id', 'arrow')
      .attr('viewBox', '0 -5 10 10')
      .attr('refX', 28)
      .attr('refY', 0)
      .attr('markerWidth', 6)
      .attr('markerHeight', 6)
      .attr('orient', 'auto')
    marker.append('path')
      .attr('d', 'M0,-5L10,0L0,5')
      .attr('fill', '#334155')

    const g = svg.append('g').attr('class', 'graph-root')

    // Zoom
    const zoom = d3.zoom()
      .scaleExtent([0.3, 3])
      .on('zoom', (event) => {
        g.attr('transform', event.transform)
      })
    svg.call(zoom)

    // Edges
    const link = g.append('g').attr('class', 'links')
      .selectAll('line')
      .data(validEdges)
      .join('line')
      .attr('stroke', d => `rgba(100, 116, 139, ${d.weight ?? 0.5})`)
      .attr('stroke-width', d => Math.max(1, (d.weight ?? 0.5) * 3))
      .attr('marker-end', 'url(#arrow)')
      .style('opacity', 0)
      .transition()
      .duration(600)
      .style('opacity', 1)

    // Edge labels
    const linkLabel = g.append('g').attr('class', 'link-labels')
      .selectAll('text')
      .data(validEdges.filter(e => e.label))
      .join('text')
      .attr('font-size', '9px')
      .attr('fill', '#475569')
      .attr('text-anchor', 'middle')
      .attr('dy', -3)
      .text(d => d.label)
      .style('opacity', 0)
      .transition()
      .duration(800)
      .style('opacity', 0.7)

    // Nodes
    const node = g.append('g').attr('class', 'nodes')
      .selectAll('g')
      .data(nodes)
      .join('g')
      .attr('class', 'node')
      .style('cursor', 'pointer')
      .call(
        d3.drag()
          .on('start', (event, d) => {
            if (!event.active) simulationRef.current?.alphaTarget(0.3).restart()
            d.fx = d.x; d.fy = d.y
          })
          .on('drag', (event, d) => {
            d.fx = event.x; d.fy = event.y
          })
          .on('end', (event, d) => {
            if (!event.active) simulationRef.current?.alphaTarget(0)
            d.fx = null; d.fy = null
          })
      )
      .on('click', (event, d) => {
        event.stopPropagation()
        setSelectedNode(prev => prev?.id === d.id ? null : d)
      })

    // Node circle
    node.append('circle')
      .attr('r', d => NODE_RADIUS(d))
      .attr('fill', d => `${getColor(d.sector)}22`)
      .attr('stroke', d => CONFIDENCE_STROKE(d.confidence))
      .attr('stroke-width', 2)
      .style('opacity', 0)
      .transition()
      .duration(500)
      .style('opacity', 1)

    // Node inner circle
    node.append('circle')
      .attr('r', d => NODE_RADIUS(d) * 0.55)
      .attr('fill', d => getColor(d.sector))
      .style('opacity', 0)
      .transition()
      .delay(200)
      .duration(400)
      .style('opacity', 0.85)

    // Node label
    node.append('text')
      .attr('text-anchor', 'middle')
      .attr('dy', d => NODE_RADIUS(d) + 14)
      .attr('font-size', '10px')
      .attr('fill', '#cbd5e1')
      .attr('font-family', 'Inter, sans-serif')
      .text(d => d.label.length > 18 ? d.label.slice(0, 17) + '…' : d.label)

    // Tooltip
    node
      .on('mouseenter', (event, d) => {
        const tooltip = tooltipRef.current
        if (!tooltip) return
        tooltip.style.display = 'block'
        tooltip.innerHTML = `
          <div class="font-medium text-white mb-1">${d.label}</div>
          <div class="text-slate-400 text-[10px] mb-1">${d.sector.toUpperCase()}</div>
          ${d.description ? `<div class="text-slate-300 text-[11px] leading-relaxed">${d.description}</div>` : ''}
          ${d.confidence !== undefined && d.confidence !== null ? `
            <div class="mt-2 text-[10px] font-mono">
              Confidence: <span style="color:${CONFIDENCE_STROKE(d.confidence)}">${Math.round(d.confidence * 100)}%</span>
            </div>` : ''}
        `
        const rect = svgRef.current.getBoundingClientRect()
        tooltip.style.left = (event.clientX - rect.left + 12) + 'px'
        tooltip.style.top = (event.clientY - rect.top - 20) + 'px'
      })
      .on('mousemove', (event) => {
        const tooltip = tooltipRef.current
        if (!tooltip) return
        const rect = svgRef.current.getBoundingClientRect()
        tooltip.style.left = (event.clientX - rect.left + 12) + 'px'
        tooltip.style.top = (event.clientY - rect.top - 20) + 'px'
      })
      .on('mouseleave', () => {
        if (tooltipRef.current) tooltipRef.current.style.display = 'none'
      })

    // Force simulation
    const simulation = d3.forceSimulation(nodes)
      .force('link', d3.forceLink(validEdges)
        .id(d => d.id)
        .distance(120)
        .strength(0.4))
      .force('charge', d3.forceManyBody().strength(-350))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(d => NODE_RADIUS(d) + 20))
      .on('tick', () => {
        link
          .attr('x1', d => d.source.x)
          .attr('y1', d => d.source.y)
          .attr('x2', d => d.target.x)
          .attr('y2', d => d.target.y)

        linkLabel
          .attr('x', d => (d.source.x + d.target.x) / 2)
          .attr('y', d => (d.source.y + d.target.y) / 2)

        node.attr('transform', d => `translate(${d.x},${d.y})`)
      })

    simulationRef.current = simulation
    svg.on('click', () => setSelectedNode(null))

    return () => {
      simulation.stop()
    }
  }, [nodes, edges, getColor])

  const isEmpty = nodes.length === 0

  return (
    <div className="relative w-full h-full">
      {isEmpty && (
        <div className="absolute inset-0 flex flex-col items-center justify-center gap-3">
          <div className="w-16 h-16 rounded-full border-2 border-dashed border-surface-4
                         flex items-center justify-center">
            <svg className="w-7 h-7 text-surface-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                d="M7.5 14.25v2.25m3-4.5v4.5m3-6.75v6.75m3-9v9M6 20.25h12A2.25 2.25 0 0020.25 18V6A2.25 2.25 0 0018 3.75H6A2.25 2.25 0 003.75 6v12A2.25 2.25 0 006 20.25z" />
            </svg>
          </div>
          <p className="text-slate-600 text-sm font-mono">
            Causal graph will appear after Stage 2
          </p>
        </div>
      )}

      <svg ref={svgRef} className="w-full h-full" />
      <div ref={tooltipRef} className="graph-tooltip" style={{ display: 'none' }} />

      {/* Legend */}
      {!isEmpty && (
        <div className="absolute bottom-3 left-3 flex flex-col gap-1.5 bg-surface-1/80 backdrop-blur
                       border border-surface-3 rounded-lg p-3">
          <p className="label-mono text-[9px] mb-1">Sector</p>
          {Object.entries(SECTOR_COLORS).map(([sector, color]) => (
            <div key={sector} className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full" style={{ background: color }} />
              <span className="text-[9px] font-mono text-slate-400 capitalize">{sector}</span>
            </div>
          ))}
          <div className="mt-2 border-t border-surface-3 pt-2">
            <p className="label-mono text-[9px] mb-1">Confidence</p>
            {[['High', '#10b981'], ['Medium', '#f59e0b'], ['Low', '#ef4444']].map(([l, c]) => (
              <div key={l} className="flex items-center gap-2">
                <div className="w-4 h-0.5 rounded" style={{ background: c }} />
                <span className="text-[9px] font-mono text-slate-400">{l}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Selected node panel */}
      {selectedNode && (
        <div className="absolute top-3 right-3 w-64 bg-surface-1/95 backdrop-blur
                       border border-surface-3 rounded-lg p-3 animate-slide-up">
          <div className="flex items-start justify-between mb-2">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <div className="w-2.5 h-2.5 rounded-full"
                  style={{ background: SECTOR_COLORS[selectedNode.sector] || '#64748b' }} />
                <span className="label-mono text-[9px] text-slate-400 capitalize">{selectedNode.sector}</span>
              </div>
              <p className="text-sm font-medium text-white">{selectedNode.label}</p>
            </div>
            <button onClick={() => setSelectedNode(null)}
              className="text-slate-500 hover:text-white transition-colors">
              <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {selectedNode.description && (
            <p className="text-xs text-slate-400 leading-relaxed mb-2">{selectedNode.description}</p>
          )}

          {selectedNode.confidence !== null && selectedNode.confidence !== undefined && (
            <div className="flex items-center gap-2 pt-2 border-t border-surface-3">
              <span className="label-mono text-[9px]">Confidence</span>
              <div className="flex-1 h-1.5 bg-surface-3 rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full transition-all"
                  style={{
                    width: `${selectedNode.confidence * 100}%`,
                    background: CONFIDENCE_STROKE(selectedNode.confidence),
                  }}
                />
              </div>
              <span className="text-[10px] font-mono" style={{ color: CONFIDENCE_STROKE(selectedNode.confidence) }}>
                {Math.round(selectedNode.confidence * 100)}%
              </span>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

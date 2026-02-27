import { useState, useEffect } from 'react'

const EXAMPLE_POLICIES = [
  {
    id: 'uae-carbon-tax',
    title: 'UAE Carbon Tax',
    country: 'UAE',
    badge: 'Carbon Pricing',
    text: `UAE implements a $75/tonne carbon tax on industrial emissions starting January 2027, covering oil & gas, petrochemicals, cement, and aluminium sectors. Revenue to be recycled into a clean energy transition fund. SMEs below 25,000 tCO2e/yr are exempt. Tax rises 5% annually to 2035.`,
  },
  {
    id: 'eu-cbam-expansion',
    title: 'EU CBAM Expansion',
    country: 'EU',
    badge: 'Trade Measure',
    text: `The EU expands its Carbon Border Adjustment Mechanism (CBAM) to cover all manufactured goods — extending beyond the current steel, cement, aluminium, fertilisers, and electricity scope to include chemicals, plastics, vehicles, and electronics — by 2030. Importers must purchase CBAM certificates matching the EU ETS carbon price. Least Developed Countries receive a 5-year phase-in exemption.`,
  },
  {
    id: 'global-methane',
    title: 'Global Methane Pledge',
    country: 'Global',
    badge: 'International',
    text: `A binding international protocol mandates a 30% reduction in anthropogenic methane emissions from 2020 baseline levels by 2030, covering oil & gas, coal mining, agriculture, and waste sectors. Signatories include G20 nations representing 80% of global methane emissions.`,
  },
  {
    id: 'abu-dhabi-solar',
    title: 'Abu Dhabi Solar Mandate',
    country: 'UAE',
    badge: 'Mandate',
    text: `Abu Dhabi mandates that 80% of energy consumption in new industrial facilities must be sourced from on-site or contracted solar power by 2030. Existing facilities must retrofit to 50% solar by 2035. ADNOC, EGA, and EMAL are the primary affected entities. Masdar provides concessional solar project financing at 3.5% for qualifying facilities.`,
  },
]

const COUNTRIES = ['UAE', 'EU', 'US', 'India', 'China', 'Global']

export function PolicyInput({ onAnalyze, isRunning, onCancel }) {
  const [text, setText] = useState('')
  const [country, setCountry] = useState('UAE')
  const [charCount, setCharCount] = useState(0)

  useEffect(() => {
    setCharCount(text.length)
  }, [text])

  const handleExample = (example) => {
    setText(example.text)
    setCountry(example.country === 'Global' ? 'UAE' : example.country)
  }

  const handleSubmit = () => {
    if (!text.trim() || isRunning) return
    onAnalyze(text.trim(), country)
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
      handleSubmit()
    }
  }

  return (
    <div className="panel flex flex-col gap-0">
      {/* Header */}
      <div className="panel-header">
        <svg className="w-4 h-4 text-accent-blue" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h3.75M9 15h3.75M9 18h3.75m3 .75H18a2.25 2.25 0 002.25-2.25V6.108c0-1.135-.845-2.098-1.976-2.192a48.424 48.424 0 00-1.123-.08m-5.801 0c-.065.21-.1.433-.1.664 0 .414.336.75.75.75h4.5a.75.75 0 00.75-.75 2.25 2.25 0 00-.1-.664m-5.8 0A2.251 2.251 0 0113.5 2.25H15c1.012 0 1.867.668 2.15 1.586m-5.8 0c-.376.023-.75.05-1.124.08C9.095 4.01 8.25 4.973 8.25 6.108V8.25m0 0H4.875c-.621 0-1.125.504-1.125 1.125v11.25c0 .621.504 1.125 1.125 1.125h9.75c.621 0 1.125-.504 1.125-1.125V9.375c0-.621-.504-1.125-1.125-1.125H8.25zM6.75 12h.008v.008H6.75V12zm0 3h.008v.008H6.75V15zm0 3h.008v.008H6.75V18z" />
        </svg>
        <span className="label-mono">Policy Input</span>
      </div>

      <div className="p-4 flex flex-col gap-4">
        {/* Example policies */}
        <div>
          <p className="label-mono mb-2 text-[10px]">Example Policies</p>
          <div className="grid grid-cols-2 gap-2">
            {EXAMPLE_POLICIES.map(ex => (
              <button
                key={ex.id}
                onClick={() => handleExample(ex)}
                className="group text-left p-2.5 rounded bg-surface-2 border border-surface-3 hover:border-accent-blue/50 hover:bg-surface-3 transition-all"
              >
                <div className="flex items-start justify-between gap-1 mb-1">
                  <span className="text-xs font-medium text-slate-200 group-hover:text-white leading-tight">
                    {ex.title}
                  </span>
                  <span className="label-mono text-[9px] text-accent-blue/80 whitespace-nowrap shrink-0">
                    {ex.country}
                  </span>
                </div>
                <span className="inline-block text-[9px] font-mono px-1.5 py-0.5 rounded bg-surface-4 text-slate-400 border border-surface-4">
                  {ex.badge}
                </span>
              </button>
            ))}
          </div>
        </div>

        {/* Country selector */}
        <div className="flex items-center gap-3">
          <label className="label-mono text-[10px] whitespace-nowrap">Country Context</label>
          <div className="flex gap-1.5 flex-wrap">
            {COUNTRIES.map(c => (
              <button
                key={c}
                onClick={() => setCountry(c)}
                className={`px-2.5 py-1 rounded text-xs font-mono transition-all
                  ${country === c
                    ? 'bg-accent-blue text-white'
                    : 'bg-surface-2 text-slate-400 border border-surface-3 hover:border-accent-blue/40 hover:text-slate-200'
                  }`}
              >
                {c}
              </button>
            ))}
          </div>
        </div>

        {/* Policy textarea */}
        <div className="relative">
          <textarea
            value={text}
            onChange={e => setText(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Describe a climate policy in plain language...&#10;&#10;Include: policy instrument, sectors covered, key parameters (price, target %), timeline, and geographic scope."
            className="w-full h-36 bg-surface-2 border border-surface-3 rounded p-3 text-sm text-slate-200
                       placeholder-slate-600 resize-none focus:outline-none focus:border-accent-blue/60
                       font-sans leading-relaxed transition-colors"
            maxLength={4000}
          />
          <span className={`absolute bottom-2 right-2 text-[10px] font-mono
            ${charCount > 3800 ? 'text-red-400' : 'text-slate-600'}`}>
            {charCount}/4000
          </span>
        </div>

        {/* Submit / Cancel */}
        <div className="flex items-center gap-3">
          {isRunning ? (
            <button
              onClick={onCancel}
              className="flex items-center gap-2 px-4 py-2.5 rounded bg-red-500/15 border border-red-500/30
                         text-red-400 text-sm font-medium hover:bg-red-500/25 transition-all"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
              Cancel Analysis
            </button>
          ) : (
            <button
              onClick={handleSubmit}
              disabled={!text.trim()}
              className="flex items-center gap-2 px-5 py-2.5 rounded bg-accent-blue text-white text-sm font-medium
                         hover:bg-blue-500 disabled:opacity-40 disabled:cursor-not-allowed transition-all
                         shadow-lg shadow-accent-blue/20"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z" />
              </svg>
              Analyze with K2
            </button>
          )}
          {!isRunning && (
            <span className="text-[10px] text-slate-600 font-mono">⌘+Enter to run</span>
          )}
        </div>
      </div>
    </div>
  )
}

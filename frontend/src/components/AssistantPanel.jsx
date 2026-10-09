import { useState, useRef, useEffect } from 'react'
import { MessageCircle, Send, Sparkles, ShieldAlert, Wrench, RotateCcw, Trash2, Cpu, Activity, AlertTriangle, CheckCircle } from 'lucide-react'

function parseInlineFormatting(text) {
  if (!text) return text
  // Match bold (**...**), code (`...`), status badges, and markdown links [text](url)
  const regex = /(\*\*.*?\*\*|`.*?`|\[(?:CRITICAL|WARNING|CAUTION|NORMAL|DEAD \/ DEEPLY DISCHARGED|ELEVATED|OVERCHARGING|HEALTHY|DANGEROUSLY LOW|REAL-TIME ANALYSIS INITIATED|COUNTERFACTUAL SIMULATION)\]|\[.*?\]\(.*?\))/g
  const parts = text.split(regex)

  return parts.map((part, i) => {
    if (!part) return null
    if (part.startsWith('**') && part.endsWith('**')) {
      return <strong key={i} className="font-semibold text-cyan-300">{part.slice(2, -2)}</strong>
    }
    if (part.startsWith('`') && part.endsWith('`')) {
      return <code key={i} className="msg-code">{part.slice(1, -1)}</code>
    }
    const linkMatch = part.match(/^\[(.*?)\]\((.*?)\)$/)
    if (linkMatch) {
      return <a key={i} href={linkMatch[2]} target="_blank" rel="noopener noreferrer" className="text-cyan-400 underline decoration-cyan-400/30 underline-offset-2 hover:decoration-cyan-400">{linkMatch[1]}</a>
    }
    if (part.startsWith('[') && part.endsWith(']')) {
      const badge = part.slice(1, -1)
      let badgeClass = 'badge-caution'
      if (badge.includes('CRITICAL') || badge.includes('DEAD') || badge.includes('DANGEROUSLY')) {
        badgeClass = 'badge-critical'
      } else if (badge.includes('WARNING') || badge.includes('ELEVATED') || badge.includes('OVERCHARGING')) {
        badgeClass = 'badge-warning'
      } else if (badge.includes('NORMAL') || badge.includes('HEALTHY')) {
        badgeClass = 'badge-normal'
      }
      return <span key={i} className={`assistant-inline-badge ${badgeClass}`}>{badge}</span>
    }
    return part
  })
}

function renderFormattedMessage(text) {
  if (!text) return null
  const lines = text.split('\n')
  const elements = []
  let listItems = []

  const flushList = () => {
    if (listItems.length > 0) {
      elements.push(
        <ul key={`list-${elements.length}`} className="assistant-msg-list">
          {listItems.map((item, idx) => (
            <li key={idx}>{parseInlineFormatting(item)}</li>
          ))}
        </ul>
      )
      listItems = []
    }
  }

  lines.forEach((line, index) => {
    const trimmed = line.trim()
    if (!trimmed) {
      flushList()
      return
    }

    if (trimmed.startsWith('### ')) {
      flushList()
      elements.push(
        <h4 key={`heading-${index}`} className="assistant-msg-heading">
          {parseInlineFormatting(trimmed.replace(/^###\s*/, ''))}
        </h4>
      )
    } else if (trimmed.startsWith('- ') || trimmed.startsWith('* ')) {
      listItems.push(trimmed.replace(/^[-*]\s*/, ''))
    } else {
      flushList()
      elements.push(
        <p key={`para-${index}`} className="assistant-msg-para">
          {parseInlineFormatting(trimmed)}
        </p>
      )
    }
  })
  flushList()
  return elements
}

export default function AssistantPanel({
  onAsk,
  conversation = [],
  diagnosis = null,
  vehicle = {},
  selectedSymptoms = [],
  onClear = () => {},
}) {
  const [question, setQuestion] = useState('')
  const [busy, setBusy] = useState(false)
  const messagesEndRef = useRef(null)

  const topFault = diagnosis?.top_faults?.[0]
  const action = diagnosis?.recommended_action
  const firstSymptom = selectedSymptoms?.[0] || diagnosis?.symptoms?.[0]
  const vehicleName = [vehicle.year, vehicle.make, vehicle.model].filter(Boolean).join(' ') || 'Vehicle'

  // Dynamic context-aware prompts based on the current live diagnosis data
  const dynamicPrompts = []
  if (diagnosis && topFault) {
    dynamicPrompts.push('Can I safely drive?')
    dynamicPrompts.push(`Why is ${topFault.label} suspected?`)
    dynamicPrompts.push('What parts need replacement?')
    if (firstSymptom) {
      dynamicPrompts.push(`What if ${firstSymptom.replace(/_/g, ' ')} is absent?`)
    }
    dynamicPrompts.push('Check sensor telemetry')
    dynamicPrompts.push('Is it the battery?')
  } else if (selectedSymptoms.length > 0) {
    dynamicPrompts.push('Diagnose with currently selected symptoms')
    dynamicPrompts.push('Can I continue driving?')
    dynamicPrompts.push('What parts could be failing?')
    dynamicPrompts.push('What are the risks if ignored?')
  } else {
    dynamicPrompts.push('Engine overheating and blowing white smoke')
    dynamicPrompts.push('Clicking noise with dim headlights')
    dynamicPrompts.push('Brakes squealing and soft brake pedal')
    dynamicPrompts.push('What causes sudden loss of engine power?')
  }

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [conversation, busy])

  async function submit(event) {
    event?.preventDefault?.()
    const query = question.trim()
    if (!query || busy) return
    setBusy(true)
    setQuestion('')
    try {
      await onAsk(query)
    } finally {
      setBusy(false)
    }
  }

  function handlePromptClick(promptText) {
    setQuestion(promptText)
  }

  return (
    <section className="glass-panel assistant-panel">
      {/* Panel Top Header */}
      <div className="assistant-heading">
        <div className="assistant-icon">
          <MessageCircle size={17} />
        </div>
        <div>
          <span className="section-index">04 / REAL-TIME ASSISTANT</span>
          <h2>AI Diagnostic Copilot</h2>
        </div>
        <div className="assistant-header-actions">
          {conversation.length > 0 && (
            <button
              type="button"
              className="assistant-clear-btn"
              onClick={onClear}
              title="Clear chat history"
              aria-label="Clear chat history"
            >
              <Trash2 size={13} />
              <span>Clear</span>
            </button>
          )}
          <span className="assistant-spark"><Sparkles size={15} /></span>
        </div>
      </div>

      {/* Real-Time Diagnostic Context Strip */}
      <div className="assistant-hud-strip">
        <div className="hud-badge-left">
          <span className={`hud-dot ${diagnosis ? 'dot-active' : 'dot-standby'}`} />
          <span className="hud-label">
            {diagnosis ? 'LIVE DIAGNOSIS DATA LINKED' : (selectedSymptoms.length > 0 ? `${selectedSymptoms.length} EVIDENCE SIGNALS STAGED` : 'READY FOR INPUT')}
          </span>
        </div>
        <div className="hud-details">
          {diagnosis && topFault ? (
            <>
              <span className="hud-target">{vehicleName}:</span>
              <strong className="hud-fault">{topFault.label}</strong>
              <span className="hud-prob">({(topFault.probability * 100).toFixed(0)}%)</span>
              <span className={`hud-action-pill action-${action?.id || 'inspect'}`}>
                {action?.label || 'Inspect soon'}
              </span>
            </>
          ) : (
            <span className="hud-hint">Ask anything or describe symptoms in real time</span>
          )}
        </div>
      </div>

      {/* Messages Scroll Area */}
      <div className="assistant-messages" aria-live="polite">
        {conversation.length === 0 ? (
          <div className="assistant-empty">
            <div className="assistant-empty-lead">
              <Cpu size={24} className="assistant-empty-icon" />
              <strong>Real-Time Automotive Intelligence</strong>
              <p>
                {diagnosis
                  ? `Your diagnosis for ${vehicleName} is loaded. Ask me about driving safety, component proofs, or simulate what-if scenarios.`
                  : 'Ask a diagnostic question or pick a scenario below to start instantaneous inference.'}
              </p>
            </div>
            <div className="prompt-list-wrap">
              <span className="prompt-kicker">SUGGESTED REAL-TIME QUERIES:</span>
              <div className="prompt-list">
                {dynamicPrompts.map((prompt) => (
                  <button
                    key={prompt}
                    type="button"
                    onClick={() => handlePromptClick(prompt)}
                  >
                    <span>{prompt}</span>
                  </button>
                ))}
              </div>
            </div>
          </div>
        ) : (
          conversation.map((item, index) => (
            <div className={`message-row ${item.role}`} key={`${index}-${item.role}`}>
              <span className="message-avatar">
                {item.role === 'assistant' ? 'AI' : 'YOU'}
              </span>
              <div className="message-body">
                {item.role === 'assistant' ? (
                  <>
                    {renderFormattedMessage(item.text)}
                    {item.sources && item.sources.length > 0 && (
                      <div className="assistant-sources mt-4 pt-4 border-t border-slate-700/50">
                        <div className="text-xs font-semibold text-slate-400 mb-2 flex items-center gap-1">
                          <Activity size={12} /> WEB SOURCES USED
                        </div>
                        <ul className="space-y-1">
                          {item.sources.map((src, i) => (
                            <li key={i} className="text-sm">
                              <a href={src.url} target="_blank" rel="noopener noreferrer" className="text-cyan-400 hover:underline">
                                [{i+1}] {src.title || src.url}
                              </a>
                              {src.publisher && <span className="text-slate-500 ml-2">- {src.publisher}</span>}
                              {src.published_date && <span className="text-slate-500 ml-2">({src.published_date})</span>}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </>
                ) : (
                  <p>{item.text}</p>
                )}
              </div>
            </div>
          ))
        )}

        {busy && (
          <div className="message-row assistant busy-row">
            <span className="message-avatar">AI</span>
            <div className="message-body typing-bubble">
              <span className="typing-dot" />
              <span className="typing-dot" />
              <span className="typing-dot" />
              <span className="typing-text">Evaluating reasoning and retrieving web evidence...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Quick Prompts Bar if conversation already started */}
      {conversation.length > 0 && (
        <div className="mini-prompts-bar">
          {dynamicPrompts.slice(0, 3).map((prompt) => (
            <button
              key={prompt}
              type="button"
              className="mini-prompt-chip"
              onClick={() => handlePromptClick(prompt)}
            >
              {prompt}
            </button>
          ))}
        </div>
      )}

      {/* Input Form */}
      <form className="assistant-form" onSubmit={submit}>
        <input
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder={diagnosis ? "Ask about safety, why this fault, parts, or what-if scenarios..." : "Ask a question or describe your vehicle symptoms..."}
          aria-label="Ask a vehicle diagnostic question"
          disabled={busy}
        />
        <button
          type="submit"
          aria-label="Send question"
          disabled={busy || !question.trim()}
        >
          <Send size={15} />
        </button>
      </form>

      {/* Footnote */}
      <div className="assistant-footnote">
        <span className="tiny-led is-active" />
        <span>Inference engine: Horn clause FOPL + Bayesian Network + Decision Utilities</span>
      </div>
    </section>
  )
}

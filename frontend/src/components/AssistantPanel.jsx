import { useState } from 'react'
import { MessageCircle, Send, Sparkles } from 'lucide-react'

const prompts = ['Why this fault?', 'What if a symptom is absent?', 'Is it the battery?']

export default function AssistantPanel({ onAsk, conversation, disabled }) {
  const [question, setQuestion] = useState('')
  const [busy, setBusy] = useState(false)
  async function submit(event) {
    event.preventDefault()
    if (!question.trim() || busy || disabled) return
    setBusy(true)
    try {
      await onAsk(question.trim())
      setQuestion('')
    } finally {
      setBusy(false)
    }
  }
  return (
    <section className="glass-panel assistant-panel">
      <div className="assistant-heading"><div className="assistant-icon"><MessageCircle size={16} /></div><div><span className="section-index">04 / FOLLOW-UP</span><h2>Ask the assistant</h2></div><span className="assistant-spark"><Sparkles size={15} /></span></div>
      <div className="assistant-messages" aria-live="polite">
        {!conversation.length ? <div className="assistant-empty"><span>Start with a question about your readout.</span><div className="prompt-list">{prompts.map((prompt) => <button key={prompt} type="button" onClick={() => setQuestion(prompt === 'What if a symptom is absent?' ? 'What if low coolant is absent?' : prompt)}>{prompt}</button>)}</div></div> : conversation.map((item, index) => <div className={`message-row ${item.role}`} key={`${index}-${item.text}`}><span className="message-avatar">{item.role === 'assistant' ? 'AI' : 'YOU'}</span><p>{item.text}</p></div>)}
      </div>
      <form className="assistant-form" onSubmit={submit}><input value={question} onChange={(event) => setQuestion(event.target.value)} placeholder={disabled ? 'Run a diagnosis to start' : 'Ask a follow-up…'} aria-label="Ask a follow-up question" disabled={disabled || busy} /><button type="submit" aria-label="Send question" disabled={disabled || busy || !question.trim()}><Send size={15} /></button></form>
      <div className="assistant-footnote"><span className="tiny-led" /> Answers use your current symptom set</div>
    </section>
  )
}

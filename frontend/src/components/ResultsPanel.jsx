import { useState } from 'react'
import { motion } from 'framer-motion'
import { AlertTriangle, ArrowUpRight, ChevronDown, CircleGauge, CircleHelp, Clock3, KeyRound, LoaderCircle, ShieldAlert, Wrench } from 'lucide-react'
import KnowledgeGraph from './KnowledgeGraph.jsx'

const severityScale = ['low', 'medium', 'high', 'critical']

function ConfidenceGauge({ value = 0 }) {
  const percent = Math.round(value * 100)
  return <div className="confidence-widget"><div className="confidence-ring" style={{ '--score': `${percent * 3.6}deg` }}><div className="confidence-inner"><strong>{percent}<small>%</small></strong><span>CONFIDENCE</span></div></div><span className="gauge-caption">BAYESIAN POSTERIOR</span></div>
}

export default function ResultsPanel({ diagnosis, loading, onRun, selectedCount, onWhy }) {
  const [whyOpen, setWhyOpen] = useState(false)
  const [utilityOpen, setUtilityOpen] = useState(true)
  const severityIndex = diagnosis ? severityScale.indexOf(diagnosis.severity) : -1
  const maxMagnitude = Math.max(...(diagnosis?.expected_utilities || []).map((item) => Math.abs(item.value)), 1)
  return (
    <section className="glass-panel results-panel">
      <div className="panel-heading results-title"><div><span className="section-index">03 / ANALYSIS</span><h2>Diagnosis</h2></div><span className={`analysis-state ${diagnosis ? 'complete' : ''}`}><i />{diagnosis ? 'COMPLETE' : 'STANDBY'}</span></div>
      {loading ? <motion.div key="loading" className="starting-state" initial={{ opacity: 0 }} animate={{ opacity: 1 }}><div className="starting-orbit"><LoaderCircle size={46} /><span /></div><span className="section-index">IGNITION SEQUENCE</span><strong>Reading the signals</strong><p>Matching rules · updating probabilities</p><div className="scan-line" /></motion.div> : diagnosis ? <motion.div key="results" className="result-content" initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
          <div className="lead-result"><ConfidenceGauge value={diagnosis.confidence} /><div className="lead-meta"><span className="eyebrow">MOST LIKELY FAULT</span><h3>{diagnosis.top_faults[0].label}</h3><p>{diagnosis.top_faults[0].system} system <ArrowUpRight size={13} /></p><span className={`severity-pill severity-${diagnosis.severity}`}><i />{diagnosis.severity.toUpperCase()} SEVERITY</span></div></div>
          <div className="severity-meter"><div className="meter-label"><span>RISK LEVEL</span><span>{diagnosis.severity.toUpperCase()}</span></div><div className="meter-track">{severityScale.map((level, index) => <i key={level} className={`${index <= severityIndex ? `meter-${diagnosis.severity}` : ''}`} />)}</div><div className="meter-caption"><span>MONITOR</span><span>STOP SAFELY</span></div></div>
          <div className="fault-list"><div className="subsection-title"><span>PROBABILITY RANKING</span><span>TOP {diagnosis.top_faults.length}</span></div>{diagnosis.top_faults.map((fault, index) => <div className="fault-row" key={fault.id}><div className="fault-row-head"><span className="fault-rank">0{index + 1}</span><strong>{fault.label}</strong><b>{Math.round(fault.probability * 100)}<small>%</small></b></div><div className="probability-track"><motion.i initial={{ width: 0 }} animate={{ width: `${fault.probability * 100}%` }} transition={{ duration: 0.65, delay: index * 0.1 }} /></div></div>)}</div>
          <div className="recommendation"><div className="recommendation-icon"><Wrench size={16} /></div><div><span className="eyebrow">RECOMMENDED NEXT STEP</span><strong>{diagnosis.recommended_action.label}</strong><small>Highest expected utility · {diagnosis.recommended_action.expected_utility > 0 ? '+' : ''}{diagnosis.recommended_action.expected_utility}</small></div><AlertTriangle size={15} className="recommendation-mark" /></div>
          <div className="utility-section"><button type="button" className="accordion-trigger utility-trigger" aria-expanded={utilityOpen} onClick={() => setUtilityOpen(!utilityOpen)}><span>DECISION UTILITIES <small>EXPECTED VALUE & COST</small></span><ChevronDown size={15} className={utilityOpen ? 'chevron-open' : ''} /></button>{utilityOpen && <div className="utility-chart">{diagnosis.expected_utilities.map((item) => { const best = item.action === diagnosis.recommended_action.id; const width = `${Math.max(3, (Math.abs(item.value) / maxMagnitude) * 50)}%`; return <div className="utility-row" key={item.action}><span>{item.label}</span><div className="utility-track" style={{ position: 'relative', background: 'linear-gradient(90deg, rgba(255, 101, 113, .13) 0 49.7%, rgba(185, 206, 210, .24) 49.7% 50.3%, rgba(118, 219, 176, .12) 50.3% 100%)' }}><i className={best ? 'utility-best' : ''} style={{ position: 'absolute', left: item.value >= 0 ? '50%' : 'auto', right: item.value < 0 ? '50%' : 'auto', width, background: best ? 'var(--mint)' : item.value < 0 ? 'var(--red)' : '#4c7a82' }} /></div><b>{item.value > 0 ? '+' : ''}{item.value} <small style={{ color: 'var(--text-muted)', fontSize: '0.8em', marginLeft: '6px', fontWeight: 'normal' }}>est. ${Math.round(item.cost)}</small></b></div> })}</div>}</div>
          <div className="why-section">
            <button type="button" className="accordion-trigger" aria-expanded={whyOpen} onClick={() => { const nextOpen = !whyOpen; setWhyOpen(nextOpen); if (nextOpen) onWhy?.() }}>
              <span><CircleHelp size={15} /> WHY THIS FAULT?</span>
              <ChevronDown size={15} className={whyOpen ? 'chevron-open' : ''} />
            </button>
            {whyOpen && <div className="why-content">
              <p className="why-intro">The estimate is supported by the observed signals and the rules below.</p>
              {diagnosis.top_faults[0].contributing_symptoms.length > 0 && <div className="why-block">
                <span className="eyebrow">TOP CONTRIBUTING SIGNALS</span>
                <div className="contributor-tags">{diagnosis.top_faults[0].contributing_symptoms.map((symptom) => <span key={symptom}>{symptom.replaceAll('_', ' ')}</span>)}</div>
              </div>}
              {diagnosis.top_faults[0].fired_rules.length > 0 ? diagnosis.top_faults[0].fired_rules.map((rule) => <div className="rule-item" key={rule.rule_id}><b>{rule.rule_id}</b><span>{rule.explanation}</span></div>) : <p className="no-rule">No complete FOPL rule fired; this ranking is based on Bayesian evidence.</p>}
              <div className="trace-block">
                <span className="eyebrow">UNIFICATION SUBSTITUTIONS</span>
                {diagnosis.unification_steps.length ? diagnosis.unification_steps.map((step, index) => <p key={`${step.rule_id}-${index}`}><b>{step.rule_id}</b><code>{step.variable.replace('?', '')} = {step.value}</code></p>) : <p>No variable substitutions were needed.</p>}
              </div>
              <details className="posterior-details">
                <summary><span>BAYESIAN POSTERIOR TABLE</span><small>{diagnosis.posterior_table.length} fault hypotheses</small></summary>
                <div className="posterior-table-wrap"><table><thead><tr><th>FAULT</th><th>POSTERIOR</th><th>RISK</th></tr></thead><tbody>{diagnosis.posterior_table.map((row) => <tr key={row.fault}><td>{row.label}</td><td>{(row.probability * 100).toFixed(1)}%</td><td>{row.severity}</td></tr>)}</tbody></table></div>
              </details>
              
              <div className="trace-block" style={{ marginTop: '15px' }}>
                 <span className="eyebrow">INTERACTIVE KNOWLEDGE GRAPH</span>
                 <p className="why-intro">Visual representation of logical FOPL inferences from symptoms to hypotheses.</p>
                 <KnowledgeGraph diagnosis={diagnosis} />
              </div>

              <div className="why-link-row"><span>{diagnosis.unification_steps.length} substitution(s) · {diagnosis.fired_rules.length} rule(s)</span><button type="button" onClick={onWhy}>Ask assistant <ArrowUpRight size={13} /></button></div>
            </div>}
          </div>
          <div className="method-note"><CircleGauge size={14} /><span>Model estimate, not a confirmed diagnosis.</span></div>
        </motion.div> : <motion.div key="empty" className="empty-diagnosis" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}><div className="empty-gauge"><CircleGauge size={34} /><span>--</span></div><span className="eyebrow">AWAITING INPUT</span><strong>Your readout appears here</strong><p>Select symptoms to calculate likely faults and the safest next step.</p><div className="empty-divider" /><span className="empty-stat"><span><i className="tiny-led" /> 14 FAULT MODELS</span><span>40 SIGNALS</span></span></motion.div>}
      {!loading && <motion.button whileTap={{ scale: 0.98 }} whileHover={{ y: -1 }} className="ignition-button" type="button" onClick={onRun} disabled={selectedCount === 0}><span className="ignition-key"><KeyRound size={17} /></span><span><strong>{diagnosis ? 'RUN AGAIN' : 'RUN DIAGNOSIS'}</strong><small>{selectedCount ? `${selectedCount} signal${selectedCount === 1 ? '' : 's'} selected` : 'Select at least one symptom'}</small></span><span className="ignition-arrow">↗</span></motion.button>}
      {loading && <div className="loading-button"><LoaderCircle size={17} /> CALCULATING</div>}
      <div className="safety-footer"><ShieldAlert size={14} /><span>{diagnosis?.safety_note || 'For safety-critical symptoms, stop in a safe place and contact a qualified technician.'}</span></div>
    </section>
  )
}

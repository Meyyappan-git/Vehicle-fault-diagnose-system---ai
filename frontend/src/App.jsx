import { useEffect, useState } from 'react'
import { ArrowLeft, ArrowRight, Check, Heart, ThumbsDown, ThumbsUp } from 'lucide-react'
import AssistantPanel from './components/AssistantPanel.jsx'
import DashboardHeader from './components/DashboardHeader.jsx'
import ResultsPanel from './components/ResultsPanel.jsx'
import SymptomSelector from './components/SymptomSelector.jsx'
import VehiclePanel from './components/VehiclePanel.jsx'
import { askAssistant, diagnose, getHealth, getMeta } from './api/client.js'

const initialVehicle = { make: '', model: '', year: '', mileage: '', fuel_type: '' }
const workflow = [
  { id: 'vehicle', label: 'Vehicle', heading: 'Tell us about your vehicle', detail: 'A few details help frame the diagnostic context.' },
  { id: 'symptoms', label: 'Symptoms', heading: 'Choose the warning signs', detail: 'Select the signals you can confirm, then add any useful context.' },
  { id: 'diagnosis', label: 'Diagnosis', heading: 'Review the diagnostic readout', detail: 'Compare the leading hypotheses and recommended next action.' },
  { id: 'assistant', label: 'Assistant', heading: 'Explore the reasoning', detail: 'Ask why a fault ranked highly or test a what-if scenario.' },
]

export default function App() {
  const [meta, setMeta] = useState({ symptoms: [], systems: [] })
  const [online, setOnline] = useState(false)
  const [activePage, setActivePage] = useState('vehicle')
  const [vehicle, setVehicle] = useState(initialVehicle)
  const [sensorValues, setSensorValues] = useState({ coolant_temp_c: '', battery_voltage_v: '', oil_pressure_psi: '' })
  const [selected, setSelected] = useState([])
  const [absent, setAbsent] = useState([])
  const [notes, setNotes] = useState('')
  const [search, setSearch] = useState('')
  const [activeSystem, setActiveSystem] = useState('All')
  const [diagnosis, setDiagnosis] = useState(null)
  const [lastPayload, setLastPayload] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [conversation, setConversation] = useState([])
  const [feedback, setFeedback] = useState(() => localStorage.getItem('vfa-feedback') || '')

  useEffect(() => {
    Promise.all([getMeta(), getHealth()]).then(([catalog]) => {
      setMeta(catalog)
      setOnline(true)
    }).catch(() => setOnline(false))
  }, [])

  function changeVehicle(field, value) {
    setVehicle((current) => ({ ...current, [field]: value }))
  }

  function changeSensor(field, value) {
    setSensorValues((current) => ({ ...current, [field]: value }))
  }

  function toggleSymptom(symptom) {
    setSelected((current) => current.includes(symptom) ? current.filter((item) => item !== symptom) : [...current, symptom])
    setAbsent((current) => current.filter((item) => item !== symptom))
  }

  function buildPayload() {
    const vehicleData = {
      ...vehicle,
      year: vehicle.year ? Number(vehicle.year) : null,
      mileage: vehicle.mileage ? Number(vehicle.mileage.replaceAll(',', '')) : null,
    }
    return {
      symptoms: selected,
      absent_symptoms: absent,
      free_text: notes,
      vehicle: vehicleData,
      vehicle_id: [vehicle.make, vehicle.model, vehicle.year].filter(Boolean).join('-').toLowerCase() || 'vehicle',
      sensor_values: Object.fromEntries(Object.entries(sensorValues).filter(([, value]) => value !== '').map(([key, value]) => [key, Number(value)])),
    }
  }

  async function runDiagnosis() {
    setLoading(true)
    setError('')
    try {
      const payload = buildPayload()
      const result = await diagnose(payload)
      setDiagnosis(result)
      setLastPayload(payload)
      setConversation([])
    } catch (problem) {
      setError(problem.message)
    } finally {
      setLoading(false)
    }
  }

  async function sendQuestion(question) {
    if (!lastPayload || !diagnosis) return
    setConversation((current) => [...current, { role: 'user', text: question }])
    try {
      const result = await askAssistant(question, lastPayload, diagnosis)
      if (result.diagnosis) setDiagnosis(result.diagnosis)
      setConversation((current) => [...current, { role: 'assistant', text: result.answer }])
    } catch (problem) {
      setConversation((current) => [...current, { role: 'assistant', text: problem.message }])
    }
  }

  function saveFeedback(value) {
    localStorage.setItem('vfa-feedback', value)
    setFeedback(value)
  }

  function clearEvidence() {
    setSelected([])
    setAbsent([])
    setNotes('')
    setDiagnosis(null)
    setLastPayload(null)
    setConversation([])
    setError('')
  }

  const pageIndex = workflow.findIndex((page) => page.id === activePage)
  const page = workflow[pageIndex]
  const evidenceCount = selected.length + (notes.trim() ? 1 : 0)
  const nextPage = workflow[Math.min(pageIndex + 1, workflow.length - 1)]
  const previousPage = workflow[Math.max(pageIndex - 1, 0)]

  return (
    <div className="app-shell">
      <div className="ambient ambient-one" /><div className="ambient ambient-two" /><div className="road-streak road-streak-one" /><div className="road-streak road-streak-two" />
      <DashboardHeader online={online} />
      <nav className="workflow-nav" aria-label="Diagnosis pages">
        {workflow.map((item, index) => <button key={item.id} type="button" className={`workflow-step ${activePage === item.id ? 'active' : ''} ${index < pageIndex ? 'complete' : ''}`} aria-current={activePage === item.id ? 'step' : undefined} onClick={() => setActivePage(item.id)}>
          <span className="workflow-number">{index < pageIndex ? <Check size={13} /> : `0${index + 1}`}</span><span>{item.label}</span>
        </button>)}
      </nav>
      <section className="page-intro"><div><span className="intro-kicker"><i /> INTELLIGENT VEHICLE TRIAGE <span className="intro-divider">/</span> PAGE 0{pageIndex + 1}</span><h1>{page.heading}</h1><p>{page.detail}</p></div><div className="intro-mark"><span>STEP</span><strong>0{pageIndex + 1}</strong><small>OF 04</small></div></section>
      {!online && <div className="connection-banner" role="status">Backend not connected. Start the FastAPI service at <code>localhost:8000</code> to load signals and run a diagnosis.</div>}
      {error && <div className="error-banner" role="alert"><span>{error}</span><button type="button" onClick={() => setError('')}>Dismiss</button></div>}
      <main key={activePage} className={`page-stage page-${activePage}`}>
          {activePage === 'vehicle' && <VehiclePanel vehicle={vehicle} onChange={changeVehicle} sensorValues={sensorValues} onSensorChange={changeSensor} onZone={(system) => setActiveSystem(system)} activeSystem={activeSystem} />}
          {activePage === 'symptoms' && <>
            <SymptomSelector symptoms={meta.symptoms} systems={meta.systems} selected={selected} onToggle={toggleSymptom} activeSystem={activeSystem} onSystemChange={setActiveSystem} search={search} onSearchChange={setSearch} notes={notes} onNotesChange={setNotes} />
            <section className="signal-summary"><span className="summary-led" /><span>LIVE INPUT</span><b>{selected.length.toString().padStart(2, '0')}</b><span>CONFIRMED SIGNALS</span><i /><span>{activeSystem === 'All' ? 'ALL SYSTEMS' : activeSystem.toUpperCase()}</span><span className="summary-spacer" /><button type="button" onClick={clearEvidence} disabled={!selected.length && !notes}>CLEAR ALL</button></section>
          </>}
          {activePage === 'diagnosis' && <>
            <ResultsPanel diagnosis={diagnosis} loading={loading} onRun={runDiagnosis} selectedCount={evidenceCount} onWhy={() => diagnosis && sendQuestion('Why this fault?')} />
            {diagnosis && <div className="feedback-strip page-feedback"><span>{feedback ? 'FEEDBACK RECORDED' : 'WAS THIS READOUT USEFUL?'}</span><button type="button" aria-label="Mark diagnosis helpful" title="Helpful" className={feedback === 'helpful' ? 'feedback-active' : ''} onClick={() => saveFeedback('helpful')}><ThumbsUp size={14} />{feedback === 'helpful' && <Check size={12} />}</button><button type="button" aria-label="Mark diagnosis not helpful" title="Not helpful" className={feedback === 'not-helpful' ? 'feedback-active' : ''} onClick={() => saveFeedback('not-helpful')}><ThumbsDown size={14} />{feedback === 'not-helpful' && <Check size={12} />}</button><Heart size={13} className="footer-heart" /></div>}
          </>}
          {activePage === 'assistant' && <AssistantPanel onAsk={sendQuestion} conversation={conversation} disabled={!diagnosis} />}
          <div className="page-actions">
            {pageIndex > 0 ? <button type="button" className="page-back" onClick={() => setActivePage(previousPage.id)}><ArrowLeft size={15} /> BACK</button> : <span className="page-back-placeholder">VEHICLE INTAKE</span>}
            <span className="page-counter">STEP 0{pageIndex + 1} <i /> 04</span>
            <button type="button" className="page-next" onClick={() => setActivePage(nextPage.id)}>{pageIndex === workflow.length - 1 ? 'REVIEW DIAGNOSIS' : `CONTINUE TO ${nextPage.label.toUpperCase()}`}<ArrowRight size={15} /></button>
          </div>
      </main>
      <footer className="page-footer"><div className="footer-method"><span className="footer-led" /><span>REASONING PIPELINE <b>FOPL</b><i>→</i><b>BAYES</b><i>→</i><b>DECISION</b></span></div><div className="legal-note">EDUCATIONAL ESTIMATE · CONFIRM WITH A QUALIFIED TECHNICIAN</div></footer>
    </div>
  )
}

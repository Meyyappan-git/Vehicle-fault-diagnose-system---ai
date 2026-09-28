import { AnimatePresence, motion } from 'framer-motion'
import { Activity, AlertCircle, BatteryCharging, Check, Disc3, Droplets, Gauge, Search, Thermometer, X } from 'lucide-react'

const iconBySystem = {
  Engine: Activity, Fuel: Droplets, Cooling: Thermometer, Electrical: BatteryCharging,
  Brakes: Disc3, Transmission: Gauge, Suspension: Activity, Exhaust: Activity, Oil: AlertCircle,
}

export default function SymptomSelector({ symptoms, systems, selected, onToggle, activeSystem, onSystemChange, search, onSearchChange, notes, onNotesChange }) {
  const visible = symptoms.filter((item) => (activeSystem === 'All' || item.system === activeSystem) && `${item.label} ${item.id}`.toLowerCase().includes(search.toLowerCase()))
  const countFor = (system) => symptoms.filter((item) => item.system === system && selected.includes(item.id)).length
  return (
    <section className="glass-panel symptom-panel">
      <div className="panel-heading symptom-heading"><div><span className="section-index">02 / SIGNALS</span><h2>What are you noticing?</h2></div><div className="selected-count"><strong>{selected.length.toString().padStart(2, '0')}</strong><span>SELECTED</span></div></div>
      <div className="symptom-tools">
        <label className="search-box"><Search size={16} /><input value={search} onChange={(event) => onSearchChange(event.target.value)} aria-label="Search symptoms" placeholder="Search signals" />{search && <button type="button" aria-label="Clear search" onClick={() => onSearchChange('')}><X size={14} /></button>}</label>
        <div className="system-tabs" role="tablist" aria-label="Symptom systems">
          {['All', ...systems].map((system) => <button type="button" key={system} role="tab" aria-selected={activeSystem === system} className={activeSystem === system ? 'system-tab active' : 'system-tab'} onClick={() => onSystemChange(system)}>{system}<span>{system === 'All' ? selected.length : countFor(system)}</span></button>)}
        </div>
      </div>
      <div className="symptom-list" aria-live="polite">
        <AnimatePresence mode="popLayout">
          {visible.map((item) => {
            const Icon = iconBySystem[item.system] || Activity
            const checked = selected.includes(item.id)
            return <motion.button layout initial={{ opacity: 0, y: 7 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, scale: 0.96 }} transition={{ duration: 0.17 }} key={item.id} type="button" aria-pressed={checked} className={`symptom-chip ${checked ? 'is-selected' : ''} system-${item.system.toLowerCase()}`} onClick={() => onToggle(item.id)}>
              <Icon size={15} strokeWidth={1.8} /><span>{item.label}</span><i className="chip-check">{checked ? <Check size={12} /> : '+'}</i>
            </motion.button>
          })}
        </AnimatePresence>
        {!visible.length && <div className="empty-filter">No matching signals in this system.</div>}
      </div>
      <label className="description-field"><span>DRIVER NOTES <small>OPTIONAL · KEYWORDS ARE MAPPED AUTOMATICALLY</small></span><span className="description-input-wrap"><textarea id="driver-notes" value={notes} onChange={(event) => onNotesChange(event.target.value)} placeholder="Add a little context, e.g. ‘the engine runs hot and I smell coolant’" rows="2" /></span></label>
      <p className="selector-footnote"><span className="footnote-spark">✳</span> Select every symptom you can confirm. More signal, clearer picture.</p>
    </section>
  )
}

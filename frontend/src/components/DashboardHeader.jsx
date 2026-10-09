import { motion } from 'framer-motion'
import { Activity, CircleHelp, Gauge } from 'lucide-react'

export default function DashboardHeader({ online }) {
  return (
    <header className="topbar">
      <div className="brand-lockup">
        <div className="brand-mark"><Activity size={20} strokeWidth={2.4} /></div>
        <div>
          <div className="brand-kicker">FIELDNOTE <span>·</span> MOBILITY LAB</div>
          <div className="brand-title">Vehicle <span>diagnostics</span></div>
        </div>
      </div>
      <div className="header-status"><span className={`status-dot ${online ? 'is-online' : ''}`} />{online ? 'SYSTEM ONLINE' : 'CONNECTING'}</div>
      <div className="cluster" aria-label="Diagnostic system ready gauge">
        <div className="cluster-copy"><span className="eyebrow">TRIAGE MODE</span><strong>READY</strong></div>
        <div className="mini-gauge">
          <div className="mini-gauge-track" />
          <motion.div className="mini-needle" animate={{ rotate: online ? 22 : -42 }} transition={{ type: 'spring', stiffness: 40, damping: 12 }} />
          <div className="mini-hub" />
          <Gauge className="gauge-icon" size={15} />
        </div>
        <div className="cluster-divider" />
        <button className="icon-button help-button" type="button" title="About this diagnostic tool" aria-label="About this diagnostic tool"><CircleHelp size={18} /></button>
      </div>
    </header>
  )
}

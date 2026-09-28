import { useState } from 'react'
import { CarFront, ChevronDown, Disc3, Zap } from 'lucide-react'

const zones = [
  { system: 'Engine', x: 117, y: 35, label: 'ENGINE' },
  { system: 'Electrical', x: 117, y: 72, label: 'POWER' },
  { system: 'Transmission', x: 117, y: 108, label: 'DRIVE' },
  { system: 'Brakes', x: 66, y: 52, label: 'BRAKES' },
  { system: 'Brakes', x: 168, y: 52, label: 'BRAKES' },
  { system: 'Suspension', x: 66, y: 123, label: 'CHASSIS' },
  { system: 'Suspension', x: 168, y: 123, label: 'CHASSIS' },
  { system: 'Exhaust', x: 117, y: 151, label: 'EXHAUST' },
]

export default function VehiclePanel({ vehicle, onChange, sensorValues, onSensorChange, onZone, activeSystem }) {
  const [yearOpen, setYearOpen] = useState(false)
  const currentYear = new Date().getFullYear()
  return (
    <section className="glass-panel vehicle-panel">
      <div className="panel-heading"><div><span className="section-index">01 / VEHICLE</span><h2>Vehicle profile</h2></div><span className="panel-icon"><CarFront size={17} /></span></div>
      <div className="vehicle-fields">
        <label className="field"><span>CAR</span><input value={vehicle.make} onChange={(event) => onChange('make', event.target.value)} placeholder="e.g. Toyota" /></label>
        <label className="field"><span>MODEL</span><input value={vehicle.model} onChange={(event) => onChange('model', event.target.value)} placeholder="e.g. Corolla" /></label>
        <div className="field-row">
          <label className="field"><span>YEAR</span><input type="number" min="1950" max={currentYear + 1} value={vehicle.year} onChange={(event) => onChange('year', event.target.value)} placeholder="2021" /></label>
          <label className="field"><span>MILEAGE</span><input type="number" min="0" value={vehicle.mileage} onChange={(event) => onChange('mileage', event.target.value)} placeholder="42,000" /></label>
        </div>
        <label className="field select-field"><span>FUEL TYPE</span><select value={vehicle.fuel_type} onChange={(event) => onChange('fuel_type', event.target.value)}><option value="">Select fuel type</option><option>Gasoline</option><option>Diesel</option><option>Hybrid</option><option>Electric</option><option>Other</option></select><ChevronDown size={15} /></label>
      </div>
      <details className="sensor-disclosure"><summary>OPTIONAL SENSOR READINGS <ChevronDown size={13} /></summary><div className="sensor-fields"><label>COOLANT °C<input type="number" value={sensorValues.coolant_temp_c} onChange={(event) => onSensorChange('coolant_temp_c', event.target.value)} placeholder="--" /></label><label>BATTERY V<input type="number" step="0.1" value={sensorValues.battery_voltage_v} onChange={(event) => onSensorChange('battery_voltage_v', event.target.value)} placeholder="--" /></label><label>OIL PSI<input type="number" value={sensorValues.oil_pressure_psi} onChange={(event) => onSensorChange('oil_pressure_psi', event.target.value)} placeholder="--" /></label></div><p>Recorded as context; not used to alter probabilities.</p></details>
      <div className="vehicle-divider" />
      <div className="zone-header"><div><span className="section-index">SYSTEM MAP</span><p>Tap a zone to filter</p></div><span className="zone-hint"><Zap size={12} /> LIVE</span></div>
      <div className="car-map-wrap">
        <svg className="car-map" viewBox="0 0 234 188" role="img" aria-label="Top-down clickable vehicle system map">
          <path className="car-shadow" d="M86 8 Q117 -2 148 8 L169 24 Q181 38 182 60 L182 132 Q179 153 163 169 L145 181 Q117 188 89 181 L71 169 Q55 153 52 132 L52 60 Q53 38 65 24 Z" />
          <path className="car-shell" d="M88 12 Q117 2 146 12 L162 25 Q175 39 175 61 L175 129 Q173 148 159 162 L143 174 Q117 181 91 174 L75 162 Q61 148 59 129 L59 61 Q59 39 72 25 Z" />
          <path className="car-glass" d="M79 32 Q117 20 155 32 L163 50 L71 50 Z" />
          <path className="car-glass" d="M72 132 L162 132 L151 153 Q117 165 83 153 Z" />
          <path className="car-hood" d="M72 54 Q117 46 162 54 L163 83 Q117 89 71 83 Z" />
          <path className="car-roof" d="M76 89 Q117 94 158 89 L158 126 Q117 131 76 126 Z" />
          <path className="car-line" d="M74 86 L160 86 M74 129 L160 129" />
          <path className="car-light" d="M69 26 L82 21 M165 26 L152 21 M67 153 L79 158 M167 153 L155 158" />
          <path className="car-wheel" d="M54 46 L64 46 L64 69 L54 69 Z M170 46 L180 46 L180 69 L170 69 Z M54 119 L64 119 L64 143 L54 143 Z M170 119 L180 119 L180 143 L170 143 Z" />
          {zones.map((zone, index) => <g key={`${zone.system}-${index}`} className={`zone-point ${activeSystem === zone.system ? 'zone-active' : ''}`} role="button" tabIndex="0" aria-label={`Filter by ${zone.system}`} onClick={() => onZone(zone.system)} onKeyDown={(event) => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); onZone(zone.system) } }}>
            <circle cx={zone.x} cy={zone.y} r="8" /><circle className="zone-core" cx={zone.x} cy={zone.y} r="2.4" />
          </g>)}
        </svg>
        <div className="zone-legend"><span><i className="legend-dot cyan" />Powertrain</span><span><i className="legend-dot amber" />Safety</span><span><i className="legend-dot mint" />Chassis</span></div>
      </div>
      <div className="vehicle-footer"><span><Disc3 size={14} /> SYSTEMS MAP</span><span>8 ZONES <b>·</b> 40 SIGNALS</span></div>
    </section>
  )
}

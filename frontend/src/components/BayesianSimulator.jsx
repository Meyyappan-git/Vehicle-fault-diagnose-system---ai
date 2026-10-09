import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { diagnose } from '../api/client.js';

export default function BayesianSimulator({ initialDiagnosis, allSymptoms, basePayload }) {
  const [activeSymptoms, setActiveSymptoms] = useState(initialDiagnosis?.symptoms || []);
  const [absentSymptoms, setAbsentSymptoms] = useState(initialDiagnosis?.absent_symptoms || []);
  const [simulatedDiagnosis, setSimulatedDiagnosis] = useState(initialDiagnosis);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Re-run diagnosis when symptoms change
    const runSim = async () => {
      setLoading(true);
      try {
        const payload = {
          ...basePayload,
          symptoms: activeSymptoms,
          absent_symptoms: absentSymptoms
        };
        const res = await diagnose(payload);
        setSimulatedDiagnosis(res);
      } catch(e) {
        console.error("Simulation error", e);
      }
      setLoading(false);
    };
    
    // Only run if it differs from the initial
    runSim();
  }, [activeSymptoms, absentSymptoms]);

  function toggleSymptom(symptomId, state) {
    if (state === 'present') {
      setActiveSymptoms(prev => [...new Set([...prev, symptomId])]);
      setAbsentSymptoms(prev => prev.filter(id => id !== symptomId));
    } else if (state === 'absent') {
      setAbsentSymptoms(prev => [...new Set([...prev, symptomId])]);
      setActiveSymptoms(prev => prev.filter(id => id !== symptomId));
    } else {
      setActiveSymptoms(prev => prev.filter(id => id !== symptomId));
      setAbsentSymptoms(prev => prev.filter(id => id !== symptomId));
    }
  }

  const topFaults = simulatedDiagnosis?.posterior_table || [];

  return (
    <div className="glass-panel" style={{ display: 'flex', gap: '20px', flexDirection: 'column' }}>
      <div className="panel-heading">
        <h2>Live Bayesian Network Simulator</h2>
        <p style={{ color: 'var(--text-muted)' }}>Toggle symptoms to see how the posterior probabilities update.</p>
      </div>
      
      <div style={{ display: 'flex', gap: '20px', flexDirection: 'row' }}>
        <div style={{ flex: 1, maxHeight: '400px', overflowY: 'auto', paddingRight: '10px' }}>
          <h3>Evidence Signals</h3>
          {allSymptoms.map(symp => {
             const isPresent = activeSymptoms.includes(symp.id);
             const isAbsent = absentSymptoms.includes(symp.id);
             return (
               <div key={symp.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px', padding: '8px', background: 'rgba(0,0,0,0.04)', borderRadius: '4px' }}>
                 <span>{symp.label}</span>
                 <div style={{ display: 'flex', gap: '5px' }}>
                   <button 
                     type="button" 
                     onClick={() => toggleSymptom(symp.id, isPresent ? 'none' : 'present')}
                     style={{ padding: '2px 8px', fontSize: '11px', background: isPresent ? 'var(--mint)' : 'transparent', color: isPresent ? '#fff' : 'var(--ink)', border: '1px solid var(--mint)', borderRadius: '4px', cursor: 'pointer' }}
                   >YES</button>
                   <button 
                     type="button" 
                     onClick={() => toggleSymptom(symp.id, isAbsent ? 'none' : 'absent')}
                     style={{ padding: '2px 8px', fontSize: '11px', background: isAbsent ? 'var(--red)' : 'transparent', color: isAbsent ? '#fff' : 'var(--ink)', border: '1px solid var(--red)', borderRadius: '4px', cursor: 'pointer' }}
                   >NO</button>
                 </div>
               </div>
             )
          })}
        </div>

        <div style={{ flex: 1 }}>
           <h3>Posterior Probabilities</h3>
           <div className="fault-list" style={{ marginTop: '10px' }}>
            {topFaults.slice(0, 8).map((fault, index) => (
              <div className="fault-row" key={fault.fault}>
                <div className="fault-row-head">
                  <span className="fault-rank">0{index + 1}</span>
                  <strong>{fault.label}</strong>
                  <b>{Math.round(fault.probability * 100)}<small>%</small></b>
                </div>
                <div className="probability-track">
                  <motion.i 
                    initial={{ width: 0 }} 
                    animate={{ width: `${fault.probability * 100}%` }} 
                    transition={{ duration: 0.3 }} 
                    style={{ background: index === 0 ? 'var(--mint)' : '#4c7a82' }}
                  />
                </div>
              </div>
            ))}
           </div>
        </div>
      </div>
    </div>
  );
}

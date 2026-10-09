import React, { useMemo } from 'react';
import ReactFlow, { Background, Controls, MarkerType } from 'reactflow';
import 'reactflow/dist/style.css';

export default function KnowledgeGraph({ diagnosis }) {
  const { nodes, edges } = useMemo(() => {
    if (!diagnosis) return { nodes: [], edges: [] };

    const initialNodes = [];
    const initialEdges = [];

    // Add Fault Node
    const topFault = diagnosis.top_faults[0];
    if (topFault) {
      initialNodes.push({
        id: topFault.fault,
        data: { label: `Fault: ${topFault.label}` },
        position: { x: 400, y: 50 },
        style: { background: '#e2e8f0', color: '#0f172a', border: '1px solid #059669', borderRadius: '8px', padding: '10px' },
      });
    }

    // Add Symptom Nodes
    const symptoms = diagnosis.symptoms || [];
    symptoms.forEach((symptom, index) => {
      initialNodes.push({
        id: symptom,
        data: { label: `Symptom: ${symptom.replace(/_/g, ' ')}` },
        position: { x: 100 + index * 200, y: 250 },
        style: { background: '#f8fafc', color: '#334155', border: '1px solid #64748b', borderRadius: '8px', padding: '10px' },
      });
    });

    // Link Symptoms to Rules to Fault
    const rules = diagnosis.fired_rules || [];
    rules.forEach((rule, ruleIdx) => {
      const ruleId = `rule-${rule.rule_id}`;
      initialNodes.push({
        id: ruleId,
        data: { label: `Rule: ${rule.rule_id}` },
        position: { x: 400, y: 150 },
        style: { background: '#fecdd3', color: '#881337', border: '1px solid #fda4af', borderRadius: '4px', padding: '5px', fontSize: '10px' },
      });

      // Link Rule to Fault
      const derivedParts = rule.derived.match(/Fault\([^,]+,\s*(.+)\)/);
      if (derivedParts && derivedParts[1]) {
         const faultId = derivedParts[1];
         initialEdges.push({
           id: `e-${ruleId}-${faultId}`,
           source: ruleId,
           target: faultId,
           animated: true,
           style: { stroke: '#059669' },
           markerEnd: { type: MarkerType.ArrowClosed, color: '#059669' },
         });
      }

      // Link Symptoms to Rule (approximate for demo)
      symptoms.forEach((symptom) => {
         // Check if this symptom is part of the rule
         const symptomMatch = new RegExp(`Symptom\\([^,]+,\\s*${symptom}\\)`);
         if (rule.when.some(w => symptomMatch.test(w))) {
           initialEdges.push({
             id: `e-${symptom}-${ruleId}`,
             source: symptom,
             target: ruleId,
             style: { stroke: '#64748b' },
             markerEnd: { type: MarkerType.ArrowClosed, color: '#64748b' },
           });
         }
      });
    });

    return { nodes: initialNodes, edges: initialEdges };
  }, [diagnosis]);

  if (!diagnosis) return null;

  return (
    <div style={{ width: '100%', height: '300px', background: '#f8fafc', borderRadius: '12px', border: '1px solid rgba(0,0,0,0.1)', marginTop: '20px' }}>
      <ReactFlow nodes={nodes} edges={edges} fitView>
        <Background color="#cbd5e1" gap={16} />
        <Controls />
      </ReactFlow>
    </div>
  );
}

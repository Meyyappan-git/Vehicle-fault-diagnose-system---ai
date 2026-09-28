# Vehicle Fault Diagnosis Assistant

An educational SDG 9 course project that turns vehicle symptoms into ranked fault hypotheses and suggested next actions. It combines a from-scratch first-order logic engine, a Bayesian-network model, and a decision utility layer. It is not a replacement for a qualified technician.

## Run locally

Requires Python 3.10+ and Node.js 20+.

Terminal 1, from the repository root:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
python -m uvicorn backend.main:app --reload
```

Terminal 2:

```powershell
cd frontend
npm install
npm run dev
```

Open the Vite URL shown in the terminal (normally http://localhost:5173). The API docs are at http://localhost:8000/docs. On Windows, if script activation is restricted, use `.venv\Scripts\python.exe -m pip install -r backend/requirements.txt` and `.venv\Scripts\python.exe -m uvicorn backend.main:app --reload` instead.

## Architecture

- `backend/kb/` contains the complete symptom, fault, part, rule, CPT, and utility datasets. Every supplied symptom is modeled and each fault links to 3–6 symptoms.
- `backend/logic/unification.py` represents predicates and computes most-general substitutions. `forward_chain.py` applies Horn clauses by Modus Ponens and returns fired-rule traces. `resolution.py` answers ground yes/no queries by refuting the negated query against the entailed closure.
- `backend/nlp/parser.py` maps common phrases and synonyms onto canonical symptom identifiers.
- `backend/prob/bayes_net.py` builds a binary Bayesian network per fault hypothesis using pgmpy when installed; an exact log-space Bayes implementation is included as a runtime fallback. Each fault is a binary hypothesis with associated symptom nodes.
- `backend/prob/decision_net.py` computes expected utilities for Continue driving, Inspect soon, Repair now, and Tow vehicle, then selects the maximum.
- `backend/diagnosis.py` combines evidence parsing, FOPL inference, posterior ranking, and action selection. `backend/qa.py` implements explanation, resolution, and what-if questions.
- `backend/main.py` exposes `/api/meta`, `/api/diagnose`, `/api/qa`, and `/api/health` through FastAPI. The React UI calls these routes directly.

## Model assumptions

The CPT file documents each hand-estimated prior and symptom likelihood. These are illustrative values, not fleet-derived frequencies. For each fault, modeled binary symptoms are conditionally independent given that fault; symptoms may support multiple fault hypotheses. P(symptom | no fault) uses a shared 0.06 false-positive rate. Only symptoms explicitly entered as absent count as negative evidence; all unmentioned symptoms are unknown. Per-fault posteriors are normalized across the 14 modeled hypotheses for a readable ranking, so the displayed confidence is a relative model score, not calibrated real-world certainty. Vehicle make, model, mileage, fuel type, and sensor readings are accepted by the API but do not currently alter the CPTs.

Decision utilities are relative course-project scores, not costs or safety guarantees. The maximum expected-utility action is chosen using the full ranked hypothesis distribution; safety-critical symptom warnings are shown separately.
The optional sensor fields capture coolant temperature, battery voltage, and oil pressure for context; they are currently accepted but do not change posterior probabilities.

## Tests

From the repository root:

```powershell
python -m unittest backend.tests.test_diagnosis
python -m backend.tests.accuracy
```

The included 15 labeled examples are a small illustrative sanity set, not a clinical or automotive benchmark. API request/response schemas are available at `/docs`.

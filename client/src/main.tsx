import React, { useState } from 'react';
import { createRoot } from 'react-dom/client';
import './style.css';

type Task = { id: string; state: string; attempts: number; result: { score: number; checks: Array<{ name: string; passed: boolean; reason: string }>; review: Array<{ check: string; suggestion: string; source: string }> } | null; error: string | null };
const base = '/api';

function App() {
  const [token, setToken] = useState('');
  const [task, setTask] = useState<Task | null>(null);
  const [variant, setVariant] = useState('golden');
  const [failure, setFailure] = useState('none');
  const [message, setMessage] = useState('');
  const [busy, setBusy] = useState(false);
  async function call(path: string, method = 'GET', body?: object, key?: string) {
    const response = await fetch(`${base}${path}`, { method, headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json', ...(key ? { 'Idempotency-Key': key } : {}) }, ...(body ? { body: JSON.stringify(body) } : {}) });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error?.message || response.statusText);
    return data as Task;
  }
  async function run() {
    setBusy(true); setMessage('');
    try {
      const created = await call('/tasks', 'POST', { scenario: 'webhook_once', input: { events: [{ id: 'evt-1', amount: 10 }, { id: 'evt-1', amount: 10 }, { id: 'evt-2', amount: -1 }] } }, crypto.randomUUID());
      setTask(await call(`/tasks/${created.id}/submit`, 'POST', { implementation: variant, inject_failure: failure }));
    } catch (error) { setMessage(error instanceof Error ? error.message : 'Request failed'); }
    finally { setBusy(false); }
  }
  async function refresh() { if (task) { try { setTask(await call(`/tasks/${task.id}`)); } catch (error) { setMessage(error instanceof Error ? error.message : 'Request failed'); } } }
  return <main><header><span className="eyebrow">OPEN SOURCE SYSTEMS DEMO</span><h1>OpenEval Systems Lab</h1><p>Run deterministic software evaluations and inspect retries, scores, and task states.</p></header><section className="panel"><label>API token<input type="password" value={token} onChange={e => setToken(e.target.value)} placeholder="Value from API_TOKEN" /></label><div className="row"><label>Implementation<select value={variant} onChange={e => setVariant(e.target.value)}><option value="golden">Golden</option><option value="defective_duplicate">Duplicate bug</option><option value="defective_validation">Validation bug</option></select></label><label>Failure injection<select value={failure} onChange={e => setFailure(e.target.value)}><option value="none">None</option><option value="transient">Transient timeout</option><option value="timeout">Persistent timeout</option><option value="invalid_output">Invalid output</option></select></label></div><div className="actions"><button disabled={busy || !token} onClick={run}>Create and evaluate</button><button className="secondary" disabled={!task} onClick={refresh}>Refresh status</button></div>{message && <p className="error">{message}</p>}</section>{task && <section className="panel"><div className="row"><div><span className="eyebrow">TASK</span><h2>{task.id}</h2></div><strong className="state">{task.state}</strong></div><p>Attempts: {task.attempts}</p>{task.error && <p className="error">{task.error}</p>}{task.result && <><h3>Score: {Math.round(task.result.score * 100)}%</h3><ul>{task.result.checks.map(check => <li key={check.name}><strong>{check.passed ? 'PASS' : 'FAIL'} · {check.name}</strong><span>{check.reason}</span></li>)}</ul>{task.result.review.length > 0 && <><h3>Review guidance</h3><ul>{task.result.review.map(item => <li key={item.check}><strong>{item.check}</strong><span>{item.suggestion}</span><small>Source: {item.source}</small></li>)}</ul></>}</>}</section>}<footer>Deterministic fixtures · Persisted task states · Replay safe worker</footer></main>;
}

createRoot(document.getElementById('root')!).render(<React.StrictMode><App /></React.StrictMode>);

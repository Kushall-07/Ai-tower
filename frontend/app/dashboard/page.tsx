"use client";

import { useEffect, useState } from "react";

type View = "agent" | "logs" | "actions";

interface AgentRunLog {
  id: number;
  created_at: string;
  prompt: string;
  response: string;
  model: string;
  trust_score: number;
  risk_level: string;
  policy_decision: string;
  policy_risk_level: string;
  // we ignore risk_flags_json, policy_reasons_json, llm_error for now
}

export default function DashboardPage() {
  const [activeView, setActiveView] = useState<View>("agent");

  // Agent runner state
  const [prompt, setPrompt] = useState("Say hello in one short sentence.");
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  // Logs state
  const [logs, setLogs] = useState<AgentRunLog[]>([]);
  const [logsLoading, setLogsLoading] = useState(false);
  const [logsError, setLogsError] = useState<string | null>(null);

  // Actions state
  const [actions, setActions] = useState<any[]>([]);
  const [newAction, setNewAction] = useState({
    agent_run_id: '',
    type: 'email_suggestion',
    payload: '{"to": "admin@example.com", "subject": "Test"}'
  });

  const runAgent = async () => {
    setLoading(true);
    setError(null);
    setResponse(null);

    try {
      const res = await fetch("http://localhost:8000/agent/run", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ prompt }),
      });

      if (!res.ok) {
        throw new Error(`Backend error: ${res.status}`);
      }

      const data = await res.json();
      setResponse(data);
    } catch (err: any) {
      console.error(err);
      setError(err.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  const loadLogs = async () => {
    setLogsLoading(true);
    setLogsError(null);

    try {
      const res = await fetch("http://127.0.0.1:8000/logs/recent");
      if (!res.ok) {
        throw new Error(`Backend error: ${res.status}`);
      }
      const data: AgentRunLog[] = await res.json();
      setLogs(data);
    } catch (err: any) {
      console.error(err);
      setLogsError(err.message || "Failed to load logs");
    } finally {
      setLogsLoading(false);
    }
  };

  // Automatically load logs when switching to Logs view for the first time
  useEffect(() => {
    if (activeView === "logs" && logs.length === 0 && !logsLoading) {
      void loadLogs();
    }
  }, [activeView]);

  // Actions handlers
  const fetchActions = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/actions/all");
      if (!res.ok) {
        console.error("Failed to fetch actions, status:", res.status);
        setActions([]);
        return;
      }

      const data = await res.json();
      console.log("Actions API response:", data);

      // Ensure `actions` is always an array
      setActions(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error("Failed to fetch actions:", error);
      setActions([]);
    }
  };

  const handleSimulateAction = async () => {
    try {
      const payload = JSON.parse(newAction.payload);
      const res = await fetch('http://127.0.0.1:8000/actions/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          agent_run_id: parseInt(newAction.agent_run_id),
          type: newAction.type,
          payload: payload
        })
      });
      
      if (res.ok) {
        alert('Action simulated successfully!');
        fetchActions();
        setNewAction({ ...newAction, payload: '{}' });
      } else {
        alert('Failed to simulate action');
      }
    } catch (error) {
      alert('Error: ' + error);
    }
  };

  const handleExecuteAction = async (actionId: number) => {
    try {
      const res = await fetch(`http://127.0.0.1:8000/actions/${actionId}/execute`, {
        method: 'POST'
      });
      
      if (res.ok) {
        alert('Action executed!');
        fetchActions();
      } else {
        alert('Failed to execute action');
      }
    } catch (error) {
      alert('Error: ' + error);
    }
  };

  const handleCancelAction = async (actionId: number) => {
    try {
      const res = await fetch(`http://127.0.0.1:8000/actions/${actionId}/cancel`, {
        method: 'POST'
      });
      
      if (res.ok) {
        alert('Action cancelled!');
        fetchActions();
      } else {
        alert('Failed to cancel action');
      }
    } catch (error) {
      alert('Error: ' + error);
    }
  };

  // Automatically load actions when switching to Actions view for the first time
  useEffect(() => {
    if (activeView === "actions") {
      void fetchActions();
    }
  }, [activeView]);

  const renderAgentView = () => (
    <>
      <h1 className="text-2xl font-bold mb-4">Agent Runner</h1>
      <p className="text-slate-300 mb-4">
        This calls your FastAPI backend at <code>/agent/run</code>.
      </p>

      <div className="mb-4">
        <label className="block text-sm mb-1">Prompt</label>
        <textarea
          className="w-full p-2 rounded-md bg-slate-800 border border-slate-700 text-sm"
          rows={3}
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
        />
      </div>

      <button
        onClick={runAgent}
        disabled={loading}
        className="px-4 py-2 rounded-md bg-emerald-500 hover:bg-emerald-600 font-semibold disabled:opacity-50"
      >
        {loading ? "Running..." : "Test Agent Runner"}
      </button>

      {error && (
        <div className="mt-4 text-sm text-red-400">Error: {error}</div>
      )}

      {response && (
        <div className="mt-6 bg-slate-800 p-4 rounded-lg text-sm space-y-2">
          <div>
            <span className="font-semibold">Status:</span> {response.status}
          </div>
          <div>
            <span className="font-semibold">Message:</span> {response.message}
          </div>
          <div>
            <span className="font-semibold">Model:</span> {response.model}</div>
          <div>
            <span className="font-semibold">Prompt sent:</span>{" "}
            {response.prompt_sent}
          </div>
          <div>
            <span className="font-semibold">Trust score:</span>{" "}
            {response.trust_score}
          </div>
          <div>
            <span className="font-semibold">Risk level:</span>{" "}
            {response.risk_level}
          </div>
          <div>
            <span className="font-semibold">Risk flags:</span>{" "}
            {response.risk_flags && response.risk_flags.length > 0
              ? response.risk_flags.join(", ")
              : "None"}
          </div>

          <hr className="border-slate-700 my-2" />

          <div>
            <span className="font-semibold">Policy decision:</span>{" "}
            {response.policy_decision}
          </div>
          <div>
            <span className="font-semibold">Policy reasons:</span>
            <ul className="list-disc list-inside mt-1">
              {response.policy_reasons &&
                response.policy_reasons.map((r: string, idx: number) => (
                  <li key={idx}>{r}</li>
                ))}
            </ul>
          </div>

          <div>
            <span className="font-semibold">Response:</span>
            <pre className="mt-1 whitespace-pre-wrap">
              {response.response}
            </pre>
          </div>
          <div>
            <span className="font-semibold">Explainability:</span>
            <p className="mt-1 whitespace-pre-wrap">
              {response.explainability}
            </p>
          </div>
        </div>
      )}
    </>
  );

  const renderLogsView = () => (
    <>
      <div className="flex items-center justify-between mb-4">
        <div>
          <h1 className="text-2xl font-bold">Agent Run Logs</h1>
          <p className="text-slate-300 text-sm">
            Showing recent runs from <code>/logs/recent</code>.
          </p>
        </div>
        <button
          onClick={loadLogs}
          disabled={logsLoading}
          className="px-3 py-1.5 rounded-md bg-slate-700 hover:bg-slate-600 text-sm font-semibold disabled:opacity-50"
        >
          {logsLoading ? "Refreshing..." : "Refresh"}
        </button>
      </div>

      {logsError && (
        <div className="text-red-400 text-sm mb-3">
          Error loading logs: {logsError}
        </div>
      )}

      {logs.length === 0 && !logsLoading ? (
        <div className="text-slate-400 text-sm">
          No logs yet. Run an agent from the <b>Agents</b> tab.
        </div>
      ) : (
        <div className="overflow-x-auto border border-slate-800 rounded-lg">
          <table className="min-w-full text-sm">
            <thead className="bg-slate-900">
              <tr>
                <th className="px-3 py-2 text-left font-semibold text-slate-300">
                  Time
                </th>
                <th className="px-3 py-2 text-left font-semibold text-slate-300">
                  Prompt
                </th>
                <th className="px-3 py-2 text-left font-semibold text-slate-300">
                  Trust
                </th>
                <th className="px-3 py-2 text-left font-semibold text-slate-300">
                  Risk
                </th>
                <th className="px-3 py-2 text-left font-semibold text-slate-300">
                  Policy
                </th>
              </tr>
            </thead>
            <tbody>
              {logs.map((log) => (
                <tr key={log.id} className="border-t border-slate-800">
                  <td className="px-3 py-2 text-slate-300">
                    {new Date(log.created_at).toLocaleString()}
                  </td>
                  <td className="px-3 py-2 text-slate-300 max-w-xs truncate">
                    {log.prompt}
                  </td>
                  <td className="px-3 py-2 text-slate-300">
                    {log.trust_score}
                  </td>
                  <td className="px-3 py-2 text-slate-300">
                    {log.risk_level}
                  </td>
                  <td className="px-3 py-2 text-slate-300">
                    {log.policy_decision}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  );

  const renderActionsView = () => (
    <>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold">Actions</h2>
        <button
          onClick={fetchActions}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Refresh
        </button>
      </div>

      {/* Simulate Action Form */}
      <div className="bg-slate-800 rounded-lg shadow p-6 mb-6">
        <h3 className="text-lg font-semibold mb-4">Simulate New Action</h3>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Agent Run ID</label>
            <input
              type="number"
              value={newAction.agent_run_id}
              onChange={(e) => setNewAction({ ...newAction, agent_run_id: e.target.value })}
              className="w-full px-3 py-2 border rounded bg-slate-700 border-slate-600 text-white"
              placeholder="Enter Agent Run ID"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Action Type</label>
            <select
              value={newAction.type}
              onChange={(e) => setNewAction({ ...newAction, type: e.target.value })}
              className="w-full px-3 py-2 border rounded bg-slate-700 border-slate-600 text-white"
            >
              <option value="email_suggestion">Email Suggestion</option>
              <option value="database_query">Database Query</option>
              <option value="api_call_external">External API Call</option>
              <option value="file_operation">File Operation</option>
              <option value="notification">Send Notification</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Payload (JSON)</label>
            <textarea
              value={newAction.payload}
              onChange={(e) => setNewAction({ ...newAction, payload: e.target.value })}
              className="w-full px-3 py-2 border rounded font-mono text-sm bg-slate-700 border-slate-600 text-white"
              rows={4}
              placeholder='{"to": "admin@example.com", "subject": "Alert"}'
            />
          </div>
          <button
            onClick={handleSimulateAction}
            className="w-full px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
          >
            Simulate Action
          </button>
        </div>
      </div>

      {/* Actions Table */}
      <div className="bg-slate-800 rounded-lg shadow overflow-hidden">
        <table className="min-w-full">
          <thead className="bg-slate-900">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase">Time</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase">Run ID</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase">Type</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase">Payload</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase">Status</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-700">
            {Array.isArray(actions) && actions.length > 0 ? (
              actions.map((action: any) => (
                <tr key={action.id}>
                  <td className="px-6 py-4 text-sm text-slate-300">
                    {new Date(action.created_at).toLocaleString()}
                  </td>
                  <td className="px-6 py-4 text-sm text-slate-300">
                    {action.agent_run_id}
                  </td>
                  <td className="px-6 py-4 text-sm font-medium text-slate-100">
                    {action.type}
                  </td>
                  <td className="px-6 py-4 text-sm text-slate-300">
                    <code className="text-xs bg-slate-800 px-2 py-1 rounded">
                      {JSON.stringify(action.payload).substring(0, 50)}...
                    </code>
                  </td>
                  <td className="px-6 py-4 text-sm">
                    <span
                      className={`px-2 py-1 rounded text-xs font-medium ${
                        action.status === "executed"
                          ? "bg-green-100 text-green-800"
                          : action.status === "simulated"
                          ? "bg-blue-100 text-blue-800"
                          : action.status === "pending"
                          ? "bg-yellow-100 text-yellow-800"
                          : "bg-gray-100 text-gray-800"
                      }`}
                    >
                      {action.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm space-x-2">
                    {action.status === "simulated" && (
                      <button
                        onClick={() => handleExecuteAction(action.id)}
                        className="px-3 py-1 bg-green-600 text-white rounded text-xs hover:bg-green-700"
                      >
                        Execute
                      </button>
                    )}
                    {(action.status === "pending" || action.status === "simulated") && (
                      <button
                        onClick={() => handleCancelAction(action.id)}
                        className="px-3 py-1 bg-red-600 text-white rounded text-xs hover:bg-red-700"
                      >
                        Cancel
                      </button>
                    )}
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td
                  className="px-6 py-4 text-sm text-slate-400"
                  colSpan={6}
                >
                  No actions found. Simulate one above or run agents that
                  suggest actions.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </>
  );

  return (
    <main className="min-h-screen flex bg-slate-900 text-white">
      {/* Sidebar */}
      <aside className="w-64 bg-slate-950 border-r border-slate-800 p-4">
        <h2 className="text-xl font-bold mb-6">Control Tower</h2>
        <nav className="space-y-2 text-sm">
          <button
            onClick={() => setActiveView("agent")}
            className={`block w-full text-left px-3 py-2 rounded-md ${
              activeView === "agent"
                ? "bg-emerald-500 text-black font-semibold"
                : "text-slate-300 hover:bg-slate-800"
            }`}
          >
            Agents
          </button>
          <button
            onClick={() => setActiveView("logs")}
            className={`block w-full text-left px-3 py-2 rounded-md ${
              activeView === "logs"
                ? "bg-emerald-500 text-black font-semibold"
                : "text-slate-300 hover:bg-slate-800"
            }`}
          >
            Logs
          </button>
          <button
            onClick={() => setActiveView("actions")}
            className={`block w-full text-left px-3 py-2 rounded-md ${
              activeView === "actions"
                ? "bg-emerald-500 text-black font-semibold"
                : "text-slate-300 hover:bg-slate-800"
            }`}
          >
            Actions
          </button>
        </nav>
      </aside>

      {/* Main content */}
      <section className="flex-1 p-8">
        {activeView === "agent" && renderAgentView()}
        {activeView === "logs" && renderLogsView()}
        {activeView === "actions" && renderActionsView()}
      </section>
    </main>
  );
}

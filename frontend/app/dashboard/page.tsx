"use client";

import { useState } from "react";

export default function DashboardPage() {
  const [prompt, setPrompt] = useState("Say hello in one short sentence.");
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const runAgent = async () => {
    setLoading(true);
    setError(null);
    setResponse(null);

    try {
      const res = await fetch("http://127.0.0.1:8000/agent/run", {
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

  return (
    <main className="min-h-screen flex bg-slate-900 text-white">
      {/* Sidebar */}
      <aside className="w-64 bg-slate-950 border-r border-slate-800 p-4">
        <h2 className="text-xl font-bold mb-6">Control Tower</h2>
        <nav className="space-y-2 text-sm">
          <div className="font-semibold text-emerald-400">Agents</div>
          <div className="text-slate-400">Policies</div>
          <div className="text-slate-400">Logs</div>
        </nav>
      </aside>

      {/* Main content */}
      <section className="flex-1 p-8">
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
          <div className="mt-4 text-sm text-red-400">
            Error: {error}
          </div>
        )}

        {response && (
          <div className="mt-6 bg-slate-800 p-4 rounded-lg text-sm space-y-2">
            <div>
              <span className="font-semibold">Status:</span> {response.status}
            </div>
            <div>
              <span className="font-semibold">Message:</span>{" "}
              {response.message}
            </div>
            <div>
              <span className="font-semibold">Prompt sent:</span>{" "}
              {response.prompt_sent}
            </div>
            <div>
              <span className="font-semibold">Trust score:</span>{" "}
              {response.trust_score}
            </div>
            <div>
              <span className="font-semibold">Response:</span>
              <pre className="mt-1 whitespace-pre-wrap">
                {response.response}
              </pre>
            </div>
          </div>
        )}
      </section>
    </main>
  );
}

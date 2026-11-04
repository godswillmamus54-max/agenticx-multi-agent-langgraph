
"use client";

import { FormEvent, useState } from "react";

type Review = {
  iteration: number;
  status: string;
  feedback: string;
};

type WorkflowResult = {
  status: string;
  task: string;
  plan: string[];
  final_output: string;
  review_status: string;
  rejection_count: number;
  iterations: number;
  review_history: Review[];
};

const API_URL = "";

export default function Home() {
  const [task, setTask] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<WorkflowResult | null>(null);
  const [error, setError] = useState("");
  const [activeTab, setActiveTab] = useState<"report" | "plan" | "review">(
    "report"
  );

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!task.trim() || loading) return;

    setLoading(true);
    setError("");
    setResult(null);
    setActiveTab("report");

    try {
      const response = await fetch("/api/run", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ task: task.trim() }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          typeof data.detail === "string"
            ? data.detail
            : "The research request could not be completed."
        );
      }

      setResult(data as WorkflowResult);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to connect to the AgenticX backend."
      );
    } finally {
      setLoading(false);
    }
  }

  function downloadReport() {
    if (!result?.final_output) return;

    const blob = new Blob([result.final_output], {
      type: "text/markdown;charset=utf-8",
    });

    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");

    link.href = url;
    link.download = "agenticx-research-report.md";
    link.click();

    URL.revokeObjectURL(url);
  }

  return (
    <main className="dashboard">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">A</div>
          <div>
            <h1>AgenticX</h1>
            <span>INTELLIGENCE WORKSPACE</span>
          </div>
        </div>

        <div className="nav-label">WORKSPACE</div>

        <div className="nav-item active">
          <span>◈</span> Research Studio
        </div>

        <div className="nav-item">
          <span>◷</span> Execution History
          <span className="coming">Soon</span>
        </div>

        <div className="nav-item">
          <span>◇</span> Agent Configuration
          <span className="coming">Soon</span>
        </div>

        <div className="sidebar-bottom">
          <div className="connection-card">
            <div className="connection-heading">
              <span className="status-dot" />
              System Status
            </div>
            <p>Local development environment</p>
            <span className="connection-address">
              API · 127.0.0.1:8000
            </span>
          </div>

          <div className="profile">
            <div className="avatar">A</div>
            <div>
              <strong>AgenticX Workspace</strong>
              <span>Research Environment</span>
            </div>
          </div>
        </div>
      </aside>

      <section className="main-area">
        <header className="topbar">
          <div>
            <span className="breadcrumb">Workspace /</span>
            <strong> Research Studio</strong>
          </div>

          <div className="topbar-right">
            <span className="environment">
              <span className="status-dot" /> LOCAL ENVIRONMENT
            </span>
            <div className="top-avatar">A</div>
          </div>
        </header>

        <div className="content">
          <section className="welcome">
            <span className="eyebrow">MULTI-AGENT RESEARCH PLATFORM</span>

            <h2>
              Think deeper.
              <br />
              <span>Research smarter.</span>
            </h2>

            <p>
              Give your research task to AgenticX. Your Planner, Worker
              and Reviewer will collaborate to produce a reviewed result.
            </p>
          </section>

          <section className="task-panel">
            <div className="panel-heading">
              <div>
                <span className="section-label">NEW RESEARCH TASK</span>
                <h3>What should your agents investigate?</h3>
              </div>
              <span className="task-icon">✳</span>
            </div>

            <form onSubmit={handleSubmit}>
              <textarea
                value={task}
                onChange={(event) => setTask(event.target.value)}
                placeholder="Describe your research objective, question or problem..."
                maxLength={10000}
                disabled={loading}
                required
              />

              <div className="form-footer">
                <span>{task.length.toLocaleString()} / 10,000 characters</span>

                <button
                  type="submit"
                  disabled={!task.trim() || loading}
                  className="run-button"
                >
                  {loading ? (
                    <>
                      <span className="spinner" /> Agents working...
                    </>
                  ) : (
                    <>Run research <span>→</span></>
                  )}
                </button>
              </div>
            </form>

            {error && (
              <div className="error-message">
                <strong>Execution error</strong>
                <p>{error}</p>
              </div>
            )}
          </section>

          <section className="agents-section">
            <div className="section-top">
              <div>
                <span className="section-label">YOUR AI TEAM</span>
                <h3>Multi-agent workflow</h3>
              </div>
              <span className="workflow-label">LANGGRAPH ENGINE</span>
            </div>

            <div className="agents-grid">
              <AgentCard
                number="01"
                icon="◇"
                name="Planner"
                description="Breaks your task into actionable steps."
                color="blue"
                status={loading ? "Working" : result ? "Completed" : "Ready"}
              />

              <AgentCard
                number="02"
                icon="✳"
                name="Worker"
                description="Executes the plan and produces the report."
                color="green"
                status={loading ? "Working" : result ? "Completed" : "Ready"}
              />

              <AgentCard
                number="03"
                icon="✓"
                name="Reviewer"
                description="Evaluates the draft and decides its outcome."
                color="purple"
                status={loading ? "Working" : result ? "Completed" : "Ready"}
              />
            </div>

            <p className="workflow-note">
              Planner <span>→</span> Worker <span>→</span> Reviewer
              <span>→</span> Approved or Escalated
            </p>
          </section>

          {result && (
            <section className="results-section">
              <div className="results-heading">
                <div>
                  <span className="section-label">EXECUTION RESULTS</span>
                  <h3>Research completed</h3>
                </div>

                <span className="approved-badge">
                  ✓ {result.review_status}
                </span>
              </div>

              <div className="metrics-grid">
                <Metric label="Iterations" value={result.iterations} />
                <Metric label="Plan steps" value={result.plan.length} />
                <Metric label="Rejections" value={result.rejection_count} />
              </div>

              <div className="results-panel">
                <div className="result-tabs">
                  <button
                    className={activeTab === "report" ? "selected" : ""}
                    onClick={() => setActiveTab("report")}
                  >
                    Final Report
                  </button>

                  <button
                    className={activeTab === "plan" ? "selected" : ""}
                    onClick={() => setActiveTab("plan")}
                  >
                    Execution Plan
                  </button>

                  <button
                    className={activeTab === "review" ? "selected" : ""}
                    onClick={() => setActiveTab("review")}
                  >
                    Review History
                  </button>

                  <button
                    className="download-button"
                    onClick={downloadReport}
                  >
                    ↓ Export MD
                  </button>
                </div>

                <div className="result-content">
                  {activeTab === "report" && (
                    <pre className="report-text">{result.final_output}</pre>
                  )}

                  {activeTab === "plan" && (
                    <ol className="plan-list">
                      {result.plan.map((step, index) => (
                        <li key={index}>{step}</li>
                      ))}
                    </ol>
                  )}

                  {activeTab === "review" && (
                    <div className="review-list">
                      {result.review_history.map((review, index) => (
                        <div className="review-item" key={index}>
                          <strong>
                            Iteration {review.iteration}: {review.status}
                          </strong>
                          <p>{review.feedback || "No additional feedback."}</p>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </section>
          )}

          {!result && !loading && !error && (
            <div className="empty-state">
              <div className="empty-icon">⌘</div>
              <strong>Your research workspace is ready</strong>
              <p>Submit a task above to start your first agent execution.</p>
            </div>
          )}

          {loading && (
            <div className="loading-panel">
              <span className="spinner large" />
              <strong>Your agents are collaborating</strong>
              <p>
                The Planner, Worker and Reviewer are processing your request.
                This can take a little while.
              </p>
            </div>
          )}

          <footer>
            <span>AGENTICX © 2026</span>
            <span>POWERED BY LANGGRAPH & FASTAPI</span>
          </footer>
        </div>
      </section>
    </main>
  );
}

function AgentCard({
  number,
  icon,
  name,
  description,
  color,
  status,
}: {
  number: string;
  icon: string;
  name: string;
  description: string;
  color: string;
  status: string;
}) {
  return (
    <div className="agent-card">
      <div className={`agent-icon ${color}`}>{icon}</div>
      <div className="agent-number">{number}</div>
      <h4>{name}</h4>
      <p>{description}</p>
      <div className="agent-status">
        <span className="status-dot" />
        {status}
      </div>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: number }) {
  return (
    <div className="metric-card">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

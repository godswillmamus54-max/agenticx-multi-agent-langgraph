
"use client";

import { useEffect, useState, type FormEvent, type ReactNode } from "react";

export default function AuthGate({ children }: { children: ReactNode }) {
  const [authenticated, setAuthenticated] = useState(false);
  const [checking, setChecking] = useState(true);
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;

    fetch("/api/auth/session", { cache: "no-store" })
      .then((response) => response.json())
      .then((data) => {
        if (active) setAuthenticated(data.authenticated === true);
      })
      .catch(() => {
        if (active) setError("Unable to verify your session. Refresh the page.");
      })
      .finally(() => {
        if (active) setChecking(false);
      });

    return () => {
      active = false;
    };
  }, []);

  async function handleLogin(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError("");

    try {
      const response = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ password }),
      });

      const data = await response.json();

      if (!response.ok) {
        setError(data.error || "Login failed.");
        return;
      }

      setPassword("");
      setAuthenticated(true);
    } catch {
      setError("Unable to connect. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  async function handleLogout() {
    try {
      await fetch("/api/auth/logout", { method: "POST" });
    } finally {
      setAuthenticated(false);
      setPassword("");
    }
  }

  if (checking) {
    return (
      <main className="auth-screen">
        <p className="auth-muted">Checking your access...</p>
      </main>
    );
  }

  if (!authenticated) {
    return (
      <main className="auth-screen">
        <form className="auth-card" onSubmit={handleLogin}>
          <div className="auth-brand">AGENTICX</div>
          <p className="auth-eyebrow">PRIVATE RESEARCH WORKSPACE</p>
          <h1>Welcome back</h1>
          <p className="auth-description">
            Enter the shared access password to continue.
          </p>

          <label className="auth-label" htmlFor="access-password">
            Access password
          </label>

          <input
            id="access-password"
            className="auth-input"
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            placeholder="Enter access password"
            autoComplete="current-password"
            required
            maxLength={256}
          />

          {error && <p className="auth-error">{error}</p>}

          <button
            className="auth-button"
            type="submit"
            disabled={loading || !password}
          >
            {loading ? "Verifying..." : "Access workspace"}
          </button>

          <p className="auth-footer">
            Authorized access only.
          </p>
        </form>
      </main>
    );
  }

  return (
    <>
      <div className="auth-session-bar">
        <span>Secure session active</span>
        <button type="button" onClick={handleLogout}>
          Sign out
        </button>
      </div>
      {children}
    </>
  );
}

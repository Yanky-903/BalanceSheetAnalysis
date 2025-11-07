// frontend/src/components/Login.jsx
import React, { useState } from "react";
import { login } from "../api";
import "./Login.css"; // make sure this file exists (below)

export default function Login({ onLogin }) {
  const [email, setEmail] = useState("analyst@example.com");
  const [password, setPassword] = useState("analystpass");
  const [err, setErr] = useState(null);
  const [loading, setLoading] = useState(false);

  async function doLogin() {
    setErr(null);
    setLoading(true);
    try {
      // api.login may return axios response or plain object depending on your api implementation.
      // We handle both forms gracefully.
      const r = await login(email, password);
      // try common shapes: r.data.access_token or r.access_token or r?.data?.access_token
      const token =
        (r && r.data && r.data.access_token) ||
        (r && r.access_token) ||
        (r && r.data && r.data.token) ||
        null;

      if (!token) {
        // maybe the login helper returned the parsed object itself
        const fallbackToken = r?.access_token || r?.data?.access_token || null;
        if (!fallbackToken) {
          throw new Error("Login failed: no token returned");
        }
      }

      // call onLogin with token string (caller should set auth state / store token)
      onLogin(token || r.access_token || r.data.access_token);

    } catch (e) {
      // derive a friendly error message
      const msg =
        e?.response?.data?.detail ||
        e?.response?.data?.message ||
        e?.message ||
        "Login failed";
      setErr(msg);
    } finally {
      setLoading(false);
    }
  }

  function onKey(e) {
    if (e.key === "Enter") doLogin();
  }

  return (
    <div className="login-root">
      <div className="login-card">
        <div className="login-title">Balance Sheet Assistant</div>

        <p className="login-sub">Sign in to continue — Analyst / CEO accounts available</p>

        {err && <div className="login-error" role="alert">{err}</div>}

        <label className="login-label">Email</label>
        <input
          className="login-input"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="you@company.com"
          onKeyDown={onKey}
        />

        <label className="login-label">Password</label>
        <input
          className="login-input"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="••••••••"
          onKeyDown={onKey}
        />

        <button
          className="login-btn"
          onClick={doLogin}
          disabled={loading}
        >
          {loading ? "Signing in…" : "Login"}
        </button>

        <div className="login-footer">
          <small>Use <strong>analyst@example.com</strong> / <em>analystpass</em> for demo</small>
        </div>
      </div>
    </div>
  );
}

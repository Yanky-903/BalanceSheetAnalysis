// frontend/src/App.jsx
import React, { useState, useEffect } from "react";
import Login from "./components/Login";
import UploadPanel from "./components/UploadPanel";
import Dashboard from "./components/Dashboard";
import { listCompanies, setAuthTokenFromStorage } from "./api";

/**
 * Top-level App
 * - stores token in localStorage under "token"
 * - uses api.setAuthTokenFromStorage() to make axios include Authorization header
 * - loads companies automatically after login
 */

function App() {
  // prefer global 'token' key used by api.js
  const [token, setToken] = useState(localStorage.getItem("token") || null);
  const [result, setResult] = useState(null);
  const [companies, setCompanies] = useState([]);
  const [selectedCompany, setSelectedCompany] = useState(null);
  const [loadingCompanies, setLoadingCompanies] = useState(false);

  // whenever token changes, persist it and tell api to use it
  useEffect(() => {
    if (token) {
      localStorage.setItem("token", token);
      setAuthTokenFromStorage();
      loadCompanies();
    } else {
      localStorage.removeItem("token");
      setAuthTokenFromStorage();
      setCompanies([]);
      setSelectedCompany(null);
    }
  }, [token]);

  // load user's companies
  async function loadCompanies() {
    setLoadingCompanies(true);
    try {
      const res = await listCompanies();
      // axios response -> res.data
      const data = res?.data ?? res;
      setCompanies(Array.isArray(data) ? data : []);
      if (Array.isArray(data) && data.length > 0) {
        // keep selection: if current selectedCompany exists in new list, keep it; otherwise pick first
        const existing = data.find((c) => selectedCompany && c.id === selectedCompany.id);
        setSelectedCompany(existing || data[0]);
      } else {
        setSelectedCompany(null);
      }
    } catch (e) {
      console.error("Failed to load companies:", e);
    } finally {
      setLoadingCompanies(false);
    }
  }

  // called by Login component with token string
  function onLogin(tkn) {
    setToken(tkn);
  }

  // called after upload finishes
  function onUploaded(data) {
    setResult(data?.data ?? data);
    // refresh companies (maybe new company got added)
    loadCompanies();
  }

  // logout helper
  function onLogout() {
    setToken(null);
    setResult(null);
  }

  // If not logged in, show the Login screen
  if (!token) {
    return <Login onLogin={onLogin} />;
  }

  // Logged-in layout: header + two-column area
  return (
    <div style={{ padding: 20, fontFamily: "Inter, system-ui, -apple-system, Roboto, Arial" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div style={{ fontWeight: 700, fontSize: 18 }}>Balance Sheet Assistant</div>
        <div>
          <button
            onClick={onLogout}
            style={{
              background: "#fff",
              border: "1px solid #e5e7eb",
              padding: "6px 10px",
              borderRadius: 8,
              cursor: "pointer",
            }}
          >
            Logout
          </button>
        </div>
      </div>

      <div style={{ display: "flex", gap: 20, marginTop: 20, alignItems: "flex-start" }}>
        {/* Left column: upload + company picker */}
        <div style={{ width: 420 }}>
          <div
            style={{
              background: "#fff",
              padding: 16,
              borderRadius: 10,
              boxShadow: "0 6px 20px rgba(16,24,40,0.06)",
            }}
          >
            <h3 style={{ margin: "0 0 8px 0" }}>Upload / Process PDF</h3>

            <label style={{ fontSize: 13, color: "#6b7280" }}>Select company</label>
            <div style={{ marginTop: 8, marginBottom: 10 }}>
              <select
                value={selectedCompany ? selectedCompany.id : ""}
                onChange={(e) => {
                  const id = Number(e.target.value);
                  const found = companies.find((c) => c.id === id);
                  setSelectedCompany(found || null);
                }}
                style={{
                  width: "100%",
                  padding: "8px 10px",
                  borderRadius: 8,
                  border: "1px solid #e6eef8",
                  background: "#fbfdff",
                }}
              >
                <option value="">{loadingCompanies ? "Loading..." : "Select a company"}</option>
                {companies.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name} {c.group ? `(${c.group})` : ""}
                  </option>
                ))}
              </select>
            </div>

            <UploadPanel
              company={selectedCompany}
              onStart={() => {
                setResult(null);
              }}
              onSuccess={onUploaded}
              onError={(err) => {
                setResult({ error: true, message: err?.message || err?.detail || "Upload failed" });
              }}
            />
          </div>
        </div>

        {/* Right column: dashboard / result */}
        <div style={{ flex: 1 }}>
          <div
            style={{
              background: "#fff",
              padding: 16,
              borderRadius: 10,
              boxShadow: "0 6px 20px rgba(16,24,40,0.06)",
              minHeight: 300,
            }}
          >
            <h3 style={{ marginTop: 0 }}>Analysis</h3>

            {!result && <div style={{ color: "#6b7280" }}>No data — upload a balance sheet PDF to begin</div>}

            {result && result.error && (
              <div style={{ color: "#991b1b", background: "#fff1f2", padding: 10, borderRadius: 8 }}>
                Error: {result.message || JSON.stringify(result)}
              </div>
            )}

            {result && !result.error && (
              <div>
                {/* If API returns a structured payload (company, numeric_context, analysis) show them nicely */}
                {result.company && (
                  <div style={{ marginBottom: 12 }}>
                    <strong>{result.company}</strong>
                    <div style={{ color: "#6b7280", fontSize: 13 }}>{result.period}</div>
                  </div>
                )}

                {result.numeric_context && (
                  <div style={{ display: "flex", gap: 12, flexWrap: "wrap", marginBottom: 12 }}>
                    {Object.entries(result.numeric_context).slice(0, 8).map(([k, v]) => (
                      <div
                        key={k}
                        style={{
                          minWidth: 140,
                          padding: 10,
                          borderRadius: 8,
                          background: "#f8fafc",
                          border: "1px solid #eef2f7",
                        }}
                      >
                        <div style={{ fontSize: 12, color: "#6b7280" }}>{k}</div>
                        <div style={{ fontWeight: 700, marginTop: 6 }}>{v}</div>
                      </div>
                    ))}
                  </div>
                )}

                {result.kpis && (
                  <div style={{ marginBottom: 12 }}>
                    <h4 style={{ margin: "8px 0" }}>KPIs</h4>
                    <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
                      {Object.entries(result.kpis).map(([k, v]) => (
                        <div
                          key={k}
                          style={{
                            minWidth: 160,
                            padding: 10,
                            borderRadius: 8,
                            background: "#ffffff",
                            border: "1px solid #eef2f7",
                          }}
                        >
                          <div style={{ fontSize: 12, color: "#6b7280" }}>{k}</div>
                          <div style={{ fontWeight: 700, marginTop: 6 }}>{String(v)}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {result.analysis && (
                  <div>
                    <h4 style={{ margin: "8px 0" }}>LLM Analysis</h4>
                    {typeof result.analysis === "object" ? (
                      <>
                        {result.analysis.tldr && <p><strong>Summary:</strong> {result.analysis.tldr}</p>}
                        {result.analysis.highlights && (
                          <div>
                            <strong>Highlights:</strong>
                            <ul>
                              {result.analysis.highlights.map((h, i) => <li key={i}>{h}</li>)}
                            </ul>
                          </div>
                        )}
                        {result.analysis.actions && (
                          <div>
                            <strong>Actions:</strong>
                            <ul>
                              {result.analysis.actions.map((a, i) => <li key={i}>{a}</li>)}
                            </ul>
                          </div>
                        )}
                      </>
                    ) : (
                      <pre style={{ whiteSpace: "pre-wrap" }}>{String(result.analysis)}</pre>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>

          {/* quick companies list duplicate (keeps previous UI visible) */}
          <div style={{ marginTop: 16 }}>
            <h4 style={{ marginBottom: 8 }}>Your companies</h4>
            <ul>
              {companies.map((c) => (
                <li key={c.id}>
                  {c.name} {c.group ? `(${c.group})` : ""}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;

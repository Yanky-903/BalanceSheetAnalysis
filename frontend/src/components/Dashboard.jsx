// frontend/src/components/Dashboard.jsx
import React, { useEffect, useState } from "react";
import UploadPanel from "./UploadPanel";
import CompanyList from "./CompanyList";
import "./Dashboard.css";
import { listCompanies } from "../api";

export default function Dashboard({ onLogout }) {
  const [companies, setCompanies] = useState([]);
  const [selectedCompany, setSelectedCompany] = useState(null);
  const [message, setMessage] = useState(null);

  useEffect(() => {
    async function load() {
      try {
        const res = await fetchCompanies();
        setCompanies(res.data || res);
        if ((res.data || res)?.length) {
          setSelectedCompany((res.data || res)[0]);
        }
      } catch (err) {
        setMessage({ type: "error", text: err.response?.data?.detail || err.message });
      }
    }
    load();
  }, []);

  return (
    <div className="dash-root">
      <header className="dash-header">
        <div className="dash-brand">Balance Sheet Assistant</div>
        <div className="dash-actions">
          <button className="btn small" onClick={onLogout}>Logout</button>
        </div>
      </header>

      <div className="dash-body">
        <aside className="dash-aside">
          <h4>Your companies</h4>
          <CompanyList
            companies={companies}
            selected={selectedCompany}
            onSelect={(c) => setSelectedCompany(c)}
          />
        </aside>

        <main className="dash-main">
          {message && <div className={`alert ${message.type}`}>{message.text}</div>}

          <div className="panel-row">
            <div className="panel-left">
              <UploadPanel
                company={selectedCompany}
                onStart={() => setMessage({ type: "info", text: "Processing PDF..." })}
                onSuccess={(res) => {
                  setMessage({ type: "success", text: "Analysis ready" });
                }}
                onError={(err) => {
                  setMessage({ type: "error", text: err?.message || "Upload failed" });
                }}
              />
            </div>

            <div className="panel-right">
              <div className="no-data">No data</div>
              {/* After implement: replace with real visualization (charts and tables) */}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}

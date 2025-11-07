// frontend/src/components/UploadPanel.jsx
import React, { useState } from "react";
import api from "../api";

export default function UploadPanel({ company, onStart, onSuccess, onError }) {
  const [pdfUrl, setPdfUrl] = useState("");
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!company) {
      onError({ message: "Please select a company" });
      return;
    }
    onStart && onStart();
    setLoading(true);

    try {
      const form = new FormData();
      form.append("company_name", company.name);
      if (pdfUrl) form.append("pdf_url", pdfUrl);
      if (file) form.append("file", file);

      const resp = await api.post("/upload_pdf", form, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      onSuccess && onSuccess(resp.data || resp);
    } catch (err) {
      onError && onError(err.response?.data || { message: err.message });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="upload-card">
      <h3>Upload / Process PDF</h3>
      <form onSubmit={handleSubmit}>
        <label>Company</label>
        <div className="readonly">{company ? company.name : "Select a company"}</div>

        <label>PDF URL (optional)</label>
        <input value={pdfUrl} onChange={(e) => setPdfUrl(e.target.value)} placeholder="https://..." />

        <div className="divider">— or —</div>

        <label>Upload PDF</label>
        <input type="file" accept="application/pdf" onChange={(e) => setFile(e.target.files[0])} />

        <div className="actions">
          <button type="submit" className="btn" disabled={loading}>
            {loading ? "Processing…" : "Process"}
          </button>
        </div>
      </form>
    </div>
  );
}

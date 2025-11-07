// frontend/src/components/CompanyList.jsx
import React from "react";

export default function CompanyList({ companies = [], selected, onSelect }) {
  if (!companies || companies.length === 0) {
    return <div className="empty">No companies assigned</div>;
  }
  return (
    <ul className="company-list">
      {companies.map((c) => (
        <li
          key={c.id}
          className={selected && selected.id === c.id ? "company-item selected" : "company-item"}
          onClick={() => onSelect(c)}
        >
          <div className="company-name">{c.name}</div>
          <div className="company-meta">{c.group}</div>
        </li>
      ))}
    </ul>
  );
}

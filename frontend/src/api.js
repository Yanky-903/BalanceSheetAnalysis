// frontend/src/api.js
import axios from "axios";

const BACKEND = process.env.REACT_APP_BACKEND_URL || "https://balancesheetanalysis-3.onrender.com";

// single axios instance
const api = axios.create({
  baseURL: BACKEND,
  // you can set other defaults here (timeout, etc.)
});

// cal this to (re)load token from localStorage into axios headers
export function setAuthTokenFromStorage() {
  const token = localStorage.getItem("token");
  if (token) {
    api.defaults.headers.common["Authorization"] = `Bearer ${token}`;
  } else {
    delete api.defaults.headers.common["Authorization"];
  }
}
// initialize once on import
setAuthTokenFromStorage();

// login returns axios Promise (caller can access res.data)
export const login = (email, password) => api.post("/auth/login", { email, password });

// listCompanies uses the shared axios instance (no need to pass token manually)
export const listCompanies = () => api.get("/companies");

// uploadPdf uses FormData. Do NOT manually set Content-Type (axios sets boundary automatically)
export const uploadPdf = (company_name, file, pdf_url) => {
  const fd = new FormData();
  fd.append("company_name", company_name);
  if (file) fd.append("file", file);
  if (pdf_url) fd.append("pdf_url", pdf_url);
  return api.post("/upload_pdf", fd);
};

// getCompanySheets
export const getCompanySheets = (company_id) => api.get(`/companies/${company_id}/balance_sheets`);

export default api;

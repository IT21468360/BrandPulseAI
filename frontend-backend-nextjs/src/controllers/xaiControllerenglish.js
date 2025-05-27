import axios from "axios";
const BASE = process.env.NEXT_PUBLIC_API_URL;

// We proxy /api/xai/* to your FastAPI via next.config.mjs
const API = `http://localhost:8000/api/xai`;                
// Base URL to prefix /reports/* static files

/**
 * Call FastAPI /api/xai/explain
 * @param {{ text:string, method:string, aspect:string }} params
 */
export async function explainEnglish({ text, method, aspect }) {
  const res = await axios.post(`${API}/explain`, { text, method, aspect });
  return res.data;
}

/**
 * Call FastAPI /api/xai/history?limit=N
 * Returns array of { _id, text, aspect, lime_html, shap_html, wordcloud_png, created_at }
 */
export async function getHistoryEnglish(limit = 10) {
  const res = await axios.get(`${API}/history?limit=${limit}`);
  return res.data;
}

// ← NEW: fetch one random sample per aspect from your Excel
export async function getExcelSamplesEnglish() {
  const res = await axios.get(`${API}/realtime-excel-samples`);
  console.log(res.data);
  return res.data;  // [{ aspect, text, lime_html, shap_html }, …]
}

/**
 * Convert a back-end path ("/reports/x.html") to a full URL
 * by prefixing with NEXT_PUBLIC_API_URL
 */
export function toUrl(path) {
  if (!path) return "";
  // If path is already absolute, return it
  if (path.startsWith("http://") || path.startsWith("https://")) {
    return path;
  }
  // Static reports are served at /reports/<file>
  if (path.startsWith("/reports")) {
    return `${BASE}${path}`;
  }
  return path;
}

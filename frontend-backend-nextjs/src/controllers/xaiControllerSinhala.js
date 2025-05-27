// frontend-backend-nextjs/src/controllers/xaiControllerSinhala.js
import axios from "axios";

const API   = "/api/xai/sinhala";                // note `/sinhala` suffix
const BASE  = process.env.NEXT_PUBLIC_API_URL;   // same base for static files

/**
 * Call FastAPI /api/xai/sinhala/explain
 */
export async function explainSinhala({ text, method, aspect }) {
  const res = await axios.post(`${API}/explain`, { text, method, aspect });
  return res.data;
}

/**
 * Call FastAPI /api/xai/sinhala/history?limit=N
 */
export async function getHistorySinhala(limit = 10) {
  const res = await axios.get(`${API}/history?limit=${limit}`);
  return res.data;
}

/**
 * Prefix `/reports/...` with your API base URL
 */
export function toUrlSinhala(path) {
  if (!path) return "";
  if (path.startsWith("http://") || path.startsWith("https://")) return path;
  if (path.startsWith("/reports")) return `${BASE}${path}`;
  return path;
}

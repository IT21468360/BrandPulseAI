import fetch from "node-fetch"; // Import node-fetch for API requests

// Define the base URL for the Python backend
const PYTHON_BACKEND_URL = "http://127.0.0.1:8000"; // Update if hosted differently

// ✅ **Function to trigger full keyword extraction pipeline**
export async function extractKeywords({ user_id, brand, url, dateRange, language }) {
  try {
    console.log("🔍 Sending request to extract keywords with payload:", JSON.stringify({ user_id, brand, url, dateRange, language }, null, 2));

    const response = await fetch(`${PYTHON_BACKEND_URL}/api/keyword/extract`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id, brand, url, dateRange, language }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`❌ Python API Error: ${response.status} - ${response.statusText} - ${errorText}`);
    }

    const data = await response.json();

    // ✅ **Fix: Ensure `keywords` is always an array**
    return Array.isArray(data.keywords) ? data.keywords : [];
  } catch (error) {
    console.error("❌ Error in extractKeywords:", error);
    return [];
  }
}

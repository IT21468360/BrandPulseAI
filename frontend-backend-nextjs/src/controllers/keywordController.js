import { getKeywordsFromDB } from "@/models/keywordModel"; 
import clientPromise from "@/db/mongodb/client"; 

const API_BASE_URL = "http://localhost:3000/api/keywords/extract/english";

// ✅ **Function to Fetch Stored Keywords**
export async function fetchStoredKeywords(user_id, brand, url, language) {
  try {
    console.log(`🔍 Fetching stored ${language.toUpperCase()} keywords from MongoDB...`);

    const response = await fetch(
      `${API_BASE_URL}?user_id=${user_id}&brand=${brand}&url=${url}&language=${language}`
    );

    if (!response.ok) throw new Error(`❌ API Error: ${response.statusText}`);

    const data = await response.json();
    return data.keywords || [];
  } catch (error) {
    console.error("❌ Error fetching stored keywords:", error);
    return [];
  }
}

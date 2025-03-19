import { NextResponse } from "next/server";
import { getKeywordsFromDB } from "@/models/keywordModel";
import clientPromise from "@/db/mongodb/client";

// ✅ **Fetch Stored Keywords API**
export async function GET(req) {
  try {
    const { searchParams } = new URL(req.url);
    const user_id = searchParams.get("user_id");
    const brand = searchParams.get("brand");
    const url = searchParams.get("url");
    const language = searchParams.get("language");
    const start = searchParams.get("start");
    const end = searchParams.get("end");

    if (!user_id || !brand || !url || !language || !start || !end) {
      return NextResponse.json({ message: "Missing required parameters." }, { status: 400 });
    }

    const client = await clientPromise;
    const db = client.db(process.env.DB_NAME);

    console.log("🔍 Checking existing keywords in DB...");

    const keywords = await getKeywordsFromDB(user_id, brand, url, language, start, end);

    if (keywords.length > 0) {
      console.log("✅ Keywords found in DB:", keywords);
      return NextResponse.json({ exists: true, keywords }, { status: 200 });
    } else {
      console.warn("⚠️ No stored keywords found.");
      return NextResponse.json({ exists: false, keywords: [] }, { status: 200 });
    }
  } catch (error) {
    console.error("❌ API Error in Fetch Keywords:", error);
    return NextResponse.json({ message: "Internal Server Error", error: error.message }, { status: 500 });
  }
}

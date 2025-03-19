import { NextResponse } from "next/server";
import { extractKeywords } from "@/controllers/keywordController";
import clientPromise from "@/db/mongodb/client";

// ✅ **Check if Keywords Already Exist in MongoDB**
export async function POST(req) {
  try {
    const body = await req.json();
    const { user_id, brand, url, dateRange, language, checkExisting } = body;

    if (!user_id || !brand || !url || !dateRange.start || !dateRange.end) {
      return NextResponse.json({ message: "All fields are required." }, { status: 400 });
    }

    const client = await clientPromise;
    const db = client.db(process.env.DB_NAME);

    // ✅ **Check if keywords exist in DB before extraction**
    if (checkExisting) {
      console.log("🔍 Checking existing keywords in DB...");

      const existingKeywords = await db.collection("keywords").findOne(
        { user_id, brand, url, language },
        { projection: { _id: 0, KeywordList: 1 } } // ✅ Fetch only `KeywordList`
      );

      if (existingKeywords && existingKeywords.KeywordList) {
        console.log("✅ Keywords found in DB, returning cached result...");
        return NextResponse.json({ exists: true, keywords: existingKeywords.KeywordList }, { status: 200 });
      }
    }

    console.log("⚡ Extracting new keywords...");
    const extractedKeywords = await extractKeywords({ user_id, brand, url, dateRange, language });

    if (!extractedKeywords || extractedKeywords.length === 0) {
      console.warn("⚠️ No keywords found. Returning empty array.");
      return NextResponse.json({ message: "No keywords found after extraction.", keywords: [] }, { status: 200 });
    }

    return NextResponse.json({ keywords: extractedKeywords }, { status: 200 });
  } catch (error) {
    console.error("❌ API Error in Extract Keywords:", error);
    return NextResponse.json({ message: "Internal Server Error", error: error.message }, { status: 500 });
  }
}

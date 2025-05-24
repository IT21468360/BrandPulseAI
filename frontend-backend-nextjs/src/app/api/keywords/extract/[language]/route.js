import { NextResponse } from "next/server";
import clientPromise from "@/db/mongodb/client";
import { getKeywordsFromDB } from "@/models/keywordModel";

// 🔁 POST: Call Python backend and return extracted keywords
export async function POST(req, context) {
  try {
    const language = context.params.language;
    const body = await req.json();

    const response = await fetch("http://127.0.0.1:8000/api/keyword/extract", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ...body, language }),
    });

    const result = await response.json();

    return NextResponse.json({
      success: result.success,
      keywords: result.keywords || [],
      message: result.message,
      statusMessages: result.statusMessages || [],
    });
  } catch (error) {
    console.error("❌ Error in keyword extraction route:", error);
    return NextResponse.json({ message: "Server error", error: error.message }, { status: 500 });
  }
}

// 🔍 GET: Check if keywords already exist in DB
export async function GET(req, context) {
  try {
    const language = context.params.language;
    const { searchParams } = new URL(req.url);
    const user_id = searchParams.get("user_id");
    const brand = searchParams.get("brand");
    const url = searchParams.get("url");
    const start = searchParams.get("start");
    const end = searchParams.get("end");

    if (!user_id || !brand || !url || !start || !end) {
      return NextResponse.json({ message: "Missing required parameters." }, { status: 400 });
    }

    const keywords = await getKeywordsFromDB(user_id, brand, url, language, start, end);
    return NextResponse.json({ exists: !!keywords.length, keywords }, { status: 200 });

  } catch (error) {
    console.error(`❌ Error in ${context.params.language}/GET route:`, error);
    return NextResponse.json({ message: "Internal Server Error", error: error.message }, { status: 500 });
  }
}

// ✅ File: /api/keywords/extract/[language]/route.js
import { NextResponse } from "next/server";
import clientPromise from "@/db/mongodb/client";
import { getKeywordsFromDB } from "@/models/keywordModel";

// 🔁 POST: Call Python backend and return extracted keywords
export async function POST(req, { params }) {
  try {
    const language = params.language;
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
    });

  } catch (error) {
    console.error(`❌ Error in ${params.language}/POST route:`, error);
    return NextResponse.json({ message: "Server Error", error: error.message }, { status: 500 });
  }
}

// 🔍 GET: Check if keywords already exist in DB
export async function GET(req, { params }) {
  try {
    const language = params.language;
    const { searchParams } = new URL(req.url);
    const user_id = searchParams.get("user_id");
    const brand = searchParams.get("brand");
    const url = searchParams.get("url");
    const start = searchParams.get("start");
    const end = searchParams.get("end");

    if (!user_id || !brand || !url || !start || !end) {
      return NextResponse.json({ message: "Missing required parameters." }, { status: 400 });
    }

    const client = await clientPromise;
    const db = client.db(process.env.DB_NAME);

    const keywords = await getKeywordsFromDB(user_id, brand, url, language, start, end);

    if (keywords.length > 0) {
      return NextResponse.json({ exists: true, keywords }, { status: 200 });
    } else {
      return NextResponse.json({ exists: false, keywords: [] }, { status: 200 });
    }

  } catch (error) {
    console.error(`❌ Error in ${params.language}/GET route:`, error);
    return NextResponse.json({ message: "Internal Server Error", error: error.message }, { status: 500 });
  }
}

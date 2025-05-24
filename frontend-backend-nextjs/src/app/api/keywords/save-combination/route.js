import { NextResponse } from "next/server";
import {
  saveKeywordCombination,
  getSavedCombinations,
  updateCombinationById,
  deleteCombinationById,
} from "@/models/savedCombinationModel";

// 🔁 POST: Save a new keyword combination
export async function POST(req) {
  try {
    const body = await req.json();
    const { user_id, brand, url, keywords } = body;

    if (!user_id || !brand || !url || !Array.isArray(keywords) || keywords.length === 0) {
      return NextResponse.json({ success: false, message: "Missing required fields" }, { status: 400 });
    }

    const result = await saveKeywordCombination({ user_id, brand, url, keywords });
    return NextResponse.json({ success: true, combination: result });
  } catch (error) {
    console.error("❌ POST error:", error);
    return NextResponse.json({ success: false, message: "Failed to save combination" }, { status: 500 });
  }
}

// 🔍 GET: Fetch all combinations for a user/brand/url
export async function GET(req) {
  try {
    const { searchParams } = new URL(req.url);
    const user_id = searchParams.get("user_id");
    const brand = searchParams.get("brand");
    const url = searchParams.get("url");

    if (!user_id || !brand || !url) {
      return NextResponse.json({ success: false, message: "Missing query params" }, { status: 400 });
    }

    const results = await getSavedCombinations(user_id, brand, url);
    return NextResponse.json({ success: true, combinations: results });
  } catch (error) {
    console.error("❌ GET error:", error);
    return NextResponse.json({ success: false, message: "Failed to fetch combinations" }, { status: 500 });
  }
}

// ✏️ PUT: Update a keyword combination by _id
export async function PUT(req) {
  try {
    const { id, keywords } = await req.json();
    if (!id || !Array.isArray(keywords)) {
      return NextResponse.json({ success: false, message: "Missing fields" }, { status: 400 });
    }

    const updated = await updateCombinationById(id, keywords);
    return NextResponse.json({ success: true, updated });
  } catch (error) {
    console.error("❌ PUT error:", error);
    return NextResponse.json({ success: false, message: "Failed to update" }, { status: 500 });
  }
}

// ❌ DELETE: Remove a combination by _id
export async function DELETE(req) {
  try {
    const { searchParams } = new URL(req.url);
    const id = searchParams.get("id");

    if (!id) {
      return NextResponse.json({ success: false, message: "Missing ID" }, { status: 400 });
    }

    const deleted = await deleteCombinationById(id);
    return NextResponse.json({ success: true, deleted });
  } catch (error) {
    console.error("❌ DELETE error:", error);
    return NextResponse.json({ success: false, message: "Failed to delete" }, { status: 500 });
  }
}

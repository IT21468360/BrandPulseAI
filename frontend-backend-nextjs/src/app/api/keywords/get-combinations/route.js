// ✅ File: /app/api/keywords/get-combinations/route.js
import { NextResponse } from "next/server";
import clientPromise from "@/db/mongodb/client";

export async function GET(req) {
  try {
    const { searchParams } = new URL(req.url);
    const user_id = searchParams.get("user_id");

    if (!user_id) {
      return NextResponse.json({ success: false, message: "Missing user_id" }, { status: 400 });
    }

    const client = await clientPromise;
    const db = client.db(process.env.DB_NAME);

    const combinations = await db
      .collection("saved_combinations")
      .find({ user_id })
      .project({ _id: 1, keywords: 1 })
      .toArray();

    return NextResponse.json({ success: true, combinations });
  } catch (err) {
    console.error("❌ Error fetching combinations:", err);
    return NextResponse.json({ success: false, message: "Server error" }, { status: 500 });
  }
}

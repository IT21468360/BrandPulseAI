import { NextResponse } from "next/server";
import clientPromise from "@/db/mongodb/client";

export async function GET(req, { params }) {
  try {
    // ✅ Await params properly
    const { user_id } = await params; 

    if (!user_id) {
      return NextResponse.json({ message: "User ID is required." }, { status: 400 });
    }

    console.log(`Fetching brands for user: ${user_id}`);

    const client = await clientPromise;
    const db = client.db(process.env.DB_NAME);

    const brands = await db.collection("brands").find({ user_id }).toArray();

    if (!brands.length) {
      return NextResponse.json({ success: true, brands: [] }, { status: 200 });
    }

    return NextResponse.json({ success: true, brands }, { status: 200 });
  } catch (error) {
    console.error("❌ Error fetching brands:", error);
    return NextResponse.json({ message: "Internal Server Error", error: error.message }, { status: 500 });
  }
}

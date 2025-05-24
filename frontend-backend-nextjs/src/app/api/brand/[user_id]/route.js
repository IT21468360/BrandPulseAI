import { NextResponse } from "next/server";
import clientPromise from "@/db/mongodb/client";

export async function GET(req, { params }) {
  try {
    const user_id = params.user_id;

    if (!user_id) {
      return NextResponse.json({ message: "User ID is required." }, { status: 400 });
    }

    console.log(`📥 Fetching brands for user: ${user_id}`);

    const client = await clientPromise;
    const db = client.db(process.env.DB_NAME);

    const brands = await db.collection("brands")
      .find({ user_id })
      .project({
        brand_name: 1,
        websites: 1,
        industry: 1,
        phone: 1,
        address: 1,
        created_at: 1,
        _id: 1
      })
      .toArray();

    console.log("✅ Brands fetched:", brands);

    return NextResponse.json({ success: true, brands }, { status: 200 });

  } catch (error) {
    console.error("❌ Error fetching brands:", error);
    return NextResponse.json({ message: "Internal Server Error", error: error.message }, { status: 500 });
  }
}

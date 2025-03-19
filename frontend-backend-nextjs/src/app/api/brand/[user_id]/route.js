import { NextResponse } from "next/server";
import clientPromise from "@/db/mongodb/client";

export async function GET(req, { params }) {
  try {
    const { user_id } = params; 

    if (!user_id) {
      return NextResponse.json({ message: "User ID is required." }, { status: 400 });
    }

    console.log(`Fetching brands for user: ${user_id}`);

    const client = await clientPromise;
    const db = client.db(process.env.DB_NAME);

    // ✅ Fetch brands including `brand_name` and `website` (or `url`)
    const brands = await db.collection("brands")
      .find({ user_id })
      .project({ brand_name: 1, website: 1, url: 1, _id: 0 }) // Includes both `website` and `url`
      .toArray();

    console.log("Fetched brands:", brands); // Debugging

    return NextResponse.json({ success: true, brands }, { status: 200 });
  } catch (error) {
    console.error("❌ Error fetching brands:", error);
    return NextResponse.json({ message: "Internal Server Error", error: error.message }, { status: 500 });
  }
}

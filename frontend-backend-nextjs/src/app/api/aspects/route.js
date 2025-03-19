import { NextResponse } from "next/server";
import clientPromise from "@/db/mongodb/client";

export async function GET() {
    try {
        const client = await clientPromise;
        const db = client.db("BrandPulseAI");
        const collection = db.collection("Aspects");

        // Fetch comments grouped by aspect
        const commentsByAspect = await collection.aggregate([
            { $group: { _id: "$aspect", comments: { $push: "$comment" } } }
        ]).toArray();

        return NextResponse.json(commentsByAspect);
    } catch (error) {
        return NextResponse.json({ error: "Failed to fetch data" }, { status: 500 });
    }
}

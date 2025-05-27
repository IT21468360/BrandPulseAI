import { NextResponse } from "next/server";
import clientPromise from "@/db/mongodb/client";

export async function GET(req) {
    try {
        const { searchParams } = new URL(req.url);
        const language = searchParams.get("language");

        const client = await clientPromise;
        const db = client.db("BrandPulseAI");

        const collectionName = language === "english" 
            ? "english_sentiment_predictions" 
            : "sinhala_sentiment_predictions";

        const collection = db.collection(collectionName);

        // ✅ Step 1: Find the latest file
        const latest = await collection
            .find({ language })
            .sort({ source_file: -1 }) // sort by file name (which has date)
            .limit(1)
            .toArray();

        if (!latest.length) {
            return NextResponse.json([], { status: 200 });
        }

        const latestFile = latest[0].source_file;

        // ✅ Step 2: Fetch only comments from the latest file
        const results = await collection.find({ language, source_file: latestFile }).toArray();

        return NextResponse.json(results, { status: 200 });
    } catch (error) {
        console.error("❌ Error fetching sentiment results:", error);
        return NextResponse.json({ error: "Internal Server Error" }, { status: 500 });
    }
}
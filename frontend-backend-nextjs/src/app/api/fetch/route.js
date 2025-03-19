import { NextResponse } from "next/server";
import mongoose from "mongoose";
import Sentiment from "../../../models/sentimentModel";

export async function GET(req) {
    try {
        // ✅ Get language parameter from URL
        const { searchParams } = new URL(req.url);
        const language = searchParams.get("language");

        if (!language) {
            return NextResponse.json({ error: "Missing language parameter" }, { status: 400 });
        }

        // ✅ Ensure MongoDB is connected
        if (mongoose.connection.readyState !== 1) {
            await mongoose.connect(process.env.MONGODB_URI);
        }

        // ✅ Fetch data from MongoDB
        const results = await Sentiment.find({ language }).lean();

        return NextResponse.json(results, { status: 200 });
    } catch (error) {
        console.error("Error fetching sentiment data:", error);
        return NextResponse.json({ error: "Failed to fetch sentiment data" }, { status: 500 });
    }
}

import { NextResponse } from "next/server";
import mongoose from "mongoose";
import Sentiment from "@/models/sentimentModel"; // ✅ Use alias if `jsconfig.json` or `tsconfig.json` is configured

// ✅ Optional: Cache DB connection in development to prevent multiple connects
let isConnected = false;

export async function GET(req) {
    try {
        const { searchParams } = new URL(req.url);
        const language = searchParams.get("language");

        // ✅ Validate language
        if (!language || !["english", "sinhala"].includes(language.toLowerCase())) {
            return NextResponse.json(
                { error: "Missing or invalid language parameter" },
                { status: 400 }
            );
        }

        // ✅ Connect to MongoDB if not already
        if (!isConnected || mongoose.connection.readyState !== 1) {
            await mongoose.connect(process.env.MONGODB_URI, {
                dbName: "BrandPulseAI", // ✅ Set DB name explicitly
                useNewUrlParser: true,
                useUnifiedTopology: true,
            });
            isConnected = true;
        }

        // ✅ Fetch sentiments based on language
        const results = await Sentiment.find({ language }).lean();

        return NextResponse.json({ data: results }, { status: 200 });
    } catch (error) {
        console.error("🔥 MongoDB Fetch Error:", error);
        return NextResponse.json(
            { error: "Failed to fetch sentiment data", details: error.message },
            { status: 500 }
        );
    }
}

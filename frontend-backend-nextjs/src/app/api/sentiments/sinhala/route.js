import { NextResponse } from "next/server";
import { processSinhalaSentiment } from "@/controllers/sentimentSinhalaController";

export async function POST() {
    try {
        const result = await processSinhalaSentiment();
        return NextResponse.json({ message: "Sinhala Sentiment Analysis Completed", result }, { status: 200 });
    } catch (error) {
        return NextResponse.json({ error: "Failed to process Sinhala sentiment" }, { status: 500 });
    }
}

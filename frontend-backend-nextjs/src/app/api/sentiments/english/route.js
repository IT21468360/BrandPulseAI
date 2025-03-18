import { NextResponse } from "next/server";
import { processEnglishSentiment } from "@/controllers/sentimentEnglishController";

export async function POST() {
    try {
        const result = await processEnglishSentiment();
        return NextResponse.json({ message: "English Sentiment Analysis Completed", result }, { status: 200 });
    } catch (error) {
        return NextResponse.json({ error: "Failed to process English sentiment" }, { status: 500 });
    }
}

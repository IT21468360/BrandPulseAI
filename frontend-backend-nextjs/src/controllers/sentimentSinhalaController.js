import clientPromise from "@/db/mongodb/client";

export async function processSinhalaSentiment() {
    try {
        const client = await clientPromise;
        const db = client.db("BrandPulseAI");

        console.log("✅ Step 1: Connected to MongoDB");

        const response = await fetch("http://127.0.0.1:8000/api/csv/sinhala-csv-predict", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
        });

        const sentimentResults = await response.json();

        console.log("✅ Step 2: Got predictions:", sentimentResults);

        if (!Array.isArray(sentimentResults) || sentimentResults.length === 0) {
            console.log("❌ Step 3: No predictions returned");
            return { message: "Model did not return predictions." };
        }

        const insertResult = await db
            .collection("sinhala_sentiment_predictions")
            .insertMany(sentimentResults);

        console.log(`✅ Step 4: Inserted ${insertResult.insertedCount} Sinhala documents into MongoDB.`);

        return sentimentResults;
    } catch (error) {
        console.error("❌ Error processing Sinhala sentiment:", error);
        return null;
    }
}

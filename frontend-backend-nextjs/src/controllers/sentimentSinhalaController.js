import clientPromise from "@/db/mongodb/client";

export async function processSinhalaSentiment() {
    try {
        const client = await clientPromise;
        const db = client.db("BrandPulseAI");

        // ✅ Step 1: Fetch Sinhala reviews from MongoDB
        const reviews = await db.collection("reviews").find({ language: "sinhala" }).toArray();

        if (reviews.length === 0) {
            return { message: "No Sinhala reviews found." };
        }

        // ✅ Step 2: Send reviews to Sinhala Sentiment Model API (Replace with actual API)
        const modelResponse = await fetch("http://localhost:8000/api/sinhala-predict", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ reviews }),
        });

        const sentimentResults = await modelResponse.json();

        // ✅ Step 3: Save Sentiment Results in MongoDB
        await db.collection("sentiment_results").insertMany(sentimentResults);

        return sentimentResults;
    } catch (error) {
        console.error("Error processing Sinhala sentiment:", error);
        return null;
    }
}

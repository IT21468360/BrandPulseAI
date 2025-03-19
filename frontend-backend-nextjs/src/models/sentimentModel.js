import mongoose from "mongoose";

const SentimentSchema = new mongoose.Schema({
    comment: String,
    aspect: String,
    sentiment_label: String,
    sentiment_score: Number,
    language: String,
}, { collection: "sentiments" }); // ✅ Ensures MongoDB uses "sentiments" collection

export default mongoose.models.Sentiment || mongoose.model("Sentiment", SentimentSchema);

import { z } from "zod";
import { ObjectId } from "mongodb"; 
import clientPromise from "@/db/mongodb/client";

const db_name = process.env.DB_NAME;
const COLLECTION_NAME = "keywords";

// ✅ **Define Keyword Schema Using Zod**
const KeywordSchema = z.object({
  user_id: z.string().min(1, "User ID is required"),
  brand: z.string().min(1, "Brand is required"),
  url: z.string().url("Invalid URL format"),
  language: z.string().min(1, "Language is required"),
  dateRange: z.object({
    start: z.string().min(1, "Start Date is required"),
    end: z.string().min(1, "End Date is required"),
  }),
  KeywordList: z.array(z.string()).min(1, "At least one keyword is required"),
  created_at: z.date().default(() => new Date()),
});

// ✅ **Validate Data Against the Schema**
export function validateKeywordData(data) {
  return KeywordSchema.parse(data);
}

// ✅ **Fetch Keywords Based on User, Brand, Language & Date Range**
export async function getKeywordsFromDB(user_id, brand, url, language) {
  const client = await clientPromise;
  const db = client.db(db_name);

  const result = await db.collection(COLLECTION_NAME).findOne(
    {
      user_id,
      brand,
      url,
      language
      // "dateRange.start": { $lte: start }, // ✅ Fetch if start is earlier than or equal to requested
      // "dateRange.end": { $gte: end }      // ✅ Fetch if end is later than or equal to requested
    },
    { projection: { _id: 0, KeywordList: 1 } }
  );
  

  return result ? result.KeywordList : [];
}

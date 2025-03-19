import { z } from "zod";
import { ObjectId } from "mongodb"; // Import ObjectId for MongoDB IDs
import clientPromise from "@/db/mongodb/client";

// MongoDB Database Name & Collection
const db_name = process.env.DB_NAME;
const COLLECTION_NAME = "keywords";

// **1️⃣ Define Keyword Schema using Zod**
const KeywordSchema = z.object({
  user_id: z.string().min(1, "User ID is required"),
  brand_id: z.string().min(1, "Brand ID is required"), // Linking to a specific brand
  url: z.string().url("Invalid URL format"),
  keywords: z.array(z.string()).min(1, "At least one keyword is required"),
  created_at: z.date().default(() => new Date()), // Default timestamp
});

// **2️⃣ Validate Data Against the Schema**
export function validateKeywordData(data) {
  return KeywordSchema.parse(data); // Throws an error if validation fails
}

// **3️⃣ Database Operations for Keyword Management**
export async function saveKeywordsToDB(user_id, brand_id, url, keywords) {
  const client = await clientPromise;
  const db = client.db(db_name);

  // Validate input using Zod schema
  const validatedData = validateKeywordData({ user_id, brand_id, url, keywords });

  // Insert data into MongoDB
  const result = await db.collection(COLLECTION_NAME).insertOne(validatedData);
  
  return {
    id: result.insertedId,
    ...validatedData,
  };
}

export async function getKeywordsByUserId(user_id) {
  const client = await clientPromise;
  const db = client.db(db_name);
  return await db.collection(COLLECTION_NAME).find({ user_id }).toArray();
}

export async function getKeywordsByBrandId(brand_id) {
  const client = await clientPromise;
  const db = client.db(db_name);

  if (!ObjectId.isValid(brand_id)) {
    throw new Error("Invalid Brand ID");
  }

  return await db.collection(COLLECTION_NAME).find({ brand_id }).toArray();
}

export async function getKeywordsByUrl(url) {
  const client = await clientPromise;
  const db = client.db(db_name);
  return await db.collection(COLLECTION_NAME).findOne({ url });
}

export async function deleteKeywordsById(id) {
  const client = await clientPromise;
  const db = client.db(db_name);

  if (!ObjectId.isValid(id)) {
    throw new Error("Invalid Keyword ID");
  }

  return await db.collection(COLLECTION_NAME).deleteOne({ _id: new ObjectId(id) });
}

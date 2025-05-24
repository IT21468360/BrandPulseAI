import clientPromise from "@/db/mongodb/client";
import { ObjectId } from "mongodb";

const db_name = process.env.DB_NAME;
const COLLECTION = "saved_combinations";

// 🔁 Save new keyword combination
export async function saveKeywordCombination({ user_id, brand, url, keywords }) {
  const client = await clientPromise;
  const db = client.db(db_name);

  const doc = {
    user_id,
    brand,
    url,
    keywords,
    created_at: new Date(),
  };

  const result = await db.collection(COLLECTION).insertOne(doc);
  return { _id: result.insertedId, ...doc };
}

// 🔍 Get all combinations for user/brand/url
export async function getSavedCombinations(user_id, brand, url) {
  const client = await clientPromise;
  const db = client.db(db_name);

  return await db.collection(COLLECTION)
    .find({ user_id, brand, url })
    .sort({ created_at: -1 })
    .toArray();
}

// ✏️ Update keywords in a combination by ID
export async function updateCombinationById(id, keywords) {
  const client = await clientPromise;
  const db = client.db(db_name);

  const result = await db.collection(COLLECTION).updateOne(
    { _id: new ObjectId(id) },
    { $set: { keywords, updated_at: new Date() } }
  );
  return result.modifiedCount > 0;
}

// ❌ Delete a combination by ID
export async function deleteCombinationById(id) {
  const client = await clientPromise;
  const db = client.db(db_name);

  const result = await db.collection(COLLECTION).deleteOne({ _id: new ObjectId(id) });
  return result.deletedCount > 0;
}

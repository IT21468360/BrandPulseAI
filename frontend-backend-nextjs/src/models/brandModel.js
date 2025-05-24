import { z } from "zod";
import { ObjectId } from "mongodb"; 
import clientPromise from "@/db/mongodb/client"; 

// MongoDB Database Name
const db_name = process.env.DB_NAME;
const COLLECTION_NAME = "brands";

// ✅ **Brand Schema Validation**
const BrandSchema = z.object({
  user_id: z.string().min(1, "User ID is required"),
  brand_name: z.string().min(1, "Brand name is required"),
  industry: z.string().min(1, "Industry is required"),
  websites: z.array(z.string().url("Invalid website URL")).min(1, "At least one website is required"),
  address: z.string().min(1, "Address is required"),
  phone: z.string().min(10, "Phone number must be at least 10 digits"),
  created_at: z.date().default(() => new Date()),
});

// ✅ **Validate Brand Data**
export function validateBrand(data) {
  return BrandSchema.parse(data);
}

// ✅ **Create Brand**
export async function createBrand(brand) {
  const client = await clientPromise;
  const db = client.db(db_name);

  // Check if brand already exists for the user
  const existingBrand = await db.collection(COLLECTION_NAME).findOne({
    user_id: brand.user_id,
    brand_name: brand.brand_name,
  });

  if (existingBrand) {
    throw new Error("Brand with this name already exists for this user.");
  }

  // Insert brand into DB
  const result = await db.collection(COLLECTION_NAME).insertOne(brand);
  
  return { id: result.insertedId, ...brand };
}

// ✅ **Get Brand By User ID**
export async function getBrandsByUserId(user_id) {
  const client = await clientPromise;
  const db = client.db(db_name);
  
  return await db.collection(COLLECTION_NAME).find({ user_id }).toArray();
}

// ✅ **Get All Brands**
export async function getAllBrands() {
  const client = await clientPromise;
  const db = client.db(db_name);
  return await db.collection(COLLECTION_NAME).find({}).toArray();
}

// ✅ **Delete Brand**
export async function deleteBrandById(id) {
  const client = await clientPromise;
  const db = client.db(db_name);

  if (!ObjectId.isValid(id)) {
    throw new Error("Invalid Brand ID");
  }

  return await db.collection(COLLECTION_NAME).deleteOne({ _id: new ObjectId(id) });
}

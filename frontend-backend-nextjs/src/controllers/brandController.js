import { createBrand, getBrandByName } from "@/models/brandModel"; // Import database operations
import clientPromise from "@/db/mongodb/client"; // Correct MongoDB connection

export const registerBrand = async ({ user_id, brand_name, industry, website, address, phone }) => {
  try {
    const client = await clientPromise; // Ensure MongoDB is connected
    const db = client.db(process.env.DB_NAME);

    if (!user_id || !brand_name || !industry || !website || !address || !phone) {
      return { success: false, message: "All fields are required" };
    }

    // Check if the brand already exists for this user
    const existingBrand = await db.collection("brands").findOne({ user_id, brand_name });

    if (existingBrand) {
      return { success: false, message: "Brand already exists!" };
    }

    // Create new brand entry
    const newBrand = await createBrand({ user_id, brand_name, industry, website, address, phone });

    return { success: true, message: "Brand registered successfully!", brand: newBrand };
  } catch (error) {
    console.error("❌ Error in registerBrand:", error);
    return { success: false, message: "Server error", error: error.message };
  }
};
